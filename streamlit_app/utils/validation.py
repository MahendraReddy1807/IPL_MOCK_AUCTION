"""Validation utilities."""
import re


def validate_username(username):
    """
    Validate username format.
    
    Args:
        username: Username string to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not username or not username.strip():
        return False, "Username cannot be empty"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Valid username"


def validate_team_name(team_name):
    """
    Validate team name format.
    
    Args:
        team_name: Team name string to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not team_name or not team_name.strip():
        return False, "Team name cannot be empty"
    
    team_name = team_name.strip()
    
    if len(team_name) < 3:
        return False, "Team name must be at least 3 characters"
    
    if len(team_name) > 30:
        return False, "Team name must be at most 30 characters"
    
    return True, "Valid team name"


def validate_purse(purse):
    """
    Validate purse amount.
    
    Args:
        purse: Purse amount to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    try:
        purse_float = float(purse)
    except (ValueError, TypeError):
        return False, "Purse must be a valid number"
    
    if purse_float <= 0:
        return False, "Purse must be greater than 0"
    
    if purse_float > 1000:
        return False, "Purse cannot exceed 1000 Lakhs"
    
    return True, "Valid purse amount"


def validate_room_code(room_code):
    """
    Validate room code format.
    
    Args:
        room_code: Room code string to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not room_code or not room_code.strip():
        return False, "Room code cannot be empty"
    
    room_code = room_code.strip().upper()
    
    if len(room_code) != 6:
        return False, "Room code must be exactly 6 characters"
    
    if not re.match(r'^[A-Z0-9]+$', room_code):
        return False, "Room code can only contain uppercase letters and numbers"
    
    return True, "Valid room code"
