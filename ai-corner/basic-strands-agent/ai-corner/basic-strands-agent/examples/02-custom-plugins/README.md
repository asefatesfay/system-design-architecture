# 02-custom-plugins: Build Your Own

Learn to create custom plugins from scratch.

## Files

### custom-plugin-basics.py ⭐ **START HERE**
- **What:** Create your first custom plugin
- **Learns:** Plugin structure, `name` property, `init_agent()`
- **Time:** 15 minutes
- **Run:** `python custom-plugin-basics.py`

### custom-plugin-counter.py
- **What:** Track conversation statistics
- **Learns:** Event data, state management, reporting
- **Time:** 15 minutes
- **Run:** `python custom-plugin-counter.py`

### plugin-cost-tracker.py 🏭 **Production**
- **What:** Track token usage and estimate costs
- **Learns:** Real-world patterns, configuration, alerts
- **Time:** 20 minutes
- **Run:** `python plugin-cost-tracker.py`

### plugin-rate-limiter.py 🏭 **Production**
- **What:** Limit requests per user/session
- **Learns:** Rate limiting strategies, burst protection
- **Time:** 20 minutes
- **Run:** `python plugin-rate-limiter.py`

## Plugin Template

```python
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent

class MyPlugin(Plugin):
    def __init__(self, name="my-plugin"):
        self._name = name
        super().__init__()

    @property
    def name(self) -> str:
        return self._name

    def init_agent(self, agent) -> None:
        agent.add_hook(self._hook, BeforeModelCallEvent)

    def _hook(self, event):
        pass  # Your logic
```

## Concepts Learned

- ✅ Custom plugin structure (3 required parts)
- ✅ Hook registration
- ✅ Event handling
- ✅ State management
- ✅ Configuration patterns
- ✅ Production patterns

## Next Steps

Move to [../03-skills/](../03-skills/) to learn about skills.
