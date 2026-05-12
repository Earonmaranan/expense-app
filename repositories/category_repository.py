from database.connection import get_connection


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
        "SELECT * FROM categories WHERE profile_id = ?",
        (profile_id,)
    ).fetchall()

    conn.close()

    return cats



def delete_category(category_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM categories WHERE id = ?",
        (category_id,)
    )

    conn.commit()
    conn.close()