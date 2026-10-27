from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from extensions import db
from models import League, Team, Match, SeasonStat, LeagueGroup
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
    groups = LeagueGroup.query.filter_by(user_id=current_user.id).order_by(LeagueGroup.created_at.asc()).all()
    leagues = League.query.filter_by(user_id=current_user.id).order_by(League.display_order.asc(), League.created_at.asc()).all()
    
    allowed_league_ids = [l.id for l in leagues]
    if not current_user.is_active_premium and len(leagues) > 3:
        allowed_league_ids = [l.id for l in leagues[:3]]
        
    active_group_id = request.args.get('group', '')
    groups_data = [g.to_dict() for g in groups]
    
    # Calculate ungrouped leagues
    grouped_league_ids = set()
    for g in groups:
        for l in g.leagues:
            grouped_league_ids.add(l.id)
    ungrouped_leagues = [l for l in leagues if l.id not in grouped_league_ids]
    
    return render_template('dashboard.html', 
                           leagues=leagues, 
                           groups=groups, 
                           groups_data=groups_data,
                           active_group_id=active_group_id,
                           ungrouped_leagues=ungrouped_leagues,
                           allowed_league_ids=allowed_league_ids)


@main_bp.route('/groups/create', methods=['POST'])
@login_required
@owner_required
def create_group():
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#3b82f6').strip()
    league_ids = request.form.getlist('league_ids')
    
    if not name:
        flash('Debes proporcionar un nombre para la carpeta/grupo.', 'warning')
        return redirect(url_for('main.dashboard'))
        
    group = LeagueGroup(
        name=name,
        user_id=current_user.id,
        color=color or '#3b82f6'
    )
    
    if league_ids:
        valid_leagues = League.query.filter(League.id.in_(league_ids), League.user_id == current_user.id).all()
        group.leagues.extend(valid_leagues)
        
    db.session.add(group)
    db.session.commit()
    flash(f'Carpeta "{name}" creada con éxito.', 'success')
    return redirect(url_for('main.dashboard', group=group.id))


@main_bp.route('/groups/<group_id>/edit', methods=['POST'])
@login_required
@owner_required
def edit_group(group_id):
    group = LeagueGroup.query.filter_by(id=group_id, user_id=current_user.id).first_or_404()
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#3b82f6').strip()
    league_ids = request.form.getlist('league_ids')
    
    if not name:
        flash('El nombre de la carpeta no puede estar vacío.', 'warning')
        return redirect(url_for('main.dashboard', group=group.id))
        
    group.name = name
    group.color = color or '#3b82f6'
    
    valid_leagues = League.query.filter(League.id.in_(league_ids), League.user_id == current_user.id).all() if league_ids else []
    group.leagues = valid_leagues
    
    db.session.commit()
    flash(f'Carpeta "{name}" actualizada.', 'success')
    return redirect(url_for('main.dashboard', group=group.id))


@main_bp.route('/groups/<group_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_group(group_id):
    group = LeagueGroup.query.filter_by(id=group_id, user_id=current_user.id).first_or_404()
    name = group.name
    group.leagues = []
    db.session.delete(group)
    db.session.commit()
    flash(f'Carpeta "{name}" eliminada (tus ligas no se borraron).', 'info')
    return redirect(url_for('main.dashboard'))


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
    
    # Filter notes for captain
    notes = [n for n in team.notes if n.is_public]
    notes.sort(key=lambda x: x.created_at, reverse=True)
    
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
                          notes=notes,
                          teams_dict=teams_dict,
                          top_scorers=top_scorers,
                          top_goalkeepers=top_goalkeepers)
