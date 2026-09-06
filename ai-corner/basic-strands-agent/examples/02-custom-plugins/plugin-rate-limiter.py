"""
Real-World Custom Plugin #2: Rate Limiter

Prevents abuse by limiting requests per user/session over time.
Essential for production APIs to control costs and prevent DoS.
"""

from strands import Agent
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, Optional
import time


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


class RateLimiterPlugin(Plugin):
    """
    Plugin that enforces rate limits on agent requests.

    Real-world use cases:
    - Prevent API abuse
    - Control costs per user
    - Fair usage across users
    - Prevent DoS attacks
    - Implement tier-based limits (free vs premium)
    """

    def __init__(
        self,
        user_id: str,
        requests_per_minute: int = 10,
        requests_per_hour: int = 100,
        burst_size: int = 5,
        strategy: str = "block"  # "block" or "delay"
    ):
        """
        Initialize the rate limiter.

        Args:
            user_id: User identifier to track
            requests_per_minute: Max requests allowed per minute
            requests_per_hour: Max requests allowed per hour
            burst_size: Allow short bursts up to this size
            strategy: "block" (reject) or "delay" (wait and proceed)
        """
        self.user_id = user_id
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        self.strategy = strategy

        # Track request timestamps
        self.request_times: deque = deque(maxlen=requests_per_hour)

        # Statistics
        self.total_requests = 0
        self.blocked_requests = 0
        self.delayed_requests = 0

        print(f"🚦 RateLimiterPlugin initialized")
        print(f"   User: {user_id}")
        print(f"   Limits: {requests_per_minute}/min, {requests_per_hour}/hour")
        print(f"   Strategy: {strategy}")

    def init_agent(self, agent: Agent) -> None:
        """Register hook when plugin is attached to agent."""
        print(f"🔌 RateLimiterPlugin connected to agent")
        agent.add_hook(self._check_rate_limit, BeforeModelCallEvent)

    def _check_rate_limit(self, event: BeforeModelCallEvent):
        """Check rate limit before each model call."""
        now = datetime.now()
        self.total_requests += 1

        # Clean old requests (older than 1 hour)
        cutoff_time = now - timedelta(hours=1)
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()

        # Check hourly limit
        if len(self.request_times) >= self.requests_per_hour:
            self._handle_limit_exceeded(
                "hour",
                self.requests_per_hour,
                self.request_times[0]
            )
            return

        # Check minute limit
        minute_ago = now - timedelta(minutes=1)
        recent_requests = sum(1 for t in self.request_times if t > minute_ago)

        if recent_requests >= self.requests_per_minute:
            self._handle_limit_exceeded(
                "minute",
                self.requests_per_minute,
                minute_ago
            )
            return

        # Check burst
        last_5_seconds = now - timedelta(seconds=5)
        burst_requests = sum(1 for t in self.request_times if t > last_5_seconds)

        if burst_requests >= self.burst_size:
            print(f"⚠️  Burst limit reached ({self.burst_size} in 5 seconds)")
            if self.strategy == "delay":
                delay = 1  # 1 second delay
                print(f"   Delaying request by {delay}s...")
                time.sleep(delay)
                self.delayed_requests += 1

        # Allow request - record timestamp
        self.request_times.append(now)
        print(f"✅ Request allowed ({recent_requests + 1}/{self.requests_per_minute} this minute)")

    def _handle_limit_exceeded(self, period: str, limit: int, oldest_request: datetime):
        """Handle when rate limit is exceeded."""
        self.blocked_requests += 1

        # Calculate when the limit will reset
        if period == "minute":
            reset_time = oldest_request + timedelta(minutes=1)
        else:  # hour
            reset_time = oldest_request + timedelta(hours=1)

        wait_seconds = (reset_time - datetime.now()).total_seconds()

        message = f"""
🚫 Rate limit exceeded for user: {self.user_id}
   Limit: {limit} requests per {period}
   Reset in: {wait_seconds:.0f} seconds
"""

        if self.strategy == "block":
            print(message)
            raise RateLimitExceeded(
                f"Rate limit exceeded: {limit} requests per {period}. "
                f"Try again in {wait_seconds:.0f} seconds."
            )
        elif self.strategy == "delay":
            print(message + f"   Strategy: Waiting {wait_seconds:.0f}s...")
            time.sleep(wait_seconds)
            self.delayed_requests += 1
            # After delay, allow the request
            self.request_times.append(datetime.now())

    def get_stats(self) -> Dict:
        """Get rate limiter statistics."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        requests_this_minute = sum(1 for t in self.request_times if t > minute_ago)

        return {
            "user_id": self.user_id,
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "delayed_requests": self.delayed_requests,
            "requests_this_minute": requests_this_minute,
            "requests_this_hour": len(self.request_times),
            "minute_limit": self.requests_per_minute,
            "hour_limit": self.requests_per_hour,
            "strategy": self.strategy
        }

    def get_summary(self) -> str:
        """Get formatted summary of rate limiter stats."""
        stats = self.get_stats()
        return f"""
