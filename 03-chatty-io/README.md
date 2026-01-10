# Chatty I/O Antipattern

## 🔴 The Problem

Making many small, individual I/O requests instead of batching them into fewer, larger requests. The classic example is the **N+1 query problem**. This leads to:
- High network latency (round-trip overhead multiplied)
- Connection pool exhaustion
- Database/API overwhelmed with requests
- Poor overall throughput

## Common Examples

1. **N+1 Query Problem** - Fetching a list, then querying for each item's details
2. **Individual API calls** - Calling an API in a loop instead of using batch endpoints
3. **Micro-transactions** - Many small database updates instead of batch updates
4. **File I/O** - Reading/writing many small chunks instead of buffering

## 📊 Impact

- **Latency**: Nx round-trip time vs 1x round-trip time
- **Throughput**: 10-100x reduction
- **Network overhead**: N times the protocol overhead
- **Resource usage**: Connection pool exhaustion

## 🏃 Running the Examples

### Bad Example (Chatty N+1)
```bash
cd bad
go run main.go
```

### Good Example (Batched Queries)
```bash
cd good
go run main.go
```

### Load Test
```bash
# Start PostgreSQL first
docker-compose up -d postgres

# Test endpoints
curl http://localhost:8084/orders/1  # Bad: N+1 queries
curl http://localhost:8085/orders/1  # Good: Batched query
```

## 🎯 Key Takeaways

1. **Batch queries**: Use `IN` clauses or batch endpoints
2. **Eager loading**: Load related data in fewer queries
3. **DataLoader pattern**: Batch and cache within a request
4. **Monitor query count**: Use APM to detect N+1 problems
5. **Use JOIN**: When appropriate, join tables instead of multiple queries

## 📚 Related Patterns

- DataLoader Pattern
- Query Batching
- Eager Loading
- Repository Pattern with includes
