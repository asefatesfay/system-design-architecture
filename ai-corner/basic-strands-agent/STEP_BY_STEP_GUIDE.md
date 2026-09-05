# Step-by-Step Guide: Session Management with SQLite

## What is Session Management?

When you talk to an agent, the conversation needs to be saved somewhere so:
1. The agent remembers what you said
2. You can continue the conversation later
3. Even after restarting your program, the history is preserved

## How FileSessionManager Works

Let's look at what FileSessionManager does:

```
~/.strands/sessions/
└── session_my-session/
    ├── session.json              # Session info
    └── agents/
        └── agent_abc123/
            ├── agent.json        # Agent config (system prompt, state)
            └── messages/
                ├── message_0.json  # First message
                ├── message_1.json  # Second message
                └── message_2.json  # Third message
```

**It stores 3 types of data:**
1. **Session** - Basic info about the conversation
2. **Agent** - The agent's configuration (system prompt, state)
3. **Messages** - All the messages in the conversation

---

## Step 1: Understanding Session Repository Interface

Strands requires these methods to manage sessions:

```python
# Session operations
create_session(session)      # Create new session
read_session(session_id)     # Load existing session
delete_session(session_id)   # Delete session

# Agent operations
create_agent(session_id, agent)   # Store agent config
read_agent(session_id, agent_id)  # Load agent config
update_agent(session_id, agent)   # Update agent config

# Message operations
create_message(session_id, agent_id, message)   # Save a message
read_message(session_id, agent_id, msg_id)      # Load a message
list_messages(session_id, agent_id)             # Get all messages
```

---

## Step 2: How to Store This in SQLite

Instead of files, we use **3 tables**:

### Table 1: sessions
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP
)
```
**Purpose:** Track which conversations exist

### Table 2: agents
```sql
CREATE TABLE agents (
    session_id TEXT,
    agent_id TEXT,
    system_prompt TEXT,      -- "You are a helpful assistant"
    state TEXT,              -- Any agent state (JSON)
    PRIMARY KEY (session_id, agent_id)
)
```
**Purpose:** Store agent configuration for each session

### Table 3: messages
```sql
CREATE TABLE messages (
    session_id TEXT,
    agent_id TEXT,
    message_id INTEGER,      -- 0, 1, 2, 3...
    role TEXT,              -- "user" or "assistant"
    content TEXT,           -- Message content (JSON)
    PRIMARY KEY (session_id, agent_id, message_id)
)
```
**Purpose:** Store all messages in order

---

## Step 3: How Messages Flow

When you chat with the agent:

```
You: "What's 2 + 2?"
```

**What happens:**

1. **Your message gets saved:**
   ```sql
   INSERT INTO messages VALUES (
       'my-session',
       'agent-123',
       0,              -- message_id
       'user',         -- role
       '[{"type": "text", "text": "What\'s 2 + 2?"}]'
   )
   ```

2. **Agent processes and responds:** "2 + 2 equals 4"

3. **Agent's response gets saved:**
   ```sql
   INSERT INTO messages VALUES (
       'my-session',
       'agent-123',
       1,              -- next message_id
       'assistant',    -- role
       '[{"type": "text", "text": "2 + 2 equals 4"}]'
   )
   ```

---

## Step 4: Why SQLite is Better Than Files

| Operation | Files | SQLite |
|-----------|-------|--------|
| Save message | Write 1 file | INSERT 1 row |
| Load all messages | Read N files, sort by name | SELECT * ORDER BY message_id |
| Find session by date | Loop through directories | SELECT WHERE created_at > '...' |
| Delete session | Delete directory + all files | DELETE FROM sessions (cascade) |
| Concurrent access | ⚠️ Conflicts | ✅ Handles locks |

---

## Step 5: Building It Step by Step

### Level 1: Just Store Sessions
```python
def create_session(session_id):
    conn = sqlite3.connect("sessions.db")
    conn.execute(
        "INSERT INTO sessions (session_id) VALUES (?)",
        (session_id,)
    )
    conn.commit()
    conn.close()
```

### Level 2: Store Agent Configuration
```python
def create_agent(session_id, agent_id, system_prompt):
    conn = sqlite3.connect("sessions.db")
    conn.execute(
        "INSERT INTO agents (session_id, agent_id, system_prompt) VALUES (?, ?, ?)",
        (session_id, agent_id, system_prompt)
    )
    conn.commit()
    conn.close()
```

### Level 3: Store Messages
```python
def create_message(session_id, agent_id, message_id, role, content):
    conn = sqlite3.connect("sessions.db")
    conn.execute(
        "INSERT INTO messages (session_id, agent_id, message_id, role, content) VALUES (?, ?, ?, ?, ?)",
        (session_id, agent_id, message_id, role, json.dumps(content))
    )
    conn.commit()
    conn.close()
```

### Level 4: Load Messages (for agent to remember)
```python
def list_messages(session_id, agent_id):
    conn = sqlite3.connect("sessions.db")
    cursor = conn.execute(
        "SELECT message_id, role, content FROM messages WHERE session_id = ? AND agent_id = ? ORDER BY message_id",
        (session_id, agent_id)
    )
    messages = []
    for msg_id, role, content in cursor.fetchall():
        messages.append({
            'message_id': msg_id,
            'role': role,
            'content': json.loads(content)
        })
    conn.close()
    return messages
```

---

## Step 6: Connecting to Strands

Strands provides two base classes:

1. **SessionRepository** - Interface that defines what methods you need
2. **RepositorySessionManager** - Handles all the agent logic, just needs a repository

You implement `SessionRepository` methods → `RepositorySessionManager` does the rest!

```python
class SQLiteSessionManager(RepositorySessionManager, SessionRepository):
    def __init__(self, session_id, db_path):
        self.db_path = db_path
        self._create_tables()
        # Pass self as the repository
        super().__init__(session_id=session_id, session_repository=self)

    # Implement create_session, read_session, create_agent, etc.
```

---

## Summary

**FileSessionManager:**
- Creates files and directories
- Each message = 1 file
- Uses filesystem operations

**SQLiteSessionManager:**
- Creates tables in database
- Each message = 1 row
- Uses SQL operations

**Same concept, different storage!**

The key insight: Both follow the same **SessionRepository** interface - they just store data differently.

---

## Next Steps

Would you like me to create:
1. ✅ Simple examples for each level (1-4 above)?
2. ✅ A side-by-side comparison script (File vs SQLite)?
3. ✅ Interactive tutorial with exercises?

Let me know which would help you learn best!
