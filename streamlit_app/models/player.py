"""Player model."""
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from models.base import Base


class Player(Base):
    """Player model for IPL players."""
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(10), nullable=False)  # BAT, BOWL, AR, WK
    country = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    batting_score = Column(Float, nullable=False)
    bowling_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    is_overseas = Column(Boolean, nullable=False)

    # Relationships
    auction_players = relationship('AuctionPlayer', back_populates='player', lazy=True)
    team_players = relationship('TeamPlayer', back_populates='player', lazy=True)
