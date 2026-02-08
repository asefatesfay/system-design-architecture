# Caching

## Definition

**Caching** is a technique of storing copies of frequently accessed data in a fast-access storage layer (cache) to reduce latency, decrease load on backend systems, and improve performance.

## Key Concepts

### Cache Hierarchy

```
Fastest/Smallest
    ↓
CPU L1/L2/L3 Cache (nanoseconds)
    ↓
Application Memory (microseconds)
    ↓
Redis/Memcached (milliseconds)
    ↓
CDN Edge Servers (10-50ms)
    ↓
Database Query Cache (50-100ms)
    ↓
Database (100-1000ms+)
    ↓
Slowest/Largest
```

### Cache Hit vs Miss

**Cache Hit:** Data found in cache
```
Request → Cache → Found! → Return (1ms) ✅
```

**Cache Miss:** Data not in cache
```
Request → Cache → Not found → Database (100ms) → Cache it → Return ❌
```

**Cache Hit Rate:** 
```
Hit Rate = Hits / (Hits + Misses)
90% hit rate = 10x faster average response
```

## Caching Patterns

### 1. Cache-Aside (Lazy Loading)
**Most common pattern**

```python
def get_user(user_id):
    # Try cache first
    user = cache.get(f"user:{user_id}")
    if user:
        return user  # Cache hit ✅
    
    # Cache miss - fetch from DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # Store in cache for next time
    cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

**Pros:**
- ✅ Simple to implement
- ✅ Only caches requested data
- ✅ Cache failure doesn't break system

**Cons:**
- ❌ Cache miss penalty (slower first request)
- ❌ Stale data possible
- ❌ Each miss = 2 operations (check cache + DB query)

**Used by:** Most web applications

### 2. Read-Through
**Cache acts as primary interface**

```python
# Cache automatically loads from DB on miss
user = cache.get(f"user:{user_id}")  # Cache handles DB query internally
```

**Pros:**
- ✅ Simpler application code
- ✅ Consistent interface

**Cons:**
- ❌ Tight coupling with cache
- ❌ Cache failure breaks system

**Used by:** Hibernate, some ORMs

### 3. Write-Through
**Write to cache AND database synchronously**

```python
def update_user(user_id, data):
    # Update database
    db.update("UPDATE users SET ... WHERE id = ?", user_id, data)
    
    # Update cache immediately
    cache.set(f"user:{user_id}", data)
```

**Pros:**
- ✅ Cache always consistent
- ✅ No stale reads

**Cons:**
- ❌ Higher write latency (2x writes)
- ❌ Caches data that may never be read

**Used by:** Banking systems, inventory

### 4. Write-Behind (Write-Back)
**Write to cache first, async to DB**

```python
def update_user(user_id, data):
    # Write to cache immediately
    cache.set(f"user:{user_id}", data)
    
    # Queue async DB write
    queue.enqueue(lambda: db.update(...))
    
    return  # Fast! ✅
```

**Pros:**
- ✅ Fast writes
- ✅ Batching possible
- ✅ Reduced DB load

**Cons:**
- ❌ Data loss risk (if cache fails before sync)
- ❌ Complex consistency guarantees

**Used by:** Facebook TAO, high-write systems

### 5. Refresh-Ahead
**Proactively refresh cache before expiry**

```python
def get_user(user_id):
    user = cache.get(f"user:{user_id}")
    
    # If TTL < threshold, async refresh
    if cache.ttl(f"user:{user_id}") < 300:  # 5 min remaining
        async_refresh(user_id)
    
    return user

def async_refresh(user_id):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    cache.set(f"user:{user_id}", user, ttl=3600)
```

**Pros:**
- ✅ Reduces cache misses
- ✅ Consistent low latency

**Cons:**
- ❌ Complex to implement
- ❌ May refresh unused data
- ❌ Extra DB load

**Used by:** High-traffic predictable access patterns

## Real-World Examples

### Facebook (TAO)
**9 billion cache queries/second!**

```
User Profile Request:
1. Check Memcached (< 1ms) → 95%+ hit rate
2. If miss → MySQL (10-50ms)
3. Cache result in Memcached

Distributed across regions:
- Master region (writes)
- Follower regions (reads)
- Async replication

Result: Serves 1 billion+ users
```

### Twitter
**Timeline caching**

```
Without cache:
- User has 1000 followers
- Each timeline = query 1000 users' tweets
- 300M users = billions of queries/second ❌

