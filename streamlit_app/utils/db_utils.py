"""Database utilities."""
import time
from functools import wraps
from models import get_session, init_db


def retry_on_lock(max_retries=3, delay=0.5):
    """
    Decorator to retry database operations on lock.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if 'database is locked' in str(e).lower() and attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    raise e
            return None
        return wrapper
    return decorator


def initialize_database():
    """Initialize database and create all tables."""
    try:
        init_db()
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


def get_db_session():
    """Get a new database session."""
    return get_session()
