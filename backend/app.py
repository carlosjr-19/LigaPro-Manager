"""
LigaPro Manager - Flask Application
Full-stack football league management with PostgreSQL
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, DateTimeField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, InputRequired
from datetime import datetime, timezone
from functools import wraps
from dotenv import load_dotenv
import os
import uuid
import stripe
from datetime import datetime, timezone, timedelta

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ligapro-secret-key-change-in-production')
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'ligapro.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
app.config['STRIPE_PUBLIC_KEY'] = os.environ.get('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY')
app.config['STRIPE_PRICE_ID'] = os.environ.get('STRIPE_PRICE_ID')
app.config['STRIPE_CAPTAIN_PRICE_ID'] = os.environ.get('STRIPE_CAPTAIN_PRICE_ID')
stripe.api_key = app.config['STRIPE_SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='owner')  # owner or captain
    is_premium = db.Column(db.Boolean, default=False)
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
    leagues = db.relationship('League', backref='owner', lazy=True, foreign_keys='League.user_id')


class League(db.Model):
    __tablename__ = 'leagues'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    max_teams = db.Column(db.Integer, default=10)
    win_points = db.Column(db.Integer, default=3)
    draw_points = db.Column(db.Integer, default=1)
    loss_points = db.Column(db.Integer, default=0)
    playoff_mode = db.Column(db.String(20), nullable=True)
    playoff_bye_teams = db.Column(db.Text, nullable=True)  # JSON string of team IDs
    show_stats = db.Column(db.Boolean, default=True)
    logo_url = db.Column(db.Text, nullable=True) # Premium only
    slogan = db.Column(db.String(255), nullable=True) # Premium only
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    teams = db.relationship('Team', backref='league', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='league', lazy=True, cascade='all, delete-orphan')
    courts = db.relationship('Court', backref='league', lazy=True, cascade='all, delete-orphan')
    playoff_type = db.Column(db.String(20), default='single') # 'single' or 'double'


class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
    shield_url = db.Column(db.Text, nullable=True)
    captain_user_id = db.Column(db.String(36), nullable=True)
    captain_email = db.Column(db.String(120), nullable=True)
    captain_password_plain = db.Column(db.String(50), nullable=True)
    captain_name = db.Column(db.String(100), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('TeamNote', backref='team', lazy=True, cascade='all, delete-orphan')
    home_matches = db.relationship('Match', backref='home_team', lazy=True, foreign_keys='Match.home_team_id')
    away_matches = db.relationship('Match', backref='away_team', lazy=True, foreign_keys='Match.away_team_id')
    
    # Captain Relationship (Virtual)
    captain = db.relationship('User', 
                             primaryjoin="Team.captain_user_id == User.id",
                             foreign_keys=captain_user_id,
                             uselist=False,
                             viewonly=True)


class TeamNote(db.Model):
    __tablename__ = 'team_notes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=False)
    curp = db.Column(db.String(20), nullable=True)
    number = db.Column(db.Integer, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Court(db.Model):
    __tablename__ = 'courts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    matches = db.relationship('Match', backref='court', lazy=True)


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


# ==================== FORMS ====================

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])


class LeagueForm(FlaskForm):
    name = StringField('Nombre de la Liga', validators=[DataRequired(), Length(min=2, max=100)])
    max_teams = IntegerField('Máximo de Equipos', validators=[DataRequired(), NumberRange(min=4, max=32)], default=10)
    win_points = IntegerField('Puntos por Victoria', validators=[DataRequired()], default=3)
    draw_points = IntegerField('Puntos por Empate', validators=[DataRequired()], default=1)
    # Field handles by template conditional, but need it in form
    show_stats = BooleanField('Mostrar Estadísticas a Capitanes', default=True)
    logo_url = StringField('URL del Logo (Premium)', validators=[Optional()])
    slogan = StringField('Slogan de la Liga (Premium)', validators=[Optional(), Length(max=255)])


class TeamForm(FlaskForm):
    name = StringField('Nombre del Equipo', validators=[DataRequired(), Length(min=2, max=100)])
    shield_url = StringField('URL del Escudo', validators=[Optional()])
    captain_name = StringField('Nombre del Capitán', validators=[Optional()])


class PlayerForm(FlaskForm):
    name = StringField('Nombre del Jugador', validators=[DataRequired(), Length(min=2, max=100)])
    number = IntegerField('Número (Dorsal)', validators=[Optional()])
    curp = StringField('CURP', validators=[Optional(), Length(max=20)])
    photo_url = StringField('URL de Foto', validators=[Optional()])


class MatchForm(FlaskForm):
    home_team_id = SelectField('Equipo Local', validators=[DataRequired()])
    away_team_id = SelectField('Equipo Visitante', validators=[DataRequired()])
    court_id = SelectField('Cancha', validators=[DataRequired()])
    match_date = DateTimeField('Fecha y Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])


class MatchResultForm(FlaskForm):
    home_score = IntegerField('Goles Local', validators=[InputRequired(), NumberRange(min=0)])
    away_score = IntegerField('Goles Visitante', validators=[InputRequired(), NumberRange(min=0)])


class TeamNoteForm(FlaskForm):
    text = TextAreaField('Nota', validators=[DataRequired()])


class StatForm(FlaskForm):
    player_name = StringField('Nombre del Jugador', validators=[DataRequired(), Length(max=100)])
    team_id = SelectField('Equipo', validators=[DataRequired()])
    photo_url = StringField('URL Foto (Opcional)', validators=[Optional()])
    value = IntegerField('Cantidad', validators=[InputRequired(), NumberRange(min=0)])
    stat_type = StringField('Tipo', validators=[DataRequired()])


# ==================== HELPERS ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def owner_required(f):
    """Decorator to require owner role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'owner' and current_user.role != 'admin':
            flash('Acceso denegado. Solo para administradores.', 'danger')
            return redirect(url_for('captain_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """Decorator to require premium subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_active_premium:
            flash('Esta función requiere suscripción Premium.', 'warning')
            return redirect(url_for('premium'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Acceso denegado. Solo para administradores del sistema.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def calculate_standings(league_id, include_playoffs=False):
    """Calculate standings for a league"""
    league = League.query.get_or_404(league_id)
    # Only show active teams in standings
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    
    # Get completed matches (only regular season by default)
    if include_playoffs:
        matches = Match.query.filter_by(league_id=league_id, is_completed=True).all()
    else:
        matches = Match.query.filter(
            Match.league_id == league_id,
            Match.is_completed == True,
            Match.stage.in_(['regular', None])
        ).all()
    
    standings = []
    for team in teams:
        stats = {
            'team': team,
            'played': 0,
            'won': 0,
            'drawn': 0,
            'lost': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'points': 0
        }
        
        for match in matches:
            if match.home_team_id == team.id:
                stats['played'] += 1
                stats['goals_for'] += match.home_score or 0
                stats['goals_against'] += match.away_score or 0
                
                if match.home_score > match.away_score:
                    stats['won'] += 1
                    stats['points'] += league.win_points
                elif match.home_score == match.away_score:
                    stats['drawn'] += 1
                    stats['points'] += league.draw_points
                else:
                    stats['lost'] += 1
                    
            elif match.away_team_id == team.id:
                stats['played'] += 1
                stats['goals_for'] += match.away_score or 0
                stats['goals_against'] += match.home_score or 0
                
                if match.away_score > match.home_score:
                    stats['won'] += 1
                    stats['points'] += league.win_points
                elif match.away_score == match.home_score:
                    stats['drawn'] += 1
                    stats['points'] += league.draw_points
                else:
                    stats['lost'] += 1
        
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        standings.append(stats)
    
    # Sort by points, goal difference, goals for
    standings.sort(key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
    return standings


# ==================== AUTH ROUTES ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        next_page = request.args.get('next') # Added this line to define next_page
        if current_user.role == 'admin':
            return redirect(next_page or url_for('admin_dashboard'))
        if current_user.role == 'captain':
            return redirect(next_page or url_for('captain_dashboard'))
        return redirect(next_page or url_for('dashboard'))
    return render_template('landing.html', title='Inicio')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('¡Bienvenido!', 'success')
            next_page = request.args.get('next')
            if current_user.role == 'admin':
                return redirect(next_page or url_for('admin_dashboard'))
            if current_user.role == 'captain':
                return redirect(next_page or url_for('captain_dashboard'))
            return redirect(next_page or url_for('dashboard'))
        flash('Email o contraseña incorrectos.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash('Este email ya está registrado.', 'danger')
        else:
            hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                name=form.name.data,
                email=form.email.data,
                password=hashed,
                role='owner'
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('¡Cuenta creada exitosamente!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    step = 'email'
    if 'reset_user_id' in session:
        step = 'password'
        
    if request.method == 'POST':
        if step == 'email':
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            
            if user:
                session['reset_user_id'] = user.id
                flash('Usuario encontrado. Por favor establece tu nueva contraseña.', 'success')
                return redirect(url_for('forgot_password'))
            else:
                flash('No encontramos una cuenta con ese correo.', 'danger')
                
        elif step == 'password':
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')
            
            if password != confirm:
                flash('Las contraseñas no coinciden.', 'danger')
            else:
                user_id = session.get('reset_user_id')
                user = User.query.get(user_id)
                
                if user:
                    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
                    user.password = hashed
                    db.session.commit()
                    
                    session.pop('reset_user_id', None)
                    flash('Contraseña actualizada exitosamente. Inicia sesión.', 'success')
                    return redirect(url_for('login'))
                else:
                    session.pop('reset_user_id', None)
                    flash('Error de sesión. Intenta de nuevo.', 'danger')
                    return redirect(url_for('forgot_password'))
                    
    return render_template('forgot_password.html', step=step)


# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
@owner_required
def dashboard():
    leagues = League.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', leagues=leagues)


@app.route('/captain')
@login_required
def captain_dashboard():
    if current_user.role != 'captain':
        return redirect(url_for('dashboard'))
    
    team = Team.query.get(current_user.team_id)
    if not team:
        flash('No tienes equipo asignado.', 'warning')
        return redirect(url_for('logout'))
    
    league = team.league
    standings = calculate_standings(league.id)
    
    # Get team matches
    matches = Match.query.filter(
        (Match.home_team_id == team.id) | (Match.away_team_id == team.id)
    ).order_by(Match.match_date.desc()).all()
    
    # Get all teams for name lookup
    teams_dict = {t.id: t for t in Team.query.filter_by(league_id=league.id).all()}
    
    # Get Top 5 Stats (if allowed)
    top_scorers = []
    top_goalkeepers = []
    
    if league.show_stats:
        top_scorers = SeasonStat.query.filter_by(league_id=league.id, stat_type='goals')\
            .order_by(SeasonStat.value.desc()).limit(5).all()
        top_goalkeepers = SeasonStat.query.filter_by(league_id=league.id, stat_type='conceded')\
            .order_by(SeasonStat.value.asc()).limit(5).all()
    
    return render_template('captain_dashboard.html', 
                          team=team, 
                          league=league, 
                          standings=standings,
                          matches=matches,
                          teams_dict=teams_dict,
                          top_scorers=top_scorers,
                          top_goalkeepers=top_goalkeepers)


# ==================== LEAGUE ROUTES ====================

@app.route('/leagues/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_league():
    # Check league limit for non-premium users
    if not current_user.is_premium:
        league_count = League.query.filter_by(user_id=current_user.id).count()
        if league_count >= 3:
            flash('Usuarios gratuitos pueden crear máximo 3 ligas. Actualiza a Premium.', 'warning')
            return redirect(url_for('premium'))
    
    form = LeagueForm()
    if form.validate_on_submit():
        max_teams = form.max_teams.data
        win_points = form.win_points.data
        draw_points = form.draw_points.data
        
        # Enforce Free Tier Limits (Override even if client bypassed disabled inputs)
        if not current_user.is_premium:
            max_teams = 10
            win_points = 3
            draw_points = 1
            # Note: We don't flash message about override to keep UX clean since UI is locked
        
        league = League(
            name=form.name.data,
            user_id=current_user.id,
            max_teams=max_teams,
            win_points=win_points,
            draw_points=draw_points
        )
        db.session.add(league)
        db.session.flush() # Get ID
        
        # Create Default Court
        court_name = request.form.get('court_name', 'Cancha Principal')
        if not court_name: court_name = 'Cancha Principal'
        
        default_court = Court(name=court_name, league_id=league.id)
        db.session.add(default_court)
        
        db.session.commit()
        flash('Liga creada exitosamente.', 'success')
        return redirect(url_for('league_detail', league_id=league.id))
    
    return render_template('league_form.html', form=form, title='Nueva Liga')


@app.route('/leagues/<league_id>')
@login_required
@owner_required
def league_detail(league_id):
    if current_user.role == 'admin':
        league = League.query.get_or_404(league_id)
    else:
        league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Show only active teams in the list, but keep deleted teams for historical match references if needed
    active_teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    all_teams = Team.query.filter_by(league_id=league_id).all() # Need all for matches history lookup
    
    standings = calculate_standings(league_id)
    
    # Matches Paging
    page = request.args.get('page', 1, type=int)
    from sqlalchemy import or_
    matches_pagination = Match.query.filter(
        Match.league_id == league_id,
        or_(Match.stage == 'regular', Match.stage == None, Match.stage == '')
    ).order_by(Match.match_date.desc()).paginate(page=page, per_page=30, error_out=False)
    
    # Keep raw matches just in case other logic needs it (though maybe not efficiently)
    # But for now let's just use matches_pagination for the main list
    # The template uses 'matches' to extract playoffs too if not passed explicitly? 
    # Actually playoff_matches are passed explicitly.
    # The 'matches' var was used for: `set regular_matches = matches|selectattr...`
    # We will replace that logic with the pre-filtered matches_pagination
    
    matches = matches_pagination.items 
    # Note: I'm not fetching ALL matches anymore into 'matches', specific playoff queries handle playoffs.

    
    playoff_matches = {
        'repechaje': Match.query.filter_by(league_id=league_id, stage='repechaje').all(),
        'quarterfinal': Match.query.filter_by(league_id=league_id, stage='quarterfinal').all(),
        'semifinal': Match.query.filter_by(league_id=league_id, stage='semifinal').all(),
        'final': Match.query.filter_by(league_id=league_id, stage='final').all()
    }
    has_playoffs = any(len(m) > 0 for m in playoff_matches.values())
    
    teams_dict = {t.id: t for t in all_teams}
    
    # Pass players by team for JS dropdown
    players_by_team = {}
    for team in active_teams:
        players = Player.query.filter_by(team_id=team.id).order_by(Player.name).all()
        players_by_team[team.id] = [{'id': p.id, 'name': p.name, 'photo_url': p.photo_url} for p in players]
    
    # Get Season Stats
    top_scorers = SeasonStat.query.filter_by(league_id=league_id, stat_type='goals').order_by(SeasonStat.value.desc()).all()
    top_goalkeepers = SeasonStat.query.filter_by(league_id=league_id, stat_type='conceded').order_by(SeasonStat.value.asc()).all()
    
    # Dashboard Data
    # Recent Matches: Completed, valid stage, sorted by date DESC, limit 3
    recent_matches = Match.query.filter(
        Match.league_id == league_id,
        Match.is_completed == True
    ).order_by(Match.match_date.desc()).limit(3).all()

    # Upcoming Matches: Not completed, valid stage, sorted by date ASC, limit 3
    upcoming_matches = Match.query.filter(
        Match.league_id == league_id,
        Match.is_completed == False
    ).order_by(Match.match_date).limit(3).all()

    # Form for adding stats (Owner Only)
    stat_form = StatForm()
    if current_user.role == 'owner' or current_user.role == 'admin':
        stat_form.team_id.choices = [(t.id, t.name) for t in active_teams]
    
    # Form for editing league settings (embedded)
    form = LeagueForm(obj=league)

    
    return render_template('league_detail.html', 
                          league=league, 
                          teams=active_teams,
                          courts=league.courts,
                          standings=standings,
                          matches=matches,
                          playoff_matches=playoff_matches,
                          has_playoffs=has_playoffs,
                          teams_dict=teams_dict,
                          top_scorers=top_scorers,
                          top_goalkeepers=top_goalkeepers,
                          recent_matches=recent_matches,
                          upcoming_matches=upcoming_matches,
                          players_by_team=players_by_team,
                          stat_form=stat_form,
                          matches_pagination=matches_pagination,
                          form=form)


@app.route('/leagues/<league_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_league(league_id):
    if current_user.role == 'admin':
        league = League.query.get_or_404(league_id)
    else:
        league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    form = LeagueForm(obj=league)
    
    if form.validate_on_submit():
        league.name = form.name.data
        
        # Premium/Restricted Features: Max Teams, Points, Visuals
        if current_user.is_premium:
            league.max_teams = form.max_teams.data
            league.win_points = form.win_points.data
            league.draw_points = form.draw_points.data
            league.show_stats = form.show_stats.data
            league.logo_url = form.logo_url.data
            league.slogan = form.slogan.data
        
        db.session.commit()
        flash('Liga actualizada.', 'success')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='settings'))
    
    return render_template('league_form.html', form=form, title='Editar Liga', league=league)


@app.route('/leagues/<league_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_league(league_id):
    if current_user.role == 'admin':
        league = League.query.get_or_404(league_id)
    else:
        league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    db.session.delete(league)
    db.session.commit()
    flash('Liga eliminada.', 'success')
    return redirect(url_for('dashboard'))


# ==================== COURT ROUTES ====================

@app.route('/leagues/<league_id>/courts', methods=['POST'])
@login_required
@owner_required
@premium_required
def add_court(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Check limit (premium only, max 3)
    court_count = Court.query.filter_by(league_id=league_id).count()
    if court_count >= 3:
        flash('Máximo 3 canchas permitidas.', 'warning')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='settings'))
    
    court_name = request.form.get('court_name')
    if not court_name or len(court_name.strip()) == 0:
        flash('El nombre de la cancha es requerido.', 'danger')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='settings'))
        
    court = Court(name=court_name, league_id=league_id)
    db.session.add(court)
    db.session.commit()
    
    flash('Cancha agregada exitosamente.', 'success')
    return redirect(url_for('league_detail', league_id=league_id, _anchor='settings'))


@app.route('/courts/<court_id>/update', methods=['POST'])
@login_required
@owner_required
def update_court(court_id):
    court = Court.query.get_or_404(court_id)
    # Check ownership through league
    league = League.query.filter_by(id=court.league_id, user_id=current_user.id).first_or_404()
    
    new_name = request.form.get('court_name')
    if not new_name or len(new_name.strip()) == 0:
        flash('El nombre de la cancha es requerido.', 'danger')
    else:
        court.name = new_name
        db.session.commit()
        flash('Nombre de cancha actualizado.', 'success')
        
    return redirect(url_for('league_detail', league_id=league.id, _anchor='settings'))


@app.route('/courts/<court_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_court(court_id):
    court = Court.query.get_or_404(court_id)
    # Check ownership through league
    league = League.query.filter_by(id=court.league_id, user_id=current_user.id).first_or_404()
    
    # Check if last court
    court_count = Court.query.filter_by(league_id=league.id).count()
    if court_count <= 1:
        flash('No puedes eliminar la última cancha.', 'danger')
        return redirect(url_for('league_detail', league_id=league.id, _anchor='settings'))
    
    # Check if matches assigned
    match_count = Match.query.filter_by(court_id=court.id).count()
    if match_count > 0:
        flash('No puedes eliminar una cancha con partidos asignados.', 'warning')
        return redirect(url_for('league_detail', league_id=league.id, _anchor='settings'))
        
    db.session.delete(court)
    db.session.commit()
    flash('Cancha eliminada.', 'success')
    return redirect(url_for('league_detail', league_id=league.id, _anchor='settings'))





# ==================== TEAM ROUTES ====================

@app.route('/leagues/<league_id>/teams/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_team(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Check team limit
    team_count = Team.query.filter_by(league_id=league_id, is_deleted=False).count()
    if not current_user.is_premium and team_count >= 12:
        flash('Límite de 12 equipos para usuarios gratuitos.', 'warning')
        return redirect(url_for('league_detail', league_id=league_id))
    
    if team_count >= league.max_teams:
        flash(f'La liga ya tiene el máximo de {league.max_teams} equipos.', 'warning')
        return redirect(url_for('league_detail', league_id=league_id))
    
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            league_id=league_id,
            shield_url=form.shield_url.data
        )
        db.session.add(team)
        db.session.flush()  # Get team ID
        
        # Create captain if name provided
        if form.captain_name.data:
            captain_email = f"capitan.{team.id[:8]}@ligapro.com"
            captain_password = f"Cap{team.id[:8]}"
            hashed = bcrypt.generate_password_hash(captain_password).decode('utf-8')
            
            captain = User(
                email=captain_email,
                password=hashed,
                name=form.captain_name.data,
                role='captain',
                team_id=team.id
            )
            db.session.add(captain)
            
            team.captain_user_id = captain.id
            team.captain_email = captain_email
            team.captain_password_plain = captain_password
            team.captain_name = form.captain_name.data
        
        db.session.commit()
        flash('Equipo creado exitosamente.', 'success')
        # Redirect to teams tab
        return redirect(url_for('team_detail', team_id=team.id))
    
    return render_template('team_form.html', form=form, league=league, title='Nuevo Equipo')


@app.route('/teams/<team_id>')
@login_required
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team_id:
            flash('No tienes acceso a este equipo.', 'danger')
            return redirect(url_for('captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso a este equipo.', 'danger')
            return redirect(url_for('dashboard'))
    
    players = Player.query.filter_by(team_id=team_id).all()
    notes = TeamNote.query.filter_by(team_id=team_id).order_by(TeamNote.created_at.desc()).all()
    matches = Match.query.filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).order_by(Match.match_date.desc()).all()
    
    teams_dict = {t.id: t for t in Team.query.filter_by(league_id=league.id).all()}
    
    return render_template('team_detail.html', 
                          team=team, 
                          league=league,
                          players=players,
                          notes=notes,
                          matches=matches,
                          teams_dict=teams_dict)


@app.route('/teams/<team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team_id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('dashboard'))
    
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.shield_url = form.shield_url.data
        db.session.commit()
        flash('Equipo actualizado.', 'success')
        return redirect(url_for('team_detail', team_id=team_id))
    
    return render_template('team_form.html', form=form, team=team, league=league, title='Editar Equipo')


@app.route('/teams/<team_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('dashboard'))
    
    league_id = team.league_id
    
    # Soft Delete: Mark as deleted, preserve COMPLETED matches
    # remove UPCOMING matches as they cannot be played
    Match.query.filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
        Match.is_completed == False
    ).delete(synchronize_session=False)
    
    team.is_deleted = True

    # Delete players
    Player.query.filter_by(team_id=team_id).delete(synchronize_session=False)
    
    # Delete team notes
    TeamNote.query.filter_by(team_id=team_id).delete(synchronize_session=False)

    # Delete captain user if exists
    # First try by direct link
    if team.captain_user_id:
        captain = User.query.get(team.captain_user_id)
        if captain:
            db.session.delete(captain)
            
    # Also ensure any user marked as captain of this team is removed (cleanup)
    User.query.filter_by(team_id=team_id, role='captain').delete(synchronize_session=False)
    
    # Do NOT delete the team record itself
    # db.session.delete(team) 
    
    db.session.commit()
    flash('Equipo eliminado de la competencia. Sus partidos históricos se conservan.', 'success')
    # Redirect to teams tab
    return redirect(url_for('league_detail', league_id=league_id, _anchor='teams'))


@app.route('/teams/<team_id>/captain', methods=['POST'])
@login_required
@owner_required
def add_captain(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('dashboard'))
    
    captain_name = request.form.get('captain_name')
    if not captain_name:
        flash('Nombre del capitán requerido.', 'danger')
        return redirect(url_for('team_detail', team_id=team_id))
    
    # Define captain email (deterministic based on team ID)
    captain_email = f"capitan.{team.id[:8]}@ligapro.com"
    captain_password = f"Cap{team.id[:8]}"
    hashed = bcrypt.generate_password_hash(captain_password).decode('utf-8')
    
    # Check if a user with this email already exists
    captain = User.query.filter_by(email=captain_email).first()
    
    if captain:
        # Update existing captain user
        captain.name = captain_name
        captain.password = hashed
        # Ensure role and team_id are correct
        captain.role = 'captain'
        captain.team_id = team.id
        flash(f'Capitán actualizado. Contraseña restablecida: {captain_password}', 'success')
    else:
        # Create new captain user
        captain = User(
            email=captain_email,
            password=hashed,
            name=captain_name,
            role='captain',
            team_id=team.id
        )
        db.session.add(captain)
        flash(f'Capitán asignado. Email: {captain_email}, Contraseña: {captain_password}', 'success')
    
    # Update team record
    db.session.flush() # Ensure captain has ID if new
    team.captain_user_id = captain.id
    team.captain_email = captain_email
    team.captain_password_plain = captain_password
    team.captain_name = captain_name
    
    db.session.commit()
    return redirect(url_for('team_detail', team_id=team_id))


@app.route('/teams/<team_id>/notes', methods=['POST'])
@login_required
@owner_required
def add_team_note(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('dashboard'))
    
    text = request.form.get('note_text')
    if text:
        note = TeamNote(team_id=team_id, text=text)
        db.session.add(note)
        db.session.commit()
        flash('Nota agregada.', 'success')
    
    return redirect(url_for('team_detail', team_id=team_id))


@app.route('/teams/<team_id>/credentials', methods=['GET'])
@login_required
def generate_credentials(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    # Permission Check: League Owner OR Team Captain
    # Permission Check: League Owner OR Team Captain
    is_owner = league.user_id == current_user.id
    
    # Robust Captain Check:
    # 1. Matches team.captain_user_id (Ideal)
    # 2. Matches current_user.team_id + role='captain' (Fallback/Self-Repair)
    is_captain = False
    
    if team.captain_user_id == current_user.id:
        is_captain = True
    elif current_user.role == 'captain' and current_user.team_id == team_id:
        is_captain = True
        # Self-Repair: Link was broken, fixing it now.
        if not team.captain_user_id:
            team.captain_user_id = current_user.id
            db.session.commit()
    
    if not (is_owner or is_captain):
        flash('No tienes permiso para ver estos registros.', 'danger')
        
        if current_user.role == 'captain':
            return redirect(url_for('captain_dashboard'))
        return redirect(url_for('dashboard'))
    
    # Premium Access Logic
    # 1. League Owner is Premium -> Access Granted to Owner AND Captain
    # 2. Captain is Premium -> Access Granted to Captain (Plan Capitán)
    
    has_access = False
    
    if is_owner:
        # Owner always has access if they are premium? Or free owners too?
        # Assuming Owner needs Premium for "advanced" features, OR credentials are a basic premium feature.
        # Original code checked: if not league.owner.is_active_premium.
        if league.owner.is_active_premium:
            has_access = True
    
    if is_captain:
        # Captain gets access if:
        # a) Owner is Premium (Unlocks for everyone in league)
        # b) Captain is Premium (Specific unlock)
        if league.owner.is_active_premium or current_user.is_active_premium:
             has_access = True
             
    if not has_access:
        flash('Esta función requiere Premium (Dueño de Liga o Plan Capitán).', 'warning')
        if is_captain and not is_owner:
            return redirect(url_for('captain_premium'))
        else:
            return redirect(url_for('premium'))
            
    players = Player.query.filter_by(team_id=team_id).order_by(Player.number.asc(), Player.name.asc()).all()
    
    return render_template('credentials.html', team=team, players=players, league=league)


# ==================== PLAYER ROUTES ====================

@app.route('/teams/<team_id>/players/new', methods=['GET', 'POST'])
@login_required
def create_player(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team_id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('dashboard'))
    
    form = PlayerForm()
    if form.validate_on_submit():
        player = Player(
            name=form.name.data,
            team_id=team_id,
            number=form.number.data,
            curp=form.curp.data,
            photo_url=form.photo_url.data
        )
        db.session.add(player)
        db.session.commit()
        flash('Jugador agregado.', 'success')
        return redirect(url_for('team_detail', team_id=team_id))
    
    return render_template('player_form.html', form=form, team=team, title='Nuevo Jugador')


@app.route('/players/<player_id>/edit', methods=['GET', 'POST'])
@login_required
@premium_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    team = player.team
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('dashboard'))
    
    form = PlayerForm(obj=player)
    if form.validate_on_submit():
        player.name = form.name.data
        player.number = form.number.data
        player.curp = form.curp.data
        player.photo_url = form.photo_url.data
        db.session.commit()
        flash('Jugador actualizado.', 'success')
        return redirect(url_for('team_detail', team_id=team.id))
    
    return render_template('player_form.html', form=form, player=player, team=team, title='Editar Jugador')


@app.route('/players/<player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    team = player.team
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('dashboard'))
    
    team_id = player.team_id
    db.session.delete(player)
    db.session.commit()
    flash('Jugador eliminado.', 'success')
    return redirect(url_for('team_detail', team_id=team_id))


# ==================== MATCH ROUTES ====================

@app.route('/leagues/<league_id>/matches/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_match(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    # Only allow scheduling matches between active teams
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    
    form = MatchForm()
    form.home_team_id.choices = [(t.id, t.name) for t in teams]
    form.away_team_id.choices = [(t.id, t.name) for t in teams]
    
    # Populate court choices
    courts = Court.query.filter_by(league_id=league_id).all()
    form.court_id.choices = [(c.id, c.name) for c in courts]
    
    if form.validate_on_submit():
        if form.home_team_id.data == form.away_team_id.data:
            flash('Un equipo no puede jugar contra sí mismo.', 'danger')
        else:
            match = Match(
                league_id=league_id,
                home_team_id=form.home_team_id.data,
                away_team_id=form.away_team_id.data,
                court_id=form.court_id.data,
                match_date=form.match_date.data
            )
            db.session.add(match)
            db.session.commit()
            flash('Partido programado.', 'success')
            return redirect(url_for('league_detail', league_id=league_id, _anchor='matches'))

    # Calculate match history for frontend display
    completed_matches = Match.query.filter_by(league_id=league_id, is_completed=True).all()
    teams_history = {t.id: {} for t in teams}
    
    for m in completed_matches:
        # Check if teams still exist (in case deleted but match kept? usually safe due to FK but good practice)
        if m.home_team_id in teams_history and m.away_team_id in teams_history:
            # Home vs Away
            teams_history[m.home_team_id][m.away_team_id] = teams_history[m.home_team_id].get(m.away_team_id, 0) + 1
            # Away vs Home
            teams_history[m.away_team_id][m.home_team_id] = teams_history[m.away_team_id].get(m.home_team_id, 0) + 1
            
    # Create a mapping of id -> name for easy JS lookup
    teams_map = {t.id: t.name for t in teams}

    return render_template('match_form.html', form=form, league=league, 
                         title='Programar Partido', teams_history=teams_history, teams_map=teams_map)


@app.route('/matches/<match_id>/result', methods=['GET', 'POST'])
@login_required
@owner_required
def update_match_result(match_id):
    match = Match.query.get_or_404(match_id)
    league = match.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = MatchResultForm(obj=match)
    if form.validate_on_submit():
        match.home_score = form.home_score.data
        match.away_score = form.away_score.data
        match.is_completed = True
        db.session.commit()
        flash('Resultado registrado.', 'success')
        anchor = 'playoff' if match.stage != 'regular' and match.stage is not None else 'matches'
        return redirect(url_for('league_detail', league_id=league.id, _anchor=anchor))
    
    home_team = Team.query.get(match.home_team_id)
    away_team = Team.query.get(match.away_team_id)
    
    return render_template('match_result_form.html', form=form, match=match, 
                          home_team=home_team, away_team=away_team, league=league)


@app.route('/matches/<match_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    league_id = match.league_id
    
    if match.league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('dashboard'))
        
    if match.is_completed:
        flash('No se pueden eliminar partidos que ya tienen resultado.', 'warning')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='matches'))
        
    db.session.delete(match)
    db.session.commit()
    flash('Partido eliminado.', 'success')
    return redirect(url_for('league_detail', league_id=league_id, _anchor='matches'))


@app.route('/matches/<match_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    league_id = match.league_id
    league = match.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('dashboard'))
        
    if match.is_completed:
        flash('No se pueden editar los detalles de un partido ya jugado. Solo se puede modificar el resultado.', 'warning')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='matches'))
        
    form = MatchForm(obj=match)
    # Populate choices
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    form.home_team_id.choices = [(t.id, t.name) for t in teams]
    form.away_team_id.choices = [(t.id, t.name) for t in teams]
    
    courts = Court.query.filter_by(league_id=league_id).all()
    form.court_id.choices = [(c.id, c.name) for c in courts]
    
    if form.validate_on_submit():
        if form.home_team_id.data == form.away_team_id.data:
            flash('Un equipo no puede jugar contra sí mismo.', 'danger')
        else:
            match.home_team_id = form.home_team_id.data
            match.away_team_id = form.away_team_id.data
            match.court_id = form.court_id.data
            match.match_date = form.match_date.data
            
            db.session.commit()
            flash('Partido actualizado.', 'success')
            return redirect(url_for('league_detail', league_id=league_id, _anchor='matches'))
            
    # Calculate match history for frontend display (reuse logic)
    completed_matches = Match.query.filter_by(league_id=league_id, is_completed=True).all()
    teams_history = {t.id: {} for t in teams}
    
    for m in completed_matches:
        if m.id == match.id: continue # Exclude current match if it was somehow completed (safeguard)
        if m.home_team_id in teams_history and m.away_team_id in teams_history:
            teams_history[m.home_team_id][m.away_team_id] = teams_history[m.home_team_id].get(m.away_team_id, 0) + 1
            teams_history[m.away_team_id][m.home_team_id] = teams_history[m.away_team_id].get(m.home_team_id, 0) + 1
            
    teams_map = {t.id: t.name for t in teams}
    
    return render_template('match_form.html', form=form, league=league, 
                          title='Editar Partido', teams_history=teams_history, teams_map=teams_map)


# ==================== SEASON ROUTES ====================

@app.route('/leagues/<league_id>/reset_season', methods=['POST'])
@login_required
@owner_required
@premium_required
def reset_season(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Delete ALL matches (regular + playoff)
    deleted = Match.query.filter_by(league_id=league_id).delete(synchronize_session=False)
    
    # Reset playoff state
    league.playoff_mode = None
    league.playoff_bye_teams = None
    
    # Delete Season Stats (Goleadores / Arqueros)
    SeasonStat.query.filter_by(league_id=league_id).delete(synchronize_session=False)

    # Clean up soft-deleted teams (Hard Delete)
    # Now that matches are gone, we can safely remove the "ghost" teams
    deleted_teams_count = Team.query.filter_by(league_id=league_id, is_deleted=True).delete(synchronize_session=False)
    
    db.session.commit()
    flash(f'Temporada reiniciada. {deleted} partidos eliminados. {deleted_teams_count} equipos eliminados permanentemente.', 'success')
    return redirect(url_for('league_detail', league_id=league_id))


# ==================== PLAYOFF ROUTES ====================


@app.route('/leagues/<league_id>/playoffs/reset', methods=['POST'])
@login_required
@owner_required
def reset_playoffs(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Delete all playoff matches
    deleted = Match.query.filter(
        Match.league_id == league_id,
        Match.stage.in_(['repechaje', 'quarterfinal', 'semifinal', 'final'])
    ).delete(synchronize_session=False)
    
    # Reset league playoff state
    league.playoff_mode = None
    league.playoff_bye_teams = None
    
    db.session.commit()
    db.session.commit()
    flash(f'Liguilla reiniciada. Se eliminaron {deleted} partidos.', 'success')
    return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))

@app.route('/leagues/<league_id>/playoffs/generate', methods=['POST'])
@login_required
@owner_required
def generate_playoffs(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    mode = request.form.get('mode', 'corte_directo')
    playoff_type = request.form.get('playoff_type', 'single')

    # Premium check for double leg
    if playoff_type == 'double' and not current_user.is_premium:
        flash('La modalidad Ida y Vuelta es exclusiva para Premium.', 'warning')
        return redirect(url_for('premium'))
    
    standings = calculate_standings(league_id)
    total_teams = len(standings)
    
    if total_teams < 5:
        flash('Se necesitan al menos 5 equipos para la liguilla.', 'danger')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))
    
    # Delete existing playoff matches
    Match.query.filter(
        Match.league_id == league_id,
        Match.stage.in_(['repechaje', 'quarterfinal', 'semifinal', 'final'])
    ).delete(synchronize_session=False)
    
    # Clear playoff state
    league.playoff_mode = mode
    league.playoff_type = playoff_type
    league.playoff_bye_teams = None
    
    playoff_matches = []
    bye_teams = []


    # Continue with generation...
    
    # Small leagues (5-7 teams)
    if total_teams <= 7:
        if mode == 'corte_directo':
            # Top 4 -> Semifinals
            playoff_matches.append({
                'home': standings[0], 'away': standings[3], 'stage': 'semifinal',
                'name': f"Semifinal 1: {standings[0]['team'].name} vs {standings[3]['team'].name}"
            })
            playoff_matches.append({
                'home': standings[1], 'away': standings[2], 'stage': 'semifinal',
                'name': f"Semifinal 2: {standings[1]['team'].name} vs {standings[2]['team'].name}"
            })
        else:  # con_repechaje
            if total_teams < 6:
                flash('Se necesitan al menos 6 equipos para modo con repechaje.', 'danger')
                return redirect(url_for('league_detail', league_id=league_id))
            
            # Top 2 get bye
            bye_teams = [standings[0]['team'].id, standings[1]['team'].id]
            
            # Repechaje: 3 vs 6, 4 vs 5
            playoff_matches.append({
                'home': standings[2], 'away': standings[5], 'stage': 'repechaje',
                'name': f"Repechaje 1: {standings[2]['team'].name} vs {standings[5]['team'].name}"
            })
            playoff_matches.append({
                'home': standings[3], 'away': standings[4], 'stage': 'repechaje',
                'name': f"Repechaje 2: {standings[3]['team'].name} vs {standings[4]['team'].name}"
            })
    
    # Large leagues (8+ teams)
    else:
        if mode == 'corte_directo':
            # Top 8 -> Quarterfinals
            if total_teams < 8:
                flash('Se necesitan al menos 8 equipos para corte directo.', 'danger')
                return redirect(url_for('league_detail', league_id=league_id))
            
            playoff_matches.append({
                'home': standings[0], 'away': standings[7], 'stage': 'quarterfinal',
                'name': f"Cuarto 1: {standings[0]['team'].name} vs {standings[7]['team'].name}"
            })
            playoff_matches.append({
                'home': standings[1], 'away': standings[6], 'stage': 'quarterfinal',
                'name': f"Cuarto 2: {standings[1]['team'].name} vs {standings[6]['team'].name}"
            })
            playoff_matches.append({
                'home': standings[2], 'away': standings[5], 'stage': 'quarterfinal',
                'name': f"Cuarto 3: {standings[2]['team'].name} vs {standings[5]['team'].name}"
            })
            playoff_matches.append({
                'home': standings[3], 'away': standings[4], 'stage': 'quarterfinal',
                'name': f"Cuarto 4: {standings[3]['team'].name} vs {standings[4]['team'].name}"
            })
        else:  # con_repechaje
            if total_teams < 10:
                flash('Se necesitan al menos 10 equipos para modo con repechaje.', 'danger')
                return redirect(url_for('league_detail', league_id=league_id))
            
            # Top 6 get bye
            bye_teams = [standings[i]['team'].id for i in range(6)]
            
            # Repechaje: 7 vs 10, 8 vs 9
            playoff_matches.append({
                'home': standings[6], 'away': standings[9], 'stage': 'repechaje',
                'name': f"Repechaje 1: {standings[6]['team'].name} vs {standings[9]['team'].name}"
            })
            playoff_matches.append({
                'home': standings[7], 'away': standings[8], 'stage': 'repechaje',
                'name': f"Repechaje 2: {standings[7]['team'].name} vs {standings[8]['team'].name}"
            })
    
    # Save bye teams
    if bye_teams:
        import json
        league.playoff_bye_teams = json.dumps(bye_teams)
    
    # Create matches
    created_count = 0
    for m in playoff_matches:
        # Match 1 (Ida or Single)
        match1 = Match(
            league_id=league_id,
            home_team_id=m['home']['team'].id,
            away_team_id=m['away']['team'].id,
            match_date=datetime.now(timezone.utc),
            stage=m['stage'],
            match_name=m['name'] + (" (Ida)" if playoff_type == 'double' else "")
        )
        db.session.add(match1)
        created_count += 1

        # Match 2 (Vuelta) if double leg AND NOT FINAL (Final is always single)
        if playoff_type == 'double' and m['stage'] != 'final':
            match2 = Match(
                league_id=league_id,
                home_team_id=m['away']['team'].id, # Swapped
                away_team_id=m['home']['team'].id, # Swapped
                match_date=datetime.now(timezone.utc), # Should ideally be later
                stage=m['stage'],
                match_name=m['name'].replace(m['home']['team'].name, "TEMP").replace(m['away']['team'].name, m['home']['team'].name).replace("TEMP", m['away']['team'].name) + " (Vuelta)"
            )
            db.session.add(match2)
            created_count += 1
    
    db.session.commit()
    flash(f'Liguilla generada ({mode} - {playoff_type}). {created_count} partidos creados.', 'success')
    return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))


@app.route('/leagues/<league_id>/playoffs/advance', methods=['POST'])
@login_required
@owner_required
def advance_playoff_round(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Get all playoff matches
    playoff_matches = Match.query.filter(
        Match.league_id == league_id,
        Match.stage.in_(['repechaje', 'quarterfinal', 'semifinal', 'final'])
    ).all()
    
    if not playoff_matches:
        flash('No hay partidos de liguilla.', 'danger')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))
    
    stages_order = ['repechaje', 'quarterfinal', 'semifinal', 'final']
    active_stage = None
    active_stage_matches = []
    
    # Scan stages to find the latest one that has matches
    for stage in stages_order:
        matches_in_stage = [m for m in playoff_matches if m.stage == stage]
        if matches_in_stage:
            active_stage = stage
            active_stage_matches = matches_in_stage
            
            # Check if this stage is completed
            if not all(m.is_completed for m in matches_in_stage):
                flash(f'Completa todos los partidos de {stage} antes de avanzar.', 'warning')
                return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))
    
    if not active_stage:
        flash('No se encontró una fase activa.', 'danger')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))
    
    # Check if tournament finished
    if active_stage == 'final':
        final = active_stage_matches[0]
        winner = Team.query.get(final.home_team_id if final.home_score > final.away_score else final.away_team_id)
        flash(f'¡El torneo ha terminado! Campeón: {winner.name} 🏆', 'success')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))
    
    # Calculate qualified teams for next round
    winners = []
    # Calculate qualified teams for next round
    winners = []

    if league.playoff_type == 'double' and active_stage != 'final':
        # Double Leg Logic: Aggregate Score
        # Group matches by teams playing each other
        processed_pairs = set()
        
        for match in active_stage_matches:
            # Create a sorted tuple of team IDs to identify the pair
            pair_id = tuple(sorted([match.home_team_id, match.away_team_id]))
            
            if pair_id in processed_pairs:
                continue
                
            # Find the other match for this pair
            pair_matches = [m for m in active_stage_matches if tuple(sorted([m.home_team_id, m.away_team_id])) == pair_id]
            
            if len(pair_matches) != 2:
                # Fallback if something is wrong, treat as single or error?
                # For now, let's just take the winner of this match if only 1 exists
                if match.home_score > match.away_score:
                    winners.append(match.home_team_id)
                else:
                    winners.append(match.away_team_id)
                continue

            # Calculate aggregate
            team1_id = pair_matches[0].home_team_id
            team2_id = pair_matches[0].away_team_id
            
            team1_goals = 0
            team2_goals = 0
            
            for m in pair_matches:
                if m.home_team_id == team1_id:
                    team1_goals += m.home_score
                    team2_goals += m.away_score
                else:
                    team2_goals += m.home_score
                    team1_goals += m.away_score
            
            if team1_goals > team2_goals:
                winners.append(team1_id)
            elif team2_goals > team1_goals:
                winners.append(team2_id)
            else:
                # Aggregate Tie
                # 1. Away Goals? (Not requested, but common)
                # 2. Seeding (Higher seed advances) - User asked for "mayor diferencia", if equal?
                # Let's stick to seeding/Home advantage of first leg fallback
                # Default: The team that was Home in the FIRST match of the pair? No, usually higher seed.
                # Let's add both to a potential winner list and let the seeding sort below pick correct one?
                # No, we need to pick ONE.
                # Fallback: Pick team1 (randomly essentially if we don't check seed here)
                # Ideally check standings points
                winners.append(team1_id) # Simplify for now, seeding check is complicated here without re-fetching standings
            
            processed_pairs.add(pair_id)

    else:
        # Single Leg Logic
        for match in active_stage_matches:
            if match.home_score > match.away_score:
                winners.append(match.home_team_id)
            elif match.away_score > match.home_score:
                winners.append(match.away_team_id)
            else:
                 # Tie-breaker: Setup a rule (e.g. better seed, or home team)
                 # Defaulting to Home Team for now (should implement penalties or seeding check)
                winners.append(match.home_team_id)

    # Add byes if coming from repechaje
    if active_stage == 'repechaje' and league.playoff_bye_teams:
        import json
        try:
            byes = json.loads(league.playoff_bye_teams)
            winners.extend(byes)
        except:
            pass
            
    # Seeding
    standings = calculate_standings(league_id)
    seed_map = {s['team'].id: i for i, s in enumerate(standings)}
    winners.sort(key=lambda tid: seed_map.get(tid, 999))
    
    num_qualified = len(winners)
    if num_qualified < 2:
        flash('No hay suficientes equipos para la siguiente ronda.', 'danger')
        return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))
        
    # Determine Next Stage
    next_stage = 'quarterfinal'
    if num_qualified == 2:
        next_stage = 'final'
    elif num_qualified <= 4:
        next_stage = 'semifinal'
        
    # Check if next stage matches already exist
    existing = Match.query.filter_by(league_id=league_id, stage=next_stage).first()
    if existing:
        flash(f'La siguiente ronda ({next_stage}) ya está generada.', 'warning')
        return redirect(url_for('league_detail', league_id=league_id))
        
    # Generate Matches (Best vs Worst)
    num_matches = num_qualified // 2
    teams_dict = {t.id: t for t in Team.query.filter_by(league_id=league_id).all()}
    created_count = 0
    
    for i in range(num_matches):
        home_id = winners[i]
        away_id = winners[num_qualified - 1 - i]
        
        
        # Match 1 (Ida or Single) - Final is ALWAYS single
        match1 = Match(
            league_id=league_id,
            home_team_id=home_id,
            away_team_id=away_id,
            match_date=datetime.now(timezone.utc),
            stage=next_stage,
            match_name=f"{next_stage.capitalize()}: {teams_dict[home_id].name} vs {teams_dict[away_id].name}" + (" (Ida)" if (league.playoff_type == 'double' and next_stage != 'final') else "")
        )
        db.session.add(match1)
        created_count += 1
        
        # Match 2 (Vuelta) - Only if double mode AND NO FINAL
        if league.playoff_type == 'double' and next_stage != 'final':
            match2 = Match(
                league_id=league_id,
                home_team_id=away_id,
                away_team_id=home_id,
                match_date=datetime.now(timezone.utc),
                stage=next_stage,
                match_name=f"{next_stage.capitalize()}: {teams_dict[away_id].name} vs {teams_dict[home_id].name} (Vuelta)"
            )
            db.session.add(match2)
            created_count += 1
        
    db.session.commit()
    flash(f'Ronda generada: {next_stage} ({created_count} partidos).', 'success')
    db.session.commit()
    flash(f'Ronda generada: {next_stage} ({created_count} partidos).', 'success')
    return redirect(url_for('league_detail', league_id=league_id, _anchor='playoff'))


