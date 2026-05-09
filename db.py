import sqlite3
import os

# ─── DATABASE PATH ────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "expense_app.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name e.g. row["name"]
    return conn

# ─── SETUP ────────────────────────────────────────────────────
def initialize_db():
    """Creates all tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # PROFILES — one per user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            lifestyle   TEXT    DEFAULT 'Student',
            currency    TEXT    DEFAULT '₱',
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # CATEGORIES — custom per profile
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id  INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            icon        TEXT    DEFAULT '📦',
            FOREIGN KEY (profile_id) REFERENCES profiles(id)
        )
    """)

    # TRANSACTIONS — every expense/income entry
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

    # BUDGETS — spending limits per category
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

# ─── PROFILES ─────────────────────────────────────────────────
def create_profile(name, lifestyle="Student", currency="₱"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO profiles (name, lifestyle, currency) VALUES (?, ?, ?)",
            (name, lifestyle, currency)
        )
        conn.commit()
        print(f"✅ Profile '{name}' created.")
    except sqlite3.IntegrityError:
        print(f"⚠️  Profile '{name}' already exists.")
    finally:
        conn.close()

def get_all_profiles():
    conn = get_connection()
    profiles = conn.execute("SELECT * FROM profiles").fetchall()
    conn.close()
    return profiles

def get_profile(profile_id):
    conn = get_connection()
    profile = conn.execute(
        "SELECT * FROM profiles WHERE id = ?", (profile_id,)
    ).fetchone()
    conn.close()
    return profile

def delete_profile(profile_id):
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE profile_id = ?", (profile_id,))
    conn.execute("DELETE FROM budgets     WHERE profile_id = ?", (profile_id,))
    conn.execute("DELETE FROM categories  WHERE profile_id = ?", (profile_id,))
    conn.execute("DELETE FROM profiles    WHERE id = ?",         (profile_id,))
    conn.commit()
    conn.close()
    print(f"🗑️  Profile {profile_id} deleted.")

# ─── CATEGORIES ───────────────────────────────────────────────
def create_category(profile_id, name, icon="📦"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO categories (profile_id, name, icon) VALUES (?, ?, ?)",
        (profile_id, name, icon)
    )
    conn.commit()
    conn.close()

def get_categories(profile_id):
    conn = get_connection()
    cats = conn.execute(
        "SELECT * FROM categories WHERE profile_id = ?", (profile_id,)
    ).fetchall()
    conn.close()
    return cats

def delete_category(category_id):
    conn = get_connection()
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()

# ─── TRANSACTIONS ─────────────────────────────────────────────
def add_transaction(profile_id, category_id, type_, amount, description, date):
    conn = get_connection()
    conn.execute("""
        INSERT INTO transactions (profile_id, category_id, type, amount, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (profile_id, category_id, type_, amount, description, date))
    conn.commit()
    conn.close()

def get_transactions(profile_id, month=None):
    """
    Returns transactions for a profile.
    If month is given (e.g. '2026-05'), filters by that month.
    """
    conn = get_connection()
    if month:
        rows = conn.execute("""
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.profile_id = ? AND strftime('%Y-%m', t.date) = ?
            ORDER BY t.date DESC
        """, (profile_id, month)).fetchall()
    else:
        rows = conn.execute("""
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.profile_id = ?
            ORDER BY t.date DESC
        """, (profile_id,)).fetchall()
    conn.close()
    return rows

def delete_transaction(transaction_id):
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

# ─── BUDGETS ──────────────────────────────────────────────────
def set_budget(profile_id, category_id, amount, period="monthly"):
    """Creates or updates a budget for a category."""
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM budgets WHERE profile_id = ? AND category_id = ?",
        (profile_id, category_id)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE budgets SET amount = ?, period = ? WHERE id = ?",
            (amount, period, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO budgets (profile_id, category_id, amount, period) VALUES (?, ?, ?, ?)",
            (profile_id, category_id, amount, period)
        )
    conn.commit()
    conn.close()

def get_budgets(profile_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, c.name as category_name, c.icon as category_icon
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.profile_id = ?
    """, (profile_id,)).fetchall()
    conn.close()
    return rows

# ─── SUMMARY QUERIES ──────────────────────────────────────────
def get_monthly_summary(profile_id, month):
    """
    Returns total income and total expenses for a given month.
    month format: 'YYYY-MM' e.g. '2026-05'
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT
            SUM(CASE WHEN type = 'income'  THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
        WHERE profile_id = ? AND strftime('%Y-%m', date) = ?
    """, (profile_id, month)).fetchone()
    conn.close()
    return row

def get_spending_by_category(profile_id, month):
    """Returns expense totals grouped by category for a given month."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.name, c.icon, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.profile_id = ? AND t.type = 'expense'
        AND strftime('%Y-%m', t.date) = ?
        GROUP BY c.id
        ORDER BY total DESC
    """, (profile_id, month)).fetchall()
    conn.close()
    return rows

# ─── QUICK TEST ───────────────────────────────────────────────
if __name__ == "__main__":
    initialize_db()

    # Test: create a profile
    create_profile("Juan", lifestyle="Student", currency="₱")

    # Test: get all profiles
    profiles = get_all_profiles()
    for p in profiles:
        print(f"Profile: {p['name']} | Lifestyle: {p['lifestyle']}")

    # Test: create categories
    profile_id = profiles[0]["id"]
    create_category(profile_id, "Food", "🍚")
    create_category(profile_id, "Transport", "🚌")
    create_category(profile_id, "Load", "📱")

    # Test: add a transaction
    cats = get_categories(profile_id)
    add_transaction(profile_id, cats[0]["id"], "expense", 120.00, "Lunch", "2026-05-09")

    # Test: monthly summary
    summary = get_monthly_summary(profile_id, "2026-05")
    print(f"Income: {summary['total_income']} | Expense: {summary['total_expense']}")

    print("✅ All tests passed.")