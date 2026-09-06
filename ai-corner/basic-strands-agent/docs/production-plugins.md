# Production Plugins Guide

This guide covers production-ready plugins that you can use in real applications.

---

## Overview

| Plugin | Purpose | Impact | Difficulty |
|--------|---------|--------|------------|
| [Audit Logger](#audit-logger) | Compliance & Security | Legal requirement | ⭐⭐ |
| [Response Cache](#response-cache) | Cost & Performance | -30-50% costs | ⭐⭐⭐ |
| Cost Tracker | Monitoring | Budget control | ⭐⭐ |
| Rate Limiter | Protection | Prevent abuse | ⭐⭐⭐ |

---

## Audit Logger Plugin 🔒

**File:** [examples/02-custom-plugins/plugin-audit-logger.py](../examples/02-custom-plugins/plugin-audit-logger.py)

### What It Does

Logs all user queries and agent responses with full metadata for compliance, security, and debugging.

### Key Features

- ✅ **Structured Logging** - JSON or CSV format
- ✅ **PII Redaction** - Automatically redact emails, phones, SSN, credit cards
- ✅ **Metadata Tracking** - User ID, session ID, timestamps
- ✅ **Integrity Hashing** - Verify log integrity
- ✅ **Multiple Formats** - JSON for parsing, CSV for reporting

### Use Cases

#### Healthcare (HIPAA Compliance)
```python
logger = AuditLoggerPlugin(
    log_dir="./hipaa_logs",
    format="json",
    redact_pii=True,  # Required for HIPAA
    user_id=patient_id,
    session_id=visit_id,
    metadata={"facility": "hospital_123", "provider": "dr_smith"}
)
```

#### Financial Services
```python
logger = AuditLoggerPlugin(
    log_dir="./audit_logs",
    format="json",
    user_id=customer_id,
    session_id=transaction_id,
    metadata={"department": "loans", "agent": "bot_v2"}
)
```

#### Enterprise SaaS
```python
logger = AuditLoggerPlugin(
    log_dir="./logs",
    format="csv",  # Easy to import into Excel/BI tools
    redact_pii=True,
    user_id=user_email,
    metadata={"tenant": org_id, "app_version": "2.1.0"}
)
```

### Example Output

**JSON format:**
```json
{
  "timestamp": "2026-09-06T14:30:45.123456",
  "event_type": "user_query",
  "user_id": "user_12345",
  "session_id": "session_abc",
  "content": "My email is [EMAIL_REDACTED]",
  "content_hash": "a1b2c3d4e5f6",
  "redacted": true,
  "metadata": {"app": "support", "version": "1.0"}
}
```

### PII Redaction

Automatically redacts:
- Email addresses → `[EMAIL_REDACTED]`
- Phone numbers → `[PHONE_REDACTED]`
- Social Security Numbers → `[SSN_REDACTED]`
- Credit card numbers → `[CC_REDACTED]`

```python
# Before: "My email is john@example.com and phone is 555-1234"
# After:  "My email is [EMAIL_REDACTED] and phone is [PHONE_REDACTED]"
```

### Configuration

```python
AuditLoggerPlugin(
    log_dir="./audit_logs",        # Where to store logs
    format="json",                  # "json" or "csv"
    redact_pii=True,               # Enable PII redaction
    user_id="user_123",            # User identifier
    session_id="session_456",      # Session identifier
    metadata={                      # Custom metadata
        "app": "customer_support",
        "version": "1.0"
    }
)
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Compliance** | GDPR, HIPAA, SOC2 ready |
| **Security** | Track unauthorized access |
| **Debugging** | Reproduce user issues |
| **Analytics** | Understand user behavior |
| **Legal** | Evidence for disputes |

### Best Practices

1. **Always redact PII in production**
   ```python
   redact_pii=True  # For healthcare, finance, EU users
   ```

2. **Include rich metadata**
   ```python
   metadata={
       "tenant_id": org_id,
       "user_role": role,
       "app_version": version
   }
   ```

3. **Use JSON for programmatic access**
   ```python
   format="json"  # For log aggregation tools
   ```

4. **Use CSV for reporting**
   ```python
   format="csv"  # For Excel, BI tools
   ```

5. **Rotate logs regularly**
   - Daily/weekly rotation
   - Archive old logs
   - Set retention policies

---

## Response Cache Plugin 💾

**File:** [examples/02-custom-plugins/plugin-response-cache.py](../examples/02-custom-plugins/plugin-response-cache.py)

### What It Does

Caches agent responses to reduce API calls, costs, and latency for repeated queries.

### Key Features

- ✅ **Multiple Backends** - Memory (fast) or File (persistent)
- ✅ **Configurable TTL** - Set cache expiration time
- ✅ **LRU Eviction** - Automatic memory management
- ✅ **Statistics** - Hit rate, tokens saved, cost savings
- ✅ **Smart Keys** - Hash-based deduplication

### Use Cases

#### FAQ Bot
```python
cache = ResponseCachePlugin(
    backend="memory",
    ttl=86400,  # 24 hours - FAQs don't change often
    max_size=500  # Store top 500 questions
)

# Common questions get cached
# "What are your hours?" asked 100x → 99 cache hits
# Saves: 99 API calls!
```

#### Documentation Assistant
```python
cache = ResponseCachePlugin(
    backend="file",  # Persistent across restarts
    ttl=3600,  # 1 hour - docs update occasionally
    cache_dir="./doc_cache"
)

# "How do I install X?" repeated queries cached
# Even after server restart, cache survives
```

#### High-Traffic Application
```python
cache = ResponseCachePlugin(
    backend="memory",
    ttl=300,  # 5 minutes - fresher responses
    max_size=10000  # Large cache for traffic
)

# 10,000 requests/hour
# 40% hit rate = 4,000 saved API calls
# At $0.01 per call = $40/hour saved = $960/day!
```

### Cache Backends

#### Memory Backend (Fast)
```python
backend="memory"
```
- ✅ Fastest (in-memory)
- ✅ LRU eviction
- ❌ Lost on restart
- **Use when:** Speed > persistence

#### File Backend (Persistent)
```python
backend="file"
```
- ✅ Survives restarts
- ✅ Can inspect cached data
- ❌ Slightly slower (disk I/O)
- **Use when:** Persistence > speed

### Configuration

```python
ResponseCachePlugin(
    backend="memory",              # or "file"
    ttl=3600,                      # 1 hour cache lifetime
    max_size=1000,                 # Max entries (memory only)
    cache_dir="./response_cache",  # Cache dir (file only)
    enabled=True                   # Can disable for testing
)
```

### How It Works

1. **User asks question**
2. **Generate cache key** - Hash of normalized query
3. **Check cache** - If found, use cached response
4. **On miss** - Call API, cache response

```python
# First time: "What is Python?"
# → Cache MISS → Call API → Cache response

# Second time: "What is Python?"
# → Cache HIT → Return cached → No API call!

# Slight variation: "what is python?" (lowercase)
# → Cache HIT → Normalized to same key
```

### Cost Savings Example

```python
# Scenario: 1,000 requests/day, 40% cache hit rate

cache_hits = 400 per day
api_calls_saved = 400
tokens_per_call = 1,000
cost_per_1k_tokens = $0.01

daily_savings = 400 * (1000 / 1000) * $0.01 = $4/day
monthly_savings = $4 * 30 = $120/month
yearly_savings = $120 * 12 = $1,440/year
```

### Statistics

```python
stats = cache.get_stats()
# {
#   'cache_hits': 400,
#   'cache_misses': 600,
#   'total_requests': 1000,
#   'hit_rate': 40.0,
#   'tokens_saved': 400000,
#   'estimated_savings': 4.00
# }
```

### Best Practices

1. **Choose TTL based on content freshness**
   ```python
   ttl=86400   # 24h for stable content (FAQs)
   ttl=3600    # 1h for semi-stable (docs)
   ttl=300     # 5min for dynamic content
   ```

2. **Use file backend for production**
   ```python
   backend="file"  # Survives restarts
   ```

3. **Monitor hit rate**
   ```python
   # Aim for >30% hit rate for cost savings
   # <20% = cache not helping much
   # >50% = great cache performance
   ```

4. **Size cache appropriately**
   ```python
   # Memory: max_size based on unique queries
   max_size=1000  # Small app
   max_size=10000 # Medium app
   max_size=100000 # Large app
   ```

5. **Clear cache when needed**
   ```python
   cache.clear_cache()  # After data updates
   ```

---

## Combining Both Plugins

Use together for complete production solution:

```python
from plugin_audit_logger import AuditLoggerPlugin
from plugin_response_cache import ResponseCachePlugin

# Audit all requests (compliance)
audit = AuditLoggerPlugin(
    log_dir="./audit",
    format="json",
    redact_pii=True,
    user_id=user_id
)

# Cache responses (cost savings)
cache = ResponseCachePlugin(
    backend="file",
    ttl=3600
)

agent = Agent(
    plugins=[
        cache,  # Cache first (saves money)
        audit   # Then audit (compliance)
    ]
)
```

**Order matters!** Cache should come before audit to avoid logging cached hits unnecessarily.

---

## Production Checklist

### For Audit Logger:
- [ ] Enable PII redaction for sensitive data
- [ ] Set up log rotation/archival
- [ ] Include user_id and session_id
- [ ] Add app metadata (version, tenant)
- [ ] Test log parsing in your log system
- [ ] Define retention policy
- [ ] Set up alerts for errors

### For Response Cache:
- [ ] Choose backend (file for production)
- [ ] Set appropriate TTL
- [ ] Size cache for your traffic
- [ ] Monitor hit rate (aim for >30%)
- [ ] Set up cache warming for common queries
- [ ] Plan cache invalidation strategy
- [ ] Track cost savings

---

## Real-World Examples

### Healthcare App
```python
# HIPAA-compliant audit + cache for performance
audit = AuditLoggerPlugin(
    log_dir="/secure/audit",
    format="json",
    redact_pii=True,  # Required
    user_id=patient_mrn,
    metadata={"facility": facility_id}
)

cache = ResponseCachePlugin(
    backend="file",
    ttl=300,  # 5min - medical info changes
    cache_dir="/secure/cache"
)
```

### SaaS Platform
```python
# Multi-tenant with caching
audit = AuditLoggerPlugin(
    log_dir=f"./logs/{tenant_id}",
    user_id=user_id,
    metadata={"tenant": tenant_id, "plan": user_plan}
)

cache = ResponseCachePlugin(
    backend="memory",
    ttl=3600,  # 1 hour
    max_size=5000
)
```

### FAQ Bot
```python
# High cache hit rate
cache = ResponseCachePlugin(
    backend="file",
    ttl=86400,  # 24 hours
)

# Simple audit
audit = AuditLoggerPlugin(
    log_dir="./logs",
    format="csv"  # For reporting
)
```

---

## Monitoring

### Audit Logger Metrics
- Logs written per day
- PII redactions per day
- Log file sizes
- Errors during logging

### Response Cache Metrics
- Hit rate (target: >30%)
- Tokens saved per day
- Cost savings ($$)
- Cache size/memory usage

---

## Troubleshooting

### Audit Logger

**Problem:** Logs too large
**Solution:** Enable log rotation, compress old logs

**Problem:** PII still visible
**Solution:** Check `redact_pii=True`, add custom patterns

**Problem:** Can't parse logs
**Solution:** Use JSON format, validate schema

### Response Cache

**Problem:** Low hit rate (<20%)
**Solution:** Increase TTL, check query variations

**Problem:** Stale responses
**Solution:** Decrease TTL, implement cache invalidation

**Problem:** Cache too large
**Solution:** Reduce max_size, decrease TTL

---

## Summary

| Plugin | Essential For | ROI |
|--------|--------------|-----|
| Audit Logger | Compliance, Security | Legal protection |
| Response Cache | Cost, Performance | 30-50% cost reduction |

**Both together = Complete production solution!** 🎉

---

## Next Steps

1. Run examples:
   ```bash
   python plugin-audit-logger.py
   python plugin-response-cache.py
   ```

2. Customize for your needs
3. Deploy to production
4. Monitor metrics
5. Adjust configuration based on data

---

See complete code:
- [plugin-audit-logger.py](../examples/02-custom-plugins/plugin-audit-logger.py)
- [plugin-response-cache.py](../examples/02-custom-plugins/plugin-response-cache.py)
