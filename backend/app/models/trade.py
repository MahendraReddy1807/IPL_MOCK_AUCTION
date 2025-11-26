"""Trade models."""
from app import db
from datetime import datetime


class Trade(db.Model):
    """Player trade between teams."""
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), index=True)
    from_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    to_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    compensation = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, accepted, rejected, cancelled
    proposed_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_team = db.relationship('Team', foreign_keys=[from_team_id], backref='trades_sent')
    to_team = db.relationship('Team', foreign_keys=[to_team_id], backref='trades_received')
    player = db.relationship('Player', backref='trades')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'from_team_id': self.from_team_id,
            'from_team_name': self.from_team.team_name if self.from_team else None,
            'to_team_id': self.to_team_id,
            'to_team_name': self.to_team.team_name if self.to_team else None,
            'player_id': self.player_id,
            'player_name': self.player.name if self.player else None,
            'compensation': float(self.compensation) if self.compensation else 0,
            'status': self.status,
            'proposed_by': self.proposed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
