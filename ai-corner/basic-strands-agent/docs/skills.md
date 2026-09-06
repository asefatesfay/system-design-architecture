# Skills Basics Guide

## What are Skills?

Skills are **specialized instruction modules** that your agent can activate on-demand. Instead of putting all instructions in the system prompt, you give the agent access to focused skill packages that load only when needed.

Think of it like this:
- **Without skills**: One massive instruction manual (system prompt gets huge)
- **With skills**: A library of specialized guides that the agent picks from as needed

---

## Why Use Skills?

### Problem: System Prompt Gets Too Big

```python
# Without skills - everything in one prompt
agent = Agent(
    system_prompt="""
    You are an assistant that can:
    1. Solve math problems step by step...
    2. Write professional emails...
    3. Review code for bugs...
    4. Summarize documents...
    5. Generate reports...
    6. Create presentations...
    [... thousands of lines ...]
    """
)
# 😫 The agent sees ALL instructions for EVERY request!
```

### Solution: Modular Skills

```python
# With skills - load only what's needed
agent = Agent(
    system_prompt="You are a helpful assistant.",
    plugins=[AgentSkills(skills=[
        math_skill,
        email_skill,
        code_review_skill,
        # ... add as many as you want
    ])]
)
# 🎉 The agent only loads relevant instructions!
```

---

## Simple Example: Inline Skills

Create skills directly in code (no files needed):

```python
from strands import Agent, AgentSkills, Skill

# Define a skill
greeting_skill = Skill(
    name="greeting",
    description="Generate friendly greetings",
    instructions="""
When greeting someone:
1. Be warm and friendly
2. Use their name if you know it
3. Add a relevant emoji
"""
)

# Use it
agent = Agent(
    plugins=[AgentSkills(skills=[greeting_skill])]
)

response = agent("Greet me! My name is Sarah.")
# Agent activates the greeting skill automatically!
```

**Run:** [skills-basics.py](skills-basics.py)

---

## File-Based Skills

Skills can live in directories with `SKILL.md` files:

### Directory Structure

```
skills/
├── math-helper/
│   └── SKILL.md
└── email-writer/
    └── SKILL.md
```

### SKILL.md Format

```markdown
---
name: math-helper
description: Solve math problems step-by-step
allowed-tools: calculator
---

# Math Helper Skill

You are a math tutor. When solving problems:
1. Show your work
2. Explain each step
3. Verify the answer
```

### Loading from Files

```python
from strands import Agent, AgentSkills

# Load all skills from directory
agent = Agent(
    plugins=[AgentSkills(skills="./skills/")]
)

# Agent automatically has access to:
# - math-helper
# - email-writer
```

**Run:** [skills-from-files.py](skills-from-files.py)

---

## How Skills Work

### 1. Discovery Phase

When you create the agent, skills are registered:

```python
agent = Agent(
    plugins=[AgentSkills(skills=[skill1, skill2, skill3])]
)
```

The agent sees:
```
Available skills:
- math-helper: Solve math problems step-by-step
- email-writer: Compose professional emails
- code-reviewer: Review code for bugs
```

### 2. Activation Phase

When the user asks something:

```python
agent("What is 15% of 200?")
```

The agent thinks: *"This is a math problem, I should use the math-helper skill"*

### 3. Execution Phase

The agent activates the skill and gets the full instructions:

```
[Full math-helper instructions loaded]

You are a math tutor. When solving problems:
1. Show your work
2. Use calculator for complex math
3. Explain each step clearly
...
```

The agent then follows those instructions!

---

## Skills vs System Prompt

| Approach | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **System Prompt** | Always-needed instructions | Simple, direct | Gets bloated |
| **Skills** | Specialized, conditional instructions | Modular, clean | More setup |

### Use System Prompt For:
- Core personality/tone
- Universal rules
- Always-needed context

```python
agent = Agent(
    system_prompt="You are helpful, concise, and professional."
)
```

### Use Skills For:
- Specialized tasks
- Domain-specific knowledge
- Optional capabilities

```python
agent = Agent(
    system_prompt="You are a helpful assistant.",
    plugins=[AgentSkills(skills=[
        pdf_processing_skill,
        data_analysis_skill,
        code_review_skill
    ])]
)
```

---

## Creating a Skill (Two Ways)

### Way 1: Programmatically (In Code)

```python
from strands import Skill

skill = Skill(
    name="summarizer",
    description="Summarize long documents",
    instructions="""
When summarizing:
1. Read the full document
2. Identify key points
3. Write 3-5 bullet points
4. Keep it under 100 words
"""
)
```

**Good for:**
- Quick prototyping
- Dynamic skills
- Simple instructions

### Way 2: File-Based (SKILL.md)

```markdown
---
name: summarizer
description: Summarize long documents
---

# Document Summarizer

When summarizing:
1. Read the full document
2. Identify key points
3. Write 3-5 bullet points
4. Keep it under 100 words
```

**Good for:**
- Complex instructions
- Sharing with team
- Version control
- Reusable across projects

---

## Real-World Example

### Customer Support Agent with Multiple Skills

