"""
Example 3: User Context Injector Plugin

Real-world use case: Inject user information (name, role, preferences) into the agent's context.
This makes the agent personalized and aware of who it's talking to.
"""

from strands import Agent
from strands.vended_plugins.context_injector import ContextInjector
from dataclasses import dataclass


@dataclass
class UserProfile:
    """Simple user profile structure."""
    user_id: str
    name: str
    role: str
    tier: str  # e.g., "free", "premium", "enterprise"
    language: str = "en"


class UserContextManager:
    """Manages user context for the agent."""

    def __init__(self):
        # Simulate a user database
        self.users = {
            "user_123": UserProfile(
                user_id="user_123",
                name="Alice Johnson",
                role="Developer",
                tier="premium"
            ),
            "user_456": UserProfile(
                user_id="user_456",
                name="Bob Smith",
                role="Manager",
                tier="enterprise"
            ),
            "user_789": UserProfile(
                user_id="user_789",
                name="Charlie Brown",
                role="Student",
                tier="free"
            )
        }
        self.current_user = None

    def set_user(self, user_id: str):
        """Set the current user for the session."""
        self.current_user = self.users.get(user_id)
        if self.current_user:
            print(f"👤 Current user: {self.current_user.name} ({self.current_user.tier})")
        else:
            print(f"⚠️  User {user_id} not found")

    def get_user_context(self, context=None) -> str:
        """Generate user context string to inject into the agent."""
        if not self.current_user:
            return ""

        user = self.current_user

        # Format the context that will be injected
        context_text = f"""<user_context>
User Information:
- Name: {user.name}
- Role: {user.role}
- Account Tier: {user.tier}
- Language: {user.language}

Instructions:
- Address the user by name when appropriate
- Provide {user.tier}-tier features and support
- Be respectful of their {user.role} background
</user_context>"""

        return context_text


# Create the user context manager
user_manager = UserContextManager()

# Create agent with user context injector
agent = Agent(
    system_prompt="You are a helpful AI assistant. Personalize your responses based on the user context provided.",
    plugins=[
        ContextInjector(user_manager.get_user_context)
    ]
)

# Test with different users
print("\n" + "=" * 60)
print("Testing User Context Injector Plugin")
print("=" * 60 + "\n")

# Test 1: Premium user (developer)
print("\n--- Test 1: Premium Developer ---")
user_manager.set_user("user_123")
response = agent("I need help with API integration")
print(f"Agent: {response}\n")

# Test 2: Enterprise user (manager)
print("\n--- Test 2: Enterprise Manager ---")
user_manager.set_user("user_456")
response = agent("Can you explain the analytics dashboard?")
print(f"Agent: {response}\n")

# Test 3: Free tier user (student)
print("\n--- Test 3: Free Tier Student ---")
user_manager.set_user("user_789")
response = agent("What features are available to me?")
print(f"Agent: {response}\n")

print("=" * 60)
print("💡 Notice how the agent personalizes responses based on:")
print("   - User's name and role")
print("   - Account tier (free/premium/enterprise)")
print("   - Context appropriate to their background")
print("=" * 60)
