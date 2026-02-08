# System Design Topics Master Guide

This directory contains comprehensive guides for essential system design concepts. Each topic includes clear explanations, real-world examples, and practical use cases.

## 📚 Topics Overview

### Core Performance & Data Concepts
1. [Latency vs Throughput](./01-latency-vs-throughput.md) - Understanding system performance metrics
2. [ACID Transactions](./02-acid-transactions.md) - Database transaction guarantees
3. [SQL vs NoSQL](./03-sql-vs-nosql.md) - Choosing the right database paradigm
4. [Database Index](./04-database-index.md) - Optimizing query performance
5. [CAP Theorem](./05-cap-theorem.md) - Distributed system trade-offs
6. [Strong vs Eventual Consistency](./06-strong-vs-eventual-consistency.md) - Data consistency models

### Caching & Performance
7. [Caching](./07-caching.md) - Improving response times
8. [Distributed Caching](./08-distributed-caching.md) - Caching at scale

### Scalability & Reliability
9. [Load Balancing](./09-load-balancing.md) - Distributing traffic across servers
10. [Rate Limiting](./10-rate-limiting.md) - Protecting services from overload
11. [Idempotency](./11-idempotency.md) - Safe retry operations
12. [Circuit Breaker](./12-circuit-breaker.md) - Preventing cascading failures
13. [Heartbeat Mechanism](./13-heartbeat-mechanism.md) - Monitoring system health

### Network & Infrastructure
14. [Proxy Server](./14-proxy-server.md) - Intermediary for requests
15. [Domain Name System (DNS)](./15-dns.md) - Translating domain names to IPs
16. [Content Delivery Network (CDN)](./16-cdn.md) - Global content distribution

### Data Management at Scale
17. [Database Scaling](./17-database-scaling.md) - Vertical and horizontal scaling
18. [Data Replication](./18-data-replication.md) - Copying data for availability
19. [Data Redundancy](./19-data-redundancy.md) - Ensuring data durability
20. [Database Sharding](./20-database-sharding.md) - Partitioning data horizontally
21. [Consistent Hashing](./21-consistent-hashing.md) - Distributing data evenly

### Communication Patterns
22. [Message Queues](./22-message-queues.md) - Asynchronous communication
23. [WebSockets](./23-websockets.md) - Real-time bidirectional communication
24. [Batch vs Stream Processing](./24-batch-vs-stream-processing.md) - Data processing paradigms
25. [REST vs RPC](./25-rest-vs-rpc.md) - API communication styles

### Architecture Patterns
26. [Microservices Architecture](./26-microservices-architecture.md) - Decomposing applications
27. [API Gateway](./27-api-gateway.md) - Single entry point for APIs

### Distributed Systems
28. [Consensus Algorithms](./28-consensus-algorithms.md) - Agreement in distributed systems
29. [Distributed Locking](./29-distributed-locking.md) - Coordinating distributed operations
30. [Checksum](./30-checksum.md) - Data integrity verification

## 🎯 How to Use This Guide

Each topic file contains:
- **Definition**: Clear explanation of the concept
- **Key Concepts**: Core principles and variations
- **Real-World Examples**: How major companies use this pattern
- **When to Use**: Practical scenarios and use cases
- **Trade-offs**: Pros, cons, and considerations
- **Implementation Tips**: Best practices

## 🚀 Learning Path

**Beginner**: Start with topics 1-6 (Core concepts)  
**Intermediate**: Progress through topics 7-16 (Performance & infrastructure)  
**Advanced**: Master topics 17-30 (Distributed systems & scaling)

## 📖 Additional Resources

- Check out the antipattern examples in parent directories (01-improper-instantiation, 02-synchronous-io, etc.)
- Review caching-patterns/ for practical caching implementations
- See CHEATSHEET.md for quick reference

---

*Last updated: February 2026*
