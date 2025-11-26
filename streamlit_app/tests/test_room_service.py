"""Unit tests for room service."""
import pytest
from services import room_service


def test_generate_room_code():
    """Test room code generation."""
    code = room_service.generate_room_code()
    
    assert code is not None
    assert len(code) == 6
    assert code.isupper()
    assert code.isalnum()


def test_create_room():
    """Test room creation."""
    room = room_service.create_room("testuser")
    
    assert room is not None
    assert room.code is not None
    assert len(room.code) == 6
    assert room.host_username == "testuser"
    assert room.status == "lobby"


def test_join_room_success():
    """Test successful room join."""
    # Create room
    room = room_service.create_room("host")
    
    # Join room
    success, message, user = room_service.join_room(room.code, "player1")
    
    assert success is True
    assert "success" in message.lower()
    assert user is not None
    assert user.username == "player1"


def test_join_room_not_found():
    """Test joining non-existent room."""
    success, message, user = room_service.join_room("FAKE01", "player1")
    
    assert success is False
    assert "not found" in message.lower()
    assert user is None


def test_get_room_participants():
    """Test getting room participants."""
    # Create room
    room = room_service.create_room("host")
    
    # Join room
    room_service.join_room(room.code, "player1")
    room_service.join_room(room.code, "player2")
    
    # Get participants
    participants = room_service.get_room_participants(room.code)
    
    assert len(participants) == 3  # host + 2 players
    usernames = [p.username for p in participants]
    assert "host" in usernames
    assert "player1" in usernames
    assert "player2" in usernames


def test_start_auction_success():
    """Test successful auction start."""
    # Create room with enough participants
    room = room_service.create_room("host")
    for i in range(4):
        room_service.join_room(room.code, f"player{i}")
    
    # Start auction
    success, message = room_service.start_auction(room.code, "host")
    
    assert success is True
    assert "success" in message.lower()


def test_start_auction_not_host():
    """Test auction start by non-host."""
    room = room_service.create_room("host")
    room_service.join_room(room.code, "player1")
    
    success, message = room_service.start_auction(room.code, "player1")
    
    assert success is False
    assert "host" in message.lower()


def test_start_auction_insufficient_participants():
    """Test auction start with too few participants."""
    room = room_service.create_room("host")
    
    success, message = room_service.start_auction(room.code, "host")
    
    assert success is False
    assert "participants" in message.lower() or "required" in message.lower()
