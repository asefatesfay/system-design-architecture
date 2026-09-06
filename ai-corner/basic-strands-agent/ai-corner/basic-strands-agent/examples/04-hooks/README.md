# 04-hooks: Direct Event Handling

Hooks are the underlying mechanism for plugins. Sometimes you want direct hook registration without creating a full plugin.

## Files

### hook-example-logger.py ⭐ **ONLY FILE**
- **What:** Use hooks directly (not as a plugin)
- **Learns:** Direct hook registration, when to skip plugins
- **Time:** 10 minutes
- **Run:** `python hook-example-logger.py`

## Hook vs Plugin

### Use Hooks Directly When:
- ✅ One-off functionality
- ✅ Quick prototyping
- ✅ Don't need reusability
- ✅ Simple logging/debugging

### Use Plugins When:
- ✅ Reusable across agents
- ✅ Need configuration
- ✅ Want to share with others
- ✅ Production code

## Example

**Hook (Direct):**
```python
def my_hook(event):
    print("Before model call")

agent = Agent()
agent.add_hook(my_hook, BeforeModelCallEvent)
```

**Plugin (Packaged):**
```python
class MyPlugin(Plugin):
    def init_agent(self, agent):
        agent.add_hook(self._hook, BeforeModelCallEvent)

agent = Agent(plugins=[MyPlugin()])
```

## Available Events

- `BeforeModelCallEvent` - Before asking the model
- `AfterModelCallEvent` - After model responds
- `BeforeToolCallEvent` - Before calling a tool
- `AfterToolCallEvent` - After tool completes

## Concepts Learned

- ✅ Direct hook registration
- ✅ Hooks vs plugins trade-offs
- ✅ When to use which approach

## Next Steps

Explore [../05-session-management/](../05-session-management/) for persistence.
