"""
Basic Skills Example - Just like plugin-basics.py

Skills are like "instruction modules" that the agent can activate on-demand.
Instead of loading all instructions upfront, they're loaded only when needed.
"""

from strands import Agent, AgentSkills, Skill

# Create a simple skill programmatically (no files needed!)
greeting_skill = Skill(
    name="greeting",
    description="Generate friendly greetings for users",
    instructions="""
You are a greeting expert. When asked to greet someone:
1. Use a warm, friendly tone
2. Personalize the greeting if you know their name
3. Add a relevant emoji
4. Keep it brief and genuine

Examples:
- "Hello Sarah! 👋 Great to see you today!"
- "Hi there! 🌟 Welcome!"
"""
)

# Create agent with the skill
agent = Agent(
    system_prompt="You are a helpful assistant.",
    plugins=[AgentSkills(skills=[greeting_skill])]
)

# Test it - the agent will activate the skill when relevant
print("=" * 60)
print("Basic Skills Example")
print("=" * 60 + "\n")

response = agent("Can you greet me? My name is Alex")
print(response)
