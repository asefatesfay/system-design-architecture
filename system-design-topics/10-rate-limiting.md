# Rate Limiting

## Definition

**Rate Limiting** is a technique to control the rate at which requests are processed or accepted by a system, preventing abuse, ensuring fair resource allocation, and protecting against DDoS attacks or system overload.

## Key Concepts

### Why Rate Limiting?

**Without rate limiting:**
```
Malicious user: 1 million requests/second → Server crash! 🔥
Bot scraping: 10,000 requests/second → Database overload ❌
Legitimate users: Can't access service ❌
```

**With rate limiting:**
```
Each User: Max 100 requests/minute
Bot: Blocked after limit exceeded ✅
Legitimate users: Protected ✅
System: Stable ✅
```

### Common Limits

**By API:**
```
Anonymous: 10 requests/minute
Free tier: 100 requests/hour
Paid tier: 10,000 requests/hour
Enterprise: Unlimited (or very high)
```

**By Resource:**
```
Login attempts: 5 per 15 minutes
Password reset: 3 per hour
File upload: 10 per day
Database writes: 1000 per second
```

## Rate Limiting Algorithms

### 1. Token Bucket
**Most flexible and popular**

```python
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
    
    def allow_request(self):
        # Refill tokens based on time elapsed
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        # Check if token available
        if self.tokens >= 1:
            self.tokens -= 1
            return True  # Allow ✅
        return False  # Deny ❌

# Example
bucket = TokenBucket(capacity=100, refill_rate=10)  # 10 tokens/second

# Burst: Can use 100 tokens immediately
# Sustained: 10 requests/second after burst
```

**Characteristics:**
- ✅ Allows bursts (up to capacity)
- ✅ Smooth refill
- ✅ Most widely used

**Used by:** Amazon AWS, Stripe

**Real-world example:**
```
Bucket capacity: 1000 tokens
Refill rate: 100 tokens/second

Scenario:
- User sends 1000 requests instantly → All allowed (burst) ✅
- Then sends 1 request → Blocked (bucket empty) ❌
- Wait 0.01 seconds → 1 token refilled → 1 request allowed ✅
- Sustained: 100 requests/second
```

### 2. Leaky Bucket
**Enforces constant output rate**

```python
import time
from collections import deque

class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        self.capacity = capacity
        self.leak_rate = leak_rate  # requests per second
        self.queue = deque()
        self.last_leak = time.time()
    
    def allow_request(self):
        # Leak (process) requests
        now = time.time()
        elapsed = now - self.last_leak
        leaks = int(elapsed * self.leak_rate)
        for _ in range(min(leaks, len(self.queue))):
            self.queue.popleft()
        self.last_leak = now
        
        # Add request to queue if space available
        if len(self.queue) < self.capacity:
            self.queue.append(now)
            return True  # Allow ✅
        return False  # Deny (bucket full) ❌
```

**Characteristics:**
- ✅ Smooths traffic (constant output)
- ✅ Good for preventing spikes
- ❌ Doesn't allow bursts
- ❌ Can delay requests

**Used by:** Network traffic shaping, queue systems

### 3. Fixed Window Counter
**Simple but has boundary issues**

```python
import time

class FixedWindowCounter:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size  # seconds
        self.counter = 0
        self.window_start = time.time()
    
    def allow_request(self):
        now = time.time()
        
        # Reset window if expired
        if now - self.window_start > self.window_size:
            self.counter = 0
            self.window_start = now
        
        # Check limit
        if self.counter < self.limit:
            self.counter += 1
            return True  # Allow ✅
        return False  # Deny ❌

# Example
limiter = FixedWindowCounter(limit=100, window_size=60)  # 100 req/minute
```

**Problem: Boundary issue**
```
Window 1 (0-60s):  99 requests at t=59s
Window 2 (60-120s): 99 requests at t=61s

Total: 198 requests in 2 seconds! ❌ (Burst at boundary)
```

**Used by:** Simple use cases, non-critical systems

### 4. Sliding Window Log
**More accurate, tracks individual timestamps**

```python
import time
from collections import deque

class SlidingWindowLog:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size  # seconds
        self.log = deque()
    
    def allow_request(self):
        now = time.time()
        
        # Remove old entries outside window
        while self.log and self.log[0] < now - self.window_size:
            self.log.popleft()
        
        # Check limit
        if len(self.log) < self.limit:
            self.log.append(now)
            return True  # Allow ✅
        return False  # Deny ❌
```

**Characteristics:**
- ✅ No boundary issues
- ✅ Accurate
- ❌ Memory intensive (stores all timestamps)

**Used by:** When precision matters

### 5. Sliding Window Counter
**Hybrid: Fixed window + smoothing**

