"""
Step 1: Create a simple SQLite database with a sessions table.

Goal: Understand how to create a database and insert/read data.
"""

import sqlite3
from pathlib import Path


def create_database():
    """Create a simple SQLite database with a sessions table."""

    # 1. Choose where to store the database
    db_path = "./my_sessions.db"

    # 2. Connect to the database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # 3. Create a simple sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print(f"✅ Database created: {db_path}")


def add_session(session_id: str):
    """Add a new session to the database."""
    conn = sqlite3.connect("./my_sessions.db")

    conn.execute(
        "INSERT OR REPLACE INTO sessions (session_id) VALUES (?)",
        (session_id,)
    )

    conn.commit()
    conn.close()

    print(f"✅ Added session: {session_id}")


def list_sessions():
    """List all sessions in the database."""
    conn = sqlite3.connect("./my_sessions.db")

    cursor = conn.execute("SELECT session_id, created_at FROM sessions")
    sessions = cursor.fetchall()

    conn.close()

    print("\n📁 Sessions in database:")
    for session_id, created_at in sessions:
        print(f"   • {session_id} (created: {created_at})")


if __name__ == "__main__":
    print("=" * 60)
    print("Step 1: Simple SQLite Database")
    print("=" * 60)

    # Create the database
    create_database()

    # Add some sessions
    add_session("session-001")
    add_session("session-002")
    add_session("session-003")

    # List all sessions
    list_sessions()

    print("\n🔍 Try this command:")
    print("   sqlite3 my_sessions.db 'SELECT * FROM sessions'")
