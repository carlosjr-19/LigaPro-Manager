from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def owner_required(f):
    """Decorator to require owner role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'owner' and current_user.role != 'admin':
            flash('Acceso denegado. Solo para administradores.', 'danger')
            return redirect(url_for('main.captain_dashboard')) # Updated endpoint
        return f(*args, **kwargs)
    return decorated_function


def premium_required(f):
    """Decorator to require premium subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_active_premium:
            flash('Esta función requiere suscripción Premium.', 'warning')
            return redirect(url_for('premium.premium')) # Updated endpoint
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Acceso denegado. Solo para administradores del sistema.', 'danger')
            return redirect(url_for('main.dashboard')) # Updated endpoint
        return f(*args, **kwargs)
    return decorated_function
