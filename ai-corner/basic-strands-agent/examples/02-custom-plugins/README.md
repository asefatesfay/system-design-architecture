# 02-custom-plugins: Build Your Own

Learn to create custom plugins from scratch, from simple examples to production-ready implementations.

## Files

### Learning Examples

#### custom-plugin-basics.py ⭐ **START HERE**
- **What:** Create your first custom plugin
- **Learns:** Plugin structure, `name` property, `init_agent()`
- **Time:** 15 minutes
- **Run:** `python custom-plugin-basics.py`

#### custom-plugin-counter.py
- **What:** Track conversation statistics
- **Learns:** Event data, state management, reporting
- **Time:** 15 minutes
- **Run:** `python custom-plugin-counter.py`

### Production-Ready Examples 🏭

#### plugin-audit-logger.py 🔒 **PRODUCTION**
- **What:** Complete audit logging for compliance
- **Features:**
  - Structured JSON/CSV logging
  - PII redaction (emails, phones, SSN)
  - Metadata tracking (user_id, session_id)
  - GDPR/HIPAA compliance ready
- **Use cases:** Healthcare, finance, enterprise SaaS
- **Time:** 20 minutes
- **Run:** `python plugin-audit-logger.py`

#### plugin-response-cache.py 💾 **PRODUCTION**
- **What:** Response caching to reduce costs 30-50%
- **Features:**
  - Multiple backends (memory, file)
  - Configurable TTL
  - Cache hit/miss statistics
  - Cost savings tracking
- **Use cases:** FAQ bots, documentation, high-traffic apps
- **Time:** 20 minutes
- **Run:** `python plugin-response-cache.py`

#### plugin-cost-tracker.py 💰 **PRODUCTION**
- **What:** Track token usage and estimate costs
- **Features:**
  - Real-time cost tracking
  - Budget alerts
  - Per-request statistics
  - JSON export
- **Use cases:** Cost monitoring, budget enforcement
- **Time:** 20 minutes
- **Run:** `python plugin-cost-tracker.py`

#### plugin-rate-limiter.py 🚦 **PRODUCTION**
- **What:** Limit requests per user/session
- **Features:**
  - Block or delay strategies
  - Burst protection
  - Tier-based limits
  - Statistics tracking
- **Use cases:** Prevent abuse, cost control, fair usage
- **Time:** 20 minutes
- **Run:** `python plugin-rate-limiter.py`

---

## Quick Start

```bash
# Learn the basics
python custom-plugin-basics.py

# Try production examples
python plugin-audit-logger.py
python plugin-response-cache.py
```

---

## Plugin Template

Use this template for your own plugins:

```python
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent

class MyPlugin(Plugin):
    def __init__(self, name="my-plugin"):
        self._name = name
        super().__init__()
        # Your initialization

    @property
    def name(self) -> str:
        return self._name

    def init_agent(self, agent) -> None:
        agent.add_hook(self._hook, BeforeModelCallEvent)

    def _hook(self, event):
        # Your logic here
        pass
```

---

## Production Plugin Comparison

| Plugin | Purpose | Cost Impact | Complexity |
|--------|---------|-------------|------------|
| Audit Logger | Compliance | None | ⭐⭐ |
| Response Cache | Performance | -30-50% | ⭐⭐⭐ |
| Cost Tracker | Monitoring | None | ⭐⭐ |
| Rate Limiter | Protection | Prevent abuse | ⭐⭐⭐ |

---

## Which Plugin Do I Need?

### For Compliance/Security:
✅ **Audit Logger** - Track all conversations
- Healthcare (HIPAA)
- Finance (regulatory)
- Enterprise (security audits)

### For Cost Savings:
✅ **Response Cache** - Reduce API calls 30-50%
- FAQ bots
- High-traffic apps
- Repeated queries

### For Monitoring:
✅ **Cost Tracker** - Track spending
- Budget enforcement
- Usage analytics
- Per-user costs

### For Protection:
✅ **Rate Limiter** - Prevent abuse
- Public APIs
- Free tiers
- DoS protection

---

## Combining Plugins

Use multiple plugins together:

```python
from plugin_audit_logger import AuditLoggerPlugin
from plugin_response_cache import ResponseCachePlugin
from plugin_cost_tracker import CostTrackerPlugin
from plugin_rate_limiter import RateLimiterPlugin

agent = Agent(
    plugins=[
        RateLimiterPlugin(requests_per_minute=10),  # Prevent abuse
        ResponseCachePlugin(ttl=3600),              # Save costs
        CostTrackerPlugin(threshold=10.0),          # Monitor spending
        AuditLoggerPlugin(redact_pii=True)          # Compliance
    ]
)
```

**Order matters!** Rate limiter should be first, cache second.

---

## Concepts Learned

### Basic Examples
- ✅ Custom plugin structure (3 required parts)
- ✅ Hook registration
- ✅ Event handling
- ✅ State management
- ✅ Configuration patterns

### Production Examples
- ✅ Error handling
- ✅ Multiple backends
- ✅ Statistics tracking
- ✅ File I/O
- ✅ Configuration flexibility
- ✅ Real-world patterns

---

## Common Plugin Patterns

### Pattern 1: Tracking/Logging
```python
# Before/After hooks to log activity
agent.add_hook(self._before, BeforeModelCallEvent)
agent.add_hook(self._after, AfterModelCallEvent)
```

### Pattern 2: Caching/Optimization
```python
# Check cache before, store after
agent.add_hook(self._check_cache, BeforeModelCallEvent)
agent.add_hook(self._store_cache, AfterModelCallEvent)
```

### Pattern 3: Validation/Control
```python
# Validate before, raise if needed
agent.add_hook(self._validate, BeforeModelCallEvent)
# raise SomeException if validation fails
```

---

## Testing Your Plugin

```python
def test_my_plugin():
    plugin = MyPlugin()
    agent = Agent(plugins=[plugin])

    # Test
    agent("test query")

    # Verify
    assert plugin.count == 1
```

---

## Next Steps

After mastering custom plugins, move to:
- [../03-skills/](../03-skills/) - Learn about skills
- [../../docs/custom-plugins.md](../../docs/custom-plugins.md) - Deep dive

---

## Resources

- **Templates:** See code above
- **Docs:** [../../docs/custom-plugins.md](../../docs/custom-plugins.md)
- **Examples:** All files in this folder

---

**Ready to build?** Start with [custom-plugin-basics.py](custom-plugin-basics.py)!
