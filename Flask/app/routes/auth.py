from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Usuario
from app import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = Usuario.query.filter_by(email=email, activo=True).first()

        if user and user.check_password(password):
            if user.rol.nombre == 'gerente':
                flash('El acceso del gerente es por el sistema de reportes (Laravel).', 'warning')
                return render_template('auth/login.html')

            login_user(user)
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            return _redirect_by_role(user)

        flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))


def _redirect_by_role(user):
    role = user.rol.nombre
    if role == 'operativo':
        return redirect(url_for('ventas.index'))
    elif role == 'almacen':
        return redirect(url_for('inventario.dashboard'))
    return redirect(url_for('auth.login'))
