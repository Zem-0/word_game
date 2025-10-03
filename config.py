import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    
    # Default to local PostgreSQL if no DATABASE_URL is provided
    DEFAULT_DB_URL = "postgresql://word_game_user:w1mSBI2N2j0pTuHpU0PmjxLvfzTeLTUT@dpg-d3ftdg3e5dus73euufk0-a.oregon-postgres.render.com/word_game"
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or DEFAULT_DB_URL
    
    # If DATABASE_URL starts with postgres://, replace it with postgresql://
    # This is needed because SQLAlchemy expects postgresql:// but Heroku/Render provides postgres://
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
