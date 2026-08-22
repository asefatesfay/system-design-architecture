# Hands-On Labs - Learn by Building

> **Theory → Practice → Mastery**. Build real systems at increasing scale to truly understand system design.

---

## 🎯 Learning Philosophy

**You don't truly understand system design until you've:**
1. Built a system that works for 100 users
2. Rebuilt it when it breaks at 10,000 users
3. Rebuilt it again when it breaks at 1,000,000 users

**Each rebuild teaches you:**
- What breaks at scale
- Why the solution works
- Trade-offs of each approach

---

## 📚 Lab Structure

### Level 1: Beginner Labs
**Prerequisites:** Basic programming, understand HTTP, basic SQL

**Labs:**
1. **URL Shortener** - Build at 3 different scales
2. **Rate Limiter** - Implement 3 algorithms
3. **Distributed Cache** - Build and scale a cache
4. **Key-Value Store** - Simple to distributed
5. **Task Queue** - Single to distributed queue

**Time:** 2-4 hours per lab

---

### Level 2: Intermediate Labs
**Prerequisites:** Completed beginner labs, understand caching, sharding

**Labs:**
1. **Social Media Feed** - Fan-out patterns
2. **Real-time Chat** - Polling to WebSocket
3. **Video Streaming** - CDN, adaptive bitrate
4. **Search Engine** - Indexing, ranking
5. **Payment System** - Idempotency, saga pattern

**Time:** 4-8 hours per lab

---

### Level 3: Advanced Labs
**Prerequisites:** Completed intermediate labs, understand distributed systems

**Labs:**
1. **Multi-Region Setup** - Consistency, latency
2. **Chaos Engineering** - Break your system deliberately
3. **Time-Series Database** - Handle billions of metrics
4. **ML Model Serving** - Deploy models at scale
5. **Event Sourcing System** - CQRS, event store

**Time:** 8-16 hours per lab

---

## 🚀 Quick Start

### Choose Your Path

**Path 1: Interview Prep (4 weeks)**
- Week 1: URL Shortener + Rate Limiter
- Week 2: Distributed Cache + Task Queue
- Week 3: Social Feed + Real-time Chat
- Week 4: Payment System + Multi-Region

**Path 2: Learn by Doing (8 weeks)**
- Weeks 1-3: All beginner labs
- Weeks 4-6: All intermediate labs
- Weeks 7-8: 2-3 advanced labs

**Path 3: Build Portfolio (12 weeks)**
- Complete all labs
- Deploy to production (AWS/GCP)
- Add monitoring, testing, CI/CD
- Write case studies

---

## 📊 Progress Tracking

### Beginner Complete ✅
- [ ] URL Shortener v1 (single server)
- [ ] URL Shortener v2 (with caching)
- [ ] URL Shortener v3 (sharded)
- [ ] Rate Limiter (fixed window)
- [ ] Rate Limiter (sliding window)
- [ ] Rate Limiter (token bucket)
- [ ] Distributed Cache (single node)
- [ ] Distributed Cache (consistent hashing)

### Intermediate Complete ✅
- [ ] Social Feed (simple)
- [ ] Social Feed (fan-out on write)
- [ ] Social Feed (hybrid fan-out)
- [ ] Chat (polling)
- [ ] Chat (WebSocket)
- [ ] Chat (distributed)

### Advanced Complete ✅
- [ ] Multi-region deployed
- [ ] Chaos tests passing
- [ ] Handling 100K+ RPS

---

## 🛠️ Lab Environment Setup

### Prerequisites

**Software:**
```bash
# Install Docker
brew install docker  # macOS
# or download from docker.com

# Install programming languages
brew install python go node  # Choose your language

# Install databases
docker pull postgres:15
docker pull redis:7
docker pull mongo:7
```

**Accounts (free tier):**
- AWS Free Tier (optional, for deployment)
- DataDog or New Relic (optional, for monitoring)

### Start Lab Environment

```bash
# Clone the repo
cd hands-on-labs

# Start infrastructure
docker-compose up -d

# Verify services
docker-compose ps

# Should see:
# - PostgreSQL (localhost:5432)
# - Redis (localhost:6379)
# - MongoDB (localhost:27017)
```

---

## 📖 How to Use Labs

### Lab Format

Each lab follows this structure:

```markdown
# Lab: System Name

## Part 1: MVP (100 users)
- Requirements
- Architecture diagram
- Tasks (step-by-step)
- Check your solution
- Measure performance

## Part 2: Scale Up (10K users)
- What breaks?
- New requirements
- Tasks
- Check your solution
- Compare performance

## Part 3: Scale Further (1M users)
- What breaks?
- New requirements
- Tasks
- Check your solution
- Production considerations
```

### Learning Tips

