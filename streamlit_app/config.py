"""Configuration settings for the Streamlit application."""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
# Detect if running on Streamlit Cloud or if app directory is not writable
def get_db_path():
    """Get appropriate database path based on environment."""
    # Check for Streamlit Cloud environment variables
    if os.getenv('STREAMLIT_SHARING') or os.getenv('STREAMLIT_CLOUD') or os.getenv('HOSTNAME', '').startswith('streamlit'):
        return '/tmp/auction.db'
    
    # Check if app directory is writable
    test_file = BASE_DIR / '.write_test'
    try:
        test_file.touch()
        test_file.unlink()
        return f'{BASE_DIR}/auction.db'
    except:
        # Not writable, use /tmp
        return '/tmp/auction.db'

DB_PATH = get_db_path()
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')

# Application settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Auction settings
MIN_USERS = 2
MAX_USERS = 10
TIMER_DURATION = 60  # seconds
BID_INCREMENT = 5.0  # Lakhs
DEFAULT_PURSE = 100.0  # Lakhs

# File upload settings
UPLOAD_FOLDER = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Data files
PLAYERS_CSV = BASE_DIR / 'data' / 'players.csv'

# Polling settings
POLL_INTERVAL = 2  # seconds


class Config:
    """Configuration class."""
    
    # Database
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    
    # Auction
    MIN_USERS = MIN_USERS
    MAX_USERS = MAX_USERS
    TIMER_DURATION = TIMER_DURATION
    BID_INCREMENT = BID_INCREMENT
    DEFAULT_PURSE = DEFAULT_PURSE
    
    # Files
    UPLOAD_FOLDER = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    MAX_FILE_SIZE = MAX_FILE_SIZE
    PLAYERS_CSV = PLAYERS_CSV
    
    # Polling
    POLL_INTERVAL = POLL_INTERVAL
