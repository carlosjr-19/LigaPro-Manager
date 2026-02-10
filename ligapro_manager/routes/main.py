from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from models import League, Team, Match, SeasonStat
from utils.decorators import owner_required
from utils.helpers import calculate_standings

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        next_page = request.args.get('next')
        if current_user.role == 'admin':
            return redirect(next_page or url_for('admin.admin_dashboard'))
        if current_user.role == 'captain':
            return redirect(next_page or url_for('main.captain_dashboard'))
        return redirect(next_page or url_for('main.dashboard'))
    return render_template('landing.html', title='Inicio')


@main_bp.route('/dashboard')
@login_required
@owner_required
def dashboard():
    leagues = League.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', leagues=leagues)


@main_bp.route('/captain')
@login_required
def captain_dashboard():
    if current_user.role != 'captain':
        return redirect(url_for('main.dashboard'))
    
    team = Team.query.get(current_user.team_id)
    if not team:
        flash('No tienes equipo asignado.', 'warning')
        logout_user() # Fix: Logout if invalid state
        return redirect(url_for('auth.login'))
    
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
