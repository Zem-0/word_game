from app import app, db
from models import Word

words = [
    "APPLE", "BRAVE", "CHESS", "DRIVE", "EAGLE",
    "FAITH", "GRAPE", "HOUSE", "INPUT", "JUMBO",
    "KNIFE", "LEMON", "MONEY", "NINJA", "OCEAN",
    "PLANT", "QUEEN", "RIVER", "SUGAR", "TRUST"
]

with app.app_context():
    for w in words:
        if not Word.query.filter_by(word=w).first():
            db.session.add(Word(word=w))
    db.session.commit()
    print("Words seeded successfully!")
