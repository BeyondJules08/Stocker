import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder.'
login_manager.login_message_category = 'warning'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.ventas import ventas_bp
    from app.routes.facturas import facturas_bp
    from app.routes.cierre_caja import cierre_bp
    from app.routes.inventario import inventario_bp
    from app.routes.ml import ml_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(facturas_bp, url_prefix='/facturas')
    app.register_blueprint(cierre_bp, url_prefix='/cierre-caja')
    app.register_blueprint(inventario_bp, url_prefix='/inventario')
    app.register_blueprint(ml_bp)

    return app
