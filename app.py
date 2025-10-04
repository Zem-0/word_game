from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm
from models import db, User, Word, Game, Guess
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from utils import grade_guess
import random
import json

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pw, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session.pop('_flashes', None)
            flash("Login successful!", "success")
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    return render_template("admin_dashboard.html")

@app.route("/user_dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/start_game", methods=["POST"])
@login_required
def start_game():
    # Check if we have any words, if not add them
    words = Word.query.all()
    if not words:
        default_words = [
            'APPLE', 'BRAVE', 'CHESS', 'DRIVE', 'EAGLE',
            'FAITH', 'GRAPE', 'HOUSE', 'INPUT', 'JUMBO'
        ]
        for word in default_words:
            db.session.add(Word(word=word))
        db.session.commit()
        words = Word.query.all()

    # Start the game
    word = random.choice(words)
    new_game = Game(user_id=current_user.id, word_id=word.id)
    db.session.add(new_game)
    db.session.commit()
    session['current_game_id'] = new_game.id
    flash("Game started!", "success")
    return redirect(url_for("get_current_game"))

@app.route("/current_game")
@login_required
def get_current_game():
    """Get the current active game for the logged-in user"""
    current_game_id = session.get('current_game_id')
    if not current_game_id:
        active_game = Game.query.filter_by(user_id=current_user.id, finished=False).first()
        if active_game:
            session['current_game_id'] = active_game.id
            current_game_id = active_game.id
        else:
            flash("No active game found", "info")
            return redirect(url_for("user_dashboard"))
    game = Game.query.get(current_game_id)
    if not game or game.user_id != current_user.id or game.finished:
        session.pop('current_game_id', None)
        active_game = Game.query.filter_by(user_id=current_user.id, finished=False).first()
        if active_game:
            session['current_game_id'] = active_game.id
            game = active_game
        else:
            flash("No active game found", "info")
            return redirect(url_for("user_dashboard"))
    guesses = Guess.query.filter_by(game_id=game.id).order_by(Guess.id).all()
    guess_history = []
    parsed_guesses = []
    for guess in guesses:
        result = json.loads(guess.result)
        guess_history.append({
            "guess_word": guess.guess_word,
            "result": result
        })
        parsed_guesses.append({
            "guess_word": guess.guess_word,
            "result": result
        })
    return render_template("current_game.html", 
                         game=game, 
                         guesses=parsed_guesses,
                         guesses_left=max(0, 5 - len(guesses)))

@app.route("/game_history")
@login_required
def game_history():
    """Show user's game history"""
    games = Game.query.filter_by(user_id=current_user.id).order_by(Game.id.desc()).limit(20).all()
    game_stats = []
    for game in games:
        guesses = Guess.query.filter_by(game_id=game.id).count()
        game_stats.append({
            "game_id": game.id,
            "finished": game.finished,
            "won": game.won,
            "guesses_count": guesses,
            "started_at": game.started_at
        })
    return render_template("game_history.html", games=game_stats)

@app.route("/game/<int:game_id>/guess", methods=["POST"])
@login_required
def make_guess(game_id):
    game = Game.query.get_or_404(game_id)
    if game.user_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for("user_dashboard"))
    if game.finished:
        flash("Game already finished", "warning")
        return redirect(url_for("get_current_game"))
    guess_word = request.form.get("guess", "").upper()
    if len(guess_word) != 5:
        flash("Guess must be exactly 5 letters", "danger")
        return redirect(url_for("get_current_game"))
    target_word = Word.query.get(game.word_id).word
    result = grade_guess(target_word, guess_word)
    g = Guess(game_id=game.id, guess_word=guess_word, result=json.dumps(result))
    db.session.add(g)
    guesses_count = Guess.query.filter_by(game_id=game.id).count()
    if all(r=="green" for r in result):
        game.finished = True
        game.won = True
        session.pop('current_game_id', None)  
    elif guesses_count >= 5:
        game.finished = True
        session.pop('current_game_id', None)  
    
    db.session.commit()
    if game.finished:
        if game.won:
            flash(f"Congratulations! You won in {guesses_count} guesses!", "success")
        else:
            flash(f"Game over! The word was {target_word}", "info")
        return redirect(url_for("user_dashboard"))
    else:
        flash("Guess submitted!", "info")
        return redirect(url_for("get_current_game"))

@app.route("/end_game/<int:game_id>")
@login_required
def end_game(game_id):
    """End the current game early"""
    game = Game.query.get_or_404(game_id)
    if game.user_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for("user_dashboard"))
    if not game.finished:
        game.finished = True
        game.won = False
        db.session.commit()
        session.pop('current_game_id', None)
        flash("Game ended", "info")
    return redirect(url_for("user_dashboard"))

@app.route("/api/admin/users")
@login_required
def api_admin_users():
    """Get list of all users for admin reports"""
    if current_user.role != "admin":
        return jsonify({"error": "Access denied"}), 403
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

@app.route("/api/admin/daily-report")
@login_required
def api_admin_daily_report():
    """Get daily report for a specific date"""
    if current_user.role != "admin":
        return jsonify({"error": "Access denied"}), 403
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date parameter required"}), 400
    try:
        from datetime import datetime
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        users_played = db.session.query(Game.user_id).filter(
            db.func.date(Game.started_at) == target_date
        ).distinct().count()
        
        total_games = Game.query.filter(
            db.func.date(Game.started_at) == target_date
        ).count()
        
        games_won = Game.query.filter(
            db.func.date(Game.started_at) == target_date,
            Game.won == True
        ).count()
        correct_guesses = games_won
        return jsonify({
            "total_users": users_played,
            "correct_guesses": correct_guesses,
            "total_games": total_games,
            "games_won": games_won
        })
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

@app.route("/api/admin/user-report")
@login_required
def api_admin_user_report():
    """Get user-specific report"""
    if current_user.role != "admin":
        return jsonify({"error": "Access denied"}), 403
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID parameter required"}), 400
    try:
        user = User.query.get_or_404(user_id)
        user_games = Game.query.filter_by(user_id=user_id).order_by(Game.started_at.desc()).all()
        from collections import defaultdict
        games_by_date = defaultdict(lambda: {"words_tried": 0, "correct_guesses": 0})
        for game in user_games:
            date_str = game.started_at.date().strftime('%Y-%m-%d')
            games_by_date[date_str]["words_tried"] += 1
            if game.won:
                games_by_date[date_str]["correct_guesses"] += 1
        reports = []
        for date_str in sorted(games_by_date.keys(), reverse=True):
            reports.append({
                "date": date_str,
                "words_tried": games_by_date[date_str]["words_tried"],
                "correct_guesses": games_by_date[date_str]["correct_guesses"]
            })
        return jsonify({"reports": reports})
    except Exception as e:
        return jsonify({"error": f"Error generating user report: {str(e)}"}), 500

@app.route("/api/admin/system-overview")
@login_required
def api_admin_system_overview():
    """Get system overview statistics"""
    if current_user.role != "admin":
        return jsonify({"error": "Access denied"}), 403
    try:
        total_users = User.query.count()
        total_games = Game.query.count()
        games_won = Game.query.filter_by(won=True).count()
        win_rate = (games_won / total_games * 100) if total_games > 0 else 0
        return jsonify({
            "total_users": total_users,
            "total_games": total_games,
            "games_won": games_won,
            "win_rate": round(win_rate, 1)
        })
    except Exception as e:
        return jsonify({"error": "Error generating system overview"}), 500

if __name__ == "__main__":
    app.run(debug=True)

