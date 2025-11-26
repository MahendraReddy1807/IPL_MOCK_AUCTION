"""AuctionPlayer model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class AuctionPlayer(Base):
    """AuctionPlayer model for room-specific player state."""
    __tablename__ = 'auction_players'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    is_sold = Column(Boolean, default=False)
    sold_price = Column(Float, nullable=True)
    sold_to_team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    sold_at = Column(DateTime, nullable=True)

    # Relationships
    room = relationship('Room', back_populates='auction_players')
    player = relationship('Player', back_populates='auction_players')
    team = relationship('Team')
