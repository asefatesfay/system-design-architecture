# Strands Agent Examples

A well-organized collection of examples and guides for learning Strands Agents SDK from scratch.

## 📂 Folder Structure

```
basic-strands-agent/
├── examples/           # Runnable examples
│   ├── 01-basics/     # Start here!
│   ├── 02-custom-plugins/
│   ├── 03-skills/
│   ├── 04-hooks/
│   └── 05-session-management/
├── skills/            # Example skill definitions
├── utils/             # Reusable utilities
├── docs/              # Comprehensive guides
└── README.md          # This file
```

---

## 🚀 Quick Start

### 1. Start with Basics

```bash
cd examples/01-basics

# Basic plugin usage
python plugin-basics.py

# Basic agent setup
python basic-agent-bedrock.py
```

### 2. Learn Custom Plugins

```bash
cd examples/02-custom-plugins

# Simple custom plugin
python custom-plugin-basics.py

# Conversation counter
python custom-plugin-counter.py

# Production-ready examples
python plugin-cost-tracker.py
python plugin-rate-limiter.py
```

### 3. Explore Skills

```bash
cd examples/03-skills

# Skills in code (simplest)
python skills-basics.py

# Skills from files
python skills-from-files.py

# Understand differences
python skills-vs-plugins-vs-tools.py
```

---

## 📚 Learning Path

Follow this order for the best learning experience:

### Level 1: Fundamentals (Start Here!)

1. **[examples/01-basics/plugin-basics.py](examples/01-basics/plugin-basics.py)**
   - What: Use a built-in plugin (ContextInjector)
   - Learn: How plugins work
   - Time: 5 minutes

2. **[examples/01-basics/basic-agent-bedrock.py](examples/01-basics/basic-agent-bedrock.py)**
   - What: Create an agent with tools and hooks
   - Learn: Agent basics, hooks
   - Time: 10 minutes

### Level 2: Custom Plugins

3. **[examples/02-custom-plugins/custom-plugin-basics.py](examples/02-custom-plugins/custom-plugin-basics.py)**
   - What: Create your first custom plugin
   - Learn: Plugin structure, hooks
   - Time: 15 minutes

4. **[examples/02-custom-plugins/custom-plugin-counter.py](examples/02-custom-plugins/custom-plugin-counter.py)**
   - What: Track conversation statistics
   - Learn: Event data, state management
   - Time: 15 minutes

5. **[examples/02-custom-plugins/plugin-cost-tracker.py](examples/02-custom-plugins/plugin-cost-tracker.py)**
   - What: Production-ready cost tracking
   - Learn: Real-world patterns
   - Time: 20 minutes

6. **[examples/02-custom-plugins/plugin-rate-limiter.py](examples/02-custom-plugins/plugin-rate-limiter.py)**
   - What: Rate limiting plugin
   - Learn: Request control, strategies
   - Time: 20 minutes

### Level 3: Skills

7. **[examples/03-skills/skills-basics.py](examples/03-skills/skills-basics.py)**
   - What: Create skills in code
   - Learn: What skills are
   - Time: 10 minutes

8. **[examples/03-skills/skills-from-files.py](examples/03-skills/skills-from-files.py)**
   - What: Load skills from SKILL.md files
   - Learn: File-based skills, activation
   - Time: 15 minutes

9. **[examples/03-skills/skills-vs-plugins-vs-tools.py](examples/03-skills/skills-vs-plugins-vs-tools.py)**
   - What: Understand the differences
   - Learn: When to use what
   - Time: 10 minutes

### Level 4: Advanced Topics

10. **[examples/04-hooks/hook-example-logger.py](examples/04-hooks/hook-example-logger.py)**
    - What: Use hooks directly (without plugins)
    - Learn: Hook registration
    - Time: 10 minutes

11. **[examples/05-session-management/](examples/05-session-management/)**
    - What: Persist conversations
    - Learn: Session management, SQLite
    - Time: 30 minutes

---

## 📖 Documentation

Comprehensive guides in the [docs/](docs/) folder:

