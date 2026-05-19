# Event-Driven Architecture and Pub/Sub

## Definition

**Event-driven architecture (EDA)** uses events to asynchronously communicate state changes.
**Publish/Subscribe (Pub/Sub)** lets publishers emit events without direct coupling to consumers.

## Key Concepts

### Event Basics
- Event: immutable fact (for example `OrderPlaced`)
- Command: intent to do work (for example `PlaceOrder`)
- Event schema versioning for compatibility

### Delivery Semantics
- At-most-once: may lose messages
- At-least-once: may deliver duplicates
- Exactly-once: usually "effectively once" with idempotency + transactions

### Ordering and Replay
- Ordering is often per partition key, not global
- Replay enables rebuilding materialized views
- Dead-letter queues isolate poison messages

## Real-World Examples

### E-commerce Order Flow
- `OrderPlaced` published once
- Inventory, payment, notification services consume independently
- Failed notification goes to DLQ; order remains valid

### Analytics Pipeline
- Clickstream events flow through Kafka topics
- Stream processor enriches and writes to warehouse
- Historical replay reprocesses with new business logic

## When to Use

- Decoupling many producers/consumers
- High-throughput asynchronous workflows
- Event sourcing and audit-heavy systems

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Async decoupling | Better scalability/resilience | Higher eventual consistency complexity |
| Rich event schemas | Better downstream utility | Schema governance overhead |
| Long event retention | Replay and audit | Storage cost |

## Implementation Tips

1. Use idempotent consumers and dedupe keys.
2. Choose partition keys based on ordering needs.
3. Version schemas with backward-compatible changes first.
4. Add DLQ and retry policy with max attempts.
5. Track consumer lag and rebalance events.

## Common Pitfalls

- Treating events as mutable shared objects
- Assuming global ordering guarantees
- Unbounded retries causing retry storms
- Breaking schema compatibility across teams

## Related Topics

- [Message Queues](./22-message-queues.md)
- [Batch vs Stream Processing](./24-batch-vs-stream-processing.md)
- [Idempotency](./11-idempotency.md)
- [Saga, Outbox, and Distributed Transactions](./57-saga-outbox-and-distributed-transactions.md)

## Interview Tips

- Clarify command vs event boundaries.
- Discuss out-of-order and duplicate handling early.
- Mention observability: lag, throughput, processing failure rate.
- Explain how replay changes architecture decisions.