🚦 Rate Limiter Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User: {stats['user_id']}
Strategy: {stats['strategy']}

Limits:
  {stats['minute_limit']} requests/minute
  {stats['hour_limit']} requests/hour

Current Usage:
  This minute: {stats['requests_this_minute']}/{stats['minute_limit']}
  This hour:   {stats['requests_this_hour']}/{stats['hour_limit']}

Statistics:
  Total requests:   {stats['total_requests']}
  Blocked:          {stats['blocked_requests']}
  Delayed:          {stats['delayed_requests']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# Example usage
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Rate Limiter Plugin Demo")
    print("=" * 60)

    # Demo 1: Block strategy (reject excess requests)
    print("\n--- DEMO 1: Block Strategy ---")
    limiter_block = RateLimiterPlugin(
        user_id="demo_user_block",
        requests_per_minute=3,  # Low limit for demo
        requests_per_hour=10,
        burst_size=2,
        strategy="block"
    )

    agent_block = Agent(
        system_prompt="You are a helpful assistant.",
        plugins=[limiter_block]
    )

    try:
        for i in range(5):
            print(f"\n--- Attempt #{i + 1} ---")
            response = agent_block(f"Request {i + 1}")
            print(f"Success: {response[:50]}...")
    except RateLimitExceeded as e:
        print(f"\n❌ {e}")

    print(limiter_block.get_summary())

    # Demo 2: Delay strategy (wait when limit reached)
    print("\n\n--- DEMO 2: Delay Strategy ---")
    limiter_delay = RateLimiterPlugin(
        user_id="demo_user_delay",
        requests_per_minute=2,
        requests_per_hour=10,
        burst_size=2,
        strategy="delay"
    )

    agent_delay = Agent(
        system_prompt="You are a helpful assistant.",
        plugins=[limiter_delay]
    )

    print("\nSending 4 rapid requests (will auto-delay when needed)...")
    for i in range(4):
        print(f"\n--- Request #{i + 1} ---")
        response = agent_delay(f"Quick request {i + 1}")
        print(f"Success: {response[:50]}...")

    print(limiter_delay.get_summary())

    # Demo 3: Tier-based limits (real-world scenario)
    print("\n\n--- DEMO 3: Tier-based Limits (Real-world) ---")

    # Different tiers
    FREE_TIER = {"requests_per_minute": 2, "requests_per_hour": 20}
    PREMIUM_TIER = {"requests_per_minute": 20, "requests_per_hour": 500}

    print("\n🆓 Free tier user:")
    free_limiter = RateLimiterPlugin(
        user_id="free_user_123",
        **FREE_TIER,
        strategy="block"
    )

    print("\n💎 Premium tier user:")
    premium_limiter = RateLimiterPlugin(
        user_id="premium_user_456",
        **PREMIUM_TIER,
        strategy="delay"
    )

    print("\n✅ Different limits applied based on user tier!")
    print(free_limiter.get_summary())
    print(premium_limiter.get_summary())
