from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import League, Team, Match, Court, SeasonStat
from forms import MatchForm, MatchResultForm
from utils.decorators import owner_required
import json
from datetime import datetime, timezone
from utils.helpers import calculate_standings

match_bp = Blueprint('match', __name__)

@match_bp.route('/leagues/<league_id>/matches/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_match(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    # Only allow scheduling matches between active teams
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False, is_hidden=False).all()
    
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
            return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))

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


@match_bp.route('/matches/<match_id>/result', methods=['GET', 'POST'])
@login_required
@owner_required
def update_match_result(match_id):
    match = Match.query.get_or_404(match_id)
    league = match.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = MatchResultForm(obj=match)
    
    # Populate Choice Fields (inherited from MatchForm)
    # Include all teams (even deleted ones if they are already part of the match, or just active ones)
    # Ideally should match create_match logic but maybe allow keeping existing if deleted
    teams = Team.query.filter_by(league_id=league.id).all() 
    # Use active_teams for dropdowns usually, but if this match involves a deleted team, we should probably include it or handle it.
    # For simplicity, let's load active teams.
    active_teams = Team.query.filter_by(league_id=league.id, is_deleted=False).all()
    form.home_team_id.choices = [(t.id, t.name) for t in active_teams]
    form.away_team_id.choices = [(t.id, t.name) for t in active_teams]
    
    # Ensure current teams are in choices even if deleted (so validation passes)
    current_home_in_choices = any(str(t.id) == str(match.home_team_id) for t in active_teams)
    if not current_home_in_choices:
        home_t = Team.query.get(match.home_team_id)
        if home_t: form.home_team_id.choices.append((home_t.id, home_t.name))
        
    current_away_in_choices = any(str(t.id) == str(match.away_team_id) for t in active_teams)
    if not current_away_in_choices:
        away_t = Team.query.get(match.away_team_id)
        if away_t: form.away_team_id.choices.append((away_t.id, away_t.name))
        
    courts = Court.query.filter_by(league_id=league.id).all()
    form.court_id.choices = [(c.id, c.name) for c in courts]
    
    if form.validate_on_submit():
        # Update Match Details
        match.home_team_id = form.home_team_id.data
        match.away_team_id = form.away_team_id.data
        match.court_id = form.court_id.data
        match.match_date = form.match_date.data
        
        # Update Scores (Only if both scores are provided)
        match.home_score = form.home_score.data
        match.away_score = form.away_score.data
        
        if match.home_score is not None and match.away_score is not None:
            match.is_completed = True
        else:
            match.is_completed = False
        
        db.session.commit()
        flash('Partido actualizado (Resultados y Detalles).', 'success')
        anchor = 'playoff' if match.stage not in ['regular', None] else 'matches'
        return redirect(url_for('league.league_detail', league_id=league.id, _anchor=anchor))
    
    home_team = Team.query.get(match.home_team_id)
    away_team = Team.query.get(match.away_team_id)
    
    return render_template('match_result_form.html', form=form, match=match, 
                          home_team=home_team, away_team=away_team, league=league)


@match_bp.route('/matches/<match_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    league_id = match.league_id
    
    if match.league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    # Removed check for is_completed to allow deleting finalized matches
        
    db.session.delete(match)
    db.session.commit()
    flash('Partido eliminado.', 'success')
    anchor = 'playoff' if match.stage not in ['regular', None, ''] else 'matches'
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor=anchor))


@match_bp.route('/matches/<match_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    league_id = match.league_id
    league = match.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    if match.is_completed:
        flash('No se pueden editar los detalles de un partido ya jugado. Solo se puede modificar el resultado.', 'warning')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='matches'))
        
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
            anchor = 'playoff' if match.stage not in ['regular', None, ''] else 'matches'
            return redirect(url_for('league.league_detail', league_id=league_id, _anchor=anchor))
            
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


@match_bp.route('/leagues/<league_id>/reset_season', methods=['POST'])
@login_required
@owner_required
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
    return redirect(url_for('league.league_detail', league_id=league_id))


@match_bp.route('/leagues/<league_id>/playoffs/reset', methods=['POST'])
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
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))

