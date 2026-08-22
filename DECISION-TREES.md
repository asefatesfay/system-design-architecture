# Decision Trees - When to Use What

> **Practical decision frameworks** for choosing the right architecture, patterns, and technologies.

---

## Table of Contents

1. [Should I Cache This?](#should-i-cache-this)
2. [SQL vs NoSQL Decision](#sql-vs-nosql-decision)
3. [Sync vs Async Communication](#sync-vs-async-communication)
4. [When to Denormalize](#when-to-denormalize)
5. [Which Consistency Model?](#which-consistency-model)
6. [Monolith vs Microservices](#monolith-vs-microservices)
7. [Which Design Pattern?](#which-design-pattern)
8. [REST vs RPC vs GraphQL](#rest-vs-rpc-vs-graphql)
9. [When to Shard the Database](#when-to-shard-the-database)
10. [Which Message Queue?](#which-message-queue)

---

## Should I Cache This?

```
Is the data accessed frequently?
│
├─ NO → Don't cache (waste of memory)
│
└─ YES
    │
    Is it expensive to compute/fetch?
    │
    ├─ NO → Don't cache (cheaper to recompute)
    │
    └─ YES
        │
        Can you tolerate stale data?
        │
        ├─ NO → Don't cache OR cache with TTL=0
        │
        └─ YES
            │
            What's the read:write ratio?
            │
            ├─ >10:1 → ✅ Cache (Redis/Memcached)
            ├─ 5:1 to 10:1 → Cache with short TTL (10-60s)
            └─ <5:1 → Reconsider caching (invalidation cost > benefit)
```

### Examples

| Data Type | Cache? | Why |
|-----------|--------|-----|
| User profile | ✅ Yes | Read-heavy (100:1), expensive JOIN |
| User password | ❌ No | Rarely accessed, security risk |
| Product catalog | ✅ Yes | Read-heavy (1000:1), doesn't change often |
| Real-time stock price | ❌ No | Stale data = wrong decisions |
| Homepage hero image | ✅ Yes (CDN) | Same for all users, doesn't change |
| Shopping cart | ❌ No (use Redis for session) | Frequently updated |
| Search results | ✅ Yes (short TTL) | Expensive to compute, stale is OK |

**Read more:** [07-Caching](./system-design-topics/07-caching.md) • [08-Distributed Caching](./system-design-topics/08-distributed-caching.md)

---

## SQL vs NoSQL Decision

```
Do you need ACID transactions?
│
├─ YES → SQL
│   Examples: Bank accounts, orders, payments
│
└─ NO
    │
    Is your schema well-defined and stable?
    │
    ├─ YES
    │   │
    │   Do you need complex queries (JOINs)?
    │   │
    │   ├─ YES → SQL (PostgreSQL, MySQL)
    │   └─ NO → Consider NoSQL for scale
    │
    └─ NO (Schema evolves frequently)
        │
        What's your access pattern?
        │
        ├─ Key-Value → Redis, DynamoDB
        ├─ Document → MongoDB, CouchDB
        ├─ Wide-Column → Cassandra, HBase
        ├─ Graph → Neo4j, Amazon Neptune
        └─ Time-Series → InfluxDB, TimescaleDB
```

### Decision Matrix

| Factor | Use SQL | Use NoSQL |
|--------|---------|-----------|
| **Schema** | Well-defined, stable | Flexible, evolving |
| **Queries** | Complex JOINs needed | Simple lookups (key-value) |
| **Transactions** | ACID required | BASE acceptable |
| **Scale** | Vertical scaling OK (<1M RPS) | Horizontal scaling needed (>1M RPS) |
| **Relationships** | Many relationships | Denormalized OK |
| **Consistency** | Strong consistency needed | Eventual consistency OK |
| **Data Size** | <1TB | Multi-TB |

### Real-World Examples

| Use Case | Database | Why |
|----------|----------|-----|
| E-commerce orders | PostgreSQL | ACID transactions, complex queries |
| User sessions | Redis | Fast, TTL-based expiration |
| Social media feed | Cassandra | Write-heavy, eventual consistency OK |
| Product catalog | PostgreSQL | Relationships (categories, variants) |
| Real-time analytics | InfluxDB | Time-series data, high write throughput |
| User profiles | MongoDB | Schema varies by user type |
| Recommendation graph | Neo4j | Complex relationship queries |

**Read more:** [03-SQL vs NoSQL](./system-design-topics/03-sql-vs-nosql.md)

---

## Sync vs Async Communication

```
Does the caller need immediate response?
│
├─ YES
│   │
│   Can it fail?
│   │
│   ├─ NO (critical path) → Synchronous (HTTP, gRPC)
│   │   Examples: Payment, authentication
│   │
│   └─ YES (can retry) → Sync with timeout + fallback
│       Example: Recommendation service (show default if fails)
│
└─ NO (can process later)
    │
    Is ordering important?
    │
    ├─ YES → Message Queue with ordering (Kafka, RabbitMQ)
    │   Examples: Bank transactions, event sourcing
    │
    └─ NO → Async worker pool (SQS, Celery)
        Examples: Email sending, image resizing
```

### When to Use Each

| Pattern | Use When | Don't Use When | Example |
|---------|----------|----------------|---------|
| **Synchronous (HTTP)** | Need immediate response, low latency | Long-running tasks | User login, fetch profile |
| **Async (Message Queue)** | Long-running, can retry, ordering matters | Need immediate response | Order processing, payment |
| **Pub/Sub** | Multiple consumers need same event | Single consumer | User signup triggers: email + SMS + analytics |
| **WebSocket** | Real-time bidirectional | Simple request-response | Chat, collaborative editing |

**Read more:** [22-Message Queues](./system-design-topics/22-message-queues.md) • [23-WebSockets](./system-design-topics/23-websockets.md) • [25-REST vs RPC](./system-design-topics/25-rest-vs-rpc.md)

---

## When to Denormalize

```
Is the query slow due to JOINs?
│
├─ NO → Keep normalized (avoid data duplication)
│
└─ YES
    │
    Is this query in the critical path?
    │
    ├─ NO → Optimize query first (add indexes)
    │
    └─ YES (affects user experience)
        │
        How often does the denormalized data change?
        │
        ├─ Frequently (>100/sec) → Don't denormalize
        │   (Consistency issues > performance gain)
        │
        └─ Rarely (<1/min)
            │
            Can you tolerate stale data?
            │
            ├─ YES → ✅ Denormalize
            │   Batch update or use cache
            │
            └─ NO → Consider materialized views or CQRS
```

### Examples

| Scenario | Denormalize? | Solution |
|----------|--------------|----------|
| **User posts with author name** | ✅ Yes | Store author name in post (rarely changes) |
| **Product price in orders** | ✅ Yes | Store price at order time (historical accuracy) |
| **User follower count** | ✅ Yes | Increment/decrement counter (eventual consistency OK) |
| **Bank account balance** | ❌ No | Always compute from transactions (need accuracy) |
| **Real-time stock price** | ❌ No | Changes constantly, stale data = wrong decisions |

**Formula:**
```
Denormalize if: (Query Frequency × JOIN Cost) > (Write Frequency × Update Cost)
```

**Read more:** [20-Database Sharding](./system-design-topics/20-database-sharding.md)

---

## Which Consistency Model?

```
Is data correctness critical?
│
├─ YES (Financial, Inventory)
│   │
│   Can you afford higher latency?
│   │
│   ├─ YES → Strong Consistency
│   │   Database: PostgreSQL with synchronous replication
│   │
│   └─ NO → Optimistic Locking + Conflict Resolution
│       Example: Stripe payments (detect conflicts, retry)
│
└─ NO (Social, Analytics)
    │
    Can users tolerate stale data?
    │
    ├─ YES → Eventual Consistency
    │   Database: Cassandra, DynamoDB
    │   Example: Facebook feed (5-min delay OK)
    │
    └─ NO → Session Consistency
        Example: User sees their own writes immediately
```

### Consistency Spectrum

```
Strong ←─────────────────────────────────→ Eventual
  ↑                                           ↑
Bank                                      News feed
```

| Level | Read Guarantee | Use Case | Example |
|-------|----------------|----------|---------|
| **Linearizable** | Always see latest write | Bank account | Money transfers |
| **Sequential** | Sees writes in order | Messaging | Chat history |
| **Causal** | Related writes in order | Comments | Reply sees parent |
| **Eventual** | Eventually sees writes | Analytics | Page views |
| **Read-your-writes** | You see your writes | Social | Your posts visible to you |

**Read more:** [05-CAP Theorem](./system-design-topics/05-cap-theorem.md) • [06-Strong vs Eventual Consistency](./system-design-topics/06-strong-vs-eventual-consistency.md)

---

## Monolith vs Microservices

```
How many developers?
│
├─ <5 → Monolith
│   (Microservices overhead > benefits)
│
└─ >10
    │
    Are teams independent?
    │
    ├─ NO (same team owns everything) → Monolith
    │
    └─ YES
        │
        Can you handle operational complexity?
        │
        ├─ NO → Modular Monolith
        │   (Clear boundaries, single deployment)
        │
        └─ YES
            │
            Do different parts need different scaling?
            │
            ├─ YES → ✅ Microservices
            │   Example: Video upload needs 10x more servers than API
            │
            └─ NO → Consider Modular Monolith first
```

### Decision Matrix

| Factor | Monolith | Microservices |
|--------|----------|---------------|
| **Team Size** | <10 engineers | >10 engineers |
| **Scaling Needs** | Uniform scaling OK | Different services need different scale |
| **Deployment** | Deploy all at once OK | Need independent deploys |
| **Operational Maturity** | Basic monitoring OK | Need advanced observability, tracing |
| **Complexity Tolerance** | Want simple | Can handle distributed systems |
| **Data Consistency** | Need ACID | Can handle eventual consistency |

**Progression:**
```
Stage 1: Monolith (0-10 engineers)
  ↓
Stage 2: Modular Monolith (10-50 engineers)
  ↓
Stage 3: Microservices (50+ engineers)
```

**Read more:** [26-Microservices Architecture](./system-design-topics/26-microservices-architecture.md)

---

## Which Design Pattern?

### Creational Patterns (Object Creation)

```
Do you need different implementations?
│
├─ YES
│   │
│   Is construction complex (many steps)?
│   │
│   ├─ YES → Builder Pattern
│   │   Example: HTTP Request (method, headers, body, timeout...)
│   │
│   └─ NO
│       │
│       Do you know type at runtime?
│       │
│       ├─ YES → Factory Pattern
│       │   Example: Animal factory creates Dog/Cat/Bird
│       │
│       └─ NO → Abstract Factory
│           Example: UI factory creates Windows/Mac components
│
└─ NO
    │
    Need exactly ONE instance?
    │
    ├─ YES → Singleton Pattern
    │   Example: Database connection pool, config manager
    │
    └─ NO → Use regular constructor
```

### Structural Patterns (Object Composition)

```
What problem are you solving?
│
├─ Incompatible interfaces → Adapter Pattern
│   Example: Integrate third-party payment API
│
├─ Add behavior dynamically → Decorator Pattern
│   Example: Add logging, caching to function
│
├─ Simplify complex system → Facade Pattern
│   Example: Order facade hides payment/shipping/inventory
│
├─ Control access → Proxy Pattern
│   Example: Lazy-load images, cache database queries
│
└─ Share objects → Flyweight Pattern
    Example: Share font objects across documents
```

### Behavioral Patterns (Object Interaction)

```
What problem are you solving?
│
├─ Different algorithms at runtime → Strategy Pattern
│   Example: Payment methods (credit card, PayPal, crypto)
│
├─ Notify multiple objects → Observer Pattern
│   Example: YouTube notifications when video uploaded
│
├─ Behavior changes with state → State Pattern
│   Example: Traffic light (Red, Yellow, Green)
│
├─ Encapsulate request → Command Pattern
│   Example: Undo/redo in text editor
│
└─ Iterate collection → Iterator Pattern
    Example: Walk through tree structure
```

**Read more:** [LLD Design Patterns](./low-level-design/06-design-patterns/)

---

## REST vs RPC vs GraphQL

```
What's your use case?
│
├─ Public API (third-party developers)
│   → REST
│   Reason: Standardized, cacheable, stateless
│
├─ Internal microservice communication
│   │
│   Need low latency?
│   │
│   ├─ YES → gRPC (HTTP/2, binary)
│   │   Example: High-frequency trading, gaming
│   │
│   └─ NO → REST or gRPC
│       Consider team familiarity
│
├─ Frontend needs flexible queries
│   │
│   Do you control backend?
│   │
│   ├─ YES → GraphQL
│   │   Example: Mobile app with slow network
│   │
│   └─ NO → REST with field filtering
│       Example: ?fields=id,name,email
│
└─ Real-time bidirectional
    → WebSocket
    Example: Chat, collaborative editing
```

### Comparison

| Feature | REST | gRPC | GraphQL |
|---------|------|------|---------|
| **Protocol** | HTTP/1.1 | HTTP/2 | HTTP/1.1 |
| **Format** | JSON | Protocol Buffers | JSON |
| **Caching** | Built-in | Manual | Complex |
| **Streaming** | No | Yes | Yes (subscriptions) |
| **Learning Curve** | Easy | Medium | Medium |
| **Latency** | Medium | Low | Medium |
| **Overfetching** | Yes | No | No |
| **Type Safety** | No | Yes | Yes |

### When to Use Each

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| Public API | REST | Standard, cacheable, docs easy |
| Mobile app | GraphQL | Flexible, reduce overfetching |
| Microservices | gRPC | Fast, type-safe, streaming |
| Real-time chat | WebSocket | Bidirectional, low latency |
| Batch processing | REST | Simple, stateless, retryable |

**Read more:** [25-REST vs RPC](./system-design-topics/25-rest-vs-rpc.md) • [API Design Playbook](./system-design-topics/42-comprehensive-api-design-playbook.md)

---

## When to Shard the Database

```
Is your database slow?
│
├─ NO → Don't shard (premature optimization)
│
└─ YES
    │
    What's the bottleneck?
    │
    ├─ Reads → Add read replicas first
    │   (Cheaper and simpler than sharding)
    │
    └─ Writes
        │
        Is single table the bottleneck?
        │
        ├─ YES → Partition that table first
        │   (Postgres partitioning, no app changes)
        │
        └─ NO (entire DB saturated)
            │
            Can you scale vertically (bigger machine)?
            │
            ├─ YES → Scale vertically first
            │   (Simpler than sharding)
            │
            └─ NO (maxed out)
                │
                Can you accept eventual consistency?
                │
                ├─ NO → Shard carefully (complex!)
                │   Need: Two-phase commit or Saga pattern
                │
                └─ YES → ✅ Shard by natural key
                    Examples: user_id, tenant_id, region
```

### Sharding Decision Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Write QPS** | <1K | Single DB OK |
| **Write QPS** | 1K-10K | Add read replicas |
| **Write QPS** | >10K | Consider sharding |
| **Data Size** | <1TB | Single DB OK |
| **Data Size** | 1TB-10TB | Partition tables |
| **Data Size** | >10TB | Shard database |

### Sharding Strategies

| Strategy | Shard Key | Pros | Cons | Use Case |
|----------|-----------|------|------|----------|
| **Hash** | user_id | Even distribution | Hard to range query | User data |
| **Range** | timestamp | Easy range queries | Hotspots possible | Time-series |
| **Geographic** | region | Low latency | Uneven distribution | Multi-region |
| **Directory** | lookup table | Flexible | Extra hop | Complex sharding |

**Read more:** [20-Database Sharding](./system-design-topics/20-database-sharding.md) • [21-Consistent Hashing](./system-design-topics/21-consistent-hashing.md)

---

## Which Message Queue?

```
What's your priority?
│
├─ Simplicity
│   → Amazon SQS / Google Pub/Sub
│   Managed, no ops, scales automatically
│
├─ Ordering + High throughput
│   → Apache Kafka
│   Best for event streaming, logs
│
├─ Flexibility + Routing
│   → RabbitMQ
│   Complex routing, priority queues
│
└─ Speed + Simplicity
    → Redis (Lists/Streams)
    In-memory, very fast, but not durable
```

### Comparison

| Feature | Kafka | RabbitMQ | SQS | Redis |
|---------|-------|----------|-----|-------|
| **Throughput** | Very High (1M+/s) | High (50K/s) | High | Very High |
| **Ordering** | Per-partition | Per-queue | FIFO queues | Yes |
| **Durability** | Disk | Disk | Replicated | Optional |
| **Latency** | Medium (2-10ms) | Low (<1ms) | Medium (1-10ms) | Very Low (<1ms) |
| **Setup** | Complex | Medium | Managed | Simple |
| **Replay** | Yes | No | No | Yes (Streams) |

### Use Cases

| Use Case | Best Choice | Why |
|----------|-------------|-----|
| Event sourcing | Kafka | Replay, ordering, high throughput |
| Background jobs | SQS, RabbitMQ | Simple, reliable, managed |
| Rate limiting | Redis | Fast, in-memory |
| Delayed jobs | RabbitMQ | Built-in delay, priority |
| Log aggregation | Kafka | High throughput, replay |
| Email sending | SQS | Simple, retry, dead letter queue |

**Read more:** [22-Message Queues](./system-design-topics/22-message-queues.md)

---

## Quick Decision Flowchart

```
Problem → Check These First → Then Consider

Slow Response Time
├→ Measure latency breakdown
├→ Add caching
├→ Add database indexes
└→ Consider CDN for static assets

High Error Rate
├→ Add circuit breakers
├→ Implement retry with backoff
├→ Add rate limiting
└→ Improve monitoring/alerting

Can't Scale
├→ Profile bottleneck (DB? App? Network?)
├→ Add read replicas
├→ Add caching
├→ Consider sharding

Inconsistent Data
├→ Check consistency model
├→ Add transactions
├→ Implement optimistic locking
└→ Consider event sourcing

Need Real-time
├→ WebSockets for bidirectional
├→ Server-Sent Events for one-way
├→ Long polling as fallback
└→ Consider Kafka for high throughput

Need to Integrate Legacy
├→ Anti-Corruption Layer
├→ API Gateway
├→ Event-driven integration
└→ Strangler Fig pattern
```

---

## Summary

**The golden rule: Measure first, optimize second.**

Don't guess which pattern/architecture to use. Instead:
1. **Profile** - Where is time spent?
2. **Measure** - What's slow? What's failing?
3. **Decide** - Use these decision trees
4. **Test** - Did it actually improve?

**Remember:**
- **Simple > Complex** - Start simple, add complexity when needed
- **Measure > Guess** - Data beats intuition
- **Trade-offs > Perfect** - Every decision has pros and cons

---

## Next Steps

- [Complete Learning Journey](./README.md#-complete-learning-journey)
- [System Design Topics](./system-design-topics/README.md)
- [WHY System Design Matters](./WHY-SYSTEM-DESIGN-MATTERS.md)
