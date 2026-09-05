# Hooks vs Plugins - What's the Difference?

## TL;DR

- **Hook** = Direct event handler you register manually
- **Plugin** = Packaged extension that registers hooks for you

Both can do the same things, but plugins are more reusable!

---

## Hook Example (Direct Registration)

```python
from strands import Agent
from strands.hooks import BeforeModelCallEvent

def my_logger(event):
    print(f"User said: {event.messages[-1]}")

agent = Agent()
agent.add_hook(my_logger, BeforeModelCallEvent)  # ← Register directly
```

**Characteristics:**
- ✅ Simple and direct
- ✅ Quick for one-off use cases
- ❌ Not packaged/reusable
- ❌ You manage the registration

---

## Plugin Example (Packaged)

```python
from strands import Agent
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent

class MyLoggerPlugin(Plugin):
    def init_agent(self, agent: Agent):
        agent.add_hook(self._log, BeforeModelCallEvent)

    def _log(self, event):
        print(f"User said: {event.messages[-1]}")

agent = Agent(plugins=[MyLoggerPlugin()])  # ← Pass in plugins parameter
```

**Characteristics:**
- ✅ Packaged and reusable
- ✅ Can have configuration (constructor args)
- ✅ Easy to share and distribute
- ✅ Cleaner agent initialization
- ⚠️  More code to write

---

## Side-by-Side Comparison

### Using Hooks Directly

```python
# Define your hook function
def log_request(event):
    print(f"Request: {event}")

# Create agent
agent = Agent()

# Register hook manually
agent.add_hook(log_request, BeforeModelCallEvent)
```

**When to use:**
- Quick prototyping
- One-off functionality
- You don't need to reuse it

---

### Using a Plugin

```python
# Define your plugin class
class RequestLoggerPlugin(Plugin):
    def __init__(self, log_file="requests.log"):
        self.log_file = log_file

    def init_agent(self, agent: Agent):
        # Plugin registers its own hooks
        agent.add_hook(self._log, BeforeModelCallEvent)

    def _log(self, event):
        # Your logging logic here
        pass

# Create agent with plugin
agent = Agent(
    plugins=[RequestLoggerPlugin("my_logs.log")]
)
```

**When to use:**
- You want to reuse it across multiple agents
- You need configuration options
- You're building a library
- You want clean, maintainable code

---

## Real Examples

### Example: ContextInjector (Built-in Plugin)

This is a **plugin** that comes with Strands:

```python
from strands.vended_plugins.context_injector import ContextInjector

agent = Agent(
    plugins=[
        ContextInjector(lambda: f"Time: {datetime.now()}")
    ]
)
```

**Why it's a plugin:** It's packaged, reusable, and configurable.

**Under the hood:** It registers hooks to inject context before model calls.

---

### Example: Your Custom Hook

This is just a **hook**:

```python
def add_timestamp(event):
    # Your custom logic
    pass

agent = Agent()
agent.add_hook(add_timestamp, BeforeModelCallEvent)
```

**Why it's just a hook:** You register it directly, not packaged.

---

## Converting Hook → Plugin

### Step 1: Hook version (simple)

```python
def my_function(event):
    print("Before model call!")

agent = Agent()
agent.add_hook(my_function, BeforeModelCallEvent)
```

### Step 2: Plugin version (packaged)

```python
class MyPlugin(Plugin):
    def init_agent(self, agent: Agent):
        agent.add_hook(self._my_function, BeforeModelCallEvent)

    def _my_function(self, event):
        print("Before model call!")

agent = Agent(plugins=[MyPlugin()])
```

**What changed:**
1. Wrapped in a `Plugin` class
2. Implemented `init_agent()` method
3. Moved hook registration inside `init_agent()`
4. Passed plugin to `Agent(plugins=[...])`

---

## Summary Table

| Feature | Hook | Plugin |
|---------|------|--------|
| **Registration** | `agent.add_hook()` | `Agent(plugins=[...])` |
| **Reusability** | Low | High |
| **Configuration** | Hard | Easy (constructor args) |
| **Code organization** | Scattered | Packaged |
| **Good for** | Quick/one-off | Production/reusable |
| **Complexity** | Simple | More code |

---

## When to Use What?

### Use Hooks Directly:
- ✅ Quick prototyping
- ✅ One-time use in a single agent
- ✅ Simple logging/debugging
- ✅ Learning/experimenting

### Use Plugins:
- ✅ Reusable functionality
- ✅ Multiple agents need the same behavior
- ✅ Need configuration options
- ✅ Building a library/framework
- ✅ Production code

---

## Both Can Do the Same Thing!

This is important: **Hooks and plugins can achieve the same results.**

A plugin is just a **convenient wrapper** around hooks that makes them more reusable.

**Hook version:**
```python
agent = Agent()
agent.add_hook(my_function, BeforeModelCallEvent)
```

**Plugin version (does the same thing):**
```python
agent = Agent(plugins=[MyPlugin()])
# MyPlugin.init_agent() calls agent.add_hook() internally
```

---

## The Files in This Project

### Hook Examples:
- [hook-example-logger.py](hook-example-logger.py) - Uses `agent.add_hook()` directly

### Plugin Examples:
- [plugin-basics.py](plugin-basics.py) - Uses `ContextInjector` plugin
- [plugin-example-logger-proper.py](plugin-example-logger-proper.py) - Custom plugin with `init_agent()`
- [plugin-example-user-context.py](plugin-example-user-context.py) - Uses `ContextInjector` plugin

---

## Quick Reference

```python
# HOOK: Direct registration
from strands.hooks import BeforeModelCallEvent

def my_hook(event):
    pass

agent = Agent()
agent.add_hook(my_hook, BeforeModelCallEvent)
```

```python
# PLUGIN: Packaged extension
from strands.plugin import Plugin

class MyPlugin(Plugin):
    def init_agent(self, agent: Agent):
        agent.add_hook(self._hook, BeforeModelCallEvent)

    def _hook(self, event):
        pass

agent = Agent(plugins=[MyPlugin()])
```

---

## Key Takeaway

**Plugins are just fancy wrappers around hooks!**

- Start with hooks when learning
- Graduate to plugins when you need reusability
- Both are valid approaches depending on your needs

🎉 Now you understand the difference!
