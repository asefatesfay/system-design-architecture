# Lab 1: URL Shortener - From 100 to 1M Users

> **Learn by building the same system 3 times at different scales**

---

## Overview

Build a URL shortener (like bit.ly) that evolves as your user base grows:
- **Part 1:** Single server for 100 users
- **Part 2:** Add caching for 10,000 users
- **Part 3:** Shard database for 1,000,000 users

**Total Time:** 3-4 hours

---

## Part 1: MVP - Single Server (100 Users)

### 🎯 Requirements

**Functional:**
- Shorten URL: `POST /shorten` → returns short URL
- Redirect: `GET /:short_code` → redirects to original URL
- Track clicks: Count how many times URL is accessed
- Custom aliases: Optional custom short code

**Non-Functional:**
- **Scale:** 100 users, 10 URL shortens/day, 100 redirects/day
- **Latency:** <500ms for both operations
- **Availability:** 95% uptime (can be down for maintenance)

### 📐 Design Decisions

**Database:** SQLite (simple, no setup, good for <100K records)
**Server:** Single Python/Go/Node server
**Deployment:** Single machine

### 🗃️ Database Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    click_count INTEGER DEFAULT 0,
    INDEX idx_short_code (short_code)
);
```

**Why this schema?**
- `short_code` indexed for fast lookups
- `click_count` for basic analytics
- Simple, normalized design

### 🔧 Tasks

#### Task 1.1: Generate Short Codes

Implement Base62 encoding:

```python
import random
import string

def generate_short_code(length=6):
    """Generate random 6-character code using Base62"""
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(chars, k=length))

# Calculate capacity:
# 62^6 = 56.8 billion possible URLs
```

**Why Base62?**
- URL-safe (no special characters)
- Case-sensitive (aB != Ab)
- 62^6 = 56B combinations (plenty for now)

#### Task 1.2: Implement Shorten Endpoint

```python
from flask import Flask, request, redirect, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """
    Input: {"url": "https://example.com/very/long/url"}
    Output: {"short_url": "http://short.ly/aB3d9f"}
    """
    data = request.json
    original_url = data.get('url')
    custom_alias = data.get('alias')  # Optional

    # Validate URL
    if not original_url or not is_valid_url(original_url):
        return jsonify({'error': 'Invalid URL'}), 400

    # Generate or use custom alias
    short_code = custom_alias if custom_alias else generate_short_code()

    # Save to database
    try:
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
            (short_code, original_url)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'short_url': f'http://short.ly/{short_code}',
            'short_code': short_code
        }), 201

    except sqlite3.IntegrityError:
        # Short code collision (rare with Base62)
        return jsonify({'error': 'Short code already exists'}), 409
```

#### Task 1.3: Implement Redirect Endpoint

```python
@app.route('/<short_code>')
def redirect_url(short_code):
    """
    Redirect to original URL and increment click counter
    """
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()

    # Get URL and increment counter in one query
    cursor.execute("""
        UPDATE urls
        SET click_count = click_count + 1
        WHERE short_code = ?
        RETURNING original_url
    """, (short_code,))

    result = cursor.fetchone()
    conn.commit()
    conn.close()

    if result:
        return redirect(result[0], code=301)  # Permanent redirect
    else:
        return jsonify({'error': 'URL not found'}), 404
