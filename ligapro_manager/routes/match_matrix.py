from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Match, League
from utils.decorators import owner_required
from datetime import datetime

match_matrix_bp = Blueprint('match_matrix', __name__)

@match_matrix_bp.route('/matches/matrix/save', methods=['POST'])
@login_required
@owner_required
def save_match_matrix():
    league_id = request.form.get('league_id')
    home_team_id = request.form.get('home_team_id')
    away_team_id = request.form.get('away_team_id')
    match_id = request.form.get('match_id')

    if not league_id or not home_team_id or not away_team_id:
        flash('Faltan datos requeridos.', 'danger')
        return redirect(request.referrer or url_for('main.dashboard'))

    # Verify League Ownership
    league = League.query.get_or_404(league_id)
    if league.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permiso para editar esta liga.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Parse Date and Time
    date_str = request.form.get('match_date')
    time_str = request.form.get('match_time')
    match_datetime = None

    if date_str and time_str:
        try:
            match_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Formato de fecha u hora inválido.', 'warning')

    # Get Court
    court_id = request.form.get('court_id')
    if not court_id:
        court_id = None

    # Get Scores
    home_score_str = request.form.get('home_score')
    away_score_str = request.form.get('away_score')
    
    home_score = int(home_score_str) if home_score_str and home_score_str.strip() else None
    away_score = int(away_score_str) if away_score_str and away_score_str.strip() else None

    # Find or Create Match
    match = None
    if match_id:
        match = Match.query.get(match_id)
        if not match or match.league_id != league.id:
            flash('Partido no encontrado o inválido.', 'danger')
            return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))
    else:
        # Check if exists (prevent duplicates if ID matches logic)
        existing = Match.query.filter_by(
            league_id=league_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            stage='regular'
        ).first()
        
        if existing:
            match = existing
        else:
            match = Match(
                league_id=league_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                stage='regular',
                match_name="Regular Match"
            )
            db.session.add(match)

    # Update Fields
    if match_datetime:
        match.match_date = match_datetime
    
    if court_id:
        match.court_id = court_id
        
    # Update Fields
    if match_datetime:
        match.match_date = match_datetime
    
    if court_id:
        match.court_id = court_id
        
    # Check for symmetric edit (Swap Detection)
    # If the match's home team is the form's away team, we are editing from the mirrored side.
    if str(match.home_team_id) == str(away_team_id) and str(match.away_team_id) == str(home_team_id):
        # Swap scores to match the real database alignment
        match.home_score = away_score
        match.away_score = home_score
    else:
        # Standard edit
        match.home_score = home_score
        match.away_score = away_score
    
    # Auto-complete if scores are present
    if home_score is not None and away_score is not None:
        match.is_completed = True
    else:
        match.is_completed = False

    db.session.commit()
    flash('Partido actualizado correctamente.', 'success')
    
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))

@match_matrix_bp.route('/matches/matrix/delete', methods=['POST'])
@login_required
@owner_required
def delete_match_matrix():
    match_id = request.form.get('match_id')
    league_id = request.form.get('league_id')
    
    if not match_id or not league_id:
        flash('Datos incompletos para eliminar.', 'danger')
        return redirect(request.referrer)

    match = Match.query.get_or_404(match_id)
    
    # Security Check
    if match.league.user_id != current_user.id and current_user.role != 'admin':
        flash('No tienes permiso.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    db.session.delete(match)
    db.session.commit()
    
    flash('Partido eliminado.', 'info')
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))
