"""Pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Base, engine, Session


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    session = Session()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def sample_room(db_session):
    """Create a sample room for testing."""
    from models import Room
    
    room = Room(
        code="TEST01",
        host_username="testhost",
        status="lobby"
    )
    db_session.add(room)
    db_session.commit()
    
    return room


@pytest.fixture(scope="function")
def sample_player(db_session):
    """Create a sample player for testing."""
    from models import Player
    
    player = Player(
        name="Test Player",
        role="BAT",
        country="India",
        base_price=10.0,
        batting_score=75.0,
        bowling_score=25.0,
        overall_score=50.0,
        is_overseas=False
    )
    db_session.add(player)
    db_session.commit()
    
    return player
