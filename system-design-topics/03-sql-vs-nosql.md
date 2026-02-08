# SQL vs NoSQL

## Definition

**SQL (Relational) Databases** organize data into structured tables with predefined schemas and relationships.

**NoSQL (Non-Relational) Databases** offer flexible data models optimized for specific use cases, without requiring fixed schemas.

## SQL Databases

### Characteristics
- ✅ Structured schema (tables, rows, columns)
- ✅ ACID transactions
- ✅ Relationships (foreign keys)
- ✅ Powerful queries (JOIN, aggregate)
- ✅ Data integrity constraints
- ✅ Mature ecosystem (40+ years)

### Popular SQL Databases

**PostgreSQL**
- Open-source, feature-rich
- Advanced data types (JSON, arrays)
- Used by: Instagram, Reddit, Apple

**MySQL/MariaDB**
- Most popular open-source
- Good read performance
- Used by: Facebook, Twitter, YouTube

**SQL Server**
- Microsoft's enterprise database
- Strong Windows integration
- Used by: Stack Overflow, Dell

**Oracle**
- Enterprise-grade
- Expensive but powerful
- Used by: Banks, governments

## NoSQL Databases

### Types of NoSQL

#### 1. Document Databases
**MongoDB, CouchDB, Firestore**

```json
{
  "_id": "user_123",
  "name": "Alice",
  "email": "alice@example.com",
  "addresses": [
    {"type": "home", "city": "SF"},
    {"type": "work", "city": "NYC"}
  ]
}
```

**Use cases:**
- Content management
- User profiles
- Catalogs

**Used by:**
- MongoDB: Uber, eBay, Cisco
- Firestore: Duolingo, Todoist

#### 2. Key-Value Stores
**Redis, DynamoDB, Memcached**

```
Key: "user:123:cart"
Value: ["item_1", "item_2", "item_3"]
```

**Use cases:**
- Caching
- Session storage
- Real-time analytics
- Shopping carts

**Used by:**
- Redis: Twitter, GitHub, Stack Overflow
- DynamoDB: Amazon, Lyft, Samsung

#### 3. Column-Family Stores
**Cassandra, HBase, ScyllaDB**

```
RowKey: user_123
  - profile:name = "Alice"
  - profile:email = "alice@example.com"
  - stats:login_count = 42
  - stats:last_login = "2026-02-08"
```

**Use cases:**
- Time-series data
- Event logging
- IoT data
- Analytics

**Used by:**
- Cassandra: Netflix, Discord, Apple
- HBase: Facebook, Adobe

#### 4. Graph Databases
**Neo4j, Amazon Neptune, ArangoDB**

```
(Alice)-[:FRIENDS_WITH]->(Bob)
(Alice)-[:WORKS_AT]->(Company_X)
(Bob)-[:WORKS_AT]->(Company_Y)
```

**Use cases:**
- Social networks
- Recommendation engines
- Fraud detection
- Knowledge graphs

**Used by:**
- Neo4j: NASA, eBay, Walmart
- Neptune: Amazon (internal)

## Real-World Examples

### Netflix
**Uses both:**
- **MySQL**: Billing, subscription management (needs ACID)
- **Cassandra**: Viewing history, 1+ trillion requests/day (needs scale)

### Facebook/Meta
**SQL:**
- **MySQL (TAO)**: Social graph queries, friend relationships
- Each user query touches hundreds of servers

**NoSQL:**
- **Cassandra**: Instagram messages (~400 million photos/day)
- **RocksDB**: Graph data storage
- **Memcached**: Caching layer (95%+ cache hit rate)

### Uber
**SQL:**
- **PostgreSQL/MySQL**: Transaction data, trip records

**NoSQL:**
- **Schemaless (MySQL + JSON)**: User profiles, driver locations
- **Cassandra**: Time-series data (GPS points)
- **Redis**: Real-time matching, caching

### Twitter
**SQL:**
- **MySQL**: User data, relationships (who follows whom)

**NoSQL:**
- **Manhattan (proprietary)**: Tweets, DMs
- **Redis**: Timeline caching
- Processes: 400+ million tweets/day, 6000+ tweets/second

### Airbnb
**SQL:**
- **PostgreSQL**: Bookings, payments, inventory

**NoSQL:**
- **Elasticsearch**: Search functionality
- **Redis**: Caching, rate limiting

## Comparison

| Feature | SQL | NoSQL |
|---------|-----|-------|
| **Schema** | Fixed, predefined | Flexible, dynamic |
| **Scalability** | Vertical (harder to scale) | Horizontal (easy to scale) |
| **Transactions** | ACID guaranteed | Varies (often eventual consistency) |
| **Joins** | Powerful, native | Limited or application-level |
| **Data Integrity** | Enforced (constraints) | Application-level |
| **Query Language** | SQL (standardized) | Database-specific |
| **Use Case** | Complex queries, relationships | High throughput, simple queries |
| **Maturity** | Very mature (40+ years) | Newer (10-20 years) |

## When to Use SQL

