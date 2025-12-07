from app.data.db import connect_database

def GetUserByUsername(username):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def InsertUser(username, password_hash):
    """Insert new user."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    conn.commit()
    conn.close()