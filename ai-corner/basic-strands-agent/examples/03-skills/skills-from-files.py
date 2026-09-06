"""
Skills Example - Loading from Files

This shows how to load skills from SKILL.md files.
Skills are organized in directories and loaded automatically.
"""

from strands import Agent, AgentSkills
from strands_tools import calculator

print("=" * 60)
print("Skills from Files Example")
print("=" * 60 + "\n")

# Load all skills from the skills/ directory
# This finds all subdirectories with SKILL.md files
skills_plugin = AgentSkills(skills="./skills/")

# Create agent with skills
agent = Agent(
    system_prompt="You are a helpful assistant with specialized skills.",
    plugins=[skills_plugin],
    tools=[calculator]  # Some skills might need tools
)

# List available skills - IMPORTANT: Pass the agent!
print("📚 Available skills:")
for skill in skills_plugin.get_available_skills(agent):  # ← Pass agent here!
    print(f"   • {skill.name}: {skill.description}")

print("\n" + "-" * 60 + "\n")

# Test 1: Math problem (should activate math-helper skill)
print("Test 1: Math Problem")
print("-" * 60)
response = agent("What is 25% of 480? Please explain step by step.")
print(response)

print("\n" + "-" * 60 + "\n")

# Test 2: Email writing (should activate email-writer skill)
print("Test 2: Email Writing")
print("-" * 60)
response = agent("Write a professional email to my manager asking for a meeting next week to discuss the project timeline.")
print(response)

print("\n" + "=" * 60)
print("✅ Skills are activated automatically when relevant!")
print("=" * 60)
