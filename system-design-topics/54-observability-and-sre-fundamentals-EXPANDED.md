# Observability and SRE Fundamentals - Complete Guide

> **"You can't fix what you can't see."**
>
> Comprehensive guide to monitoring, alerting, and operating distributed systems at scale.

---

## Table of Contents

1. [The Three Pillars of Observability](#the-three-pillars-of-observability)
2. [Logs - Events in Time](#logs---events-in-time)
3. [Metrics - Numbers Over Time](#metrics---numbers-over-time)
4. [Traces - Request Journey](#traces---request-journey)
5. [Putting It All Together](#putting-it-all-together)
6. [SRE Fundamentals](#sre-fundamentals)
7. [SLIs, SLOs, and SLAs](#slis-slos-and-slas)
8. [Alerting Strategy](#alerting-strategy)
9. [Debugging Production Issues](#debugging-production-issues)
10. [Tools and Tech Stack](#tools-and-tech-stack)

---

## The Three Pillars of Observability

```
Observability = Logs + Metrics + Traces

Why three?
- Logs: Tell you WHAT happened
- Metrics: Tell you HOW MUCH happened
- Traces: Tell you WHERE it happened (across services)
```

### When to Use Each

| Question | Tool | Example |
|----------|------|---------|
| Why is checkout slow? | **Traces** | Follow request through 10 microservices |
| Is error rate increasing? | **Metrics** | Graph of errors/sec over time |
| What caused this error? | **Logs** | Stack trace, request context |
| Which service is the bottleneck? | **Traces** | See 80% of time spent in payment service |
| Is the database slow? | **Metrics** | Query latency p99 increasing |
| What data caused the crash? | **Logs** | Request payload in error log |

---

## Logs - Events in Time

### What are Logs?

**Individual events** that happened in your system:
- User logged in
- Payment failed
- Database query slow
- Exception thrown

### Structured Logs

```json
{
  "timestamp": "2026-08-22T14:30:00.123Z",
  "level": "ERROR",
  "service": "payment-service",
  "request_id": "abc-123-def",
  "user_id": "user-456",
  "endpoint": "/api/payments",
  "method": "POST",
  "status_code": 500,
  "latency_ms": 5234,
  "error": "Stripe timeout after 5s",
  "error_type": "TimeoutError",
  "stack_trace": "...",
  "payment_amount": 99.99,
  "currency": "USD"
}
```

**Why structured (JSON) over plain text?**
- ✅ Easy to query: `level:ERROR AND service:payment-service`
- ✅ Easy to parse: Automatic field extraction
- ✅ Easy to aggregate: Count errors by service
- ❌ Plain text: Hard to parse, slow to search

### Log Levels

```
TRACE   → Detailed debug info (rarely enabled)
DEBUG   → Diagnostic info (dev only)
INFO    → General informational messages
WARN    → Potential problems
ERROR   → Errors that need attention
FATAL   → Application is crashing
```

**Production:**
- API servers: INFO level
- Background jobs: DEBUG level (more verbose OK)
- Critical services: WARN level (reduce noise)

### Correlation IDs

**Problem:** How to trace a request across 10 microservices?

**Solution:** Correlation ID (request ID)

```python
# API Gateway generates correlation ID
import uuid

@app.before_request
def add_correlation_id():
    request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    g.request_id = request_id

# Log with correlation ID
logger.info({
    'request_id': g.request_id,  # ← Same ID across all services
    'message': 'Processing payment',
    'user_id': user_id
})

# Pass to downstream services
headers = {'X-Request-ID': g.request_id}
response = requests.post('http://payment-service/charge', headers=headers)
```

**Now you can find all logs for a single request:**
```
GET /logs?request_id=abc-123-def
→ Returns logs from API Gateway, Auth Service, Payment Service, Notification Service
```

### Context Logging

**Bad:**
```python
logger.error("Payment failed")  # ❌ No context!
```

**Good:**
```python
logger.error({
    'message': 'Payment failed',
    'request_id': request_id,
    'user_id': user_id,
    'payment_amount': 99.99,
    'payment_method': 'credit_card',
    'error': str(e),
    'stripe_response_code': response.status_code
})
```

### Sensitive Data in Logs

**Never log:**
- ❌ Passwords
- ❌ Credit card numbers
- ❌ API keys
- ❌ Social Security Numbers
- ❌ Personal health information

**How to avoid:**
```python
def sanitize_log(data):
    """Remove sensitive fields before logging"""
    sensitive_fields = ['password', 'ssn', 'credit_card']
    return {k: v if k not in sensitive_fields else '[REDACTED]'
            for k, v in data.items()}

logger.info(sanitize_log(user_data))
```

### Log Aggregation

**Problem:** 100 servers, each with local logs. How to search?

**Solution:** Centralized logging (ELK Stack, Loki, CloudWatch)

```
Application Servers (100 instances)
    ↓ (forward logs)
Logstash/Fluentd (aggregator)
    ↓ (index)
Elasticsearch (storage + search)
    ↓ (visualize)
Kibana (UI)
```

### Example: ELK Stack Setup

```yaml
# docker-compose.yml
version: '3'
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

```python
# Python app sends logs to Logstash
import logstash
import logging

logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler('localhost', 5000, version=1))

logger.info('Payment processed', extra={'user_id': '123', 'amount': 99.99})
```

### Log Retention

**Storage is expensive!**

**Strategy:**
```
Hot storage (fast, expensive):
  - Last 7 days: Full logs in Elasticsearch

Warm storage (slower, cheaper):
  - 8-30 days: Compressed logs in S3

Cold storage (slowest, cheapest):
  - 31-365 days: Archived in Glacier

Delete after 1 year (unless required by law)
```

**Cost example:**
- 1TB logs/day × 30 days = 30TB
- Elasticsearch: $500/TB/month = $15,000/month
- S3: $23/TB/month = $690/month
- Glacier: $4/TB/month = $120/month

---

## Metrics - Numbers Over Time

### What are Metrics?

**Aggregated numbers** measured over time:
- Requests per second
- Error rate
- Latency (p50, p95, p99)
- CPU usage
- Memory usage
- Queue depth

### Types of Metrics

**1. Counter** - Always increases
```python
requests_total.inc()  # Total requests served
errors_total.inc()    # Total errors
```

**2. Gauge** - Goes up and down
```python
active_connections.set(42)  # Current connections
memory_usage.set(75)        # Current memory %
queue_depth.set(100)        # Current queue size
```

**3. Histogram** - Bucketed observations
```python
request_duration.observe(0.123)  # 123ms
# Automatically buckets into: <10ms, <50ms, <100ms, <500ms, <1s, >1s
```

**4. Summary** - Like histogram but calculates percentiles
```python
request_latency.observe(0.123)
# Calculates: p50, p95, p99
```

### The RED Method (for Requests)

**Monitor these for every service:**

**R**ate - Requests per second
```promql
rate(http_requests_total[5m])
```

**E**rrors - Error rate
```promql
rate(http_errors_total[5m]) / rate(http_requests_total[5m])
```

**D**uration - Latency (p95, p99)
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### The USE Method (for Resources)

**Monitor these for infrastructure:**

**U**tilization - % of resource used
```promql
100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])))
```

**S**aturation - Queue depth, contention
```promql
node_load5  # Load average (should be < CPU count)
```

**E**rrors - Error count
```promql
rate(node_network_receive_errs_total[5m])
```

### Example: Prometheus Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s  # Scrape metrics every 15s

scrape_configs:
  - job_name: 'api-servers'
    static_configs:
      - targets:
        - api-1:9090
        - api-2:9090
        - api-3:9090

  - job_name: 'databases'
    static_configs:
      - targets:
        - postgres-1:9187
        - postgres-2:9187
```

```python
# Expose metrics in your app
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
requests_total = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    # Record metrics
    duration = time.time() - g.start_time
    request_duration.observe(duration)
    requests_total.labels(method=request.method, endpoint=request.path).inc()
    return response

# Start metrics server on port 9090
start_http_server(9090)
```

### Key Metrics to Monitor

**Application Metrics:**
- Request rate (RPS)
- Error rate (%)
- Latency (p50, p95, p99)
- Active connections
- Queue depth
- Cache hit rate

**Infrastructure Metrics:**
- CPU usage (%)
- Memory usage (%)
- Disk I/O (IOPS, throughput)
- Network I/O (bytes/sec)
- Disk space (% full)

**Database Metrics:**
- Query latency
- Connection pool usage
- Cache hit rate
- Replication lag
- Slow queries (>1s)

**Business Metrics:**
- Orders per minute
- Revenue per hour
- Active users
- Conversion rate

---

## Traces - Request Journey

### What is Distributed Tracing?

**Follow a single request** as it travels through multiple services.

```
User Request → API Gateway → Auth → Payment → Notification → Email
   (10ms)        (5ms)       (50ms)   (200ms)     (30ms)      (100ms)
                                        ↑
                                   Bottleneck!
```

### Trace Structure

```
Trace (end-to-end request)
  └─ Span (single operation)
      ├─ Span ID
      ├─ Parent Span ID
      ├─ Service name
      ├─ Operation name
      ├─ Start time
      ├─ Duration
      └─ Tags/Logs
```

### Example: OpenTelemetry (Python)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

@app.route('/checkout')
def checkout():
    # Start span for this operation
    with tracer.start_as_current_span("checkout"):
        user_id = request.args.get('user_id')

        # Child span for auth
        with tracer.start_as_current_span("authenticate"):
            user = authenticate(user_id)

        # Child span for payment
        with tracer.start_as_current_span("process_payment") as span:
            span.set_attribute("payment.amount", 99.99)
            span.set_attribute("payment.method", "credit_card")
            payment_result = process_payment(user)

        # Child span for notification
        with tracer.start_as_current_span("send_notification"):
            send_email(user.email, "Order confirmed")

        return {'status': 'success'}
```

**Result in Jaeger UI:**
```
checkout (total: 385ms)
  ├─ authenticate (50ms)
  ├─ process_payment (200ms)  ← Slowest!
  │   ├─ validate_card (10ms)
  │   ├─ charge_stripe (180ms)  ← Real bottleneck
  │   └─ update_db (10ms)
  └─ send_notification (135ms)
      ├─ render_email (5ms)
      └─ smtp_send (130ms)
```

### Context Propagation

**Problem:** How do child services know they're part of the same trace?

**Solution:** Pass trace context in HTTP headers

```python
# Parent service
with tracer.start_as_current_span("call_payment_service") as span:
    # Get trace context
    context = span.get_span_context()

    # Pass in headers
    headers = {
        'traceparent': f'00-{context.trace_id}-{context.span_id}-01'
    }

    response = requests.post('http://payment-service/charge', headers=headers)

# Child service extracts trace context
from opentelemetry.propagate import extract

@app.before_request
def extract_trace_context():
    # Extract parent trace context from headers
    ctx = extract(request.headers)
    # This span will be child of parent span
```

### Sampling

**Problem:** Tracing every request is expensive (network, storage)

**Solution:** Sample traces

**Strategies:**
1. **Head-based sampling** (decide at start)
   ```python
   # Sample 1% of all requests
   if random.random() < 0.01:
       start_trace()
   ```

2. **Tail-based sampling** (decide at end)
   ```python
   # Only keep traces with errors or >1s latency
   if had_error or duration > 1.0:
       keep_trace()
   else:
       discard_trace()
   ```

3. **Adaptive sampling**
   ```python
   # Sample more during errors, less during normal operation
   if error_rate > 0.05:
       sample_rate = 0.1  # 10%
   else:
       sample_rate = 0.01  # 1%
   ```

---

## Putting It All Together

### Scenario: "Checkout is slow"

**Step 1: Check Metrics** (Is it really slow?)
```promql
# Query Prometheus
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{endpoint="/checkout"}[5m]))
# Result: p99 = 5.2s (normally 500ms)
# ✅ Confirmed: Checkout is slow
```

**Step 2: Find Affected Requests** (Traces)
```
# Query Jaeger: Show me slow traces
duration > 3s AND service = checkout-service
# Result: 1247 slow traces in last hour
# Click one to see details
```

**Step 3: Identify Bottleneck** (Traces)
```
Trace shows:
  checkout (5.2s total)
    ├─ validate_cart (10ms)
    ├─ check_inventory (4.9s)  ← 94% of time!
    │   └─ database_query (4.8s)  ← Actual bottleneck
    └─ create_order (300ms)
```

**Step 4: Find Root Cause** (Logs)
```
# Query Elasticsearch for slow queries
GET /logs?service=inventory-service AND latency_ms>1000 AND time>now-1h

Result:
{
  "query": "SELECT * FROM inventory WHERE product_id IN (...1000 items...)",
  "duration_ms": 4823,
  "error": "Missing index on product_id"
}
```

**Step 5: Fix**
```sql
-- Add missing index
CREATE INDEX idx_inventory_product_id ON inventory(product_id);

-- After fix:
-- p99 latency: 5.2s → 450ms ✅
```

---

## SRE Fundamentals

### What is SRE?

**Site Reliability Engineering** - Google's approach to operations

**Key principles:**
1. **Treat operations as a software problem**
2. **Error budgets** (acceptable downtime)
3. **Automate toil** (repetitive manual work)
4. **Measure everything**

### Error Budget

**Concept:** If SLO is 99.9% uptime, you have 0.1% error budget

**Math:**
```
99.9% uptime = 43 minutes downtime per month allowed

Error budget spent:
- 10 min outage on Monday
- 15 min outage on Wednesday
- 18 min remaining for the month

If error budget exhausted:
- Freeze feature launches
- Focus on reliability
- Investigate root causes
```

### Toil

**Definition:** Repetitive, manual, automatable work

**Examples of toil:**
- Manually restarting crashed services
- Manually scaling servers
- Manually deploying code
- Manually running database queries

**Goal:** Reduce toil to <50% of time

**How:**
- Automate deployments (CI/CD)
- Auto-scaling based on metrics
- Auto-remediation (restart on crash)
- Self-service tools for developers

---

## SLIs, SLOs, and SLAs

### Definitions

**SLI** (Service Level Indicator) - Measurement
```
Examples:
- Request success rate
- Request latency (p99)
- System uptime
```

**SLO** (Service Level Objective) - Target
```
Examples:
- 99.9% of requests succeed
- 99% of requests < 500ms (p99)
- 99.95% uptime
```

**SLA** (Service Level Agreement) - Contract
```
Example:
- If uptime < 99.9%, customer gets refund
- Binding legal agreement
```

### Setting SLOs

**Bad SLO:**
```
❌ "System should be fast"  (Not measurable)
❌ "99.999% uptime"  (Too aggressive, expensive)
```

**Good SLO:**
```
✅ "99.9% of API requests return success (2xx/3xx) over a 30-day window"
✅ "99% of API requests complete in <500ms (p99) over a 30-day window"
```

### Example SLOs by Service Type

**Public API:**
- Availability: 99.9% (43 min downtime/month)
- Latency: p99 < 1s
- Error rate: <0.1%

**Internal Service:**
- Availability: 99.5% (3.6 hours downtime/month)
- Latency: p99 < 2s
- Error rate: <1%

**Batch Job:**
- Completion rate: 99.9%
- Completion time: 95% within SLA time
- Data loss: 0%

### Calculating SLO Compliance

```python
def calculate_slo_compliance(period_days=30):
    """
    Calculate if we met our SLO
    """
    total_requests = 10_000_000
    successful_requests = 9_990_000
    success_rate = successful_requests / total_requests

    slo_target = 0.999  # 99.9%

    if success_rate >= slo_target:
        print(f"✅ SLO met: {success_rate:.5f} >= {slo_target}")
        error_budget_remaining = (success_rate - slo_target) * total_requests
        print(f"Error budget remaining: {error_budget_remaining:.0f} errors")
    else:
        print(f"❌ SLO violated: {success_rate:.5f} < {slo_target}")
        error_budget_deficit = (slo_target - success_rate) * total_requests
        print(f"Error budget deficit: {error_budget_deficit:.0f} errors")

# Output:
# ✅ SLO met: 0.99900 >= 0.99900
# Error budget remaining: 0 errors
```

---

## Alerting Strategy

### Symptom vs Cause Alerts

**Bad (Cause Alert):**
```
❌ "Disk usage on server-3 is 85%"
→ Why do I care? Is it affecting users?
```

**Good (Symptom Alert):**
```
✅ "p99 latency >1s for 5 minutes"
→ Clear impact: Users experiencing slow response
```

### Alert Severity Levels

**P0 - Critical** (Page on-call immediately)
- Complete outage
- Data loss
- Security breach
- SLO burn rate >10x

**P1 - High** (Page during business hours)
- Partial outage
- SLO burn rate >5x
- Key features broken

**P2 - Medium** (Ticket for next business day)
- Minor degradation
- SLO burn rate >2x
- Non-critical features broken

**P3 - Low** (No alert, log only)
- Informational
- Capacity planning
- Optimization opportunities

### Alerting Best Practices

**1. Alert on symptoms, not causes**
```yaml
# ❌ Bad
alert: DiskUsageHigh
expr: disk_usage > 85%

# ✅ Good
alert: APILatencyHigh
expr: histogram_quantile(0.99, rate(http_request_duration[5m])) > 1.0
```

**2. Include runbook in alerts**
```yaml
alert: APILatencyHigh
expr: ...
annotations:
  summary: "API p99 latency is {{ $value }}s"
  runbook: https://wiki.company.com/runbooks/api-latency
  description: |
    Check:
    1. Database slow queries
    2. Cache hit rate
    3. Downstream service latency
```

**3. Set appropriate thresholds**
```yaml
# Alert if burning through error budget 10x faster than normal
alert: ErrorBudgetBurnRateHigh
expr: |
  (
    sum(rate(http_errors[5m])) / sum(rate(http_requests[5m]))
  ) > (10 * (1 - 0.999))  # 10x SLO error rate
for: 5m
```

**4. Avoid alert fatigue**
```python
# ❌ Bad: Alert on every error
if error:
    send_alert()

# ✅ Good: Alert on error rate increase
if error_rate > threshold and error_rate > baseline * 2:
    send_alert()
```

### Example: Prometheus Alerting Rules

```yaml
# alerts.yml
groups:
  - name: api_alerts
    rules:
      # P0 - Critical
      - alert: APIDown
        expr: up{job="api-servers"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API server {{ $labels.instance }} is down"
          runbook_url: https://wiki/runbooks/api-down

      # P1 - High
      - alert: HighErrorRate
        expr: |
          rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Error rate is {{ $value | humanizePercentage }}"

      # P2 - Medium
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "p99 latency is {{ $value }}s"
```

---

## Debugging Production Issues

### The Debugging Process

**1. Identify** (What's wrong?)
- Check alerts
- Check dashboards
- Check recent deployments

**2. Triage** (How bad?)
- How many users affected?
- Is it getting worse?
- What's the business impact?

**3. Mitigate** (Stop the bleeding)
- Rollback deployment
- Scale up resources
- Enable circuit breakers
- Redirect traffic

**4. Investigate** (Why did it happen?)
- Check metrics (when did it start?)
- Check traces (where is bottleneck?)
- Check logs (what errors?)

**5. Fix** (Resolve root cause)
- Deploy fix
- Verify fix
- Monitor closely

**6. Postmortem** (Prevent recurrence)
- Write postmortem
- Action items
- Update runbooks

### Example: Debugging High Latency

```bash
# Step 1: Confirm the issue (Metrics)
curl "http://prometheus/api/v1/query?query=histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))"
# Result: 5.2s (normally 0.5s)

# Step 2: When did it start? (Metrics)
# Look at graph → Started 30 minutes ago

# Step 3: What changed? (Logs)
curl "http://kibana/api?query=level:INFO AND deployed:true AND timestamp>now-1h"
# Result: Deployment of payment-service v2.3.1 at 14:00

# Step 4: Is it specific to one service? (Traces)
curl "http://jaeger/api/traces?service=checkout&lookback=1h&minDuration=1s"
# Result: All slow traces involve payment-service

# Step 5: What's slow in payment-service? (Traces)
# Click trace → 4.8s spent in database_query

# Step 6: What query? (Logs)
curl "http://elasticsearch/logs?service=payment-service AND query_time>1000"
# Result: SELECT * FROM transactions WHERE user_id IN (...1000 IDs...)

# Step 7: Mitigate - Rollback deployment
kubectl rollout undo deployment/payment-service

# Step 8: Verify fix
# Check metrics → Latency back to normal within 2 minutes

# Step 9: Root cause
# Code review: v2.3.1 changed query to fetch 1000 records (N+1 query)
# Proper fix: Optimize query, add index

# Step 10: Postmortem
# - What: N+1 query introduced in v2.3.1
# - Impact: 30 min outage, p99 latency 10x higher
# - Resolution: Rollback, then deploy fix with optimized query
# - Action items:
#   1. Add load testing to CI/CD
#   2. Add query performance monitoring
#   3. Code review checklist for N+1 queries
```

### Common Issues and Solutions

| Symptom | Possible Causes | How to Debug |
|---------|----------------|--------------|
| **High latency** | Slow DB query, N+1 query, external API timeout | Check traces, slow query log |
| **High error rate** | Bug in code, external dependency down, rate limiting | Check logs for error messages |
| **High CPU** | Infinite loop, inefficient algorithm, no caching | Profile with pprof, check hot paths |
| **High memory** | Memory leak, caching too much, not closing connections | Check heap dump, connection pool |
| **Timeouts** | Slow dependency, no timeout set, resource exhaustion | Check traces, connection pool usage |

---

## Tools and Tech Stack

### Logs

| Tool | Pros | Cons | Use When |
|------|------|------|----------|
| **ELK Stack** | Powerful search, open source | Complex setup, expensive | Large scale, need flexibility |
| **Loki** | Simple, cheap, Grafana integration | Limited search | Kubernetes, cost-sensitive |
| **CloudWatch** | Managed, AWS integration | Expensive, slow search | AWS-only infrastructure |
| **DataDog** | All-in-one, easy setup | Expensive | Want turnkey solution |

### Metrics

| Tool | Pros | Cons | Use When |
|------|------|------|----------|
| **Prometheus** | Open source, powerful queries | Need to manage | Self-hosted, flexible queries |
| **DataDog** | All-in-one, APM included | Expensive | Want managed solution |
| **CloudWatch** | Managed, AWS integration | Limited queries | AWS infrastructure |
| **Graphite** | Simple, mature | Aging, no labels | Legacy systems |

### Traces

| Tool | Pros | Cons | Use When |
|------|------|------|----------|
| **Jaeger** | Open source, battle-tested | Need to manage | Self-hosted, cost-sensitive |
| **Zipkin** | Open source, simple | Fewer features | Simple use cases |
| **DataDog APM** | All-in-one, auto-instrumentation | Expensive | Want managed solution |
| **AWS X-Ray** | Managed, AWS integration | AWS-only | AWS infrastructure |

### All-in-One Solutions

| Tool | Pricing | Best For |
|------|---------|----------|
| **DataDog** | $$$$$ | Enterprises, want everything |
| **New Relic** | $$$$$ | APM-focused, Ruby/Node apps |
| **Honeycomb** | $$$$ | Modern observability, traces |
| **Grafana Cloud** | $$$ | Open source tools, managed |

---

## Real-World Examples

### Netflix

**Scale:** 200M+ users, 15K microservices

**Observability Stack:**
- Metrics: Atlas (custom)
- Logs: ELK + custom tools
- Traces: Mantis (custom)
- Chaos: Chaos Monkey

**Key learnings:**
- Built custom tools for massive scale
- Chaos engineering in production
- Automated remediation

### Uber

**Scale:** 100M+ users, 4K microservices

**Observability Stack:**
- Metrics: Prometheus + M3
- Logs: ELK
- Traces: Jaeger
- All in open source

**Key learnings:**
- Open source at scale
- Contributed Jaeger to CNCF
- Heavy investment in automation

### Stripe

**Scale:** Process $640B/year

**Observability:**
- Comprehensive logging (PCI compliant)
- Real-time fraud detection
- 99.999% uptime SLA

**Key learnings:**
- Observability for compliance
- Real-time alerting critical
- Invest in runbooks

---

## Key Takeaways

1. **Three Pillars** - Logs (what), Metrics (how much), Traces (where)
2. **Correlation IDs** - Track requests across services
3. **Structured Logs** - JSON logs are queryable
4. **RED Method** - Rate, Errors, Duration for every service
5. **SLOs over SLAs** - Focus on user experience
6. **Alert on Symptoms** - Not on causes
7. **Error Budgets** - Balance speed and stability
8. **Automate Toil** - Reduce repetitive work
9. **Runbooks** - Document how to fix issues
10. **Postmortems** - Learn from incidents

---

## Next Steps

1. **Add observability to your project**
   - Logs: Add structured logging
   - Metrics: Expose Prometheus metrics
   - Traces: Add OpenTelemetry

2. **Set up dashboards**
   - RED dashboard for your service
   - Infrastructure dashboard (USE method)

3. **Define SLOs**
   - What matters to users?
   - What's realistic?

4. **Create runbooks**
   - How to debug common issues?
   - Who to contact?

5. **Practice incident response**
   - Run game days
   - Test runbooks
   - Improve alerting

---

**Related Topics:**
- [Testing Guide](../TESTING-DISTRIBUTED-SYSTEMS.md)
- [55-Multi-Region DR](./55-multi-region-and-disaster-recovery.md)
- [Hands-On Labs](../hands-on-labs/)

**Congratulations!** You now understand how to observe and operate distributed systems at scale. 🎉

