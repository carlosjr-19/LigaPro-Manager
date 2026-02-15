from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import League, Team, Match, Player, Court, SeasonStat
from forms import LeagueForm, StatForm, MatchForm
from utils.decorators import owner_required, premium_required
from utils.helpers import calculate_standings
from sqlalchemy import or_
from datetime import datetime
import json

league_bp = Blueprint('league', __name__)

@league_bp.route('/leagues/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_league():
    # Check league limit for non-premium users
    if not current_user.is_premium:
        league_count = League.query.filter_by(user_id=current_user.id).count()
        if league_count >= 3:
            flash('Usuarios gratuitos pueden crear máximo 3 ligas. Actualiza a Premium.', 'warning')
            return redirect(url_for('premium.premium'))
    
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
        return redirect(url_for('league.league_detail', league_id=league.id))
    
    return render_template('league_form.html', form=form, title='Nueva Liga')


@league_bp.route('/leagues/<league_id>')
@login_required
@owner_required
def league_detail(league_id):
    if current_user.role == 'admin':
        league = League.query.get_or_404(league_id)
    else:
        league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Show only active teams in the list, but keep deleted teams for historical match references if needed
    # Show only active teams in the list, but keep deleted teams for historical match references if needed
    active_teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    # Scheduling Teams (Exclude Hidden)
    print("DEBUG: Active Teams:", [(t.name, t.is_hidden) for t in active_teams])
    scheduling_teams = [t for t in active_teams if not t.is_hidden]
    print("DEBUG: Scheduling Teams:", [t.name for t in scheduling_teams])
    all_teams = Team.query.filter_by(league_id=league_id).all() # Need all for matches history lookup
    
    standings = calculate_standings(league_id)

    # Form for editing league settings (embedded)
    form = LeagueForm(obj=league)
    
    # Update Form Choices to use scheduling_teams
    # Removed incorrect form fields assignments as LeagueForm does not have home_team/away_team
    
    # Matches Paging
    page = request.args.get('page', 1, type=int)
    matches_pagination = Match.query.filter(
        Match.league_id == league_id,
        or_(Match.stage == 'regular', Match.stage == None, Match.stage == '')
    ).order_by(Match.match_date.desc()).paginate(page=page, per_page=30, error_out=False)
    
    matches = matches_pagination.items 

    # Matrix View Data
    # Use scheduling_teams for Matrix
    match_matrix = {}
    for home in scheduling_teams:
        match_matrix[home.id] = {}
        for away in scheduling_teams:
            if home.id == away.id:
                 match_matrix[home.id][away.id] = {'status': 'cnt_play'} 
            else:
                 match_matrix[home.id][away.id] = {'status': 'empty', 'home_id': home.id, 'away_id': away.id}

    # Fetch ALL regular matches
    all_regular_matches = Match.query.filter(
        Match.league_id == league_id,
        or_(Match.stage == 'regular', Match.stage == None, Match.stage == '')
    ).all()
    
    for m in all_regular_matches:
        if m.home_team_id in match_matrix and m.away_team_id in match_matrix[m.home_team_id]:
             # We found a match for this cell
             match_matrix[m.home_team_id][m.away_team_id] = {
                 'status': 'scheduled',
                 'match': {
                     'id': m.id,
                     'home_score': m.home_score,
                     'away_score': m.away_score,
                     'match_date_iso': m.match_date.isoformat(),
                     'match_date_display': m.match_date.strftime('%d-%b'),
                     'match_time_display': m.match_date.strftime('%I:%M %p'),
                     'court_id': m.court_id,
                     'is_completed': m.is_completed
                 },
                 'home_id': m.home_team_id,
                 'away_id': m.away_team_id
             }
             if m.is_completed:
                  match_matrix[m.home_team_id][m.away_team_id]['status'] = 'completed'

    playoff_matches = {
        'repechaje': Match.query.filter_by(league_id=league_id, stage='repechaje').all(),
        'quarterfinal': Match.query.filter_by(league_id=league_id, stage='quarterfinal').all(),
        'semifinal': Match.query.filter_by(league_id=league_id, stage='semifinal').all(),
        'final': Match.query.filter_by(league_id=league_id, stage='final').all()
    }
    has_playoffs = any(len(m) > 0 for m in playoff_matches.values())
    
    teams_dict = {t.id: t for t in all_teams}
    
    # Teams Data for JS (Matrix View) use scheduling_teams
    teams_js = {t.id: {'name': t.name, 'shield_url': t.shield_url} for t in scheduling_teams}
    
    # Pass players by team for JS dropdown
    players_by_team = {}
    for team in active_teams:
        players = Player.query.filter_by(team_id=team.id).order_by(Player.name).all()
        players_by_team[team.id] = [{'id': p.id, 'name': p.name, 'photo_url': p.photo_url} for p in players]
    
    # Get Season Stats
    top_scorers = SeasonStat.query.filter_by(league_id=league_id, stat_type='goals').order_by(SeasonStat.value.desc()).all()
    top_goalkeepers = SeasonStat.query.filter_by(league_id=league_id, stat_type='conceded').order_by(SeasonStat.value.asc()).all()
    
    # Dashboard Data
    recent_matches = Match.query.filter(
        Match.league_id == league_id,
        Match.is_completed == True
    ).order_by(Match.match_date.desc()).limit(3).all()

    upcoming_matches = Match.query.filter(
        Match.league_id == league_id,
        Match.is_completed == False
    ).order_by(Match.match_date).limit(3).all()

    # Form for adding stats (Owner Only)
    stat_form = StatForm()
    if current_user.role == 'owner' or current_user.role == 'admin':
        stat_form.team_id.choices = [(t.id, t.name) for t in active_teams]
    
    return render_template('league_detail.html', 
                          league=league, 
                          teams=active_teams,
                          courts=league.courts,
                          standings=standings,
                          matches=matches,
                          match_matrix=match_matrix,
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
                          teams_js=teams_js,
                          scheduling_teams=scheduling_teams,
                          form=form)


@league_bp.route('/leagues/<league_id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='settings'))
    
    return render_template('league_form.html', form=form, title='Editar Liga', league=league)


@league_bp.route('/leagues/<league_id>/delete', methods=['POST'])
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
    return redirect(url_for('main.dashboard'))


@league_bp.route('/leagues/<league_id>/courts', methods=['POST'])
@login_required
@owner_required
@premium_required
def add_court(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Check limit (premium only, max 3)
    court_count = Court.query.filter_by(league_id=league_id).count()
    if court_count >= 3:
        flash('Máximo 3 canchas permitidas.', 'warning')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='settings'))
    
    court_name = request.form.get('court_name')
    if not court_name or len(court_name.strip()) == 0:
        flash('El nombre de la cancha es requerido.', 'danger')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='settings'))
        
    court = Court(name=court_name, league_id=league_id)
    db.session.add(court)
    db.session.commit()
    
    flash('Cancha agregada exitosamente.', 'success')
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='settings'))


