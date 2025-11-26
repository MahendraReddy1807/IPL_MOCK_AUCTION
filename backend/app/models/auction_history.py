"""Auction history and analytics models."""
from app import db
from datetime import datetime


class AuctionHistory(db.Model):
    """Historical record of auction sales."""
    __tablename__ = 'auction_history'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), index=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), index=True)
    winning_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    final_price = db.Column(db.Numeric(10, 2), nullable=False)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    num_bids = db.Column(db.Integer, default=0)
    bid_duration = db.Column(db.Integer)  # seconds
    is_bargain = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    player = db.relationship('Player', backref='auction_history')
    winning_team = db.relationship('Team', backref='auction_wins')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'player_id': self.player_id,
            'player_name': self.player.name if self.player else None,
            'winning_team_id': self.winning_team_id,
            'winning_team_name': self.winning_team.team_name if self.winning_team else None,
            'final_price': float(self.final_price),
            'base_price': float(self.base_price),
            'num_bids': self.num_bids,
            'bid_duration': self.bid_duration,
            'is_bargain': self.is_bargain,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ArchivedAuction(db.Model):
    """Archived completed auction."""
    __tablename__ = 'archived_auctions'
    
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), index=True)
    room_data = db.Column(db.JSON)
    teams_data = db.Column(db.JSON)
    players_data = db.Column(db.JSON)
    statistics = db.Column(db.JSON)
    completed_at = db.Column(db.DateTime, index=True)
    archived_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_code': self.room_code,
            'room_data': self.room_data,
            'teams_data': self.teams_data,
            'players_data': self.players_data,
            'statistics': self.statistics,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None
        }


class AnalyticsEvent(db.Model):
    """Analytics event tracking."""
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), index=True)
    username = db.Column(db.String(100))
    event_type = db.Column(db.String(50), index=True)  # bid_placed, player_won, rtm_used, etc.
    event_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'username': self.username,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Spectator(db.Model):
    """Spectator in a room."""
    __tablename__ = 'spectators'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), index=True)
    username = db.Column(db.String(100), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'username': self.username,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


class DraftPick(db.Model):
    """Draft mode pick."""
    __tablename__ = 'draft_picks'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), index=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    pick_number = db.Column(db.Integer, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    pick_time = db.Column(db.Integer)  # seconds taken
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    team = db.relationship('Team', backref='draft_picks')
    player = db.relationship('Player', backref='draft_picks')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'room_id': self.room_id,
            'team_id': self.team_id,
            'team_name': self.team.team_name if self.team else None,
            'player_id': self.player_id,
            'player_name': self.player.name if self.player else None,
            'pick_number': self.pick_number,
            'round_number': self.round_number,
            'pick_time': self.pick_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
