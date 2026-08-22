# System Design - Patterns & Antipatterns

A comprehensive guide to cloud design patterns and common performance antipatterns with practical Python and Go examples.

## 📋 Contents

1. **[Design Patterns](./design-patterns/)** - Learn cloud design patterns (Ambassador, Gateway, CQRS, etc.)
2. **[Performance Antipatterns](./anti-patterns/)** - Avoid common performance pitfalls
3. **[Low-Level Design](./low-level-design/)** - System design interviews and implementations

---

## 🎨 Design Patterns

**Location**: [`design-patterns/`](./design-patterns/)

Learn cloud design patterns with real-world Python examples inspired by [Microsoft Azure Architecture Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/).

### ✅ Currently Available

#### 1. **[Ambassador Pattern](./design-patterns/01-ambassador/)**
Centralize common client connectivity tasks like retry logic, circuit breaking, logging, and monitoring.

**Use when**: Multiple services call external APIs and need consistent behavior

**Real-world example**: E-commerce app with 20 microservices calling payment, shipping, and notification APIs

**Quick start**:
```bash
cd design-patterns/01-ambassador
python demo/mock_api.py        # Terminal 1
python demo/run_demo.py         # Terminal 2
```

#### 2. **[Anti-Corruption Layer](./design-patterns/02-anti-corruption-layer/)**
Isolate your clean domain model from external systems with different semantics. Translate between legacy/external formats and your modern domain.

**Use when**: Integrating with legacy systems or badly designed external APIs

**Real-world example**: Modern app integrating with 20-year-old mainframe using cryptic codes and weird date formats

**Quick start**:
```bash
cd design-patterns/02-anti-corruption-layer
python demo/mock_legacy_system.py  # Terminal 1
python demo/run_demo.py            # Terminal 2
```

### 🚧 Coming Soon
- Gateway Aggregation
- Gateway Offloading
- Circuit Breaker
- Cache-Aside
- CQRS
- Event Sourcing
- And more...

**[📖 View All Patterns →](./design-patterns/README.md)**

---

## ⚠️ Performance Antipatterns

**Location**: [`anti-patterns/`](./anti-patterns/)

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

### Design Patterns
- **Primary**: Python 3.11+ (with Flask, requests)
- **Infrastructure**: Docker (for mock services)

### Performance Antipatterns
- **Primary**: Go 1.21+ (for performance-critical examples)
- **Secondary**: Java Spring Boot, Python FastAPI
- **Infrastructure**: Docker, Docker Compose, PostgreSQL, Redis

## 📖 How to Use This Repository

### Design Patterns
Each pattern directory contains:
```
pattern-name/
├── README.md              # Pattern explanation
├── QUICKSTART.md          # Quick start guide
├── without_pattern/       # Problem (code without pattern)
│   └── main.py
├── with_pattern/          # Solution (code with pattern)
│   └── main.py
├── demo/                  # Interactive demonstration
│   ├── mock_api.py
│   └── run_demo.py
└── benchmarks/            # Performance comparison
    └── benchmark.py
```

### Performance Antipatterns
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

#### Design Patterns (Python)
```bash
# Navigate to pattern directory
cd design-patterns/01-ambassador

# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start mock API
python demo/mock_api.py

# Terminal 2: Run demo
python demo/run_demo.py

# Run benchmarks
python benchmarks/benchmark.py
```

#### Performance Antipatterns (Go)
```bash
# Navigate to antipattern directory
cd anti-patterns/01-improper-instantiation

# Read the README
cat README.md

# Run bad example
cd bad && go run main.go

# Run good example
cd ../good && go run main.go

# Run benchmarks
cd ../benchmarks && go test -bench=. -benchmem
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+** (for design patterns)
- **Go 1.21+** (for performance antipatterns)
- **Docker & Docker Compose** (for infrastructure)
- (Optional) Java 17+ for Spring Boot examples
- (Optional) FastAPI for Python API examples

### Quick Start

#### Design Patterns
```bash
cd design-patterns/01-ambassador
pip install -r requirements.txt
python demo/mock_api.py        # Terminal 1
python demo/run_demo.py         # Terminal 2
```

#### Performance Antipatterns
```bash
# Start infrastructure (databases, cache, etc.)
docker-compose up -d

# Run any antipattern example
cd anti-patterns/01-improper-instantiation/bad
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
