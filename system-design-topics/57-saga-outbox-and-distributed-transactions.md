# Saga, Outbox, and Distributed Transactions

## Definition

A **distributed transaction** spans multiple services/datastores.
Instead of global locks/2PC everywhere, many systems use:
- **Saga**: sequence of local transactions with compensations
- **Outbox pattern**: atomically store business change + event in one DB transaction

## Key Concepts

### Why Not Global 2PC by Default
- Coordinator bottleneck
- Higher latency and lock contention
- Fragile under partial failures

### Saga Styles
- Orchestration: central coordinator decides next step
- Choreography: services react to events without central coordinator

### Outbox + CDC
- Service writes business row + outbox row in same local transaction
- CDC/relay publishes outbox events to broker
- Prevents "DB committed but event lost" failures

## Real-World Examples

### Travel Booking Saga
1. Reserve flight
2. Reserve hotel
3. Reserve car
4. If step 3 fails, compensate 1 and 2 (cancel)

### Order Service Outbox
- Local transaction writes `orders` and `outbox_events`
- Relay publishes `OrderCreated`
- Consumer retries safely with idempotency key

## When to Use

- Cross-service workflows with eventual consistency
- Need reliable event publication from transactional data
- Business can define compensation logic

## Trade-offs

| Pattern | Benefit | Cost |
|--------|---------|------|
| 2PC | Strong atomicity | Throughput and availability penalties |
| Saga | Better resilience/scalability | Compensation complexity |
| Outbox | Reliable publication | Extra relay/CDC component |

## Implementation Tips

1. Design compensating actions before coding the happy path.
2. Make all handlers idempotent (`operation_id`, dedupe table).
3. Include saga state machine with explicit terminal states.
4. Add timeouts/escalation for stuck steps.
5. Use outbox cleanup with retention windows.

## Common Pitfalls

- No compensation path for irreversible side effects
- Hidden side effects inside read APIs
- Replaying outbox without dedupe protections
- Treating saga completion as immediate consistency

## Related Topics

- [ACID Transactions](./02-acid-transactions.md)
- [Message Queues](./22-message-queues.md)
- [Event-Driven Architecture and Pub/Sub](./56-event-driven-architecture-and-pubsub.md)
- [Idempotency](./11-idempotency.md)

## Interview Tips

- Start with invariants and what must be eventually true.
- Explain where atomicity is local vs global.
- Show failure flow, not only success flow.
- Mention observability for saga progress and stuck transactions.
