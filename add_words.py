from app import app, db, Word

words = [
    'APPLE', 'BRAVE', 'CHESS', 'DRIVE', 'EAGLE',
    'FAITH', 'GRAPE', 'HOUSE', 'INPUT', 'JUMBO'
]

def add_words():
    with app.app_context():
        for word in words:
            existing = Word.query.filter_by(word=word).first()
            if not existing:
                db.session.add(Word(word=word))
        db.session.commit()
        print(f"Added words to database. Total words: {Word.query.count()}")

if __name__ == '__main__':
    add_words()