```

#### Task 1.4: Add Analytics Endpoint

```python
@app.route('/analytics/<short_code>')
def get_analytics(short_code):
    """
    Get click statistics for a short URL
    """
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT short_code, original_url, created_at, click_count
        FROM urls
        WHERE short_code = ?
    """, (short_code,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({
            'short_code': result[0],
            'original_url': result[1],
            'created_at': result[2],
            'clicks': result[3]
        })
    else:
        return jsonify({'error': 'URL not found'}), 404
```

### 📊 Measure Performance

```bash
# Install Apache Bench
brew install httpd  # macOS

# Test shorten endpoint
ab -n 1000 -c 10 -p post_data.json -T application/json \
   http://localhost:5000/shorten

# Test redirect (warmup first)
ab -n 1000 -c 10 http://localhost:5000/abc123

# Expected:
# - 50-100 requests/sec
# - Average latency: 10-50ms
```

### ✅ Part 1 Checklist

- [ ] Short code generation works
- [ ] URLs are shortened successfully
- [ ] Redirects work correctly
- [ ] Click counting is accurate
- [ ] Handles duplicate short codes
- [ ] Performance: >50 RPS, <100ms average latency

### 🎓 What You Learned

1. **Base62 encoding** for URL-safe short codes
2. **Database indexing** for fast lookups
3. **Atomic updates** for click counting
4. **HTTP 301 redirect** for permanent redirects

---

## Part 2: Add Caching (10,000 Users)

### 💥 What Breaks?

**New requirements:**
- 10,000 users
- 1,000 new URLs/day
- 100,000 redirects/day
- Response time must be <100ms

**Problems:**
- SQLite can handle reads but becomes slow under load
- Every redirect hits database (expensive)
- Popular URLs get accessed frequently (hot keys)

**Bottleneck:** Database

### 🎯 Solution: Add Redis Cache

**Cache-aside pattern:**
1. Check cache first
2. If miss, query database
3. Store result in cache
4. Return result

### 🔧 Tasks

#### Task 2.1: Add Redis

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

```python
import redis

# Connect to Redis
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)
```

#### Task 2.2: Implement Cache-Aside Pattern

```python
import json

@app.route('/<short_code>')
def redirect_url(short_code):
    """
    Redirect with caching
    """
    # 1. Check cache first
    cached_url = cache.get(f'url:{short_code}')

    if cached_url:
        # Cache hit - no database query!
        cache.incr(f'clicks:{short_code}')  # Increment counter in Redis
        return redirect(cached_url, code=301)

    # 2. Cache miss - query database
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        original_url = result[0]

        # 3. Store in cache (TTL = 1 hour)
        cache.setex(f'url:{short_code}', 3600, original_url)

        # 4. Increment click counter
        cache.incr(f'clicks:{short_code}')

        return redirect(original_url, code=301)
    else:
        return jsonify({'error': 'URL not found'}), 404
```

#### Task 2.3: Background Job to Sync Clicks to DB

```python
import threading
import time

def sync_clicks_to_db():
    """
    Periodically sync click counts from Redis to SQLite
    """
    while True:
        # Get all click counters from Redis
        keys = cache.keys('clicks:*')

        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()

        for key in keys:
            short_code = key.replace('clicks:', '')
            clicks = int(cache.get(key) or 0)

            # Update database
            cursor.execute("""
                UPDATE urls
                SET click_count = click_count + ?
                WHERE short_code = ?
            """, (clicks, short_code))

            # Reset Redis counter
            cache.delete(key)

        conn.commit()
        conn.close()

        time.sleep(60)  # Sync every minute

# Start background thread
sync_thread = threading.Thread(target=sync_clicks_to_db, daemon=True)
sync_thread.start()
```

#### Task 2.4: Cache Warming

```python
def warm_cache():
    """
    Pre-load popular URLs into cache on startup
    """
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()

    # Get top 1000 most clicked URLs
    cursor.execute("""
        SELECT short_code, original_url
        FROM urls
        ORDER BY click_count DESC
        LIMIT 1000
    """)

    results = cursor.fetchall()
    conn.close()

    # Load into cache
    for short_code, original_url in results:
        cache.setex(f'url:{short_code}', 3600, original_url)

    print(f"Warmed cache with {len(results)} URLs")

# Call on startup
warm_cache()
```

### 📊 Measure Improvement

```bash
# Test with cache
ab -n 10000 -c 100 http://localhost:5000/abc123

# Expected improvements:
# - Before: 50-100 RPS, 50ms average
# - After: 5000+ RPS, 5-10ms average
# - 50-100x improvement!
```

### 🎯 Calculate Cache Hit Rate

```python
@app.route('/cache-stats')
def cache_stats():
    """
    Monitor cache performance
    """
    info = cache.info('stats')
    hits = int(info.get('keyspace_hits', 0))
    misses = int(info.get('keyspace_misses', 0))
    total = hits + misses
    hit_rate = (hits / total * 100) if total > 0 else 0

    return jsonify({
        'cache_hits': hits,
        'cache_misses': misses,
        'hit_rate': f'{hit_rate:.2f}%'
    })

# Target: >90% hit rate for popular URLs
```

### ✅ Part 2 Checklist

- [ ] Redis integrated successfully
- [ ] Cache-aside pattern implemented
- [ ] Click counts sync to database
- [ ] Cache warming on startup
- [ ] Performance: >1000 RPS, <20ms average
- [ ] Cache hit rate: >80%

### 🎓 What You Learned

1. **Cache-aside pattern** - Most common caching strategy
2. **Cache warming** - Pre-load popular data
3. **Eventual consistency** - Clicks sync eventually (acceptable trade-off)
4. **Performance measurement** - Before/after comparison
5. **Cache hit rate** - Key metric for cache effectiveness

---

## Part 3: Shard Database (1,000,000 Users)

### 💥 What Breaks?

**New requirements:**
- 1,000,000 users
- 100,000 new URLs/day
- 10,000,000 redirects/day
- Must support custom analytics

**Problems:**
- Single SQLite database can't handle write load
- Need to upgrade to PostgreSQL
- Even single PostgreSQL will struggle with this write load
- Need database sharding

### 🎯 Solution: Shard by Short Code

**Sharding strategy:** Hash-based sharding
- Hash short code → Shard ID
- 4 database shards
- Each shard handles ~250K users

### 🔧 Tasks

#### Task 3.1: Setup PostgreSQL Shards

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres-shard-0:
    image: postgres:15
    environment:
      POSTGRES_DB: urls_shard_0
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  postgres-shard-1:
    image: postgres:15
    environment:
      POSTGRES_DB: urls_shard_1
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"

  postgres-shard-2:
    image: postgres:15
    environment:
      POSTGRES_DB: urls_shard_2
      POSTGRES_PASSWORD: password
    ports:
      - "5434:5432"

  postgres-shard-3:
    image: postgres:15
    environment:
      POSTGRES_DB: urls_shard_3
      POSTGRES_PASSWORD: password
    ports:
      - "5435:5432"
```

#### Task 3.2: Implement Shard Router

```python
import hashlib
import psycopg2
from psycopg2.pool import SimpleConnectionPool

# Database connection pools for each shard
SHARD_COUNT = 4
db_pools = []

for i in range(SHARD_COUNT):
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=20,
        host='localhost',
        port=5432 + i,
        database=f'urls_shard_{i}',
        user='postgres',
        password='password'
    )
    db_pools.append(pool)

def get_shard_id(short_code):
    """
    Determine which shard to use based on short code
    """
    hash_value = int(hashlib.md5(short_code.encode()).hexdigest(), 16)
    return hash_value % SHARD_COUNT

def get_connection(short_code):
    """
    Get database connection for the appropriate shard
    """
    shard_id = get_shard_id(short_code)
    return db_pools[shard_id].getconn()

def return_connection(short_code, conn):
    """
    Return connection to pool
    """
    shard_id = get_shard_id(short_code)
    db_pools[shard_id].putconn(conn)
```

#### Task 3.3: Update Shorten Endpoint

```python
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')

    # Generate short code
    short_code = generate_short_code()

    # Get connection for this shard
    conn = get_connection(short_code)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO urls (short_code, original_url, created_at)
            VALUES (%s, %s, NOW())
        """, (short_code, original_url))
        conn.commit()

        return jsonify({
            'short_url': f'http://short.ly/{short_code}',
            'shard_id': get_shard_id(short_code)  # For debugging
        }), 201

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': 'Short code collision'}), 409
    finally:
        return_connection(short_code, conn)
