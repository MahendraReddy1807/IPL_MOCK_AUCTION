"""Room model."""
from datetime import datetime
from app import db


class Room(db.Model):
    """Room model for auction rooms."""
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='lobby')  # lobby, active, completed
    min_users = db.Column(db.Integer, default=5)
    max_users = db.Column(db.Integer, default=10)
    host_username = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teams = db.relationship('Team', back_populates='room', lazy=True)
    auction_players = db.relationship('AuctionPlayer', back_populates='room', lazy=True)
    users = db.relationship('User', back_populates='room', lazy=True)
