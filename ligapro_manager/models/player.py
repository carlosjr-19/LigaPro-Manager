from extensions import db
from datetime import datetime, timezone
import uuid

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    curp = db.Column(db.String(20), nullable=True)
    number = db.Column(db.Integer, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