With cache (Redis):
- Pre-compute timelines
- Store in Redis
- Read timeline: 1 Redis query (1ms) ✅

Cache strategy:
- Write-through: New tweet → update followers' timelines
- Cache-aside: Old tweets loaded on demand
```

### Netflix
**Multi-tier caching**

```
1. EVCache (Memcached): Active users, viewing history
   - Thousands of nodes
   - 1 trillion requests/day
   - Sub-millisecond latency

2. CDN (AWS CloudFront): Video content
   - Cached at edge locations worldwide
   - 90%+ CDN hit rate
   - Saves billions in bandwidth

3. Application-level: Metadata, recommendations
```

### Amazon
**Product catalog**

```
Product Page Request:
1. CloudFront CDN → Static assets (images, CSS)
2. ElastiCache (Redis) → Product data
   - Price, inventory (short TTL)
   - Description, reviews (long TTL)
3. DynamoDB → User-specific data (cart, recommendations)

Cache hierarchy:
- Browser cache (static assets)
- CDN (edge locations)
- Application cache (Redis)
- Database query cache
```

### Google Search
**Multi-level caching**

```
1. Browser cache (visited pages)
2. ISP/network cache
3. Google's edge servers (results, autocomplete)
4. Google's data centers (index shards)

Popular queries cached:
- "weather" → 1 second cache
- "breaking news" → 10 second cache
- "historical facts" → 1 day cache
```

### Airbnb
**Listing search**

```
Search: "SF apartments, 2 beds, $100-200"

Without cache: Query millions of listings ❌

With cache:
1. Cache popular search combinations
2. Cache nearby results (geo-spatial)
3. Cache listing details
4. TTL: 5-15 minutes

Technologies:
- Redis: Search results, user sessions
- ElastiCache: Listing metadata
- CDN: Photos
```

## Cache Invalidation Strategies

### 1. Time-To-Live (TTL)
**Auto-expire after duration**

```python
# Short TTL (frequently changing data)
cache.set("stock_price:AAPL", price, ttl=60)  # 1 minute

# Long TTL (stable data)
cache.set("product:123", product, ttl=86400)  # 1 day
```

### 2. Explicit Invalidation
**Manually remove on update**

```python
def update_product(product_id, data):
    db.update("UPDATE products SET ...", product_id, data)
    cache.delete(f"product:{product_id}")  # Invalidate
```

### 3. Event-Driven Invalidation
**Invalidate on database changes**

```python
# Database trigger or CDC (Change Data Capture)
@on_database_update("products")
def invalidate_cache(event):
    cache.delete(f"product:{event.product_id}")
```

### 4. Cache Stampede Prevention
**Problem:** Many requests hit cache miss simultaneously

```python
# Without protection:
1000 requests → Cache miss → 1000 DB queries! ❌

# With locking:
def get_user_safe(user_id):
    user = cache.get(f"user:{user_id}")
    if user:
        return user
    
    # Only one request fetches from DB
    with redis.lock(f"lock:user:{user_id}", timeout=10):
        # Double-check after acquiring lock
        user = cache.get(f"user:{user_id}")
        if user:
            return user
        
        user = db.query(...)
        cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

## Caching Technologies

### Redis
```bash
# Strings (simple key-value)
redis> SET user:123 "{'name':'Alice'}"
redis> GET user:123

# Hashes (structured data)
redis> HSET user:123 name "Alice" email "alice@example.com"
redis> HGET user:123 name

# Lists (timelines, queues)
redis> LPUSH timeline:alice "post1"
redis> LRANGE timeline:alice 0 9  # Latest 10 posts

# Sorted Sets (leaderboards)
redis> ZADD leaderboard 1000 "alice"
redis> ZRANGE leaderboard 0 9 WITHSCORES  # Top 10

# TTL
redis> SET key value EX 3600  # Expires in 1 hour
```

**Features:**
- Persistence options
- Pub/sub
- Lua scripting
- Cluster mode

**Used by:** Twitter, GitHub, Stack Overflow

### Memcached
```python
import memcache
mc = memcache.Client(['127.0.0.1:11211'])

mc.set("user:123", user_data, time=3600)
user = mc.get("user:123")
```

**Features:**
- Simple, fast
- LRU eviction
- Multi-threaded
- No persistence

