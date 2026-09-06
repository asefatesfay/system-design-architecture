# Strands Agent Examples & Guides

A comprehensive, well-organized collection of examples and guides for learning Strands Agents SDK from scratch. Perfect for beginners and experienced developers alike.

---

## 🚀 Quick Start

**New to Strands?** Start here:

```bash
cd examples/01-basics
python plugin-basics.py
```

That's it! Follow the examples in order and you'll learn everything step-by-step.

---

## 📂 What's Inside

```
basic-strands-agent/
├── examples/              # Runnable code examples (START HERE!)
│   ├── 01-basics/        # Basic plugins and agents
│   ├── 02-custom-plugins/# Build your own plugins
│   ├── 03-skills/        # Specialized instructions
│   ├── 04-hooks/         # Direct event handling
│   └── 05-session-management/ # Persist conversations
│
├── skills/               # Example skill definitions
│   ├── math-helper/
│   └── email-writer/
│
├── utils/                # Reusable utilities
│   └── sqlite_session_manager.py
│
└── docs/                 # Comprehensive guides
    ├── plugins.md
    ├── custom-plugins.md
    ├── skills.md
    └── ...
```

---

## 📚 Learning Path

### Complete Beginner? Follow This Path:

#### Level 1: Basics (30 minutes)
1. **[examples/01-basics/plugin-basics.py](examples/01-basics/plugin-basics.py)** ⭐ START HERE
   - Learn how to use a built-in plugin
   - Understand basic agent setup

2. **[examples/01-basics/basic-agent-bedrock.py](examples/01-basics/basic-agent-bedrock.py)**
   - Create agents with tools
   - Register hooks
   - Handle events

#### Level 2: Custom Plugins (1 hour)
3. **[examples/02-custom-plugins/custom-plugin-basics.py](examples/02-custom-plugins/custom-plugin-basics.py)**
   - Create your first custom plugin
   - Learn the 3 required parts

4. **[examples/02-custom-plugins/custom-plugin-counter.py](examples/02-custom-plugins/custom-plugin-counter.py)**
   - Track conversation statistics
   - Manage plugin state

5. **[examples/02-custom-plugins/plugin-cost-tracker.py](examples/02-custom-plugins/plugin-cost-tracker.py)** 🏭
   - Production-ready cost tracking
   - Real-world patterns

6. **[examples/02-custom-plugins/plugin-rate-limiter.py](examples/02-custom-plugins/plugin-rate-limiter.py)** 🏭
   - Rate limiting strategies
   - Request control

#### Level 3: Skills (45 minutes)
7. **[examples/03-skills/skills-basics.py](examples/03-skills/skills-basics.py)**
   - What are skills?
   - Create skills in code

8. **[examples/03-skills/skills-from-files.py](examples/03-skills/skills-from-files.py)**
   - Load skills from SKILL.md files
   - Skill activation

9. **[examples/03-skills/skills-vs-plugins-vs-tools.py](examples/03-skills/skills-vs-plugins-vs-tools.py)**
   - Understand when to use what

#### Level 4: Advanced (1 hour)
10. **[examples/04-hooks/hook-example-logger.py](examples/04-hooks/hook-example-logger.py)**
    - Use hooks directly
    - Hooks vs plugins

11. **[examples/05-session-management/learn_session_management.py](examples/05-session-management/learn_session_management.py)**
    - Interactive tutorial
    - How sessions work

12. **[examples/05-session-management/session-manager-sqlite.py](examples/05-session-management/session-manager-sqlite.py)**
    - Database persistence
    - Production patterns

---

## 🎯 Find What You Need

### Want to Build Plugins?
→ [examples/02-custom-plugins/](examples/02-custom-plugins/)
→ [docs/custom-plugins.md](docs/custom-plugins.md)

### Need Skills?
→ [examples/03-skills/](examples/03-skills/)
→ [docs/skills.md](docs/skills.md)

### Session Management?
→ [examples/05-session-management/](examples/05-session-management/)
→ [docs/session-management.md](docs/session-management.md)

