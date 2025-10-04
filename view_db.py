import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def view_database():
    # Get database URL from environment variable
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment variables")
        return

    try:
        # Connect to the database
        with psycopg.connect(DATABASE_URL) as conn:
            # Create a cursor
            with conn.cursor() as cur:
                print("\n=== Words in database ===")
                cur.execute("SELECT id, word FROM word")
                words = cur.fetchall()
                for word_id, word in words:
                    print(f"ID: {word_id}, Word: {word}")

                print("\n=== Users in database ===")
                cur.execute("SELECT id, username, role FROM \"user\"")
                users = cur.fetchall()
                for user_id, username, role in users:
                    print(f"ID: {user_id}, Username: {username}, Role: {role}")

                print("\n=== Games in database ===")
                cur.execute("""
                    SELECT g.id, g.user_id, w.word, g.finished, g.won, g.started_at 
                    FROM game g 
                    LEFT JOIN word w ON g.word_id = w.id
                """)
                games = cur.fetchall()
                for game_id, user_id, word, finished, won, started_at in games:
                    print(f"Game ID: {game_id}, User ID: {user_id}, Word: {word}, Won: {won}, Finished: {finished}, Started: {started_at}")

                print("\n=== Guesses in database ===")
                cur.execute("SELECT id, game_id, guess_word, result FROM guess")
                guesses = cur.fetchall()
                for guess_id, game_id, guess_word, result in guesses:
                    print(f"Guess ID: {guess_id}, Game ID: {game_id}, Word: {guess_word}, Result: {result}")

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == '__main__':
    view_database()