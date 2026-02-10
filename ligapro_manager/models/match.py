from extensions import db
from datetime import datetime, timezone
import uuid

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
    court_id = db.Column(db.String(36), db.ForeignKey('courts.id'), nullable=True) # Valid court ID
    home_team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    stage = db.Column(db.String(20), default='regular')  # regular, repechaje, quarterfinal, semifinal, final
    match_date = db.Column(db.DateTime, nullable=False)
    match_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
