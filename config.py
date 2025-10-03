import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    
    # Use SQLite for development, but allow DATABASE_URL override for production
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(BASE_DIR, 'game_app.db')}"
    
    # If DATABASE_URL starts with postgres://, replace it with postgresql://
    # This is needed because SQLAlchemy expects postgresql:// but Heroku/Render provides postgres://
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
