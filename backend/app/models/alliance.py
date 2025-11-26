"""Alliance models."""
from app import db
from datetime import datetime


class Alliance(db.Model):
    """Team alliance."""
    __tablename__ = 'alliances'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'))
    name = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('AllianceMember', backref='alliance', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('AllianceMessage', backref='alliance', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_count': self.members.count()
        }


class AllianceMember(db.Model):
    """Alliance member."""
    __tablename__ = 'alliance_members'
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_id = db.Column(db.Integer, db.ForeignKey('alliances.id', ondelete='CASCADE'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    team = db.relationship('Team', backref='alliance_memberships')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'alliance_id': self.alliance_id,
            'team_id': self.team_id,
            'team_name': self.team.team_name if self.team else None,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }


class AllianceMessage(db.Model):
    """Alliance chat message."""
    __tablename__ = 'alliance_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_id = db.Column(db.Integer, db.ForeignKey('alliances.id', ondelete='CASCADE'))
    username = db.Column(db.String(100))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'alliance_id': self.alliance_id,
            'username': self.username,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
