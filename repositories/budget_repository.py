from database.connection import get_connection


def set_budget(profile_id, category_id, amount, period="monthly"):
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
            """
            INSERT INTO budgets
            (profile_id, category_id, amount, period)
            VALUES (?, ?, ?, ?)
            """,
            (profile_id, category_id, amount, period)
        )

    conn.commit()
    conn.close()



def get_budgets(profile_id):
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            b.*,
            c.name as category_name,
            c.icon as category_icon
        FROM budgets b
        JOIN categories c
            ON b.category_id = c.id
        WHERE b.profile_id = ?
    """, (profile_id,)).fetchall()

    conn.close()

    return rows