"""
Real-World Custom Plugin #1: Cost Tracker

Tracks token usage and estimates costs for each conversation.
Essential for production to monitor API spending.
"""

from strands import Agent
from strands.plugin import Plugin
from strands.hooks import AfterModelCallEvent
from dataclasses import dataclass
from typing import Dict
import json
from pathlib import Path


@dataclass
class UsageStats:
    """Statistics for a single request."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    model: str


class CostTrackerPlugin(Plugin):
    """
    Plugin that tracks token usage and costs across conversations.

    Real-world use cases:
    - Monitor API spending per user/session
    - Alert when costs exceed threshold
    - Generate usage reports for billing
    - Budget enforcement
    """

    # Pricing per 1M tokens (as of 2024, adjust as needed)
    PRICING = {
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    }

    def __init__(
        self,
        session_id: str,
        cost_threshold: float = 10.0,
        alert_callback=None,
        stats_file: str = "usage_stats.json"
    ):
        """
        Initialize the cost tracker.

        Args:
            session_id: Unique session identifier for tracking
            cost_threshold: Alert when cumulative cost exceeds this (in dollars)
            alert_callback: Function to call when threshold is exceeded
            stats_file: File to save usage statistics
        """
        self.session_id = session_id
        self.cost_threshold = cost_threshold
        self.alert_callback = alert_callback
        self.stats_file = stats_file

        # Track cumulative stats
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.request_count = 0
        self.requests: list[UsageStats] = []

        print(f"💰 CostTrackerPlugin initialized")
        print(f"   Session: {session_id}")
        print(f"   Alert threshold: ${cost_threshold:.2f}")

    def init_agent(self, agent: Agent) -> None:
        """Register hook when plugin is attached to agent."""
        print(f"🔌 CostTrackerPlugin connected to agent")
        agent.add_hook(self._track_usage, AfterModelCallEvent)

    def _track_usage(self, event: AfterModelCallEvent):
        """Track token usage after each model call."""
        # Extract usage from event
        usage = event.usage
        if not usage:
            return

        input_tokens = getattr(usage, 'input_tokens', 0)
        output_tokens = getattr(usage, 'output_tokens', 0)
        total_tokens = input_tokens + output_tokens

        # Estimate cost (assumes Claude model for this example)
        model = "claude-3-5-sonnet"  # Default, adjust based on your model
        pricing = self.PRICING.get(model, self.PRICING["claude-3-5-sonnet"])

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        request_cost = input_cost + output_cost

        # Update cumulative stats
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += request_cost
        self.request_count += 1

        # Store this request
        stats = UsageStats(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=request_cost,
            model=model
        )
        self.requests.append(stats)

        # Log this request
        print(f"\n📊 Request #{self.request_count}")
        print(f"   Input tokens:  {input_tokens:,}")
        print(f"   Output tokens: {output_tokens:,}")
        print(f"   Cost: ${request_cost:.4f}")
        print(f"   Cumulative: ${self.total_cost:.4f}")

        # Check threshold
        if self.total_cost > self.cost_threshold:
            self._alert_threshold_exceeded()

        # Save stats to file
        self._save_stats()

    def _alert_threshold_exceeded(self):
        """Alert when cost threshold is exceeded."""
        message = f"⚠️  COST ALERT: Session {self.session_id} exceeded ${self.cost_threshold:.2f}!"
        message += f"\n   Current cost: ${self.total_cost:.2f}"
        print(f"\n{message}")

        if self.alert_callback:
            self.alert_callback(self.session_id, self.total_cost)

    def _save_stats(self):
        """Save statistics to file."""
        stats = {
            "session_id": self.session_id,
            "request_count": self.request_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost,
            "requests": [
                {
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "cost": r.estimated_cost,
                    "model": r.model
                }
                for r in self.requests
            ]
        }

        with open(self.stats_file, "w") as f:
            json.dump(stats, f, indent=2)

    def get_summary(self) -> str:
        """Get a formatted summary of usage."""
        avg_cost = self.total_cost / self.request_count if self.request_count > 0 else 0
        return f"""
📊 Cost Tracker Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session: {self.session_id}
Requests: {self.request_count}

Tokens:
  Input:  {self.total_input_tokens:,}
  Output: {self.total_output_tokens:,}
  Total:  {self.total_input_tokens + self.total_output_tokens:,}

Costs:
  Total: ${self.total_cost:.4f}
  Average per request: ${avg_cost:.4f}
  Threshold: ${self.cost_threshold:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# Example usage
def cost_alert(session_id: str, cost: float):
    """Custom alert handler."""
    print(f"\n🚨 SEND ALERT: Session {session_id} cost is ${cost:.2f}")
    # In production: send email, Slack message, log to monitoring system, etc.


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Cost Tracker Plugin Demo")
    print("=" * 60)

    # Create agent with cost tracker
    tracker = CostTrackerPlugin(
        session_id="user_123_session_456",
        cost_threshold=0.01,  # Low threshold for demo
        alert_callback=cost_alert,
        stats_file="demo_usage_stats.json"
    )

    agent = Agent(
        system_prompt="You are a helpful assistant.",
        plugins=[tracker]
    )

    # Simulate some requests
    print("\n--- Request 1 ---")
    agent("What is Python?")

    print("\n--- Request 2 ---")
    agent("Explain machine learning in simple terms.")

    print("\n--- Request 3 ---")
    agent("What are the benefits of cloud computing?")

    # Print summary
    print(tracker.get_summary())

    print("\n💾 Statistics saved to: demo_usage_stats.json")
    print("   cat demo_usage_stats.json")
