"""
Interactive tutorial: Learn Session Management Step by Step

Run this and follow along to understand how session management works!
"""

import sqlite3
import json
from pathlib import Path


class LearningSessionManager:
    """Simple session manager for learning - step by step."""

    def __init__(self, db_path="./learning.db"):
        self.db_path = db_path
        print(f"\n📦 Using database: {db_path}")

    def step1_create_tables(self):
        """Step 1: Create the database tables."""
        print("\n" + "=" * 60)
        print("STEP 1: Creating Database Tables")
        print("=" * 60)

        conn = sqlite3.connect(self.db_path)

        # Create sessions table
        print("\n📋 Creating 'sessions' table...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create agents table
        print("📋 Creating 'agents' table...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                session_id TEXT,
                agent_id TEXT,
                system_prompt TEXT,
                state TEXT,
                PRIMARY KEY (session_id, agent_id)
            )
        """)

        # Create messages table
        print("📋 Creating 'messages' table...")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                session_id TEXT,
                agent_id TEXT,
                message_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, agent_id, message_id)
            )
        """)

        conn.commit()
        conn.close()

        print("\n✅ Tables created successfully!")
        print("\n💡 What we did: Created 3 tables to store:")
        print("   1. sessions  - Track conversations")
        print("   2. agents    - Store agent configuration")
        print("   3. messages  - Store all messages in order")

    def step2_create_session(self, session_id):
        """Step 2: Create a new session."""
        print("\n" + "=" * 60)
        print("STEP 2: Creating a Session")
        print("=" * 60)

        conn = sqlite3.connect(self.db_path)

        print(f"\n💾 Creating session: '{session_id}'")
        conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id) VALUES (?)",
            (session_id,)
        )
        conn.commit()
        conn.close()

        print(f"✅ Session '{session_id}' created!")
        print("\n💡 What we did: Added a row to 'sessions' table")
        print(f"   SQL: INSERT INTO sessions (session_id) VALUES ('{session_id}')")

    def step3_create_agent(self, session_id, agent_id, system_prompt):
        """Step 3: Store agent configuration."""
        print("\n" + "=" * 60)
        print("STEP 3: Storing Agent Configuration")
        print("=" * 60)

        conn = sqlite3.connect(self.db_path)

        print(f"\n🤖 Creating agent: '{agent_id}'")
        print(f"   Session: {session_id}")
        print(f"   System prompt: {system_prompt}")

        conn.execute(
            "INSERT OR REPLACE INTO agents (session_id, agent_id, system_prompt, state) VALUES (?, ?, ?, ?)",
            (session_id, agent_id, system_prompt, json.dumps({}))
        )
        conn.commit()
        conn.close()

        print("\n✅ Agent configuration saved!")
        print("\n💡 What we did: Saved agent's system prompt and state")

    def step4_save_message(self, session_id, agent_id, message_id, role, text):
        """Step 4: Save a message to the conversation."""
        print("\n" + "=" * 60)
        print(f"STEP 4: Saving a {role.upper()} Message")
        print("=" * 60)

        conn = sqlite3.connect(self.db_path)

        # Strands stores content as a list of content blocks
        content = [{"type": "text", "text": text}]

        print(f"\n💬 Saving message #{message_id}:")
        print(f"   Role: {role}")
        print(f"   Text: {text}")

        conn.execute(
            "INSERT INTO messages (session_id, agent_id, message_id, role, content) VALUES (?, ?, ?, ?, ?)",
            (session_id, agent_id, message_id, role, json.dumps(content))
        )
        conn.commit()
        conn.close()

        print("\n✅ Message saved!")
        print("\n💡 What we did: Added a row to 'messages' table with:")
        print(f"   - message_id: {message_id} (sequence number)")
        print(f"   - role: {role}")
        print(f"   - content: JSON with the message text")

    def step5_load_messages(self, session_id, agent_id):
        """Step 5: Load all messages from a session."""
        print("\n" + "=" * 60)
        print("STEP 5: Loading Conversation History")
        print("=" * 60)

        conn = sqlite3.connect(self.db_path)

        print(f"\n📖 Loading messages for session '{session_id}'...")

        cursor = conn.execute(
            """SELECT message_id, role, content
               FROM messages
               WHERE session_id = ? AND agent_id = ?
               ORDER BY message_id""",
            (session_id, agent_id)
        )

        messages = cursor.fetchall()
        conn.close()

        print(f"\n✅ Found {len(messages)} messages:")
        print("\n" + "-" * 60)

        for msg_id, role, content in messages:
            content_data = json.loads(content)
            text = content_data[0]["text"] if content_data else ""
            icon = "👤" if role == "user" else "🤖"
            print(f"{icon} [{msg_id}] {role}: {text}")

        print("-" * 60)

        print("\n💡 What we did: Retrieved all messages in order")
        print("   This is how the agent remembers the conversation!")

        return messages

    def step6_continue_conversation(self, session_id, agent_id):
        """Step 6: Show how to continue a conversation."""
        print("\n" + "=" * 60)
        print("STEP 6: Continuing a Conversation")
        print("=" * 60)

        # Load existing messages
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ? AND agent_id = ?",
            (session_id, agent_id)
        )
        count = cursor.fetchone()[0]
        conn.close()

        print(f"\n📊 Current state:")
        print(f"   - Existing messages: {count}")
        print(f"   - Next message_id: {count}")

        # Add a new message
        new_message = "What's 100 + 200?"
        print(f"\n💬 Adding new user message: '{new_message}'")
        self.step4_save_message(session_id, agent_id, count, "user", new_message)

        # Simulate agent response
        response = "100 + 200 equals 300"
        print(f"\n🤖 Adding agent response: '{response}'")
        self.step4_save_message(session_id, agent_id, count + 1, "assistant", response)

        print("\n💡 What we did: Added new messages to existing conversation")
        print("   The conversation continues where it left off!")


