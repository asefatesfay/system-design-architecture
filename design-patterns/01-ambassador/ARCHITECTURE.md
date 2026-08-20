# Ambassador Pattern - Architecture

## Pattern Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Payment    │  │   Shipping   │  │ Notification │              │
│  │   Service    │  │   Service    │  │   Service    │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                      │
│         └──────────────────┴──────────────────┘                      │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Ambassador Service                              │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  🔄 Retry Logic          (Exponential Backoff)                  │ │
│  │  🛡️  Circuit Breaker      (Prevent Cascading Failures)          │ │
│  │  📊 Metrics Collection   (Success Rate, Latency)                │ │
│  │  📝 Logging              (Request/Response)                     │ │
│  │  ⚡ Rate Limiting         (Token Bucket)                         │ │
│  │  ⏱️  Timeout Handling     (Configurable)                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External APIs                                   │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Payment    │  │   Shipping   │  │    Email     │              │
│  │   API        │  │   API        │  │    API       │              │
│  │  (Stripe)    │  │  (FedEx)     │  │ (SendGrid)   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Without Ambassador (Problem)

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   Payment    │        │   Shipping   │        │ Notification │
│   Service    │        │   Service    │        │   Service    │
│              │        │              │        │              │
│ ┌──────────┐ │        │ ┌──────────┐ │        │ ┌──────────┐ │
│ │  Retry   │ │        │ │  Retry   │ │        │ │  Retry   │ │
│ │  Logic   │ │        │ │  Logic   │ │        │ │  Logic   │ │
│ │(3 times) │ │        │ │(3 times) │ │        │ │(2 times) │ │  ❌ Inconsistent!
│ └──────────┘ │        │ └──────────┘ │        │ └──────────┘ │
│              │        │              │        │              │
│ ┌──────────┐ │        │ ┌──────────┐ │        │ ┌──────────┐ │
│ │ Logging  │ │        │ │ Logging  │ │        │ │ Logging  │ │
│ │          │ │        │ │          │ │        │ │          │ │  ❌ Duplicated!
│ └──────────┘ │        │ └──────────┘ │        │ └──────────┘ │
│              │        │              │        │              │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       ▼                       ▼                       ▼
   Payment API            Shipping API              Email API
```

**Problems**:
- ❌ Code duplication (retry logic in 3 places)
- ❌ Inconsistent behavior (different retry counts)
- ❌ Hard to maintain (change requires updating 3 services)
- ❌ Scattered monitoring (no centralized metrics)

## With Ambassador (Solution)

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   Payment    │        │   Shipping   │        │ Notification │
│   Service    │        │   Service    │        │   Service    │
│              │        │              │        │              │
│  (Clean!)    │        │  (Clean!)    │        │  (Clean!)    │
│              │        │              │        │              │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       └───────────────────────┴───────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Ambassador Service  │
                    │                      │
                    │  ✅ Retry Logic      │
                    │  ✅ Circuit Breaker  │
                    │  ✅ Logging          │
                    │  ✅ Monitoring       │
                    │  ✅ Rate Limiting    │
                    │  ✅ Timeout          │
                    │                      │
                    └──────────┬───────────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
   Payment API            Shipping API              Email API
```

**Benefits**:
- ✅ No code duplication (centralized logic)
- ✅ Consistent behavior (same retry/timeout everywhere)
- ✅ Easy to maintain (change in one place)
- ✅ Centralized monitoring (single metrics source)

## Flow Diagram - Request with Retry

```
Application
    │
    │ 1. make_payment()
    ▼
Ambassador
    │
    │ 2. Check circuit breaker
    ├──► [OPEN] → Return error immediately
    │
    │ 3. Check rate limit
    ├──► [EXCEEDED] → Wait for tokens
    │
    │ 4. Attempt #1
    ▼
Payment API
    │
    │ ❌ 500 Error
    ▼
Ambassador
    │
    │ 5. Log failure
    │ 6. Increment failure count
    │ 7. Wait 1s (exponential backoff)
    │
    │ 8. Attempt #2
    ▼
Payment API
    │
    │ ❌ 500 Error
    ▼
Ambassador
    │
    │ 9. Log failure
    │ 10. Wait 2s (exponential backoff)
    │
    │ 11. Attempt #3
    ▼
Payment API
    │
    │ ✅ 200 Success
    ▼
Ambassador
    │
    │ 12. Log success
    │ 13. Record metrics
    │ 14. Reset failure count
    ▼
Application
    │
    │ ✅ Payment successful!
```

## Circuit Breaker States

```
            ┌─────────────┐
            │   CLOSED    │ ◄─────────────┐
            │  (Normal)   │                │
            └──────┬──────┘                │
                   │                       │
        Failures   │                       │ Success
        reach      │                       │ in half-open
        threshold  │                       │
                   ▼                       │
            ┌─────────────┐                │
            │    OPEN     │                │
            │  (Failing)  │                │
            └──────┬──────┘                │
                   │                       │
        Timeout    │                       │
        expires    │                       │
                   ▼                       │
            ┌─────────────┐                │
            │  HALF-OPEN  │ ───────────────┘
            │  (Testing)  │
            └─────────────┘
                   │
        Failure    │
                   ▼
            (Back to OPEN)
```

