# Load Balancing

## Definition

**Load Balancing** is the process of distributing network traffic or computational workload across multiple servers to ensure no single server becomes overwhelmed, improving responsiveness, availability, and reliability.

## Key Concepts

### Without Load Balancer
```
All requests → Single Server
   ↓
   🔥 Overloaded!
   ❌ 503 errors
   ❌ Slow responses
   ❌ Single point of failure
```

### With Load Balancer
```
Requests → Load Balancer → [Server1, Server2, Server3]
              ↓              ↓       ↓       ↓
         Distributes    50 req/s 50 req/s 50 req/s
         150 req/s      ✅ Fast  ✅ Fast  ✅ Fast
                        ✅ Fault tolerant
```

## Load Balancing Algorithms

### 1. Round Robin
**Distribute requests sequentially**

```python
servers = ["server1", "server2", "server3"]
current = 0

def get_next_server():
    global current
    server = servers[current]
    current = (current + 1) % len(servers)
    return server

# Requests distributed:
# R1 → server1
# R2 → server2
# R3 → server3
# R4 → server1 (cycle repeats)
```

**Pros:**
- ✅ Simple, fair distribution
- ✅ Works well with homogeneous servers

**Cons:**
- ❌ Doesn't consider server load
- ❌ Doesn't account for different server capacities

**Used by:** NGINX (default), Apache

### 2. Weighted Round Robin
**Assign more requests to powerful servers**

```python
servers = [
    ("server1", 1),  # Small server
    ("server2", 2),  # Medium server
    ("server3", 3),  # Large server
]

# Distribution over 6 requests:
# server1: 1/6 = 16.7%
# server2: 2/6 = 33.3%
# server3: 3/6 = 50%
```

**Use case:** Mixed server capacities (old + new hardware)

### 3. Least Connections
**Send to server with fewest active connections**

```python
def get_server():
    # Choose server with minimum connections
    return min(servers, key=lambda s: s.active_connections)

# Dynamic load balancing based on current load
```

**Pros:**
- ✅ Better for long-lived connections
- ✅ Adapts to actual load

**Cons:**
- ❌ More complex (track connections)
- ❌ Slight overhead

**Best for:** WebSocket connections, database connections

### 4. Weighted Least Connections
**Combines capacity and current load**

```python
def get_server():
    # Score = connections / weight (lower is better)
    return min(servers, key=lambda s: s.connections / s.weight)
```

### 5. IP Hash / Sticky Sessions
**Same client → same server (session affinity)**

```python
import hashlib

def get_server(client_ip):
    hash_val = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
    return servers[hash_val % len(servers)]

# 192.168.1.1 → always server2
# 192.168.1.2 → always server1
```

**Pros:**
- ✅ Maintains session state
- ✅ No shared session store needed

**Cons:**
- ❌ Uneven distribution
- ❌ Server failure = lost sessions
- ❌ Harder to scale

**Used by:** Applications with in-memory sessions

### 6. Least Response Time
**Send to server with fastest response**

```python
def get_server():
    # Choose server with lowest latency + connections
    return min(servers, key=lambda s: s.avg_response_time * s.connections)
```

**Best for:** Geographically distributed servers

### 7. Random
**Randomly select server**

```python
import random

def get_server():
    return random.choice(servers)
```

**Pros:**
- ✅ Simple
- ✅ Stateless

**Cons:**
- ❌ Can be uneven in short term

### 8. Least Bandwidth
**Send to server using least bandwidth**

```python
def get_server():
    return min(servers, key=lambda s: s.current_bandwidth)
```

**Best for:** Streaming, large file downloads

## Load Balancer Types

### 1. Layer 4 (Transport Layer) - L4
**Operates at TCP/UDP level**

```
Client → L4 Load Balancer → Server
         ↓
    Sees only:
    - Source IP
    - Destination IP
    - Port numbers
    
Cannot see:
    ❌ HTTP headers
    ❌ Cookies
    ❌ URL paths
```

**Pros:**
- ✅ Fast (less processing)
- ✅ Protocol agnostic (HTTP, TCP, UDP, etc.)
- ✅ Lower latency

**Cons:**
- ❌ No content-based routing
- ❌ No SSL termination
- ❌ Less intelligent

**Examples:** AWS NLB (Network Load Balancer), HAProxy (TCP mode)

### 2. Layer 7 (Application Layer) - L7
**Operates at HTTP level**

```
Client → L7 Load Balancer → Server
         ↓
    Sees:
    - HTTP headers
    - Cookies
    - URL path
    - SSL/TLS
    - Request body
```

**Capabilities:**
```nginx
# Route by path
location /api/    → API servers
location /static/ → CDN/Static servers

# Route by header
User-Agent: mobile → Mobile servers
User-Agent: desktop → Desktop servers

# Route by cookie
Cookie: session_id → Sticky session

# SSL termination
HTTPS → Load Balancer → HTTP → Servers
```

