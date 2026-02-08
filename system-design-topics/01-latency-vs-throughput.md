# Latency vs Throughput

## Definition

**Latency** is the time it takes to complete a single request (response time), while **Throughput** is the number of requests that can be processed in a given time period (requests per second).

## Key Concepts

### Latency
- Measured in: milliseconds (ms), seconds (s)
- Represents: "How fast is one operation?"
- Lower is better
- Types:
  - **Network Latency**: Time for data to travel over network
  - **Processing Latency**: Time to process the request
  - **I/O Latency**: Time for disk/database operations
  - **Queueing Latency**: Time spent waiting in queues

### Throughput
- Measured in: requests/second (RPS), queries/second (QPS), transactions/second (TPS)
- Represents: "How many operations can we handle?"
- Higher is better
- Limited by: CPU, memory, network bandwidth, I/O capacity

## Real-World Examples

### Netflix
- **Latency Focus**: Video start time must be <1 second (critical for user experience)
- **Throughput Focus**: Must handle 250+ million concurrent streaming requests during peak hours
- **Trade-off**: They use adaptive bitrate streaming to balance both

### Google Search
- **Latency**: Average search latency <200ms 
- **Throughput**: Handles 99,000+ searches per second (8.5 billion/day)
- **Optimization**: Pre-computing results, distributed caching, CDNs

### Amazon DynamoDB
- **Latency**: Single-digit millisecond latency at any scale
- **Throughput**: Can handle 10+ trillion requests per day
- **Design**: Uses consistent hashing and replication

### Twitter
- **Latency**: Tweet posting <100ms
- **Throughput**: 6,000 tweets per second (peak: 25,000+)
- **Challenge**: Timeline reads (300,000 RPS) vs writes

## The Trade-off

```
High Throughput ≠ Low Latency
```

**Example Scenario:**
```
System A: 10ms latency, 100 RPS throughput
System B: 100ms latency, 1000 RPS throughput
```

System B has better throughput but worse latency. Which is better depends on your use case!

## When to Optimize for Latency

✅ **Real-time systems**
- Trading platforms (microseconds matter)
- Gaming servers (lag affects gameplay)
- Voice/video calls (WebRTC, Zoom)

✅ **User-facing applications**
- E-commerce checkout (reduce cart abandonment)
- Search engines (users expect instant results)
- Mobile apps (limited by cellular networks)

✅ **Chain of operations**
- Microservices with many dependent calls
- Each service's latency adds up

## When to Optimize for Throughput

✅ **Batch processing**
- ETL pipelines
- Data analytics (Hadoop, Spark)
- Log processing

✅ **High-volume systems**
- Ad serving platforms
- IoT data ingestion
- Social media feeds

✅ **Background tasks**
- Email sending
- Report generation
- Image processing

## How They Relate

### Little's Law
```
Average # of requests in system = Throughput × Latency
```

**Example:**
- If throughput = 100 RPS
- And latency = 0.5 seconds
- Then average concurrent requests = 50

### Impact of Latency on Throughput

**Without Parallelism:**
```
If one request takes 100ms (latency)
Maximum throughput = 1000ms / 100ms = 10 RPS
```

**With Parallelism (10 threads):**
```
Maximum throughput = 10 threads × 10 RPS = 100 RPS
```

## Optimization Strategies

### Reducing Latency
1. **Caching** (Redis, Memcached)
2. **CDNs** for static content
3. **Database indexing**
4. **Connection pooling**
5. **Asynchronous processing**
6. **Geographic distribution** (edge servers)
7. **HTTP/2 multiplexing**

### Increasing Throughput
1. **Horizontal scaling** (add more servers)
2. **Load balancing**
3. **Batch processing**
4. **Connection reuse (Keep-Alive)**
5. **Compression**
6. **Efficient serialization** (Protocol Buffers, Avro)
7. **Resource pooling**

## Measuring Both

### Percentiles Matter

Don't just measure averages:
- **P50 (Median)**: 50% of requests are faster
- **P95**: 95% of requests are faster
- **P99**: 99% of requests are faster
- **P99.9**: Critical for SLA commitments

**Amazon's approach:** They optimize for P99.9 because slow requests affect revenue.

### Example Metrics
```
Latency:
  P50: 50ms
  P95: 200ms
  P99: 500ms
  P99.9: 2000ms

Throughput:
  Average: 10,000 RPS
  Peak: 50,000 RPS
```

## Common Pitfalls

❌ **Optimizing the wrong metric**
- E-commerce: Latency > Throughput (users wait)
- Log processing: Throughput > Latency (batch acceptable)

❌ **Ignoring tail latency**
- Average might be great, but P99 could be terrible
- Affects overall user experience

❌ **Not considering the full path**
- Frontend might be fast, but backend slow
- Network latency between services

## Interview Tips

**Questions you might get:**
1. "How would you improve latency for a global user base?" → CDN, edge computing, regional databases
2. "System handles 10K RPS but users complain it's slow?" → Check latency percentiles, not just throughput
3. "Trade-off between latency and throughput?" → Depends on use case, batch vs real-time

**Key Takeaway:** Know when to prioritize which metric based on business requirements.
