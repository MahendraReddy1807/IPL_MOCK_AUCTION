"""User model for authentication and profiles."""
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Account(db.Model):
    """User account model for authentication (future feature)."""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500))
    bio = db.Column(db.Text)
    theme = db.Column(db.String(10), default='light')
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    reset_token = db.Column(db.String(255))
    reset_token_expires = db.Column(db.DateTime)
    
    # Relationships
    profile = db.relationship('AccountProfile', backref='account', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'theme': self.theme,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class AccountProfile(db.Model):
    """Account profile with statistics."""
    __tablename__ = 'account_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete='CASCADE'), unique=True)
    total_auctions = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Numeric(12, 2), default=0)
    favorite_role = db.Column(db.String(10))
    achievement_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    preferences = db.Column(db.JSON)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'account_id': self.account_id,
            'total_auctions': self.total_auctions,
            'total_wins': self.total_wins,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'favorite_role': self.favorite_role,
            'achievement_points': self.achievement_points,
            'level': self.level,
            'preferences': self.preferences or {}
        }


class Friendship(db.Model):
    """Friendship/connection between accounts."""
    __tablename__ = 'friendships'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete='CASCADE'))
    friend_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete='CASCADE'))
    status = db.Column(db.String(20), default='pending')  # pending, accepted, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'account_id': self.account_id,
            'friend_id': self.friend_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
