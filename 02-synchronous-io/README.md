# Synchronous I/O Antipattern

## 🔴 The Problem

Blocking threads while waiting for I/O operations (database queries, HTTP calls, file operations) instead of using asynchronous patterns. This leads to:
- Thread starvation under load
- Poor throughput and scalability
- Wasted resources (idle threads consuming memory)
- Cascading failures when downstream services slow down

## Common Examples

1. **Sequential API calls** - Waiting for each call to complete before starting the next
2. **Blocking database queries** - Not using async drivers or concurrent patterns
3. **File I/O** - Reading/writing files synchronously in request handlers
4. **External service calls** - Blocking on slow third-party APIs

## 📊 Impact

- **Throughput**: 10-100x reduction under concurrent load
- **Latency**: Linearly increases with number of I/O operations
- **Resource usage**: Threads blocked waiting for I/O
- **Scalability**: Cannot handle more concurrent requests

## 🏃 Running the Examples

### Bad Example (Synchronous/Blocking)
```bash
cd bad
go run main.go
```

### Good Example (Asynchronous/Concurrent)
```bash
cd good
go run main.go
```

### Load Test
```bash
# Install hey if needed: brew install hey
# Test bad endpoint (will struggle with concurrency)
hey -n 1000 -c 50 http://localhost:8082/aggregate

# Test good endpoint (handles concurrency well)
hey -n 1000 -c 50 http://localhost:8083/aggregate
```

## 🎯 Key Takeaways

1. **Use goroutines**: Launch concurrent operations with goroutines
2. **WaitGroups or channels**: Coordinate concurrent work
3. **Context for cancellation**: Propagate timeouts and cancellations
4. **Error handling**: Collect errors from concurrent operations
5. **Rate limiting**: Don't overwhelm downstream services

## 📚 Related Patterns

- Fan-out/Fan-in Pattern
- Pipeline Pattern
- Worker Pool Pattern
- Context Pattern
