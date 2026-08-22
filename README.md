# System Design Mastery - From Zero to Staff Engineer

> **Complete learning path**: Low-Level Design → High-Level System Design → API Design → Production Patterns → Real Implementations

A comprehensive, hands-on guide covering everything from OOP design patterns to distributed systems at billion-user scale. Learn through real-world examples, production incidents, and working implementations.

---

## 🎯 Choose Your Path

### Quick Navigation by Goal

| I Want To... | Start Here | Time Needed |
|-------------|------------|-------------|
| **Pass FAANG interview** | [Interview Prep Path](#-interview-prep-path-4-8-weeks) | 4-8 weeks |
| **Fix production issues** | [Performance Anti-patterns](./anti-patterns/) → [CHEATSHEET](./CHEATSHEET.md) | 1-2 weeks |
| **Master system design** | [Complete Learning Journey](#-complete-learning-journey) | 12-16 weeks |
| **Build portfolio projects** | [Real Implementations](#-real-implementations) | 8-16 weeks |
| **Quick reference** | [CHEATSHEET.md](./CHEATSHEET.md) • [QUICKSTART.md](./QUICKSTART.md) | - |

### Navigation by Experience Level

| Level | Focus Areas | Entry Point |
|-------|-------------|-------------|
| 👶 **New Grad** (0-2 YOE) | OOP, Design Patterns, Basic System Design | [Low-Level Design](#1-low-level-design-lld) |
| 🎯 **Mid-Level** (3-5 YOE) | Distributed Systems, Scaling, APIs | [System Design Topics](#2-system-design-topics-62-concepts) |
| 🚀 **Senior** (5-8 YOE) | Architecture, Trade-offs, Multi-region | [API Design](#3-api-design-18-walkthroughs) + [Advanced Topics](#advanced-topics-53-62) |
| ⭐ **Staff+** (8+ YOE) | Large-scale systems, Cost, Incidents | [Production Patterns](#4-cloud-design-patterns) + [Implementations](#-real-implementations) |

---

## 📚 What You'll Learn

This guide contains **6 interconnected learning modules**:

1. **[Low-Level Design](#1-low-level-design-lld)** - OOP, SOLID, Design Patterns (Python/Go/Java/JS)
2. **[System Design Topics](#2-system-design-topics-62-concepts)** - 62 concepts from CAP theorem to multi-region DR
3. **[API Design](#3-api-design-18-walkthroughs)** - 18 production API designs (Instagram, Uber, Figma...)
4. **[Cloud Design Patterns](#4-cloud-design-patterns)** - Azure-inspired patterns (Ambassador, Anti-Corruption...)
5. **[Performance Anti-patterns](#5-performance-anti-patterns)** - 10 common pitfalls with Go examples
6. **[Real Implementations](#-real-implementations)** - Build: Proximity Service, Collaborative Editor, Figma Clone

---

## 🚀 Interview Prep Path (4-8 Weeks)

**Goal**: Pass FAANG system design interviews

### Week 1-2: Low-Level Design Foundation
- **Start**: [LLD Learning Guide](./low-level-design/LEARNING-GUIDE.md) ⭐
- **Focus**:
  - OOP fundamentals (4 pillars)
  - SOLID principles with real violations
  - Essential patterns: Factory, Singleton, Strategy, Observer
- **Practice**: Parking Lot, LRU Cache
- **Checkpoint**: Can you explain each SOLID principle with examples?

### Week 3-4: System Design Fundamentals
- **Start**: [System Design Framework](./system-design-topics/00-system-design-framework.md) ⭐ **Read This First!**
- **Core Topics**:
  - 01-06: Latency, ACID, CAP, Consistency, Caching
  - 09-12: Load Balancing, Rate Limiting, Circuit Breaker, Idempotency
- **Practice**: [Back-of-Envelope Estimation](./system-design-topics/42-back-of-the-envelope-estimation-framework.md)
- **Checkpoint**: Can you design a basic URL shortener?

### Week 5-6: Scaling & Communication
- **Topics**:
  - 17-21: Database Scaling, Replication, Sharding, Consistent Hashing
  - 22-27: Message Queues, WebSockets, Microservices, API Gateway
- **Study**: [API Design Playbook](./system-design-topics/42-comprehensive-api-design-playbook.md)
- **Practice**: Design Instagram, WhatsApp
- **Checkpoint**: Can you explain sharding vs replication trade-offs?

### Week 7-8: System Design Practice
- **Walkthroughs**:
  - [Instagram](./system-design-topics/35-instagram-system-design-walkthrough.md)
  - [Uber](./system-design-topics/38-uber-system-design-walkthrough.md)
  - [WhatsApp](./system-design-topics/33-whatsapp-system-design-walkthrough.md)
  - [YouTube](./system-design-topics/34-youtube-system-design-walkthrough.md)
- **Practice**: Design 2 systems from scratch per day
- **Mock**: [Interview Room Behavior](./system-design-topics/63-interview-room-behavior.md)
- **Final Checkpoint**: Can you complete a system design in 45 minutes?

---

## 📖 Complete Learning Journey

### 🔵 Stage 1: Foundation (Weeks 1-4)

#### Build Intuition First
- **Why design matters**: [Real-World Intuition](./low-level-design/REAL-WORLD-INTUITION.md) - Start here to understand WHY
- **Scale understanding**: How systems evolve from 1 → 1K → 1M → 1B users
- **Trade-offs**: CAP theorem, latency vs throughput, consistency models

#### Learn Low-Level Design
- **Location**: [`./low-level-design/`](./low-level-design/)
- **Path**: Follow [LEARNING-GUIDE.md](./low-level-design/LEARNING-GUIDE.md)
- **Covers**:
  - OOP: Encapsulation, Abstraction, Inheritance, Polymorphism
  - SOLID: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
  - Patterns: Factory, Singleton, Builder, Strategy, Observer, State, Adapter, Decorator
  - Practice: 10+ interview problems with solutions

**Time**: 4 weeks • **Checkpoint**: [Can you design a Parking Lot system in 60 minutes?]

---

### 🟢 Stage 2: System Design Fundamentals (Weeks 5-8)

#### Master Core Concepts
- **Location**: [`./system-design-topics/`](./system-design-topics/)
- **Framework**: [00-System Design Framework](./system-design-topics/00-system-design-framework.md) ⭐ **Start Here**

#### Topics 01-30: Essential Concepts

**Performance & Data (01-08)**
- [01 - Latency vs Throughput](./system-design-topics/01-latency-vs-throughput.md) - Understand metrics
- [02 - ACID Transactions](./system-design-topics/02-acid-transactions.md) - Database guarantees
- [03 - SQL vs NoSQL](./system-design-topics/03-sql-vs-nosql.md) - When to use which
- [04 - Database Index](./system-design-topics/04-database-index.md) - Query optimization
- [05 - CAP Theorem](./system-design-topics/05-cap-theorem.md) - The fundamental trade-off
- [06 - Strong vs Eventual Consistency](./system-design-topics/06-strong-vs-eventual-consistency.md)
- [07 - Caching](./system-design-topics/07-caching.md) - Cache strategies
- [08 - Distributed Caching](./system-design-topics/08-distributed-caching.md) - Scale caching

**Reliability & Protection (09-13)**
- [09 - Load Balancing](./system-design-topics/09-load-balancing.md) - Distribute traffic
- [10 - Rate Limiting](./system-design-topics/10-rate-limiting.md) - Protect from overload
- [11 - Idempotency](./system-design-topics/11-idempotency.md) - Safe retries
- [12 - Circuit Breaker](./system-design-topics/12-circuit-breaker.md) - Prevent cascades
- [13 - Heartbeat Mechanism](./system-design-topics/13-heartbeat-mechanism.md) - Health monitoring

**Infrastructure (14-16)**
- [14 - Proxy Server](./system-design-topics/14-proxy-server.md)
- [15 - DNS](./system-design-topics/15-dns.md)
- [16 - CDN](./system-design-topics/16-cdn.md)

**Scaling Data (17-21)**
- [17 - Database Scaling](./system-design-topics/17-database-scaling.md) - Vertical & horizontal
- [18 - Data Replication](./system-design-topics/18-data-replication.md) - Read scaling
- [19 - Data Redundancy](./system-design-topics/19-data-redundancy.md) - Durability
- [20 - Database Sharding](./system-design-topics/20-database-sharding.md) - Write scaling
- [21 - Consistent Hashing](./system-design-topics/21-consistent-hashing.md) - Partition data

**Communication & Architecture (22-30)**
- [22 - Message Queues](./system-design-topics/22-message-queues.md) - Async communication
- [23 - WebSockets](./system-design-topics/23-websockets.md) - Real-time bidirectional
- [24 - Batch vs Stream Processing](./system-design-topics/24-batch-vs-stream-processing.md)
- [25 - REST vs RPC](./system-design-topics/25-rest-vs-rpc.md) - API styles
- [26 - Microservices Architecture](./system-design-topics/26-microservices-architecture.md)
- [27 - API Gateway](./system-design-topics/27-api-gateway.md) - Single entry point
- [28 - Consensus Algorithms](./system-design-topics/28-consensus-algorithms.md) - Raft, Paxos
- [29 - Distributed Locking](./system-design-topics/29-distributed-locking.md)
- [30 - Checksum](./system-design-topics/30-checksum.md) - Data integrity

**Time**: 4 weeks • **Checkpoint**: [Can you design a system for 1M users?]

---

### 🟡 Stage 3: Advanced System Design (Weeks 9-12)

#### Advanced Topics (53-62)
**Location**: [`./system-design-topics/`](./system-design-topics/) - Topics 53-62

**Security & Identity**
- [53 - Authentication and Authorization](./system-design-topics/53-authentication-and-authorization.md) - OAuth, JWT, RBAC
- [62 - Security for System Design](./system-design-topics/62-security-for-system-design.md) - Threat modeling

**Operations & Reliability**
- [54 - Observability and SRE Fundamentals](./system-design-topics/54-observability-and-sre-fundamentals.md) - SLOs, alerts
- [55 - Multi-Region and Disaster Recovery](./system-design-topics/55-multi-region-and-disaster-recovery.md)
- [58 - Backpressure, Load Shedding, and Graceful Degradation](./system-design-topics/58-backpressure-load-shedding-and-graceful-degradation.md)

**Event-Driven & Transactions**
- [56 - Event-Driven Architecture and Pub/Sub](./system-design-topics/56-event-driven-architecture-and-pubsub.md)
- [57 - Saga, Outbox, and Distributed Transactions](./system-design-topics/57-saga-outbox-and-distributed-transactions.md)

**Data & Configuration**
- [59 - Data Modeling and Schema Evolution](./system-design-topics/59-data-modeling-and-schema-evolution.md)
- [60 - Service Discovery, Config, and Feature Flags](./system-design-topics/60-service-discovery-config-and-feature-flags.md)

**Specialized Systems**
- [61 - Search System Design](./system-design-topics/61-search-system-design.md) - Indexing, ranking

#### API Design Mastery
- **Location**: [`./api-design/`](./api-design/)
- **Master Guide**: [API Design Playbook](./system-design-topics/42-comprehensive-api-design-playbook.md)

**Study Real Production APIs:**
- Social: [Instagram](./api-design/01-instagram-api-design.md), [Twitter](./api-design/09-twitter-api-design.md), [Discord](./api-design/10-discord-api-design.md)
- Collaboration: [Figma](./api-design/03-figma-api-design.md), [Google Docs](./api-design/04-google-docs-api-design.md), [Slack](./api-design/13-slack-api-design.md)
- Media: [YouTube](./api-design/06-youtube-api-design.md), [Spotify](./api-design/07-spotify-api-design.md), [Netflix](./api-design/08-netflix-api-design.md)
- Infrastructure: [Stripe](./api-design/11-stripe-api-design.md), [Dropbox](./api-design/12-dropbox-api-design.md)
- Mobility: [Uber](./api-design/02-uber-api-design.md), [Zoom](./api-design/17-zoom-api-design.md)
- AI: [ChatGPT](./api-design/14-chatgpt-api-design.md), [GitHub Copilot](./api-design/15-github-copilot-api-design.md), [Perplexity](./api-design/16-perplexity-api-design.md)

**Each includes:** Resource modeling, Authentication, Critical paths, Error handling, Rate limiting, Idempotency, Versioning

**Time**: 4 weeks • **Checkpoint**: [Can you design an API with idempotency and versioning?]

---

### 🔴 Stage 4: Production Mastery (Weeks 13-16)

#### Performance Anti-patterns
- **Location**: [`./anti-patterns/`](./anti-patterns/)
- **Quick Reference**: [CHEATSHEET.md](./CHEATSHEET.md)

**10 Anti-patterns with Go examples:**

| # | Anti-pattern | Impact | Solution | Code |
|---|-------------|--------|----------|------|
| 1 | [Improper Instantiation](./anti-patterns/01-improper-instantiation/) | Memory leak, GC pressure | Object pooling | [Go examples](./anti-patterns/01-improper-instantiation/) |
| 2 | [Synchronous I/O](./anti-patterns/02-synchronous-io/) | Low throughput | Goroutines, async | [Go examples](./anti-patterns/02-synchronous-io/) |
| 3 | [Chatty I/O](./anti-patterns/03-chatty-io/) | High latency (N+1) | Batch queries, JOIN | [Go examples](./anti-patterns/03-chatty-io/) |
| 4 | [No Caching](./anti-patterns/04-no-caching/) | Slow response | Cache-aside pattern | [Go examples](./anti-patterns/04-no-caching/) |
| 5 | [Busy Database](./anti-patterns/05-busy-database/) | DB bottleneck | App-layer compute | [Go examples](./anti-patterns/05-busy-database/) |
| 6 | [Retry Storm](./anti-patterns/06-retry-storm/) | Cascading failure | Exponential backoff | [Go examples](./anti-patterns/06-retry-storm/) |
| 7 | [Monolithic Persistence](./anti-patterns/07-monolithic-persistence/) | Poor scaling | Polyglot persistence | [Go examples](./anti-patterns/07-monolithic-persistence/) |
| 8 | [Noisy Neighbor](./anti-patterns/08-noisy-neighbor/) | Unpredictable perf | Resource isolation | [Go examples](./anti-patterns/08-noisy-neighbor/) |
| 9 | [Extraneous Fetching](./anti-patterns/09-extraneous-fetching/) | Network waste | Projection queries | [Go examples](./anti-patterns/09-extraneous-fetching/) |
| 10 | [Busy Frontend](./anti-patterns/10-busy-frontend/) | Battery drain | Backend processing | [Go examples](./anti-patterns/10-busy-frontend/) |

**Quick Start**: [QUICKSTART.md](./QUICKSTART.md) - Run examples in 15 minutes

#### Cloud Design Patterns
- **Location**: [`./design-patterns/`](./design-patterns/)
- **Inspired by**: [Microsoft Azure Architecture Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)

**Available Patterns (Python):**

**1. [Ambassador Pattern](./design-patterns/01-ambassador/)**
- **Use case**: Centralized client connectivity (retry, circuit breaking, logging)
- **Example**: E-commerce with 20 microservices calling external APIs
- **Quick start**: `cd design-patterns/01-ambassador && python demo/run_demo.py`

**2. [Anti-Corruption Layer](./design-patterns/02-anti-corruption-layer/)**
- **Use case**: Isolate clean domain from legacy/external systems
- **Example**: Modern app integrating with 20-year-old mainframe
- **Quick start**: `cd design-patterns/02-anti-corruption-layer && python demo/run_demo.py`

**Coming Soon**: Gateway Aggregation, Gateway Offloading, Circuit Breaker, Cache-Aside, CQRS, Event Sourcing

#### Caching Patterns
- **Location**: [`./caching-patterns/`](./caching-patterns/)
- Detailed caching strategies and implementations

**Time**: 4 weeks • **Checkpoint**: [Can you identify and fix anti-patterns in production code?]

---

## 🏗️ Real Implementations

Build production-ready systems to master concepts:

### 1. [Proximity Service](./proximity-service/) - Geo-spatial System
**What**: Yelp-like service to find nearby places
**Tech**: Geohashing, Quadtrees, Redis Geo, PostgreSQL
**Concepts**: Spatial indexing, radius search, pagination
**Time**: 2-3 weeks
**Interview**: Common in location-based service interviews

### 2. [Collaborative Editor](./collaborative-editor/) - Real-time Collaboration
**What**: Google Docs-like editor with live collaboration
**Tech**: Operational Transformation (OT) / CRDTs, WebSockets, Redis
**Concepts**: Conflict resolution, presence, real-time sync
**Time**: 3-4 weeks
**Interview**: Common at Google, Figma, Notion

### 3. [Messaging System](./messaging-demo/) - Message Queue Demo
**What**: WhatsApp-like messaging backend
**Tech**: Python, Redis, Message queues
**Patterns**: Exactly-once delivery, fan-out, ack/nack
**Guide**: [PATTERNS.md](./messaging-demo/PATTERNS.md)
**Time**: 2-3 weeks

### 4. [Figma Clone](./figma-clone-v1/) - Real-time Design Tool
**What**: Collaborative design canvas
**Tech**: React, Canvas API, WebSockets, State management
**Concepts**: Real-time sync, presence, vector storage
**Time**: 4-6 weeks
**Interview**: Common at Figma, Canva, Miro

---

## 📊 System Design Walkthroughs (31-51)

Complete end-to-end designs:

| # | System | Topics Covered | Difficulty |
|---|--------|---------------|------------|
| [31](./system-design-topics/31-figma-system-design-walkthrough.md) | **Figma** | Real-time collab, WebSockets, CRDT | Advanced |
| [32](./system-design-topics/32-google-docs-system-design-walkthrough.md) | **Google Docs** | OT, conflict resolution, versioning | Advanced |
| [33](./system-design-topics/33-whatsapp-system-design-walkthrough.md) | **WhatsApp** | Message delivery, fan-out, receipts | Medium |
| [34](./system-design-topics/34-youtube-system-design-walkthrough.md) | **YouTube** | Video transcoding, CDN, recommendations | Advanced |
| [35](./system-design-topics/35-instagram-system-design-walkthrough.md) | **Instagram** | Feed generation, media storage, graph | Medium |
| [36](./system-design-topics/36-spotify-system-design-walkthrough.md) | **Spotify** | Catalog, playback, multi-device sync | Medium |
| [37](./system-design-topics/37-netflix-system-design-walkthrough.md) | **Netflix** | Adaptive streaming, home rows, CDN | Advanced |
| [38](./system-design-topics/38-uber-system-design-walkthrough.md) | **Uber** | Matching, geohashing, ETA, pricing | Advanced |
| [39](./system-design-topics/39-twitter-system-design-walkthrough.md) | **Twitter/X** | Timeline, fan-out, trending, engagement | Medium |
| [40](./system-design-topics/40-discord-system-design-walkthrough.md) | **Discord** | Real-time messaging, voice signaling | Advanced |
| [41](./system-design-topics/41-stripe-system-design-walkthrough.md) | **Stripe** | Payment processing, idempotency, webhooks | Advanced |
| [42](./system-design-topics/42-dropbox-system-design-walkthrough.md) | **Dropbox** | File sync, delta updates, conflict handling | Advanced |
| [43](./system-design-topics/43-slack-system-design-walkthrough.md) | **Slack** | Workspace messaging, threads, search | Medium |
| [44](./system-design-topics/44-zoom-system-design-walkthrough.md) | **Zoom** | Video conferencing, SFU, signaling | Advanced |
| [46](./system-design-topics/46-chatgpt-llm-serving-system-design-walkthrough.md) | **ChatGPT** | LLM serving, token streaming, context | Advanced |
| [47](./system-design-topics/47-ai-recommendation-engine-system-design-walkthrough.md) | **AI Recommendations** | Candidate generation, ranking, features | Advanced |
| [49](./system-design-topics/49-perplexity-ai-search-system-design-walkthrough.md) | **Perplexity** | RAG, retrieval, reranking, citations | Advanced |
| [50](./system-design-topics/50-github-copilot-system-design-walkthrough.md) | **GitHub Copilot** | Code completion, context assembly | Advanced |

---

## 🎯 Interview Guides

### System Design Interview Strategy
- [00 - System Design Framework](./system-design-topics/00-system-design-framework.md) ⭐ **The 6-step method**
- [42 - Back-of-Envelope Estimation](./system-design-topics/42-back-of-the-envelope-estimation-framework.md)
- [52 - Estimation Cheat Sheet](./system-design-topics/52-back-of-the-envelope-estimation-cheat-sheet.md)
- [63 - Interview Room Behavior](./system-design-topics/63-interview-room-behavior.md)
- [65 - Ambiguous to Concrete](./system-design-topics/65-ambiguous-to-concrete.md)

### Low-Level Design Interview
- [LLD Interview Tips](./low-level-design/INTERVIEW-TIPS.md)
- [Complete Walkthroughs](./low-level-design/COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md) - Python, Go, Java, JS
- [Quick Reference](./low-level-design/QUICK-REFERENCE.md) - One-page cheat sheet

### Staff+ Interview
- [46 - Staff Engineer System Design](./system-design-topics/46-staff-engineer-system-design.md)
- [47 - Staff STAR Examples](./system-design-topics/47-staff-star-examples.md)
- [66 - Staff Behavioral Interview](./system-design-topics/66-staff-behavioral-interview.md)
- [67 - Nordstrom Platform Story](./system-design-topics/67-nordstrom-platform-story.md)

---

## 📚 Additional Resources

### Quick Reference
- [CHEATSHEET.md](./CHEATSHEET.md) - Anti-pattern diagnosis guide
- [QUICKSTART.md](./QUICKSTART.md) - Run examples in 15 minutes
- [BENCHMARKS.md](./BENCHMARKS.md) - Performance comparison data
- [Glossary](./system-design-topics/68-system-design-jargon-glossary.md) - System design jargon explained

### Deep Dives
- [Cloud Design Patterns in Popular Apps](./system-design-topics/41-azure-cloud-design-patterns-in-popular-apps.md)
- [Cloud Patterns Grouped by App](./system-design-topics/42-cloud-design-patterns-grouped-by-popular-apps.md)
- [Real-World Intuition](./low-level-design/REAL-WORLD-INTUITION.md) - Why design matters
- [Concurrency Deep Dive](./low-level-design/CONCURRENCY-DEEP-DIVE.md)
- [Python Must-Knows](./low-level-design/python-must-knows.md) - Language essentials

---

## 🛠️ Technology Stack

### Low-Level Design
- **Primary**: Python 3.11+ (with multi-language support)
- **Also**: Go, Java, JavaScript examples
- **Patterns**: All 7 core patterns with complete implementations

### System Design Topics
- **Language-agnostic** conceptual guides
- Focus on architecture, trade-offs, real-world examples

### Performance Anti-patterns
- **Primary**: Go 1.21+ (for performance-critical examples)
- **Infrastructure**: Docker, PostgreSQL, Redis

### Cloud Design Patterns
- **Primary**: Python 3.11+ with Flask
- **Infrastructure**: Docker for mock services

---

## 📈 Learning Progression

```
Foundation (4 weeks)
    ├── Low-Level Design (OOP, SOLID, Patterns)
    └── System Design Basics (Topics 01-10)
         ↓
Intermediate (4 weeks)
    ├── Scaling & Data (Topics 11-30)
    └── API Design fundamentals
         ↓
Advanced (4 weeks)
    ├── Advanced Topics (53-62)
    ├── API Design Mastery (18 walkthroughs)
    └── System Design Walkthroughs (31-51)
         ↓
Expert (4+ weeks)
    ├── Performance Anti-patterns
    ├── Cloud Design Patterns
    └── Build Real Implementations
```

**Total Time**: 12-16 weeks for complete mastery

---

## 🎓 Success Checklist

### Foundation Complete ✅
- [ ] Understand all 4 OOP pillars with examples
- [ ] Can explain all SOLID principles
- [ ] Know 5+ design patterns and when to use each
- [ ] Understand CAP theorem trade-offs
- [ ] Can design a basic REST API

### Intermediate Complete ✅
- [ ] Can design systems for 1M+ users
- [ ] Understand sharding, replication, consistent hashing
- [ ] Know when to use message queues vs RPC
- [ ] Can implement caching strategies
- [ ] Understand rate limiting and circuit breakers

### Advanced Complete ✅
- [ ] Can design systems for 100M+ users
- [ ] Understand eventual consistency and conflict resolution
- [ ] Can design multi-region architectures
- [ ] Know consensus algorithms (Raft, Paxos)
- [ ] Can handle 99.99% SLA requirements

### Expert Complete ✅
- [ ] Built 2+ real systems at scale
- [ ] Can explain trade-offs in production incidents
- [ ] Understand cost optimization at scale
- [ ] Can mentor others on system design
- [ ] Contributed to production systems

---

## 1. Low-Level Design (LLD)

**Location**: [`./low-level-design/`](./low-level-design/)

**What you'll learn:**
- OOP fundamentals (Encapsulation, Abstraction, Inheritance, Polymorphism)
- SOLID principles with real-world violations and fixes
- Design patterns: Factory, Singleton, Builder, Adapter, Decorator, Strategy, Observer, State
- Interview problems: Parking Lot, Elevator, LRU Cache, Vending Machine, Chess

**Multi-language support**: Python, Go, Java, JavaScript

**Start here**: [LEARNING-GUIDE.md](./low-level-design/LEARNING-GUIDE.md) 🎯

**Key Resources**:
- [Real-World Intuition](./low-level-design/REAL-WORLD-INTUITION.md) - WHY design matters
- [Complete Interview Walkthroughs](./low-level-design/COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md)
- [QUICK-REFERENCE.md](./low-level-design/QUICK-REFERENCE.md) - Print this!
- [NAVIGATION.md](./low-level-design/NAVIGATION.md) - Quick topic finder

**Time**: 4-8 weeks for complete mastery

---

## 2. System Design Topics (62 Concepts)

**Location**: [`./system-design-topics/`](./system-design-topics/)

**62 Topics organized by complexity:**

### 🔵 Foundation (Topics 01-10)
- [00 - System Design Framework](./system-design-topics/00-system-design-framework.md) ⭐ **Must Read First**
- Performance: Latency vs Throughput
- Data: ACID, SQL vs NoSQL, Database Index
- Consistency: CAP Theorem, Strong vs Eventual
- Caching: Local and Distributed

### 🟢 Intermediate (Topics 11-30)
- Reliability: Load Balancing, Rate Limiting, Circuit Breaker, Idempotency
- Network: Proxy, DNS, CDN
- Scaling: Database Scaling, Sharding, Consistent Hashing
- Communication: Message Queues, WebSockets, REST vs RPC
- Architecture: Microservices, API Gateway
- Distributed: Consensus, Distributed Locking

### 🟡 Advanced (Topics 53-62)
- Security: Authentication, Authorization, Threat Modeling
- Operations: Observability, SRE, Multi-Region, Disaster Recovery
- Patterns: Event-Driven, Saga, Outbox, Backpressure
- Data: Schema Evolution, Service Discovery
- Specialized: Search Systems, Security Design

**Time**: 8-12 weeks to complete

**All topics**: [Topics Index](./system-design-topics/README.md)

---

## 3. API Design (18 Walkthroughs)

**Location**: [`./api-design/`](./api-design/)

Learn by studying production APIs:
- **Social**: Instagram, Twitter/X, Discord
- **Collaboration**: Figma, Google Docs, Slack
- **Media**: YouTube, Spotify, Netflix
- **Infrastructure**: Stripe, Dropbox, GitHub Copilot
- **Mobility**: Uber, Zoom
- **AI**: ChatGPT, Perplexity, AI Recommendations

**What each includes**:
- Resource modeling and relationships
- Authentication & authorization flows
- Critical path deep-dives (highest traffic operations)
- Error handling with retry guidance
- Rate limiting and quota strategies
- Idempotency for safe retries
- Versioning without breaking clients
- Real-time / Webhook alternatives

**Master Guide**: [Comprehensive API Design Playbook](./system-design-topics/42-comprehensive-api-design-playbook.md)

**Time**: 4-6 weeks

---

## 4. Cloud Design Patterns

**Location**: [`./design-patterns/`](./design-patterns/)

Production-tested patterns inspired by [Microsoft Azure Architecture](https://learn.microsoft.com/en-us/azure/architecture/patterns/):

### ✅ Currently Available

**1. [Ambassador Pattern](./design-patterns/01-ambassador/)**
- **Purpose**: Centralize common client connectivity (retry, circuit breaking, logging)
- **Use case**: E-commerce with 20 microservices calling external APIs
- **Real-world**: Netflix, Uber
- **Quick start**: `cd design-patterns/01-ambassador && python demo/run_demo.py`

**2. [Anti-Corruption Layer](./design-patterns/02-anti-corruption-layer/)**
- **Purpose**: Isolate clean domain from legacy/external systems
- **Use case**: Modern app integrating with 20-year-old mainframe
- **Real-world**: Banks, Government systems
- **Quick start**: `cd design-patterns/02-anti-corruption-layer && python demo/run_demo.py`

### 🚧 Coming Soon
- Gateway Aggregation - Reduce chattiness
- Gateway Offloading - Offload shared functionality
- Circuit Breaker - Prevent cascading failures
- Cache-Aside - Caching pattern
- CQRS - Command Query Responsibility Segregation
- Event Sourcing - Event-driven state

**Language**: Python 3.11+ with Flask

---

## 5. Performance Anti-patterns

**Location**: [`./anti-patterns/`](./anti-patterns/)

10 common pitfalls with Go implementations:

| # | Antipattern | Severity | Impact | Common In |
|---|-------------|----------|--------|-----------|
| 1 | [Improper Instantiation](./anti-patterns/01-improper-instantiation/) | 🔴 High | Memory & CPU | All layers |
| 2 | [Synchronous I/O](./anti-patterns/02-synchronous-io/) | 🔴 Critical | Throughput | Backend services |
| 3 | [Chatty I/O](./anti-patterns/03-chatty-io/) | 🔴 High | Latency (N+1) | Data access |
| 4 | [No Caching](./anti-patterns/04-no-caching/) | 🟡 Medium-High | Response time | All layers |
| 5 | [Busy Database](./anti-patterns/05-busy-database/) | 🔴 High | Scalability | Data layer |
| 6 | [Retry Storm](./anti-patterns/06-retry-storm/) | 🔴 Critical | Availability | Distributed |
| 7 | [Monolithic Persistence](./anti-patterns/07-monolithic-persistence/) | 🟡 Medium | Scalability | Architecture |
| 8 | [Noisy Neighbor](./anti-patterns/08-noisy-neighbor/) | 🔴 High | Consistency | Multi-tenant |
| 9 | [Extraneous Fetching](./anti-patterns/09-extraneous-fetching/) | 🟡 Medium | Network & memory | Data access |
| 10 | [Busy Frontend](./anti-patterns/10-busy-frontend/) | 🟡 Medium | User experience | Client apps |

**Quick Start**: [QUICKSTART.md](./QUICKSTART.md) - Run examples in 15 minutes
**Quick Reference**: [CHEATSHEET.md](./CHEATSHEET.md) - Diagnosis guide

**Tech Stack**: Go 1.21+, Docker, PostgreSQL, Redis

---

## 🤝 Contributing

Found an error or want to add content? Contributions welcome!

**What we're looking for**:
- Real production stories and incident reports
- More decision trees and visual diagrams
- Additional API design walkthroughs
- Performance benchmark data
- Translations to other languages

---

## 📖 External Resources

- [Microsoft Azure Architecture Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
- [Google SRE Book](https://sre.google/books/)
- [Designing Data-Intensive Applications](https://dataintensive.net/) by Martin Kleppmann
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

---

## 🎉 Final Tips

1. **Don't memorize** - Understand WHY and WHEN
2. **Start simple** - Don't over-engineer early
3. **Practice explaining** - Talk through your designs out loud
4. **Learn from failures** - Study production incidents
5. **Build real things** - Theory without practice is incomplete
6. **Focus on trade-offs** - Every decision has pros and cons
7. **Stay current** - System design evolves constantly

---

## 🚀 Ready to Start?

**Choose your path**:
- 🎯 **Interview in 4-8 weeks?** → [Interview Prep Path](#-interview-prep-path-4-8-weeks)
- 🧠 **Complete mastery?** → [Complete Learning Journey](#-complete-learning-journey)
- 🔧 **Fix production issues?** → [Performance Anti-patterns](./anti-patterns/) + [CHEATSHEET](./CHEATSHEET.md)
- 🏗️ **Build portfolio?** → [Real Implementations](#-real-implementations)

---

**Good luck on your system design journey! 🚀**

*Remember: The goal isn't to memorize patterns, but to understand trade-offs and build intuition for when to apply each concept.*

---

## 📝 License

MIT License - Feel free to use for learning and reference.
