import sqlite3

from database.connection import get_connection


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
        print(f"⚠️ Profile '{name}' already exists.")

    finally:
        conn.close()



def get_all_profiles():
    conn = get_connection()

    profiles = conn.execute(
        "SELECT * FROM profiles"
    ).fetchall()

    conn.close()

    return profiles



def get_profile(profile_id):
    conn = get_connection()

    profile = conn.execute(
        "SELECT * FROM profiles WHERE id = ?",
        (profile_id,)
    ).fetchone()

    conn.close()

    return profile



def delete_profile(profile_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM transactions WHERE profile_id = ?",
        (profile_id,)
    )

    conn.execute(
        "DELETE FROM budgets WHERE profile_id = ?",
        (profile_id,)
    )

    conn.execute(
        "DELETE FROM categories WHERE profile_id = ?",
        (profile_id,)
    )

    conn.execute(
        "DELETE FROM profiles WHERE id = ?",
        (profile_id,)
    )

    conn.commit()
    conn.close()

    print(f"🗑️ Profile {profile_id} deleted.")