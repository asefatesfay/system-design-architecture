# No Caching Antipattern

## 🔴 The Problem

Repeatedly fetching or computing the same data without any caching mechanism. This leads to:
- Unnecessary load on databases and external APIs
- Slow response times for repeated requests
- Wasted CPU cycles recomputing the same results
- Poor scalability and higher infrastructure costs

## Common Examples

1. **Database queries** - Fetching the same reference data repeatedly
2. **API calls** - Calling external APIs without caching responses
3. **Expensive computations** - Recalculating results that rarely change
4. **File reads** - Reading configuration files on every request

## 📊 Impact

- **Response time**: 10-100x slower for cached data
- **Database load**: 100-1000x more queries
- **Cost**: Higher API bills and infrastructure costs
- **Scalability**: Limited by backend capacity

## 🏃 Running the Examples

### Bad Example (No Caching)
```bash
cd bad
go run main.go
```

### Good Example (With Caching)
```bash
cd good
go run main.go
```

### Test
```bash
# Start Redis
docker-compose up -d redis

# Test bad endpoint (always hits DB)
curl http://localhost:8086/products/1
curl http://localhost:8086/products/1  # Still hits DB

# Test good endpoint (uses cache)
curl http://localhost:8087/products/1  # Hits DB, caches result
curl http://localhost:8087/products/1  # Serves from cache
```

## 🎯 Key Takeaways

1. **Cache reference data**: Data that rarely changes (products, categories, config)
2. **Set appropriate TTL**: Balance freshness vs. cache effectiveness
3. **Cache invalidation**: Update/delete cache when data changes
4. **Multiple cache layers**: In-memory → Redis → Database
5. **Cache-aside pattern**: Application manages cache population

## 📚 Caching Strategies

- **Cache-Aside**: App checks cache, loads from DB if miss
- **Write-Through**: Write to cache and DB simultaneously
- **Write-Behind**: Write to cache, async write to DB
- **Read-Through**: Cache automatically loads from DB on miss

## 🛠️ Tools

- In-memory: `sync.Map`, `github.com/patrickmn/go-cache`
- Distributed: Redis, Memcached
- HTTP: Varnish, CDN caching
