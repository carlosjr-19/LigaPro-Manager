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
    match_round = request.form.get('match_round', 1, type=int)

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
            stage='regular',
            match_round=match_round
        ).first()
        
        if existing:
            match = existing
            if league.auto_fill_prices and match.referee_cost_home == '0' and match.referee_cost_away == '0' and match.referee_cost == '0':
                if match_datetime and match.match_date != match_datetime:
                    match.referee_cost_home = str(league.price_per_match)
                    match.referee_cost_away = str(league.price_per_match)
                    match.referee_cost = str(league.price_referee)
        else:
            if not match_datetime:
                flash('Debes seleccionar una fecha y hora para programar el partido.', 'danger')
                return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))

            match = Match(
                league_id=league_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                stage='regular',
                match_round=match_round,
                match_name=f"Jornada {match_round}"
            )
            if league.auto_fill_prices:
                match.referee_cost_home = str(league.price_per_match)
                match.referee_cost_away = str(league.price_per_match)
                match.referee_cost = str(league.price_referee)
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
        
        if league.enable_shutdown_tiebreaker and match.home_score == match.away_score:
            shutdown_winner_id = request.form.get('shutdown_winner_id')
            if shutdown_winner_id in [str(match.home_team_id), str(match.away_team_id)]:
                match.shutdown_winner_id = shutdown_winner_id
            else:
                match.shutdown_winner_id = None
        else:
            match.shutdown_winner_id = None
    else:
        match.is_completed = False
        match.shutdown_winner_id = None

    # Practice Match
    match.is_practice = request.form.get('is_practice') == 'on'

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
        
    keep_in_ai = request.form.get('keep_in_ai_report')
    if keep_in_ai == '1' and getattr(current_user, 'is_ultra', False):
        from models import ArchivedFinance
        import json
        
        def parse_cost(val):
            if not val: return 0
            if isinstance(val, str) and not val.isdigit(): return 0 
            try: return int(val)
            except: return 0
            
        def is_waived(val):
            if isinstance(val, str) and val.upper() in ['NSP', 'GIFT']: 
                return True
            return False

        date_key = match.match_date.date() if match.match_date else None
        if date_key:
            court_name = match.court.name if match.court else "Sin Cancha"
            
            income_home = parse_cost(match.referee_cost_home) if not is_waived(match.referee_cost_home) else 0
            income_away = parse_cost(match.referee_cost_away) if not is_waived(match.referee_cost_away) else 0
            expense_ref = parse_cost(match.referee_cost) if not is_waived(match.referee_cost) else 0
            
            income = income_home + income_away
            expense = expense_ref
            
            match_data = {
                'home': match.home_team.name if match.home_team else 'Local',
                'away': match.away_team.name if match.away_team else 'Visita',
                'home_paid': income_home,
                'away_paid': income_away,
                'ref_paid': expense_ref,
                'time': match.match_date.strftime('%H:%M') if match.match_date else '',
                'home_score': match.home_score,
                'away_score': match.away_score,
                'is_practice': getattr(match, 'is_practice', False),
                'expected_price': match.league.price_per_match or 0,
                'match_date_raw': match.match_date.strftime('%Y-%m-%d %H:%M:%S') if match.match_date else '',
                'referee_cost_home_raw': match.referee_cost_home if match.referee_cost_home is not None else "",
                'referee_cost_away_raw': match.referee_cost_away if match.referee_cost_away is not None else "",
                'referee_cost_raw': match.referee_cost if match.referee_cost is not None else "",
                'court_name': court_name
            }
            
            archive = ArchivedFinance.query.filter_by(
                user_id=match.league.user_id,
                league_name=match.league.name,
                court_name=court_name,
                date=date_key
            ).first()
            
            if archive:
                archive.income += income
                archive.expense += expense
                archive.profit += (income - expense)
                if archive.details_json:
                    try:
                        details = json.loads(archive.details_json)
                    except:
                        details = []
                else:
                    details = []
                details.append(match_data)
                archive.details_json = json.dumps(details)
            else:
                archive = ArchivedFinance(
                    user_id=match.league.user_id,
                    league_name=match.league.name,
                    court_name=court_name,
                    date=date_key,
                    income=income,
                    expense=expense,
                    profit=income - expense,
                    details_json=json.dumps([match_data])
                )
                db.session.add(archive)
                
    db.session.delete(match)
    db.session.commit()
    
    flash('Partido eliminado.', 'info')
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))
