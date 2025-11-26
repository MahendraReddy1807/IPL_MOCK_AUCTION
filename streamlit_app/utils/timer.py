"""Timer utilities."""
from datetime import datetime, timedelta


def get_remaining_time(start_time, duration):
    """
    Calculate remaining time for a timer.
    
    Args:
        start_time: datetime when timer started
        duration: Total duration in seconds
        
    Returns:
        int: Remaining seconds (0 if expired)
    """
    if not start_time:
        return duration
    
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    remaining = max(0, duration - elapsed)
    
    return int(remaining)


def is_timer_expired(start_time, duration):
    """
    Check if timer has expired.
    
    Args:
        start_time: datetime when timer started
        duration: Total duration in seconds
        
    Returns:
        bool: True if expired, False otherwise
    """
    if not start_time:
        return False
    
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    return elapsed >= duration


def format_time(seconds):
    """
    Format seconds into MM:SS format.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        str: Formatted time string
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
