import os
from datetime import timedelta

class Config:
    # 1. Basic Flask Config
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # 2. Database Config (Absolute Path to avoid "File not found" errors)
    # This places parkzone.db in the backend/ folder
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASEDIR, 'parkzone.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. JWT Config
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # 4. Admin Credentials
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPass123")

    # 5. Caching Config (Redis)
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT = 300

    # 6. Celery Config (Redis)
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    # Ensure Celery uses your local time
    CELERY_TIMEZONE = 'Asia/Kolkata' 

    # 7. Email Config (SMTP)
    # If using Gmail, you MUST use an App Password, not your login password
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'baburaoo1500@gmail.com') 
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'yqgu gwux cnod nckc')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', 'baburaoo1500@gmail.com')