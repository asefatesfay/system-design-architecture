# Skills Gotcha: get_available_skills() Returns Empty

## The Problem

```python
skills_plugin = AgentSkills(skills="./skills/")

# This returns EMPTY! 😱
for skill in skills_plugin.get_available_skills():
    print(f"• {skill.name}: {skill.description}")
# (prints nothing)
```

## The Solution

```python
skills_plugin = AgentSkills(skills="./skills/")
agent = Agent(plugins=[skills_plugin])

# Pass the agent! ✅
for skill in skills_plugin.get_available_skills(agent):
    print(f"• {skill.name}: {skill.description}")
# (now it works!)
```

---

## Why This Happens

### File-based skills are loaded lazily per-agent

When you load skills from files:
```python
AgentSkills(skills="./skills/")  # Path to directory
```

These are **filesystem skills** that get loaded when the agent is created, not when the plugin is created.

### Two types of skills

| Type | Example | Loaded When |
|------|---------|-------------|
| **Inline skills** | `Skill(name="test", ...)` | Immediately |
| **File-based skills** | `"./skills/"` | When agent is initialized |

### The method signature

```python
def get_available_skills(agent: Agent | None = None) -> list[Skill]
```

**Without agent:**
- Returns only inline skills (created with `Skill()`)
- File-based skills are NOT included

**With agent:**
- Returns ALL skills for that specific agent
- Includes file-based skills loaded from filesystem

---

## Examples

### ❌ Wrong - Returns Empty

```python
# Load from files
plugin = AgentSkills(skills="./skills/")

# This is empty because filesystem skills aren't loaded yet
skills = plugin.get_available_skills()
print(len(skills))  # 0
```

### ✅ Correct - Returns All Skills

```python
# Load from files
plugin = AgentSkills(skills="./skills/")

# Create agent (this loads the filesystem skills)
agent = Agent(plugins=[plugin])

# Pass the agent to get ALL skills
skills = plugin.get_available_skills(agent)
print(len(skills))  # 2 (or however many you have)
```

### ✅ Alternative - Use Inline Skills

If you don't want to pass the agent, create skills in code:

```python
# Create skills in code (not from files)
skill1 = Skill(name="test1", description="...", instructions="...")
skill2 = Skill(name="test2", description="...", instructions="...")

plugin = AgentSkills(skills=[skill1, skill2])

# This works without passing agent!
skills = plugin.get_available_skills()
print(len(skills))  # 2
```

---

## Quick Reference

```python
# FILE-BASED SKILLS (from ./skills/ directory)
plugin = AgentSkills(skills="./skills/")
agent = Agent(plugins=[plugin])

# Must pass agent:
plugin.get_available_skills(agent)  # ✅ Works

# Without agent:
plugin.get_available_skills()  # ❌ Returns empty


# INLINE SKILLS (created in code)
skill = Skill(name="test", description="...", instructions="...")
plugin = AgentSkills(skills=[skill])

# Works either way:
plugin.get_available_skills()       # ✅ Works
plugin.get_available_skills(agent)  # ✅ Also works
```

---

## Why This Design?

Each agent can have its own filesystem (sandbox/container), so filesystem skills are loaded per-agent, not globally. This allows different agents to see different skills based on their environment.

**Example:**
```python
plugin = AgentSkills(skills="./skills/")

# Agent 1 in container A
agent1 = Agent(plugins=[plugin])
# Loads skills from container A's filesystem

# Agent 2 in container B
agent2 = Agent(plugins=[plugin])
# Loads skills from container B's filesystem

# Different agents can have different skills!
plugin.get_available_skills(agent1)  # Skills from container A
plugin.get_available_skills(agent2)  # Skills from container B
```

---

## The Fix (Updated Code)

### Before (doesn't work):
```python
skills_plugin = AgentSkills(skills="./skills/")

for skill in skills_plugin.get_available_skills():  # ❌ Empty
    print(f"• {skill.name}")
```

### After (works):
```python
skills_plugin = AgentSkills(skills="./skills/")
agent = Agent(plugins=[skills_plugin])

for skill in skills_plugin.get_available_skills(agent):  # ✅ Works
    print(f"• {skill.name}")
```

---

## Summary

**When loading skills from files:**
1. Create the agent first
2. Pass the agent to `get_available_skills(agent)`

**When creating skills in code:**
1. Can call `get_available_skills()` without agent
2. Works immediately

**Remember:** File-based skills = pass agent. Inline skills = optional.