### Understand Concepts?
→ [docs/hooks-vs-plugins.md](docs/hooks-vs-plugins.md)
→ [docs/plugins.md](docs/plugins.md)

---

## 📖 Documentation

Complete guides in [docs/](docs/):

| Guide | What You'll Learn |
|-------|-------------------|
| [plugins.md](docs/plugins.md) | Complete plugin guide |
| [hooks-vs-plugins.md](docs/hooks-vs-plugins.md) | Difference between hooks and plugins |
| [custom-plugins.md](docs/custom-plugins.md) | Build your own plugins |
| [skills.md](docs/skills.md) | Skills from scratch |
| [skills-gotcha.md](docs/skills-gotcha.md) | Common pitfalls and solutions |
| [session-management.md](docs/session-management.md) | Persist conversations |

---

## 🏃 Quick Examples

### Use a Built-in Plugin
```python
from strands import Agent
from strands.vended_plugins.context_injector import ContextInjector
import datetime

agent = Agent(
    plugins=[
        ContextInjector(lambda: f"Current time: {datetime.datetime.now()}")
    ]
)
```
See: [examples/01-basics/plugin-basics.py](examples/01-basics/plugin-basics.py)

### Create a Custom Plugin
```python
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent

class MyPlugin(Plugin):
    def __init__(self, name="my-plugin"):
        self._name = name
        super().__init__()
        self.count = 0

    @property
    def name(self) -> str:
        return self._name

    def init_agent(self, agent) -> None:
        agent.add_hook(self._count, BeforeModelCallEvent)

    def _count(self, event):
        self.count += 1
        print(f"Request #{self.count}")

agent = Agent(plugins=[MyPlugin()])
```
See: [examples/02-custom-plugins/custom-plugin-basics.py](examples/02-custom-plugins/custom-plugin-basics.py)

### Create a Skill
```python
from strands import Agent, AgentSkills, Skill

skill = Skill(
    name="math-helper",
    description="Solve math problems step-by-step",
    instructions="Show your work, explain each step..."
)

agent = Agent(plugins=[AgentSkills(skills=[skill])])
```
See: [examples/03-skills/skills-basics.py](examples/03-skills/skills-basics.py)

### Persist Sessions
```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager

session = FileSessionManager(
    session_id="user-123",
    storage_dir="./sessions"
)

agent = Agent(
    system_prompt="You are helpful.",
    session_manager=session
)

agent("Remember: My name is Alex")
# Session automatically saved!
```
See: [examples/05-session-management/session-manager-file.py](examples/05-session-management/session-manager-file.py)

---

## 🎓 Key Concepts

### Plugins
**What:** Modify HOW the agent works
**Examples:** Logging, cost tracking, rate limiting
**When:** You want to extend agent behavior

### Skills
**What:** Specialized instructions the agent activates on-demand
**Examples:** Math tutor, email writer, code reviewer
**When:** Agent needs domain-specific knowledge

### Hooks
**What:** Run code at specific lifecycle events
**Examples:** Before/after model calls, tool calls
**When:** You need direct event handling

### Tools
**What:** Actions the agent can perform
**Examples:** Calculate, read files, search web
**When:** Agent needs to DO something

---

## 🗂️ Examples by Topic

### Plugins
| Example | Difficulty | Time |
|---------|-----------|------|
| [plugin-basics.py](examples/01-basics/plugin-basics.py) | ⭐ Beginner | 5min |
| [custom-plugin-basics.py](examples/02-custom-plugins/custom-plugin-basics.py) | ⭐⭐ Easy | 15min |
| [custom-plugin-counter.py](examples/02-custom-plugins/custom-plugin-counter.py) | ⭐⭐ Easy | 15min |
| [plugin-cost-tracker.py](examples/02-custom-plugins/plugin-cost-tracker.py) | ⭐⭐⭐ Intermediate | 20min |
| [plugin-rate-limiter.py](examples/02-custom-plugins/plugin-rate-limiter.py) | ⭐⭐⭐ Intermediate | 20min |

