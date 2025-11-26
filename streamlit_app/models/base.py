"""Base database setup for SQLAlchemy."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config

# Database schema version - increment this when schema changes
DB_SCHEMA_VERSION = 4  # Force cache clear: min_users=2, timer=60s, session fix

# Create engine
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args={'check_same_thread': False} if 'sqlite' in Config.SQLALCHEMY_DATABASE_URI else {}
)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Create base class for models
Base = declarative_base()


def init_db():
    """Initialize database - create all tables."""
    # Check if we need to reset the database due to schema changes
    if 'sqlite' in Config.SQLALCHEMY_DATABASE_URI:
        db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        version_file = db_path + '.version'
        
        # Check current version
        current_version = None
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    current_version = int(f.read().strip())
            except:
                current_version = None
        
        # If version mismatch or no version file, drop and recreate
        if current_version != DB_SCHEMA_VERSION:
            # Try to remove old database
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except Exception as e:
                    # If we can't delete, try to drop all tables
                    try:
                        Base.metadata.drop_all(engine)
                    except:
                        pass
            
            # Remove old version file
            if os.path.exists(version_file):
                try:
                    os.remove(version_file)
                except:
                    pass
            
            # Create all tables with new schema
            Base.metadata.create_all(engine)
            
            # Write new version
            try:
                with open(version_file, 'w') as f:
                    f.write(str(DB_SCHEMA_VERSION))
            except:
                pass  # Non-critical if we can't write version
        else:
            # Version matches, just ensure tables exist
            Base.metadata.create_all(engine)
    else:
        # For non-SQLite databases, just create tables
        Base.metadata.create_all(engine)


def get_session():
    """Get database session."""
    return Session()