**1. Don't Skip Parts**
- Build Part 1 completely before Part 2
- Each part teaches specific lessons

**2. Measure Everything**
```bash
# Before optimization
ab -n 1000 -c 10 http://localhost:8000/

# After optimization
ab -n 1000 -c 10 http://localhost:8000/
```

**3. Compare Your Solution**
- Try solving first
- Then check solution
- Understand the differences

**4. Break Things**
- Kill database
- Disconnect network
- See what fails

---

## 🎓 Learning Outcomes

### After Beginner Labs
- Understand caching deeply (not just theory)
- Know when to add read replicas vs sharding
- Can implement rate limiting correctly
- Understand database connection pooling

### After Intermediate Labs
- Can design fan-out patterns
- Understand WebSocket vs polling trade-offs
- Know when to use message queues
- Can implement idempotency

### After Advanced Labs
- Can design multi-region systems
- Understand CAP theorem practically
- Can debug distributed systems
- Know cost optimization strategies

---

## 📚 Lab Catalog

### 🟢 Beginner Labs

#### [Lab 1: URL Shortener](./01-beginner/labs/01-url-shortener.md) ⭐ **Start Here**
Build a URL shortener that scales from 100 to 1M users.

**What you'll learn:**
- Database design
- Caching strategies (cache-aside)
- Consistent hashing
- Base62 encoding
- Rate limiting

**Progression:**
- Part 1: Single server + SQLite (100 users)
- Part 2: PostgreSQL + Redis (10K users)
- Part 3: Sharded DB + CDN (1M users)

**Time:** 3-4 hours total

---

#### [Lab 2: Rate Limiter](./01-beginner/labs/02-rate-limiter.md)
Implement three rate limiting algorithms.

**What you'll learn:**
- Fixed window algorithm
- Sliding window log
- Token bucket algorithm
- Redis for distributed rate limiting

**Time:** 2-3 hours

---

#### [Lab 3: Distributed Cache](./01-beginner/labs/03-distributed-cache.md)
Build a cache that scales horizontally.

**What you'll learn:**
- Cache eviction policies (LRU, LFU)
- Consistent hashing
- Cache stampede prevention
- Hot key problem

**Time:** 3-4 hours

---

#### [Lab 4: Key-Value Store](./01-beginner/labs/04-key-value-store.md)
Build a simple distributed key-value store.

**What you'll learn:**
- Data partitioning
- Replication strategies
- Conflict resolution
- Eventual consistency

**Time:** 4-5 hours

---

#### [Lab 5: Task Queue](./01-beginner/labs/05-task-queue.md)
Build a distributed task queue system.

**What you'll learn:**
- Queue implementations
- Worker pools
- At-least-once delivery
- Dead letter queues

**Time:** 3-4 hours

---

### 🟡 Intermediate Labs

#### [Lab 6: Social Media Feed](./02-intermediate/labs/01-social-feed.md)
Build Instagram/Twitter-like feed at scale.

**What you'll learn:**
- Fan-out on write vs read
- Timeline generation
- Hot user problem
- Graph database for followers

**Progression:**
- Part 1: Simple feed (pull model)
- Part 2: Fan-out on write (push model)
- Part 3: Hybrid approach (push + pull)

**Time:** 6-8 hours

---

#### [Lab 7: Real-time Chat](./02-intermediate/labs/02-realtime-chat.md)
Build WhatsApp-like chat system.

**What you'll learn:**
- Polling vs Long-polling vs WebSocket
- Message delivery guarantees
- Read receipts
- Typing indicators

**Time:** 6-8 hours

---

#### [Lab 8: Video Streaming](./02-intermediate/labs/03-video-streaming.md)
Build YouTube-like video platform.

**What you'll learn:**
- Video transcoding
- Adaptive bitrate streaming (HLS, DASH)
- CDN integration
- Progress tracking

**Time:** 8-10 hours

---

#### [Lab 9: Search Engine](./02-intermediate/labs/04-search-engine.md)
Build Google-like search with ElasticSearch.

**What you'll learn:**
- Inverted index
- Ranking algorithms (TF-IDF, BM25)
- Autocomplete
- Fuzzy search

**Time:** 6-8 hours

---

#### [Lab 10: Payment System](./02-intermediate/labs/05-payment-system.md)
Build Stripe-like payment processing.

**What you'll learn:**
- Idempotency keys
- Distributed transactions
- Saga pattern
- Webhook delivery

**Time:** 8-10 hours

---

### 🔴 Advanced Labs

#### [Lab 11: Multi-Region Setup](./03-advanced/labs/01-multi-region.md)
Deploy system across multiple AWS regions.

**What you'll learn:**
- Active-active vs active-passive
- Data replication strategies
- Conflict resolution (CRDTs)
- Latency-based routing

**Time:** 10-12 hours

