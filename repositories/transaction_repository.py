from database.connection import get_connection


def add_transaction(profile_id, category_id, type_, amount, description, date):
    conn = get_connection()

    conn.execute("""
        INSERT INTO transactions
        (profile_id, category_id, type, amount, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        profile_id,
        category_id,
        type_,
        amount,
        description,
        date
    ))

    conn.commit()
    conn.close()



def get_transactions(profile_id, month=None):
    conn = get_connection()

    if month:
        rows = conn.execute("""
            SELECT
                t.*,
                c.name as category_name,
                c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c
                ON t.category_id = c.id
            WHERE t.profile_id = ?
            AND strftime('%Y-%m', t.date) = ?
            ORDER BY t.date DESC
        """, (profile_id, month)).fetchall()

    else:
        rows = conn.execute("""
            SELECT
                t.*,
                c.name as category_name,
                c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c
                ON t.category_id = c.id
            WHERE t.profile_id = ?
            ORDER BY t.date DESC
        """, (profile_id,)).fetchall()

    conn.close()

    return rows



def delete_transaction(transaction_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    conn.commit()
    conn.close()