"""Room management service."""
import random
import string
from datetime import datetime
from app import db
from app.models.room import Room
from app.models.simple_user import User


def generate_room_code(length=6):
    """
    Generate a unique room code.
    
    Args:
        length: Length of the room code (default 6)
        
    Returns:
        str: Unique room code
    """
    while True:
        # Generate random code with uppercase letters and digits
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        # Check if code already exists
        existing_room = Room.query.filter_by(code=code).first()
        if not existing_room:
            return code


def create_room(host_username):
    """
    Create a new auction room.
    
    Args:
        host_username: Username of the host creating the room
        
    Returns:
        Room: Created room object
    """
    # Generate unique room code
    room_code = generate_room_code()
    
    # Create room
    room = Room(
        code=room_code,
        host_username=host_username,
        status='lobby'
    )
    
    db.session.add(room)
    db.session.commit()
    
    # Add host as first user
    host_user = User(username=host_username, room_id=room.id)
    db.session.add(host_user)
    db.session.commit()
    
    return room


def join_room(room_code, username):
    """
    Join an existing auction room.
    
    Args:
        room_code: Code of the room to join
        username: Username of the user joining
        
    Returns:
        tuple: (success: bool, message: str, user: User or None)
    """
    # Validate room exists
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return False, "Room not found", None
    
    # Check if room is active or completed
    if room.status != 'lobby':
        return False, "Cannot join active auction", None
    
    # Check room capacity
    current_participants = len(room.users)
    if current_participants >= room.max_users:
        return False, "Room is full", None
    
    # Create user and add to room
    user = User(username=username, room_id=room.id)
    db.session.add(user)
    db.session.commit()
    
    return True, "Successfully joined room", user


def get_room_participants(room_code):
    """
    Get list of participants in a room.
    
    Args:
        room_code: Code of the room
        
    Returns:
        list: List of User objects
    """
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return []
    
    return room.users


def start_auction(room_code, host_username):
    """
    Start the auction for a room.
    
    Args:
        room_code: Code of the room
        host_username: Username of the host (for authorization)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Get room
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return False, "Room not found"
    
    # Verify host
    if room.host_username != host_username:
        return False, "Only host can start auction"
    
    # Check minimum participants
    current_participants = len(room.users)
    if current_participants < room.min_users:
        return False, f"At least {room.min_users} participants required to start auction"
    
    # Transition room to active
    room.status = 'active'
    db.session.commit()
    
    return True, "Auction started successfully"