**Pros:**
- ✅ Content-based routing
- ✅ SSL termination (offload from servers)
- ✅ Request modification (headers, compression)
- ✅ Caching possible
- ✅ Better observability

**Cons:**
- ❌ Higher latency (more processing)
- ❌ More CPU intensive
- ❌ Only for HTTP/HTTPS

**Examples:** AWS ALB (Application Load Balancer), NGINX, HAProxy (HTTP mode)

## Real-World Examples

### NGINX (Most Popular)
**Used by:** Netflix, Airbnb, Pinterest, NASA

```nginx
upstream backend {
    # Load balancing method
    least_conn;
    
    # Server pool
    server backend1.example.com weight=3;
    server backend2.example.com weight=2;
    server backend3.example.com weight=1;
    
    # Health checks
    server backend4.example.com down;  # Maintenance
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        
        # Headers for backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
    
    # Path-based routing
    location /api/ {
        proxy_pass http://api_backend;
    }
    
    location /static/ {
        proxy_pass http://cdn_backend;
    }
}
```

### AWS Elastic Load Balancer (ELB)

#### Application Load Balancer (ALB) - L7
**Used by:** Thousands of AWS customers

```python
# Content-based routing
Rules:
1. Path /api/* → API Target Group
2. Path /mobile/* → Mobile Target Group
3. Header X-Custom: value → Custom Target Group
4. Query string ?version=2 → V2 Target Group
5. Default → Main Target Group

# Target groups:
- EC2 instances
- Lambda functions
- IP addresses
- Containers (ECS)
```

**Features:**
- HTTP/2, gRPC support
- WebSocket support
- SSL/TLS termination
- Sticky sessions (cookie-based)
- Health checks
- Auto-scaling integration

#### Network Load Balancer (NLB) - L4
**Ultra-high performance**

```
Performance:
- Millions of requests/second
- Ultra-low latency (~100 microseconds)
- Static IP per AZ
- Preserves source IP

Use cases:
- Gaming servers
- IoT devices
- VoIP
- Financial trading platforms
```

### Google Cloud Load Balancing
**Global load balancing**

```
User in Tokyo   → Tokyo  backend (30ms)
User in NYC     → NYC    backend (20ms)
User in London  → London backend (15ms)

Features:
- Anycast IP (same IP worldwide)
- Automatic failover
- DDoS protection
- Cross-region load balancing
```

**Example: YouTube**
```
youtube.com (single IP)
    ↓
Global Load Balancer
    ↓
[US DC, EU DC, Asia DC, ...]
    ↓
Nearest data center serves request ✅
```

### HAProxy
**High-performance TCP/HTTP load balancer**

**Used by:** Reddit, GitHub, Stack Overflow, Imgur

```haproxy
# HAProxy Configuration
frontend http_front
    bind *:80
    
    # ACL (Access Control Lists)
    acl url_api path_beg /api
    acl url_static path_beg /static
    acl is_mobile hdr_sub(User-Agent) -i mobile
    
    # Routing rules
    use_backend api_servers if url_api
    use_backend static_servers if url_static
    use_backend mobile_servers if is_mobile
    default_backend web_servers

backend web_servers
    balance leastconn
    option httpchk GET /health
    
    server web1 192.168.1.10:80 check
    server web2 192.168.1.11:80 check
    server web3 192.168.1.12:80 check backup  # Only used if others down

backend api_servers
    balance roundrobin
    server api1 192.168.2.10:8080 check
    server api2 192.168.2.11:8080 check
```

### Netflix
**Multi-tier load balancing**

```
User request
    ↓
Route 53 (DNS) → Closest region
    ↓
ELB (Elastic Load Balancer) → Availability Zone
    ↓
Zuul (API Gateway) → Service-level routing
    ↓
Ribbon (Client-side LB) → Service instances
    ↓
Microservice (e.g., Video Service)
```

**Technologies:**
- AWS Route 53 (DNS-based geo-routing)
- AWS ELB (Regional load balancing)
- Zuul (API Gateway + intelligent routing)
- Ribbon (Client-side discovery + load balancing)

### Facebook
**Social Load Balancer (SLB)**

```
Billions of requests/hour

Edge servers (global) → Regional data centers → Backend services
    ↓                        ↓                     ↓
DNS resolution       Proxygen (HTTP proxy)    Service mesh
Anycast             SSL termination           Microservices
                    Connection pooling
```

## Health Checks

### Active Health Checks
**Load balancer probes servers**

```python
# HTTP health check
GET /health HTTP/1.1
Response: 200 OK → Server healthy ✅
Response: 500 Error → Server unhealthy ❌
No response → Server down ❌

# Configuration
check_interval = 5s  # Check every 5 seconds
unhealthy_threshold = 3  # 3 failures → mark unhealthy
healthy_threshold = 2  # 2 successes → mark healthy
timeout = 3s
```

### Passive Health Checks
**Monitor actual traffic**

