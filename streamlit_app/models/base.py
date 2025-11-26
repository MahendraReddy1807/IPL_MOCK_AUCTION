"""Base database setup for SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config

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
    Base.metadata.create_all(engine)


def get_session():
    """Get database session."""
    return Session()