# ==================== STATS ROUTES ====================

@app.route('/leagues/<league_id>/stats/add', methods=['POST'])
@login_required
@owner_required
def add_stat(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    form = StatForm()
    form = StatForm()
    # Populate choices dynamically for validation
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    form.team_id.choices = [(t.id, t.name) for t in teams]
    
    if form.validate_on_submit():
        # Check limit for non-premium users
        if not current_user.is_premium:
            current_count = SeasonStat.query.filter_by(
                league_id=league_id, 
                stat_type=form.stat_type.data
            ).count()
            
            if current_count >= 5:
                flash(f'Límite de 5 registros alcanzado. Actualiza a Premium para añadir ilimitados.', 'warning')
                flash(f'Límite de 5 registros alcanzado. Actualiza a Premium para añadir ilimitados.', 'warning')
                return redirect(url_for('league_detail', league_id=league_id, _anchor='stats'))

        # Check if player_name is actually an ID (from dropdown)
        player_id = form.player_name.data
        player = Player.query.get(player_id)
        
        if player:
            final_player_name = player.name
            final_photo_url = player.photo_url
            final_team_id = player.team_id # Ensure team matches player
        else:
            # Fallback for legacy or manual (should not happen with new UI)
            final_player_name = form.player_name.data
            final_photo_url = form.photo_url.data
            final_team_id = form.team_id.data

        stat = SeasonStat(
            league_id=league_id,
            team_id=final_team_id,
            player_name=final_player_name,
            photo_url=final_photo_url,
            stat_type=form.stat_type.data,
            value=form.value.data
        )
        db.session.add(stat)
        db.session.commit()
        flash('Estadística agregada correctamente.', 'success')
    else:
        flash('Error al agregar estadística. Verifica los datos.', 'danger')
        
    return redirect(url_for('league_detail', league_id=league_id, _anchor='stats'))


@app.route('/stats/<stat_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_stat(stat_id):
    stat = SeasonStat.query.get_or_404(stat_id)
    # Check ownership via league
    league = League.query.get(stat.league_id)
    if not league or league.user_id != current_user.id:
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('dashboard'))
        
    db.session.delete(stat)
    db.session.commit()
    flash('Estadística eliminada.', 'success')
    return redirect(url_for('league_detail', league_id=league.id, _anchor='stats'))


@app.route('/stats/<stat_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_stat(stat_id):
    stat = SeasonStat.query.get_or_404(stat_id)
    # Check ownership
    league = League.query.get(stat.league_id)
    if not league or league.user_id != current_user.id:
        flash('No tienes permiso para editar esta estadística.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Pre-fill form
    form = StatForm(obj=stat)
    
    # Populate choices dynamically for validation
    teams = Team.query.filter_by(league_id=league.id).all()
    form.team_id.choices = [(t.id, t.name) for t in teams]
    
    if form.validate_on_submit():
        stat.player_name = form.player_name.data
        stat.team_id = form.team_id.data
        stat.photo_url = form.photo_url.data
        stat.value = form.value.data
        stat.stat_type = form.stat_type.data
        
        db.session.commit()
        flash('Estadística actualizada.', 'success')
        return redirect(url_for('league_detail', league_id=league.id, _anchor='stats'))
        
    return render_template('stat_form.html', form=form, stat=stat, league=league)


# ==================== PREMIUM ROUTES ====================

@app.route('/premium')
@login_required
def premium():
    return render_template('premium.html')


@app.route('/premium/captain')
@login_required
def captain_premium():
    return render_template('captain_premium.html')


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        plan_type = request.args.get('plan', 'owner') # 'owner' (subscription) or 'captain' (one-time)
        
        if plan_type == 'captain':
             price_id = app.config['STRIPE_CAPTAIN_PRICE_ID']
             mode = 'payment'
        else:
             price_id = app.config['STRIPE_PRICE_ID']
             mode = 'subscription'

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode=mode,
            success_url=url_for('success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('premium', _external=True) if plan_type == 'owner' else url_for('captain_premium', _external=True),
            customer_email=current_user.email,
            client_reference_id=current_user.id,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error al conectar con Stripe: {str(e)}', 'danger')
        return redirect(url_for('premium'))


@app.route('/success')
@login_required
def success():
    session_id = request.args.get('session_id')
    if session_id:
        # Aquí podrías verificar la sesión con Stripe si quisieras doble seguridad
        # session = stripe.checkout.Session.retrieve(session_id)
        pass
    
    current_user.is_premium = True
    db.session.commit()
    flash('¡Gracias por tu suscripción! Tu cuenta ahora es Premium.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not webhook_secret:
        return 'Webhook secret not configured', 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Payload inválido
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida (alguien intenta hackear)
        return 'Invalid signature', 400

    # Manejar el evento: Pago Exitoso
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Recuperamos el ID del usuario que guardamos al crear la sesión
        user_id = session.get('client_reference_id')
        
        if user_id:
            # Buscamos al usuario y activamos el Premium de verdad
            # Usamos un contexto de aplicación por si acaso (aunque Flask suele manejarlo)
            try:
                user = User.query.get(user_id)
                if user:
                    user.is_premium = True
                    db.session.commit()
                    print(f"✅ WEBHOOK: Premium activado para el usuario {user.email}")
                else:
                    print(f"⚠️ WEBHOOK: Usuario {user_id} no encontrado.")
            except Exception as e:
                print(f"❌ WEBHOOK ERROR: No se pudo actualizar la DB: {e}")
                db.session.rollback()

    return jsonify(success=True)


# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Dashboard Stats
    total_users = User.query.count()
    total_leagues = League.query.count()
    total_teams = Team.query.count()
    total_players = Player.query.count()
    premium_users = User.query.filter_by(is_premium=True).count()
    
    # Active users (with temporary premium)
    temp_premium = User.query.filter(User.premium_expires_at > datetime.now(timezone.utc)).count()
    
    # Recent Users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users,
                          total_leagues=total_leagues,
                          total_teams=total_teams,
                          total_players=total_players,
                          premium_users=premium_users,
                          temp_premium=temp_premium,
                          recent_users=recent_users)

@app.route('/admin/leagues')
@login_required
@admin_required
def admin_leagues():
    leagues = League.query.order_by(League.created_at.desc()).all()
    # Pre-calculate counts to avoid N+1 in template (though access via property is lazy, this is cleaner)
    # Actually, SQLAlchemy relationship lazy='true' does separate queries.
    # We'll just pass the objects.
    return render_template('admin/leagues.html', leagues=leagues)

@app.route('/admin/teams')
@login_required
@admin_required
def admin_teams():
    # Join with League and User (Captain) to get names efficiently
    teams = Team.query.join(League).order_by(Team.created_at.desc()).all()
    return render_template('admin/teams.html', teams=teams)




@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(User.email.contains(search) | User.name.contains(search))
        
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users, search=search)

@app.route('/admin/users/<user_id>/grant_premium', methods=['POST'])
@login_required
@admin_required
def admin_grant_premium(user_id):
    user = User.query.get_or_404(user_id)
    days = request.form.get('days', 7, type=int)
    
    from datetime import timedelta
    user.premium_expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    db.session.commit()
    
    flash(f'Premium temporal ({days} días) otorgado a {user.email}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<user_id>/toggle_premium', methods=['POST'])
@login_required
@admin_required
def admin_toggle_premium(user_id):
    user = User.query.get_or_404(user_id)
    user.is_premium = not user.is_premium
    # Clear temp premium if setting permanent
    if user.is_premium:
        user.premium_expires_at = None
        
    db.session.commit()
    status = "Activado" if user.is_premium else "Desactivado"
    flash(f'Premium permanente {status} para {user.email}.', 'success')
    return redirect(url_for('admin_users'))
    
@app.route('/admin/users/<user_id>/login_as', methods=['POST'])
@login_required
@admin_required
def admin_login_as(user_id):
    user = User.query.get_or_404(user_id)
    login_user(user)
    flash(f'Has iniciado sesión como {user.name}', 'info')
    return redirect(url_for('dashboard'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Página no encontrada', code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Error del servidor', code=500), 500


# ==================== CLI COMMANDS ====================

@app.cli.command('init-db')
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command('create-admin')
def create_admin():
    """Create default admin user"""
    existing = User.query.filter_by(email='delegado@ligapro.com').first()
    if existing:
        print('Admin already exists.')
        return
        
    hashed = bcrypt.generate_password_hash('admin123').decode('utf-8')
    user = User(
        name='Delegado Liga',
        email='delegado@ligapro.com',
        password=hashed,
        role='owner',
        is_premium=True
    )
    db.session.add(user)
    db.session.commit()
    print('Admin user created successfully.')


# ==================== SHARE ROUTES ====================

@app.route('/leagues/<league_id>/share', methods=['POST'])
@login_required
@owner_required
def generate_share_report(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Get form data
    include_standings = request.form.get('include_standings') == 'on'
    include_recent = request.form.get('include_recent') == 'on'
    date_start_str = request.form.get('date_start')
    date_end_str = request.form.get('date_end')
    include_upcoming = request.form.get('include_upcoming') == 'on'
    include_scorers = request.form.get('include_scorers') == 'on'
    include_keepers = request.form.get('include_keepers') == 'on'
    
    # Data containers
    standings = []
    recent_matches = []
    upcoming_matches = []
    top_scorers = []
    top_goalkeepers = []
    teams_dict = {}
    
    # Needs teams anyway for matches dict
    teams = Team.query.filter_by(league_id=league_id).all()
    teams_dict = {t.id: t for t in teams}

    if include_standings:
        standings = calculate_standings(league_id)
        
    if include_recent:
        query = Match.query.filter(
            Match.league_id == league_id,
            Match.is_completed == True
        )
        
        # Apply Date Filter if provided
        if date_start_str:
            try:
                date_start = datetime.strptime(date_start_str, '%Y-%m-%d')
                query = query.filter(Match.match_date >= date_start)
            except ValueError:
                pass
                
        if date_end_str:
            try:
                # Add 1 day to end date to include the full day
                date_end = datetime.strptime(date_end_str, '%Y-%m-%d')
                # Adjust for simple date compare if using datetime
                query = query.filter(Match.match_date <= date_end.replace(hour=23, minute=59))
            except ValueError:
                pass
                
        recent_matches = query.order_by(Match.match_date.desc()).all()
        
    if include_upcoming:
        if date_start_str and date_end_str:
             # If date filter is applied, maybe we want upcoming in that range too?
             # But usually upcoming means "future from now". 
             # Let's keep distinct logic: Upcoming is always future matches.
             pass

        upcoming_matches = Match.query.filter(
            Match.league_id == league_id,
            Match.is_completed == False
        ).order_by(Match.match_date.asc()).limit(10).all()

    # Group upcoming matches by court
    matches_by_court = {}
    if upcoming_matches:
        for match in upcoming_matches:
            # Use court name if exists, else "Cancha Principal" or similar fallback
            court_name = match.court.name if match.court else "Cancha Principal"
            if court_name not in matches_by_court:
                matches_by_court[court_name] = []
            matches_by_court[court_name].append(match)

    if include_scorers:
        top_scorers = SeasonStat.query.filter_by(league_id=league_id, stat_type='goals').order_by(SeasonStat.value.desc()).limit(5).all()
        
    if include_keepers:
        top_goalkeepers = SeasonStat.query.filter_by(league_id=league_id, stat_type='conceded').order_by(SeasonStat.value.asc()).limit(5).all()
        
    return render_template('share_report.html',
                          league=league,
                          today=datetime.now().strftime('%d/%m/%Y'),
                          teams_dict=teams_dict,
                          include_standings=include_standings, standings=standings,
                          include_recent=include_recent, recent_matches=recent_matches,
                          include_upcoming=include_upcoming, upcoming_matches=upcoming_matches, matches_by_court=matches_by_court,
                          include_scorers=include_scorers, top_scorers=top_scorers,
                          include_keepers=include_keepers, top_goalkeepers=top_goalkeepers,
                          date_start=date_start_str if date_start_str else 'Inicio',
                          date_end=date_end_str if date_end_str else 'Actualidad')


# ==================== AUTO MIGRATION ====================

def run_auto_migration():
    """Checks and adds missing columns automatically on startup"""
    with app.app_context():
        from sqlalchemy import text, inspect
        inspector = inspect(db.engine)
        
        if not inspector.has_table("leagues"):
            return

        columns = [c['name'] for c in inspector.get_columns('leagues')]
        
        with db.engine.connect() as conn:
            if 'logo_url' not in columns:
                try:
                    conn.execute(text("ALTER TABLE leagues ADD COLUMN logo_url TEXT"))
                    conn.commit()
                    print("Auto-Migration: logo_url added via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (logo_url): {e}")

            if 'slogan' not in columns:
                try:
                    conn.execute(text("ALTER TABLE leagues ADD COLUMN slogan VARCHAR(255)"))
                    conn.commit()
                    print("Auto-Migration: slogan added via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (slogan): {e}")

            if 'playoff_type' not in columns:
                try:
                    conn.execute(text("ALTER TABLE leagues ADD COLUMN playoff_type VARCHAR(20)"))
                    conn.commit()
                    print("Auto-Migration: playoff_type added via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (playoff_type): {e}")

            if 'number' not in [c['name'] for c in inspector.get_columns('players')]:
                try:
                    conn.execute(text("ALTER TABLE players ADD COLUMN number INTEGER"))
                    conn.commit()
                    print("Auto-Migration: number added via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (number): {e}")

            if 'premium_expires_at' not in [c['name'] for c in inspector.get_columns('users')]:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN premium_expires_at TIMESTAMP"))
                    conn.commit()
                    print("Auto-Migration: premium_expires_at added via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (premium_expires_at): {e}")

            # Teams Soft Delete
            if 'is_deleted' not in [c['name'] for c in inspector.get_columns('teams')]:
                try:
                    conn.execute(text("ALTER TABLE teams ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                    print("Auto-Migration: is_deleted added to teams via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (teams.is_deleted): {e}")

            # Courts Table
            if not inspector.has_table("courts"):
                try:
                    conn.execute(text('''
                        CREATE TABLE courts (
                            id VARCHAR(36) PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            league_id VARCHAR(36) NOT NULL,
                            created_at TIMESTAMP,
                            FOREIGN KEY(league_id) REFERENCES leagues(id)
                        )
                    '''))
                    conn.commit()
                    print("Auto-Migration: courts table created via app.py")
                except Exception as e:
                    print(f"Auto-Migration Error (create courts): {e}")

            # Matches Court ID
            if 'court_id' not in [c['name'] for c in inspector.get_columns('matches')]:
                try:
                    conn.execute(text("ALTER TABLE matches ADD COLUMN court_id VARCHAR(36) REFERENCES courts(id)"))
                    conn.commit()
                    print("Auto-Migration: court_id added to matches via app.py")
                    
                    # Optional: Create default court and assign existing matches
                    # This is complex to do safely in auto-migration for all scenarios, 
                    # but essential for preventing null errors in reports if not handled via code.
                    # For now, code handles null court_id (e.g. "Cancha Principal" fallback).
                except Exception as e:
                    print(f"Auto-Migration Error (matches.court_id): {e}")

# Run once on module load (works for Gunicorn workers)
try:
    run_auto_migration()
except Exception as e:
    print(f"Migration Setup Failed: {e}")


# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
