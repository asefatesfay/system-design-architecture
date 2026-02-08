# Proxy Server

## Definition

A **Proxy Server** acts as an intermediary between clients and servers, forwarding requests and responses while potentially adding functionality like caching, security, load balancing, or anonymity.

## Types

### 1. Forward Proxy
**Client → Proxy → Internet**

```
Employee → Company Proxy → Internet
          (Filters, logs, caches)
```

**Examples:**
- Corporate firewalls
- VPNs
- Squid proxy

**Use cases:**
- Access control
- Content filtering
- Anonymity (hide client IP)
- Caching

### 2. Reverse Proxy
**Client → Proxy → Backend Servers**

```
User → NGINX → [Server1, Server2, Server3]
       (Load balance, cache, SSL)
```

**Examples:**
- NGINX, HAProxy, Apache
- AWS CloudFront, Cloudflare

**Use cases:**
- Load balancing
- SSL termination
- Caching
- Security (hide backend)
- Compression

## Real-World Examples

### NGINX (Reverse Proxy)
**Used by:** Netflix, Airbnb, Pinterest

```nginx
upstream backend {
    server backend1.example.com;
    server backend2.example.com;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Caching
        proxy_cache my_cache;
        proxy_cache_valid 200 1h;
    }
}
```

### Cloudflare (CDN + Proxy)
- 300+ data centers worldwide
- DDoS protection
- SSL/TLS
- Caching
- Bot management

### AWS API Gateway
- Acts as reverse proxy for Lambda, EC2
- Rate limiting
- Authentication
- Request/response transformation

### Squid (Forward Proxy)
- Web caching proxy
- Access control
- Bandwidth control

## Benefits

✅ **Security:** Hide backend topology
✅ **Performance:** Caching, compression
✅ **Load balancing:** Distribute requests
✅ **SSL termination:** Offload encryption
✅ **Access control:** Authentication, authorization
✅ **Monitoring:** Centralized logging

**Key Takeaway:** Proxies add functionality between clients and servers, enabling caching, security, load balancing, and more!
