from extensions import db
import uuid
from datetime import datetime, timezone

class ArchivedFinance(db.Model):
    __tablename__ = 'archived_finances'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    league_name = db.Column(db.String(100), nullable=False)
    court_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    income = db.Column(db.Integer, default=0)
    expense = db.Column(db.Integer, default=0)
    profit = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<ArchivedFinance {self.league_name} on {self.date} for User {self.user_id}>'
