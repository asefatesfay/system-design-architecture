# Observability and SRE Fundamentals

## Definition

**Observability** is the ability to understand internal system state from external outputs.
Core signals are **logs, metrics, and traces**.

## Key Concepts

### Three Pillars
- Logs: detailed event records
- Metrics: numeric time-series (latency, error rate, queue depth)
- Traces: request path across distributed services

### SRE Reliability Model
- SLI: measured reliability indicator
- SLO: target for an SLI (for example p99 latency < 250 ms)
- Error budget: allowed unreliability before slowing feature rollout

### Golden Signals
- Latency
- Traffic
- Errors
- Saturation

## Real-World Examples

### API Service SLO
- SLI: successful requests / total requests
- SLO: 99.9% successful over 30 days
- Alert when burn rate threatens to exhaust error budget

### Checkout Trace
- Trace shows slowdown in payment dependency
- Metrics confirm increased upstream timeout rate
- Logs reveal TLS handshake failures after certificate change

## When to Use

- Always in production systems
- Mandatory for multi-service architectures
- Critical for on-call and incident response

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| High-cardinality metrics | Better drill-down | Storage/query cost |
| Full trace sampling | Better diagnostics | More overhead |
| Verbose logs | Better debugging | Noise and retention cost |

## Implementation Tips

1. Define SLIs/SLOs before launch, not after incidents.
2. Use structured logs (`request_id`, `user_id`, `tenant_id`, `error_code`).
3. Propagate correlation IDs across all services.
4. Use adaptive sampling for traces under high load.
5. Build runbooks linked from alerts.

## Common Pitfalls

- Alerting on symptoms that are not user-impacting
- Too many low-severity alerts (alert fatigue)
- Missing dashboards for dependencies (DB, cache, queue)
- No postmortem process after incidents

## Related Topics

- [Latency vs Throughput](./01-latency-vs-throughput.md)
- [Circuit Breaker](./12-circuit-breaker.md)
- [Heartbeat Mechanism](./13-heartbeat-mechanism.md)
- [Backpressure, Load Shedding, and Graceful Degradation](./58-backpressure-load-shedding-and-graceful-degradation.md)

## Interview Tips

- Tie reliability to user impact, not raw CPU/memory numbers.
- Explain alert thresholds using error budget burn rate.
- Mention incident loop: detect, mitigate, recover, learn.
- Show how traces + logs + metrics are correlated.
