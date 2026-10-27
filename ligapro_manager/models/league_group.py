from extensions import db
from datetime import datetime, timezone
import uuid

league_group_items = db.Table('league_group_items',
    db.Column('group_id', db.String(36), db.ForeignKey('league_groups.id', ondelete='CASCADE'), primary_key=True),
    db.Column('league_id', db.String(36), db.ForeignKey('leagues.id', ondelete='CASCADE'), primary_key=True)
)

class LeagueGroup(db.Model):
    __tablename__ = 'league_groups'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    color = db.Column(db.String(20), default='#3b82f6')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship with leagues
    leagues = db.relationship('League', secondary=league_group_items, backref=db.backref('groups', lazy='select'), lazy='subquery')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color or '#3b82f6',
            'league_ids': [l.id for l in self.leagues]
        }
