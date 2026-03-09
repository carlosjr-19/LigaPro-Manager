from extensions import db
import uuid
from datetime import datetime, timezone

class IgnoredDiscrepancy(db.Model):
    __tablename__ = 'ignored_discrepancies'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    hash_id = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<IgnoredDiscrepancy {self.hash_id} for User {self.user_id}>'
