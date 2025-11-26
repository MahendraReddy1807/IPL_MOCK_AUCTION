"""Validation utilities for the application."""


def validate_purse_amount(purse_amount):
    """
    Validate purse amount.
    
    Args:
        purse_amount: The purse amount to validate
        
    Returns:
        bool: True if valid (positive number), False otherwise
        
    Validates: Requirements 4.4
    """
    if purse_amount is None:
        return False
    if not isinstance(purse_amount, (int, float)):
        return False
    if purse_amount <= 0:
        return False
    return True


def validate_username(username):
    """
    Validate username.
    
    Args:
        username: The username to validate
        
    Returns:
        bool: True if valid (non-empty), False otherwise
        
    Validates: Requirements 1.2
    """
    if username is None:
        return False
    if not isinstance(username, str):
        return False
    if len(username.strip()) == 0:
        return False
    return True


def validate_team_name(team_name):
    """
    Validate team name.
    
    Args:
        team_name: The team name to validate
        
    Returns:
        bool: True if valid (non-empty), False otherwise
        
    Validates: Requirements 4.2
    """
    if team_name is None:
        return False
    if not isinstance(team_name, str):
        return False
    if len(team_name.strip()) == 0:
        return False
    return True
