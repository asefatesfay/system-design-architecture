# Performance Antipatterns Cheat Sheet

Quick reference guide for identifying and fixing common performance antipatterns.

## 🔍 Quick Identification

| Symptom | Likely Antipattern | Quick Check |
|---------|-------------------|-------------|
| High memory usage, GC pressure | Improper Instantiation | Are you creating expensive objects repeatedly? |
| Low throughput under load | Synchronous I/O | Are you waiting for I/O sequentially? |
| Many small DB queries | Chatty I/O | Do you have N+1 query problems? |
| Same queries repeating | No Caching | Are you fetching the same data repeatedly? |
| Database CPU at 100% | Busy Database | Is business logic in stored procedures? |
| Failures cascade/amplify | Retry Storm | Do retries have backoff & circuit breakers? |
| Scaling difficulties | Monolithic Persistence | Is one DB handling all data types? |
| Inconsistent performance | Noisy Neighbor | Are resources properly isolated per tenant? |
| High network traffic | Extraneous Fetching | Are you using SELECT * or loading full objects? |
| Slow mobile experience | Busy Frontend | Is business logic running in the client? |

## ⚡ Quick Fixes

### 1. Improper Instantiation
```go
// ❌ Bad
func handler() {
    db, _ := sql.Open("postgres", connStr)  // Every request!
    defer db.Close()
}

// ✅ Good
var db *sql.DB  // Package level

func init() {
    db, _ = sql.Open("postgres", connStr)  // Once at startup
}
```

### 2. Synchronous I/O
```go
// ❌ Bad: Sequential
user := fetchUser()      // Wait
posts := fetchPosts()    // Wait
comments := fetchComments()  // Wait

// ✅ Good: Concurrent
var wg sync.WaitGroup
wg.Add(3)
go func() { user = fetchUser(); wg.Done() }()
go func() { posts = fetchPosts(); wg.Done() }()
go func() { comments = fetchComments(); wg.Done() }()
wg.Wait()
```

### 3. Chatty I/O (N+1)
```sql
-- ❌ Bad: N+1 queries
SELECT * FROM orders WHERE user_id = 1;
SELECT * FROM items WHERE order_id = 101;  -- For each order!
SELECT * FROM items WHERE order_id = 102;
SELECT * FROM items WHERE order_id = 103;

-- ✅ Good: One query with JOIN
SELECT o.*, i.* 
FROM orders o 
LEFT JOIN items i ON o.id = i.order_id 
WHERE o.user_id = 1;
```

### 4. No Caching
```go
// ❌ Bad: Always hit database
func getProduct(id int) (*Product, error) {
    return db.QueryRow("SELECT * FROM products WHERE id = ?", id)
}

// ✅ Good: Cache-aside pattern
func getProduct(id int) (*Product, error) {
    // Try cache first
    if cached, err := redis.Get("product:" + id); err == nil {
        return cached, nil
    }
    
    // Cache miss - query DB
    product, err := db.QueryRow("SELECT * FROM products WHERE id = ?", id)
    if err != nil {
        return nil, err
    }
    
    // Cache for next time
    redis.Set("product:" + id, product, 5*time.Minute)
    return product, nil
}
```

### 5. Busy Database
```sql
-- ❌ Bad: Complex aggregation in DB
SELECT 
    category,
    SUM(amount) as total,
    AVG(amount) as avg,
    COUNT(*) as count,
    -- Complex window functions
    RANK() OVER (PARTITION BY category ORDER BY amount DESC) as rank
FROM sales
GROUP BY category;

-- ✅ Good: Simple query, aggregate in app
SELECT category, amount FROM sales;
```

```go
// Process in application memory
for _, sale := range sales {
    categoryTotals[sale.Category] += sale.Amount
}
```

### 6. Retry Storm
```go
// ❌ Bad: Immediate retry
for i := 0; i < 5; i++ {
    resp, err := http.Get(url)
    if err == nil { return resp }
    // No delay!
}

// ✅ Good: Exponential backoff + jitter
for i := 0; i < 5; i++ {
    resp, err := http.Get(url)
    if err == nil { return resp }
    
    delay := time.Duration(math.Pow(2, float64(i))) * 100 * time.Millisecond
    jitter := time.Duration(rand.Float64() * 0.25 * float64(delay))
    time.Sleep(delay + jitter)
}
```

### 7. Monolithic Persistence
```go
// ❌ Bad: Everything in one PostgreSQL
postgres.Store(userAuth)        // High consistency needed
postgres.Store(sessionData)     // Fast access needed
postgres.Store(mediaFiles)      // Large blobs
postgres.Store(analytics)       // Write-heavy

// ✅ Good: Right tool for each job
postgres.Store(userAuth)        // ACID for critical data
redis.Store(sessionData)        // Fast TTL-based storage
s3.Store(mediaFiles)           // Blob storage
influxdb.Store(analytics)      // Time-series optimized
```

### 8. Noisy Neighbor
```go
// ❌ Bad: No limits
func handler(tenantID string) {
    // Tenant can consume unlimited resources
    runExpensiveQuery()
}

// ✅ Good: Per-tenant rate limiting
func handler(tenantID string) {
    if !rateLimiter.Allow(tenantID) {
        return http.StatusTooManyRequests
    }
    runExpensiveQuery()
}
```

