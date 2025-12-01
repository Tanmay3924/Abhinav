from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
from celery import Celery

# -----------------------------
# Extensions (Global)
# -----------------------------
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
cache = Cache()

# Global Celery instance (empty for now)
celery = Celery('app', broker=None, backend=None)



# -----------------------------
# Celery Factory
# -----------------------------
def make_celery(app):
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery.conf.timezone = app.config.get("CELERY_TIMEZONE", "Asia/Kolkata")
    
    # Add this line to fix the next warning:
    celery.conf.broker_connection_retry_on_startup = True

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
# -----------------------------
# Flask Application Factory
# -----------------------------
def create_app(config_class=None):
    app = Flask(__name__)

    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        from .config import Config
        app.config.from_object(Config)

    # Enable CORS for frontend
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True
    )

    # Initialize Flask extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    # Initialize Celery WITH this Flask app config
    global celery
    celery = make_celery(app)

    # Register Blueprints
    from .auth import auth_bp
    from .admin import admin_bp
    from .user import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(user_bp, url_prefix="/api/user")

    # Create DB tables + seed admin
    with app.app_context():
        db.create_all()
        seed_admin(app)

    return app


# -----------------------------
# Seed Admin User
# -----------------------------
def seed_admin(app):
    from .models import User

    admin_email = app.config.get("ADMIN_EMAIL", "tanmay.aj2004@gmail.com")
    admin_pass = app.config.get("ADMIN_PASSWORD", "AdminPass123")

    # Check if admin already exists
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
        print(f"✔ Admin created: {admin_email}")
from . import tasks
