# Strong vs Eventual Consistency

## Definition

**Strong Consistency** guarantees that once a write completes, all subsequent reads will see that write's value. Every read gets the most recent write.

**Eventual Consistency** guarantees that if no new updates are made, eventually all replicas will converge to the same value. Reads might return stale data temporarily.

## Key Concepts

### Strong Consistency
**"Read your own writes immediately"**

```
Time  Node A   Node B   Node C
  0     100      100      100
  1   Write 200
  2   Sync→    Sync→    Sync→
  3     200      200      200  ✅ All updated before accepting new reads
  4   Read: 200 from any node ✅
```

**Guarantees:**
- ✅ Always see latest data
- ✅ No stale reads
- ✅ Linearizable (operations appear instantaneous)

**Trade-offs:**
- ❌ Higher latency (wait for sync)
- ❌ Lower availability (if nodes unreachable)
- ❌ Reduced throughput (coordination overhead)

### Eventual Consistency
**"Will be consistent... eventually"**

```
Time  Node A   Node B   Node C
  0     100      100      100
  1   Write 200
  2     200    Still 100  Still 100  ⚠️ Inconsistent!
  3     200      200    Still 100
  4     200      200      200  ✅ Eventually consistent
```

**Guarantees:**
- ✅ High availability (always accept writes)
- ✅ Low latency (no waiting)
- ✅ High throughput

**Trade-offs:**
- ❌ Stale reads possible
- ❌ Read-your-own-writes not guaranteed
- ❌ Conflict resolution needed
- ❌ More complex application logic

## Consistency Models (Spectrum)

```
Strongest ←──────────────────────────→ Weakest

Linearizability (Strong Consistency)
    ↓
Sequential Consistency
    ↓
Causal Consistency
    ↓
Session Consistency (read-your-writes)
    ↓
Eventual Consistency
    ↓
Best Effort
```

### 1. Linearizability (Strongest)
All operations appear to execute atomically in real-time order.

**Example:** Google Spanner, ZooKeeper

```
Client A: Write X=1 at T1
Client B: Read X at T2 (T2 > T1)
Result: Must return X=1 ✅
```

### 2. Sequential Consistency
Operations appear in some sequential order, but not necessarily real-time.

**Example:** Some replicated databases

```
Client A: Write X=1, Write X=2
Client B sees: X=1, then X=2 ✅
Client C sees: X=1, then X=2 ✅
(Same order for everyone, but might lag real-time)
```

### 3. Causal Consistency
If operation A causes operation B, everyone sees A before B.

**Example:** Social media posts and comments

```
Alice: Post "I got a dog!" (A)
Bob: Comment "Congrats!" on A (B)

Everyone sees post (A) before comment (B) ✅
But might see other unrelated posts out of order
```

### 4. Session Consistency (Read-Your-Writes)
Within a session, you see your own writes.

**Example:** Shopping cart

```
User's session:
  1. Add iPhone to cart
  2. Refresh page
  3. See iPhone in cart ✅

Different user might not see iPhone yet ✅
```

### 5. Eventual Consistency
No ordering guarantees, but will converge.

**Example:** DNS, Cassandra (default)

```
Write to Node A: X=100
Read from Node B: X=100 (eventually)
How long? Depends (milliseconds to seconds)
```

## Real-World Examples

### Strong Consistency

#### Google Spanner
**Use case:** AdWords billing (money involved)

```
1. Advertiser adds $1000 to account
2. System charges for ad clicks
3. Must never show negative balance or oversell ✅

How: TrueTime (atomic clocks), synchronous replication
Cost: Higher latency (~10ms extra for global consistency)
```

#### Amazon RDS (PostgreSQL/MySQL)
**Use case:** E-commerce orders

```
1. User purchases last item in stock
2. Stock count: 1 → 0
3. Next user immediately sees: Out of stock ✅

How: Single-primary with synchronous replicas
Trade-off: Writes wait for replica acknowledgment
```

#### MongoDB (with majority write concern)
**Use case:** Banking transactions

