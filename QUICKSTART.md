# Quick Start Guide

## Prerequisites

Make sure you have installed:
- **Go 1.21+**: `go version`
- **Docker & Docker Compose**: `docker --version && docker-compose --version`
- **curl or httpie**: For testing endpoints

## 🚀 Getting Started

### 1. Start Infrastructure

Start PostgreSQL, Redis, and MongoDB:

```bash
# From the root directory
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs if needed
docker-compose logs -f postgres
```

### 2. Run Your First Example

Let's start with **Improper Instantiation**:

```bash
cd 01-improper-instantiation

# Terminal 1: Run the BAD example
cd bad
go run main.go

# Terminal 2: Run the GOOD example
cd good
go run main.go

# Terminal 3: Test them
curl http://localhost:8080/user  # Bad version
curl http://localhost:8081/user  # Good version

# Run benchmarks
cd benchmarks
go mod download
go test -bench=. -benchmem
```

Expected benchmark results:
```
BenchmarkBadRegexCompile     50000    35000 ns/op    12000 B/op    100 allocs/op
BenchmarkGoodRegexCompile   5000000      250 ns/op        0 B/op      0 allocs/op
```

### 3. Try More Antipatterns

#### Synchronous I/O
```bash
cd 02-synchronous-io

# Run both versions
cd bad && go run main.go &
cd good && go run main.go &

# Compare response times
curl -w "\nTime: %{time_total}s\n" http://localhost:8082/aggregate  # ~1.5s
curl -w "\nTime: %{time_total}s\n" http://localhost:8083/aggregate  # ~0.5s (3x faster!)
```

#### Chatty I/O (N+1 Problem)
```bash
cd 03-chatty-io

# Make sure Postgres is running
docker-compose up -d postgres

cd bad && go run main.go &
cd good && go run main.go &

# Compare query count in logs
curl http://localhost:8084/orders/1  # Watch log: "Executed 4 queries"
curl http://localhost:8085/orders/1  # Watch log: "Executed 1 query"
```

#### No Caching
```bash
cd 04-no-caching

# Make sure Postgres and Redis are running
docker-compose up -d postgres redis

cd bad && go run main.go &
cd good && go run main.go &

# Test caching
curl -v http://localhost:8086/products/1  # Always X-Cache: MISS
curl -v http://localhost:8087/products/1  # First: MISS
curl -v http://localhost:8087/products/1  # Second: HIT (much faster!)
```

#### Busy Database
```bash
cd 05-busy-database

cd bad && go run main.go &
cd good && go run main.go &

curl http://localhost:8088/reports/sales  # Heavy DB work
curl http://localhost:8089/reports/sales  # App-layer processing
```

#### Retry Storm
```bash
cd 06-retry-storm

cd bad && go run main.go &
cd good && go run main.go &

# Watch the logs to see retry behavior
curl http://localhost:8090/call  # Aggressive retries
curl http://localhost:8091/call  # Exponential backoff + circuit breaker
```

## 📊 Load Testing

Install `hey` for load testing:

```bash
# macOS
brew install hey

# Linux
go install github.com/rakyll/hey@latest
```

### Compare Performance Under Load

```bash
# Synchronous I/O comparison
hey -n 100 -c 10 http://localhost:8082/aggregate  # Bad
hey -n 100 -c 10 http://localhost:8083/aggregate  # Good

# Chatty I/O comparison
hey -n 100 -c 10 http://localhost:8084/orders/1   # Bad
hey -n 100 -c 10 http://localhost:8085/orders/1   # Good

# Caching comparison
hey -n 1000 -c 50 http://localhost:8086/products/1  # No cache
hey -n 1000 -c 50 http://localhost:8087/products/1  # With cache
```

## 📈 Monitoring

View metrics in Prometheus:

```bash
# Start Prometheus
docker-compose up -d prometheus

# Open in browser
open http://localhost:9090

# Example queries:
# - http_request_duration_seconds
# - go_goroutines
# - go_memstats_alloc_bytes
```

## 🧹 Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Kill any running Go servers
pkill -f "go run"
```

## 📚 Learning Path

Recommended order for learning:

1. **Improper Instantiation** - Easiest to understand, immediate impact
2. **No Caching** - Clear before/after comparison
3. **Synchronous I/O** - Learn goroutines and concurrency
4. **Chatty I/O** - Understand N+1 problem
5. **Busy Database** - Learn when to process in app vs DB
6. **Retry Storm** - Advanced: circuit breakers and backoff

Then read the documentation for:
7. **Monolithic Persistence** - Architectural pattern
8. **Noisy Neighbor** - Multi-tenancy concepts
9. **Extraneous Fetching** - API design principles
10. **Busy Frontend** - Full-stack architecture

## 🎯 Key Takeaways

After going through these examples, you should understand:

- ✅ Why object reuse matters (memory & performance)
- ✅ How to use goroutines for concurrent I/O
- ✅ The N+1 query problem and how to fix it
- ✅ Cache-aside pattern with Redis
- ✅ When to process in app vs database
- ✅ Exponential backoff and circuit breakers
- ✅ Polyglot persistence for different data types
- ✅ Resource isolation for multi-tenant systems
- ✅ Efficient data fetching strategies
- ✅ Thin client vs thick client trade-offs

## 🐛 Troubleshooting

### Database connection failed
```bash
# Check if Postgres is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### Redis connection failed
```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost ping
# Should return: PONG
```

### Port already in use
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>
```

## 🤝 Next Steps

1. **Experiment**: Modify the code and see how it affects performance
2. **Benchmark**: Add your own benchmarks for different scenarios
3. **Add patterns**: Implement additional antipatterns you encounter
4. **Real projects**: Apply these patterns to your actual work

## 📖 Additional Resources

- [Go Concurrency Patterns](https://go.dev/blog/pipelines)
- [Database Performance Tips](https://use-the-index-luke.com/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Microsoft Azure Antipatterns](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/)
