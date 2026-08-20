# Ambassador Pattern

## Overview

The **Ambassador Pattern** creates helper services (ambassadors) that sit between your application and external services. The ambassador handles common connectivity tasks like **retry logic**, **circuit breaking**, **logging**, **monitoring**, and **security** on behalf of the client application.

Think of it as a **diplomatic ambassador** - just as an ambassador represents your country in foreign affairs, an ambassador service represents your application when communicating with external services.

## Problem

Your application needs to call external APIs, but you end up with:

❌ **Repeated boilerplate code** for retries, timeouts, and error handling
❌ **Scattered monitoring/logging** logic across multiple services
❌ **Difficult to enforce policies** consistently (rate limiting, auth, etc.)
❌ **Hard to test** because network logic is mixed with business logic
❌ **Language-specific implementations** if you have polyglot services

```python
# Every service has this repeated code
response = requests.get(api_url)
if response.status_code == 500:
    time.sleep(1)  # retry logic
    response = requests.get(api_url)
log(response)  # logging
metrics.record(response)  # monitoring
```

## Solution

✅ Create an **Ambassador service** that handles all connectivity concerns
✅ **Centralize** retry logic, monitoring, and security in one place
✅ **Decouple** network concerns from business logic
✅ **Reuse** the same ambassador across different services
✅ **Test easily** by mocking the ambassador

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│             │         │              │         │             │
│ Application ├────────►│  Ambassador  ├────────►│  External   │
│             │         │   Service    │         │     API     │
│             │         │              │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
                             │
                             │ Handles:
                             ├─ Retries
                             ├─ Circuit Breaking
                             ├─ Logging
                             ├─ Monitoring
                             ├─ Auth/Security
                             └─ Rate Limiting
```

## Real-World Use Cases

### 1. **Microservices Communication**
**Scenario**: E-commerce app with 20 microservices calling external payment, shipping, and notification APIs.

**Without Ambassador**: Each service implements its own retry, logging, and monitoring → 20 different implementations

**With Ambassador**: Single ambassador handles all external calls → consistent behavior, centralized monitoring

### 2. **Legacy System Integration**
**Scenario**: Modern app needs to call unreliable legacy SOAP API with custom authentication.

**Without Ambassador**: Every team struggles with SOAP, auth tokens, and retries

**With Ambassador**: Ambassador handles SOAP conversion, auth refresh, intelligent retries

### 3. **Multi-Cloud API Gateway**
**Scenario**: Application calls AWS S3, Google Cloud Storage, and Azure Blob Storage.

**Without Ambassador**: Different SDK patterns, different error handling for each cloud

**With Ambassador**: Unified interface, consistent retry/timeout logic for all clouds

### 4. **Third-Party API Rate Limiting**
**Scenario**: Calling Stripe API with strict rate limits (100 req/sec).

**Without Ambassador**: Each service tracks its own rate limits → easy to exceed limits

**With Ambassador**: Centralized rate limiting and queuing prevents API ban

## When to Use

✅ You call **multiple external APIs** with similar connectivity needs
✅ You need **consistent retry/timeout** behavior across services
✅ You want to **centralize monitoring** of external API calls
✅ You have **polyglot services** (Python, Node, Go) that need the same logic
✅ You need to **enforce policies** (rate limiting, security) uniformly

## When NOT to Use

❌ Single simple API call with no special requirements
❌ API already has excellent SDK with built-in resilience
❌ Ultra-low latency requirements (extra hop adds ~1-5ms)
❌ Internal service-to-service calls in same cluster (use service mesh instead)

## Related Patterns

- **Sidecar Pattern**: Ambassador runs as sidecar container (common in Kubernetes)
- **Gateway Aggregation**: Combines multiple API calls into one
- **Retry Pattern**: Part of what Ambassador implements
- **Circuit Breaker**: Often implemented within Ambassador

## Implementation Approaches

### 1. **HTTP Proxy** (Simplest)
Ambassador runs as HTTP proxy, application makes normal HTTP calls through it.

### 2. **Sidecar Container** (Kubernetes/Docker)
Ambassador runs as sidecar container alongside main application container.

### 3. **SDK/Library** (Language-Specific)
Ambassador logic packaged as library, imported into application.

### 4. **Service Mesh** (Enterprise)
Istio, Linkerd provide ambassador-like capabilities at infrastructure level.

## Key Metrics to Monitor

1. **Retry Rate**: How often requests are retried
2. **Circuit Breaker Status**: Open/closed state per external API
3. **Latency**: P50, P95, P99 response times
4. **Error Rate**: Failed requests after all retries
5. **Rate Limit Hits**: How often rate limits are reached

## Python Implementation Highlights

Our implementation shows:
- ✅ **Retry with exponential backoff**
- ✅ **Circuit breaker** to prevent cascading failures
- ✅ **Request/response logging**
- ✅ **Metrics collection** (success rate, latency)
- ✅ **Rate limiting** with token bucket
- ✅ **Timeout handling**
- ✅ **Request/response transformation**

## Performance Impact

| Metric | Without Ambassador | With Ambassador | Impact |
|--------|-------------------|-----------------|--------|
| Network Hops | 1 | 2 | +1-5ms latency |
| Retry Logic | Manual, inconsistent | Automatic, smart | -50% failures |
| Debugging Time | Hours (scattered logs) | Minutes (centralized) | -80% debug time |
| Code Duplication | High (every service) | None (centralized) | -70% code |
| Rate Limit Errors | Common | Rare | -95% API bans |

## Example

```python
# WITHOUT Ambassador - Every call needs this boilerplate
import requests
import time

def call_payment_api(data):
    for attempt in range(3):
        try:
            response = requests.post("https://api.stripe.com/charge",
                                     json=data, timeout=5)
            if response.status_code < 500:
                return response.json()
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

# WITH Ambassador - Clean business logic
from ambassador import PaymentAmbassador

def call_payment_api(data):
    return ambassador.post("/charge", data)  # Retry/logging handled!
```

## Files

- [without_pattern/main.py](./without_pattern/main.py) - Direct API calls with manual retry
- [with_pattern/main.py](./with_pattern/main.py) - Using Ambassador pattern
- [demo/run_demo.py](./demo/run_demo.py) - Interactive demonstration
- [benchmarks/benchmark.py](./benchmarks/benchmark.py) - Performance comparison

## Running the Demo

```bash
# Install dependencies
pip install requests flask

# Terminal 1: Start mock API server
python demo/mock_api.py

# Terminal 2: Run demo
python demo/run_demo.py

# Run benchmarks
python benchmarks/benchmark.py
```

## Further Reading

- [Microsoft Azure Ambassador Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/ambassador)
- [Sidecar Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar)
- [Service Mesh (Istio)](https://istio.io/latest/docs/concepts/what-is-istio/)
