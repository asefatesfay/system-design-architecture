# Content Delivery Network (CDN)

## Definition

A **CDN** is a geographically distributed network of servers that caches and delivers content from locations closest to users, reducing latency and improving load times.

## How CDN Works

```
Without CDN:
User in Tokyo → US Server (200ms latency) ❌

With CDN:
User in Tokyo → Tokyo Edge Server (10ms) ✅
               ↓ (Cache miss)
               US Origin Server (one-time fetch)
               ↓
               Store in cache
```

## Real-World Examples

### Netflix
**CDN: Open Connect**
- 14,000+ servers in ISPs worldwide
- 90%+ of traffic served from cache
- Saves billions in bandwidth costs

```
User requests Stranger Things episode:
1. DNS routes to nearest Open Connect server
2. Server has episode cached → Instant streaming ✅
3. No need to fetch from central datacenter
```

### YouTube (Google CDN)
- Billions of video views daily
- Edge caching at ISP level
- Adaptive bitrate streaming

### Amazon CloudFront
**AWS CDN**

```javascript
// CloudFront distribution
{
  "Origins": ["s3://my-bucket"],
  "EdgeLocations": "300+ worldwide",
  "CacheBehaviors": {
    "/static/*": {"TTL": 86400},  // 24 hours
    "/api/*": {"TTL": 0}          // No cache
  }
}
```

### Cloudflare
- 300+ data centers
- 20%+ of web traffic
- DDoS protection
- Automatic optimization

**Services:**
- Static asset caching
- Dynamic content acceleration
- Video streaming
- Security (WAF, bot management)

### Akamai
**First CDN (1998)**
- 365,000+ servers
- Used by: Apple, Microsoft, Adobe
- Handles 15-30% of all web traffic

## CDN Content Types

### Static Content (High Cache)
```
Images, CSS, JavaScript, Fonts
TTL: Hours to days
Example: logo.png cached for 30 days
```

### Dynamic Content (Low/No Cache)
```
Personalized pages, API responses, user data
TTL: 0 seconds or very short
Example: User dashboard (cache 5 seconds)
```

### Video Streaming
```
Adaptive bitrate
Multiple quality levels
Chunked delivery (HLS, DASH)
```

## Cache Control Headers

```http
# Static assets (long cache)
Cache-Control: public, max-age=31536000, immutable

# Dynamic content (short cache)
Cache-Control: public, max-age=60

# No cache
Cache-Control: no-cache, no-store, must-revalidate

# Private (user-specific, no CDN)
Cache-Control: private, max-age=3600
```

## CDN Benefits

✅ **Reduced Latency**
```
US user → US edge: 20ms
EU user → EU edge: 15ms
Asia user → Asia edge: 10ms
```

✅ **Lower Bandwidth Costs**
```
CDN cache hit = No origin bandwidth used
Netflix: 90%+ cache hit rate = Massive savings
```

✅ **Higher Availability**
```
Origin down? CDN serves cached content ✅
DDoS protection at edge
```

✅ **Improved Security**
```
SSL/TLS termination
DDoS mitigation
Web Application Firewall (WAF)
Bot detection
```

## CDN Patterns

### 1. Push CDN
**You upload content to CDN**
```
Website: Upload all assets to CDN
CDN: Stores until you delete
Good for: Small sites, infrequent updates
```

### 2. Pull CDN
**CDN fetches content on demand**
```
User requests file → CDN checks cache
If miss → CDN fetches from origin → Caches
Good for: Large sites, frequent updates
```

### 3. Hybrid
```
Critical assets: Push
Long-tail content: Pull
```

## Cache Invalidation

```python
# Purge by URL
cloudfront.delete_cache("/images/logo.png")

# Purge by tag
cloudfront.delete_cache(tags=["product-images"])

# Purge all
cloudfront.delete_cache("/*")  # Expensive!

# Versioned URLs (better)
/images/logo.v2.png  # New version, new URL
```

## CDN Providers Comparison

| Provider | Edge Locations | Key Features |
|----------|----------------|--------------|
| Cloudflare | 300+ | Free tier, DDoS, WAF |
| AWS CloudFront | 400+ | AWS integration, Lambda@Edge |
| Akamai | 365,000+ servers | Enterprise, largest |
| Fastly | 70+ | Real-time purge, VCL |
| Azure CDN | 200+ | Azure integration |
| Google Cloud CDN | 100+ | GCP integration, Cloud Armor |

## Best Practices

✅ **Use versioned URLs**
```
/css/style.css?v=1.2.3
/js/app.abc123.js  # Hash in filename
```

✅ **Set appropriate TTLs**
```
Images, CSS, JS: 1 year
HTML: 10 minutes (revalidate)
API: No cache or <60s
```

✅ **Enable compression**
```
gzip, brotli compression
30-80% size reduction
```

✅ **Use HTTP/2+**
```
Multiplexing, header compression
Faster than HTTP/1.1
```

✅ **Monitor cache hit ratio**
```
Target: >80% cache hit rate
Low hit rate = Investigate caching config
```

✅ **Leverage CDN security features**
```
WAF, DDoS protection, bot management
SSL/TLS, DNSSEC
```

## Interview Tips

**Q: "When would you use a CDN?"**

**A:** For static assets (images, CSS, JS), video streaming, and geographical distribution. Examples: Netflix uses CDN for video, e-commerce uses CDN for product images. Benefits: Reduced latency, lower bandwidth costs, higher availability.

**Q: "How does CDN caching work?"**

**A:** User requests content → CDN checks edge cache → If hit, return cached content (fast). If miss, fetch from origin, cache for TTL duration, then return to user. Subsequent requests served from cache.

**Q: "How to invalidate CDN cache?"**

**A:** 
1. Purge/invalidate specific URLs (takes time)
2. Use versioned URLs (best practice: /app.v2.js)
3. Set short TTL for frequently changing content
4. Purge by tags/patterns

**Key Takeaway:** CDNs cache content at edge locations worldwide, dramatically reducing latency and bandwidth costs. Essential for global applications!
