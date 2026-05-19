# Data Modeling and Schema Evolution

## Definition

**Data modeling** designs data structures based on access patterns and consistency needs.
**Schema evolution** changes those structures safely over time without breaking clients.

## Key Concepts

### Modeling for Access Patterns
- Query-first design: model by reads/writes, not by abstract entities only
- Normalize for integrity, denormalize for performance where needed
- Partition keys should align with high-volume access paths

### Schema Compatibility
- Backward compatible: new producer works with old consumers
- Forward compatible: old producer works with new consumers
- Full compatible: both directions

### Migration Strategy
- Expand and contract pattern
- Dual-write or backfill during transitions
- Versioned contracts for external APIs/events

## Real-World Examples

### Add Required Field Safely
1. Add nullable field first
2. Deploy writers to populate it
3. Backfill old data
4. Enforce non-null constraint later

### Event Schema Upgrade
- Add optional field `currency` to payment event
- Consumers default to `USD` if missing
- Old and new events can coexist safely

## When to Use

- Any long-lived production system
- Multi-team schemas and shared datasets
- APIs/events with external consumers

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Strict normalized schema | Data consistency | Potential join-heavy reads |
| Denormalized read model | Fast queries | Duplication/update complexity |
| Frequent schema versions | Faster product iteration | Consumer migration overhead |

## Implementation Tips

1. Track schema versions in metadata and dashboards.
2. Use migration jobs that are resumable and idempotent.
3. Roll out in phases: read compatibility before write enforcement.
4. Keep old fields until all consumers are upgraded.
5. Add data quality checks before and after migration.

## Common Pitfalls

- Breaking change deployed without compatibility window
- Backfill without throttling causing production impact
- Ignoring historical data shape differences
- Missing ownership for schema contracts

## Related Topics

- [SQL vs NoSQL](./03-sql-vs-nosql.md)
- [Database Index](./04-database-index.md)
- [Database Sharding](./20-database-sharding.md)
- [Event-Driven Architecture and Pub/Sub](./56-event-driven-architecture-and-pubsub.md)

## Interview Tips

- Start from access patterns and scale estimates.
- Explain online migration with zero downtime.
- Mention rollback and dual-read/dual-write options.
- Include validation metrics for migration correctness.
