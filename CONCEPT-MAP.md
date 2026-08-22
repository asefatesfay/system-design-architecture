# Concept Map - How Everything Connects

> **Learning is not linear.** This map shows how concepts build on each other and when you need to understand one concept before learning another.

---

## Learning Dependency Graph

### Level 1: Foundation (Start Here)

```
OOP Fundamentals
├── Classes & Objects
├── Four Pillars (Encapsulation, Abstraction, Inheritance, Polymorphism)
└── SOLID Principles
     │
     └──> Enables Level 2 Design Patterns
```

**Learn first:** [Low-Level Design](./low-level-design/)

---

### Level 2: Design Patterns

```
Creational Patterns
├── Factory (object creation)
├── Singleton (one instance)
└── Builder (step-by-step construction)
     │
     ├──> Becomes Service Discovery at scale
     └──> Becomes Leader Election (distributed Singleton)

Structural Patterns
├── Adapter (interface compatibility)
├── Decorator (add behavior)
├── Facade (simplify complexity)
└── Proxy (control access)
     │
     ├──> Proxy → Load Balancer (system design)
     ├──> Decorator → Middleware/Interceptors
     └──> Facade → API Gateway

Behavioral Patterns
├── Strategy (swap algorithms)
├── Observer (notify subscribers)
└── State (behavior by state)
     │
     ├──> Strategy → Cache Eviction Policies
     ├──> Observer → Pub/Sub, Event-Driven Architecture
     └──> State → Saga Pattern (distributed transactions)
```

**Learn next:** [Design Patterns](./low-level-design/06-design-patterns/)

---

### Level 3: System Design Fundamentals

```
Performance Basics
│
├── Latency vs Throughput
│    │
│    ├──> Understand before learning Caching
│    └──> Understand before learning Load Balancing
│
└── CAP Theorem
     │
     ├──> Explains why Eventual Consistency exists
     ├──> Explains why Multi-Region is hard
     └──> Foundation for all distributed systems
```

---

## The Caching Chain

```
Problem: Slow response times
    ↓
01. Latency vs Throughput
    (Understand the metrics)
    ↓
07. Caching Basics
    (Cache-aside, write-through)
    ↓
08. Distributed Caching
    (Redis, Memcached)
    ↓
Cache Invalidation Problem
    ↓
21. Consistent Hashing
    (Route cache requests evenly)
    ↓
Scale Further
    ↓
20. Database Sharding
    (When caching isn't enough)
```

**Path:**
1. [01-Latency vs Throughput](./system-design-topics/01-latency-vs-throughput.md)
2. [07-Caching](./system-design-topics/07-caching.md)
3. [08-Distributed Caching](./system-design-topics/08-distributed-caching.md)
4. [21-Consistent Hashing](./system-design-topics/21-consistent-hashing.md)
5. [20-Database Sharding](./system-design-topics/20-database-sharding.md)

---

## The Reliability Chain

```
Problem: Service failures cascade
    ↓
10. Rate Limiting
    (Protect single service)
    ↓
12. Circuit Breaker
    (Prevent cascading failures)
    ↓
Anti-Pattern: Retry Storm
    (What happens without circuit breaker)
    ↓
11. Idempotency
    (Make retries safe)
    ↓
57. Saga Pattern
    (Reliable distributed transactions)
    ↓
55. Multi-Region + Disaster Recovery
    (Regional failures)
```

**Path:**
1. [10-Rate Limiting](./system-design-topics/10-rate-limiting.md)
2. [12-Circuit Breaker](./system-design-topics/12-circuit-breaker.md)
3. [06-Retry Storm Anti-pattern](./anti-patterns/06-retry-storm/)
4. [11-Idempotency](./system-design-topics/11-idempotency.md)
5. [57-Saga Pattern](./system-design-topics/57-saga-outbox-and-distributed-transactions.md)
6. [55-Multi-Region DR](./system-design-topics/55-multi-region-and-disaster-recovery.md)

---

## The Scaling Chain

