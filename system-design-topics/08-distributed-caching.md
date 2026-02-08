# Distributed Caching

## Definition

**Distributed Caching** is a caching system where data is spread across multiple nodes (servers) to provide horizontal scalability, high availability, and fault tolerance beyond what a single cache server can provide.

## Key Concepts

### Why Distributed Cache?

**Single Cache Limitations:**
```
┌─────────────┐
│   Redis     │  ← Single point of failure
│   16GB RAM  │  ← Limited capacity
│  50K QPS    │  ← Limited throughput
└─────────────┘
```

**Distributed Cache:**
```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Node 1  │  │ Node 2  │  │ Node 3  │
│ 16GB    │  │ 16GB    │  │ 16GB    │  ← 48GB total
│ 50K QPS │  │ 50K QPS │  │ 50K QPS │  ← 150K QPS
└─────────┘  └─────────┘  └─────────┘
     ↑            ↑            ↑
     └────────────┴────────────┘
       Fault tolerant (redundancy)
```

### Data Distribution Strategies

#### 1. Consistent Hashing
**Avoids massive re-distribution when nodes added/removed**

```python
import hashlib

def hash_key(key, num_nodes):
    # Hash key to determine which node
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return hash_val % num_nodes

# Example
cache_node = hash_key("user:123", 3)  # Returns 0, 1, or 2
```

**Traditional hashing problem:**
```
3 nodes → Add 1 node → 75% of keys rehash! ❌

With consistent hashing:
3 nodes → Add 1 node → Only 25% keys rehash ✅
```

**How it works:**
```
   0°──────────────────────360°
   │   N1    N2    N3       │  (Nodes on circle)
   │                        │
   └────────────────────────┘
        ↑         ↑
    user:123  user:456  (Keys map to nearest node)
```

**Used by:** Memcached, DynamoDB, Cassandra

#### 2. Range-Based Partitioning
**Distribute by key ranges**

```
Node 1: A-M
Node 2: N-Z

user:alice → Node 1
user:zack  → Node 2
```

**Pros:**
- ✅ Simple
- ✅ Range queries possible

**Cons:**
- ❌ Hot spots (uneven distribution)
- ❌ Hard to rebalance

#### 3. Random/Round-Robin
**Hash assigns nodes randomly**

```python
nodes = ["node1", "node2", "node3"]
node = nodes[hash(key) % len(nodes)]
```

## Real-World Examples

### Facebook - TAO
**"The Associations and Objects" - Distributed cache for social graph**

**Scale:**
- 9+ billion requests/second
- Petabytes of data
- Thousands of cache servers globally

**Architecture:**
```
User request → TAO layer (cache) → MySQL (if cache miss)

Geographic distribution:
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  US Region   │     │   EU Region  │     │ Asia Region  │
│ ┌──────────┐ │     │ ┌──────────┐ │     │ ┌──────────┐ │
│ │ TAO Cache│ │     │ │ TAO Cache│ │     │ │ TAO Cache│ │
│ └──────────┘ │     │ └──────────┘ │     │ └──────────┘ │
│      ↓       │     │      ↓       │     │      ↓       │
│ ┌──────────┐ │     │ ┌──────────┐ │     │ ┌──────────┐ │
│ │  MySQL   │ │     │ │  MySQL   │ │     │ │  MySQL   │ │
│ └──────────┘ │     │ └──────────┘ │     │ └──────────┘ │
└──────────────┘     └──────────────┘     └──────────────┘
        ↑                    ↑                    ↑
        └────────────────────┴────────────────────┘
                 Async replication
```

**Features:**
- Eventual consistency across regions
- Write to master region
- Read from local region (low latency)
- Invalidation propagation

### Netflix - EVCache
**Ephemeral Volatile Cache - Memcached-based distributed cache**

**Scale:**
- 1+ trillion requests per day
- 30+ million operations/second peak
- Thousands of servers across AWS regions

**Architecture:**
```
Application → EVCache Client → Memcached clusters

Replication:
Zone A: [Cache1, Cache2, Cache3]
Zone B: [Cache4, Cache5, Cache6]  ← Replica of Zone A
Zone C: [Cache7, Cache8, Cache9]  ← Another replica

Write: All zones
Read: Nearest zone
```

**Features:**
- Multi-zone replication
- Automatic failover
- Dark reads (verify replicas)
- Chunking for large objects

### Twitter - Distributed Redis
**Timeline caching**

**Scale:**
- 6,000+ tweets per second
- 400+ million tweets per day
- Cache 500 million+ timelines

**Architecture:**
```
┌─────────────┐
│  FastFollow │  ← Real-time fan-out service
└──────┬──────┘
       ↓
┌──────────────────────┐
│  Redis Cluster       │
│ ┌────┐ ┌────┐ ┌────┐│
│ │ N1 │ │ N2 │ │ N3 ││  ← Sharded by user_id
│ └────┘ └────┘ └────┘│
└──────────────────────┘

Tweet: user:elonmusk posts → Fan-out to followers' timelines
Read timeline: user:123 → Redis node (user_id % nodes)
```

