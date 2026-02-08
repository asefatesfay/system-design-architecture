# Circuit Breaker

## Definition

**Circuit Breaker** is a design pattern that prevents an application from repeatedly trying to execute an operation that's likely to fail, allowing it to continue operating without waiting for the fault to be fixed or wasting resources on doomed requests.

## Key Concept

Like an electrical circuit breaker that trips to prevent damage:

```
Closed (Normal) → Open (Failure) → Half-Open (Testing) → Closed (Recovered)
     ↓                  ↓                   ↓                    ↓
All requests pass  Fail fast         Limited test       Resume normal
 ```

## States

### 1. Closed (Normal Operation)
```
Requests → Service ✅
All requests pass through
Monitor failure rate
```

### 2. Open (Service Down)
```
Requests → ❌ Fail immediately (don't even try)
No requests to failing service
Wait timeout period
Prevents cascade failures
```

### 3. Half-Open (Testing Recovery)
```
Requests → Limited requests to test ⚠️
If success → Close circuit ✅
If failure → Open circuit again ❌
```

## Real-World Examples

### Netflix Hystrix
**Most famous circuit breaker library**

```java
@HystrixCommand(
    fallbackMethod = "getDefaultRecommendations",
    commandProperties = {
        @HystrixProperty(name="circuitBreaker.errorThresholdPercentage", value="50"),
        @HystrixProperty(name="circuitBreaker.sleepWindowInMilliseconds", value="10000")
    }
)
public List<Movie> getRecommendations(userId) {
    return recommendationService.fetch(userId);  // May fail
}

public List<Movie> getDefaultRecommendations(userId) {
    return Arrays.asList(defaultMovies);  // Fallback ✅
}
```

**When recommendation service fails:**
- First 50% errors → Circuit opens
- For next 10 seconds → Return fallback immediately
- After 10s → Try again (half-open)

### AWS API Gateway
**Built-in circuit breaker**

```
Configuration:
- Threshold: 50% error rate
- Minimum requests: 100
- Break duration: 30 seconds

If backend fails:
1. API Gateway detects 50% error rate (after 100 requests)
2. Opens circuit for 30 seconds
3. Returns 503 Service Unavailable
4. After 30s → Tries again
```

### Microservices (Netflix, Uber, Amazon)

**Problem without circuit breaker:**
```
User Service → Order Service (down) → Wait 30s timeout ❌
1000 users × 30s = 30,000s of blocked threads!
User Service crashes from resource exhaustion 🔥
```

**With circuit breaker:**
```
User Service → Order Service (down, circuit open)
→ Fail immediately (1ms) ✅
→ Return cached data or graceful error
User Service stays healthy ✅
```

## Implementation

### Python (using pybreaker)

```python
import pybreaker

# Configure circuit breaker
breaker = pybreaker.CircuitBreaker(
    fail_max=5,           # Open after 5 failures
    timeout_duration=60   # Stay open for 60 seconds
)

@breaker
def call_external_api():
    response = requests.get('https://api.example.com/data')
    response.raise_for_status()
    return response.json()

# Usage
try:
    data = call_external_api()
except pybreaker.CircuitBreakerError:
    # Circuit is open, fail fast
    return get_cached_data()  # Fallback ✅
```

### Custom Implementation

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise Exception("Circuit breaker HALF_OPEN limit reached")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def risky_operation():
    breaker.call(external_api_call)
```

## Best Practices

✅ **Set appropriate thresholds**
✅ **Implement fallback mechanisms**  
✅ **Monitor circuit breaker state**
✅ **Different breakers for different services**
✅ **Combine with retry and timeout patterns**

**Key Takeaway:** Circuit breakers prevent cascade failures by failing fast when services are down, allowing systems to recover gracefully!
