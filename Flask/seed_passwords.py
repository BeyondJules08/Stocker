"""
Run this script once after the first DB init to set proper werkzeug password hashes.
Usage inside Docker:  docker compose exec flask python seed_passwords.py
"""
from app import create_app, db
from app.models import Usuario

USUARIOS = [
    ('gerente@stocker.com',   'Admin123!'),
    ('operativo@stocker.com', 'Operativo1!'),
    ('almacen@stocker.com',   'Almacen1!'),
]

app = create_app()
with app.app_context():
    for email, password in USUARIOS:
        user = Usuario.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            print(f'✓ Password actualizado: {email}')
        else:
            print(f'✗ Usuario no encontrado: {email}')
    db.session.commit()
    print('Listo.')