```python
# If 3 consecutive requests fail, mark server as unhealthy
request1 → server1 → 500 Error (1/3)
request2 → server1 → 502 Error (2/3)
request3 → server1 → 503 Error (3/3) → UNHEALTHY ❌

# Stop sending traffic to server1
# Retry after backoff period
```

### Example Health Check Endpoint
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    # Check critical dependencies
    if not database.is_connected():
        return jsonify({"status": "unhealthy"}), 503
    
    if not cache.is_reachable():
        return jsonify({"status": "degraded"}), 200
    
    return jsonify({"status": "healthy"}), 200
```

## High Availability Patterns

### 1. Active-Active
**All load balancers handle traffic**

```
    ┌────────┐           ┌────────┐
    │  LB 1  │ (active)  │  LB 2  │ (active)
    └────┬───┘           └───┬────┘
         │                   │
         └─────┬─────┬───────┘
               ↓     ↓     ↓
          [Server Pool]
```

**Pros:**
- ✅ Full capacity utilized
- ✅ Better resource usage

### 2. Active-Passive
**One load balancer, one hot standby**

```
    ┌────────┐           ┌────────┐
    │  LB 1  │ (active)  │  LB 2  │ (standby)
    └────┬───┘           └────────┘
         │                    ↑
         │              Heartbeat monitoring
         ↓
    [Server Pool]

If LB1 fails → LB2 takes over (VIP failover)
```

**Technologies:**
- Keepalived (VRRP protocol)
- Pacemaker + Corosync

### 3. DNS-Based
**Multiple load balancers via DNS**

```
example.com → [IP1, IP2, IP3]

DNS round-robin:
- Request 1 → IP1
- Request 2 → IP2
- Request 3 → IP3
```

**Pros:**
- ✅ Simple
- ✅ Geographic distribution

**Cons:**
- ❌ DNS caching issues
- ❌ No health checks
- ❌ Slow failover

## Common Pitfalls

### 1. Single Point of Failure
```
❌ Load Balancer as SPOF
User → Single LB → Servers

✅ Redundant load balancers
User → [LB1, LB2] → Servers
```

### 2. Uneven Distribution
```python
# Problem: IP hash with few clients
5 clients → 3 servers
Client1, Client2 → Server1 (80% traffic) 🔥
Client3 → Server2 (10% traffic)
Client4, Client5 → Server3 (10% traffic)

# Solution: Use better algorithm (least connections)
```

### 3. Session Loss
```python
# Problem: Stateful sessions without sticky sessions
User → LB → Server1 (creates session)
User → LB → Server2 (no session!) ❌

# Solutions:
1. Sticky sessions (IP hash/cookie)
2. External session store (Redis)
3. JWT tokens (stateless)
```

### 4. Health Check Overhead
```python
# Bad: Too frequent
check_interval = 1s  # 1000 health checks/second for 1000 servers! ❌

# Good: Reasonable interval
check_interval = 10s  # 100 checks/second ✅
```

## Best Practices

✅ **Use health checks**
```nginx
upstream backend {
    server server1:80 max_fails=3 fail_timeout=30s;
    server server2:80 max_fails=3 fail_timeout=30s;
}
```

✅ **Implement graceful degradation**
```
If 50% servers down:
- Still handle ~50% capacity
- Return 503 for excess traffic (better than timeouts)
```

✅ **Monitor load balancer metrics**
```
- Active connections
- Requests/second
- Error rates (4xx, 5xx)
- Backend response times
- Unhealthy backends
```

✅ **Set appropriate timeouts**
```nginx
proxy_connect_timeout 5s;    # Connect to backend
proxy_send_timeout 60s;      # Send request
proxy_read_timeout 60s;      # Read response
```

✅ **Use connection pooling**
```
Load Balancer ←→ Backend: Keep connections alive
Reduces connection overhead
```

## Interview Tips

**Q: "How would you design load balancing for a video streaming service?"**

**A:**
```
1. DNS-based: Route to nearest region (AWS Route 53)
2. L4 Load Balancer: Distribute to video servers (low latency)
3. Sticky sessions: Keep user on same server (buffering)
4. Health checks: Don't send to overloaded servers
5. CDN: Cache video chunks (reduce backend load)
```

**Q: "L4 vs L7 load balancer?"**

**A:**
```
L4 (TCP):
- Faster, lower latency
- Can't inspect HTTP
- For high throughput (gaming, IoT)

L7 (HTTP):
- Content-based routing (/api, /static)
- SSL termination
- For web applications (APIs, websites)
```

**Q: "How to handle session state with load balancing?"**

**A:**
```
1. Sticky sessions (cookie/IP hash) - Simple but limited
2. External session store (Redis) - Scalable, requires infra
3. JWT tokens (stateless) - No session storage needed
4. Replicate sessions across servers - Complex, high overhead
```

**Key Takeaway:** Load balancing is essential for scalability and availability. Choose algorithm based on workload, use health checks, and make load balancers redundant!
