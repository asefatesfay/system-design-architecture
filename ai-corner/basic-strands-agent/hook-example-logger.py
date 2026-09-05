"""
Example 2A: Request Logger using HOOKS (not a plugin)

This shows how to use hooks directly without creating a plugin.
"""

from strands import Agent
from strands.hooks import BeforeModelCallEvent
import datetime


class RequestLogger:
    """Simple logger using hooks."""

    def __init__(self, log_file="requests.log"):
        self.log_file = log_file
        print(f"📝 Request logger initialized: {log_file}")

    def log_request(self, event: BeforeModelCallEvent):
        """Hook function that logs the user's message."""
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


# Create the logger
logger = RequestLogger()

# Create agent
agent = Agent(
    system_prompt="You are a helpful customer support agent."
)

# Register the hook directly (NOT using plugins parameter)
agent.add_hook(logger.log_request, BeforeModelCallEvent)

# Test it
print("\n" + "=" * 60)
print("Testing HOOK-based Request Logger")
print("=" * 60 + "\n")

response = agent("How do I reset my password?")
print(f"Agent: {response}\n")

print("=" * 60)
print("✅ This uses HOOKS, not plugins!")
print("   - Registered with: agent.add_hook()")
print("   - Event: BeforeModelCallEvent")
print("=" * 60)