```javascript
// Strong consistency
db.accounts.updateOne(
  {id: 'alice'},
  {$inc: {balance: -100}},
  {writeConcern: {w: 'majority'}}  // Wait for majority
)

// Read immediately after write
const balance = db.accounts.findOne({id: 'alice'})
// Guaranteed to see the -100 update ✅
```

#### Redis (single master)
**Use case:** Lock management, rate limiting

```python
# Acquire distributed lock
redis.set("lock:resource", "uuid", nx=True, ex=30)
# No other node can acquire until released
# Strong consistency within single master
```

### Eventual Consistency

#### Cassandra
**Use case:** Netflix viewing history

```sql
-- Write to any replica (fast!)
INSERT INTO viewing_history (user, show, timestamp) 
VALUES ('alice', 'stranger-things', NOW());

-- Read from any replica
SELECT * FROM viewing_history WHERE user = 'alice';
-- Might not see latest watch immediately ⚠️
-- Shows up within seconds ✅

Why acceptable: Not critical if history lags a bit
Benefit: 99.99% availability, handles millions of writes/sec
```

#### DynamoDB
**Use case:** Shopping cart

```python
# Write accepted immediately
table.put_item(Item={'user': 'alice', 'items': ['iPhone', 'AirPods']})

# Read might be stale (eventually consistent by default)
response = table.get_item(Key={'user': 'alice'})
# Might not see AirPods yet ⚠️

# Option: Strongly consistent read (costs more)
response = table.get_item(Key={'user': 'alice'}, ConsistentRead=True)
```

#### DNS
**Use case:** Domain name resolution

```bash
# Update DNS record
example.com → 1.2.3.4 (new IP)

# Propagation time: Minutes to hours
# Different DNS servers return different IPs during propagation
dig example.com @8.8.8.8  # Returns old IP
dig example.com @1.1.1.1  # Returns new IP

# Eventually (after TTL expires): All consistent ✅
```

#### Facebook/Instagram
**Use case:** Like counts

```
1. User A likes photo (count: 100 → 101)
2. User B views photo immediately
3. Sees count: 100 OR 101 (depends on which replica)
4. Within seconds: Everyone sees 101 ✅

Why acceptable: Exact like count not critical
Benefit: Sub-second responses, massive scale
```

#### Twitter
**Use case:** Follower counts, tweet propagation

```
1. User posts tweet
2. Propagates to follower timelines (async)
3. Followers see tweet: 0-5 seconds later
4. Retweet counts update: Eventually

Using: Cassandra, eventually consistent
Trade-off: Speed + scale > immediate consistency
```

### Hybrid Approaches

#### Amazon S3
**Default:** Eventual consistency for overwrites and deletes

```
PUT object/key → version 2
GET object/key → might return version 1 or 2

Eventually: Always returns version 2 ✅
```

**Available:** Strong consistency for new objects (since Dec 2020)

```
PUT new-object/key
GET new-object/key → Always returns latest version ✅
```

#### Riak
**Tunable consistency:** Choose per-request

```erlang
% Eventual consistency (fast)
riakc_pb_socket:get(Pid, <<"bucket">>, <<"key">>, [{r, 1}])

% Strong consistency (wait for quorum)
riakc_pb_socket:get(Pid, <<"bucket">>, <<"key">>, [{r, quorum}])
```

## Choosing Strong vs Eventual

### Use Strong Consistency When:

✅ **Financial transactions**
```
- Bank account balances
- Payment processing
- Billing systems
- Cryptocurrency wallets
```

✅ **Inventory management**
```
- Stock levels
- Ticket/seat reservations
- Limited-quantity flash sales
```

✅ **Authentication & authorization**
```
- User login/logout
- Permission changes
- Password resets
```

✅ **Critical metadata**
```
- Configuration changes
- Schema updates
- Access control lists
```

✅ **Regulatory compliance**
```
- Audit logs (immediate consistency)
- GDPR data deletion
- Financial reporting
```

### Use Eventual Consistency When:

✅ **Social features**
```
- Like/follow counts
- Comments, reactions
- User profiles
- Activity feeds
```

✅ **Analytics & metrics**
```
- Page views
- Click tracking
- Real-time dashboards
- Monitoring metrics
```

