# API Gateway

## Definition

**API Gateway** is a server that acts as a single entry point for client requests to multiple backend microservices. It routes requests, aggregates responses, and handles cross-cutting concerns like authentication, rate limiting, and logging.

## Architecture

```
Without API Gateway (Chaos):
┌────────┐
│ Mobile │───→ User Service (auth?)
│  App   │───→ Product Service (rate limit?)
└────────┘───→ Order Service (logging?)
             → Payment Service
             
Each service handles auth, rate limiting, etc. ❌
```

```
With API Gateway (Clean):
┌────────┐        ┌──────────────┐
│ Mobile │───────→│ API Gateway  │
│  App   │        │ ─────────────│
└────────┘        │ Auth         │
                  │ Rate Limit   │
                  │ Routing      │
                  └──────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    User Service   Product Service  Order Service
    
Single entry point ✅
```

## Responsibilities

### 1. Request Routing
```
GET /api/users/123 → Route to User Service
GET /api/products → Route to Product Service
POST /api/orders → Route to Order Service
```

### 2. Authentication/Authorization
```javascript
// API Gateway checks token before forwarding
if (!verifyToken(request.headers.authorization)) {
  return 401 Unauthorized;
}
// Forward to service
```

### 3. Rate Limiting
```javascript
// Limit: 100 requests per minute per user
if (userRequestCount > 100) {
  return 429 Too Many Requests;
}
```

### 4. Response Aggregation
```javascript
// Client needs user + orders + products
// Without gateway: 3 API calls from client ❌
// With gateway: 1 call to gateway

GET /api/user-dashboard/123

Gateway:
1. Call User Service
2. Call Order Service  
3. Call Product Service
4. Aggregate responses
5. Return single response ✅
```

### 5. Load Balancing
```
API Gateway → [User Service Instance 1, User Service Instance 2, User Service Instance 3]
Round-robin / least connections
```

### 6. Caching
```javascript
// Cache frequent requests
if (cache.has(request.url)) {
  return cache.get(request.url);
}
response = forwardToService(request);
cache.set(request.url, response, ttl=60);
```

### 7. Protocol Translation
```
Client (HTTP/REST) → Gateway → Backend (gRPC)
Gateway translates between protocols
```

## Real-World Examples

### Netflix (Zuul)
**Custom-built API Gateway**

```
Client (TV/Mobile/Web) → Zuul Gateway
- Authentication with OAuth
- Dynamic routing to 700+ microservices
- Stress testing (chaos engineering)
- Real-time insights

Handles millions of requests per second
```

### Amazon (AWS API Gateway)
```
Mobile App → API Gateway → Lambda Functions / EC2
- Request/response transformation
- API key management
- Throttling (burst limits)
- Regional endpoints
- WebSocket support

Used by: Prime Video, AWS Console, third-party APIs
```

### Uber
```
Rider App → API Gateway → [TripService, PaymentService, MappingService]
- Single endpoint for mobile apps
- Protocol translation (HTTP → internal RPC)
- Authentication (JWT tokens)
- Rate limiting per user tier

Benefits:
- Clients don't know about microservices
- Easy to change backend without updating apps
```

### Twitter (GraphQL Gateway)
```
Twitter App → GraphQL Gateway → REST microservices
- Clients request exactly what they need
- Gateway fetches from multiple services
- Response aggregation
```

## Popular API Gateways

### 1. Kong
```yaml
# Open-source, plugin-based
services:
  - name: user-service
    url: http://user-service:8080
    routes:
      - paths: [/users]
    plugins:
      - name: rate-limiting
        config:
          minute: 100
      - name: jwt
```

### 2. NGINX
```nginx
# High-performance reverse proxy
location /api/users {
    proxy_pass http://user-service:8080;
    proxy_set_header Authorization $http_authorization;
}

location /api/products {
    proxy_pass http://product-service:8080;
}
```

### 3. AWS API Gateway
```yaml
# Managed service
Resources:
  UsersApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: MyAPI
      
  UsersResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref UsersApi
      PathPart: users
```

### 4. Spring Cloud Gateway
```java
@Bean
public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("users", r -> r.path("/api/users/**")
            .filters(f -> f.addRequestHeader("X-Request-Source", "Gateway"))
            .uri("http://user-service:8080"))
        .route("products", r -> r.path("/api/products/**")
            .uri("http://product-service:8080"))
        .build();
}
```

### 5. Express Gateway (Node.js)
```yaml
apiEndpoints:
  users:
    host: api.example.com
    paths: '/users/*'

serviceEndpoints:
  userService:
    url: 'http://user-service:8080'

pipelines:
  user-pipeline:
    apiEndpoints:
      - users
    policies:
      - jwt
      - rate-limit:
          - action:
              max: 100
              windowMs: 60000
      - proxy:
          - action:
              serviceEndpoint: userService
```

