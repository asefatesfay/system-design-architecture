# CAP Theorem

## Definition

The **CAP Theorem** (also called Brewer's Theorem) states that in a distributed system, you can only guarantee **two out of three** properties simultaneously:

- **C**onsistency: All nodes see the same data at the same time
- **A**vailability: Every request receives a response (success or failure)
- **P**artition Tolerance: System continues operating despite network failures

## Key Concepts

### The Three Properties

#### Consistency (C)
**All nodes have the same data**

```
User writes to Node A: balance = $100
User reads from Node B: balance = $100 ✅ (consistent)
User reads from Node C: balance = $100 ✅ (consistent)
```

Strong consistency means:
- Read always returns the most recent write
- All replicas synchronized
- May need to wait for coordination

#### Availability (A)
**Every request gets a response**

```
User requests data from any node → Always get response ✅
Even if some nodes are down
Even if data might be stale
```

High availability means:
- No downtime
- System operational even with failures
- May return stale data

#### Partition Tolerance (P)
**System works despite network splits**

```
Network Partition:
[Node A, Node B] | Network down | [Node C, Node D]
         ↓                              ↓
    Cluster 1                      Cluster 2
```

Partition tolerance means:
- System continues despite communication failures
- Must handle split-brain scenarios
- Essential in distributed systems

### Why Only Two?

**Network partitions WILL happen** in distributed systems:
- Cable cuts
- Switch failures
- Data center connectivity issues
- Slow networks (appear as partitions)

So in practice, you must choose:
- **CP**: Consistency + Partition Tolerance (Sacrifice Availability)
- **AP**: Availability + Partition Tolerance (Sacrifice Consistency)

**CA** (Consistency + Availability) is only possible in single-node systems (not distributed).

## CAP Trade-offs

### CP Systems (Consistency + Partition Tolerance)
**"Refuse to respond if not sure data is current"**

**During partition:**
```
Write to Node A → Success
Read from Node B (partitioned) → ERROR (no response) ❌
Why? Can't guarantee consistency, so refuses to answer
```

**Examples:**
- **MongoDB** (default mode)
- **HBase**
- **Redis** (in certain configs)
- **ZooKeeper**
- **Consul**

**Use cases:**
- Financial transactions
- Inventory management
- Strong consistency required

### AP Systems (Availability + Partition Tolerance)
**"Always respond, even if data might be stale"**

**During partition:**
```
Write to Node A: balance = $100
Write to Node B (partitioned): balance = $50
Both accept writes! ✅
Later reconcile (last-write-wins, version vectors, etc.)
```

**Examples:**
- **Cassandra**
- **DynamoDB**
- **CouchDB**
- **Riak**
- **DNS**

**Use cases:**
- Social media feeds
- Analytics
- Shopping carts
- View counts

## Real-World Examples

### MongoDB (CP)
**Scenario:** E-commerce inventory

```javascript
// During network partition:
// Primary node accessible → Writes succeed
db.inventory.update({product: "iPhone"}, {$inc: {stock: -1}})
// OK ✅

// Primary node unreachable → Reads/writes fail
db.inventory.find({product: "iPhone"})
// Error: No primary available ❌
```

**Why CP?**
- Inventory must be accurate (can't oversell)
- Better to show error than wrong data
- Money is involved

**Real example:** When MongoDB loses quorum, writes are rejected until connectivity restored.

### Cassandra (AP)
**Scenario:** User activity timeline

```sql
-- Write to Node A during partition
INSERT INTO timeline (user, post, time) VALUES ('alice', 'Hello', '2026-02-08');
-- OK ✅

-- Read from Node B (partitioned)
SELECT * FROM timeline WHERE user = 'alice';
-- Returns data (might miss latest post) ✅

-- Later: Nodes sync, conflicts resolved
```

**Why AP?**
- Timeline doesn't need immediate consistency
- Users must always be able to post
- Temporary inconsistency acceptable

**Real example:** Netflix uses Cassandra - if you post a review, it might take seconds to appear everywhere, but posting never fails.

### DynamoDB (AP)
**Scenario:** Shopping cart

```python
# Add to cart on Node A
cart.add_item("iPhone", quantity=1)

# View cart on Node B (partitioned)
cart.get_items()  # Might not show iPhone yet
# But still returns SOMETHING ✅

# Eventually consistent
# After partition heals: all nodes synchronized
```

**Why AP?**
- Shopping cart doesn't need immediate consistency
- Users must always be able to shop
- Temporary stale data acceptable

**Amazon's reasoning:** Better to show slightly stale cart than block user from shopping.

### Google Spanner (CP pretending to be CA?)
**Special case:** Uses atomic clocks (TrueTime)

```
- GPS and atomic clocks synchronize global timestamps
- Sacrifices latency for consistency (waits for clock sync)
- Still CP: During partition, some shards unavailable
```

**Limitations:**
- Requires specialized hardware
- Higher latency (waits for time uncertainty)
- Expensive!

### DNS (AP)
**Highly available, eventually consistent**

```
1. Update DNS: example.com → 1.2.3.4
2. Propagates to millions of servers
3. Takes minutes to hours (TTL-dependent)
4. During propagation: Different servers return different IPs
```

**Why AP?**
- DNS must always work
- Temporary inconsistency acceptable
- Availability critical for internet

## Tunable Consistency

Some systems let you CHOOSE per-request:

### Cassandra
```sql
-- Strong consistency (CP-like)
SELECT * FROM users WHERE id = 123 USING CONSISTENCY QUORUM;

-- High availability (AP-like)
SELECT * FROM users WHERE id = 123 USING CONSISTENCY ONE;
```

### DynamoDB
```python
# Eventually consistent read (AP)
response = table.get_item(Key={'id': '123'})

# Strongly consistent read (CP-like)
response = table.get_item(
    Key={'id': '123'},
    ConsistentRead=True  # More expensive, might fail during partition
)
```

## CAP in Microservices

### Scenario: Order Service + Inventory Service

**Network partition between services:**

**CP Approach:**
```
1. User places order
2. Order service calls Inventory service
3. If Inventory unreachable → Reject order ❌
   "Sorry, system temporarily unavailable"
```

**AP Approach:**
```
1. User places order → Success ✅
2. Inventory service unavailable
3. Accept order anyway (optimistic)
4. Later: Async check inventory
5. If insufficient stock → Cancel order, refund user
```

**Which to choose?**
- **Flash sales, limited inventory**: CP (prevent overselling)
- **Regular shopping**: AP (better UX, handle inconsistency async)

## Beyond CAP: PACELC

CAP is incomplete. **PACELC** adds:

**PACELC:**
- If **P**artition → Choose **A** or **C**
- **E**lse (no partition) → Choose **L**atency or **C**onsistency

### Examples

**MongoDB:**
- **PA/EC**: During partition → Consistency; Normal → Consistency (higher latency)

**Cassandra:**
- **PA/EL**: During partition → Availability; Normal → Low latency

**DynamoDB:**
- **PA/EL**: During partition → Availability; Normal → Low latency

**Google Spanner:**
- **PC/EC**: During partition → Consistency; Normal → Consistency (higher latency)

## Practical Strategies

### 1. Hybrid Storage
Use different databases for different data:

```
CP Database (PostgreSQL):
  - Financial transactions
  - Inventory counts
  - User authentication

AP Database (Cassandra):
  - User activity logs
  - Analytics events
  - Social media posts
```

### 2. Compensating Actions
Accept writes optimistically, resolve conflicts later:

```
1. User A sets status = "busy"
2. User B sets status = "away" (concurrent, partitioned)
3. Conflict! Both succeeded
4. Resolution: Last-write-wins (timestamp), or custom logic
```

### 3. Event Sourcing
Store events, rebuild state:

```
Events (always available, append-only):
  - Account created
  - $100 deposited
  - $50 withdrawn

Current state (computed from events):
  - Balance: $50
```

### 4. Saga Pattern
Break transactions across services:

```
Order Service → Inventory Service → Payment Service
Each step can fail independently
Compensate on failure:
  1. Reserve inventory ✅
  2. Charge payment ❌
  3. Rollback: Release inventory
```

## Common Misconceptions

❌ **"ACID databases are CA"**
- Single-node ACID = not distributed, so CAP doesn't apply
- Multi-node ACID (like Postgres with replication) = typically CP

❌ **"NoSQL = AP, SQL = CP"**
- NoSQL can be CP (MongoDB, HBase)
- SQL can be AP (CockroachDB with relaxed settings)

❌ **"Partitions are rare"**
- In large distributed systems, partitions happen constantly
- Cloud environments have regular network hiccups

## Decision Framework

```
Choose CP if:
├─ Data correctness critical? YES (money, inventory, auth)
├─ Can tolerate downtime? YES (better unavailable than wrong)
├─ Can reject requests? YES (fail fast)
└─ Read-after-write consistency needed? YES

Choose AP if:
├─ Uptime critical? YES (99.99%+ availability)
├─ Can tolerate stale reads? YES (eventual consistency OK)
├─ Write-heavy workload? YES (always accept writes)
└─ User experience > perfect data? YES (social media, carts)
```

## Monitoring CAP Trade-offs

### CP System Health
```
- Monitor rejected requests (during partitions)
- Track consistency lag
- Alert on quorum loss
- Measure leader election time
```

### AP System Health
```
- Monitor replication lag
- Track conflict resolution
- Alert on divergence beyond threshold
- Measure eventual consistency delay
```

## Interview Tips

**Q: "What is CAP theorem?"**

**A:** In a distributed system with network partitions, you must choose between Consistency (all nodes see same data) and Availability (always respond). Can't have both during partition.

**Q: "Is it possible to have CA?"**

**A:** Only in single-node systems (not distributed). In distributed systems, network partitions WILL happen, so P is required. Must choose CP or AP.

**Q: "Design a social media system - CP or AP?"**

**A:** AP. Users must always be able to post (availability). Temporary inconsistency in feeds is acceptable. Example: Instagram uses Cassandra.

**Q: "Design a banking system - CP or AP?"**

**A:** CP. Account balances must be accurate (consistency). Better to reject transaction than show wrong balance. Example: Traditional banks use CP databases.

**Key Takeaway:** CAP theorem forces trade-offs in distributed systems. Choose based on business requirements: correctness (CP) vs. availability (AP).
