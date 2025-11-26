"""TeamPlayer model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class TeamPlayer(Base):
    """TeamPlayer model for players in a team."""
    __tablename__ = 'team_players'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    price = Column(Float, nullable=False)
    in_playing_xi = Column(Boolean, default=False)
    is_impact_player = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship('Team', back_populates='team_players')
    player = relationship('Player', back_populates='team_players')
