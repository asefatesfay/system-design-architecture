"""
Simple Custom Plugin #2: Conversation Counter

Counts questions and responses in the conversation.
"""

from strands import Agent
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent, AfterModelCallEvent


class ConversationCounterPlugin(Plugin):
    """
    Simple plugin that tracks conversation statistics.

    Real-world use: Monitor engagement, track conversation length, etc.
    """

    def __init__(self, name="conversation-counter"):
        """Initialize counters."""
        self._name = name  # IMPORTANT: Set name BEFORE calling super().__init__()
        super().__init__()  # Initialize base Plugin class
        self.user_questions = 0
        self.agent_responses = 0

        print("📊 ConversationCounterPlugin initialized")

    @property
    def name(self) -> str:
        """Plugin name (required by Plugin base class)."""
        return self._name

    def init_agent(self, agent: Agent) -> None:
        """Register hooks when attached to agent."""
        print("🔌 ConversationCounterPlugin connected")
        agent.add_hook(self._count_question, BeforeModelCallEvent)
        agent.add_hook(self._count_response, AfterModelCallEvent)

    def _count_question(self, event: BeforeModelCallEvent):
        """Count user questions."""
        self.user_questions += 1
        print(f"📝 Question #{self.user_questions} received")

    def _count_response(self, event: AfterModelCallEvent):
        """Count agent responses."""
        self.agent_responses += 1
        print(f"✅ Response #{self.agent_responses} sent")

    def get_stats(self) -> str:
        """Get formatted statistics."""
        return f"""
📊 Conversation Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Questions asked:    {self.user_questions}
Responses given:    {self.agent_responses}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# =============================================================================
# Usage
# =============================================================================

print("\n" + "=" * 60)
print("Conversation Counter Plugin Example")
print("=" * 60 + "\n")

# Create plugin
counter = ConversationCounterPlugin()

# Create agent with plugin
agent = Agent(
    system_prompt="You are a helpful assistant. Keep responses concise.",
    plugins=[counter]
)

# Have a conversation
print("--- Conversation Start ---\n")

agent("What is Python?")
agent("How do I install it?")
agent("What are the best practices for Python development?")

print("\n--- Conversation End ---\n")

# Show statistics
print(counter.get_stats())

print("=" * 60)
print("✅ Plugin tracked all conversation metrics!")
print("=" * 60)
