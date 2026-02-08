# Database Index

## Definition

A **Database Index** is a data structure that improves the speed of data retrieval operations on a table at the cost of additional storage space and slower writes. Think of it like a book's index that helps you find topics quickly without reading every page.

## Key Concepts

### How Indexes Work

**Without Index (Full Table Scan):**
```sql
SELECT * FROM users WHERE email = 'alice@example.com';
-- Database scans ALL rows: O(n)
-- 1 million rows = 1 million checks
```

**With Index:**
```sql
CREATE INDEX idx_email ON users(email);
SELECT * FROM users WHERE email = 'alice@example.com';
-- Database uses index: O(log n)
-- 1 million rows = ~20 checks (binary search in B-tree)
```

### Common Index Types

#### 1. B-Tree Index (Most Common)
- Default in most databases
- Good for: equality and range queries
- Structure: Balanced tree with sorted keys

```sql
CREATE INDEX idx_created_at ON orders(created_at);

-- Fast queries:
SELECT * FROM orders WHERE created_at > '2026-01-01';  -- Range
SELECT * FROM orders WHERE created_at = '2026-02-08';  -- Equality
```

#### 2. Hash Index
- Fast for equality checks (O(1))
- Cannot do range queries
- Used in: Memory tables, PostgreSQL partial support

```sql
CREATE INDEX idx_user_id USING HASH ON sessions(user_id);

-- Fast:
SELECT * FROM sessions WHERE user_id = 123;

-- Cannot use index:
SELECT * FROM sessions WHERE user_id > 100;  -- Range not supported
```

#### 3. Full-Text Index
- For searching text content
- Supports: word matching, ranking, stemming

```sql
CREATE FULLTEXT INDEX idx_content ON articles(title, body);

-- Full-text search:
SELECT * FROM articles WHERE MATCH(title, body) AGAINST('database indexing');
```

#### 4. Composite (Multi-Column) Index
- Index on multiple columns
- Order matters!

```sql
CREATE INDEX idx_user_category ON products(user_id, category);

-- Uses index (left-to-right):
WHERE user_id = 123 AND category = 'electronics'  ✅
WHERE user_id = 123                                ✅

-- Cannot use index:
WHERE category = 'electronics'                     ❌
```

#### 5. Unique Index
- Ensures column values are unique
- Automatically created for PRIMARY KEY and UNIQUE constraints

```sql
CREATE UNIQUE INDEX idx_unique_email ON users(email);
-- Prevents duplicate emails
```

#### 6. Partial/Filtered Index
- Index only subset of rows

```sql
-- PostgreSQL
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- SQL Server
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

## Real-World Examples

### Google Search
**Challenge:** Search billions of web pages in milliseconds

**Solution:**
- Inverted index: word → list of pages containing that word
- When you search "database indexing":
  1. Look up "database" in index → Pages [1, 5, 100, 203, ...]
  2. Look up "indexing" in index → Pages [1, 42, 100, 501, ...]
  3. Intersect the lists → Pages [1, 100]
  4. Rank results
  
**Result:** Billions of pages searched in ~0.2 seconds

### Facebook
**Challenge:** Find user by email from 3+ billion users

```sql
-- Without index: Scans 3 billion rows (minutes)
-- With index on email: O(log n) = ~32 lookups (milliseconds)
CREATE UNIQUE INDEX idx_email ON users(email);
```

**Other indexes:**
```sql
-- Friend lookups
CREATE INDEX idx_friends ON friendships(user_id, friend_id);

-- Content feed (composite index)
CREATE INDEX idx_feed ON posts(user_id, created_at DESC);
```

### Twitter
**Challenge:** Query tweets by user and date

```sql
-- Composite index: user first, then date
CREATE INDEX idx_user_tweets ON tweets(user_id, created_at DESC);

-- Fast query:
SELECT * FROM tweets 
WHERE user_id = 'elonmusk' 
ORDER BY created_at DESC 
LIMIT 20;
```

**What they index:**
- User IDs (lookup tweets by user)
- Tweet IDs (lookup specific tweet)
- Hashtags (trending topics)
- Timestamps (recent tweets)

### E-commerce (Amazon, eBay)

```sql
-- Product search
CREATE INDEX idx_category_price ON products(category, price);

-- Fast query:
SELECT * FROM products 
WHERE category = 'electronics' 
  AND price BETWEEN 100 AND 500
ORDER BY price ASC;

-- Order history lookup
CREATE INDEX idx_user_orders ON orders(user_id, created_at DESC);
```

### Uber/Lyft - Geospatial Queries

```sql
-- PostGIS spatial index
CREATE INDEX idx_location ON drivers USING GIST(location);

-- Find nearby drivers
SELECT * FROM drivers 
WHERE ST_DWithin(location, ST_Point(-122.4, 37.8), 5000)  -- Within 5km
  AND status = 'available';
