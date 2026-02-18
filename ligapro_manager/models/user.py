from extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='owner')  # owner or captain
    is_premium = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    is_suspended = db.Column(db.Boolean, default=False)
    is_ultra = db.Column(db.Boolean, default=False)
    color_win = db.Column(db.String(7), default='#22c55e') # Green-500
    color_loss = db.Column(db.String(7), default='#ef4444') # Red-500
    highlight_mode = db.Column(db.String(20), default='simple') # 'simple' or 'full'
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    @property
    def is_active_premium(self):
        """Check if user has active premium (lifetime or temporary)"""
        if self.is_premium:
            return True
        
        if self.premium_expires_at:
            # Handle timezone awareness for comparison
            expires_at = self.premium_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at > datetime.now(timezone.utc):
                return True
                
        return False

    # Relationships
    leagues = db.relationship('League', backref='owner', lazy=True, cascade='all, delete-orphan', foreign_keys='League.user_id')