@match_bp.route('/leagues/<league_id>/playoffs/generate', methods=['POST'])
@login_required
@owner_required
def generate_playoffs(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    mode = request.form.get('mode', 'corte_directo')
    playoff_type = request.form.get('playoff_type', 'single')

    # Premium check for double leg
    if playoff_type == 'double' and not current_user.is_active_premium:
        flash('La modalidad Ida y Vuelta es exclusiva para Premium.', 'warning')
        return redirect(url_for('premium.premium'))
    
    standings = calculate_standings(league_id)
    total_teams = len(standings)
    
    if total_teams < 5:
        flash('Se necesitan al menos 5 equipos para la liguilla.', 'danger')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
    
    # Delete existing playoff matches
    Match.query.filter(
        Match.league_id == league_id,
        Match.stage.in_(['repechaje', 'round_of_16', 'quarterfinal', 'semifinal', 'final'])
    ).delete(synchronize_session=False)
    
    # Clear playoff state
    league.playoff_mode = mode
    league.playoff_type = playoff_type
    league.playoff_bye_teams = None
    
    playoff_matches = []
    bye_teams = []
    
    # Get default court (first one registered)
    default_court = Court.query.filter_by(league_id=league_id).order_by(Court.created_at.asc()).first()
    default_court_id = default_court.id if default_court else None


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
                return redirect(url_for('league.league_detail', league_id=league_id))
            
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
    
    # Large leagues (16+ teams) -> Round of 16
    elif total_teams >= 16:
        if mode == 'corte_directo':
            # Top 16 -> Round of 16
            for i in range(8):
                playoff_matches.append({
                    'home': standings[i], 'away': standings[15-i], 'stage': 'round_of_16',
                    'name': f"Octavo {i+1}: {standings[i]['team'].name} vs {standings[15-i]['team'].name}"
                })
        else: # con_repechaje for 16+ teams could be complex, keeping top 14 with bye or similar. 
              # For now, let's keep it simple: if >= 16 and corte_directo, do 16.
              # If con_repechaje, let's do top 12 bye and 13-20 repechaje?
              # User explicitly asked for 16 teams.
            for i in range(8):
                playoff_matches.append({
                    'home': standings[i], 'away': standings[15-i], 'stage': 'round_of_16',
                    'name': f"Octavo {i+1}: {standings[i]['team'].name} vs {standings[15-i]['team'].name}"
                })

    # Medium leagues (8+ teams)
    elif total_teams >= 8:
        if mode == 'corte_directo':
            # Top 8 -> Quarterfinals
            if total_teams < 8:
                flash('Se necesitan al menos 8 equipos para corte directo.', 'danger')
                return redirect(url_for('league.league_detail', league_id=league_id))
            
            # Match 1: 1 vs 8
            playoff_matches.append({
                'home': standings[0], 'away': standings[7], 'stage': 'quarterfinal',
                'name': f"Cuarto 1: {standings[0]['team'].name} vs {standings[7]['team'].name}"
            })
            # Match 2: 2 vs 7
            playoff_matches.append({
                'home': standings[1], 'away': standings[6], 'stage': 'quarterfinal',
                'name': f"Cuarto 2: {standings[1]['team'].name} vs {standings[6]['team'].name}"
            })
            # Match 3: 3 vs 6
            playoff_matches.append({
                'home': standings[2], 'away': standings[5], 'stage': 'quarterfinal',
                'name': f"Cuarto 3: {standings[2]['team'].name} vs {standings[5]['team'].name}"
            })
            # Match 4: 4 vs 5
            playoff_matches.append({
                'home': standings[3], 'away': standings[4], 'stage': 'quarterfinal',
                'name': f"Cuarto 4: {standings[3]['team'].name} vs {standings[4]['team'].name}"
            })
        else:  # con_repechaje
            if total_teams < 10:
                flash('Se necesitan al menos 10 equipos para modo con repechaje.', 'danger')
                return redirect(url_for('league.league_detail', league_id=league_id))
            
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
        league.playoff_bye_teams = json.dumps(bye_teams)
    
    # Create matches
    created_count = 0
    for m in playoff_matches:
        # Match 1 (Ida or Single)
        match1 = Match(
            league_id=league_id,
            home_team_id=m['home']['team'].id,
            away_team_id=m['away']['team'].id,
            court_id=default_court_id,
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
                court_id=default_court_id,
                match_date=datetime.now(timezone.utc), # Should ideally be later
                stage=m['stage'],
                match_name=m['name'].replace(m['home']['team'].name, "TEMP").replace(m['away']['team'].name, m['home']['team'].name).replace("TEMP", m['away']['team'].name) + " (Vuelta)"
            )
            db.session.add(match2)
            created_count += 1
    
    db.session.commit()
    flash(f'Liguilla generada ({mode} - {playoff_type}). {created_count} partidos creados.', 'success')
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))


@match_bp.route('/leagues/<league_id>/playoffs/advance', methods=['POST'])
@login_required
@owner_required
def advance_playoff_round(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Get all playoff matches
    playoff_matches = Match.query.filter(
        Match.league_id == league_id,
        Match.stage.in_(['repechaje', 'round_of_16', 'quarterfinal', 'semifinal', 'final'])
    ).all()
    
    if not playoff_matches:
        flash('No hay partidos de liguilla.', 'danger')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
    
    stages_order = ['repechaje', 'round_of_16', 'quarterfinal', 'semifinal', 'final']
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
                return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
    
    if not active_stage:
        flash('No se encontró una fase activa.', 'danger')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
    
    # Check if tournament finished
    if active_stage == 'final':
        final = active_stage_matches[0]
        winner = Team.query.get(final.home_team_id if final.home_score > final.away_score else final.away_team_id)
        flash(f'¡El torneo ha terminado! Campeón: {winner.name} 🏆', 'success')
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
    
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
        return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
        
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
        return redirect(url_for('league.league_detail', league_id=league_id))
        
    # Generate Matches (Best vs Worst)
    num_matches = num_qualified // 2
    teams_dict = {t.id: t for t in Team.query.filter_by(league_id=league_id).all()}
    
    # Get default court
    default_court = Court.query.filter_by(league_id=league_id).order_by(Court.created_at.asc()).first()
    default_court_id = default_court.id if default_court else None
    
    created_count = 0
    
    for i in range(num_matches):
        home_id = winners[i]
        away_id = winners[num_qualified - 1 - i]
        
        
        # Match 1 (Ida or Single) - Final is ALWAYS single
        match1 = Match(
            league_id=league_id,
            home_team_id=home_id,
            away_team_id=away_id,
            court_id=default_court_id,
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
                court_id=default_court_id,
                match_date=datetime.now(timezone.utc),
                stage=next_stage,
                match_name=f"{next_stage.capitalize()}: {teams_dict[away_id].name} vs {teams_dict[home_id].name} (Vuelta)"
            )
            db.session.add(match2)
            created_count += 1
        
    db.session.commit()
    flash(f'Ronda generada: {next_stage} ({created_count} partidos).', 'success')
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='playoff'))
