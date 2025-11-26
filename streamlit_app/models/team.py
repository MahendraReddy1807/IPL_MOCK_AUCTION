"""Team model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Team(Base):
    """Team model for user teams in auction."""
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    username = Column(String(100), nullable=False)
    team_name = Column(String(100), nullable=False)
    logo_url = Column(String(255), nullable=True)
    initial_purse = Column(Float, nullable=False)
    purse_left = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    room = relationship('Room', back_populates='teams')
    team_players = relationship('TeamPlayer', back_populates='team', lazy=True)
    team_rating = relationship('TeamRating', back_populates='team', uselist=False)
