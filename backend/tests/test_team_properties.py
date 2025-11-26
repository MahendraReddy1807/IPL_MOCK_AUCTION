"""Property-based tests for Team model."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from app.models import Team, Room
from app.utils import validate_purse_amount
from app import db
import string


# Feature: ipl-mock-auction-arena, Property 10: Purse amount validation
# Validates: Requirements 4.4
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    purse_amount=st.one_of(
        st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1000.0, max_value=-0.01, allow_nan=False, allow_infinity=False),
        st.just(0.0),
        st.just(-1.0)
    )
)
def test_purse_amount_validation_rejects_invalid(app, db_session, purse_amount):
    """
    Property 10: Purse amount validation
    For any purse amount that is not a positive number, the validation function should reject it.
    """
    # Test that the validation function correctly rejects non-positive values
    result = validate_purse_amount(purse_amount)
    assert result is False, f"Expected validation to reject {purse_amount}, but it was accepted"


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    purse_amount=st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
)
def test_purse_amount_validation_accepts_valid(app, db_session, purse_amount):
    """
    Property 10: Purse amount validation (positive case)
    For any purse amount that is a positive number, the validation function should accept it.
    """
    # Test that the validation function correctly accepts positive values
    result = validate_purse_amount(purse_amount)
    assert result is True, f"Expected validation to accept {purse_amount}, but it was rejected"
    
    with app.app_context():
        # Also verify we can create a team with valid purse
        room = Room(
            code=f"TEST{abs(hash(purse_amount)) % 10000}",
            host_username="testhost"
        )
        db_session.add(room)
        db_session.commit()
        
        team = Team(
            room_id=room.id,
            username="testuser",
            team_name="Test Team",
            initial_purse=purse_amount,
            purse_left=purse_amount
        )
        
        db_session.add(team)
        db_session.commit()
        
        # Verify the team was created successfully
        assert team.id is not None
        assert team.initial_purse == purse_amount
        assert team.purse_left == purse_amount
        
        # Clean up
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 1: Username validation rejects empty inputs
# Validates: Requirements 1.2
@settings(max_examples=100)
@given(
    username=st.one_of(
        st.just(''),  # Empty string
        st.just('   '),  # Whitespace only
        st.just('\t\n'),  # Tabs and newlines
        st.text(alphabet=string.whitespace, min_size=1, max_size=10)  # Various whitespace
    )
)
def test_username_validation_rejects_empty(username):
    """
    Property 1: Username validation rejects empty inputs
    For any username input that is empty or contains only whitespace, 
    the system should reject it and prevent user entry.
    """
    from app.utils.validation import validate_username
    
    # Validate username
    is_valid = validate_username(username)
    
    # Should be rejected
    assert is_valid is False, f"Username '{repr(username)}' should be rejected"


# Feature: ipl-mock-auction-arena, Property 8: Team name validation
# Validates: Requirements 4.2
@settings(max_examples=100)
@given(
    team_name=st.one_of(
        st.just(''),  # Empty string
        st.just('   '),  # Whitespace only
        st.just('\t\n'),  # Tabs and newlines
        st.text(alphabet=string.whitespace, min_size=1, max_size=10)  # Various whitespace
    )
)
def test_team_name_validation(team_name):
    """
    Property 8: Team name validation
    For any team name input that is empty or contains only whitespace, 
    the system should reject it.
    """
    from app.utils.validation import validate_team_name
    
    # Validate team name
    is_valid = validate_team_name(team_name)
    
    # Should be rejected
    assert is_valid is False, f"Team name '{repr(team_name)}' should be rejected"


# Feature: ipl-mock-auction-arena, Property 9: Logo file persistence
# Validates: Requirements 4.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    filename=st.text(alphabet=string.ascii_letters + string.digits + '._-', min_size=5, max_size=50)
)
def test_logo_file_persistence(app, db_session, filename, tmp_path):
    """
    Property 9: Logo file persistence
    For any uploaded logo file, the system should store it and return a valid URL 
    that can be used to retrieve the file.
    """
    with app.app_context():
        from app.services.team_service import upload_logo
        from werkzeug.datastructures import FileStorage
        import io
        
        # Ensure filename has an extension
        if '.' not in filename:
            filename = filename + '.png'
        
        # Create a mock file
        file_content = b'fake image content'
        file = FileStorage(
            stream=io.BytesIO(file_content),
            filename=filename,
            content_type='image/png'
        )
        
        # Use tmp_path for upload folder
        upload_folder = str(tmp_path / 'logos')
        
        # Upload the file
        success, message, file_path = upload_logo(file, upload_folder)
        
        # Verify success
        assert success is True, f"Upload should succeed, got: {message}"
        assert file_path is not None, "File path should not be None"
        
        # Verify file exists
        import os
        assert os.path.exists(file_path), f"File should exist at {file_path}"
        
        # Verify file content
        with open(file_path, 'rb') as f:
            saved_content = f.read()
        assert saved_content == file_content, "File content should match"


# Feature: ipl-mock-auction-arena, Property 22: Purse deduction on player win
# Validates: Requirements 9.1
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=100),
    initial_purse=st.floats(min_value=100.0, max_value=10000.0),
    player_price=st.floats(min_value=1.0, max_value=100.0)
)
def test_purse_deduction_on_player_win(app, db_session, host_username, team_name, initial_purse, player_price):
    """
    Property 22: Purse deduction on player win
    For any player won by a team, the team's purse should decrease by exactly 
    the sold price.
    """
    with app.app_context():
        from app.services.room_service import create_room
        from app.services.team_service import configure_team, add_player_to_team
        from app.models.player import Player
        
        # Create a room
        room = create_room(host_username)
        
        # Configure team
        success, message, team = configure_team(room.id, host_username, team_name, initial_purse)
        assert success is True, f"Team configuration should succeed: {message}"
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Record initial purse
        initial_purse_left = team.purse_left
        
        # Add player to team
        success, message, team_player = add_player_to_team(team.id, player.id, player_price)
        
        # Skip if price exceeds purse
        if not success and "Insufficient" in message:
            return
        
        assert success is True, f"Adding player should succeed: {message}"
        
        # Refresh team to get updated purse
        db_session.refresh(team)
        
        # Verify purse deduction
        expected_purse = initial_purse_left - player_price
        assert abs(team.purse_left - expected_purse) < 0.01, \
            f"Purse should be {expected_purse}, got {team.purse_left}"
        
        # Clean up
        db_session.delete(team_player)
        db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()