```

## When to Create Indexes

✅ **Columns in WHERE clauses**
```sql
CREATE INDEX idx_status ON orders(status);
-- For: WHERE status = 'pending'
```

✅ **Columns in JOIN conditions**
```sql
CREATE INDEX idx_user_id ON orders(user_id);
-- For: JOIN orders ON orders.user_id = users.id
```

✅ **Columns in ORDER BY**
```sql
CREATE INDEX idx_created ON posts(created_at DESC);
-- For: ORDER BY created_at DESC
```

✅ **Foreign keys**
```sql
CREATE INDEX idx_fk_category ON products(category_id);
-- Speeds up: JOIN categories ON products.category_id = categories.id
```

✅ **Columns with high selectivity**
- Email, username: High selectivity (unique values) ✅
- Gender, boolean: Low selectivity (few values) ❌

## When NOT to Create Indexes

❌ **Small tables** (< 1000 rows)
- Full table scan might be faster

❌ **Columns rarely queried**
- Wastes space and slows writes

❌ **High write/low read tables**
- Logs, audit trails
- Index maintenance overhead exceeds benefit

❌ **Columns with low selectivity**
```sql
-- BAD: Only 2 possible values
CREATE INDEX idx_gender ON users(gender);  -- male/female
```

❌ **Every column**
- Indexes have costs (storage, write performance)

## Costs of Indexes

### Storage Overhead
- Each index copies data
- Can double database size
- Example: 100GB table + 5 indexes = 150-200GB total

### Write Performance Impact

**INSERT:**
```sql
-- Without index: Write 1 row
-- With 5 indexes: Write 1 row + update 5 indexes
```

**UPDATE:**
```sql
UPDATE users SET email = 'new@example.com' WHERE id = 123;
-- Update table + update email index
```

**DELETE:**
```sql
DELETE FROM users WHERE id = 123;
-- Delete row + delete from all indexes
```

**Benchmark example:**
| Operation | No Indexes | 5 Indexes | Slowdown |
|-----------|------------|-----------|----------|
| INSERT | 1ms | 5ms | 5x slower |
| UPDATE | 2ms | 8ms | 4x slower |
| SELECT by ID | 10ms | 0.1ms | **100x faster** |

## Index Optimization Strategies

### 1. Covering Index
Include all columns needed in query:

```sql
-- Query:
SELECT user_id, created_at, status 
FROM orders 
WHERE status = 'pending';

-- Covering index (no table lookup needed):
CREATE INDEX idx_covering ON orders(status, user_id, created_at);
```

### 2. Index Column Order (Composite Indexes)

**Rule:** Most selective columns first (usually)

```sql
-- users table: 1M rows, 100 admins, 10K active

-- GOOD: Narrow down quickly
CREATE INDEX idx ON users(is_admin, status, created_at);
WHERE is_admin = true AND status = 'active'  -- 10 rows

-- BAD: Too broad initially
CREATE INDEX idx ON users(status, is_admin, created_at);
WHERE status = 'active' AND is_admin = true  -- 10K rows first
```

### 3. Partial Indexes (Save Space)

```sql
-- Only index active users (most queries)
CREATE INDEX idx_active ON users(email) WHERE status = 'active';

-- Instead of indexing all 10M users, index 8M active ones
```

### 4. Index-Only Scans

```sql
-- PostgreSQL
CREATE INDEX idx ON orders(user_id, total_amount);

-- Index-only scan (no table access):
SELECT user_id, SUM(total_amount) 
FROM orders 
GROUP BY user_id;
```

## Analyzing Index Usage

### PostgreSQL
```sql
-- Check if index is used
EXPLAIN ANALYZE 
SELECT * FROM orders WHERE status = 'pending';

-- Output shows:
-- Index Scan using idx_status on orders (cost=0..100 rows=50)

-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexname NOT LIKE '%_pkey';
```

### MySQL
```sql
-- Check index usage
EXPLAIN SELECT * FROM orders WHERE status = 'pending';

-- Rows examined:
-- GOOD: rows=100
-- BAD: rows=1000000 (full table scan)

-- Find unused indexes
SELECT * FROM sys.schema_unused_indexes;
```

## Common Pitfalls

### 1. Not Using Index (Functions)

```sql
-- Index NOT used:
SELECT * FROM users WHERE LOWER(email) = 'alice@example.com';

-- Solution: Function-based index
CREATE INDEX idx_lower_email ON users(LOWER(email));
```

### 2. Implicit Type Conversion

```sql
-- user_id is VARCHAR, but query uses integer
SELECT * FROM users WHERE user_id = 123;  -- Index NOT used!

-- Solution: Match types
SELECT * FROM users WHERE user_id = '123';  -- Index used
```

### 3. OR Clauses

```sql
-- May not use index efficiently:
SELECT * FROM orders WHERE status = 'pending' OR user_id = 123;

-- Better: Use UNION
SELECT * FROM orders WHERE status = 'pending'
UNION
SELECT * FROM orders WHERE user_id = 123;
```

### 4. Leading Wildcards

```sql
-- Index NOT used:
SELECT * FROM users WHERE email LIKE '%@gmail.com';

-- Index used:
SELECT * FROM users WHERE email LIKE 'alice%';
```

## Best Practices

✅ **Start simple, add as needed**
- Don't create indexes prematurely
- Monitor slow queries, then optimize

✅ **Analyze query patterns**
- What columns appear in WHERE?
- What's the ORDER BY?
- Which JOINs are slow?

✅ **Monitor index usage**
- Remove unused indexes
- Update statistics regularly

✅ **Consider write/read ratio**
- Read-heavy: More indexes
- Write-heavy: Fewer indexes

✅ **Test with production-like data**
- Indexes on small datasets misleading
- Load test with millions of rows

## Interview Tips

**Q: "How would you optimize this slow query?"**
```sql
SELECT * FROM orders WHERE user_id = 123 ORDER BY created_at DESC;
```

**A:**
1. Check if indexes exist: `EXPLAIN` the query
2. If not, create composite index: `CREATE INDEX idx ON orders(user_id, created_at DESC)`
3. Verify improvement with `EXPLAIN ANALYZE`
4. Monitor query performance over time

**Q: "When would you NOT use an index?"**

**A:**
- Small tables (full scan faster)
- Low selectivity columns
- High write, low read workloads
- Temporary/staging tables

**Key Takeaway:** Indexes are like book indexes—they speed up finding information but take space and must be maintained. Use strategically based on query patterns!
