"""Room model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from models.base import Base


class Room(Base):
    """Room model for auction rooms."""
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    status = Column(String(20), default='lobby')  # lobby, active, completed
    min_users = Column(Integer, default=5)
    max_users = Column(Integer, default=10)
    host_username = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teams = relationship('Team', back_populates='room', lazy=True)
    auction_players = relationship('AuctionPlayer', back_populates='room', lazy=True)
    users = relationship('User', back_populates='room', lazy=True)