---

#### [Lab 12: Chaos Engineering](./03-advanced/labs/02-chaos-engineering.md)
Break your system to make it stronger.

**What you'll learn:**
- Chaos Monkey implementation
- Failure injection
- Circuit breaker testing
- Graceful degradation

**Time:** 8-10 hours

---

#### [Lab 13: Time-Series Database](./03-advanced/labs/03-timeseries-db.md)
Handle billions of metrics (monitoring system).

**What you'll learn:**
- Time-series data structures
- Downsampling
- Aggregation strategies
- Query optimization

**Time:** 10-12 hours

---

#### [Lab 14: ML Model Serving](./03-advanced/labs/04-ml-model-serving.md)
Deploy ML models at scale.

**What you'll learn:**
- Model versioning
- A/B testing
- Feature store
- Batch vs real-time inference

**Time:** 10-12 hours

---

#### [Lab 15: Event Sourcing](./03-advanced/labs/05-event-sourcing.md)
Build system with event sourcing + CQRS.

**What you'll learn:**
- Event store design
- Projection building
- Snapshot strategies
- Time travel debugging

**Time:** 12-15 hours

---

## 🔬 Lab Infrastructure

### Docker Compose Setup

```yaml
# hands-on-labs/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: labs
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongo_data:/data/db

  elasticsearch:
    image: elasticsearch:8.11.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - es_data:/usr/share/elasticsearch/data

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

volumes:
  postgres_data:
  redis_data:
  mongo_data:
  es_data:
```

---

## 🎯 Success Metrics

### Lab Completion Criteria

**For each lab, you should be able to:**
- ✅ Explain why you made each design decision
- ✅ Measure performance before/after optimization
- ✅ Identify bottlenecks using profiling
- ✅ Estimate costs at scale
- ✅ Handle edge cases and failures

### Performance Targets

**Beginner Labs:**
- URL Shortener: 1000 RPS, <50ms p99
- Rate Limiter: 10K RPS, <5ms p99
- Distributed Cache: 10K RPS, 95%+ hit rate

**Intermediate Labs:**
- Social Feed: 5K RPS, <200ms p99
- Real-time Chat: 10K concurrent users
- Payment System: 100% consistency, idempotent

**Advanced Labs:**
- Multi-Region: <100ms cross-region latency
- Chaos: 99.9% uptime despite failures
- Time-Series: 1M writes/sec

---

## 💡 Pro Tips

### 1. Start Small, Then Scale
```python
# ❌ Don't do this
def design_url_shortener():
    # Let me design for 1B users from day 1
    # with sharding, caching, CDN, multi-region...

# ✅ Do this
def design_url_shortener_v1():
    # Single server, SQLite, works for 100 users
    # Measure, find bottleneck, then optimize
```

### 2. Measure Everything
```bash
# Before optimization
hey -n 10000 -c 100 http://localhost:8000/shorten
# 500 RPS, 200ms average

# After adding Redis cache
hey -n 10000 -c 100 http://localhost:8000/shorten
# 5000 RPS, 20ms average ← 10x improvement!
```

### 3. Break Things
```bash
# Kill database
docker stop postgres

# See what happens
curl http://localhost:8000/shorten
# Should see graceful error, not crash

# Kill cache
docker stop redis

# System should still work (slower)
```

### 4. Compare Solutions
- Try solving first (1-2 hours)
- Get stuck? Check hints
- Still stuck? Check solution
- Understand WHY solution works

---

## 🤝 Community

### Share Your Solutions
- Fork the repo
- Implement labs in your language
- Share on Twitter/LinkedIn with #SystemDesignLabs
- Help others in discussions

### Get Help
- GitHub Discussions for questions
- Check solution explanations
- Compare with others' solutions

---

## 📝 Assessment Quiz

After completing labs, test your understanding:

### Beginner Quiz
1. When should you add caching? (calculate read:write ratio)
2. What breaks first when scaling from 100 to 10K users?
3. When do you need consistent hashing vs simple modulo?

### Intermediate Quiz
1. Fan-out on write vs read - which for Twitter? Instagram? WhatsApp?
2. How do you handle a celebrity with 100M followers posting?
3. When is eventual consistency acceptable?

### Advanced Quiz
1. How do you resolve conflicts in multi-master setup?
2. What's the cost difference: single region vs multi-region?
3. How do you debug a distributed system with 100 microservices?

---

## 🚀 Next Steps

1. **Start with Lab 1:** [URL Shortener](./01-beginner/labs/01-url-shortener.md)
2. **Set up environment:** `docker-compose up -d`
3. **Join community:** GitHub Discussions
4. **Track progress:** Check off completed labs above

---

**Remember:** You learn system design by building systems, not just reading about them. Start building! 🎯

Good luck! 🚀