```python
import time
import math

class SlidingWindowCounter:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size
        self.prev_count = 0
        self.curr_count = 0
        self.prev_window_start = time.time()
        self.curr_window_start = time.time()
    
    def allow_request(self):
        now = time.time()
        
        # Move window if needed
        if now - self.curr_window_start > self.window_size:
            self.prev_count = self.curr_count
            self.curr_count = 0
            self.prev_window_start = self.curr_window_start
            self.curr_window_start = now
        
        # Calculate weighted count
        elapsed = now - self.curr_window_start
        overlap = 1 - (elapsed / self.window_size)
        weighted_count = (self.prev_count * overlap) + self.curr_count
        
        # Check limit
        if weighted_count < self.limit:
            self.curr_count += 1
            return True  # Allow ✅
        return False  # Deny ❌
```

**Characteristics:**
- ✅ Smoother than fixed window
- ✅ Memory efficient (2 counters only)
- ✅ Good balance

**Used by:** Redis-based rate limiting (recommended)

## Real-World Examples

### Twitter API
**Different tiers**

```
Standard API:
- 300 requests per 15-minute window
- 900 requests per 15-minute window (elevated access)

Rate limit headers in response:
X-Rate-Limit-Limit: 300
X-Rate-Limit-Remaining: 287
X-Rate-Limit-Reset: 1644364800

When exceeded:
HTTP 429: Too Many Requests
Retry-After: 900 seconds
```

### GitHub API
**Token bucket with different limits**

```
Unauthenticated: 60 requests/hour
Authenticated: 5,000 requests/hour
GitHub Actions: 1,000 requests/hour
Enterprise: 15,000 requests/hour

Conditional requests (304 Not Modified): Don't count toward limit ✅

Headers:
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1644364800
X-RateLimit-Used: 1
```

### AWS API Gateway
**Token bucket algorithm**

```
Throttle settings:
- Rate: 10,000 requests/second
- Burst: 5,000 requests

Example:
- Burst of 5,000 requests → All succeed ✅
- Sustained: 10,000 requests/second

Exceeded:
HTTP 429: Too Many Requests
{"message": "Rate exceeded"}
```

### Stripe API
**Token bucket per resource**

```
Read operations: 100 requests/second
Write operations: 100 requests/second

Per endpoint limits:
/v1/charges: 100/sec
/v1/customers: 100/sec

Headers:
Stripe-RateLimit-Limit: 100
Stripe-RateLimit-Remaining: 99
Stripe-RateLimit-Reset: 1644364800
```

### Cloudflare
**DDoS protection + rate limiting**

```
Free plan: 1 rate limiting rule
Pro plan: 10 rules
Business: 15 rules

Example rule:
- Threshold: 100 requests per 1 minute
- Action: Block for 10 minutes
- Match: URI path = /api/*

Advanced:
- CAPTCHA challenge
- JavaScript challenge
- Managed challenge
```

### Reddit API
**OAuth rate limits**

```
OAuth: 60 requests per minute
Without authentication: 10 requests per minute

User-Agent required (or banned!)

Headers:
X-Ratelimit-Used: 5
X-Ratelimit-Remaining: 55
X-Ratelimit-Reset: 1644364800
```

## Implementation Patterns

### 1. Application-Level (In-Memory)
**Simple, single server**

```python
from functools import wraps
import time

# In-memory storage
rate_limits = {}

def rate_limit(limit=100, window=60):
    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            now = time.time()
            key = f"{user_id}:{func.__name__}"
            
            # Initialize or reset window
            if key not in rate_limits or now - rate_limits[key]['start'] > window:
                rate_limits[key] = {'start': now, 'count': 0}
            
            # Check limit
            if rate_limits[key]['count'] >= limit:
                raise Exception(f"Rate limit exceeded: {limit} requests per {window}s")
            
            rate_limits[key]['count'] += 1
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@rate_limit(limit=10, window=60)
def api_endpoint(user_id):
    return {"data": "response"}
```

**Pros:**
- ✅ Fast (in-memory)
- ✅ Simple

**Cons:**
- ❌ Not distributed (loses state on restart)
- ❌ Doesn't work with multiple servers

### 2. Redis-Based (Distributed)
**Industry standard for distributed systems**

```python
import redis
import time

redis_client = redis.Redis(host='localhost', port=6379)

def rate_limit_redis(user_id, limit=100, window=60):
    key = f"ratelimit:{user_id}"
    now = int(time.time())
    
    # Sliding window using sorted set
    pipe = redis_client.pipeline()
    
    # Remove old entries
    pipe.zremrangebyscore(key, 0, now - window)
    
    # Count requests in window
    pipe.zcard(key)
    
    # Add current request
    pipe.zadd(key, {now: now})
    
    # Set expiry
    pipe.expire(key, window)
    
    results = pipe.execute()
    count = results[1]
    
    if count >= limit:
        return False  # Rate limit exceeded ❌
    return True  # Allow ✅

# Usage
if rate_limit_redis(user_id="user123", limit=100, window=60):
    # Process request
    pass
else:
    # Return 429
    return {"error": "Rate limit exceeded"}, 429
```

