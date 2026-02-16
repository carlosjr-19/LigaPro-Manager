from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db, bcrypt
from models import League, Team, Match, Player, TeamNote, User
from forms import TeamForm, PlayerForm
from utils.decorators import owner_required

team_bp = Blueprint('team', __name__)

@team_bp.route('/leagues/<league_id>/teams/new', methods=['GET', 'POST'])
@login_required
@owner_required
def create_team(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    # Check team limit
    # Check team limit
    team_count = Team.query.filter_by(league_id=league_id, is_deleted=False).count()
    if not current_user.is_active_premium and team_count >= 12:
        flash('Límite de 12 equipos para usuarios gratuitos.', 'warning')
        return redirect(url_for('league.league_detail', league_id=league_id))
    
    if team_count >= league.max_teams:
        flash(f'La liga ya tiene el máximo de {league.max_teams} equipos.', 'warning')
        return redirect(url_for('league.league_detail', league_id=league_id))
    
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
        return redirect(url_for('team.team_detail', team_id=team.id))
    
    return render_template('team_form.html', form=form, league=league, title='Nuevo Equipo')


@team_bp.route('/teams/<team_id>')
@login_required
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team_id:
            flash('No tienes acceso a este equipo.', 'danger')
            return redirect(url_for('main.captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso a este equipo.', 'danger')
            return redirect(url_for('main.dashboard'))
    
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


@team_bp.route('/teams/<team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team_id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('main.captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.shield_url = form.shield_url.data
        db.session.commit()
        flash('Equipo actualizado.', 'success')
        return redirect(url_for('team.team_detail', team_id=team_id))
    
    return render_template('team_form.html', form=form, team=team, league=league, title='Editar Equipo')


@team_bp.route('/teams/<team_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
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
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='teams'))


@team_bp.route('/teams/<team_id>/toggle_visibility', methods=['POST'])
@login_required
@owner_required
def toggle_team_visibility(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    team.is_hidden = not team.is_hidden
    db.session.commit()
    
    status = "OCULTO" if team.is_hidden else "VISIBLE"
    flash(f'Equipo {team.name} ahora está {status}.', 'success' if not team.is_hidden else 'warning')
    return redirect(url_for('team.team_detail', team_id=team.id))


@team_bp.route('/teams/<team_id>/captain', methods=['POST'])
@login_required
@owner_required
def add_captain(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    captain_name = request.form.get('captain_name')
    if not captain_name:
        flash('Nombre del capitán requerido.', 'danger')
        return redirect(url_for('team.team_detail', team_id=team_id))
    
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
    return redirect(url_for('team.team_detail', team_id=team_id))


@team_bp.route('/teams/<team_id>/notes', methods=['POST'])
@login_required
@owner_required
def add_team_note(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
    if league.user_id != current_user.id:
        flash('No tienes acceso.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    text = request.form.get('note_text')
    if text:
        note = TeamNote(team_id=team_id, text=text)
        db.session.add(note)
        db.session.commit()
        flash('Nota agregada.', 'success')
    
    return redirect(url_for('team.team_detail', team_id=team_id))


@team_bp.route('/teams/<team_id>/credentials', methods=['GET'])
@login_required
def generate_credentials(team_id):
    team = Team.query.get_or_404(team_id)
    league = team.league
    
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
            return redirect(url_for('main.captain_dashboard'))
        return redirect(url_for('main.dashboard'))
    
    # Premium Access Logic
    # 1. League Owner is Premium -> Access Granted to Owner AND Captain
    # 2. Captain is Premium -> Access Granted to Captain (Plan Capitán)
    
    has_access = False
    
    if is_owner:
        if league.owner.is_active_premium:
            has_access = True
    
    if is_captain:
        if league.owner.is_active_premium or current_user.is_active_premium:
             has_access = True
             
    if not has_access:
        flash('Esta función requiere Premium (Dueño de Liga o Plan Capitán).', 'warning')
        if is_captain and not is_owner:
            return redirect(url_for('premium.captain_premium'))
        else:
            return redirect(url_for('premium.premium'))
            
    players = Player.query.filter_by(team_id=team_id).order_by(Player.number.asc(), Player.name.asc()).all()
    
    return render_template('credentials.html', team=team, players=players, league=league)
