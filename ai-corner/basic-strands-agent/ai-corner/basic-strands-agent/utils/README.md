# Utilities

Reusable components you can copy into your own projects.

## Files

### sqlite_session_manager.py
**Production-ready SQLite session manager**

- ✅ Fully implemented SessionRepository
- ✅ CRUD operations for sessions/agents/messages
- ✅ Transaction-safe
- ✅ Indexed for performance

**Usage:**
```python
from utils.sqlite_session_manager import SQLiteSessionManager
from strands import Agent

session = SQLiteSessionManager(
    session_id="user_123",
    db_path="./sessions.db"
)

agent = Agent(
    system_prompt="You are helpful.",
    session_manager=session
)
```

**See Example:**
[../examples/05-session-management/session-manager-sqlite.py](../examples/05-session-management/session-manager-sqlite.py)

---

## Adding More Utilities

Got a reusable component? Add it here!

Examples:
- Custom memory stores
- Specialized plugins
- Tool implementations
- Helper functions
