"""Player model."""
from app import db


class Player(db.Model):
    """Player model for IPL players."""
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # BAT, BOWL, AR, WK
    country = db.Column(db.String(50), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    batting_score = db.Column(db.Float, nullable=False)
    bowling_score = db.Column(db.Float, nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    is_overseas = db.Column(db.Boolean, nullable=False)

    # Relationships
    auction_players = db.relationship('AuctionPlayer', back_populates='player', lazy=True)
    team_players = db.relationship('TeamPlayer', back_populates='player', lazy=True)
