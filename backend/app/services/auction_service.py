"""Auction engine service."""
from datetime import datetime
from app import db
from app.models.room import Room
from app.models.player import Player
from app.models.auction_player import AuctionPlayer
from app.models.team import Team
from app.models.team_player import TeamPlayer


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
# In production, this should be stored in Redis or similar
_auction_states = {}


def initialize_auction(room_code):
    """
    Initialize auction for a room by creating AuctionPlayer records.
    
    Args:
        room_code: Code of the room
        
    Returns:
        tuple: (success: bool, message: str)
    """
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return False, "Room not found"
    
    # Get all players
    all_players = Player.query.all()
    
    # Create AuctionPlayer records for this room
    for player in all_players:
        # Check if already exists
        existing = AuctionPlayer.query.filter_by(
            room_id=room.id, 
            player_id=player.id
        ).first()
        
        if not existing:
            auction_player = AuctionPlayer(
                room_id=room.id,
                player_id=player.id,
                is_sold=False
            )
            db.session.add(auction_player)
    
    db.session.commit()
    
    # Initialize auction state
    _auction_states[room_code] = {
        'current_player_id': None,
        'current_bid': None,
        'highest_bidder': None,
        'bid_increment': 5.0,  # Default bid increment in Lakhs
        'timer_duration': 30  # 30 seconds per player (as per requirements)
    }
    
    return True, "Auction initialized successfully"


def present_next_player(room_code):
    """
    Present the next unsold player for auction.
    
    Args:
        room_code: Code of the room
        
    Returns:
        Player or None: Next player to auction, or None if all sold
    """
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return None
    
    # Find next unsold player
    unsold_auction_player = AuctionPlayer.query.filter_by(
        room_id=room.id,
        is_sold=False
    ).first()
    
    if not unsold_auction_player:
        # All players sold
        return None
    
    player = unsold_auction_player.player
    
    # Update auction state
    if room_code not in _auction_states:
        _auction_states[room_code] = {
            'bid_increment': 5.0,
            'timer_duration': 60  # 60 seconds (1 minute)
        }
    
    _auction_states[room_code]['current_player_id'] = player.id
    _auction_states[room_code]['current_bid'] = player.base_price
    _auction_states[room_code]['highest_bidder'] = None
    
    return player


def place_bid(room_code, username):
    """
    Place a bid for the current player.
    
    Args:
        room_code: Code of the room
        username: Username of the bidder
        
    Returns:
        BidResult: Result of the bid attempt
    """
    # Get auction state
    if room_code not in _auction_states:
        return BidResult(False, "Auction not initialized", None, None)
    
    state = _auction_states[room_code]
    
    if state['current_player_id'] is None:
        return BidResult(False, "No player currently being auctioned", None, None)
    
    # Get room and team
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return BidResult(False, "Room not found", None, None)
    
    team = Team.query.filter_by(room_id=room.id, username=username).first()
    if not team:
        return BidResult(False, "Team not found", None, None)
    
    # Calculate new bid
    current_bid = state['current_bid']
    bid_increment = state['bid_increment']
    new_bid = current_bid + bid_increment
    
    # Check if team has sufficient purse
    if team.purse_left < new_bid:
        return BidResult(False, "Insufficient purse for this bid", None, None)
    
    # Update bid
    state['current_bid'] = new_bid
    state['highest_bidder'] = username
    
    return BidResult(True, "Bid placed successfully", new_bid, username)


def handle_timer_expiry(room_code):
    """
    Handle timer expiry and assign player to highest bidder.
    
    Args:
        room_code: Code of the room
        
    Returns:
        dict: Information about the sold player
    """
    if room_code not in _auction_states:
        return None
    
    state = _auction_states[room_code]
    
    if state['current_player_id'] is None:
        return None
    
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return None
    
    player_id = state['current_player_id']
    sold_price = state['current_bid']
    highest_bidder = state['highest_bidder']
    
    # Get auction player record
    auction_player = AuctionPlayer.query.filter_by(
        room_id=room.id,
        player_id=player_id
    ).first()
    
    if not auction_player:
        return None
    
    # Mark as sold
    auction_player.is_sold = True
    auction_player.sold_price = sold_price
    auction_player.sold_at = datetime.utcnow()
    
    # If there was a bidder, assign to team
    if highest_bidder:
        team = Team.query.filter_by(room_id=room.id, username=highest_bidder).first()
        if team:
            auction_player.sold_to_team_id = team.id
            
            # Create team player record
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player_id,
                price=sold_price
            )
            db.session.add(team_player)
            
            # Update team purse
            team.purse_left -= sold_price
    
    db.session.commit()
    
    # Clear current player from state
    state['current_player_id'] = None
    state['current_bid'] = None
    state['highest_bidder'] = None
    
    player = Player.query.get(player_id)
    
    return {
        'player': player,
        'sold_price': sold_price,
        'sold_to': highest_bidder,
        'team_id': auction_player.sold_to_team_id
    }


def get_current_auction_state(room_code):
    """
    Get current state of the auction.
    
    Args:
        room_code: Code of the room
        
    Returns:
        AuctionState: Current auction state
    """
    if room_code not in _auction_states:
        return AuctionState(room_code, auction_complete=False)
    
    state = _auction_states[room_code]
    
    current_player = None
    if state['current_player_id']:
        current_player = Player.query.get(state['current_player_id'])
    
    # Check if auction is complete
    room = Room.query.filter_by(code=room_code).first()
    auction_complete = False
    if room:
        unsold_count = AuctionPlayer.query.filter_by(
            room_id=room.id,
            is_sold=False
        ).count()
        # Only mark as complete if there are auction players and all are sold
        total_count = AuctionPlayer.query.filter_by(room_id=room.id).count()
        auction_complete = (total_count > 0 and unsold_count == 0)
    
    return AuctionState(
        room_code=room_code,
        current_player=current_player,
        current_bid=state['current_bid'],
        highest_bidder=state['highest_bidder'],
        timer_remaining=state.get('timer_duration', 30),
        auction_complete=auction_complete
    )
