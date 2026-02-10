from extensions import db
from datetime import datetime, timezone
import uuid

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
    shield_url = db.Column(db.Text, nullable=True)
    captain_user_id = db.Column(db.String(36), nullable=True)
    captain_email = db.Column(db.String(120), nullable=True)
    captain_password_plain = db.Column(db.String(50), nullable=True)
    captain_name = db.Column(db.String(100), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='team_ref', lazy=True, cascade='all, delete-orphan', foreign_keys='User.team_id')
    notes = db.relationship('TeamNote', backref='team', lazy=True, cascade='all, delete-orphan')
    home_matches = db.relationship('Match', backref='home_team', lazy=True, foreign_keys='Match.home_team_id')
    away_matches = db.relationship('Match', backref='away_team', lazy=True, foreign_keys='Match.away_team_id')
    
    # Captain Relationship (Virtual)
    captain = db.relationship('User', 
                             primaryjoin="Team.captain_user_id == User.id",
                             foreign_keys=captain_user_id,
                             uselist=False,
                             viewonly=True)


class TeamNote(db.Model):
    __tablename__ = 'team_notes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
