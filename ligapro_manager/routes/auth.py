from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt, login_manager
from models import User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.is_suspended:
                flash('Tu cuenta ha sido suspendida. Contacta al administrador.', 'danger')
                return render_template('login.html', form=form)
                
            login_user(user)
            flash('¡Bienvenido!', 'success')
            next_page = request.args.get('next')
            if current_user.role == 'admin':
                return redirect(next_page or url_for('admin.admin_dashboard'))
            if current_user.role == 'captain':
                return redirect(next_page or url_for('main.captain_dashboard'))
            return redirect(next_page or url_for('main.dashboard'))
        flash('Email o contraseña incorrectos.', 'danger')
    
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash('Este email ya está registrado.', 'danger')
        else:
            hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(
                name=form.name.data,
                email=form.email.data,
                password=hashed,
                role='owner'
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('¡Cuenta creada exitosamente!', 'success')
            return redirect(url_for('main.dashboard'))
    
    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    step = 'email'
    if 'reset_user_id' in session:
        step = 'password'
        
    if request.method == 'POST':
        if step == 'email':
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            
            if user:
                session['reset_user_id'] = user.id
                flash('Usuario encontrado. Por favor establece tu nueva contraseña.', 'success')
                return redirect(url_for('auth.forgot_password'))
            else:
                flash('No encontramos una cuenta con ese correo.', 'danger')
                
        elif step == 'password':
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')
            
            if password != confirm:
                flash('Las contraseñas no coinciden.', 'danger')
            else:
                user_id = session.get('reset_user_id')
                user = User.query.get(user_id)
                
                if user:
                    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
                    user.password = hashed
                    db.session.commit()
                    
                    session.pop('reset_user_id', None)
                    flash('Contraseña actualizada exitosamente. Inicia sesión.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    session.pop('reset_user_id', None)
                    flash('Error de sesión. Intenta de nuevo.', 'danger')
                    return redirect(url_for('auth.forgot_password'))
                    
    return render_template('forgot_password.html', step=step)
