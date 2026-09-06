# Simple Custom Plugin Guide

Learn how to create your own plugins from scratch!

---

## What is a Custom Plugin?

A plugin is a **reusable piece of code** that extends your agent's behavior. Instead of writing the same hook registration code over and over, you package it into a plugin.

**Think of it like:**
- Tool = A screwdriver (does one thing)
- Skill = Instructions manual (knowledge)
- Plugin = A toolbelt (adds capabilities/behavior)

---

## Minimal Plugin Structure

Every custom plugin needs **just 2 things**:

### 1. Inherit from `Plugin`
```python
from strands.plugin import Plugin

class MyPlugin(Plugin):
    pass
```

### 2. Implement `init_agent()`
```python
def init_agent(self, agent: Agent) -> None:
    """Called when plugin is attached to agent."""
    # Register your hooks here
    agent.add_hook(self._my_hook, SomeEvent)
```

**That's it!** The rest is up to you.

---

## Simple Example - Step by Step

Let's build a plugin that counts requests:

### Step 1: Import what you need
```python
from strands import Agent
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent
```

### Step 2: Create the plugin class
```python
class RequestCounterPlugin(Plugin):
    pass
```

### Step 3: Add initialization
```python
class RequestCounterPlugin(Plugin):
    def __init__(self):
        self.count = 0
        print("Plugin initialized!")
```

### Step 4: Implement init_agent()
```python
class RequestCounterPlugin(Plugin):
    def __init__(self):
        self.count = 0

    def init_agent(self, agent: Agent) -> None:
        """Register hooks when attached to agent."""
        agent.add_hook(self._count_request, BeforeModelCallEvent)
```

### Step 5: Add your hook method
```python
class RequestCounterPlugin(Plugin):
    def __init__(self):
        self.count = 0

    def init_agent(self, agent: Agent) -> None:
        agent.add_hook(self._count_request, BeforeModelCallEvent)

    def _count_request(self, event: BeforeModelCallEvent):
        """Count each request."""
        self.count += 1
        print(f"Request #{self.count}")
```

### Step 6: Use it!
```python
plugin = RequestCounterPlugin()
agent = Agent(plugins=[plugin])

agent("Question 1")  # Request #1
agent("Question 2")  # Request #2

print(f"Total: {plugin.count}")  # Total: 2
```

**Done!** That's a complete custom plugin. 🎉

---

## Plugin Anatomy

```python
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent, AfterModelCallEvent

class MyCustomPlugin(Plugin):
    """
    1. CLASS: Inherit from Plugin
    """

    def __init__(self, config_value):
        """
        2. CONSTRUCTOR: Accept configuration
        Initialize any state you need
        """
        self.config = config_value
        self.state = {}

    def init_agent(self, agent: Agent) -> None:
        """
        3. INIT_AGENT: Called when plugin is attached to agent
        Register your hooks here
        """
        agent.add_hook(self._before, BeforeModelCallEvent)
        agent.add_hook(self._after, AfterModelCallEvent)

    def _before(self, event: BeforeModelCallEvent):
        """
        4. HOOK METHODS: Your custom logic
        Called at specific lifecycle events
        """
        # Do something before model is called
        pass

    def _after(self, event: AfterModelCallEvent):
        """
        4. HOOK METHODS: Your custom logic
        Called at specific lifecycle events
        """
        # Do something after model responds
        pass

    def get_stats(self):
        """
        5. UTILITY METHODS: Helper functions (optional)
        Not required, just helpful
        """
        return self.state
```

---

## Common Hook Events

Use these events to run your code at different times:

| Event | When it fires | Use for |
|-------|--------------|---------|
| `BeforeModelCallEvent` | Before asking the model | Validation, logging, rate limiting |
| `AfterModelCallEvent` | After model responds | Tracking, post-processing, stats |
| `BeforeToolCallEvent` | Before calling a tool | Tool validation, logging |
| `AfterToolCallEvent` | After tool completes | Tool result tracking |

```python
from strands.hooks import (
    BeforeModelCallEvent,
    AfterModelCallEvent,
    BeforeToolCallEvent,
    AfterToolCallEvent
)

class MyPlugin(Plugin):
    def init_agent(self, agent: Agent) -> None:
        # Pick the events you need
        agent.add_hook(self._before_model, BeforeModelCallEvent)
        agent.add_hook(self._after_model, AfterModelCallEvent)
        agent.add_hook(self._before_tool, BeforeToolCallEvent)
        agent.add_hook(self._after_tool, AfterToolCallEvent)
```

---

## Examples

### Example 1: Request Logger
**File:** [custom-plugin-basics.py](custom-plugin-basics.py)

Simple plugin that logs each request:
```python
class SimpleGreetingPlugin(Plugin):
    def __init__(self):
        self.request_count = 0

    def init_agent(self, agent: Agent) -> None:
        agent.add_hook(self._log, BeforeModelCallEvent)

    def _log(self, event: BeforeModelCallEvent):
        self.request_count += 1
        print(f"Request #{self.request_count}")
```

### Example 2: Conversation Counter
**File:** [custom-plugin-counter.py](custom-plugin-counter.py)

Tracks questions, responses, and word counts:
```python
class ConversationCounterPlugin(Plugin):
    def __init__(self):
        self.questions = 0
        self.responses = 0
        self.total_words = 0

    def init_agent(self, agent: Agent) -> None:
        agent.add_hook(self._count_question, BeforeModelCallEvent)
        agent.add_hook(self._count_response, AfterModelCallEvent)

    # ... hook methods ...
```

---

## Accessing Event Data

Hook events contain useful information:

