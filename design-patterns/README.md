# Cloud Design Patterns

Comprehensive guide to cloud design patterns with real-world Python examples, inspired by [Microsoft Azure Architecture Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/).

## 🤔 New to Patterns? Start Here

**[📖 Pattern Selection Guide](./PATTERN_GUIDE.md)** - One comprehensive guide covering:
- Quick decision trees ("What's your problem?" → Pattern)
- Ambassador vs ACL explained (the most common confusion!)
- When to use which pattern with real examples
- Common scenarios (e-commerce, legacy migration, etc.)
- Practice exercises to build intuition

## Pattern Categories

### 🔌 Connectivity & Messaging
- **[01 - Ambassador](./01-ambassador/README.md)** - Offload common client connectivity tasks (retry, monitoring, logging)
- **[02 - Anti-Corruption Layer](./02-anti-corruption-layer/README.md)** - Isolate your domain from external systems with different models
- **03 - Gateway Aggregation** - Aggregate multiple requests into a single request
- **04 - Gateway Offloading** - Offload shared functionality to a gateway proxy
- **05 - Gateway Routing** - Route requests to multiple services using a single endpoint

### 🔄 Availability & Resiliency
- **06 - Circuit Breaker** - Handle faults that might take a variable amount of time to recover
- **07 - Retry** - Handle transient failures with automatic retry logic
- **08 - Throttling** - Control resource consumption by throttling requests
- **09 - Bulkhead** - Isolate critical resources to prevent cascading failures

### 📊 Data Management
- **10 - Cache-Aside** - Load data on demand into a cache from a data store
- **11 - CQRS** - Segregate read and write operations for data stores
- **12 - Event Sourcing** - Use append-only store to record full series of events
- **13 - Sharding** - Divide data store into horizontal partitions

### 🎯 Performance & Scalability
- **14 - Competing Consumers** - Enable multiple consumers to process messages concurrently
- **15 - Queue-Based Load Leveling** - Use a queue as buffer between task and service
- **16 - Throttling** - Control consumption of resources by an instance

### 🔐 Security
- **17 - Valet Key** - Use token that provides limited direct access to resources
- **18 - Federated Identity** - Delegate authentication to external identity provider

## Running Examples

Each pattern includes:
- **📖 README.md** - Pattern explanation, use cases, and diagrams
- **❌ without_pattern/** - Code without the pattern (demonstrates the problem)
- **✅ with_pattern/** - Code with the pattern (demonstrates the solution)
- **🧪 demo/** - Practical demonstration scripts
- **📈 benchmarks/** - Performance comparisons (where applicable)

```bash
# Run a specific pattern demo
cd design-patterns/01-ambassador
python demo/run_demo.py

# Run benchmarks
python benchmarks/benchmark.py
```

## Prerequisites

```bash
# Install common dependencies
pip install -r requirements.txt

# For patterns requiring infrastructure
docker-compose up -d
```

## Learning Path

**Beginners**: Start with Ambassador → Anti-Corruption Layer → Cache-Aside → Retry

**Intermediate**: Gateway patterns → Circuit Breaker → Queue-Based Load Leveling → Competing Consumers

**Advanced**: CQRS → Event Sourcing → Sharding → Bulkhead

## Pattern Selection Guide

| You Need To... | Use This Pattern |
|----------------|------------------|
| Add retry logic, logging, monitoring to API calls | **Ambassador** |
| Integrate with legacy systems or bad APIs | **Anti-Corruption Layer** |
| Cache frequently accessed data | **Cache-Aside** |
| Prevent cascading failures | **Circuit Breaker** |
| Handle transient failures | **Retry** |
| Combine multiple API calls | **Gateway Aggregation** |
| Separate read/write workloads | **CQRS** |
| Scale data storage horizontally | **Sharding** |
| Process messages in parallel | **Competing Consumers** |
| Smooth out burst traffic | **Queue-Based Load Leveling** |
| Protect domain model from external changes | **Anti-Corruption Layer** |
| Migrate from legacy to modern systems | **Anti-Corruption Layer** |

## Contributing

Each pattern follows this structure:
```
pattern-name/
├── README.md                 # Pattern documentation
├── without_pattern/         # Code showing the problem
│   └── main.py
├── with_pattern/            # Code showing the solution
│   └── main.py
├── demo/                    # Practical demo
│   └── run_demo.py
└── benchmarks/              # Performance tests
    └── benchmark.py
```
