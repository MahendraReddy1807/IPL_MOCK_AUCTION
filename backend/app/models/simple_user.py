"""Simple User model for tracking participants in auction rooms."""
from datetime import datetime
from app import db


class User(db.Model):
    """Simple user model for auction participants."""
    __tablename__ = 'simple_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    room = db.relationship('Room', back_populates='users', lazy=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'room_id': self.room_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
