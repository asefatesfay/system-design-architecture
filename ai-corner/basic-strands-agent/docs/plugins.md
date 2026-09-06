# Simple Guide to Strands Plugins

## What are Plugins?

Plugins let you extend your agent's behavior without changing the core logic. Think of them as "add-ons" that hook into specific moments in the agent's lifecycle.

## The 3 Examples

### Example 1: Time Context Injector ([plugin-basics.py](plugin-basics.py))

**What it does:** Injects the current time into every conversation

**Real-world use case:**
- Support agents need to know current time for "are you open?" questions
- Scheduling assistants need accurate time
- Time-sensitive recommendations

**Key concept:** `ContextInjector` - adds information to the agent's context

```python
from strands.vended_plugins.context_injector import ContextInjector

def get_current_time():
    return f"Current time: {datetime.datetime.now()}"

agent = Agent(
    plugins=[ContextInjector(get_current_time)]
)
```

**What happens:**
1. User asks: "Are your support lines open?"
2. Plugin injects: "Current time: 2026-09-05T14:30:00"
3. Agent sees the time and can answer accurately

---

### Example 2: Request Logger ([plugin-example-logger.py](plugin-example-logger.py))

**What it does:** Logs every user question to a file

**Real-world use cases:**
- **Analytics** - What are users asking about most?
- **Compliance** - Keep records of all interactions
- **Debugging** - See what questions caused errors
- **Training** - Collect real user questions to improve the agent

**Key concept:** `Hooks` - run code at specific lifecycle events

```python
from strands.hooks import BeforeModelCallEvent

def log_request(event):
    # Extract user message from event
    # Write to log file

agent.add_hook(log_request, BeforeModelCallEvent)
```

**What happens:**
1. User sends message
2. `BeforeModelCallEvent` fires
3. Your hook logs the message
4. Agent processes normally

**Output:** Creates `requests.log` with all user questions

---

### Example 3: User Context Injector ([plugin-example-user-context.py](plugin-example-user-context.py))

**What it does:** Injects user profile information (name, role, tier) into context

**Real-world use cases:**
- **Personalization** - Address user by name
- **Access control** - Different features for free vs premium users
- **Relevance** - Tailor responses to user's role (developer vs manager)
- **Multi-tenant** - Different context per organization

**Key concept:** `ContextInjector` with dynamic data

```python
class UserContextManager:
    def get_user_context(self, context=None):
        user = self.current_user
        return f"User: {user.name}, Tier: {user.tier}"

user_manager = UserContextManager()
agent = Agent(
    plugins=[ContextInjector(user_manager.get_user_context)]
)

# Set current user
user_manager.set_user("user_123")
agent("Help me")  # Agent knows who "me" is!
```

**What happens:**
1. You set current user: `user_manager.set_user("user_123")`
2. User asks question
3. Plugin injects user profile: name, role, tier, etc.
4. Agent personalizes response based on context

---

## Plugin Types Comparison

| Plugin | Type | When it runs | Use case |
|--------|------|-------------|----------|
| Time Injector | ContextInjector | Before every user turn | Add dynamic info |
| Request Logger | Hook | Before model call | Track/log activity |
| User Context | ContextInjector | Before every user turn | Personalization |

---

## Key Concepts

### 1. ContextInjector Plugin
- **Purpose:** Add information to agent's context
- **Ephemeral:** Not saved to conversation history
- **Function:** Takes a function that returns a string
- **Timing:** Runs before each user turn (default)

```python
ContextInjector(function_that_returns_string)
```

### 2. Hooks
- **Purpose:** Run custom code at lifecycle events
- **Events:**
  - `BeforeModelCallEvent` - Before asking the model
  - `AfterModelCallEvent` - After model responds
  - `BeforeToolCallEvent` - Before calling a tool
  - `AfterToolCallEvent` - After tool completes
- **Usage:**
  ```python
  agent.add_hook(your_function, EventType)
  ```

### 3. Plugin vs Hook
- **Plugin:** Packaged, reusable extension (like `ContextInjector`)
- **Hook:** Direct event handler you register yourself
- Plugins often use hooks internally!

---

## Try It Yourself

### Run the examples:
```bash
# Example 1: Time injection
python plugin-basics.py

# Example 2: Request logging
python plugin-example-logger.py
cat requests.log  # See logged requests

# Example 3: User context
python plugin-example-user-context.py
```

### Modify them:
1. **Example 1:** Change the time format, add timezone
2. **Example 2:** Log to database instead of file, add response times
3. **Example 3:** Add more user fields (company, location), load from real DB

---

## Common Plugin Patterns

### Pattern 1: Static Context
Add fixed information:
```python
def get_policies():
    return "Company policy: Be polite and helpful"

agent = Agent(plugins=[ContextInjector(get_policies)])
```

### Pattern 2: Dynamic Context
Add information that changes:
```python
def get_system_status():
    return f"System load: {get_current_load()}%"
```

### Pattern 3: Session-based Context
Add per-user information:
```python
def get_user_info():
    user = session.current_user
    return f"User preferences: {user.preferences}"
```

---

## When to Use Plugins

✅ **Use plugins when:**
- You need to inject context that changes
- You want to log/monitor agent activity
- You need user-specific personalization
- You want reusable functionality across agents

❌ **Don't need plugins when:**
- Information is static → Use system prompt instead
- You want to give agent data to work with → Use tools instead
- You're modifying agent logic → Subclass Agent instead

---

## Next Steps

1. ✅ Run all 3 examples
2. ✅ Modify them to understand how they work
3. Create your own plugin:
   - Rate limiter (limit requests per user)
   - Cost tracker (track token usage)
   - Safety filter (check for inappropriate content)
   - A/B testing (randomly use different system prompts)

---

## Quick Reference

```python
# Context Injector Plugin
from strands.vended_plugins.context_injector import ContextInjector

agent = Agent(
    plugins=[
        ContextInjector(your_function)
    ]
)

# Hook Registration
from strands.hooks import BeforeModelCallEvent

agent.add_hook(your_function, BeforeModelCallEvent)
```

That's it! Plugins are simpler than they seem - they're just functions that run at the right time. 🎉
