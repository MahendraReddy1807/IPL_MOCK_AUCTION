"""WebSocket event handlers for real-time auction communication."""
from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.services.room_service import get_room_participants, start_auction as start_auction_service
from app.services.auction_service import place_bid as place_bid_service, present_next_player, handle_timer_expiry
from app.models.room import Room
from app.models.team import Team


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to auction server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f"Client disconnected: {request.sid}")


@socketio.on('join_room')
def handle_join_room(data):
    """
    Handle user joining a room.
    
    Expected data: {
        'room_code': str,
        'username': str
    }
    """
    room_code = data.get('room_code')
    username = data.get('username')
    
    if not room_code or not username:
        emit('error', {'message': 'Room code and username are required'})
        return
    
    # Join the Socket.IO room
    join_room(room_code)
    
    # Get updated participant list
    participants = get_room_participants(room_code)
    participant_usernames = [p.username for p in participants]
    
    # Broadcast to all users in the room
    emit('user_joined', {
        'username': username,
        'participants': participant_usernames,
        'participants_count': len(participant_usernames)
    }, room=room_code)
    
    print(f"User {username} joined room {room_code}")


@socketio.on('leave_room')
def handle_leave_room(data):
    """
    Handle user leaving a room.
    
    Expected data: {
        'room_code': str,
        'username': str
    }
    """
    room_code = data.get('room_code')
    username = data.get('username')
    
    if not room_code:
        return
    
    # Leave the Socket.IO room
    leave_room(room_code)
    
    # Get updated participant list
    participants = get_room_participants(room_code)
    participant_usernames = [p.username for p in participants]
    
    # Broadcast to remaining users
    emit('user_left', {
        'username': username,
        'participants': participant_usernames,
        'participants_count': len(participant_usernames)
    }, room=room_code)
    
    print(f"User {username} left room {room_code}")


@socketio.on('start_auction')
def handle_start_auction(data):
    """
    Handle auction start request from host.
    
    Expected data: {
        'room_code': str,
        'host_username': str
    }
    """
    room_code = data.get('room_code')
    host_username = data.get('host_username')
    
    if not room_code or not host_username:
        emit('error', {'message': 'Room code and host username are required'})
        return
    
    # Start the auction
    success, message = start_auction_service(room_code, host_username)
    
    if not success:
        emit('error', {'message': message})
        return
    
    # Initialize auction (create AuctionPlayer records)
    from app.services.auction_service import initialize_auction
    init_success, init_message = initialize_auction(room_code)
    if not init_success:
        emit('error', {'message': f'Failed to initialize auction: {init_message}'})
        return
    
    # Broadcast auction started event
    emit('auction_started', {
        'room_code': room_code,
        'message': 'Auction has started!'
    }, room=room_code)
    
    # Present the first player
    player = present_next_player(room_code)
    if player:
        emit('player_presented', {
            'player': {
                'id': player.id,
                'name': player.name,
                'role': player.role,
                'country': player.country,
                'base_price': player.base_price,
                'batting_score': player.batting_score,
                'bowling_score': player.bowling_score,
                'overall_score': player.overall_score,
                'is_overseas': player.is_overseas
            },
            'current_bid': player.base_price,
            'timer_duration': 60
        }, room=room_code)
    
    print(f"Auction started in room {room_code}")


@socketio.on('place_bid')
def handle_place_bid(data):
    """
    Handle bid placement.
    
    Expected data: {
        'room_code': str,
        'username': str
    }
    """
    room_code = data.get('room_code')
    username = data.get('username')
    
    if not room_code or not username:
        emit('error', {'message': 'Room code and username are required'})
        return
    
    # Place the bid
    result = place_bid_service(room_code, username)
    
    if not result.success:
        emit('bid_error', {'message': result.message}, room=request.sid)
        return
    
    # Get team info for purse update
    room = Room.query.filter_by(code=room_code).first()
    if room:
        team = Team.query.filter_by(room_id=room.id, username=username).first()
        if team:
            # Broadcast bid placed event to all users
            emit('bid_placed', {
                'username': username,
                'bid_amount': result.new_bid,
                'current_highest': result.new_bid,
                'highest_bidder': result.highest_bidder
            }, room=room_code)
            
            # Broadcast purse update
            emit('purse_updated', {
                'username': username,
                'team_id': team.id,
                'new_purse': team.purse_left,
                'team_name': team.team_name
            }, room=room_code)
    
    print(f"Bid placed by {username} in room {room_code}: {result.new_bid}")


@socketio.on('timer_expired')
def handle_timer_expired(data):
    """
    Handle timer expiry for current player.
    
    Expected data: {
        'room_code': str
    }
    """
    room_code = data.get('room_code')
    
    if not room_code:
        emit('error', {'message': 'Room code is required'})
        return
    
    # Handle timer expiry and assign player
    sold_info = handle_timer_expiry(room_code)
    
    if sold_info:
        # Broadcast player sold event
        emit('player_sold', {
            'player': {
                'id': sold_info['player'].id,
                'name': sold_info['player'].name,
                'role': sold_info['player'].role
            },
            'sold_to': sold_info['sold_to'],
            'sold_price': sold_info['sold_price'],
            'team_id': sold_info['team_id']
        }, room=room_code)
        
        # Present next player
        next_player = present_next_player(room_code)
        if next_player:
            emit('player_presented', {
                'player': {
                    'id': next_player.id,
                    'name': next_player.name,
                    'role': next_player.role,
                    'country': next_player.country,
                    'base_price': next_player.base_price,
                    'batting_score': next_player.batting_score,
                    'bowling_score': next_player.bowling_score,
                    'overall_score': next_player.overall_score,
                    'is_overseas': next_player.is_overseas
                },
                'current_bid': next_player.base_price,
                'timer_duration': 30
            }, room=room_code)
        else:
            # Auction completed
            emit('auction_completed', {
                'message': 'All players have been sold!',
                'room_code': room_code
            }, room=room_code)
    
    print(f"Timer expired in room {room_code}")


@socketio.on('get_auction_state')
def handle_get_auction_state(data):
    """
    Get current auction state.
    
    Expected data: {
        'room_code': str
    }
    """
    from app.services.auction_service import get_current_auction_state
    
    room_code = data.get('room_code')
    
    if not room_code:
        emit('error', {'message': 'Room code is required'})
        return
    
    state = get_current_auction_state(room_code)
    
    player_data = None
    if state.current_player:
        player_data = {
            'id': state.current_player.id,
            'name': state.current_player.name,
            'role': state.current_player.role,
            'country': state.current_player.country,
            'base_price': state.current_player.base_price,
            'batting_score': state.current_player.batting_score,
            'bowling_score': state.current_player.bowling_score,
            'overall_score': state.current_player.overall_score,
            'is_overseas': state.current_player.is_overseas
        }
    
    emit('auction_state', {
        'current_player': player_data,
        'current_bid': state.current_bid,
        'highest_bidder': state.highest_bidder,
        'timer_remaining': state.timer_remaining,
        'auction_complete': state.auction_complete
    })
