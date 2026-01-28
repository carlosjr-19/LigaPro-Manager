"""
LigaPro Manager - Flask Application
Full-stack football league management with PostgreSQL
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, DateTimeField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, InputRequired
from datetime import datetime, timezone
from functools import wraps
import os
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ligapro-secret-key-change-in-production')
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'ligapro.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
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
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    leagues = db.relationship('League', backref='owner', lazy=True, foreign_keys='League.user_id')


class League(db.Model):
    __tablename__ = 'leagues'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    max_teams = db.Column(db.Integer, default=12)
    win_points = db.Column(db.Integer, default=3)
    draw_points = db.Column(db.Integer, default=1)
    loss_points = db.Column(db.Integer, default=0)
    playoff_mode = db.Column(db.String(20), nullable=True)
    playoff_bye_teams = db.Column(db.Text, nullable=True)  # JSON string of team IDs
    show_stats = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    teams = db.relationship('Team', backref='league', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='league', lazy=True, cascade='all, delete-orphan')


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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('TeamNote', backref='team', lazy=True, cascade='all, delete-orphan')
    home_matches = db.relationship('Match', backref='home_team', lazy=True, foreign_keys='Match.home_team_id')
    away_matches = db.relationship('Match', backref='away_team', lazy=True, foreign_keys='Match.away_team_id')


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
    photo_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    league_id = db.Column(db.String(36), db.ForeignKey('leagues.id'), nullable=False)
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
    max_teams = IntegerField('Máximo de Equipos', validators=[DataRequired(), NumberRange(min=4, max=32)], default=12)
    win_points = IntegerField('Puntos por Victoria', validators=[DataRequired()], default=3)
    draw_points = IntegerField('Puntos por Empate', validators=[DataRequired()], default=1)
    # Field handles by template conditional, but need it in form
    show_stats = BooleanField('Mostrar Estadísticas a Capitanes', default=True)


class TeamForm(FlaskForm):
    name = StringField('Nombre del Equipo', validators=[DataRequired(), Length(min=2, max=100)])
    shield_url = StringField('URL del Escudo', validators=[Optional()])
    captain_name = StringField('Nombre del Capitán', validators=[Optional()])


class PlayerForm(FlaskForm):
    name = StringField('Nombre del Jugador', validators=[DataRequired(), Length(min=2, max=100)])
    curp = StringField('CURP', validators=[Optional(), Length(max=20)])
    photo_url = StringField('URL de Foto', validators=[Optional()])


class MatchForm(FlaskForm):
    home_team_id = SelectField('Equipo Local', validators=[DataRequired()])
    away_team_id = SelectField('Equipo Visitante', validators=[DataRequired()])
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
        if current_user.role != 'owner':
            flash('Acceso denegado. Solo para administradores.', 'danger')
            return redirect(url_for('captain_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """Decorator to require premium subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_premium:
            flash('Esta función requiere suscripción Premium.', 'warning')
            return redirect(url_for('premium'))
        return f(*args, **kwargs)
    return decorated_function


