# Microservices Architecture

## Definition

**Microservices Architecture** is an architectural style that structures an application as a collection of small, independent, loosely coupled services, each responsible for a specific business capability.

## Monolith vs Microservices

### Monolith (Traditional)
```
┌─────────────────────────────┐
│    Single Application       │
│                             │
│  User Module                │
│  Product Module             │
│  Order Module               │
│  Payment Module             │
│                             │
│  Single Database            │
└─────────────────────────────┘
- Deploy entire app for small change
- One tech stack
```

### Microservices
```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  User    │  │ Product  │  │  Order   │
│ Service  │  │ Service  │  │ Service  │
│          │  │          │  │          │
│  Own DB  │  │  Own DB  │  │  Own DB  │
└──────────┘  └──────────┘  └──────────┘
- Deploy independently
- Different tech stacks possible
```

## Real-World Examples

### Netflix
**From monolith to 700+ microservices**

```
Services:
- User Service (account management)
- Recommendation Service (personalized suggestions)
- Video Encoding Service (transcode videos)
- Playback Service (streaming)
- Billing Service (subscriptions)
- ...700+ more

Benefits:
- Teams work independently
- Deploy 1000+ times/day
- Scale services differently
  (Encoding needs more CPU, Recommendation needs more memory)
```

### Amazon
**"Two-pizza teams" - each team owns microservice**

```
- Product Catalog Service
- Shopping Cart Service
- Order Service
- Payment Service
- Inventory Service
- Shipping Service

Each team:
- Owns service end-to-end
- Deploys independently
- Uses best tech for their problem
```

### Uber
```
- Trip Service (ride matching)
- Mapping Service (routes, ETA)
- Pricing Service (surge pricing)
- Payment Service (driver/rider payments)
- Driver Service (driver management)
- Rider Service (rider management)

Example: Surge pricing changes deployed without touching other services
```

### Spotify
```
- User Service
- Playlist Service
- Music Catalog Service
- Recommendation Service
- Social Service (following, sharing)

Teams iterate independently
Deploy multiple times per day
```

## Benefits

✅ **Independent deployment**
```
Update Payment Service without touching User Service
Deploy 100x per day instead of 1x per month
```

✅ **Technology diversity**
```
User Service: Java + PostgreSQL
Recommendation Service: Python + ML models
Video Service: Go + S3
```

✅ **Fault isolation**
```
Payment Service crashes → Other services still work
Not entire app down ✅
```

✅ **Scalability**
```
Scale services independently:
Video streaming needs 100 instances
User profile needs 10 instances
```

✅ **Team autonomy**
```
Small teams (5-10 people) own services
Faster decision making
Clear ownership
```

## Challenges

❌ **Complexity**
```
Monolith: 1 app, 1 database
Microservices: 50 services, 50 databases, network calls
```

❌ **Network latency**
```
Monolith: function call (1ms)
Microservices: HTTP call (50ms)

User request might call 10 services = 500ms!
```

❌ **Data consistency**
```
Monolith: Single DB transaction (ACID)
Microservices: Distributed transaction (complex!)

How to ensure order + payment both succeed?
→ Saga pattern, eventual consistency
```

❌ **Testing complexity**
```
Test interactions between 50 services?
Need integration tests, contract tests
```

❌ **Operational overhead**
```
Monitor 50 services
Deploy 50 services
Debug across services
```

## Communication Patterns

### 1. Synchronous (HTTP/gRPC)
```
User Service → GET /products/123 → Product Service
                ← Product data ←

Pros: Simple, immediate response
Cons: Tight coupling, if Product Service down, User Service affected
```

### 2. Asynchronous (Message Queue)
```
Order Service → [Queue] → Email Service

Pros: Loose coupling, fault tolerant
Cons: Eventual consistency, harder to debug
```

### 3. Event-Driven
```
Order Created → Event Bus → [Inventory Service, Email Service, Analytics Service]
                           All react to event

Pros: Loose coupling, scalable
Cons: Complex flow, hard to trace
```

## Service Discovery