### States Explained

1. **CLOSED** (Normal Operation)
   - All requests pass through
   - Failures are tracked
   - If failures reach threshold → OPEN

2. **OPEN** (Failing)
   - Requests fail immediately (no API call)
   - Protects external API from overload
   - After timeout → HALF-OPEN

3. **HALF-OPEN** (Testing Recovery)
   - Allow one request through
   - If success → CLOSED
   - If failure → OPEN

## Rate Limiting - Token Bucket

```
Time: 0s
Bucket: [●●●●●] (5 tokens, capacity=5, refill=1/sec)
Request 1: ✅ Take 1 token → [●●●●○]
Request 2: ✅ Take 1 token → [●●●○○]
Request 3: ✅ Take 1 token → [●●○○○]

Time: 1s (refill 1 token)
Bucket: [●●●○○]
Request 4: ✅ Take 1 token → [●●○○○]

Time: 2s (refill 1 token)
Bucket: [●●●○○]
Request 5: ✅ Take 1 token → [●●○○○]
Request 6: ❌ No tokens → Wait...

Time: 3s (refill 1 token)
Bucket: [●●●○○]
Request 6: ✅ Take 1 token → [●●○○○]
```

## Deployment Patterns

### 1. Standalone Service (Microservices)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Service A  │────►│             │     │             │
├─────────────┤     │  Ambassador │────►│ External    │
│  Service B  │────►│   Service   │     │ APIs        │
├─────────────┤     │  (Port 8080)│     │             │
│  Service C  │────►│             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 2. Sidecar Container (Kubernetes)

```
┌───────────────────────────────┐
│           Pod                  │
│                                │
│  ┌──────────┐  ┌───────────┐ │     ┌─────────────┐
│  │   App    │  │Ambassador │ │     │             │
│  │Container │─►│ Container │─┼────►│ External    │
│  │(Port 80) │  │(Localhost)│ │     │ APIs        │
│  └──────────┘  └───────────┘ │     │             │
│                                │     └─────────────┘
└───────────────────────────────┘
```

### 3. SDK Library (In-Process)

```
┌─────────────────────┐
│    Application      │
│                     │     ┌─────────────┐
│  ┌───────────────┐ │     │             │
│  │ Ambassador    │─┼────►│ External    │
│  │ SDK Library   │ │     │ APIs        │
│  └───────────────┘ │     │             │
│                     │     └─────────────┘
└─────────────────────┘
```

## Key Design Decisions

### 1. Retry Strategy
**Choice**: Exponential backoff (1s, 2s, 4s)
**Rationale**: Prevents overwhelming recovering services
**Alternative**: Fixed delay (simpler but less effective)

### 2. Circuit Breaker Threshold
**Choice**: 5 consecutive failures
**Rationale**: Balance between sensitivity and stability
**Alternative**: Percentage-based (e.g., 50% over time window)

### 3. Rate Limiting Algorithm
**Choice**: Token bucket
**Rationale**: Allows bursts while enforcing average rate
**Alternative**: Leaky bucket (stricter, no bursts)

### 4. Metrics Collection
**Choice**: In-memory counters
**Rationale**: Fast, simple for demo
**Alternative**: Prometheus, StatsD (production use)

## Performance Characteristics

| Metric | Impact | Mitigation |
|--------|--------|------------|
| Latency Overhead | +1-5ms per request | Acceptable for resiliency benefits |
| Memory Usage | +2-5MB per Ambassador | Minimal compared to service memory |
| CPU Usage | +1-3% | Negligible for most workloads |
| Network Hops | +1 hop | Can use sidecar for localhost only |

## Security Considerations

1. **Credential Management**
   - Ambassador handles API keys
   - Credentials not exposed to application

2. **SSL/TLS**
   - Ambassador terminates SSL
   - Simplifies certificate management

3. **Input Validation**
   - Validate requests before forwarding
   - Prevent injection attacks

4. **Rate Limiting**
   - Protects against DoS
   - Enforces fair use policies

## Monitoring & Observability

Key metrics to track:
```python
{
    "total_requests": 1000,
    "successful_requests": 950,
    "failed_requests": 50,
    "success_rate": "95.0%",
    "average_latency": "0.123s",
    "p95_latency": "0.250s",
    "p99_latency": "0.500s",
    "total_retries": 75,
    "circuit_breaker_state": "closed",
    "circuit_breaker_open_count": 0,
    "rate_limit_hits": 5
}
```

## Testing Strategy

1. **Unit Tests**: Test Ambassador logic in isolation
2. **Integration Tests**: Test with real services
3. **Chaos Tests**: Inject failures, test resilience
4. **Load Tests**: Verify performance under load
5. **Circuit Breaker Tests**: Test state transitions

## Further Reading

- [Microsoft Azure Ambassador Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/ambassador)
- [Netflix Hystrix](https://github.com/Netflix/Hystrix) (Circuit Breaker)
- [Envoy Proxy](https://www.envoyproxy.io/) (Production Ambassador)
- [Istio](https://istio.io/) (Service Mesh)
