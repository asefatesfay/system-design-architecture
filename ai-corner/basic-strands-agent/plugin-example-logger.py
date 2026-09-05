"""
Example 2: Request Logger Plugin

Real-world use case: Log all user questions for analytics, debugging, or compliance.
This is useful when you need to track what users are asking your agent.
"""

from strands import Agent
from strands.hooks import BeforeModelCallEvent
import datetime


class RequestLogger:
    """Simple plugin that logs every user request."""

    def __init__(self, log_file="requests.log"):
        self.log_file = log_file
        print(f"📝 Request logger initialized: {log_file}")

    def log_request(self, event: BeforeModelCallEvent):
        """Log the user's message before the agent processes it."""
        # Get the last user message
        messages = event.messages
        if messages:
            last_message = messages[-1]
            if last_message.role == "user":
                # Extract text from the message
                text = ""
                for content in last_message.content:
                    if hasattr(content, 'text'):
                        text = content.text
                        break

                # Log to file
                timestamp = datetime.datetime.now().isoformat()
                log_entry = f"[{timestamp}] USER: {text}\n"

                with open(self.log_file, "a") as f:
                    f.write(log_entry)

                print(f"📊 Logged request: {text[:50]}...")


# Create the logger
logger = RequestLogger()

# Create agent with logger hook
agent = Agent(
    system_prompt="You are a helpful customer support agent."
)

# Register the logging hook
agent.add_hook(logger.log_request, BeforeModelCallEvent)

# Test it
print("\n" + "=" * 60)
print("Testing Request Logger Plugin")
print("=" * 60 + "\n")

response1 = agent("How do I reset my password?")
print(f"Agent: {response1}\n")

response2 = agent("What are your business hours?")
print(f"Agent: {response2}\n")

response3 = agent("I need help with my order #12345")
print(f"Agent: {response3}\n")

print("=" * 60)
print("✅ All requests logged to requests.log")
print("=" * 60)
print("\nCheck the log file:")
print("  cat requests.log")
