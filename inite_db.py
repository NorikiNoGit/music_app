import sqlite3

DB_PATH = "music.db"  # データベースファイル名

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS music (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        title TEXT,
        artist TEXT,
        duration REAL,
        filesize INTEGER,
        created_at TEXT,
        source_url TEXT,
        tags TEXT,
        genre_ai TEXT
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
