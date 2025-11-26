"""Room management service."""
import random
import string
from datetime import datetime
from models import get_session, Room, User


def generate_room_code(length=6):
    """
    Generate a unique room code.
    
    Args:
        length: Length of the room code (default 6)
        
    Returns:
        str: Unique room code
    """
    session = get_session()
    try:
        while True:
            # Generate random code with uppercase letters and digits
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            
            # Check if code already exists
            existing_room = session.query(Room).filter_by(code=code).first()
            if not existing_room:
                return code
    finally:
        session.close()


def create_room(host_username):
    """
    Create a new auction room.
    
    Args:
        host_username: Username of the host creating the room
        
    Returns:
        Room: Created room object
    """
    session = get_session()
    try:
        # Generate unique room code
        room_code = generate_room_code()
        
        # Create room
        room = Room(
            code=room_code,
            host_username=host_username,
            status='lobby'
        )
        
        session.add(room)
        session.commit()
        
        # Add host as first user
        host_user = User(username=host_username, room_id=room.id)
        session.add(host_user)
        session.commit()
        
        return room
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def join_room(room_code, username):
    """
    Join an existing auction room.
    
    Args:
        room_code: Code of the room to join
        username: Username of the user joining
        
    Returns:
        tuple: (success: bool, message: str, user: User or None)
    """
    session = get_session()
    try:
        # Validate room exists
        room = session.query(Room).filter_by(code=room_code).first()
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
        session.add(user)
        session.commit()
        
        return True, "Successfully joined room", user
    except Exception as e:
        session.rollback()
        return False, f"Error joining room: {str(e)}", None
    finally:
        session.close()


def get_room_participants(room_code):
    """
    Get list of participants in a room.
    
    Args:
        room_code: Code of the room
        
    Returns:
        list: List of User objects
    """
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return []
        
        return room.users
    finally:
        session.close()


def start_auction(room_code, host_username):
    """
    Start the auction for a room.
    
    Args:
        room_code: Code of the room
        host_username: Username of the host (for authorization)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    session = get_session()
    try:
        # Get room
        room = session.query(Room).filter_by(code=room_code).first()
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
        session.commit()
        
        return True, "Auction started successfully"
    except Exception as e:
        session.rollback()
        return False, f"Error starting auction: {str(e)}"
    finally:
        session.close()


def get_room(room_code):
    """
    Get room by code.
    
    Args:
        room_code: Code of the room
        
    Returns:
        Room or None: Room object if found
    """
    session = get_session()
    try:
        return session.query(Room).filter_by(code=room_code).first()
    finally:
        session.close()
