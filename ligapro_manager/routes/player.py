from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Team, Player
from forms import PlayerForm
from utils.decorators import premium_required

player_bp = Blueprint('player', __name__)

@player_bp.route('/teams/<team_id>/players/new', methods=['GET', 'POST'])
@login_required
def create_player(team_id):
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
        return redirect(url_for('team.team_detail', team_id=team_id))
    
    return render_template('player_form.html', form=form, team=team, title='Nuevo Jugador')


@player_bp.route('/players/<player_id>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('main.captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    form = PlayerForm(obj=player)
    if form.validate_on_submit():
        player.name = form.name.data
        player.number = form.number.data
        player.curp = form.curp.data
        player.photo_url = form.photo_url.data
        db.session.commit()
        flash('Jugador actualizado.', 'success')
        return redirect(url_for('team.team_detail', team_id=team.id))
    
    return render_template('player_form.html', form=form, player=player, team=team, title='Editar Jugador')


@player_bp.route('/players/<player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    team = player.team
    league = team.league
    
    # Check access
    if current_user.role == 'captain':
        if current_user.team_id != team.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('main.captain_dashboard'))
    else:
        if league.user_id != current_user.id:
            flash('No tienes acceso.', 'danger')
            return redirect(url_for('main.dashboard'))
    
    team_id = player.team_id
    db.session.delete(player)
    db.session.commit()
    flash('Jugador eliminado.', 'success')
    return redirect(url_for('team.team_detail', team_id=team_id))
