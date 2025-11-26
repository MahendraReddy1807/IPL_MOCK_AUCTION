"""Simple User model for tracking participants in auction rooms."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class User(Base):
    """Simple user model for auction participants."""
    __tablename__ = 'simple_users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    room = relationship('Room', back_populates='users', lazy=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'room_id': self.room_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
