from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()

def create_app(config_class=None):
    app = Flask(__name__)

    # Load config
    if config_class:
        app.config.from_object(config_class)
    else:
        from .config import Config
        app.config.from_object(Config)

    # Enable CORS (frontend <-> backend)
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)

    # Register blueprints
    from .auth import auth_bp
    from .admin import admin_bp
    from .user import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(user_bp, url_prefix="/api/user")

    # Create all tables + seed admin
    from .models import User
    with app.app_context():
        db.create_all()
        seed_admin(app, User)

    return app

def seed_admin(app, User):
    """Creates admin user if not present."""
    from . import db

    admin_email = app.config["ADMIN_EMAIL"]
    admin_pass = app.config["ADMIN_PASSWORD"]

    existing = User.query.filter_by(email=admin_email).first()

    if not existing:
        admin = User(
            username="admin",
            email=admin_email,
            role="admin"
        )
        admin.set_password(admin_pass)
        db.session.add(admin)
        db.session.commit()
        print("Admin seeded:", admin_email)
