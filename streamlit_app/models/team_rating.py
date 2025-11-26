"""TeamRating model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class TeamRating(Base):
    """TeamRating model for storing computed team ratings."""
    __tablename__ = 'team_ratings'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    overall_rating = Column(Float, nullable=False)
    batting_rating = Column(Float, nullable=False)
    bowling_rating = Column(Float, nullable=False)
    balance_score = Column(Float, nullable=False)
    bench_depth = Column(Float, nullable=False)
    role_coverage = Column(Float, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship('Team', back_populates='team_rating')
