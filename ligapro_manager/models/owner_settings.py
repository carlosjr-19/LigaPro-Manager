from extensions import db
import uuid
from datetime import datetime, timezone

class OwnerCourtSetting(db.Model):
    __tablename__ = 'owner_court_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    court_name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), default='#16a34a')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Establish relationship to user
    user = db.relationship('User', backref=db.backref('court_settings', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<OwnerCourtSetting {self.court_name} for User {self.user_id}>'