```
1 User → 1K Users → 1M Users → 1B Users

Stage 1: Single Server
├── Bottleneck: Everything
└── Solution: None needed yet
     ↓
Stage 2: Add Caching
├── 07. Caching
├── 08. Distributed Caching
└── Bottleneck: Database reads
     ↓
Stage 3: Read Scaling
├── 09. Load Balancing (app servers)
├── 18. Data Replication (DB replicas)
└── Bottleneck: Database writes
     ↓
Stage 4: Write Scaling
├── 17. Database Scaling (vertical)
├── 20. Database Sharding (horizontal)
└── 21. Consistent Hashing (partition)
     ↓
Stage 5: Global Scale
├── 16. CDN (static assets)
├── 55. Multi-Region (low latency globally)
└── 28. Consensus Algorithms (coordination)
```

**Path:**
1. Start: [WHY System Design Matters](./WHY-SYSTEM-DESIGN-MATTERS.md)
2. [07-Caching](./system-design-topics/07-caching.md)
3. [09-Load Balancing](./system-design-topics/09-load-balancing.md)
4. [18-Data Replication](./system-design-topics/18-data-replication.md)
5. [20-Database Sharding](./system-design-topics/20-database-sharding.md)
6. [55-Multi-Region DR](./system-design-topics/55-multi-region-and-disaster-recovery.md)

---

## The Data Chain

```
Understanding Data Storage
    ↓
02. ACID Transactions
    (Strong consistency guarantees)
    ↓
03. SQL vs NoSQL
    (Which database for which problem?)
    ↓
04. Database Index
    (Make queries fast)
    ↓
17. Database Scaling
    (Vertical vs Horizontal)
    ↓
     ├──> Read Scaling
     │    ├── 18. Data Replication
     │    └── 19. Data Redundancy
     │
     └──> Write Scaling
          ├── 20. Database Sharding
          └── 21. Consistent Hashing
               ↓
          Advanced: Consistency Trade-offs
               ├── 05. CAP Theorem
               ├── 06. Strong vs Eventual Consistency
               └── 59. Schema Evolution
```

**Path:**
1. [02-ACID Transactions](./system-design-topics/02-acid-transactions.md)
2. [03-SQL vs NoSQL](./system-design-topics/03-sql-vs-nosql.md)
3. [04-Database Index](./system-design-topics/04-database-index.md)
4. [17-Database Scaling](./system-design-topics/17-database-scaling.md)
5. [18-Data Replication](./system-design-topics/18-data-replication.md)
6. [20-Database Sharding](./system-design-topics/20-database-sharding.md)

---

## The Communication Chain

```
How Services Talk
    ↓
25. REST vs RPC
    (Synchronous communication)
    ↓
Problem: Tight coupling, cascading failures
    ↓
22. Message Queues
    (Async communication, decoupling)
    ↓
Problem: Need real-time
    ↓
23. WebSockets
    (Bidirectional, real-time)
    ↓
Scale to microservices
    ↓
26. Microservices Architecture
    ↓
Need single entry point
    ↓
27. API Gateway
    ↓
Need event-driven
    ↓
56. Event-Driven Architecture & Pub/Sub
```

**Path:**
1. [25-REST vs RPC](./system-design-topics/25-rest-vs-rpc.md)
2. [22-Message Queues](./system-design-topics/22-message-queues.md)
3. [23-WebSockets](./system-design-topics/23-websockets.md)
4. [26-Microservices](./system-design-topics/26-microservices-architecture.md)
5. [27-API Gateway](./system-design-topics/27-api-gateway.md)
6. [56-Event-Driven](./system-design-topics/56-event-driven-architecture-and-pubsub.md)

---

## How Design Patterns Become System Design Patterns

### Pattern Evolution at Scale

```
Low-Level Design          →    System Design
─────────────────────────────────────────────────────
Singleton                 →    Leader Election, Service Discovery
Factory                   →    Load Balancer (creates server instances)
Strategy                  →    Cache Eviction Policies (LRU, LFU, FIFO)
Observer                  →    Pub/Sub, Event-Driven Architecture
State                     →    Saga Pattern (distributed state machines)
Decorator                 →    API Gateway (add auth, rate limiting)
Proxy                     →    Reverse Proxy, CDN, Cache
Adapter                   →    Anti-Corruption Layer, Legacy integration
Facade                    →    API Gateway, BFF (Backend for Frontend)
Command                   →    Event Sourcing, CQRS
```

### Examples

**1. Singleton → Leader Election**

