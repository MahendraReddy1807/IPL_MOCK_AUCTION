"""TeamPlayer model."""
from datetime import datetime
from app import db


class TeamPlayer(db.Model):
    """TeamPlayer model for players in a team."""
    __tablename__ = 'team_players'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    in_playing_xi = db.Column(db.Boolean, default=False)
    is_impact_player = db.Column(db.Boolean, default=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    team = db.relationship('Team', back_populates='team_players')
    player = db.relationship('Player', back_populates='team_players')
