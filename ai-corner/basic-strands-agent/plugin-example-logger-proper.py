"""
Example 2B: Request Logger as a proper PLUGIN

This shows how to create a reusable plugin that can be passed in the plugins parameter.
"""

from strands import Agent
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent
import datetime


class RequestLoggerPlugin(Plugin):
    """Proper plugin that logs user requests."""

    def __init__(self, log_file="requests.log"):
        self.log_file = log_file
        print(f"📝 RequestLoggerPlugin initialized: {log_file}")

    def init_agent(self, agent: Agent) -> None:
        """Called when plugin is registered with an agent."""
        print(f"🔌 RequestLoggerPlugin connected to agent")
        # Register our hook when the plugin is initialized
        agent.add_hook(self._log_request, BeforeModelCallEvent)

    def _log_request(self, event: BeforeModelCallEvent):
        """Internal hook function that logs the user's message."""
        messages = event.messages
        if messages:
            last_message = messages[-1]
            if last_message.role == "user":
                text = ""
                for content in last_message.content:
                    if hasattr(content, 'text'):
                        text = content.text
                        break

                timestamp = datetime.datetime.now().isoformat()
                log_entry = f"[{timestamp}] USER: {text}\n"

                with open(self.log_file, "a") as f:
                    f.write(log_entry)

                print(f"📊 Logged request: {text[:50]}...")


# Create agent WITH the plugin (passed in plugins parameter)
agent = Agent(
    system_prompt="You are a helpful customer support agent.",
    plugins=[RequestLoggerPlugin("plugin_requests.log")]  # ← Plugin passed here!
)

# Test it
print("\n" + "=" * 60)
print("Testing PLUGIN-based Request Logger")
print("=" * 60 + "\n")

response = agent("How do I reset my password?")
print(f"Agent: {response}\n")

print("=" * 60)
print("✅ This is a PROPER PLUGIN!")
print("   - Passed in: Agent(plugins=[...])")
print("   - Implements: Plugin.init_agent()")
print("   - Reusable: Can use with any agent")
print("=" * 60)