def calculate_standings(league_id, include_playoffs=False):
    """Calculate standings for a league"""
    league = League.query.get_or_404(league_id)
    teams = Team.query.filter_by(league_id=league_id).all()
    
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
        if current_user.role == 'captain':
            return redirect(url_for('captain_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


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
        if not current_user.is_premium and max_teams > 12:
            max_teams = 12
            flash('Límite de 12 equipos para usuarios gratuitos.', 'info')
        
        league = League(
            name=form.name.data,
            user_id=current_user.id,
            max_teams=max_teams,
            win_points=form.win_points.data,
            draw_points=form.draw_points.data
        )
        db.session.add(league)
        db.session.commit()
        flash('Liga creada exitosamente.', 'success')
        return redirect(url_for('league_detail', league_id=league.id))
    
    return render_template('league_form.html', form=form, title='Nueva Liga')


@app.route('/leagues/<league_id>')
@login_required
@owner_required
def league_detail(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    teams = Team.query.filter_by(league_id=league_id).all()
    standings = calculate_standings(league_id)
    matches = Match.query.filter_by(league_id=league_id).order_by(Match.match_date).all()
    
    playoff_matches = {
        'repechaje': Match.query.filter_by(league_id=league_id, stage='repechaje').all(),
        'quarterfinal': Match.query.filter_by(league_id=league_id, stage='quarterfinal').all(),
        'semifinal': Match.query.filter_by(league_id=league_id, stage='semifinal').all(),
        'final': Match.query.filter_by(league_id=league_id, stage='final').all()
    }
    has_playoffs = any(len(m) > 0 for m in playoff_matches.values())
    
    teams_dict = {t.id: t for t in teams}
    
    # Pass players by team for JS dropdown
    players_by_team = {}
    for team in teams:
        players = Player.query.filter_by(team_id=team.id).order_by(Player.name).all()
        players_by_team[team.id] = [{'id': p.id, 'name': p.name, 'photo_url': p.photo_url} for p in players]
    
    # Get Season Stats
    top_scorers = SeasonStat.query.filter_by(league_id=league_id, stat_type='goals').order_by(SeasonStat.value.desc()).all()
    top_goalkeepers = SeasonStat.query.filter_by(league_id=league_id, stat_type='conceded').order_by(SeasonStat.value.asc()).all()
    
    # Form for adding stats (Owner Only)
    stat_form = StatForm()
    if current_user.role == 'owner':
        stat_form.team_id.choices = [(t.id, t.name) for t in teams]
    
    return render_template('league_detail.html', 
                          league=league, 
                          teams=teams,
                          standings=standings,
                          matches=matches,
                          playoff_matches=playoff_matches,
                          has_playoffs=has_playoffs,
                          teams_dict=teams_dict,
                          top_scorers=top_scorers,
                          top_goalkeepers=top_goalkeepers,
                          players_by_team=players_by_team,
                          stat_form=stat_form)


@app.route('/leagues/<league_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
@premium_required
def edit_league(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    form = LeagueForm(obj=league)
    
    if form.validate_on_submit():
        league.name = form.name.data
        league.max_teams = form.max_teams.data
        league.win_points = form.win_points.data
        league.draw_points = form.draw_points.data
        if current_user.is_premium:
            league.show_stats = form.show_stats.data
        db.session.commit()
        flash('Liga actualizada.', 'success')
        return redirect(url_for('league_detail', league_id=league_id))
    
    return render_template('league_form.html', form=form, title='Editar Liga', league=league)


@app.route('/leagues/<league_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_league(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    db.session.delete(league)
    db.session.commit()
    flash('Liga eliminada.', 'success')
    return redirect(url_for('dashboard'))


# ==================== TEAM ROUTES ====================

@app.route('/leagues/<league_id>/teams/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_team(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Check team limit
    team_count = Team.query.filter_by(league_id=league_id).count()
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
    
    # Delete matches involving this team
    Match.query.filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).delete(synchronize_session=False)

    # Delete players
    Player.query.filter_by(team_id=team_id).delete(synchronize_session=False)
    
    # Delete team notes
    TeamNote.query.filter_by(team_id=team_id).delete(synchronize_session=False)

    # Delete captain user if exists
    if team.captain_user_id:
        captain = User.query.get(team.captain_user_id)
        if captain:
            db.session.delete(captain)
    
    db.session.delete(team)
    db.session.commit()
    flash('Equipo eliminado.', 'success')
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
    teams = Team.query.filter_by(league_id=league_id).all()
    
    form = MatchForm()
    form.home_team_id.choices = [(t.id, t.name) for t in teams]
    form.away_team_id.choices = [(t.id, t.name) for t in teams]
    
    if form.validate_on_submit():
        if form.home_team_id.data == form.away_team_id.data:
            flash('El equipo local y visitante no pueden ser el mismo.', 'danger')
        else:
            match = Match(
                league_id=league_id,
                home_team_id=form.home_team_id.data,
                away_team_id=form.away_team_id.data,
                match_date=form.match_date.data,
                stage='regular'
            )
            db.session.add(match)
            db.session.commit()
            flash('Partido programado.', 'success')
            return redirect(url_for('league_detail', league_id=league_id, _anchor='matches'))
    
    return render_template('match_form.html', form=form, league=league, title='Nuevo Partido')


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
    
    db.session.commit()
    flash(f'Temporada reiniciada correctamente. Se eliminaron {deleted} partidos. Equipos y jugadores preservados.', 'success')
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
    for m in playoff_matches:
        match = Match(
            league_id=league_id,
            home_team_id=m['home']['team'].id,
            away_team_id=m['away']['team'].id,
            match_date=datetime.now(timezone.utc),
            stage=m['stage'],
            match_name=m['name']
        )
        db.session.add(match)
    
    db.session.commit()
    flash(f'Liguilla generada ({mode}). {len(playoff_matches)} partidos creados.', 'success')
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
        
        match = Match(
            league_id=league_id,
            home_team_id=home_id,
            away_team_id=away_id,
            match_date=datetime.now(timezone.utc),
            stage=next_stage,
            match_name=f"{next_stage.capitalize()}: {teams_dict[home_id].name} vs {teams_dict[away_id].name}"
        )
        db.session.add(match)
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
    # Populate choices dynamically for validation
    teams = Team.query.filter_by(league_id=league_id).all()
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


@app.route('/premium/activate', methods=['POST'])
@login_required
def activate_premium():
    # In a real app, this would integrate with Stripe
    current_user.is_premium = True
    db.session.commit()
    flash('¡Cuenta Premium activada!', 'success')
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
        print('Admin user already exists')
        return
    
    hashed = bcrypt.generate_password_hash('password123').decode('utf-8')
    admin = User(
        email='delegado@ligapro.com',
        password=hashed,
        name='Delegado Admin',
        role='owner',
        is_premium=False
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: delegado@ligapro.com / password123')


# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