```

#### Task 3.4: Update Redirect Endpoint

```python
@app.route('/<short_code>')
def redirect_url(short_code):
    # Check cache first (same as Part 2)
    cached_url = cache.get(f'url:{short_code}')
    if cached_url:
        cache.incr(f'clicks:{short_code}')
        return redirect(cached_url, code=301)

    # Cache miss - query appropriate shard
    conn = get_connection(short_code)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT original_url FROM urls WHERE short_code = %s
    """, (short_code,))

    result = cursor.fetchone()
    return_connection(short_code, conn)

    if result:
        original_url = result[0]
        cache.setex(f'url:{short_code}', 3600, original_url)
        cache.incr(f'clicks:{short_code}')
        return redirect(original_url, code=301)
    else:
        return jsonify({'error': 'URL not found'}), 404
```

#### Task 3.5: Cross-Shard Analytics

```python
@app.route('/analytics/global')
def global_analytics():
    """
    Get analytics across all shards (expensive query!)
    """
    total_urls = 0
    total_clicks = 0

    # Query all shards
    for shard_id in range(SHARD_COUNT):
        conn = db_pools[shard_id].getconn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*), SUM(click_count)
            FROM urls
        """)

        result = cursor.fetchone()
        total_urls += result[0] or 0
        total_clicks += result[1] or 0

        db_pools[shard_id].putconn(conn)

    return jsonify({
        'total_urls': total_urls,
        'total_clicks': total_clicks,
        'average_clicks_per_url': total_clicks / total_urls if total_urls > 0 else 0
    })
```

### 📊 Measure Sharding Impact

```bash
# Test write performance
ab -n 100000 -c 100 -p post_data.json -T application/json \
   http://localhost:5000/shorten