**Problem:** Services need to find each other
```
Order Service needs to call Payment Service
But Payment Service IP address changes (auto-scaling)
```

**Solution: Service Registry**
```
1. Consul / Eureka / etcd
2. Services register themselves: "Payment Service @ 10.0.0.5:8080"
3. Order Service queries registry for Payment Service location
4. Call discovered address
```

## API Gateway

**Single entry point for clients**

```
          ┌─────────────┐
          │ API Gateway │
          └──────┬──────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
│  User  │  │Product │  │ Order  │
│Service │  │Service │  │Service │
└────────┘  └────────┘  └────────┘

Benefits:
- Authentication/authorization centralized
- Rate limiting
- Request routing
- Response aggregation
```

## Data Management

### Database per Service
```
✅ Independence
✅ Right DB for the job
❌ Joins across services hard
❌ Distributed transactions
```

### Saga Pattern (Distributed Transactions)
```
Place Order:
1. Order Service: Create order → Success
2. Payment Service: Charge card → Success
3. Inventory Service: Reserve items → FAIL

Compensating transactions:
← Refund payment
← Cancel order

Eventually consistent
```

## Best Practices

✅ **Single Responsibility:** One service = one business capability

✅ **Design for failure:**
```python
# Circuit breaker pattern
try:
    response = payment_service.charge()
except ServiceDown:
    return "Payment temporarily unavailable"
```

✅ **Centralized logging:**
```
All services → Elasticsearch → Kibana
Trace request across services (correlation ID)
```

✅ **Monitoring:**
```
Prometheus + Grafana
- Service health
- Latency
- Error rates
```

✅ **Automated deployment:**
```
CI/CD pipeline
Containerization (Docker)
Orchestration (Kubernetes)
```

## When to Use Microservices

✅ **Large teams** (100+ engineers)
✅ **Complex domain** (many business capabilities)
✅ **Scale requirements** (services need different scaling)
✅ **Fast iteration** (deploy multiple times/day)
✅ **Technology diversity** (best tool for each job)

## When NOT to Use Microservices

❌ **Small team** (< 10 engineers) - overhead not worth it
❌ **Simple app** - monolith fine
❌ **Early startup** - iterate fast, don't optimize early
❌ **No DevOps expertise** - need strong ops team

**Start with monolith, extract services as you grow!**

## Migration Strategy

```
1. Start: Monolith
2. Identify bounded contexts (user, product, order)
3. Extract one service at a time
4. Strangler pattern: Gradually replace monolith
5. Don't do "big bang" rewrite!

Netflix took years to migrate from monolith
```

## Technologies

- **Frameworks:** Spring Boot (Java), Flask/FastAPI (Python), Express (Node.js)
- **Communication:** REST, gRPC, message queues (Kafka, RabbitMQ)
- **Service Discovery:** Consul, Eureka, etcd
- **API Gateway:** Kong, NGINX, AWS API Gateway
- **Orchestration:** Kubernetes, Docker Swarm
- **Monitoring:** Prometheus, Grafana, Datadog, New Relic

## Interview Tips

**Q: "Monolith vs Microservices?"**

**A:** Monolith = single app, simpler, good for small teams. Microservices = independent services, complex, good for large orgs. Microservices enable independent deployment, tech diversity, scalability. But add network latency, distributed data challenges. Netflix/Amazon use microservices (100s of engineers), startups often use monoliths.

**Q: "Challenges with microservices?"**

**A:** 1) Distributed data (transactions across services hard), 2) Network latency (service calls slower than function calls), 3) Operational complexity (monitor/deploy 50 services), 4) Testing (integration across services). Solutions: Saga pattern, circuit breakers, API gateway, centralized logging/monitoring.

**Q: "How do microservices communicate?"**

**A:** Synchronous (HTTP/gRPC for immediate response), Asynchronous (message queues for loose coupling), Event-driven (services react to events). Use sync for queries (get user), async for commands (send email), events for broadcasting (order created).

**Key Takeaway:** Microservices enable independence and scalability but add complexity. Use when benefits outweigh costs!
