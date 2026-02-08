# Database Sharding

## Definition

**Database Sharding** (horizontal partitioning) is splitting a large database into smaller, faster, more manageable pieces called shards. Each shard is an independent database containing a subset of the total data.

## How Sharding Works

```
Single Database (Before):
[All 10M users] → Slow, hard to scale ❌

Sharded (After):
Shard 1: [Users 1-2.5M]  → Fast ✅
Shard 2: [Users 2.5-5M]  → Fast ✅
Shard 3: [Users 5-7.5M]  → Fast ✅
Shard 4: [Users 7.5-10M] → Fast ✅

Query for user 6M → Route to Shard 3
4x parallelization = 4x faster!
```

## Sharding Strategies

### 1. Range-Based Sharding
```
Shard 1: user_id 1-1000000
Shard 2: user_id 1000001-2000000
Shard 3: user_id 2000001-3000000

Pros: ✅ Simple, range queries easy
Cons: ❌ Hotspots (uneven distribution)
```

### 2. Hash-Based Sharding
```python
def get_shard(user_id, num_shards):
    return hash(user_id) % num_shards

user_id = 123456
shard = hash(123456) % 4 = 2  → Shard 2

Pros: ✅ Even distribution
Cons: ❌ Range queries hard, resharding difficult
```

### 3. Geographic Sharding
```
US users → US database
EU users → EU database
Asia users → Asia database

Pros: ✅ Data locality, compliance (GDPR)
Cons: ❌ Global queries difficult
```

### 4. Entity-Based/Directory Sharding
```
Lookup table:
user_id → shard_id

123 → Shard 1
456 → Shard 2
789 → Shard 1

Pros: ✅ Flexible, easy resharding
Cons: ❌ Extra lookup, SPOF (directory service)
```

## Real-World Examples

### Instagram
**Massive PostgreSQL sharding**

```
1 billion+ users
Thousands of PostgreSQL shards

Sharding key: user_id
Shard selection: Consistent hashing

Schema per shard:
- Users
- Posts (belonging to users in shard)
- Likes
- Comments

User data colocated → Fast queries, no cross-shard joins
```

**Shard ID generation:**
```python
# 64-bit ID
shard_id = bits 0-12  (4096 shards)
type = bits 13-20
local_id = bits 21-63

Example: user_id 250563223767015450
→ Extract shard_id = 1265
→ Query Shard 1265
```

### YouTube
**Video sharding**

```
Billions of videos

Sharding strategies:
1. Video metadata: Sharded by video_id
2. User data: Sharded by user_id
3. Comments: Sharded by video_id
4. Views: Aggregated (BigTable/Cassandra)

Shard routing:
video_id → hash → shard_id
Metadata + video file references in same shard
```

### Discord
**Message sharding with Cassandra**

```
Billions of messages across channels

Partition key: (channel_id, bucket)

bucket = message_id / bucketSize

Messages distributed across Cassandra nodes
Linear scalability: Add nodes = more capacity
```

### Pinterest
**16,000+ MySQL shards**

```
Pins sharded by pin_id
Users sharded by user_id
Boards sharded by board_id

Shard mapping: Stored in ZooKeeper
Application handles routing

pyres library: Routes queries to correct shard
```

### Uber
**Schemaless sharding**

```
Sharded MySQL with JSON docs

Sharding key: user_id, driver_id, trip_id

Each entity type independently sharded
Thousands of shards globally
```

## Sharding Challenges

### 1. Cross-Shard Queries
```sql
-- Bad: Requires querying all shards
SELECT * FROM users WHERE age > 30;

-- Good: Scoped to single shard
SELECT * FROM users WHERE user_id = 123456;
```

**Solution:**
```python
# Parallel fan-out query
def query_all_shards(sql):
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(shard.query, sql) for shard in shards]
        for future in futures:
            results.extend(future.result())
    return results
```

### 2. Cross-Shard Joins
```sql
-- Can't join across shards efficiently
SELECT users.name, orders.total
FROM users JOIN orders ON users.id = orders.user_id;

-- If users and orders in different shards ❌
```

**Solution:**
```python
# Denormalize or application-level joins
1. Query user from user_shard
2. Query orders from order_shard (filtered by user_id)
3. Join in application code
```

### 3. Distributed Transactions
```python
# Transfer money: Alice (Shard 1) → Bob (Shard 2)
# Requires 2-phase commit (complex, slow)

# Better: Avoid cross-shard transactions
# Design sharding key to keep related data together
```

### 4. Resharding
```
Adding shard: Hash changes, data must migrate
4 shards → 5 shards = 80% of data moves! ❌

Solution: Consistent hashing (minimizes moves)
```

### 5. Hotspots
```
Celebrity user gets 100M followers
→ One shard overloaded 🔥

Solutions:
- Dedicated shard for celebrities
- Further sharding (followers sub-sharded)
- Caching
```

## Implementation Example

```python
import hashlib

class ShardedDB:
    def __init__(self, shards):
        self.shards = shards  # List of DB connections
    
    def get_shard(self, shard_key):
        """Determine which shard to use"""
        hash_val = int(hashlib.md5(str(shard_key).encode()).hexdigest(), 16)
        shard_id = hash_val % len(self.shards)
        return self.shards[shard_id]
    
    def insert_user(self, user_id, data):
        shard = self.get_shard(user_id)
        shard.execute("INSERT INTO users (id, data) VALUES (?, ?)", [user_id, data])
    
    def get_user(self, user_id):
        shard = self.get_shard(user_id)
        return shard.query("SELECT * FROM users WHERE id = ?", [user_id])
    
    def get_all_active_users(self):
        """Cross-shard query"""
        results = []
        for shard in self.shards:
            results.extend(shard.query("SELECT * FROM users WHERE active = true"))
        return results

# Usage
db = ShardedDB([shard1_conn, shard2_conn, shard3_conn, shard4_conn])
db.insert_user(123456, {"name": "Alice"})
user = db.get_user(123456)  # Routes to correct shard automatically
```

## Sharding Best Practices

✅ **Choose immutable shard key**
```
Good: user_id (doesn't change)
Bad: email (can change)
```

✅ Colocate related data
```
User + their posts + their likes → Same shard
Minimizes cross-shard queries
```

✅ **Monitor shard health**
```
- Shard size balance
- Query distribution
- Hotspot detection
```

✅ **Use consistent hashing**
```
Minimizes data movement when adding/removing shards
```

✅ **Avoid distributed transactions**
```
Design to keep transactions within single shard
```

✅ **Plan for resharding**
```
Use directory-based or consistent hashing
Makes adding shards easier
```

## When to Shard?

```
Consider sharding when:
✅ Data > single server capacity (1TB+)
✅ Write throughput > single server (10K+ writes/sec)
✅ Need linear scalability

DON'T shard if:
❌ Adds unnecessary complexity
❌ Read replicas sufficient
❌ Vertical scaling still possible
```

## Alternatives to Sharding

1. **Read replicas** (for read-heavy loads)
2. **Caching** (Redis, Memcached)
3. **Vertical scaling** (bigger hardware)
4. **NoSQL databases** (Cassandra, DynamoDB - built-in sharding)

## Interview Tips

**Q: "How does Instagram shard their database?"**

**A:** User_id-based sharding with consistent hashing. Thousands of PostgreSQL shards. Each shard contains users and all their data (posts, likes, comments) for fast queries without cross-shard joins.

**Q: "What are the challenges of sharding?"**

**A:** 
1. Cross-shard queries (fan-out needed)
2. No cross-shard joins
3. Distributed transactions complex
4. Resharding expensive
5. Hotspots (uneven load)

**Q: "Range vs hash sharding?"**

**A:**
Range: Simple, range queries easy, but hotspots likely
Hash: Even distribution, but range queries hard and resharding difficult

**Key Takeaway:** Sharding enables horizontal scaling by splitting data across independent databases. Adds complexity, so only shard when necessary. Design shard key carefully!