### BeforeModelCallEvent
```python
def _my_hook(self, event: BeforeModelCallEvent):
    # Access the messages
    messages = event.messages
    last_msg = messages[-1]

    # Get user's text
    if last_msg.role == "user":
        for content in last_msg.content:
            if hasattr(content, 'text'):
                text = content.text
                print(f"User said: {text}")
```

### AfterModelCallEvent
```python
def _my_hook(self, event: AfterModelCallEvent):
    # Access the response
    response = event.response

    # Get response text
    if response and response.content:
        for content in response.content:
            if hasattr(content, 'text'):
                text = content.text
                print(f"Agent said: {text}")

    # Access usage stats
    usage = event.usage
    if usage:
        print(f"Tokens used: {usage.input_tokens + usage.output_tokens}")
```

---

## Plugin vs Hook Comparison

### Using a Hook Directly
```python
# Simple, but not reusable
def log_request(event):
    print("Request received")

agent = Agent()
agent.add_hook(log_request, BeforeModelCallEvent)
```

### Using a Plugin
```python
# Reusable, configurable, shareable
class LoggerPlugin(Plugin):
    def __init__(self, prefix="Request"):
        self.prefix = prefix

    def init_agent(self, agent: Agent) -> None:
        agent.add_hook(self._log, BeforeModelCallEvent)

    def _log(self, event):
        print(f"{self.prefix} received")

agent = Agent(plugins=[LoggerPlugin(prefix="API Call")])
```

**Plugin benefits:**
- ✅ Reusable across agents
- ✅ Configurable (constructor args)
- ✅ Stateful (can track things)
- ✅ Testable
- ✅ Shareable with others

---

## Adding Configuration

Make your plugin flexible with configuration:

```python
class FlexiblePlugin(Plugin):
    def __init__(
        self,
        feature_enabled=True,
        log_level="info",
        custom_message="Hello"
    ):
        """Accept configuration in constructor."""
        self.feature_enabled = feature_enabled
        self.log_level = log_level
        self.custom_message = custom_message

    def init_agent(self, agent: Agent) -> None:
        if self.feature_enabled:
            agent.add_hook(self._process, BeforeModelCallEvent)

    def _process(self, event):
        if self.log_level == "debug":
            print(f"[DEBUG] {self.custom_message}")

# Use with different configs
plugin1 = FlexiblePlugin(log_level="debug")
plugin2 = FlexiblePlugin(feature_enabled=False)
plugin3 = FlexiblePlugin(custom_message="Custom!")
```

---

## Best Practices

### 1. Name Convention
```python
# ✅ Good: Clear, descriptive
class RequestLoggerPlugin(Plugin): ...
class CostTrackerPlugin(Plugin): ...

# ❌ Bad: Vague, generic
class MyPlugin(Plugin): ...
class HelperPlugin(Plugin): ...
```

### 2. Private Methods
```python
class MyPlugin(Plugin):
    def init_agent(self, agent: Agent) -> None:
        # Use _ prefix for internal methods
        agent.add_hook(self._internal_hook, BeforeModelCallEvent)

    def _internal_hook(self, event):  # ← Private
        pass

    def get_stats(self):  # ← Public
        return self.stats
```

### 3. Initialize State
```python
class MyPlugin(Plugin):
    def __init__(self):
        # Initialize all state in __init__
        self.count = 0
        self.data = []
        self.config = {}
```

### 4. Provide Utility Methods
```python
class MyPlugin(Plugin):
    # ... hooks ...

    def get_stats(self):
        """Public method to get stats."""
        return {"count": self.count}

    def reset(self):
        """Public method to reset state."""
        self.count = 0
```

---

## Quick Template

Copy this to start a new plugin:

```python
from strands import Agent
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent

class MyCustomPlugin(Plugin):
    """
    Brief description of what your plugin does.
    """

    def __init__(self, config_option="default"):
        """Initialize with configuration."""
        self.config_option = config_option
        self.state = {}
        print(f"MyCustomPlugin initialized")

    def init_agent(self, agent: Agent) -> None:
        """Register hooks when attached to agent."""
        print(f"MyCustomPlugin connected to agent")
        agent.add_hook(self._my_hook, BeforeModelCallEvent)

    def _my_hook(self, event: BeforeModelCallEvent):
        """Your custom logic here."""
        # Do something with the event
        pass

    def get_stats(self):
        """Get plugin statistics."""
        return self.state

# Usage
plugin = MyCustomPlugin(config_option="custom")
agent = Agent(plugins=[plugin])
```

---

## Examples in This Project

| File | Plugin | Purpose |
|------|--------|---------|
| [custom-plugin-basics.py](custom-plugin-basics.py) | SimpleGreetingPlugin | Minimal example |
| [custom-plugin-counter.py](custom-plugin-counter.py) | ConversationCounterPlugin | Track stats |
| [plugin-cost-tracker.py](plugin-cost-tracker.py) | CostTrackerPlugin | Production-ready |
| [plugin-rate-limiter.py](plugin-rate-limiter.py) | RateLimiterPlugin | Production-ready |

---

## Next Steps

1. ✅ Run [custom-plugin-basics.py](custom-plugin-basics.py)
2. ✅ Run [custom-plugin-counter.py](custom-plugin-counter.py)
3. ✅ Modify them to understand how they work
4. ✅ Create your own plugin using the template
5. ✅ Check out production examples: [plugin-cost-tracker.py](plugin-cost-tracker.py), [plugin-rate-limiter.py](plugin-rate-limiter.py)

---

## Summary

**Creating a custom plugin:**

1. Inherit from `Plugin`
2. Implement `__init__()` for configuration
3. Implement `init_agent()` to register hooks
4. Add hook methods for your logic
5. Add utility methods for state access

**Benefits:**
- Reusable across agents
- Configurable
- Testable
- Shareable

Start with [custom-plugin-basics.py](custom-plugin-basics.py) - it's the simplest! 🚀
