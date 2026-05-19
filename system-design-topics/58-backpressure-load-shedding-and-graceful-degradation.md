# Backpressure, Load Shedding, and Graceful Degradation

## Definition

**Backpressure** controls incoming work when downstream systems are saturated.
**Load shedding** intentionally drops low-priority work to preserve core availability.
**Graceful degradation** keeps critical features alive with reduced functionality.

## Key Concepts

### Backpressure Signals
- Queue length thresholds
- Consumer lag
- CPU/memory saturation
- Timeout and retry amplification

### Protection Patterns
- Bounded queues
- Admission control (reject early)
- Token buckets and concurrency limits
- Bulkheads to isolate failure domains

### Degradation Strategy
- Tier 0: critical path (must survive)
- Tier 1: important but optional
- Tier 2: nice-to-have, disable first under stress

## Real-World Examples

### Ride-Hailing Surge Event
- Matchmaking service overloads
- System rejects low-priority refresh calls
- Core ride request/accept flow preserved

### E-commerce Flash Sale
- Product recommendation service disabled temporarily
- Checkout and payment remain available
- Queue-based asynchronous email confirmations

## When to Use

- Any high-traffic or bursty workload
- Systems with strict availability targets
- Dependencies with variable latency

## Trade-offs

| Pattern | Benefit | Cost |
|--------|---------|------|
| Hard request limits | Protects core systems | Some valid requests rejected |
| Aggressive load shedding | Fast recovery | Potential UX degradation |
| Large queues | Absorb bursts | Longer tail latency |

## Implementation Tips

1. Prefer fail-fast over slow-fail under overload.
2. Apply retry budgets to avoid retry storms.
3. Distinguish user-facing errors (429) from internal errors (5xx).
4. Define feature degradation matrix before incidents.
5. Run overload tests and validate autoscaling behavior.

## Common Pitfalls

- Infinite retries without jitter/backoff
- Unbounded in-memory queues
- Shedding random traffic instead of low-priority traffic first
- No dashboards for queue saturation and rejection rates

## Related Topics

- [Rate Limiting](./10-rate-limiting.md)
- [Circuit Breaker](./12-circuit-breaker.md)
- [Message Queues](./22-message-queues.md)
- [Observability and SRE Fundamentals](./54-observability-and-sre-fundamentals.md)

## Interview Tips

- Describe overload as a normal operating scenario.
- Explain exactly what gets dropped first and why.
- Mention client behavior under 429 responses.
- Include game-day load tests in reliability plan.
