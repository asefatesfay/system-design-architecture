# Retry Storm Antipattern

## 🔴 The Problem

Aggressive retry logic without proper backoff, jitter, or circuit breakers. When a service fails, all clients retry simultaneously, amplifying the load and preventing recovery. This leads to:
- Cascading failures across services
- Extended outages (preventing service recovery)
- Resource exhaustion on failing services
- Thundering herd problem

## Common Examples

1. **Immediate retries** - Retrying failed requests without delay
2. **No exponential backoff** - Fixed retry intervals
3. **No jitter** - All clients retry at the same time
4. **No circuit breaker** - Keep retrying even when service is clearly down
5. **No retry budget** - Unlimited retries exhausting resources

## 📊 Impact

- **Failure amplification**: 10-100x load increase on failing service
- **Extended downtime**: Service can't recover under retry load
- **Cascading failures**: Entire system becomes unavailable
- **Resource exhaustion**: Connection pools, threads, memory depleted

## 🏃 Running the Examples

### Bad Example (Retry Storm)
```bash
cd bad
go run main.go
```

### Good Example (Proper Retry Strategy)
```bash
cd good
go run main.go
```

### Simulate Failure
```bash
# Watch the logs to see retry behavior
# Bad version will hammer the failing service
# Good version will back off and eventually circuit break
```

## 🎯 Key Takeaways

1. **Exponential backoff**: Increase delay between retries (1s, 2s, 4s, 8s...)
2. **Jitter**: Add randomness to prevent thundering herd
3. **Circuit breaker**: Stop retrying when service is down
4. **Retry budget**: Limit total retry attempts
5. **Fail fast**: Return errors quickly when service is unhealthy

## 📚 Related Patterns

- Circuit Breaker Pattern
- Bulkhead Pattern
- Timeout Pattern
- Rate Limiting
