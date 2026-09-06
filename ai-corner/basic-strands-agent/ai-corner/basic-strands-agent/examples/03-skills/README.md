# 03-skills: Specialized Instructions

Skills are modular instruction sets the agent activates on-demand.

## Files

### skills-basics.py ⭐ **START HERE**
- **What:** Create skills in code (no files)
- **Learns:** What skills are, inline skills
- **Time:** 10 minutes
- **Run:** `python skills-basics.py`

### skills-from-files.py
- **What:** Load skills from SKILL.md files
- **Learns:** File-based skills, activation, `get_available_skills(agent)`
- **Time:** 15 minutes
- **Run:** `python skills-from-files.py`
- **Note:** Uses `../../skills/` folder

### skills-working-example.py
- **What:** Guaranteed working inline skills example
- **Learns:** Alternative to file-based approach
- **Time:** 10 minutes
- **Run:** `python skills-working-example.py`

### skills-vs-plugins-vs-tools.py
- **What:** Visual comparison of all three concepts
- **Learns:** When to use skills vs plugins vs tools
- **Time:** 10 minutes
- **Run:** `python skills-vs-plugins-vs-tools.py`

## Skill Template (Inline)

```python
from strands import Agent, AgentSkills, Skill

skill = Skill(
    name="my-skill",
    description="Brief description for agent",
    instructions="Detailed instructions..."
)

agent = Agent(plugins=[AgentSkills(skills=[skill])])
```

## Skill Template (File)

**SKILL.md:**
```markdown
---
name: my-skill
description: Brief description
---

# My Skill

Detailed instructions here...
```

## Key Concepts

**Skills =** Specialized knowledge
**Plugins =** Behavior modification
**Tools =** Actions to perform

### When to Use Skills

✅ Agent needs domain-specific knowledge
✅ Instructions are conditional (not always needed)
✅ You want modular, reusable instruction sets

### Important Gotcha

When loading skills from files, pass agent to `get_available_skills()`:

```python
# ❌ Wrong
skills = plugin.get_available_skills()

# ✅ Correct
skills = plugin.get_available_skills(agent)
```

See [../../docs/skills-gotcha.md](../../docs/skills-gotcha.md)

## Concepts Learned

- ✅ What skills are
- ✅ Inline vs file-based skills
- ✅ Skill activation
- ✅ Skills vs plugins vs tools
- ✅ Common pitfalls

## Next Steps

Check out [../04-hooks/](../04-hooks/) for direct hook usage.