**Strategy:**
- Sharded by user_id (consistent hashing)
- Pre-computed timelines (write-through)
- Persistence via RDB/AOF
- Pub/sub for real-time updates

### Amazon - ElastiCache
**Managed Redis/Memcached**

**Use cases at Amazon:**
```
1. Session store (Shopping cart)
   - User's session across load-balanced servers
   - Distributed Redis with replication

2. Product catalog
   - Memcached for read-heavy workload
   - Millions of product lookups/second

3. Recommendation engine
   - Cache recommendations per user
   - TTL: 1 hour, refresh-ahead
```

**Architecture example:**
```
┌─────────────┐
│ Application │
└──────┬──────┘
       ↓
┌──────────────────────────────┐
│   ElastiCache Cluster        │
│ ┌───────┐ ┌───────┐ ┌───────┐│
│ │Primary│→│Replica│→│Replica││
│ └───────┘ └───────┘ └───────┘│
└──────────────────────────────┘
   ↓
Automatic failover to replica if primary fails
```

### Discord - Distributed Redis (Cassandra Migration)
**Message caching**

**Original:** Cassandra (eventually consistent) → Latency spikes

**Solution:** Distributed Redis cluster

**Scale:**
- 1+ billion messages per day
- 100+ million active users
- Sub-10ms read latency

**Architecture:**
```
┌────────────────────────┐
│   Redis Cluster        │
│  (16,384 hash slots)   │
│                        │
│ Master1 → Replica1     │  ← Slots 0-5461
│ Master2 → Replica2     │  ← Slots 5462-10922
│ Master3 → Replica3     │  ← Slots 10923-16383
└────────────────────────┘

Each shard handles:
- ~33% of data
- Independent failure domain
- Automatic slot rebalancing
```

### Google - Memcache (Internal)
**Gmail, YouTube, Maps**

**Scale:**
- Petabytes of cached data
- Millions of queries per second per service

**Features:**
- Multi-layer caching (local + distributed)
- Automatic invalidation
- Smart routing (geo-awareness)
- Proactive refresh

## Distributed Cache Patterns

### 1. Client-Side Partitioning
**Client knows which node to query**

```python
import hashlib

class DistributedCache:
    def __init__(self, nodes):
        self.nodes = nodes
    
    def get_node(self, key):
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return self.nodes[hash_val % len(self.nodes)]
    
    def get(self, key):
        node = self.get_node(key)
        return node.get(key)
    
    def set(self, key, value):
        node = self.get_node(key)
        node.set(key, value)

# Usage
cache = DistributedCache([redis1, redis2, redis3])
cache.set("user:123", data)
```

**Pros:**
- ✅ Simple
- ✅ No proxy overhead

**Cons:**
- ❌ Client complexity
- ❌ Hard to rebalance

### 2. Proxy-Based Partitioning
**Proxy routes requests**

```
Client → Twemproxy/mcrouter → [Node1, Node2, Node3]
```

**Examples:**
- **Twemproxy**: Redis/Memcached proxy
- **mcrouter**: Facebook's Memcached router
- **Envoy**: Modern service proxy

**Pros:**
- ✅ Simple clients
- ✅ Centralized logic

**Cons:**
- ❌ Proxy becomes SPOF
- ❌ Extra network hop

### 3. Cluster Mode (Server-Side Partitioning)
**Nodes coordinate themselves**

```
Client → Any node → Redirects to correct node

Example: Redis Cluster
Client → Node1: GET user:123
Node1: "-MOVED 3999 127.0.0.1:7002"
Client → Node2: GET user:123  # Correct node
Node2: Returns data ✅
```

**Pros:**
- ✅ No proxy needed
- ✅ Automatic rebalancing

**Cons:**
- ❌ Client must support cluster protocol
- ❌ More complex setup

## Replication Strategies

### 1. Primary-Replica
**One primary (writes), multiple replicas (reads)**

```
Write → Primary → Async replicate → Replicas
Read  → Any replica
```

**Example: Redis Sentinel**
```
┌─────────┐
│ Primary │ ← Writes
└────┬────┘
     ↓ Replicate
┌────┴──────────┐
│               │
▼               ▼
┌──────────┐ ┌──────────┐
│ Replica1 │ │ Replica2 │ ← Reads
└──────────┘ └──────────┘

If primary fails: Sentinel promotes replica
```

### 2. Multi-Primary
**Multiple nodes accept writes**

```
┌────────┐ ↔ ┌────────┐ ↔ ┌────────┐
│ Node 1 │   │ Node 2 │   │ Node 3 │
└────────┘   └────────┘   └────────┘
All can write, bidirectional sync
```

