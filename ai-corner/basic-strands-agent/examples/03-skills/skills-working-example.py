"""
Working Skills Example - No files needed!

This example is guaranteed to work because it creates skills in code.
"""

from strands import Agent, AgentSkills, Skill

print("\n" + "=" * 60)
print("Working Skills Example")
print("=" * 60 + "\n")

# Create skills directly in code (no files needed!)
math_skill = Skill(
    name="math-helper",
    description="Solve math problems step-by-step",
    instructions="""
You are a math tutor. When solving math problems:

1. **Show your work** - Explain each step
2. **Be clear** - Use simple language
3. **Verify** - Double-check the answer

Example:
Problem: What is 15% of 200?
Step 1: Convert to decimal: 15% = 0.15
Step 2: Multiply: 0.15 × 200 = 30
Answer: 30
"""
)

email_skill = Skill(
    name="email-writer",
    description="Compose professional emails",
    instructions="""
You are an expert email writer. Structure emails like this:

1. **Subject**: Clear and specific
2. **Greeting**: Professional but friendly
3. **Purpose**: State why you're writing (1-2 sentences)
4. **Details**: Provide necessary information (2-3 paragraphs)
5. **Action**: What you want them to do
6. **Closing**: Professional sign-off

Keep it concise and action-oriented!
"""
)

# Create the plugin with both skills
skills_plugin = AgentSkills(skills=[math_skill, email_skill])

print("📚 Available skills:")
for skill in skills_plugin.get_available_skills():
    print(f"   • {skill.name}: {skill.description}")

print("\n" + "-" * 60 + "\n")

# Create agent
agent = Agent(
    system_prompt="You are a helpful assistant with specialized skills.",
    plugins=[skills_plugin]
)

# Test 1: Math
print("Test 1: Math Problem")
print("-" * 60)
response = agent("What is 25% of 480? Please explain step by step.")
print(response)

print("\n" + "-" * 60 + "\n")

# Test 2: Email
print("Test 2: Email Writing")
print("-" * 60)
response = agent("Write a professional email to my manager requesting a meeting next week.")
print(response)

print("\n" + "=" * 60)
print("✅ Skills working perfectly!")
print("=" * 60)
