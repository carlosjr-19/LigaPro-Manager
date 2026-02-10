from extensions import db
from datetime import datetime, timezone
import uuid

class Court(db.Model):
    __tablename__ = 'courts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    matches = db.relationship('Match', backref='court', lazy=True)