**Challenges:**
- Conflict resolution
- Higher consistency overhead

**Used by:** Cassandra, DynamoDB

### 3. Geo-Replication
**Data centers in multiple regions**

```
US: [Primary + Replicas] ↔ EU: [Primary + Replicas] ↔ Asia: [Primary + Replicas]
              ↕                        ↕                           ↕
          Local reads              Local reads                Local reads
       Cross-region writes      Cross-region writes        Cross-region writes
```

## Challenges & Solutions

### 1. Cache Stampede (Thundering Herd)
**Problem:** Popular key expires, many requests hit database

```python
# Solution: Lock-based
import redis
import time

def get_with_lock(key):
    value = cache.get(key)
    if value:
        return value
    
    lock_key = f"lock:{key}"
    # Try to acquire lock (only one succeeds)
    if redis.set(lock_key, "1", nx=True, ex=10):
        try:
            # This request fetches from DB
            value = db.query(key)
            cache.set(key, value, ex=3600)
            return value
        finally:
            redis.delete(lock_key)
    else:
        # Others wait and retry
        time.sleep(0.1)
        return get_with_lock(key)
```

### 2. Hot Key Problem
**Problem:** One key gets massive traffic

```python
# Solution: Replicate hot key
def get_hot_key(key):
    # Create multiple copies
    replica = random.randint(1, 10)
    replicated_key = f"{key}:replica:{replica}"
    return cache.get(replicated_key)

def set_hot_key(key, value):
    # Set all replicas
    for i in range(1, 11):
        cache.set(f"{key}:replica:{i}", value)
```

### 3. Network Partitions
**Problem:** Split-brain, inconsistent data

```python
# Solution: Quorum reads/writes
def quorum_get(key, nodes, quorum=2):
    responses = []
    for node in nodes:
        try:
            val = node.get(key)
            responses.append(val)
        except:
            pass
    
    # Need majority agreement
    if len(responses) >= quorum:
        return most_common(responses)
    raise Exception("Quorum not reached")
```

### 4. Cache Warming
**Problem:** Cold cache after restart/deployment

```python
# Solution: Pre-populate cache
def warm_cache():
    # Most popular items
    popular_ids = analytics.get_top_1000_products()
    
    for product_id in popular_ids:
        product = db.get_product(product_id)
        cache.set(f"product:{product_id}", product)
    
    print("Cache warmed!")
```

## Best Practices

✅ **Monitor cache clusters**
```
- Hit/miss rate per node
- Eviction rate
- Memory usage
- Network I/O
- Replication lag
- Node health
```

✅ **Handle failures gracefully**
```python
try:
    value = cache.get(key)
except CacheUnavailable:
    # Fallback to database
    value = db.query(key)
```

✅ **Use connection pooling**
```python
from redis import ConnectionPool

pool = ConnectionPool(host='localhost', port=6379, max_connections=50)
redis = Redis(connection_pool=pool)
```

✅ **Implement circuit breaker**
```python
if cache.error_rate > 50%:
    # Stop hitting cache, go direct to DB
    bypass_cache = True
```

✅ **TTL with jitter**
```python
import random
ttl = base_ttl + random.randint(0, base_ttl * 0.2)  # ±20% jitter
```

## When to Use Distributed Cache

✅ **Single cache insufficient**
- Data > single node RAM
- Throughput > single node capacity
- Geographic distribution needed

✅ **High availability required**
- Cannot tolerate cache downtime
- Automatic failover needed

✅ **Predictable access patterns**
- Known hot keys
- Consistent workload

❌ **When NOT to use:**
- Small dataset (single node sufficient)
- Unpredictable access patterns
- Strong consistency required (use database)

## Interview Tips

**Q: "How would you design a distributed cache for user sessions?"**

**A:**
```
1. Consistent hashing for distribution (add/remove nodes easily)
2. Redis Cluster or Memcached with Twemproxy
3. Replication (primary-replica) for availability
4. TTL: 30 minutes (auto-cleanup inactive sessions)
5. Write: Session creation/update
6. Read: Every request (verify session)
7. Fallback: If cache down, create new session
```

**Q: "How to handle a hot key in distributed cache?"**

**A:**
```
1. Detect: Monitor key access frequency
2. Replicate: Create N copies of hot key
3. Route: Hash-based selection of replica
4. Local cache: Add application-level cache for extreme cases
5. Split: If possible, partition the data differently
```

**Q: "Distributed cache with 3 nodes, 1 fails. What happens?"**

**A:**
```
Without replication:
- 33% of data unavailable
- Those requests go to database (slower)
- Cache hit rate drops

With replication:
- Failover to replica
- No data loss
- Slight increase in load on remaining nodes
- Automatic detection and promotion (Redis Sentinel)
```

**Key Takeaway:** Distributed caching enables massive scale and fault tolerance. Use consistent hashing for distribution, replication for availability, and monitoring for hot spots!