### Skills
| Example | Difficulty | Time |
|---------|-----------|------|
| [skills-basics.py](examples/03-skills/skills-basics.py) | ⭐ Beginner | 10min |
| [skills-from-files.py](examples/03-skills/skills-from-files.py) | ⭐⭐ Easy | 15min |
| [skills-vs-plugins-vs-tools.py](examples/03-skills/skills-vs-plugins-vs-tools.py) | ⭐⭐ Easy | 10min |

### Session Management
| Example | Difficulty | Time |
|---------|-----------|------|
| [learn_session_management.py](examples/05-session-management/learn_session_management.py) | ⭐ Beginner | 20min |
| [session-manager-file.py](examples/05-session-management/session-manager-file.py) | ⭐⭐ Easy | 10min |
| [session-manager-sqlite.py](examples/05-session-management/session-manager-sqlite.py) | ⭐⭐⭐ Intermediate | 15min |

---

## 🛠️ Utilities

Production-ready components in [utils/](utils/):

**[sqlite_session_manager.py](utils/sqlite_session_manager.py)**
- Full SQLite session manager implementation
- Transaction-safe
- Production-ready
- Copy into your projects!

---

## 🎯 Templates

### Custom Plugin Template
```python
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent

class MyPlugin(Plugin):
    def __init__(self, name="my-plugin"):
        self._name = name
        super().__init__()
        # Your initialization

    @property
    def name(self) -> str:
        return self._name

    def init_agent(self, agent) -> None:
        agent.add_hook(self._hook, BeforeModelCallEvent)

    def _hook(self, event):
        # Your logic here
        pass
```

### Skill Template (Inline)
```python
from strands import Skill

skill = Skill(
    name="my-skill",
    description="Brief description",
    instructions="Detailed instructions..."
)
```

### Skill Template (File)
Create `skills/my-skill/SKILL.md`:
```markdown
---
name: my-skill
description: Brief description
---

# My Skill

Detailed instructions here...
```

---

## 📦 Folder Organization

See [ORGANIZATION.md](ORGANIZATION.md) for:
- Before/after comparison
- What was removed
- Migration guide
- Maintenance notes

---

## 💡 Tips for Learning

1. **Follow the order** - Examples are numbered for a reason
2. **Run everything** - Don't just read, execute the code
3. **Modify examples** - Change values and see what happens
4. **Read error messages** - They tell you what's wrong
5. **Check docs/** - Deep dives for each topic

---

## 🐛 Common Issues

### Plugin: "Can't instantiate abstract class"
**Problem:** Missing `name` property
**Solution:** Add `@property def name(self)` to your plugin
**See:** [docs/custom-plugins.md](docs/custom-plugins.md)

### Skills: `get_available_skills()` returns empty
**Problem:** Need to pass agent parameter
**Solution:** `plugin.get_available_skills(agent)`
**See:** [docs/skills-gotcha.md](docs/skills-gotcha.md)

### Import Error: "No module named strands"
**Problem:** Not in virtual environment
**Solution:** `source .venv/bin/activate` or `uv run python file.py`

---

## 🔗 External Resources

- [Strands Documentation](https://strandsagents.com/)
- [Agent Skills Specification](https://agentskills.io/)
- [Strands GitHub](https://github.com/strands-agents)

---

## 🤝 Contributing

This is a learning resource! Feel free to:
- Add new examples
- Improve documentation
- Fix bugs
- Share your custom plugins/skills

---

## 📧 Need Help?

1. Check [docs/](docs/) for detailed guides
2. Look at similar examples
3. Read error messages carefully
4. Simplify your code to isolate the issue

---

## 🎉 You're Ready!

Start with: **`python examples/01-basics/plugin-basics.py`**

Then follow the learning path above. Happy coding! 🚀

---

**Last Updated:** 2026-09-06
**Strands Version:** Compatible with latest SDK
