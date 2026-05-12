from database.connection import get_connection


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            lifestyle   TEXT    DEFAULT 'Student',
            currency    TEXT    DEFAULT '₱',
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id  INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            icon        TEXT    DEFAULT '📦',
            FOREIGN KEY (profile_id) REFERENCES profiles(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id  INTEGER NOT NULL,
            category_id INTEGER,
            type        TEXT    NOT NULL CHECK(type IN ('expense', 'income')),
            amount      REAL    NOT NULL,
            description TEXT,
            date        TEXT    DEFAULT (date('now')),
            FOREIGN KEY (profile_id)  REFERENCES profiles(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id  INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            period      TEXT    DEFAULT 'monthly',
            FOREIGN KEY (profile_id)  REFERENCES profiles(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Database initialized.")