✅ **Caching**
```
- CDN content
- DNS records
- Session data
```

✅ **Collaborative editing (with CRDT)**
```
- Google Docs (OT/CRDT)
- Figma (multiplayer)
- Conflict-free data types
```

✅ **High-volume logging**
```
- Application logs
- Telemetry data
- Event streams
```

## Conflict Resolution (Eventual Consistency)

### Last-Write-Wins (LWW)
**Simplest:** Timestamp-based

```
Node A: Set X=100 at T1
Node B: Set X=200 at T2 (concurrent due to partition)

Resolution: X=200 (T2 > T1) ✅
Problem: Lost update (X=100 discarded) ❌
```

### Version Vectors
**Track causality**

```
Client A writes: X=1 [A:1]
Client B writes: X=2 [B:1]
Conflict! Neither causally after the other

Resolution: Application decides (merge, prompt user, etc.)
```

### CRDTs (Conflict-Free Replicated Data Types)
**Automatically merge**

```javascript
// G-Counter (increment-only)
Node A: counter.increment() // {A:1, B:0, C:0}
Node B: counter.increment() // {A:0, B:1, C:0}
Merge: {A:1, B:1, C:0} = 2 ✅

// No conflicts!
```

**Examples:**
- Counters (like counts)
- Sets (add-only, remove-only, or observed-remove)
- Text (collaborative editing)

## Performance Comparison

### Latency

| Operation | Strong | Eventual |
|-----------|--------|----------|
| **Write** | 50-200ms (wait for quorum) | 1-10ms (async) |
| **Read** | 10-50ms (up-to-date) | 1-5ms (might be stale) |

### Throughput

| Metric | Strong | Eventual |
|--------|--------|----------|
| **Writes/sec** | 10,000s | 100,000s to millions |
| **Reads/sec** | 100,000s | millions |

### Availability

| Scenario | Strong | Eventual |
|----------|--------|----------|
| **Node failure** | Reduced (until replaced) | Unaffected |
| **Network partition** | Some requests fail | All requests succeed |
| **Multi-region** | Higher latency | Low latency (local reads) |

## Best Practices

### 1. Default to Eventual, Use Strong When Needed
```python
# Eventual (default, fast)
user_profile = cache.get(user_id)

# Strong (when critical)
account_balance = db.query(account_id, consistent=True)
```

### 2. Read-Your-Own-Writes for UX
```python
# Write
session_id = write_to_cache(data)

# Read from same node/session
data = read_from_cache(session_id, sticky_session=True)
```

### 3. Versioning
```python
# Include version in writes
db.put(key, value, version=5)

# Conditional write
if db.get(key).version == 4:
    db.put(key, new_value, version=5)
```

### 4. Compensating Transactions
```python
# Eventual consistency with compensation
try:
    order_service.create_order(order_id)  # Eventually consistent
    payment_service.charge(order_id)
except PaymentFailed:
    order_service.cancel_order(order_id)  # Compensate
```

## Monitoring Consistency

### Strong Consistency Metrics
```
- Replication lag (should be ~0)
- Quorum response time
- Failed writes (due to unavailability)
- Leader election duration
```

### Eventual Consistency Metrics
```
- Replication lag (track P99)
- Time to consistency (T to converge)
- Conflict rate
- Divergence magnitude
```

## Interview Tips

**Q: "Explain strong vs eventual consistency"**

**A:** Strong consistency means immediate visibility of writes (all nodes synchronized). Eventual consistency means replicas converge over time (faster, more available, but temporary stal reads).

**Q: "When would you use eventual consistency?"**

**A:** When availability and latency matter more than immediate consistency. Examples: social media likes, view counts, analytics. Not for: payments, inventory, authentication.

**Q: "How does Cassandra handle consistency?"**

**A:** Cassandra is eventually consistent by default (AP system). Offers tunable consistency per-request with quorum reads/writes. Can simulate strong consistency with QUORUM (trade-off: higher latency).

**Key Takeaway:** Strong consistency = correct but slow. Eventual consistency = fast but complex. Choose based on business requirements!
