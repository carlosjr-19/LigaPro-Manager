from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user
from extensions import db, bcrypt
from models import User, League, Team, Match, Player
from datetime import datetime, timedelta
from forms import RegisterForm
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Statistics
    total_users = User.query.count()
    premium_users = User.query.filter_by(is_premium=True).count()
    total_leagues = League.query.count()
    total_teams = Team.query.count()
    total_players = Player.query.count()
    
    # Recent users (last 5)
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         premium_users=premium_users,
                         total_leagues=total_leagues,
                         total_teams=total_teams,
                         total_players=total_players,
                         recent_users=recent_users)


@admin_bp.route('/admin/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('No puedes eliminar administradores.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
        
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {user.email} eliminado.', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/users/<user_id>/toggle_premium', methods=['POST'])
@login_required
@admin_required
def toggle_premium(user_id):
    user = User.query.get_or_404(user_id)
    user.is_premium = not user.is_premium
    
    # Al cambiar el estado manual, limpiamos cualquier fecha de expiración
    # para evitar estados inconsistentes (ej: desactivar manual pero que siga activo por fecha)
    user.premium_expires_at = None
        
    db.session.commit()
    status = "PREMIUM" if user.is_premium else "GRATUITO"
    flash(f'Usuario {user.email} es ahora {status}.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/users/<user_id>/toggle_suspend', methods=['POST'])
@login_required
@admin_required
def toggle_suspend(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('No puedes suspender a un administrador.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
        
    user.is_suspended = not user.is_suspended
    db.session.commit()
    status = "SUSPENDIDO" if user.is_suspended else "ACTIVO"
    flash(f'Usuario {user.email} está ahora {status}.', 'warning' if user.is_suspended else 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/users/<user_id>/toggle_ultra', methods=['POST'])
@login_required
@admin_required
def toggle_ultra(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('No puedes modificar atributos de un administrador.', 'danger')
        return redirect(url_for('admin.users'))
        
    user.is_ultra = not user.is_ultra
    db.session.commit()
    status = "ULTRA" if user.is_ultra else "ESTÁNDAR"
    flash(f'Usuario {user.email} es ahora {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')

    query = User.query

    if search:
        query = query.filter(User.email.ilike(f'%{search}%') | User.name.ilike(f'%{search}%'))
    
    if role:
        query = query.filter_by(role=role)

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, search=search, current_role=role)


@admin_bp.route('/admin/leagues')
@login_required
@admin_required
def leagues():
    leagues = League.query.order_by(League.created_at.desc()).all()
    return render_template('admin/leagues.html', leagues=leagues)


@admin_bp.route('/admin/teams')
@login_required
@admin_required
def teams():
    teams = Team.query.order_by(Team.created_at.desc()).all()
    return render_template('admin/teams.html', teams=teams)


@admin_bp.route('/admin/users/<user_id>/grant_premium', methods=['POST'])
@login_required
@admin_required
def grant_premium(user_id):
    user = User.query.get_or_404(user_id)
    days = int(request.form.get('days', 7))
    
    if not user.premium_expires_at or user.premium_expires_at < datetime.utcnow():
        user.premium_expires_at = datetime.utcnow() + timedelta(days=days)
    else:
        user.premium_expires_at += timedelta(days=days)
        
    db.session.commit()
    flash(f'Se otorgaron {days} días de Premium a {user.email}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<user_id>/login_as', methods=['POST'])
@login_required
@admin_required
def login_as(user_id):
    user = User.query.get_or_404(user_id)
    login_user(user)
    flash(f'Has iniciado sesión como {user.name}.', 'info')
    return redirect(url_for('main.dashboard'))

@admin_bp.route('/admin/users/<user_id>/colors', methods=['POST'])
@login_required
@admin_required
def update_user_colors(user_id):
    user = User.query.get_or_404(user_id)
    
    color_win = request.form.get('color_win')
    color_loss = request.form.get('color_loss')
    highlight_mode = request.form.get('highlight_mode', 'simple')
    
    if color_win and color_loss:
        user.color_win = color_win
        user.color_loss = color_loss
        user.highlight_mode = highlight_mode
        db.session.commit()
        flash(f'Colores actualizados para {user.name}.', 'success')
    else:
        flash('Ambos colores son requeridos.', 'warning')
        
    return redirect(url_for('admin.users', page=request.args.get('page', 1), search=request.args.get('search', ''), role=request.args.get('role', '')))
