from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="player")  # admin / player
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), nullable=False, unique=True)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished = db.Column(db.Boolean, default=False)
    won = db.Column(db.Boolean, default=False)

class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    guess_word = db.Column(db.String(5), nullable=False)
    result = db.Column(db.String, nullable=False)  # store as JSON string
