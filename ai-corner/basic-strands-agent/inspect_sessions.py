"""
Utility script to inspect SQLite session database.

Run: python inspect_sessions.py
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def inspect_database(db_path: str = None):
    """Inspect the SQLite session database."""
    if db_path is None:
        db_path = str(Path.home() / ".strands" / "sessions.db")

    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("Run session-manager-sqlite.py first to create some sessions!")
        return

    print(f"\n{'=' * 70}")
    print(f"📊 Inspecting: {db_path}")
    print(f"{'=' * 70}\n")

    with sqlite3.connect(db_path) as conn:
        # List all sessions
        print("📁 Sessions:")
        print("-" * 70)
        cursor = conn.execute("""
            SELECT session_id, created_at, updated_at
            FROM sessions
            ORDER BY created_at DESC
        """)
        sessions = cursor.fetchall()

        if not sessions:
            print("   No sessions found")
        else:
            for session_id, created_at, updated_at in sessions:
                print(f"   • {session_id}")
                print(f"     Created:  {created_at}")
                print(f"     Updated:  {updated_at}")

        # List agents
        print("\n🤖 Agents:")
        print("-" * 70)
        cursor = conn.execute("""
            SELECT session_id, agent_id, system_prompt, updated_at
            FROM agents
            ORDER BY session_id, updated_at DESC
        """)
        agents = cursor.fetchall()

        if not agents:
            print("   No agents found")
        else:
            for session_id, agent_id, system_prompt, updated_at in agents:
                print(f"   • Session: {session_id}")
                print(f"     Agent ID: {agent_id}")
                print(f"     Prompt: {system_prompt[:60]}...")
                print(f"     Updated: {updated_at}")

        # Count messages per session
        print("\n💬 Messages:")
        print("-" * 70)
        cursor = conn.execute("""
            SELECT session_id, agent_id, COUNT(*) as msg_count
            FROM messages
            GROUP BY session_id, agent_id
            ORDER BY session_id
        """)
        message_counts = cursor.fetchall()

        if not message_counts:
            print("   No messages found")
        else:
            for session_id, agent_id, count in message_counts:
                print(f"   • {session_id} ({agent_id}): {count} messages")

        # Show recent messages from a specific session
        if sessions:
            session_id = sessions[0][0]  # Most recent session
            print(f"\n💭 Recent messages from '{session_id}':")
            print("-" * 70)

            cursor = conn.execute("""
                SELECT message_id, role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY message_id DESC
                LIMIT 10
            """, (session_id,))

            messages = cursor.fetchall()
            if not messages:
                print("   No messages in this session")
            else:
                for msg_id, role, content in reversed(messages):
                    content_data = json.loads(content)
                    # Extract text from content
                    text = ""
                    if isinstance(content_data, list):
                        for item in content_data:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    text = item.get("text", "")
                                    break

                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"\n   [{msg_id}] {role.upper()}")
                    print(f"   {preview}")

    print(f"\n{'=' * 70}")
    print("✅ Inspection complete!")
    print(f"{'=' * 70}\n")


def delete_session(session_id: str, db_path: str = None):
    """Delete a specific session from the database."""
    if db_path is None:
        db_path = str(Path.home() / ".strands" / "sessions.db")

    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        print(f"✅ Deleted session: {session_id}")


def clear_all_sessions(db_path: str = None):
    """Clear all sessions from the database."""
    if db_path is None:
        db_path = str(Path.home() / ".strands" / "sessions.db")

    response = input("⚠️  Delete ALL sessions? (yes/no): ")
    if response.lower() == "yes":
        with sqlite3.connect(db_path) as conn:
            conn.execute("DELETE FROM sessions")
            conn.commit()
            print("✅ All sessions cleared!")
    else:
        print("❌ Cancelled")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "clear":
            clear_all_sessions()
        elif command == "delete" and len(sys.argv) > 2:
            delete_session(sys.argv[2])
        else:
            print("Usage:")
            print("  python inspect_sessions.py         # Inspect database")
            print("  python inspect_sessions.py clear   # Clear all sessions")
            print("  python inspect_sessions.py delete <session_id>  # Delete specific session")
    else:
        inspect_database()
