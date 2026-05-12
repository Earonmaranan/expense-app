from database.connection import get_connection


def get_monthly_summary(profile_id, month):
    conn = get_connection()

    row = conn.execute("""
        SELECT
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
        WHERE profile_id = ?
        AND strftime('%Y-%m', date) = ?
    """, (profile_id, month)).fetchone()

    conn.close()

    return row


def get_spending_by_category(profile_id, month):
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            c.name,
            c.icon,
            SUM(t.amount) as total
        FROM transactions t
        JOIN categories c
            ON t.category_id = c.id
        WHERE t.profile_id = ?
        AND t.type = 'expense'
        AND strftime('%Y-%m', t.date) = ?
        GROUP BY c.id
        ORDER BY total DESC
    """, (profile_id, month)).fetchall()

    conn.close()

    return rows