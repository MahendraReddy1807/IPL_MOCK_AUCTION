"""Team model."""
from datetime import datetime
from app import db


class Team(db.Model):
    """Team model for user teams in auction."""
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    initial_purse = db.Column(db.Float, nullable=False)
    purse_left = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    room = db.relationship('Room', back_populates='teams')
    team_players = db.relationship('TeamPlayer', back_populates='team', lazy=True)
    team_rating = db.relationship('TeamRating', back_populates='team', uselist=False)
