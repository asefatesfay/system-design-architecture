# System Design - Performance Antipatterns

A comprehensive guide to common performance antipatterns with practical examples and solutions.

## 🎯 Purpose

This repository demonstrates common performance antipatterns found in distributed systems and web applications, along with proper solutions. Each antipattern includes:
- **Problem Description**: What the antipattern is and why it's problematic
- **Code Examples**: Bad implementation demonstrating the antipattern
- **Solution**: Proper implementation with best practices
- **Benchmarks**: Performance comparisons where applicable

## 📚 Antipatterns Covered

### 1. [Improper Instantiation](./01-improper-instantiation/)
Creating expensive objects repeatedly instead of reusing them. Examples: database connections, HTTP clients, regex patterns.

**Impact**: Increased memory allocation, GC pressure, slower response times

### 2. [Synchronous I/O](./02-synchronous-io/)
Blocking threads while waiting for I/O operations to complete instead of using asynchronous patterns.

**Impact**: Thread exhaustion, poor throughput, scalability issues

### 3. [Chatty I/O](./03-chatty-io/)
Making many small I/O requests instead of fewer, larger batched requests (N+1 problem).

**Impact**: High latency, network overhead, connection pool exhaustion

### 4. [No Caching](./04-no-caching/)
Repeatedly fetching or computing the same data without caching strategies.

**Impact**: Unnecessary load on databases/APIs, slow response times, wasted resources

### 5. [Busy Database](./05-busy-database/)
Pushing too much work to the database layer (complex queries, business logic in stored procedures).

**Impact**: Database becomes bottleneck, reduced scalability, difficult maintenance

### 6. [Retry Storm](./06-retry-storm/)
Aggressive retry logic without backoff or circuit breakers causing cascading failures.

**Impact**: Amplified failures, resource exhaustion, extended downtime

### 7. [Monolithic Persistence](./07-monolithic-persistence/)
Using a single database/storage mechanism for all data types regardless of access patterns.

**Impact**: Suboptimal performance, scaling issues, technology lock-in

### 8. [Noisy Neighbor](./08-noisy-neighbor/)
One tenant/process consuming excessive shared resources, affecting others.

**Impact**: Unpredictable performance, unfair resource distribution, SLA violations

### 9. [Extraneous Fetching](./09-extraneous-fetching/)
Retrieving more data than needed (SELECT *, loading entire objects when only IDs needed).

**Impact**: Increased network traffic, memory waste, slower queries

### 10. [Busy Frontend](./10-busy-frontend/)
Performing heavy computation or logic in the client/frontend layer.

**Impact**: Poor mobile performance, battery drain, inconsistent behavior

## 🛠️ Technology Stack

- **Primary**: Go (golang) - for most examples
- **Secondary**: Java Spring Boot, Python FastAPI - for specific patterns where they're particularly illustrative
- **Tools**: Docker, Docker Compose (for databases/infrastructure)

## 📖 How to Use This Repository

Each antipattern directory contains:
```
antipattern-name/
├── README.md          # Detailed explanation
├── bad/              # Antipattern implementation
├── good/             # Proper solution
├── benchmarks/       # Performance tests
└── docker-compose.yml # Infrastructure (if needed)
```

### Running Examples

1. Navigate to the antipattern directory:
```bash
cd 01-improper-instantiation
```

2. Read the README for context

3. Run the bad example:
```bash
cd bad && go run main.go
```

4. Run the good example:
```bash
cd good && go run main.go
```

5. Run benchmarks:
```bash
cd benchmarks && go test -bench=. -benchmem
```

## 🚀 Getting Started

### Prerequisites
- Go 1.21+
- Docker & Docker Compose
- (Optional) Java 17+ for Spring Boot examples
- (Optional) Python 3.11+ for FastAPI examples

### Quick Start
```bash
# Clone and enter directory
cd system-design

# Start infrastructure (databases, cache, etc.)
docker-compose up -d

# Run any example
cd 01-improper-instantiation/bad
go run main.go
```

## 📊 Performance Impact Summary

| Antipattern | Severity | Common In | Primary Impact |
|-------------|----------|-----------|----------------|
| Improper Instantiation | High | All layers | Memory & CPU |
| Synchronous I/O | Critical | Backend services | Throughput |
| Chatty I/O | High | Data access layer | Latency |
| No Caching | Medium-High | All layers | Response time |
| Busy Database | High | Data layer | Scalability |
| Retry Storm | Critical | Distributed systems | Availability |
| Monolithic Persistence | Medium | Architecture | Scalability |
| Noisy Neighbor | High | Multi-tenant | Consistency |
| Extraneous Fetching | Medium | Data access | Network & memory |
| Busy Frontend | Medium | Client apps | User experience |

## 📚 Additional Resources

- [Microsoft Azure Performance Antipatterns](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/)
- [Google SRE Book](https://sre.google/books/)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

## 🤝 Contributing

Feel free to add more examples, benchmarks, or additional antipatterns!

## 📝 License

MIT License - Feel free to use for learning and reference.