@league_bp.route('/courts/<court_id>/update', methods=['POST'])
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
        
    return redirect(url_for('league.league_detail', league_id=league.id, _anchor='settings'))


@league_bp.route('/courts/<court_id>/delete', methods=['POST'])
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
        return redirect(url_for('league.league_detail', league_id=league.id, _anchor='settings'))
    
    # Check if matches assigned
    match_count = Match.query.filter_by(court_id=court.id).count()
    if match_count > 0:
        flash('No puedes eliminar una cancha con partidos asignados.', 'warning')
        return redirect(url_for('league.league_detail', league_id=league.id, _anchor='settings'))
        
    db.session.delete(court)
    db.session.commit()
    flash('Cancha eliminada.', 'success')
    return redirect(url_for('league.league_detail', league_id=league.id, _anchor='settings'))


@league_bp.route('/leagues/<league_id>/share', methods=['GET', 'POST'])
@login_required
@owner_required
def generate_share_report(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Get form data - Checkboxes send their value (e.g., 'on') only if checked. 
    # If unchecked, they are missing from request.values.
    # We check for presence (is not None) to handle 'on', 'true', etc.
    include_standings = request.values.get('include_standings') is not None
    include_recent = request.values.get('include_recent') is not None
    date_start_str = request.values.get('date_start')
    date_end_str = request.values.get('date_end')
    include_upcoming = request.values.get('include_upcoming') is not None
    include_scorers = request.values.get('include_scorers') is not None
    include_keepers = request.values.get('include_keepers') is not None
    
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

