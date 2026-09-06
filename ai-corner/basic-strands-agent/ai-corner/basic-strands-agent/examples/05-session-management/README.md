# 05-session-management: Persist Conversations

Learn how to save and restore agent conversations.

## Files

### learn_session_management.py ⭐ **START HERE**
- **What:** Interactive step-by-step tutorial
- **Learns:** How session management works internally
- **Time:** 20 minutes
- **Run:** `python learn_session_management.py`
- **Note:** Press Enter to advance through steps

### session-manager-file.py
- **What:** Use built-in FileSessionManager
- **Learns:** File-based sessions, simple persistence
- **Time:** 10 minutes
- **Run:** `python session-manager-file.py`

### session-manager-sqlite.py
- **What:** Use custom SQLiteSessionManager
- **Learns:** Database sessions, better persistence
- **Time:** 15 minutes
- **Run:** `python session-manager-sqlite.py`
- **Uses:** `../../utils/sqlite_session_manager.py`

### inspect_sessions.py
- **What:** Inspect SQLite session database
- **Learns:** How data is stored
- **Time:** 5 minutes
- **Run:** `python inspect_sessions.py`

## Quick Comparison

| Feature | Files | SQLite |
|---------|-------|--------|
| Setup | ✅ Simple | ⚠️ More code |
| Query | ❌ Hard | ✅ Easy (SQL) |
| Concurrent | ❌ Issues | ✅ Safe |
| Inspect | ❌ Many files | ✅ One DB |

## File-Based Example

```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager

session = FileSessionManager(
    session_id="my-session",
    storage_dir="./sessions"
)

agent = Agent(
    system_prompt="You are helpful.",
    session_manager=session
)

agent("Remember: My name is Alex")
# Session automatically saved!
```

## SQLite Example

```python
from strands import Agent
from utils.sqlite_session_manager import SQLiteSessionManager

session = SQLiteSessionManager(
    session_id="my-session",
    db_path="./sessions.db"
)

agent = Agent(
    system_prompt="You are helpful.",
    session_manager=session
)

agent("Remember: My name is Alex")
# Saved to database!
```

## Session Structure

Both managers store:
1. **Session** - Conversation metadata
2. **Agent** - System prompt, state
3. **Messages** - All messages in order

## Use Cases

### File Sessions
- ✅ Simple applications
- ✅ Single user
- ✅ Debugging

### SQLite Sessions
- ✅ Multi-user apps
- ✅ Analytics/reporting
- ✅ Need to query conversations
- ✅ Production apps

## Concepts Learned

- ✅ What sessions store
- ✅ File vs database storage
- ✅ SessionManager interface
- ✅ Persistence patterns
- ✅ Querying sessions

## Utilities

See [../../utils/sqlite_session_manager.py](../../utils/sqlite_session_manager.py) for production-ready SQLite implementation.

## Docs

See [../../docs/session-management.md](../../docs/session-management.md) for complete guide.

---

**Congratulations!** You've completed all example categories. 🎉

Next: Build your own agent using what you learned!
