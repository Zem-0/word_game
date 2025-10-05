# word_game

Simple Flask word-guessing game with a small words database and admin/player views.

This repository contains a lightweight Flask app that stores a list of five-letter words and runs a guessing game. It includes small utility scripts to seed the database, a raw SQL seed file, and templates for the UI.

## Contents

- `app.py` — Flask application entry point and routes.
- `models.py` — SQLAlchemy models (Word, Game, Guess, etc.).
- `seed_words.py` — Python script to seed the words table with a default list.
- `add_words.py` — Smaller helper script to add a handful of words.
- `insert_words.sql` — Raw SQL seed that inserts a small list of words (optional to keep).
- `templates/` — Jinja2 templates for the website.
- `requirements.txt` — Python dependencies.

## Quick start

1. Create and activate a virtual environment (Python 3.10+ recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Configure the database URL in `config.py` (the app reads DB settings from there).

4. Initialize the database (example uses Flask-Migrate / Alembic if configured):

```powershell
flask db upgrade
```

5. Seed the database. You have two options:

- Python seed (recommended): runs inside the app context and uses the ORM.

```powershell
python seed_words.py
```

- Raw SQL seed (optional): run `insert_words.sql` directly against your Postgres database if you prefer raw SQL.

```powershell
psql "<your-connection-string>" -f insert_words.sql
```

6. Run the app locally:

```powershell
flask run
```

Open http://127.0.0.1:5000 in your browser.

## Which seed to use?

- The repository includes `seed_words.py` and `add_words.py` which insert words using SQLAlchemy; these are the primary, recommended ways to seed because they respect the app's models and constraints.
- `insert_words.sql` is a convenience file if you want to run raw SQL directly against the DB or keep a SQL snapshot. It's not referenced by the app. If you don't need it, it's safe to remove or move into a `sql/` or `data/` folder for documentation.

## Development notes

- To add more words, update `seed_words.py` or create new migration files and use the ORM to insert data.
- Templates live in `templates/` and can be edited to change the UI.