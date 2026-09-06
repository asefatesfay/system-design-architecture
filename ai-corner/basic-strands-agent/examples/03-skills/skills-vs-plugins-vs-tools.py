"""
Understanding: Skills vs Plugins vs Tools

This example shows the difference between these three concepts.
"""

from strands import Agent, AgentSkills, Skill
from strands_tools import calculator
from strands.vended_plugins.context_injector import ContextInjector
import datetime

print("\n" + "=" * 70)
print("Skills vs Plugins vs Tools - What's the Difference?")
print("=" * 70 + "\n")

# =============================================================================
# 1. TOOLS - Actions the agent can perform
# =============================================================================
print("🔧 TOOLS: Actions the agent can perform")
print("-" * 70)
print("Examples:")
print("  • calculator - Do math calculations")
print("  • file_read - Read files")
print("  • web_search - Search the web")
print("  • database_query - Query database")
print("\nTools = WHAT THE AGENT CAN DO")
print()

# =============================================================================
# 2. PLUGINS - Modify HOW the agent works
# =============================================================================
print("🔌 PLUGINS: Modify HOW the agent works")
print("-" * 70)
print("Examples:")
print("  • ContextInjector - Add dynamic info (time, user data)")
print("  • RateLimiter - Limit requests per minute")
print("  • CostTracker - Track API costs")
print("  • Logger - Log all conversations")
print("\nPlugins = HOW THE AGENT BEHAVES")
print()

# =============================================================================
# 3. SKILLS - Specialized instructions
# =============================================================================
print("📚 SKILLS: Specialized instructions")
print("-" * 70)
print("Examples:")
print("  • math-helper - Instructions on how to solve math problems")
print("  • email-writer - Instructions on how to write emails")
print("  • code-reviewer - Instructions on how to review code")
print("  • summarizer - Instructions on how to summarize documents")
print("\nSkills = WHAT THE AGENT KNOWS")
print()

print("=" * 70)
print("Visual Comparison")
print("=" * 70)
print("""
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR AGENT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  System Prompt: "You are a helpful assistant"                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ 🔌 PLUGINS (Behavior Modifiers)                       │    │
│  │  • Add current time to every request                  │    │
│  │  • Track costs                                        │    │
│  │  • Rate limit requests                                │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ 📚 SKILLS (On-Demand Instructions)                    │    │
│  │  Available:                                            │    │
│  │   - math-helper: Solve math step-by-step             │    │
│  │   - email-writer: Write professional emails           │    │
│  │                                                        │    │
│  │  Activated when relevant!                             │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ 🔧 TOOLS (Actions)                                     │    │
│  │  • calculator                                          │    │
│  │  • file_read                                           │    │
│  │  • web_search                                          │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")

print("\n" + "=" * 70)
print("Example: All Three Together")
print("=" * 70 + "\n")

# Create a skill
math_skill = Skill(
    name="math-tutor",
    description="Teach math concepts step-by-step",
    instructions="""
When teaching math:
1. Break down the problem
2. Use the calculator tool for complex math
3. Explain each step clearly
4. Provide examples
"""
)

# Create a plugin (adds current time)
time_plugin = ContextInjector(
    lambda: f"Current time: {datetime.datetime.now().strftime('%I:%M %p')}"
)

# Create agent with all three
agent = Agent(
    system_prompt="You are a friendly math tutor.",

    # Plugins: HOW the agent behaves
    plugins=[
        time_plugin,              # Always inject current time
        AgentSkills(skills=[math_skill])  # Load math skill when needed
    ],

    # Tools: WHAT the agent can do
    tools=[calculator]            # Can perform calculations
)

print("Agent created with:")
print("  • System Prompt: Core personality")
print("  • Plugin: Adds current time to context")
print("  • Skill: Math teaching instructions")
print("  • Tool: Calculator for calculations")
print()

# Test it
print("-" * 70)
question = "What is 15% of 250? Teach me how to calculate it."
print(f"User: {question}")
print("-" * 70)
response = agent(question)
print(f"Agent: {response}")
print()

print("=" * 70)
print("What Happened?")
print("=" * 70)
print("""
1. 🔌 Plugin injected current time into context
2. 📚 Agent activated the math-tutor skill (saw "teach me" + "calculate")
3. 📚 Loaded math teaching instructions
4. 🔧 Used calculator tool to do the math
5. ✅ Responded with step-by-step explanation
""")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("""
┌──────────┬────────────────────────┬─────────────────────────────┐
│ Type     │ Purpose                │ When to Use                 │
├──────────┼────────────────────────┼─────────────────────────────┤
│ Tools    │ Actions agent can take │ Agent needs to DO something │
│ Plugins  │ Modify agent behavior  │ Change HOW agent works      │
│ Skills   │ Specialized knowledge  │ Agent needs to KNOW how     │
└──────────┴────────────────────────┴─────────────────────────────┘

💡 Think of it like a person:
  • Tools = Their hands (what they can physically do)
  • Skills = Their training (what they learned)
  • Plugins = Their habits (how they behave)
""")
