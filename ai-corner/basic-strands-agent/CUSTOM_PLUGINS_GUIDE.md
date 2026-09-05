# Real-World Custom Plugins Guide

This guide explains two production-ready custom plugins that you'd actually use in real applications.

---

## Plugin 1: Cost Tracker 💰

**File:** [plugin-cost-tracker.py](plugin-cost-tracker.py)

### What it does
Tracks token usage and estimates API costs for each conversation.

### Real-world use cases

1. **Monitor spending per user/session**
   - Track costs for each customer
   - Bill customers based on actual usage
   - Identify high-cost users

2. **Budget enforcement**
   - Alert when costs exceed threshold
   - Automatically stop when budget is reached
   - Prevent runaway costs

3. **Usage analytics**
   - Generate reports for management
   - Identify optimization opportunities
   - Forecast future costs

4. **Cost attribution**
   - Track costs by department/team
   - Internal chargeback/showback
   - ROI analysis per feature

### How it works

```python
from plugin_cost_tracker import CostTrackerPlugin

# Create tracker
tracker = CostTrackerPlugin(
    session_id="user_123",
    cost_threshold=10.0,  # Alert at $10
    alert_callback=send_alert,  # Your alert function
    stats_file="usage_stats.json"
)

# Use with agent
agent = Agent(plugins=[tracker])

# After conversation, get summary
print(tracker.get_summary())
```

### Key features

- ✅ **Tracks per request**: Input tokens, output tokens, cost
- ✅ **Cumulative tracking**: Session totals across requests
- ✅ **Cost alerts**: Notifies when threshold exceeded
- ✅ **Persistent stats**: Saves to JSON file
- ✅ **Model-aware pricing**: Different rates for different models
- ✅ **Custom callbacks**: Hook into alerts for notifications

### Production deployment

```python
def send_cost_alert(session_id: str, cost: float):
    """Send alert via email/Slack when cost exceeded."""
    send_email(
        to="ops@company.com",
        subject=f"Cost Alert: Session {session_id}",
        body=f"Session exceeded budget: ${cost:.2f}"
    )

    slack_notify(
        channel="#billing-alerts",
        message=f"⚠️ Session {session_id}: ${cost:.2f}"
    )

tracker = CostTrackerPlugin(
    session_id=user_session_id,
    cost_threshold=BUDGET_LIMIT,
    alert_callback=send_cost_alert
)
```

### Stats output

```json
{
  "session_id": "user_123_session_456",
  "request_count": 3,
  "total_input_tokens": 1245,
  "total_output_tokens": 892,
  "total_cost": 0.0234,
  "requests": [
    {
      "input_tokens": 415,
      "output_tokens": 287,
      "cost": 0.0078,
      "model": "claude-3-5-sonnet"
    }
  ]
}
```

---

## Plugin 2: Rate Limiter 🚦

**File:** [plugin-rate-limiter.py](plugin-rate-limiter.py)

### What it does
Enforces request rate limits to prevent abuse and control costs.

### Real-world use cases

1. **Prevent API abuse**
   - Stop automated scraping
   - Prevent DoS attacks
   - Fair usage enforcement

2. **Cost control**
   - Limit expensive operations
   - Prevent accidental runaway costs
   - Budget compliance

3. **Tier-based limits**
   - Free: 10 requests/hour
   - Pro: 100 requests/hour
   - Enterprise: Unlimited
   - Fair usage across tiers

4. **Quality of service**
   - Prevent one user from monopolizing resources
   - Ensure availability for all users
   - Smooth out traffic spikes

### How it works

```python
from plugin_rate_limiter import RateLimiterPlugin

# Block strategy: Reject excess requests
limiter = RateLimiterPlugin(
    user_id="user_123",
    requests_per_minute=10,
    requests_per_hour=100,
    burst_size=5,
    strategy="block"  # or "delay"
)

agent = Agent(plugins=[limiter])

try:
    response = agent("Question")
except RateLimitExceeded as e:
    print(f"Rate limit: {e}")
```

### Strategies

#### Block Strategy
```python
strategy="block"
```
- **Behavior:** Reject requests that exceed limit
- **User experience:** Fast failure with clear error
- **Use when:** You want strict enforcement
- **Example:** Public API, free tier

#### Delay Strategy
```python
strategy="delay"
```
- **Behavior:** Wait until limit resets, then proceed
- **User experience:** Request completes but may be slow
- **Use when:** You want graceful handling
- **Example:** Internal tools, premium tier

### Rate limit parameters

```python
RateLimiterPlugin(
    user_id="user_123",

    # Sustained rate (prevents constant hammering)
    requests_per_minute=10,
    requests_per_hour=100,

    # Burst protection (prevents sudden spikes)
    burst_size=5,  # Max 5 requests in 5 seconds

    # How to handle violations
    strategy="block"  # or "delay"
)
```

### Tier-based implementation

```python
# Define tiers
TIERS = {
    "free": {
        "requests_per_minute": 2,
        "requests_per_hour": 20,
        "strategy": "block"
    },
    "premium": {
        "requests_per_minute": 20,
        "requests_per_hour": 500,
        "strategy": "delay"
    },
    "enterprise": {
        "requests_per_minute": 100,
        "requests_per_hour": 10000,
        "strategy": "delay"
    }
}

# Get user's tier
user_tier = get_user_tier(user_id)
tier_config = TIERS[user_tier]

# Create limiter with tier-specific limits
limiter = RateLimiterPlugin(
    user_id=user_id,
    **tier_config
)

agent = Agent(plugins=[limiter])
```

### Statistics