| Guide | Description |
|-------|-------------|
| [plugins.md](docs/plugins.md) | Complete plugin guide |
| [hooks-vs-plugins.md](docs/hooks-vs-plugins.md) | Understand the difference |
| [custom-plugins.md](docs/custom-plugins.md) | Build your own plugins |
| [skills.md](docs/skills.md) | Skills from scratch |
| [skills-gotcha.md](docs/skills-gotcha.md) | Common skills pitfalls |
| [session-management.md](docs/session-management.md) | Persist conversations |

---

## 🗂️ Examples by Category

### Plugins

| File | Description | Difficulty |
|------|-------------|------------|
| [plugin-basics.py](examples/01-basics/plugin-basics.py) | Built-in ContextInjector | ⭐ Beginner |
| [custom-plugin-basics.py](examples/02-custom-plugins/custom-plugin-basics.py) | Simple custom plugin | ⭐⭐ Easy |
| [custom-plugin-counter.py](examples/02-custom-plugins/custom-plugin-counter.py) | Conversation counter | ⭐⭐ Easy |
| [plugin-cost-tracker.py](examples/02-custom-plugins/plugin-cost-tracker.py) | Track API costs | ⭐⭐⭐ Intermediate |
| [plugin-rate-limiter.py](examples/02-custom-plugins/plugin-rate-limiter.py) | Rate limiting | ⭐⭐⭐ Intermediate |

### Skills

| File | Description | Difficulty |
|------|-------------|------------|
| [skills-basics.py](examples/03-skills/skills-basics.py) | Inline skills | ⭐ Beginner |
| [skills-from-files.py](examples/03-skills/skills-from-files.py) | File-based skills | ⭐⭐ Easy |
| [skills-working-example.py](examples/03-skills/skills-working-example.py) | Guaranteed working example | ⭐ Beginner |
| [skills-vs-plugins-vs-tools.py](examples/03-skills/skills-vs-plugins-vs-tools.py) | Comparison | ⭐⭐ Easy |

### Session Management

| File | Description | Difficulty |
|------|-------------|------------|
| [session-manager-file.py](examples/05-session-management/session-manager-file.py) | File-based sessions | ⭐⭐ Easy |
| [session-manager-sqlite.py](examples/05-session-management/session-manager-sqlite.py) | SQLite sessions | ⭐⭐⭐ Intermediate |
| [learn_session_management.py](examples/05-session-management/learn_session_management.py) | Interactive tutorial | ⭐ Beginner |
| [inspect_sessions.py](examples/05-session-management/inspect_sessions.py) | Inspect SQLite DB | ⭐⭐ Easy |

---

## 🛠️ Utilities

Reusable components in [utils/](utils/):

- **[sqlite_session_manager.py](utils/sqlite_session_manager.py)** - Production-ready SQLite session manager

---

## 🎯 Key Concepts

### Plugins
**What:** Modify HOW the agent works
**Examples:** Add logging, track costs, rate limiting
**When:** You want to extend agent behavior

### Skills
**What:** Specialized instructions the agent can activate
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

## 📝 Quick Reference

### Custom Plugin Template

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
        # Your logic here
        pass
```

### Skill Template

```python
from strands import Agent, AgentSkills, Skill

skill = Skill(
    name="my-skill",
    description="What it does",
    instructions="How to do it"
)

agent = Agent(plugins=[AgentSkills(skills=[skill])])
```

---

## 🤝 Contributing

Found an issue or want to add an example? The files are organized for easy navigation and contribution.

---

## 📦 Skills Folder

Example skill definitions:

```
skills/
├── math-helper/SKILL.md
└── email-writer/SKILL.md
```

Used by [skills-from-files.py](examples/03-skills/skills-from-files.py)

---

## 🎓 Tips

1. **Start Simple**: Begin with Level 1 examples
2. **Run Everything**: Don't just read - run the code!
3. **Modify Examples**: Change values and see what happens
4. **Read Docs**: Check [docs/](docs/) for deep dives
5. **Build Your Own**: Use templates to create custom solutions

---

## 🔗 External Resources

- [Strands Documentation](https://strandsagents.com/)
- [Agent Skills Specification](https://agentskills.io/)

---

## 📧 Getting Help

1. Check [docs/](docs/) guides
2. Look at similar examples
3. Read error messages carefully
4. Simplify your code to debug

---

**Happy learning!** 🚀

Start with: `python examples/01-basics/plugin-basics.py`