```python
from strands import Agent, AgentSkills, Skill

# Define support skills
order_lookup = Skill(
    name="order-lookup",
    description="Look up customer orders",
    instructions="Use the order_id to find order details..."
)

refund_process = Skill(
    name="refund-process",
    description="Process refunds for customers",
    instructions="Check eligibility, calculate amount, process refund..."
)

troubleshooting = Skill(
    name="troubleshooting",
    description="Help customers fix technical issues",
    instructions="Gather symptoms, check common issues, provide steps..."
)

# Create support agent
support_agent = Agent(
    system_prompt="You are a friendly customer support agent.",
    plugins=[AgentSkills(skills=[
        order_lookup,
        refund_process,
        troubleshooting
    ])],
    tools=[database_tool, payment_tool]
)

# Agent automatically uses the right skill:
support_agent("I need a refund for order #12345")
# → Activates refund-process skill

support_agent("My app keeps crashing")
# → Activates troubleshooting skill
```

---

## Managing Skills at Runtime

```python
from strands import Agent, AgentSkills, Skill

plugin = AgentSkills(skills="./skills/")
agent = Agent(plugins=[plugin])

# List available skills
for skill in plugin.get_available_skills():
    print(f"{skill.name}: {skill.description}")

# Add a new skill dynamically
new_skill = Skill(
    name="translator",
    description="Translate between languages",
    instructions="..."
)
current_skills = plugin.get_available_skills()
plugin.set_available_skills(current_skills + [new_skill])

# Check which skills were activated
activated = plugin.get_activated_skills(agent)
print(f"The agent used these skills: {activated}")
```

---

## Skills with Resources

Skills can include helper files:

```
my-skill/
├── SKILL.md
├── scripts/
│   └── process.py      # Scripts the agent can run
├── references/
│   └── API.md          # Reference docs
└── assets/
    └── template.json   # Data files
```

```markdown
---
name: data-processor
description: Process CSV data files
allowed-tools: file_read shell
---

# Data Processor

To process data:
1. Run the script: `scripts/process.py input.csv`
2. Read the output with `file_read`
3. Summarize results
```

```python
from strands import Agent, AgentSkills
from strands_tools import file_read, shell

agent = Agent(
    plugins=[AgentSkills(skills="./my-skill/")],
    tools=[file_read, shell]  # Tools the skill needs
)
```

---

## Quick Comparison

### Plugins vs Skills

- **Plugins** = Change HOW the agent works (rate limiting, logging, cost tracking)
- **Skills** = Change WHAT the agent knows (specialized instructions)

```python
agent = Agent(
    # Plugins: Behavior modifications
    plugins=[
        RateLimiterPlugin(),       # HOW: Limit requests
        CostTrackerPlugin(),       # HOW: Track costs
        AgentSkills(skills=[...])  # WHAT: Load instructions
    ]
)
```

### Tools vs Skills

- **Tools** = Actions the agent can take (call APIs, read files, calculate)
- **Skills** = Instructions on how to use those tools

```python
agent = Agent(
    tools=[calculator, file_read],  # Actions available
    plugins=[AgentSkills(skills=[
        math_skill,    # Instructions: "Use calculator to solve step-by-step"
        reader_skill   # Instructions: "Use file_read to extract key info"
    ])]
)
```

---

## Best Practices

### 1. Keep Skills Focused
✅ Good: `email-writer` - One clear purpose
❌ Bad: `general-helper` - Too broad

### 2. Clear Descriptions
✅ Good: `"Solve math problems step-by-step with explanations"`
❌ Bad: `"Math stuff"`

The description helps the agent decide when to use the skill!

### 3. Structure Instructions
```markdown
# Good Structure

## When to use this skill
[Clear criteria]

## Steps to follow
1. First do this
2. Then do that
3. Finally verify

## Examples
[Show concrete examples]
```

### 4. List Required Tools
```markdown
---
allowed-tools: file_read shell calculator
---
```

This documents what tools the skill needs.

---

## Try It Yourself

### 1. Run Basic Example
```bash
python skills-basics.py
```

### 2. Create Your Own Skill
```bash
mkdir -p skills/my-skill
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: What your skill does
---

Your instructions here!
EOF
```

### 3. Run File-Based Example
```bash
python skills-from-files.py
```

---

## Summary

| Concept | Purpose | Example |
|---------|---------|---------|
| **Skill** | Specialized instructions | Math tutor, email writer |
| **AgentSkills Plugin** | Manages skill loading | `AgentSkills(skills=[...])` |
| **SKILL.md** | File format for skills | YAML frontmatter + markdown |
| **Activation** | Agent loads skill when needed | Automatic, based on description |

**Key insight:** Skills keep your agent's context lean while giving it access to deep, specialized knowledge on-demand!

---

## Files in This Project

- [skills-basics.py](skills-basics.py) - Simple inline skill example
- [skills-from-files.py](skills-from-files.py) - Load skills from SKILL.md files
- [skills/math-helper/SKILL.md](skills/math-helper/SKILL.md) - Example skill file
- [skills/email-writer/SKILL.md](skills/email-writer/SKILL.md) - Example skill file

Start with `skills-basics.py` - it's the simplest! 🚀