## Benefits

✅ **Single entry point**
```
Clients call one endpoint, not 50 microservices
```

✅ **Simplified clients**
```
Mobile app doesn't handle auth, retries, etc.
Gateway handles it ✅
```

✅ **Centralized cross-cutting concerns**
```
Auth, rate limiting, logging in one place
Not duplicated across services
```

✅ **Backend flexibility**
```
Change microservices without updating clients
Add/remove services transparently
```

✅ **Protocol translation**
```
HTTP → gRPC
REST → GraphQL
```

## Challenges

❌ **Single point of failure**
```
Gateway down = entire system down
Solution: Load balance multiple gateway instances
```

❌ **Performance bottleneck**
```
All requests through gateway
Solution: Horizontal scaling, caching
```

❌ **Added latency**
```
Extra hop: Client → Gateway → Service
Solution: Keep gateway lightweight
```

❌ **Complexity**
```
Another service to maintain
Solution: Use managed service (AWS API Gateway)
```

## Backend for Frontend (BFF) Pattern

**Different gateways for different clients**

```
Mobile App → Mobile BFF Gateway → Microservices
Web App → Web BFF Gateway → Microservices

Mobile BFF:
- Returns minimal data (bandwidth-conscious)
- Optimized for slow networks

Web BFF:
- Returns richer data
- Different caching strategy
```

**Used by:** Netflix, SoundCloud
```
Netflix Android → Android BFF → Services
Netflix iOS → iOS BFF → Services
(Each optimized for platform)
```

## Implementation Example

```javascript
const express = require('express');
const axios = require('axios');

const app = express();

// Middleware: Authentication
app.use(async (req, res, next) => {
  const token = req.headers.authorization;
  if (!token || !await verifyToken(token)) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});

// Middleware: Rate limiting
const rateLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 100  // 100 requests per minute
});
app.use(rateLimiter);

// Route: Users
app.get('/api/users/:id', async (req, res) => {
  try {
    const response = await axios.get(`http://user-service:8080/users/${req.params.id}`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'User service unavailable' });
  }
});

// Route: Aggregation
app.get('/api/dashboard/:userId', async (req, res) => {
  try {
    const [user, orders, recommendations] = await Promise.all([
      axios.get(`http://user-service:8080/users/${req.params.userId}`),
      axios.get(`http://order-service:8080/orders?userId=${req.params.userId}`),
      axios.get(`http://recommendation-service:8080/recommendations/${req.params.userId}`)
    ]);
    
    res.json({
      user: user.data,
      orders: orders.data,
      recommendations: recommendations.data
    });
  } catch (error) {
    res.status(500).json({ error: 'Dashboard unavailable' });
  }
});

app.listen(3000);
```

## Best Practices

✅ **Keep it lightweight**
```
Don't add business logic to gateway
Gateway = routing + cross-cutting concerns only
```

✅ **High availability**
```
Multiple gateway instances
Load balancer in front
Health checks
```

✅ **Caching**
```
Cache frequent requests (product catalog)
Reduce load on backend services
```

✅ **Circuit breaker**
```
If service down, fail fast
Don't wait for timeout
```

✅ **Observability**
```
Log all requests
Monitor latency, error rates
Distributed tracing (OpenTelemetry)
```

## When to Use API Gateway

✅ **Microservices architecture** (many backend services)
✅ **Multiple client types** (mobile, web, IoT)
✅ **Cross-cutting concerns** (auth, rate limiting need centralization)
✅ **Response aggregation** (combine multiple API calls)

## When NOT Needed

❌ **Monolith** (single backend service)
❌ **Internal services only** (no external clients)
❌ **Simple architecture** (2-3 services)

## Interview Tips

**Q: "What is API Gateway?"**

**A:** Single entry point for clients to access multiple microservices. Handles routing, authentication, rate limiting, response aggregation. Instead of client calling 10 services directly, calls gateway once. Used by Netflix (Zuul), AWS, Uber. Benefits: simplified clients, centralized cross-cutting concerns.

**Q: "API Gateway challenges?"**

**A:** 1) Single point of failure (solution: multiple instances), 2) Performance bottleneck (solution: caching, horizontal scaling), 3) Added latency (solution: lightweight gateway), 4) Complexity (solution: managed service like AWS API Gateway).

**Q: "Design API for mobile app accessing microservices"**

**A:** Use API Gateway as single endpoint. Gateway handles: authentication (JWT), rate limiting (per user), routing (mobile app → user/order/product services), response aggregation (dashboard = 1 call instead of 3). Consider BFF pattern (separate gateway for mobile vs web for different optimization).

**Key Takeaway:** API Gateway simplifies microservices access by providing single entry point with centralized concerns!
