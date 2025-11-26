"""TeamRating model."""
from datetime import datetime
from app import db


class TeamRating(db.Model):
    """TeamRating model for storing computed team ratings."""
    __tablename__ = 'team_ratings'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    overall_rating = db.Column(db.Float, nullable=False)
    batting_rating = db.Column(db.Float, nullable=False)
    bowling_rating = db.Column(db.Float, nullable=False)
    balance_score = db.Column(db.Float, nullable=False)
    bench_depth = db.Column(db.Float, nullable=False)
    role_coverage = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    team = db.relationship('Team', back_populates='team_rating')
