"""Achievement models."""
from app import db
from datetime import datetime


class Achievement(db.Model):
    """Achievement definition."""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    category = db.Column(db.String(50))  # auction, team_building, strategy, social, tournament
    criteria = db.Column(db.JSON)
    points = db.Column(db.Integer, default=0)
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'criteria': self.criteria,
            'points': self.points,
            'rarity': self.rarity
        }


class UserAchievement(db.Model):
    """User's earned achievements."""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'achievement_id': self.achievement_id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'room_id': self.room_id,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }
