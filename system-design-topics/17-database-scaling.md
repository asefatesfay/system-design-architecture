# Database Scaling

## Definition

**Database Scaling** is the process of increasing database capacity to handle more load through either upgrading existing hardware (vertical scaling) or adding more database servers (horizontal scaling).

## Vertical Scaling (Scale Up)

**Add more power to existing server**

```
Before: 8 cores, 32GB RAM, 500GB SSD
After:  32 cores, 256GB RAM, 2TB NVMe SSD
```

**Pros:**
✅ Simple (no code changes)
✅ Maintains ACID properties
✅ No data partitioning complexity

**Cons:**
❌ Limited (hardware limits)
❌ Expensive (exponential cost)
❌ Single point of failure
❌ Downtime for upgrades

**Example:** AWS RDS instance upgrade
```
db.t3.small → db.r6g.8xlarge
$25/month → $2,500/month
```

## Horizontal Scaling (Scale Out)

**Add more database servers**

### 1. Read Replicas
**Primary for writes, replicas for reads**

```
        ┌─── Read Replica 1 (Read-only)
Write → Primary ─┼─── Read Replica 2 (Read-only)
                └─── Read Replica 3 (Read-only)

Write: Primary only (100% writes)
Read: Balanced across replicas (distributed load)
```

**Use case:** Read-heavy applications (90% reads, 10% writes)

**Examples:**
- Instagram: Read posts from replicas
- Twitter: Read timelines from replicas
- E-commerce: Product catalog reads from replicas

### 2. Sharding (Horizontal Partitioning)
**Split data across multiple databases**

```
Shard 1: Users A-M
Shard 2: Users N-Z

user_id = "alice" → hash → Shard 1
user_id = "zack" → hash → Shard 2
```

**Sharding strategies:**

**a) Range-based:**
```
Shard 1: user_id 1-1000000
Shard 2: user_id 1000001-2000000
```

**b) Hash-based:**
```
shard = hash(user_id) % num_shards
```

**c) Geographic:**
```
US users → US database
EU users → EU database
```

**d) Feature-based:**
```
Orders database
Products database
Users database
```

## Real-World Examples

### Instagram (Facebook)
**Massive sharding implementation**

```
1 billion+ users
Thousands of PostgreSQL shards

Sharding key: user_id
Each shard: ~10,000 users
Shard location determined by consistent hashing

Features:
- Automatic shard balancing
- Cross-shard queries minimized
- User data colocated (posts, likes, comments in same shard)
```

### YouTube
**Sharding for videos**

```
Video metadata: Sharded by video_id
User data: Sharded by user_id
Comments: Sharded by video_id
Views: Aggregated in BigTable

Billions of videos, exabytes of data
```

### Discord
**Migrated from MongoDB to Cassandra for scaling**

```
Problem: MongoDB couldn't scale (billions of messages)
Solution: Cassandra (horizontal scaling)

Partition key: (channel_id, bucket)
Messages distributed across nodes
Linearly scalable (add more nodes = more capacity)
```

### Pinterest
**Sharding MySQL**

```
Pins table sharded by pin_id
Users table sharded by user_id
Boards table sharded by board_id

16,000+ MySQL shards
Shard mapping in ZooKeeper
Application handles routing
```

## Scaling Techniques

### 1. Connection Pooling

```python
# Without pooling
for request in requests:
    conn = create_connection()  # Expensive!
    execute_query(conn)
    close_connection()

# With pooling
pool = ConnectionPool(size=100)
conn = pool.get_connection()  # Reuse existing
execute_query(conn)
pool.release(connection)
```

### 2. Caching (Redis, Memcached)

```
Read request:
1. Check cache → Hit? Return ✅
2. Cache miss → Query database
3. Store in cache
4. Return result

95% cache hit rate = 20x less database load
```

### 3. Indexing

```sql
-- Without index: Full table scan O(n)
SELECT * FROM users WHERE email = 'alice@example.com';

-- With index: O(log n)
CREATE INDEX idx_email ON users(email);
```

### 4. Query Optimization

```sql
-- Bad: Multiple queries
SELECT * FROM orders WHERE user_id = 123;
SELECT * FROM items WHERE order_id IN (1,2,3);

-- Good: Single join
SELECT o.*, i.* 
FROM orders o 
JOIN items i ON i.order_id = o.id 
WHERE o.user_id = 123;
```

### 5. Denormalization

```sql
-- Normalized (requires JOIN)
SELECT users.name, COUNT(posts.id)
FROM users
JOIN posts ON posts.user_id = users.id
GROUP BY users.id;

-- Denormalized (faster, no JOIN)
SELECT name, post_count FROM users;
-- Update post_count when post created/deleted
```

## Challenges

### Sharding Challenges

❌ **Cross-shard queries**
```sql
-- Query spans multiple shards (slow)
SELECT * FROM users WHERE age > 30;
-- Must query all shards, merge results
```

❌ **Transactions across shards**
```
Transfer money from Alice (Shard 1) to Bob (Shard 2)
Requires distributed transaction (2PC, complex)
```

❌ **Resharding**
```
Adding/removing shards requires data migration
Downtime or complex live migration
```

❌ **Hotspots**
```
Celebrity user gets 1M followers → One shard overloaded
Requires special handling (dedicated shard, caching)
```

### Replication Lag

```
Write to primary: balance = $100
Read from replica (1s lag): balance = $0 (stale!)

Solutions:
- Read from primary for critical reads
- Use "read-your-writes" consistency
- Accept eventual consistency
```

## Best Practices

✅ **Start with vertical scaling**
```
Easier, no code changes
Scale up until hardware limits reached
```

✅ **Add read replicas for read-heavy workloads**
```
Write: Primary
Read: Round-robin across replicas
Works for 90% of applications
```

✅ **Shard only when necessary**
```
Adds complexity
Consider when single DB can't handle load
Usually at millions of rows, 100K+ QPS
```

✅ **Use appropriate sharding key**
```
- Evenly distributed (avoid hotspots)
- Aligned with query patterns
- Immutable (user_id, not email)
```

✅ **Monitor and optimize queries**
```
- Slow query logs
- Query EXPLAIN plans
- Index usage
```

✅ **Use caching aggressively**
```
Cache frequently read data
Reduce database load by 10-100x
```

## Interview Tips

**Q: "How would you scale a database handling 100K reads/second?"**

**A:**
```
1. Add read replicas (5-10 replicas)
2. Load balance reads across replicas
3. Add caching layer (Redis) for hot data
4. Optimize queries, add indexes
5. Monitor and scale replicas as needed

Writes: Still handled by primary
Reads: Distributed across replicas
```

**Q: "When would you choose sharding over read replicas?"**

**A:**
```
Read replicas: Read-heavy (90% reads, 10% writes)
Sharding: Write-heavy OR data too large for single server

Choose sharding when:
- Write throughput exceeds single server
- Data size > single server capacity (1TB+)
- Need to scale writes linearly
```

**Q: "How does Instagram shard their database?"**

**A:**
```
Sharding key: user_id
Thousands of PostgreSQL shards
Each shard: ~10K-100K users
Consistent hashing for shard assignment
User data colocated (posts, likes in same shard)
Minimizes cross-shard queries
```

**Key Takeaway:** Start with vertical scaling, add read replicas for read-heavy workloads, use sharding only when necessary for writes or data size. Always measure and optimize!