**LLD:**
```python
class Database:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**System Design:**
```
Multiple servers, only ONE can be leader
├── Use consensus algorithm (Raft, Paxos)
├── Leader handles writes
└── Followers handle reads
```

**Real:** Kafka, Redis Sentinel, MongoDB replica sets

---

**2. Observer → Pub/Sub**

**LLD:**
```python
class YouTuber:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def notify(self, video):
        for sub in self.subscribers:
            sub.update(video)
```

**System Design:**
```
Pub/Sub System
├── Publishers send events to topic
├── Multiple subscribers listen
├── Decoupled (don't know about each other)
└── Scales independently
```

**Real:** Kafka, Google Pub/Sub, AWS SNS

---

**3. Strategy → Cache Eviction**

**LLD:**
```python
class Cache:
    def __init__(self, eviction_strategy):
        self.strategy = eviction_strategy

    def evict(self):
        self.strategy.evict()
```

**System Design:**
```
Distributed Cache
├── LRU: Evict least recently used
├── LFU: Evict least frequently used
├── TTL: Expire after time
└── Random: Random eviction
```

**Real:** Redis, Memcached, CDN caching

---

## Anti-Pattern → Solution Pattern Mapping

```
Anti-Pattern                  →    Solution
─────────────────────────────────────────────────────
Improper Instantiation        →    Object Pooling, Singleton
Synchronous I/O               →    Message Queues (Topic 22)
Chatty I/O (N+1)             →    Batch Processing, JOIN queries
No Caching                    →    Cache-Aside (Topic 07)
Busy Database                 →    CQRS, App-layer compute
Retry Storm                   →    Circuit Breaker (Topic 12)
Monolithic Persistence        →    Polyglot Persistence
Noisy Neighbor                →    Rate Limiting (Topic 10)
Extraneous Fetching           →    GraphQL, Field projection
Busy Frontend                 →    Backend for Frontend (BFF)
```

---

## System Design Topic Dependencies

### Must Learn Before

```
Before learning Sharding:
├── Understand CAP Theorem (05)
├── Understand Consistent Hashing (21)
└── Understand Replication (18)

Before learning Microservices:
├── Understand REST vs RPC (25)
├── Understand Message Queues (22)
├── Understand Service Discovery (60)
└── Understand Circuit Breaker (12)

Before learning Multi-Region:
├── Understand CAP Theorem (05)
├── Understand Eventual Consistency (06)
├── Understand Consensus Algorithms (28)
└── Understand Data Replication (18)

Before learning Event-Driven:
├── Understand Message Queues (22)
├── Understand Idempotency (11)
└── Understand Saga Pattern (57)
```

---

## Cross-Module Connections

### LLD → System Design → API Design

```
LLD: Builder Pattern
    ↓
System Design: Request Building
    ↓
API Design: HTTP Request Builder
    └── Example: Stripe API client

LLD: Proxy Pattern
    ↓
System Design: Reverse Proxy, CDN
    ↓
API Design: API Gateway
    └── Example: AWS API Gateway

LLD: State Pattern
    ↓
System Design: Saga Pattern
    ↓
API Design: Order State Machine
    └── Example: E-commerce order flow
```

### System Concept → API Implementation

```
System: Idempotency (Topic 11)
API: Idempotency-Key header
└── Example: Stripe payments

System: Rate Limiting (Topic 10)
API: 429 status + Retry-After header
└── Example: GitHub API

System: Eventual Consistency (Topic 06)
API: Optimistic locking + ETags
└── Example: Dropbox file sync

System: Sharding (Topic 20)
API: Tenant ID in URL/header
└── Example: Slack workspaces
```

---

## Learning Paths by Goal

### Path 1: "I want to pass interviews"

```
Week 1-2: Foundation
├── OOP + SOLID
├── 5 essential patterns (Factory, Singleton, Strategy, Observer, State)
└── Checkpoint: Design Parking Lot

Week 3-4: System Design Basics
├── Topics 01-10 (Latency, CAP, Caching, Load Balancing)
├── Topics 17-21 (Scaling, Sharding)
└── Checkpoint: Design URL Shortener

Week 5-6: Communication & Architecture
├── Topics 22-27 (Message Queues, WebSockets, Microservices)
├── API Design Playbook
└── Checkpoint: Design Instagram

Week 7-8: Practice
├── Walkthroughs: Instagram, Uber, WhatsApp
├── Back-of-envelope estimation
└── Checkpoint: Design 2 systems per day
```

**Start:** [Interview Prep Path](./README.md#-interview-prep-path-4-8-weeks)

---

### Path 2: "I want to fix production issues"

```
Week 1: Identify Issues
├── Performance Anti-patterns (01-10)
├── CHEATSHEET for quick diagnosis
└── Audit codebase

Week 2-3: Fix Critical Path
├── Add caching (Topics 07-08)
├── Add circuit breakers (Topic 12)
├── Add rate limiting (Topic 10)
└── Implement retry with backoff

Week 4: Improve Reliability
├── Observability (Topic 54)
├── Backpressure (Topic 58)
└── Event-Driven (Topic 56)
```

**Start:** [Anti-patterns](./anti-patterns/) + [CHEATSHEET](./CHEATSHEET.md)

---

### Path 3: "I want deep understanding"

```
Stage 1: Why (2 weeks)
├── WHY-SYSTEM-DESIGN-MATTERS.md
├── Real-World Intuition (LLD)
├── How systems fail
└── Scale intuition

Stage 2: Foundation (4 weeks)
├── OOP + SOLID + Patterns
├── Topics 01-30
└── Decision Trees

Stage 3: Advanced (4 weeks)
├── Topics 53-62
├── API Design (18 walkthroughs)
└── Concept Map

Stage 4: Practice (4+ weeks)
├── Build real implementations
├── Study production incidents
└── Contribute to open source
```

**Start:** [WHY System Design Matters](./WHY-SYSTEM-DESIGN-MATTERS.md)

---

## Prerequisites Chart

### System Design Topics

```
01-10: Foundation
├── Prerequisites: None (start here!)
└── Enables: Everything else

11-21: Scaling & Reliability
├── Prerequisites: 01-10
└── Enables: 53-62 (Advanced)

22-30: Communication & Distributed
├── Prerequisites: 01-10, 11-21
└── Enables: Microservices, Event-Driven

53-62: Advanced Patterns
├── Prerequisites: 01-30
└── Enables: Production mastery
```

### API Design

```
Before studying API designs:
├── Understand REST vs RPC (Topic 25)
├── Understand Idempotency (Topic 11)
├── Understand Rate Limiting (Topic 10)
└── Read API Design Playbook (Topic 42)

Then study relevant APIs:
├── Social apps? → Instagram, Twitter, Discord
├── Collaboration? → Figma, Google Docs, Slack
├── Payments? → Stripe
└── AI? → ChatGPT, GitHub Copilot
```

---

## The Complete Map

```
                Start Here
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
    Foundation            Why It Matters
    (LLD + OOP)          (Scale Intuition)
        │                       │
        └───────────┬───────────┘
                    ↓
            System Design Basics
            (Topics 01-30)
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   Reliability   Scaling    Communication
   (10-13)      (17-21)       (22-27)
        │           │           │
        └───────────┼───────────┘
                    ↓
            Advanced Patterns
            (Topics 53-62)
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
    API Design  Anti-patterns  Real
    (18 apps)   (10 issues)  Implementations
        │           │           │
        └───────────┼───────────┘
                    ↓
            Production Mastery
            (Build, Scale, Optimize)
```

---

## Key Insights

### 1. Learning is Not Linear
Don't try to master Topic 1 before starting Topic 2. Instead:
- Learn fundamentals (01-10)
- Jump to what interests you
- Return to fill gaps

### 2. Patterns Repeat at Every Scale
- LLD Singleton → System Design Leader Election
- LLD Observer → System Design Pub/Sub
- LLD Strategy → System Design Cache Eviction

### 3. Every Concept Has Multiple Applications
- **Caching**: Performance, cost reduction, offline support
- **Sharding**: Write scaling, data locality, compliance
- **Circuit Breaker**: Reliability, cost control, user experience

### 4. Trade-offs are Everywhere
- Strong consistency → Slow but correct
- Eventual consistency → Fast but potentially stale
- Understand the trade-off, pick based on needs

---

## Next Steps

1. **Understand WHY:** [WHY System Design Matters](./WHY-SYSTEM-DESIGN-MATTERS.md)
2. **Learn WHEN:** [Decision Trees](./DECISION-TREES.md)
3. **Follow a path:** [Complete Learning Journey](./README.md#-complete-learning-journey)
4. **Use this map:** Revisit when concepts seem disconnected

Remember: **Understanding connections > memorizing facts**

Good luck! 🚀
