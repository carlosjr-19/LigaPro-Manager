from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import League, Team, SeasonStat, Player
from forms import StatForm
from utils.decorators import owner_required

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/leagues/<league_id>/stats/add', methods=['POST'])
@login_required
@owner_required
def add_stat(league_id):
    league = League.query.filter_by(id=league_id, user_id=current_user.id).first_or_404()
    
    form = StatForm()
    # Populate choices dynamically for validation
    teams = Team.query.filter_by(league_id=league_id, is_deleted=False).all()
    form.team_id.choices = [(t.id, t.name) for t in teams]
    
    if form.validate_on_submit():
        # Check limit for non-premium users
        if not current_user.is_active_premium:
            current_count = SeasonStat.query.filter_by(
                league_id=league_id, 
                stat_type=form.stat_type.data
            ).count()
            
            if current_count >= 5:
                flash(f'Límite de 5 registros alcanzado. Actualiza a Premium para añadir ilimitados.', 'warning')
                return redirect(url_for('league.league_detail', league_id=league_id, _anchor='stats'))

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
        
    return redirect(url_for('league.league_detail', league_id=league_id, _anchor='stats'))


@stats_bp.route('/stats/<stat_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_stat(stat_id):
    stat = SeasonStat.query.get_or_404(stat_id)
    # Check ownership via league
    league = League.query.get(stat.league_id)
    if not league or league.user_id != current_user.id:
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    db.session.delete(stat)
    db.session.commit()
    flash('Estadística eliminada.', 'success')
    return redirect(url_for('league.league_detail', league_id=league.id, _anchor='stats'))


@stats_bp.route('/stats/<stat_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_stat(stat_id):
    stat = SeasonStat.query.get_or_404(stat_id)
    # Check ownership
    league = League.query.get(stat.league_id)
    if not league or league.user_id != current_user.id:
        flash('No tienes permiso para editar esta estadística.', 'danger')
        return redirect(url_for('main.dashboard'))
    
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
        return redirect(url_for('league.league_detail', league_id=league.id, _anchor='stats'))
        
    return render_template('stat_form.html', form=form, stat=stat, league=league)
