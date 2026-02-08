# Domain Name System (DNS)

## Definition

**DNS** translates human-readable domain names (like amazon.com) into IP addresses (like 52.85.151.9) that computers use to communicate.

## How DNS Works

```
User types: www.amazon.com
    ↓
1. Browser cache → Not found
2. OS cache → Not found  
3. Router cache → Not found
4. ISP DNS resolver → Queries root servers
5. Root server → Points to .com TLD server
6. TLD server → Points to amazon.com nameserver
7. Nameserver → Returns IP: 52.85.151.9 ✅
8. Browser connects to 52.85.151.9
```

## DNS Record Types

```
A Record:     domain.com → 192.0.2.1 (IPv4)
AAAA Record:  domain.com → 2001:db8::1 (IPv6)
CNAME Record: www.domain.com → domain.com (Alias)
MX Record:    domain.com → mail.domain.com (Email)
TXT Record:   domain.com → "v=spf1 ..." (Text data)
NS Record:    domain.com → ns1.nameserver.com (Nameserver)
SOA Record:   domain.com → authority information
```

## Real-World Examples

### AWS Route 53
**Highly available DNS service**

```python
# Geographic routing
User in US → us-east-1
User in EU → eu-west-1
User in Asia → ap-southeast-1

# Weighted routing
80% traffic → new version
20% traffic → old version

# Latency-based routing
Route to nearest region

# Failover routing
Primary fails → Secondary
```

### Cloudflare DNS (1.1.1.1)
- Fastest DNS resolver
- Privacy-focused
- DNSSEC support
- 200+ data centers

### Google Public DNS (8.8.8.8)
- Free, global DNS service
- Fast, secure
- DNSSEC validation

### CDN + DNS

**Example: Netflix**
```
1. User requests netflix.com
2. DNS returns nearest CDN edge server
3. Video streams from nearby location (low latency)
```

## DNS Caching

```
Browser cache: 1-30 minutes
OS cache: Minutes to hours
ISP cache: Hours (based on TTL)
```

**TTL (Time To Live):**
```
Short TTL (60s): Frequent changes, failover
Long TTL (24h): Static content, reduce DNS load
```

## DNS Load Balancing

**Round Robin DNS:**
```
domain.com → [IP1, IP2, IP3]

Request 1 → IP1
Request 2 → IP2
Request 3 → IP3
Request 4 → IP1 (cycle repeats)
```

## DNS Security

**DDoS Attacks:**
- DNS amplification attacks
- Query floods
- Mitigation: Anycast, rate limiting

**DNS Spoofing/Cache Poisoning:**
- Return fake IPs
- DNSSEC prevents this

## Best Practices

✅ Use multiple nameservers (redundancy)
✅ Set appropriate TTLs
✅ Enable DNSSEC
✅ Use anycast for DDoS protection
✅ Monitor DNS query patterns
✅ Use DNS-based load balancing for geographic distribution

**Key Takeaway:** DNS is the internet's phonebook, translating domains to IPs. Critical for routing, load balancing, and failover!