✅ **Complex relationships and joins**
```sql
SELECT o.id, u.name, p.title, SUM(oi.quantity * p.price)
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
WHERE o.created_at > '2026-01-01'
GROUP BY o.id;
```

✅ **ACID transactions required**
- Financial applications
- Inventory management
- Booking systems

✅ **Well-defined schema**
- Stable data structure
- Data integrity critical

✅ **Complex analytics queries**
- Reports with aggregations
- Business intelligence
- Data warehousing

✅ **Small to medium datasets** (< millions of rows)

## When to Use NoSQL

✅ **Massive scale (millions of operations/second)**
- Social media activity feeds
- IoT sensor data
- Real-time analytics

✅ **Flexible/evolving schema**
```javascript
// Different users can have different fields
{id: 1, name: "Alice", email: "alice@example.com"}
{id: 2, name: "Bob", twitter: "@bob", github: "bobdev"}
```

✅ **Distributed/geographical deployment**
- Multi-region data centers
- Edge computing
- Global applications

✅ **Specific access patterns**
- Key-value lookups (user sessions)
- Time-series data (metrics, logs)
- Graph traversals (social networks)

✅ **High write throughput**
- Logging systems
- Click-stream data
- Event tracking

## Hybrid Approaches

### Polyglot Persistence
Use the best database for each use case:

**Example E-commerce Stack:**
```
- PostgreSQL: Orders, payments, inventory
- Redis: Shopping cart, session data
- Elasticsearch: Product search
- MongoDB: Product catalog, reviews
- Neo4j: Recommendations ("you might also like")
```

### SQL Databases with NoSQL Features

**PostgreSQL:**
```sql
-- JSON column for flexibility
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  metadata JSONB  -- NoSQL-style flexible data
);

-- Query JSON data
SELECT * FROM users WHERE metadata->>'city' = 'San Francisco';
```

**MySQL:**
```sql
-- JSON support (5.7+)
CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  attributes JSON
);

-- Array functions
SELECT * FROM products WHERE JSON_CONTAINS(attributes, '["wireless"]');
```

## Migration Challenges

### SQL → NoSQL

**Challenges:**
- No native joins (denormalize data)
- Application-level integrity checks
- Different query patterns
- Learning curve

**When to migrate:**
- Hitting scalability limits
- Need better availability
- Simple data model

### NoSQL → SQL

**Challenges:**
- Schema design complexity
- Performance with large datasets
- Sharding/partitioning needs

**When to migrate:**
- Need complex queries/joins
- Data integrity issues
- Transaction requirements grow

## Performance Considerations

### SQL Strengths
- Complex joins
- Aggregations
- Consistent reads
- Range queries with indexes

### NoSQL Strengths
- Simple key lookups (O(1))
- Horizontal scaling
- Write-heavy workloads
- Eventual consistency acceptable

## Cost Considerations

### SQL
- **Vertical scaling**: Expensive (bigger servers)
- **Licensing**: Can be costly (Oracle, SQL Server)
- **Managed services**: RDS, Cloud SQL ($$$)

### NoSQL
- **Horizontal scaling**: Cheaper (commodity hardware)
- **Open-source**: Many free options
- **Managed services**: DynamoDB (pay per request), MongoDB Atlas

## Interview Scenarios

### Question 1: Design Twitter
**Answer:**
```
SQL (MySQL): User accounts, relationships (followers)
NoSQL (Cassandra): Tweets, timeline (billions of tweets)
NoSQL (Redis): Timeline cache, trending topics
Reason: Different parts have different requirements
```

### Question 2: Design Banking System
**Answer:**
```
SQL (PostgreSQL): Primary database for all transactions
- Critical: ACID, integrity, audit trails
- Transactions: Transfers, deposits, withdrawals
- Reporting: Complex queries on transaction history

NoSQL (Redis): Caching layer only
- Session tokens
- Account balance cache
- But NOT source of truth
```

### Question 3: Design Instagram
**Answer:**
```
SQL: User accounts, relationships
NoSQL (Cassandra): Photos, comments, likes (massive scale)
NoSQL (Redis): Feed cache
Why both: Need ACID for accounts, scale for content
```

## Decision Framework

```
Start with SQL if:
├─ Data has clear relationships? YES
├─ Need complex queries? YES
├─ ACID required? YES
├─ Dataset < 10M rows? YES
└─ Team knows SQL? YES

Consider NoSQL if:
├─ Massive scale needed? YES (>10M ops/day)
├─ Flexible schema? YES
├─ Specific access patterns? YES (key-value, time-series)
├─ Horizontal scaling needed? YES
└─ Eventual consistency OK? YES
```

## Key Takeaways

1. **Not either/or**: Most large systems use both
2. **Start with SQL**: Easier to migrate SQL→NoSQL than reverse
3. **Use NoSQL for specific problems**: Cache, logs, time-series, graphs
4. **ACID matters**: If money/inventory involved, prefer SQL
5. **Scale matters**: NoSQL excels at web-scale (billions of operations)

**Golden Rule:** Use SQL by default; use NoSQL when you have a specific problem that NoSQL solves better.