**Used by:** Facebook, Wikipedia, YouTube

### CDN (CloudFront, Cloudflare, Fastly)
```
Geographic distribution:
User in Tokyo → Served from Tokyo edge
User in NYC → Served from NYC edge

Cache-Control headers:
Cache-Control: public, max-age=31536000  # 1 year
Cache-Control: no-cache  # Always revalidate
Cache-Control: private  # User-specific, no CDN cache
```

**Used by:** Every major website

## Cache Sizing

### Cache Hit Rate vs Size
```
Size    Hit Rate
10MB     50%
100MB    70%
1GB      90%
10GB     95%
100GB    98%

Diminishing returns! Balance cost vs benefit
```

### Estimation Example
```
Users: 10 million
Average user data: 1KB
Active users (20%): 2 million
Cache size needed: 2M × 1KB = 2GB

With 90% hit rate:
- Cache hits: 90% × 1ms = 0.9ms avg
- Cache misses: 10% × 100ms = 10ms avg
- Weighted average: ~2ms vs 100ms (50x improvement!)
```

## Common Pitfalls

### 1. Cache Inconsistency
```python
# BAD: Race condition
user = cache.get("user:123")
if user:
    db.update("UPDATE users SET ...")  # Cache now stale! ❌
    
# GOOD: Invalidate after update
db.update("UPDATE users SET ...")
cache.delete("user:123")  # Force refresh ✅
```

### 2. Cache Avalanche
**All keys expire simultaneously**

```python
# BAD: Same TTL for everything
cache.set(key, value, ttl=3600)  # All expire together ❌

# GOOD: Add jitter
import random
ttl = 3600 + random.randint(0, 600)  # 3600-4200 seconds
cache.set(key, value, ttl=ttl)  # Distributed expiry ✅
```

### 3. Hot Key Problem
**One key gets massive traffic**

```python
# Example: Celebrity's profile
cache.get("user:celebrity")  # Millions of requests

# Solution: Replicate hot keys
keys = ["user:celebrity:1", "user:celebrity:2", "user:celebrity:3"]
key = random.choice(keys)  # Distribute load
```

### 4. Caching Large Objects
```python
# BAD: Cache 10MB object
cache.set("report:123", huge_report)  # Network overhead ❌

# GOOD: Cache result, not raw data
summary = compute_summary(huge_report)
cache.set("report:123:summary", summary)  # Small, fast ✅
```

## Best Practices

✅ **Cache high-read, low-write data**
```
Good: Product catalog, user profiles
Bad: Bank account balance, real-time stock prices
```

✅ **Set appropriate TTLs**
```
Frequently changing: 1-5 minutes
Moderate: 1 hour
Stable: 1 day to 1 week
Static: 1 year
```

✅ **Monitor cache metrics**
```
- Hit rate (target: >80%)
- Miss rate
- Eviction rate
- Memory usage
- Latency (P50, P99)
```

✅ **Handle cache failures gracefully**
```python
try:
    data = cache.get(key)
except CacheError:
    # Fallback to database
    data = db.query(...)
```

✅ **Use namespaces/prefixes**
```python
# Avoid key collisions
cache.set("user:profile:123", ...)
cache.set("user:settings:123", ...)

# Easy batch invalidation
cache.delete_pattern("user:*:123")
```

## Interview Tips

**Q: "How would you implement caching for a social media feed?"**

**A:**
```
1. Cache-aside for user feeds (Redis)
2. TTL: 5-10 minutes (balance freshness vs load)
3. Invalidate on new post (write-through for author's feed)
4. Pre-compute feeds for active users (refresh-ahead)
5. Fallback to DB on cache miss
```

**Q: "Cache hit rate is 50%. How to improve?"**

**A:**
```
1. Increase cache size (more data fits)
2. Optimize TTL (less premature eviction)
3. Identify hot keys (cache more aggressively)
4. Pre-warm cache (popular items)
5. Use tiered caching (local + distributed)
```

**Q: "How to handle cache invalidation for related data?"**

**A:**
```
Option 1: Tag-based invalidation (group related keys)
Option 2: Publish/subscribe (notify all caches)
Option 3: Short TTL (eventual consistency)
Option 4: Versioned keys (user:123:v2)
```

**Key Takeaway:** Caching dramatically improves performance but requires careful invalidation strategy. Start simple (cache-aside with TTL), iterate based on metrics!