# Expected:
# - Write throughput: 5000-10000 writes/sec
# - Read throughput: 50000+ reads/sec (thanks to cache)
# - Latency: <50ms p99
```

### 🔍 Monitor Shard Distribution

```python
@app.route('/shard-stats')
def shard_stats():
    """
    Check if data is evenly distributed across shards
    """
    shard_counts = []

    for shard_id in range(SHARD_COUNT):
        conn = db_pools[shard_id].getconn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM urls")
        count = cursor.fetchone()[0]
        shard_counts.append(count)
        db_pools[shard_id].putconn(conn)

    return jsonify({
        'shard_distribution': {
            f'shard_{i}': count
            for i, count in enumerate(shard_counts)
        },
        'std_dev': calculate_std_dev(shard_counts),
        'is_balanced': is_balanced(shard_counts)  # Should be roughly equal
    })
```

### ✅ Part 3 Checklist

- [ ] 4 PostgreSQL shards running
- [ ] Shard router implemented
- [ ] Data evenly distributed (check std dev)
- [ ] Cache still working
- [ ] Performance: >5000 writes/sec, >50K reads/sec
- [ ] Can handle 10M redirects/day

### 🎓 What You Learned

1. **Database sharding** - Horizontal partitioning for write scaling
2. **Hash-based sharding** - Even distribution using MD5 hash
3. **Connection pooling** - Reuse connections, don't create per request
4. **Cross-shard queries** - Expensive, avoid in critical path
5. **Monitoring shard balance** - Ensure even distribution

---

## 🎯 Bonus Challenges

### Challenge 1: Handle Shard Rebalancing
**Problem:** You started with 4 shards, now need 8 shards
**Solution:** Implement consistent hashing instead of modulo

### Challenge 2: Add Analytics
**Problem:** Need click analytics by date, country, referrer
**Solution:** Use ClickHouse or BigQuery for analytics, separate from transactional DB

### Challenge 3: Handle Hot Keys
**Problem:** One URL gets 1M clicks/sec (viral content)
**Solution:** Add CDN layer, cache at edge

### Challenge 4: Custom Domains
**Problem:** Users want custom domains (short.nike.com/abc123)
**Solution:** Add domain routing, virtual hosting

### Challenge 5: URL Expiration
**Problem:** URLs should expire after N days
**Solution:** Add TTL field, background cleanup job

---

## 📊 Final Comparison

| Metric | Part 1 | Part 2 | Part 3 |
|--------|--------|--------|--------|
| **Users** | 100 | 10,000 | 1,000,000 |
| **Write RPS** | 10 | 100 | 5,000+ |
| **Read RPS** | 50 | 5,000 | 50,000+ |
| **Latency (p99)** | 100ms | 20ms | 50ms |
| **Storage** | SQLite | SQLite + Redis | PostgreSQL x4 + Redis |
| **Complexity** | Low | Medium | High |
| **Cost/month** | $0 | $50 | $500 |

---

## 🎓 Key Takeaways

### 1. **Scale Progressively**
Don't over-engineer for scale you don't have. Build for current needs + 10x.

### 2. **Caching is Powerful**
90%+ cache hit rate can handle 100x more traffic with same database.

### 3. **Sharding is Last Resort**
Shard when single database can't handle load. Adds significant complexity.

### 4. **Measure Everything**
You can't optimize what you don't measure. Benchmark before and after.

### 5. **Trade-offs Matter**
- **Eventual consistency** (click counts) - acceptable for analytics
- **Strong consistency** (URL mapping) - critical, can't be stale
- **Complexity vs Scale** - only add complexity when needed

---

## 🔗 Related Topics

**System Design Concepts:**
- [07-Caching](../../../system-design-topics/07-caching.md)
- [20-Database Sharding](../../../system-design-topics/20-database-sharding.md)
- [21-Consistent Hashing](../../../system-design-topics/21-consistent-hashing.md)

**Design Patterns:**
- Cache-Aside Pattern
- Sharding Pattern
- Connection Pooling

**Next Labs:**
- [Lab 2: Rate Limiter](./02-rate-limiter.md)
- [Lab 3: Distributed Cache](./03-distributed-cache.md)

---

## ✅ Solution Code

**Full implementation:** [../solutions/01-url-shortener/](../solutions/01-url-shortener/)
- Python version
- Go version
- Node.js version
- Docker setup
- Load testing scripts

---

**Congratulations!** 🎉 You just built a production-ready URL shortener that scales from 100 to 1M users!

**Next:** Try [Lab 2: Rate Limiter](./02-rate-limiter.md) to learn rate limiting algorithms.
