from extensions import db
from datetime import datetime, timezone
import uuid

class League(db.Model):
    __tablename__ = 'leagues'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    max_teams = db.Column(db.Integer, default=10)
    win_points = db.Column(db.Integer, default=3)
    draw_points = db.Column(db.Integer, default=1)
    loss_points = db.Column(db.Integer, default=0)
    num_vueltas = db.Column(db.Integer, default=1) # Premium feature: 1-5 rounds
    playoff_mode = db.Column(db.String(20), nullable=True)
    playoff_bye_teams = db.Column(db.Text, nullable=True)  # JSON string of team IDs
    show_stats = db.Column(db.Boolean, default=True)
    logo_url = db.Column(db.Text, nullable=True) # Premium only
    slogan = db.Column(db.String(255), nullable=True) # Premium only
    credential_color = db.Column(db.String(10), default='#dc2626') # Premium only
    show_team_logos = db.Column(db.Boolean, default=False) # Premium only
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    teams = db.relationship('Team', backref='league', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='league', lazy=True, cascade='all, delete-orphan')
    courts = db.relationship('Court', backref='league', lazy=True, cascade='all, delete-orphan')
    playoff_type = db.Column(db.String(20), default='single') # 'single' or 'double'
    price_per_match = db.Column(db.Integer, default=0) # Default cost for team per match
    price_referee = db.Column(db.Integer, default=0) # Default payment to referee per match
    charge_from_start = db.Column(db.Boolean, default=True)
    charge_start_date = db.Column(db.Date, nullable=True)
    
    # Premium Personalization for Reports
    highlight_standings = db.Column(db.Boolean, default=False)
    highlight_start = db.Column(db.Integer, default=1)
    highlight_end = db.Column(db.Integer, default=4)
    highlight_color = db.Column(db.String(10), default='#4ade80') # Tailwind green-400
    report_date_color = db.Column(db.String(10), default='#ffffff99') # White with opacity
    report_date_size = db.Column(db.Integer, default=14) # Default size in px

    @property
    def active_teams_count(self):
        return sum(1 for t in self.teams if not t.is_deleted and not t.is_hidden)
