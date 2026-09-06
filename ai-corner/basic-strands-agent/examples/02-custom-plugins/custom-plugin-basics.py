"""
Simple Custom Plugin Example - Just like plugin-basics.py

This shows how to create your own plugin from scratch.
A plugin is just a class that hooks into the agent's lifecycle.
"""

from strands import Agent
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent, AfterModelCallEvent


class SimpleGreetingPlugin(Plugin):
    """
    A simple plugin that adds a greeting before each response.

    This is the minimal structure for a custom plugin.
    """

    def __init__(self, greeting_style="friendly", name="simple-greeting"):
        """Initialize the plugin with configuration."""
        self._name = name  # IMPORTANT: Set name BEFORE calling super().__init__()
        super().__init__()  # Initialize base Plugin class
        self.greeting_style = greeting_style
        self.request_count = 0
        print(f"👋 SimpleGreetingPlugin initialized ({greeting_style} style)")

    @property
    def name(self) -> str:
        """Plugin name (required by Plugin base class)."""
        return self._name

    def init_agent(self, agent: Agent) -> None:
        """
        Called when the plugin is attached to an agent.
        This is where you register your hooks.
        """
        print("🔌 Plugin connected to agent")

        # Register hooks for before and after model calls
        agent.add_hook(self._before_call, BeforeModelCallEvent)
        agent.add_hook(self._after_call, AfterModelCallEvent)

    def _before_call(self, event: BeforeModelCallEvent):
        """Called before the model processes the request."""
        self.request_count += 1
        print(f"\n📨 Request #{self.request_count} - Processing...")

    def _after_call(self, event: AfterModelCallEvent):
        """Called after the model responds."""
        print(f"✅ Response #{self.request_count} completed!")


# =============================================================================
# Usage - Just like plugin-basics.py!
# =============================================================================

print("\n" + "=" * 60)
print("Simple Custom Plugin Example")
print("=" * 60 + "\n")

# Create the plugin
my_plugin = SimpleGreetingPlugin(greeting_style="friendly")

# Create agent with the plugin
agent = Agent(
    system_prompt="You are a helpful and friendly assistant.",
    plugins=[my_plugin]
)

# Test it
print("\n--- Test 1 ---")
response = agent("What's the capital of France?")
print(f"Agent: {response}")

print("\n--- Test 2 ---")
response = agent("What's 2 + 2?")
print(f"Agent: {response}")

print("\n" + "=" * 60)
print("✅ Custom plugin working!")
print(f"   Total requests: {my_plugin.request_count}")
print("=" * 60)
