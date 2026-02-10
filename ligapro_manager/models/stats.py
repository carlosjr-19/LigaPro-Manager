from extensions import db
from datetime import datetime, timezone
import uuid

class SeasonStat(db.Model):
    __tablename__ = 'season_stats'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(500), nullable=True)
    stat_type = db.Column(db.String(20), nullable=False)  # 'goals' or 'conceded'
    value = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    team = db.relationship('Team', backref='season_stats')
