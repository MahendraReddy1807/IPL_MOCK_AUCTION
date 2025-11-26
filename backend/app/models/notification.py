"""Notification models."""
from app import db
from datetime import datetime


class Notification(db.Model):
    """User notification."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(100), index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'))
    type = db.Column(db.String(50), nullable=False)  # bid_turn, budget_warning, player_recommendation, etc.
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    data = db.Column(db.JSON)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'room_id': self.room_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NotificationPreference(db.Model):
    """User notification preferences."""
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=True)
    email_address = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'username': self.username,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'push_notifications': self.push_notifications,
            'email_address': self.email_address,
            'phone_number': self.phone_number
        }