```python
stats = limiter.get_stats()
# {
#   "user_id": "user_123",
#   "total_requests": 45,
#   "blocked_requests": 3,
#   "delayed_requests": 2,
#   "requests_this_minute": 7,
#   "requests_this_hour": 45,
#   "minute_limit": 10,
#   "hour_limit": 100
# }
```

---

## Using Both Together 🎯

Real-world production setup combining both plugins:

```python
from plugin_cost_tracker import CostTrackerPlugin
from plugin_rate_limiter import RateLimiterPlugin

def create_agent_for_user(user_id: str, tier: str):
    """Create an agent with cost tracking and rate limiting."""

    # Tier configuration
    TIER_CONFIG = {
        "free": {
            "rate_limit": {"requests_per_minute": 2, "requests_per_hour": 20},
            "cost_threshold": 1.0  # $1 per day
        },
        "premium": {
            "rate_limit": {"requests_per_minute": 20, "requests_per_hour": 500},
            "cost_threshold": 50.0  # $50 per day
        }
    }

    config = TIER_CONFIG[tier]

    # Create plugins
    cost_tracker = CostTrackerPlugin(
        session_id=f"{user_id}_session",
        cost_threshold=config["cost_threshold"],
        alert_callback=lambda sid, cost: notify_ops(user_id, cost)
    )

    rate_limiter = RateLimiterPlugin(
        user_id=user_id,
        **config["rate_limit"],
        strategy="block" if tier == "free" else "delay"
    )

    # Create agent with both plugins
    agent = Agent(
        system_prompt="You are a helpful assistant.",
        plugins=[rate_limiter, cost_tracker]  # Order matters!
    )

    return agent, cost_tracker, rate_limiter


# Usage
agent, tracker, limiter = create_agent_for_user("user_123", "premium")

try:
    response = agent("Help me with something")
    print(response)
except RateLimitExceeded as e:
    print(f"Please wait: {e}")

# Get stats
print(tracker.get_summary())
print(limiter.get_summary())
```

---

## Plugin Architecture

Both plugins follow the same pattern:

```python
from strands.plugin import Plugin
from strands.hooks import BeforeModelCallEvent, AfterModelCallEvent

class MyCustomPlugin(Plugin):
    """Your custom plugin."""

    def __init__(self, config_param):
        """Initialize with configuration."""
        self.config = config_param

    def init_agent(self, agent: Agent) -> None:
        """Called when plugin is registered."""
        # Register hooks
        agent.add_hook(self._before_call, BeforeModelCallEvent)
        agent.add_hook(self._after_call, AfterModelCallEvent)

    def _before_call(self, event: BeforeModelCallEvent):
        """Run before model is called."""
        # Validate, log, check limits, etc.

    def _after_call(self, event: AfterModelCallEvent):
        """Run after model responds."""
        # Track usage, log results, etc.
```

### Key components

1. **`__init__`**: Accept configuration
2. **`init_agent`**: Register hooks when attached to agent
3. **Hook methods**: Implement the actual logic
4. **Stats methods**: Provide visibility into plugin state

---

## Best Practices

### 1. Plugin Ordering Matters

```python
agent = Agent(plugins=[
    rate_limiter,    # Check limits FIRST
    cost_tracker     # Track costs AFTER
])
```

Rate limiter should come first to prevent unnecessary costs.

### 2. Graceful Error Handling

```python
try:
    response = agent("Question")
except RateLimitExceeded as e:
    # User-friendly message
    return {"error": "Rate limit exceeded", "retry_after": 60}
except Exception as e:
    # Log and handle
    log_error(e)
    return {"error": "Internal error"}
```

### 3. Monitoring and Alerts

```python
# Integrate with monitoring
def alert_callback(session_id, cost):
    # Send to monitoring system
    datadog.increment('agent.cost.threshold_exceeded')
    datadog.gauge('agent.cost.total', cost)

    # Alert team
    pagerduty.trigger_alert(
        severity="warning",
        description=f"Cost threshold exceeded: ${cost}"
    )
```

### 4. Persistence

```python
# Save stats regularly
cost_tracker._save_stats()

# Load stats on restart
def load_existing_stats(session_id):
    stats_file = f"{session_id}_stats.json"
    if Path(stats_file).exists():
        with open(stats_file) as f:
            return json.load(f)
    return None
```

---

## Testing

### Test Cost Tracker

```python
def test_cost_tracker():
    tracker = CostTrackerPlugin(
        session_id="test",
        cost_threshold=0.01  # Low for testing
    )

    agent = Agent(plugins=[tracker])

    # Make some requests
    agent("Test 1")
    agent("Test 2")

    # Check stats
    stats = tracker.get_stats()
    assert stats["request_count"] == 2
    assert stats["total_cost"] > 0
```

### Test Rate Limiter

```python
def test_rate_limiter():
    limiter = RateLimiterPlugin(
        user_id="test",
        requests_per_minute=2,
        strategy="block"
    )

    agent = Agent(plugins=[limiter])

    # First 2 should succeed
    agent("Request 1")
    agent("Request 2")

    # Third should fail
    with pytest.raises(RateLimitExceeded):
        agent("Request 3")
```

---

## Next Steps

1. ✅ Run both examples: `python plugin-cost-tracker.py` and `python plugin-rate-limiter.py`
2. ✅ Combine them together in your own agent
3. ✅ Customize thresholds and limits for your use case
4. ✅ Add monitoring/alerting integration
5. ✅ Deploy to production with proper error handling

---

## Summary

| Plugin | Purpose | Hook | Production Ready |
|--------|---------|------|------------------|
| Cost Tracker | Monitor API spending | AfterModelCallEvent | ✅ Yes |
| Rate Limiter | Prevent abuse | BeforeModelCallEvent | ✅ Yes |

Both plugins are production-ready and used in real-world applications! 🚀