**Alternative: Simple counter**
```python
def rate_limit_simple(user_id, limit=100, window=60):
    key = f"ratelimit:{user_id}"
    current = redis_client.get(key)
    
    if current is None:
        # First request in window
        redis_client.setex(key, window, 1)
        return True
    elif int(current) < limit:
        # Increment counter
        redis_client.incr(key)
        return True
    else:
        # Limit exceeded
        return False
```

### 3. API Gateway (Cloud)
**AWS API Gateway example**

```yaml
# Throttle settings
throttle:
  rateLimit: 10000    # requests per second
  burstLimit: 5000    # burst capacity

# Per-method settings
methods:
  GET /users:
    throttle:
      rateLimit: 100
      burstLimit: 50
  
  POST /orders:
    throttle:
      rateLimit: 50
      burstLimit: 25

# Usage plans for different tiers
usagePlans:
  free:
    throttle: {rateLimit: 10, burstLimit: 5}
    quota: {limit: 1000, period: DAY}
  
  premium:
    throttle: {rateLimit: 1000, burstLimit: 500}
    quota: {limit: 1000000, period: MONTH}
```

### 4. Nginx Rate Limiting

```nginx
# Define rate limit zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    
    location /api/ {
        # Apply rate limit
        limit_req zone=api_limit burst=20 nodelay;
        
        # Custom headers
        add_header X-Rate-Limit-Limit 10;
        add_header X-Rate-Limit-Remaining $limit_req_remaining;
        
        proxy_pass http://backend;
    }
}

# Different limits for different paths
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

location /login {
    limit_req zone=login_limit burst=5;
    proxy_pass http://backend;
}
```

## Response Headers (Standard)

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1644364800
X-RateLimit-Used: 13

// When exceeded:
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
  "error": "Rate limit exceeded",
  "limit": 100,
  "reset": 1644364800,
  "retry_after": 60
}
```

## Best Practices

✅ **Use distributed rate limiting (Redis)**
```python
# For multiple servers, use Redis not in-memory
```

✅ **Return clear error messages**
```json
{
  "error": "Rate limit exceeded",
  "limit": 100,
  "window": 60,
  "retry_after": 35
}
```

✅ **Implement by user/IP/API key**
```python
# Rate limit key options
key = f"ratelimit:{user_id}"        # Per user
key = f"ratelimit:{ip_address}"     # Per IP
key = f"ratelimit:{api_key}"        # Per API key
key = f"ratelimit:{user_id}:{endpoint}"  # Per user per endpoint
```

✅ **Different limits for different operations**
```
Read operations: 1000/minute
Write operations: 100/minute
Login attempts: 5/15 minutes
```

✅ **Whitelist trusted IPs/users**
```python
WHITELIST = ["10.0.0.1", "admin_user"]

if user_id in WHITELIST:
    # Skip rate limiting
    pass
```

✅ **Monitor and alert**
```python
# Track metrics
- Rate limit hit rate (% of requests blocked)
- Top rate-limited users
- False positives (legitimate users blocked)
```

✅ **Graceful degradation**
```python
try:
    if not check_rate_limit(user_id):
        return 429
except RedisConnectionError:
    # If Redis down, allow request (fail open)
    # Or use local rate limiting as fallback
    pass
```

## Common Pitfalls

❌ **Fixed window boundary issue**
```
Use sliding window instead of fixed window
```

❌ **Not considering distributed systems**
```
In-memory rate limiting doesn't work across servers
Use Redis or similar distributed store
```

❌ **Too strict limits**
```
Monitor false positives
Adjust limits based on actual usage patterns
```

❌ **No retry information**
```
Always include Retry-After header
```

❌ **Rate limiting after processing**
```
❌ Process request → Check rate limit → Return 429
✅ Check rate limit → Process request
```

## Interview Tips

**Q: "How would you implement rate limiting for an API?"**

**A:**
```
1. Use Redis with sliding window counter
2. Key: user_id or IP address
3. Window: 60 seconds, Limit: 100 requests
4. Return 429 with Retry-After header if exceeded
5. Different limits for different endpoints
6. Whitelist for trusted users
```

**Q: "Token bucket vs leaky bucket?"**

**A:**
```
Token Bucket:
- Allows bursts (up to capacity)
- Refills at constant rate
- Better for most APIs

Leaky Bucket:
- Smooths traffic (constant output)
- No bursts
- Better for network traffic shaping
```

**Q: "How to handle rate limiting in distributed system?"**

**A:**
```
1. Use Redis/Memcached (shared state)
2. Consistent approach across all servers
3. Handle Redis failures gracefully (fail open?)
4. Monitor for hot keys
5. Consider API Gateway (AWS, Kong) for centralized management
```

**Key Takeaway:** Rate limiting protects your system from abuse and overload. Use distributed solutions (Redis) for production, return clear headers, and monitor usage patterns!
