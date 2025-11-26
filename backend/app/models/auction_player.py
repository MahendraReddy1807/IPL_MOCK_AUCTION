"""AuctionPlayer model."""
from datetime import datetime
from app import db


class AuctionPlayer(db.Model):
    """AuctionPlayer model for room-specific player state."""
    __tablename__ = 'auction_players'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    is_sold = db.Column(db.Boolean, default=False)
    sold_price = db.Column(db.Float, nullable=True)
    sold_to_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    sold_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    room = db.relationship('Room', back_populates='auction_players')
    player = db.relationship('Player', back_populates='auction_players')
    team = db.relationship('Team')
