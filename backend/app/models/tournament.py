"""Tournament models."""
from app import db
from datetime import datetime


class Tournament(db.Model):
    """Tournament definition."""
    __tablename__ = 'tournaments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    status = db.Column(db.String(20), default='setup')  # setup, active, completed
    tournament_type = db.Column(db.String(20), default='bracket')  # bracket, league, knockout
    max_teams = db.Column(db.Integer, default=8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    rooms = db.relationship('Room', backref='tournament', lazy='dynamic')
    standings = db.relationship('TournamentStanding', backref='tournament', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'status': self.status,
            'tournament_type': self.tournament_type,
            'max_teams': self.max_teams,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_rooms': self.rooms.count()
        }


class TournamentStanding(db.Model):
    """Tournament standings/leaderboard."""
    __tablename__ = 'tournament_standings'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id', ondelete='CASCADE'), index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    points = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)
    total_spent = db.Column(db.Numeric(10, 2))
    team_strength = db.Column(db.Numeric(5, 2))
    
    # Relationships
    team = db.relationship('Team', backref='tournament_standings')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'team_id': self.team_id,
            'team_name': self.team.team_name if self.team else None,
            'room_id': self.room_id,
            'points': self.points,
            'rank': self.rank,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'team_strength': float(self.team_strength) if self.team_strength else 0
        }
