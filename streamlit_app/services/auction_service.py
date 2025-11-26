"""Auction engine service."""
from datetime import datetime
from models import get_session, Room, Player, AuctionPlayer, Team, TeamPlayer


class AuctionState:
    """Class to represent current auction state."""
    def __init__(self, room_code, current_player=None, current_bid=None, 
                 highest_bidder=None, timer_remaining=None, auction_complete=False):
        self.room_code = room_code
        self.current_player = current_player
        self.current_bid = current_bid
        self.highest_bidder = highest_bidder
        self.timer_remaining = timer_remaining
        self.auction_complete = auction_complete


class BidResult:
    """Class to represent bid result."""
    def __init__(self, success, message, new_bid=None, highest_bidder=None):
        self.success = success
        self.message = message
        self.new_bid = new_bid
        self.highest_bidder = highest_bidder


# Global state to track current auction state for each room
_auction_states = {}


def initialize_auction(room_code):
    """Initialize auction for a room by creating AuctionPlayer records."""
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return False, "Room not found"
        
        # Get all players
        all_players = session.query(Player).all()
        
        # Create AuctionPlayer records for this room
        for player in all_players:
            existing = session.query(AuctionPlayer).filter_by(
                room_id=room.id, 
                player_id=player.id
            ).first()
            
            if not existing:
                auction_player = AuctionPlayer(
                    room_id=room.id,
                    player_id=player.id,
                    is_sold=False
                )
                session.add(auction_player)
        
        session.commit()
        
        # Initialize auction state
        _auction_states[room_code] = {
            'current_player_id': None,
            'current_bid': None,
            'highest_bidder': None,
            'bid_increment': 5.0,
            'timer_duration': 30,
            'timer_start': None
        }
        
        return True, "Auction initialized successfully"
    except Exception as e:
        session.rollback()
        return False, f"Error initializing auction: {str(e)}"
    finally:
        session.close()


def present_next_player(room_code):
    """Present the next unsold player for auction."""
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return None
        
        unsold_auction_player = session.query(AuctionPlayer).filter_by(
            room_id=room.id,
            is_sold=False
        ).first()
        
        if not unsold_auction_player:
            return None
        
        player = unsold_auction_player.player
        
        if room_code not in _auction_states:
            _auction_states[room_code] = {
                'bid_increment': 5.0,
                'timer_duration': 30
            }
        
        _auction_states[room_code]['current_player_id'] = player.id
        _auction_states[room_code]['current_bid'] = player.base_price
        _auction_states[room_code]['highest_bidder'] = None
        _auction_states[room_code]['timer_start'] = datetime.utcnow()
        
        return player
    finally:
        session.close()


def place_bid(room_code, username):
    """Place a bid for the current player."""
    if room_code not in _auction_states:
        return BidResult(False, "Auction not initialized", None, None)
    
    state = _auction_states[room_code]
    
    if state['current_player_id'] is None:
        return BidResult(False, "No player currently being auctioned", None, None)
    
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return BidResult(False, "Room not found", None, None)
        
        team = session.query(Team).filter_by(room_id=room.id, username=username).first()
        if not team:
            return BidResult(False, "Team not found", None, None)
        
        current_bid = state['current_bid']
        bid_increment = state['bid_increment']
        new_bid = current_bid + bid_increment
        
        if team.purse_left < new_bid:
            return BidResult(False, "Insufficient purse for this bid", None, None)
        
        state['current_bid'] = new_bid
        state['highest_bidder'] = username
        
        return BidResult(True, "Bid placed successfully", new_bid, username)
    finally:
        session.close()


def handle_timer_expiry(room_code):
    """Handle timer expiry and assign player to highest bidder."""
    if room_code not in _auction_states:
        return None
    
    state = _auction_states[room_code]
    
    if state['current_player_id'] is None:
        return None
    
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return None
        
        player_id = state['current_player_id']
        sold_price = state['current_bid']
        highest_bidder = state['highest_bidder']
        
        auction_player = session.query(AuctionPlayer).filter_by(
            room_id=room.id,
            player_id=player_id
        ).first()
        
        if not auction_player:
            return None
        
        auction_player.is_sold = True
        auction_player.sold_price = sold_price
        auction_player.sold_at = datetime.utcnow()
        
        if highest_bidder:
            team = session.query(Team).filter_by(room_id=room.id, username=highest_bidder).first()
            if team:
                auction_player.sold_to_team_id = team.id
                
                team_player = TeamPlayer(
                    team_id=team.id,
                    player_id=player_id,
                    price=sold_price
                )
                session.add(team_player)
                
                team.purse_left -= sold_price
        
        session.commit()
        
        state['current_player_id'] = None
        state['current_bid'] = None
        state['highest_bidder'] = None
        state['timer_start'] = None
        
        player = session.query(Player).get(player_id)
        
        return {
            'player': player,
            'sold_price': sold_price,
            'sold_to': highest_bidder,
            'team_id': auction_player.sold_to_team_id
        }
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_current_auction_state(room_code):
    """Get current state of the auction."""
    if room_code not in _auction_states:
        return AuctionState(room_code, auction_complete=False)
    
    state = _auction_states[room_code]
    
    session = get_session()
    try:
        current_player = None
        if state['current_player_id']:
            current_player = session.query(Player).get(state['current_player_id'])
        
        room = session.query(Room).filter_by(code=room_code).first()
        auction_complete = False
        if room:
            unsold_count = session.query(AuctionPlayer).filter_by(
                room_id=room.id,
                is_sold=False
            ).count()
            total_count = session.query(AuctionPlayer).filter_by(room_id=room.id).count()
            auction_complete = (total_count > 0 and unsold_count == 0)
        
        return AuctionState(
            room_code=room_code,
            current_player=current_player,
            current_bid=state['current_bid'],
            highest_bidder=state['highest_bidder'],
            timer_remaining=state.get('timer_duration', 30),
            auction_complete=auction_complete
        )
    finally:
        session.close()


def get_timer_start(room_code):
    """Get timer start timestamp for a room."""
    if room_code in _auction_states:
        return _auction_states[room_code].get('timer_start')
    return None
