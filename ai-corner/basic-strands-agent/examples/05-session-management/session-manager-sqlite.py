"""
Example using SQLite session manager for persistent conversations.

Run this script multiple times - the agent will remember previous conversations!
"""

from strands import Agent
from sqlite_session_manager import SQLiteSessionManager


def main():
    print("=" * 60)
    print("SQLite Session Manager Demo")
    print("=" * 60)

    # Create agent with SQLite session manager
    # All sessions are stored in ~/.strands/sessions.db by default
    session_manager = SQLiteSessionManager(
        session_id="demo-session",
        # db_path="./my_sessions.db"  # Optional: custom database path
    )

    agent = Agent(
        system_prompt="You are a helpful assistant with a great memory.",
        session_manager=session_manager
    )

    # First conversation
    print("\n[User] Tell me your name and remember it")
    response1 = agent("My name is Alex and I love Python programming.")
    print(f"[Agent] {response1}\n")

    # Ask a follow-up question
    print("[User] What's my name and what do I love?")
    response2 = agent("What's my name and what do I love?")
    print(f"[Agent] {response2}\n")

    print("=" * 60)
    print("✅ Session saved to SQLite database")
    print("=" * 60)
    print("\nRun this script again - the agent will remember everything!")
    print("Or try querying the database with:")
    print("  sqlite3 ~/.strands/sessions.db 'SELECT * FROM sessions'")


if __name__ == "__main__":
    main()