### 9. Extraneous Fetching
```go
// ❌ Bad: Fetch everything
type User struct {
    ID, Name, Email, PasswordHash string
    Address, Phone, Bio, Preferences string
    LoginHistory []Login  // Large array
}
users := db.Query("SELECT * FROM users")

// ✅ Good: Fetch only what's needed
type UserListDTO struct {
    ID, Name, Email string
}
users := db.Query("SELECT id, name, email FROM users")
```

### 10. Busy Frontend
```javascript
// ❌ Bad: Heavy computation in client
const sortedProducts = products.sort((a, b) => {
  return calculateComplexScore(a) - calculateComplexScore(b);
});

// ✅ Good: Backend does heavy lifting
const products = await fetch('/api/products?sort=relevance');
```

## 🎯 Detection Commands

```bash
# High connection creation rate
netstat -an | grep ESTABLISHED | wc -l

# Database query analysis
EXPLAIN ANALYZE SELECT ...;

# Memory allocations
go test -bench=. -benchmem

# HTTP request times
curl -w "Time: %{time_total}s\n" http://localhost:8080/api

# Load test
hey -n 1000 -c 50 http://localhost:8080/api

# Database connections
SELECT count(*) FROM pg_stat_activity;

# Cache hit rate
redis-cli INFO stats | grep keyspace_hits
```

## 📊 Performance Targets

| Metric | Target | Red Flag |
|--------|--------|----------|
| API Response Time (p95) | < 200ms | > 1s |
| Database Query Time | < 50ms | > 500ms |
| Cache Hit Rate | > 80% | < 50% |
| Connection Pool Usage | < 70% | > 90% |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 90% |
| Memory Usage | < 80% | > 95% |
| Goroutines | Stable | Growing |

## 🔧 Go-Specific Tips

```go
// Use sync.Pool for frequently allocated objects
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

// Context for timeouts
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// Buffered channels for async work
results := make(chan Result, 100)

// Limit concurrency with worker pool
sem := make(chan struct{}, 10)  // Max 10 concurrent

// Close HTTP response bodies
defer resp.Body.Close()

// Use strings.Builder for string concatenation
var sb strings.Builder
for _, s := range strings {
    sb.WriteString(s)
}
result := sb.String()
```

## 📝 Code Review Checklist

- [ ] Are database connections pooled and reused?
- [ ] Are HTTP clients reused (not created per request)?
- [ ] Are regex patterns pre-compiled?
- [ ] Are I/O operations done concurrently when possible?
- [ ] Is there an N+1 query problem?
- [ ] Is caching used for frequently accessed data?
- [ ] Are queries fetching only needed columns?
- [ ] Is pagination implemented for large datasets?
- [ ] Do retries have exponential backoff?
- [ ] Are circuit breakers in place for external calls?
- [ ] Is business logic in the backend (not frontend)?
- [ ] Are resources limited per tenant?
- [ ] Is `SELECT *` avoided?
- [ ] Are timeouts set on all I/O operations?

## 🚨 Red Flags in Code

```go
// 🚨 Creating DB connection in handler
func handler() {
    db, _ := sql.Open(...)
}

// 🚨 Sequential I/O operations
userAPI.Get()
orderAPI.Get()
paymentAPI.Get()

// 🚨 No query timeout
db.Query("SELECT * FROM huge_table")

// 🚨 Regex compilation in loop
for _, text := range texts {
    re, _ := regexp.Compile(pattern)
}

// 🚨 SELECT * queries
db.Query("SELECT * FROM users")

// 🚨 No pagination
db.Query("SELECT * FROM orders")  // Could be millions

// 🚨 Immediate retry without backoff
if err != nil {
    return retry()  // Immediately
}

// 🚨 No rate limiting
func publicAPI() {
    // Anyone can call unlimited times
}
```

## 🎓 Learning Resources

- **Books**: 
  - "Designing Data-Intensive Applications" - Martin Kleppmann
  - "Database Performance at Scale" - Felipe Cardeneti Mendes
  
- **Online**:
  - [Use The Index, Luke](https://use-the-index-luke.com/)
  - [Go Concurrency Patterns](https://go.dev/blog/pipelines)
  - [Microsoft Azure Antipatterns](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/)
  
- **Tools**:
  - `pprof` - Go profiling
  - `hey` or `wrk` - Load testing
  - `pgBadger` - PostgreSQL log analyzer
  - `redis-cli` - Redis monitoring

## 🔄 Migration Strategy

When fixing antipatterns in production:

1. **Measure first**: Profile and benchmark current state
2. **Start small**: Fix one antipattern at a time
3. **Feature flag**: Use flags to toggle new behavior
4. **Monitor closely**: Watch metrics during rollout
5. **Rollback plan**: Be ready to revert quickly
6. **Gradual rollout**: Use canary deployments
7. **Document changes**: Update team on new patterns

---

**Remember**: Premature optimization is evil, but these antipatterns cause real problems at scale. Fix them when you see them!
