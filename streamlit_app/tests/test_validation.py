"""Unit tests for validation utilities."""
import pytest
from utils.validation import (
    validate_username,
    validate_team_name,
    validate_purse,
    validate_room_code
)


class TestUsernameValidation:
    """Tests for username validation."""
    
    def test_valid_username(self):
        """Test valid username."""
        is_valid, msg = validate_username("testuser")
        assert is_valid is True
    
    def test_empty_username(self):
        """Test empty username."""
        is_valid, msg = validate_username("")
        assert is_valid is False
        assert "empty" in msg.lower()
    
    def test_short_username(self):
        """Test username too short."""
        is_valid, msg = validate_username("ab")
        assert is_valid is False
        assert "3" in msg
    
    def test_long_username(self):
        """Test username too long."""
        is_valid, msg = validate_username("a" * 25)
        assert is_valid is False
        assert "20" in msg
    
    def test_invalid_characters(self):
        """Test username with invalid characters."""
        is_valid, msg = validate_username("test@user")
        assert is_valid is False


class TestTeamNameValidation:
    """Tests for team name validation."""
    
    def test_valid_team_name(self):
        """Test valid team name."""
        is_valid, msg = validate_team_name("Mumbai Indians")
        assert is_valid is True
    
    def test_empty_team_name(self):
        """Test empty team name."""
        is_valid, msg = validate_team_name("")
        assert is_valid is False
    
    def test_short_team_name(self):
        """Test team name too short."""
        is_valid, msg = validate_team_name("MI")
        assert is_valid is False


class TestPurseValidation:
    """Tests for purse validation."""
    
    def test_valid_purse(self):
        """Test valid purse amount."""
        is_valid, msg = validate_purse(100.0)
        assert is_valid is True
    
    def test_zero_purse(self):
        """Test zero purse."""
        is_valid, msg = validate_purse(0)
        assert is_valid is False
    
    def test_negative_purse(self):
        """Test negative purse."""
        is_valid, msg = validate_purse(-10)
        assert is_valid is False
    
    def test_excessive_purse(self):
        """Test purse exceeding limit."""
        is_valid, msg = validate_purse(2000)
        assert is_valid is False


class TestRoomCodeValidation:
    """Tests for room code validation."""
    
    def test_valid_room_code(self):
        """Test valid room code."""
        is_valid, msg = validate_room_code("ABC123")
        assert is_valid is True
    
    def test_empty_room_code(self):
        """Test empty room code."""
        is_valid, msg = validate_room_code("")
        assert is_valid is False
    
    def test_wrong_length(self):
        """Test room code with wrong length."""
        is_valid, msg = validate_room_code("ABC")
        assert is_valid is False
    
    def test_lowercase(self):
        """Test lowercase room code (should be converted)."""
        is_valid, msg = validate_room_code("abc123")
        assert is_valid is True