def main():
    """Run the interactive tutorial."""
    print("\n" + "=" * 60)
    print("🎓 Session Management Tutorial")
    print("=" * 60)

    # Clean start
    db_path = "./learning.db"
    if Path(db_path).exists():
        Path(db_path).unlink()
        print(f"\n🧹 Cleaned up old database")

    # Initialize
    manager = LearningSessionManager(db_path)

    # Step 1: Create tables
    manager.step1_create_tables()
    input("\n▶️  Press Enter to continue to Step 2...")

    # Step 2: Create session
    session_id = "my-first-session"
    manager.step2_create_session(session_id)
    input("\n▶️  Press Enter to continue to Step 3...")

    # Step 3: Create agent
    agent_id = "agent-001"
    system_prompt = "You are a helpful math assistant."
    manager.step3_create_agent(session_id, agent_id, system_prompt)
    input("\n▶️  Press Enter to continue to Step 4...")

    # Step 4: Save first conversation
    manager.step4_save_message(session_id, agent_id, 0, "user", "What's 2 + 2?")
    input("\n▶️  Press Enter to see the agent response...")
    manager.step4_save_message(session_id, agent_id, 1, "assistant", "2 + 2 equals 4")
    input("\n▶️  Press Enter to continue to Step 5...")

    # Step 5: Load messages
    manager.step5_load_messages(session_id, agent_id)
    input("\n▶️  Press Enter to continue to Step 6...")

    # Step 6: Continue conversation
    manager.step6_continue_conversation(session_id, agent_id)
    input("\n▶️  Press Enter to see final conversation...")

    # Show final conversation
    manager.step5_load_messages(session_id, agent_id)

    # Final summary
    print("\n" + "=" * 60)
    print("🎉 Tutorial Complete!")
    print("=" * 60)
    print("\n📚 What you learned:")
    print("   1. How to create database tables for sessions")
    print("   2. How to store session information")
    print("   3. How to save agent configuration")
    print("   4. How to store messages in order")
    print("   5. How to load conversation history")
    print("   6. How to continue existing conversations")
    print("\n💡 This is exactly how FileSessionManager works,")
    print("   but it uses files instead of a database!")
    print("\n🔍 Explore the database:")
    print(f"   sqlite3 {db_path}")
    print("   sqlite> SELECT * FROM sessions;")
    print("   sqlite> SELECT * FROM agents;")
    print("   sqlite> SELECT * FROM messages;")
    print("\n")


if __name__ == "__main__":
    main()
