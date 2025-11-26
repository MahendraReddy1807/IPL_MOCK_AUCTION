"""Property-based tests for Room model."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models import Room
from app.services.room_service import create_room, generate_room_code
from app import db
import string


# Feature: ipl-mock-auction-arena, Property 4: Room capacity constraints
# Validates: Requirements 2.2, 2.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    room_code=st.text(alphabet=string.ascii_uppercase + string.digits, min_size=4, max_size=20)
)
def test_room_capacity_constraints(app, db_session, host_username, room_code):
    """
    Property 4: Room capacity constraints
    For any created room, the minimum participant count should be 2 
    and the maximum should be 10.
    """
    with app.app_context():
        # Create a room
        room = Room(
            code=room_code,
            host_username=host_username
        )
        
        db_session.add(room)
        db_session.commit()
        
        # Verify capacity constraints
        assert room.min_users == 2, f"Expected min_users to be 2, got {room.min_users}"
        assert room.max_users == 10, f"Expected max_users to be 10, got {room.max_users}"
        
        # Clean up
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 3: Room code uniqueness
# Validates: Requirements 2.1, 2.4
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_usernames=st.lists(
        st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
        min_size=2,
        max_size=20
    )
)
def test_room_code_uniqueness(app, db_session, host_usernames):
    """
    Property 3: Room code uniqueness
    For any set of created rooms, all room codes should be distinct from each other.
    """
    with app.app_context():
        created_rooms = []
        room_codes = set()
        
        # Create multiple rooms
        for host_username in host_usernames:
            room = create_room(host_username)
            created_rooms.append(room)
            
            # Check that this room code is unique
            assert room.code not in room_codes, f"Duplicate room code generated: {room.code}"
            room_codes.add(room.code)
        
        # Verify all codes are unique
        assert len(room_codes) == len(created_rooms), "Not all room codes are unique"
        
        # Clean up
        for room in created_rooms:
            db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 5: Invalid room code rejection
# Validates: Requirements 3.1
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    invalid_code=st.text(alphabet=string.ascii_uppercase + string.digits, min_size=1, max_size=20),
    username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100)
)
def test_invalid_room_code_rejection(app, db_session, invalid_code, username):
    """
    Property 5: Invalid room code rejection
    For any room code that does not exist in the system, join attempts should be 
    rejected with an appropriate error.
    """
    with app.app_context():
        from app.services.room_service import join_room
        
        # Ensure the code doesn't exist by checking database
        existing_room = Room.query.filter_by(code=invalid_code).first()
        
        # If by chance the code exists, skip this test case
        if existing_room:
            return
        
        # Attempt to join with non-existent room code
        success, message, user = join_room(invalid_code, username)
        
        # Verify rejection
        assert success is False, "Join should fail for non-existent room code"
        assert message == "Room not found", f"Expected 'Room not found', got '{message}'"
        assert user is None, "User should be None when join fails"


# Feature: ipl-mock-auction-arena, Property 6: Participant list consistency
# Validates: Requirements 3.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    joining_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100)
)
def test_participant_list_consistency(app, db_session, host_username, joining_username):
    """
    Property 6: Participant list consistency
    For any successful room join operation, the user should appear in the room's 
    participant list immediately after joining.
    """
    with app.app_context():
        from app.services.room_service import join_room, get_room_participants
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Join the room
        success, message, user = join_room(room_code, joining_username)
        
        # Verify join was successful
        assert success is True, f"Join should succeed, but got: {message}"
        assert user is not None, "User should not be None on successful join"
        
        # Get participant list
        participants = get_room_participants(room_code)
        
        # Verify user appears in participant list
        participant_usernames = [p.username for p in participants]
        assert joining_username in participant_usernames, \
            f"User '{joining_username}' should appear in participant list"
        
        # Verify user object is in the list
        assert user in participants, "User object should be in participant list"
        
        # Clean up
        db_session.delete(user)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 11: Auction start precondition
# Validates: Requirements 5.1
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    num_additional_participants=st.integers(min_value=0, max_value=0)
)
def test_auction_start_precondition(app, db_session, host_username, num_additional_participants):
    """
    Property 11: Auction start precondition
    For any room with fewer than 2 participants, attempting to start the auction 
    should be rejected.
    """
    with app.app_context():
        from app.services.room_service import join_room, start_auction
        
        # Create a room (host is automatically added as first participant)
        room = create_room(host_username)
        room_code = room.code
        
        # Add additional participants (total will be 1 + num_additional_participants, which is < 2)
        for i in range(num_additional_participants):
            username = f"user_{i}_{host_username[:5]}"
            join_room(room_code, username)
        
        # Verify we have fewer than 2 participants
        room = Room.query.filter_by(code=room_code).first()
        total_participants = len(room.users)
        assert total_participants < 2, f"Test setup error: should have < 2 participants, got {total_participants}"
        
        # Attempt to start auction
        success, message = start_auction(room_code, host_username)
        
        # Verify rejection
        assert success is False, "Auction start should fail with insufficient participants"
        assert "2 participants required" in message, \
            f"Expected message about minimum participants, got: {message}"
        
        # Verify room status is still lobby
        room = Room.query.filter_by(code=room_code).first()
        assert room.status == 'lobby', "Room status should remain 'lobby'"
        
        # Clean up
        for user in room.users:
            db_session.delete(user)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 12: Room state transition on auction start
# Validates: Requirements 5.2
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    num_participants=st.integers(min_value=2, max_value=10)
)
def test_room_state_transition(app, db_session, host_username, num_participants):
    """
    Property 12: Room state transition on auction start
    For any room in lobby state with sufficient participants, starting the auction 
    should transition the room to active state.
    """
    with app.app_context():
        from app.services.room_service import join_room, start_auction
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Verify initial state
        assert room.status == 'lobby', "Room should start in 'lobby' state"
        
        # Add sufficient participants (host is already added, so add num_participants - 1 more)
        for i in range(num_participants - 1):
            username = f"user_{i}_{host_username[:5]}"
            join_room(room_code, username)
        
        # Start auction
        success, message = start_auction(room_code, host_username)
        
        # Verify success
        assert success is True, f"Auction start should succeed, but got: {message}"
        
        # Verify room state transition
        room = Room.query.filter_by(code=room_code).first()
        assert room.status == 'active', f"Room status should be 'active', got '{room.status}'"
        
        # Clean up
        for user in room.users:
            db_session.delete(user)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 13: Join prevention in active auctions
# Validates: Requirements 5.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    late_joiner=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    num_participants=st.integers(min_value=2, max_value=10)
)
def test_join_prevention_in_active_auctions(app, db_session, host_username, late_joiner, num_participants):
    """
    Property 13: Join prevention in active auctions
    For any room in active state, join attempts should be rejected.
    """
    with app.app_context():
        from app.services.room_service import join_room, start_auction
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Add sufficient participants (host is already added, so add num_participants - 1 more)
        for i in range(num_participants - 1):
            username = f"user_{i}_{host_username[:5]}"
            join_room(room_code, username)
        
        # Start auction to make room active
        success, message = start_auction(room_code, host_username)
        assert success is True, "Auction should start successfully"
        
        # Verify room is active
        room = Room.query.filter_by(code=room_code).first()
        assert room.status == 'active', "Room should be in 'active' state"
        
        # Attempt to join active room
        success, message, user = join_room(room_code, late_joiner)
        
        # Verify rejection
        assert success is False, "Join should fail for active auction"
        assert message == "Cannot join active auction", \
            f"Expected 'Cannot join active auction', got '{message}'"
        assert user is None, "User should be None when join fails"
        
        # Clean up
        for user in room.users:
            db_session.delete(user)
        db_session.delete(room)
        db_session.commit()
