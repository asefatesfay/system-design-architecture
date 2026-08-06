# System Design Jargon — Comprehensive Glossary with Real-World Examples

> Every term you'll hear in system design interviews, explained plainly with
> a concrete example from a system you already know. Organized by category
> so related terms are together. Read the whole thing once, then use it as
> a reference.

---

## Category 1 — Reliability and Service Level Terms

These are the terms that come up most in staff-level conversations about
production systems. Get these exactly right — interviewers probe on the
differences between them.

---

### SLI — Service Level Indicator

**What it is:** A metric that measures one specific aspect of a service's
behavior. It's a number you can measure.

**Plain English:** "The thing we're actually measuring."

**Real example — Nordstrom Content API:**
```
SLI: The percentage of content API requests that return a response
     in under 100ms, measured over a rolling 5-minute window.

This is measurable. You can query your metrics system right now and
get this number.
```

**More examples:**
```
Stripe:     Percentage of charge API requests that succeed (non-5xx)
YouTube:    Percentage of video segments delivered within 2s of request
WhatsApp:   Percentage of messages delivered within 5s of sending
Uber:       Percentage of driver location updates processed within 1s
```

---

### SLO — Service Level Objective

**What it is:** A target for an SLI. It's the number you're trying to hit.

**Plain English:** "The goal for the thing we're measuring."

**Real example — Nordstrom Content API:**
```
SLO: 99.5% of content API requests must return in under 100ms,
     measured over a rolling 30-day window.

SLI: the measured percentage
SLO: 99.5% is the target
```

**The relationship:**
```
SLI (what you measure) + target = SLO (what you're trying to achieve)

"99.9% of requests succeed" is an SLO.
"the current success rate" is the SLI.
```

**More examples:**
```
Netflix:    99.99% of streaming sessions start within 2 seconds
            (SLI: session start time; target: 99.99%; together = SLO)

Google Search: 99.9% of searches return results in under 300ms

Stripe:     99.99% of charge API requests succeed
            (this is both their SLO and their contractual SLA)
```

**Why SLOs matter in interviews:**
When you say "p99 latency under 200ms," you're describing an SLO.
Interviewers expect staff engineers to define SLOs before designing
architecture — the SLO tells you what you're optimizing for.

---

### SLA — Service Level Agreement

**What it is:** An SLO with a contractual consequence for missing it.
Usually involves money (credits, refunds) or legal penalties.

**Plain English:** "A promise we made to a customer, in writing, with
consequences if we break it."

**Real example:**
```
AWS S3 SLA: 99.9% monthly availability.
If S3 drops below 99.9%, AWS credits your bill:
  99.0–99.9% availability → 10% service credit
  Below 99.0%             → 25% service credit
  Below 95.0%             → 100% service credit

The 99.9% target is the SLO.
The credit structure makes it an SLA.
```

**The hierarchy:**
```
SLI → what you measure
SLO → what you're trying to achieve (internal goal)
SLA → what you've promised (external commitment with consequences)

SLOs are typically stricter than SLAs:
  SLA (promised to customer): 99.9% availability
  Internal SLO (what engineering targets): 99.95% availability
  → Buffer between internal goal and external promise
```

**Nordstrom context:**
The Content API probably has an internal SLO (p99 < 100ms) but not a formal
SLA — it's an internal service, not sold to external customers. Stripe's
charge API has both an internal SLO and an SLA with merchants.

---

### Error Budget

**What it is:** The amount of downtime or errors you're allowed before
you've violated your SLO. Calculated from the SLO.

**Plain English:** "How much can go wrong before we've broken our promise."

**Formula:**
```
Error budget = 1 - SLO

SLO = 99.9% over 30 days
Error budget = 0.1% of 30 days
             = 0.001 × 30 × 24 × 60
             = 43.2 minutes per month
```

**How it's used:**
```
Each incident, deployment failure, or planned maintenance consumes
from the error budget.

If you've used 30 of your 43 minutes this month:
  → Slow down deployments (risky changes burn the budget)
  → Focus on reliability improvements

If you've used 0 minutes (well under budget):
  → Ship faster, take more risks
  → The budget gives you permission to move fast
```

**Real example — Netflix:**
```
SLO: 99.99% of streaming sessions start within 2 seconds
Error budget: 0.01% of 30 days = 4.32 minutes per month

Netflix's Chaos Monkey intentionally burns error budget by
terminating production instances. If the budget is healthy,
Chaos Monkey runs. If the budget is nearly exhausted,
Chaos Monkey is paused.
```

---

### Availability

**What it is:** The percentage of time a system is operational and
serving requests correctly.

**Plain English:** "What fraction of the time does it work?"

**The nines:**
```
99%     → 3.65 days downtime/year   → unacceptable for most services
99.9%   → 8.77 hours downtime/year  → acceptable for internal tools
99.99%  → 52.6 minutes downtime/year → good for consumer products
99.999% → 5.26 minutes downtime/year → required for payment systems
```

**Real examples:**
```
Nordstrom.com during normal period: target 99.99%
                during Anniversary Sale: target 99.999% (stricter during peak)
Stripe charge API: 99.9999% (financial transactions)
Gmail: 99.9% (email can tolerate brief outages)
AWS EC2: 99.99% per region
```

**Common mistake:** Stating availability as a goal without saying what
"available" means. "Available" should be defined by an SLI:
```
Vague:   "The system will be 99.9% available"
Better:  "99.9% of requests will return a non-5xx response
          within 500ms, measured monthly"
```

---

---

## Category 2 — Performance Terms

---

### Latency

**What it is:** The time it takes for one operation to complete, from start to finish.

**Plain English:** "How long does one thing take?"

**Real examples:**
```
Nordstrom Content API:   8ms to serve a cached content response
Google Search:           ~200ms from keystroke to results page
WhatsApp message:        <100ms from send to delivery (online recipient)
Stripe charge API:       ~500ms end-to-end (card network included)
Redis GET:               ~0.1ms (in-memory, same datacenter)
Postgres query (index):  ~1ms
S3 object fetch:         ~20-50ms
Cross-region network:    ~100ms US to Europe
```

**p50, p95, p99, p999 — percentile latency:**
```
If you measure 1,000 requests and sort them by response time:

p50  = the 500th slowest = median (half are faster, half are slower)
p95  = the 950th slowest = 95% of requests are faster than this
p99  = the 990th slowest = 99% of requests are faster than this
p999 = the 999th slowest = 0.1% of requests are slower than this

Real example — Nordstrom product page:
  p50:  120ms  (typical user experience)
  p95:  380ms  (slower users, complex pages)
  p99:  820ms  (worst 1% — large wishlists, slow connections)
  p999: 3,200ms (0.1% — edge cases, server restarts, cold caches)
```

**Why p99 matters more than average:**
```
Average latency: 150ms (looks fine)
p99 latency:    2,000ms (1 in 100 users waits 2 seconds)

At 1M requests/day: 10,000 users per day have a terrible experience.
Average hides the long tail. Always optimize for p99, not average.
```

---

### Throughput

**What it is:** The number of operations a system can handle per unit of time.

**Plain English:** "How much can it process at once?"

**Real examples:**
```
Kafka broker:          ~1M messages/second
Redis:                 ~100K operations/second (single instance)
Postgres:              ~10K writes/second (single primary)
Nordstrom Content API: ~50K requests/second at peak (Anniversary Sale)
YouTube CDN edge node: ~100 Gbps bandwidth
WhatsApp message bus:  ~1M messages/second
```

**Latency vs. Throughput — the key distinction:**
```
Latency:    Time for ONE request    → "this took 8ms"
Throughput: Volume per unit time    → "we handle 50,000 requests/second"

They're related but not the same:
  A system can have low latency AND low throughput
    (fast but can only handle 1 request at a time)
  A system can have high throughput AND high latency
    (handles 1M requests/second but each takes 500ms)

Example — batch file processing:
  Latency:    5 minutes to process one file (slow)
  Throughput: 10,000 files/hour (high, because thousands run in parallel)
```

---

### Bandwidth

**What it is:** The maximum data transfer rate of a network link or system. Measured in bits or bytes per second.

**Plain English:** "How much data can flow through the pipe per second?"

**Real examples:**
```
Home internet (cable):  100–500 Mbps download
Server NIC (1 GbE):     1 Gbps = 125 MB/s
Server NIC (10 GbE):    10 Gbps = 1.25 GB/s
YouTube peak egress:    ~40 Tbps globally (CDN handles this)
Nordstrom CDN egress:   ~500 Gbps during Anniversary Sale peak
AWS region interconnect: hundreds of Gbps
```

**Bandwidth vs. Latency — common confusion:**
```
Bandwidth: width of the pipe (how much fits through at once)
Latency:   how long it takes to travel through the pipe

High bandwidth + high latency = fast file transfer, slow interactive use
  (think: satellite internet — fast downloads, terrible for gaming)

Low bandwidth + low latency = slow file transfer, responsive interactive use
  (think: old 2G phone — pages load slowly but feel responsive)
```

---

### TTFB — Time to First Byte

**What it is:** How long from when a client sends a request to when it receives the first byte of the response.

**Plain English:** "How long before the browser starts receiving anything?"

**Real example — Nordstrom.com product page:**
```
User clicks a link:
  DNS lookup:          5ms
  TCP connection:      15ms
  SSL handshake:       20ms
  Server processing:   80ms  ← this is what you control
  First byte received: 120ms total TTFB

A good TTFB is under 200ms. Google uses TTFB as a Core Web Vital.
SSR (Server-Side Rendering) directly improves TTFB because the
server sends rendered HTML instead of a blank page.
```

---

### QPS / RPS — Queries Per Second / Requests Per Second

**What it is:** How many requests a system receives or handles per second. QPS and RPS mean the same thing.

**Plain English:** "How busy is the system right now?"

**Real examples:**
```
Google Search:          ~100,000 queries/second globally
Twitter feed reads:     ~300,000 requests/second at peak
Nordstrom.com:          ~50,000 requests/second during Anniversary Sale
Stripe charge API:      ~6,350 charges/second on Black Friday
YouTube video views:    ~100,000 view requests/second
```

**How to estimate QPS from DAU:**
```
Formula: QPS = (DAU × actions/user/day) ÷ 86,400
Shortcut: DAU × actions ÷ 100,000 (since 1 day ≈ 100K seconds)

Example — Nordstrom.com:
  10M DAU × 20 page views/day ÷ 100,000 = 2,000 QPS average
  Peak (3× average) = 6,000 QPS normal days
  Anniversary Sale (10× average) = 20,000 QPS
```

---

## Category 3 — Consistency and Data Terms

---

### Consistency

**What it is:** Whether all parts of the system see the same data at the same time.

**Plain English:** "If I write something, can someone else read it immediately?"

**Strong consistency:**
```
After a write completes, every subsequent read returns that write.
No stale data. Every reader sees the latest version.

Example: Stripe payment records.
  When a charge succeeds, every service that reads that charge
  immediately sees the success status. You can't have the
  merchant dashboard showing "pending" while the receipt shows "paid."

Cost: Slower writes (must wait for all replicas to confirm).
      Cannot tolerate network partitions.
```

**Eventual consistency:**
```
After a write, readers will eventually see it — but not immediately.
There's a window where different readers see different versions.

Example: Nordstrom Content API (SWR pattern).
  An editor publishes updated promotion copy.
  For ~5 seconds, some users see the old copy (cached),
  others see the new copy (revalidated).
  Within 5 seconds, everyone sees the same copy.

Cost: Stale reads during the consistency window.
Benefit: Faster writes, higher availability, tolerates network partitions.
```

**Causal consistency:**
```
If event A causes event B, every reader that sees B also sees A.
Operations that are causally related appear in the correct order.

Example: WhatsApp messages in a group.
  Alice sends "Are you coming to the meeting?" (message A)
  Bob replies "Yes, see you there!" (message B, caused by A)
  Causal consistency ensures no one sees Bob's reply before Alice's question.
```

---

### CAP Theorem

**What it is:** In a distributed system, you can only guarantee two of three properties: Consistency, Availability, Partition tolerance.

**Plain English:** "When the network breaks, choose: stay consistent or stay available."

```
C = Consistency:         all nodes see the same data at the same time
A = Availability:        every request gets a response (not an error)
P = Partition tolerance: system works even when network splits nodes

Network partitions always happen eventually.
So the real choice is always: C vs. A during a partition.

CP (choose consistency over availability):
  During a network partition, some nodes refuse to respond
  rather than return potentially stale data.
  Example: Stripe payments — better to fail a charge than
           charge twice or return wrong balance.

AP (choose availability over consistency):
  During a network partition, nodes respond with potentially stale data
  rather than returning an error.
  Example: Nordstrom product catalog — better to show a slightly
           stale price than to show "service unavailable."
```

---

### ACID

**What it is:** Four properties that guarantee database transactions are processed reliably.

**Plain English:** "The rules that make databases trustworthy for financial data."

```
A = Atomicity:    All or nothing. If any part of a transaction fails,
                  the whole thing is rolled back.
                  Example: Stripe charges a card AND creates an order record.
                  If the order record fails, the charge is reversed.

C = Consistency:  A transaction brings the database from one valid state
                  to another. No partial writes that violate constraints.
                  Example: An order can't reference a product_id that doesn't exist.

I = Isolation:    Concurrent transactions don't interfere with each other.
                  Example: Two users buying the last item —
                  only one transaction succeeds, not both.

D = Durability:   Once committed, data survives crashes.
                  Example: After Stripe confirms a charge, a server crash
                  doesn't lose that charge record.

Databases with ACID: Postgres, MySQL, Oracle, SQL Server
Databases without full ACID: Cassandra, DynamoDB, Redis (by default)
```

---

### BASE

**What it is:** The alternative to ACID used by many NoSQL databases.

**Plain English:** "A more relaxed set of guarantees that allows higher availability and scale."

```
BA = Basically Available:  The system remains available (with possible staleness)
S  = Soft state:           Data may change over time even without new writes
                           (as replicas sync)
E  = Eventual consistency: The system will become consistent over time

Example: Cassandra (used by Discord, Instagram)
  A message written to one Cassandra node is eventually replicated
  to all other nodes. For a brief period, different nodes may have
  different data. Eventually they converge.

When to use ACID vs BASE:
  ACID: Financial transactions, inventory reservations, user accounts
  BASE: Social feeds, content metadata, analytics, non-critical data
```

---

### Idempotency

**What it is:** An operation that produces the same result no matter how many times you perform it.

**Plain English:** "Doing it twice is the same as doing it once."

**Real examples:**
```
Idempotent:
  Stripe charge with idempotency key:
    POST /charges {amount: 100, idempotency_key: "order_123"}
    → First call: charges the card, returns success
    → Second call (retry): returns the SAME success response, no new charge
    → Customer is never charged twice for the same order

  HTTP GET: fetching a product page is idempotent (doesn't change state)
  Redis SET: setting a key to a value is idempotent

Not idempotent:
  HTTP POST without idempotency key: clicking "submit order" twice
  creates two orders
  
  Kafka at-least-once delivery: a message may be delivered multiple times.
  The consumer must be idempotent (handle duplicates gracefully).
```

**Why it matters in system design:**
```
Network calls can fail in ways where you don't know if the call succeeded.
The safe response to ambiguity is to retry.
Retries are only safe if the operation is idempotent.

Stripe's solution: every mutating API call accepts an Idempotency-Key header.
The same key always produces the same result. Merchants can retry safely.
```

---

### Sharding / Horizontal Partitioning

**What it is:** Splitting data across multiple databases or nodes, where each node holds a subset of the data.

**Plain English:** "Splitting one big database into many smaller ones."

**Real example — Nordstrom order database:**
```
Problem: 80M orders/year growing at 20%/year.
         Single Postgres instance can't store or query this efficiently.

Solution: Shard by user_id.
  Users with user_id ending in 0-1 → Shard 0
  Users with user_id ending in 2-3 → Shard 1
  Users with user_id ending in 4-5 → Shard 2
  Users with user_id ending in 6-7 → Shard 3
  Users with user_id ending in 8-9 → Shard 4

  "Show me all orders for user 12345678" →
  Hash user_id → go to the correct shard → query only there

Benefits: Each shard is smaller, faster, independently scalable.
Costs:    Queries across users (reports, analytics) require querying all shards.
          The shard key is hard to change later.
```

**Shard key selection is critical:**
```
Good shard key: high cardinality, even distribution, matches query patterns
Bad shard key: creates hot shards (one shard gets all the traffic)

Example of a bad shard key for Nordstrom:
  Shard by created_at month.
  All new orders go to this month's shard → that shard is always hot.
  Old shards are cold but still taking up resources.
```

---

### Replication

**What it is:** Keeping copies of data on multiple nodes so that if one node fails, others can serve the data.

**Plain English:** "Making backups that can also serve traffic."

```
Primary-Replica (Master-Slave):
  Primary node accepts all writes.
  Replica nodes receive copies of writes asynchronously.
  Reads can be served from replicas.

  Example: Nordstrom product catalog
    Primary: accepts CREATE/UPDATE product operations
    Replicas (3): serve 95% of read traffic (product pages, search)
    If primary fails: a replica is promoted to primary (failover)

Replication factor:
  How many copies of data exist.
  Cassandra default: 3 (data on 3 nodes, tolerates 1 node failure)
  HDFS default: 3
  AWS S3: 11 nines durability = many copies across many data centers
```

---

### Dimensionality (as used in data/ML contexts)

**What it is:** The number of features or attributes used to describe a data point.

**Plain English:** "How many things you know about each item."

**Real examples:**
```
Low dimensionality:
  A tweet: {text, user_id, timestamp} = 3 dimensions

High dimensionality:
  A product recommendation model input for a Nordstrom customer:
  {
    age_group,
    gender,
    loyalty_tier,
    days_since_last_purchase,
    avg_order_value,
    top_category_1, top_category_2, top_category_3,
    last_10_brands_viewed,
    time_of_day,
    device_type,
    ...
  } = potentially hundreds of dimensions

"Curse of dimensionality":
  As dimensions increase, data becomes sparse.
  You need exponentially more data to find meaningful patterns.
  Solution: dimensionality reduction (PCA, embeddings) to compress
  hundreds of dimensions into 50-100 meaningful ones.
```

**In vector databases (used in AI systems):**
```
A text embedding from GPT has 1,536 dimensions.
Each dimension is a number capturing some aspect of meaning.
Two semantically similar texts have similar values across all 1,536 dimensions.
Searching for similar texts = finding vectors close in 1,536-dimensional space.
```

---

## Category 4 — Architecture Patterns

---

### Microservices

**What it is:** An architecture where an application is built as a collection of small, independent services that each do one thing and communicate over APIs.

**Plain English:** "Many small apps instead of one big app."

```
Monolith (before):
  One codebase, one deployment, one database.
  Search, Checkout, Product pages all in one app.
  Benefit: Simple to develop initially.
  Problem: Any change requires deploying everything.
           One bug in Checkout can break Search.

Microservices (after):
  Search Service, Checkout Service, Product Service each deployable independently.
  Each has its own database.
  Each can be scaled independently.

Nordstrom example:
  The micro-frontend platform is a form of microservices for the frontend.
  Each team (Search, PDP, Checkout) deploys their app independently.
  The platform service handles routing and SSR infrastructure.
```

---

### Event-Driven Architecture

**What it is:** Components communicate by publishing and subscribing to events, rather than calling each other directly.

**Plain English:** "Instead of calling you directly, I announce something happened, and you react to it."

```
Synchronous (direct call):
  Order Service calls Inventory Service: "Reserve this item"
  Inventory Service calls Payment Service: "Charge this card"
  Everything waits for everything else.
  Problem: If one service is slow, everything is slow.
           If one service is down, everything fails.

Event-driven (async):
  Order Service publishes event: "order.created" to Kafka
  Inventory Service subscribes, processes reservation
  Payment Service subscribes, processes payment
  Notification Service subscribes, sends confirmation email
  Each service reacts independently.
  If Notification Service is down, orders still process.

Real example — Nordstrom order lifecycle:
  order.created → [inventory reservation, payment initiation]
  payment.succeeded → [warehouse notification, email confirmation]
  order.shipped → [tracking update, loyalty points credited]
```

---

### CQRS — Command Query Responsibility Segregation

**What it is:** Separating the write path (commands) from the read path (queries) so each can be optimized independently.

**Plain English:** "Different systems for writing data and reading data."

```
Without CQRS:
  Same database handles reads and writes.
  A heavy analytics query competes with write transactions for DB resources.
  Optimizing for reads (indexes) slows down writes.

With CQRS:
  Write path: normalized database (fast writes, easy consistency)
  Read path:  denormalized read models (fast reads, pre-joined data)

Real example — Nordstrom order history:
  Write path: Order events written to Postgres (ACID, normalized)
  Read path:  Pre-computed order summaries written to Elasticsearch
              (denormalized, fast search, no joins needed)

  "Get all orders for customer 12345" → Elasticsearch (fast)
  "Create order"                      → Postgres (ACID)
```

---

### Circuit Breaker

**What it is:** A mechanism that detects when a downstream service is failing and stops sending requests to it for a period, allowing it to recover.

**Plain English:** "Stop hammering a broken service — give it time to recover."

```
Without circuit breaker:
  Visa card network is slow (500ms normally → 8 seconds)
  Your API keeps sending requests to Visa
  Thread pool fills up waiting for Visa responses
  Your entire API becomes unresponsive
  (This is what happened to Stripe on Black Friday 2019)

With circuit breaker:
  Visa response time > 3 seconds → record failure
  After 5 failures in 60 seconds → circuit breaker OPENS
  While open: immediately return error to caller (no wait)
              "Card network unavailable, try again later"
  After 30 seconds → circuit breaker HALF-OPEN
  Send one test request to Visa
  If it succeeds → circuit breaker CLOSES (normal operation)
  If it fails → stay OPEN for another 30 seconds

States:
  CLOSED:      Normal operation, requests pass through
  OPEN:        Failure detected, requests fail immediately
  HALF-OPEN:   Testing if service recovered
```

---

### Bulkhead Pattern

**What it is:** Isolating components so that a failure in one doesn't cascade to others. Named after ship compartments that prevent flooding.

**Plain English:** "Walls between parts of the system so a leak in one doesn't sink the whole ship."

```
Without bulkheads:
  One thread pool handles all API requests (Visa, fraud check, DB).
  Visa gets slow → threads fill up waiting for Visa.
  No threads left to handle DB calls or fraud checks.
  Entire API is down.

With bulkheads:
  Dedicated thread pool for Visa calls (max 20 threads)
  Dedicated thread pool for DB calls (max 50 threads)
  Dedicated thread pool for fraud calls (max 10 threads)

  Visa gets slow → only Visa thread pool fills up.
  DB and fraud continue working.
  Visa-related requests fail gracefully; everything else works.

Real example — Nordstrom checkout:
  Separate worker pools for:
    - Payment processing (Stripe calls)
    - Inventory checks (internal DB)
    - Promotion evaluation (rules engine)
  A slow Stripe response doesn't block inventory checks.
```

---

### Rate Limiting

**What it is:** Restricting how many requests a client can make within a time window.

**Plain English:** "Only X requests per second/minute from you."

```
Why it's needed:
  Without rate limiting, one misbehaving client can consume all server capacity.
  A bot sending 10,000 product page requests/second would overwhelm Nordstrom.com.

Common algorithms:
  Token bucket: client gets N tokens/second; each request consumes one token.
                Allows short bursts up to bucket capacity.
                Example: Stripe allows 100 API calls/second per account.

  Sliding window: count requests in the last N seconds.
                  More accurate than fixed windows.
                  Example: GitHub API: 5,000 requests per hour per user.

  Fixed window:   count requests in the current time window (minute, hour).
                  Simple but allows burst at window boundary.

Real example — Nordstrom Content API:
  Rate limit: 1,000 requests/minute per API consumer (frontend app)
  Storage: Redis counter per client_id, TTL = 60 seconds
  On limit exceeded: return HTTP 429 Too Many Requests
```

---

### Load Balancing

**What it is:** Distributing incoming requests across multiple servers so no single server is overwhelmed.

**Plain English:** "Spreading the work evenly across many workers."

```
Algorithms:
  Round robin:    request 1 → server A, request 2 → server B, request 3 → server C...
                  Simple, doesn't account for server load.

  Least connections: send to the server with fewest active connections.
                     Better for long-lived connections (WebSockets).

  Consistent hashing: same client always goes to same server.
                      Important for stateful services (Collab Node in Figma).

L4 vs L7:
  L4 (TCP level):  Fast, protocol-agnostic. Routes by IP and port.
                   Can't inspect HTTP content.

  L7 (HTTP level): Can route by URL, headers, cookies.
                   Nordstrom platform: routes /search to Search team's app,
                   /product to PDP team's app.
```

---

### CDN — Content Delivery Network

**What it is:** A globally distributed network of servers that cache content close to users.

**Plain English:** "Copies of your content stored near every user in the world."

```
Without CDN:
  A user in Tokyo requests a Nordstrom product image.
  Request travels from Tokyo → Seattle datacenter → back to Tokyo.
  Latency: ~150ms just for the network round trip.

With CDN (CloudFront, Akamai, Fastly):
  The same product image is cached on a CDN server in Tokyo.
  Request: Tokyo user → Tokyo CDN node → image served.
  Latency: ~5ms.

What goes on the CDN:
  ✓ Static assets (images, CSS, JavaScript bundles)
  ✓ Rendered HTML pages with short TTLs
  ✓ Product images, video content
  ✗ Personalized content (can't be cached — different per user)
  ✗ Dynamic API responses (stock levels, prices — change frequently)

Nordstrom example:
  Product images: CDN with 24-hour TTL
  Homepage HTML: CDN with 5-minute TTL (refreshed when content changes)
  Pricing: NOT on CDN — computed per user at request time
```

---

## Category 5 — Storage Terms

---

### Cache

**What it is:** A fast, temporary storage layer that stores frequently accessed data so you don't have to fetch it from the slower original source every time.

**Plain English:** "Keep a quick copy of things you use often."

```
Without cache:
  Every product page request → query Postgres for product data → 15ms
  At 50,000 requests/second: Postgres gets 50,000 queries/second → overwhelmed

With Redis cache:
  First request → query Postgres → store result in Redis (TTL: 5 min)
  Next 50,000 requests → read from Redis → 0.5ms each
  Postgres gets ~1 query/5 minutes per product → completely manageable

Cache hit: data found in cache (fast path)
Cache miss: data not in cache, must fetch from source (slow path)
Cache hit rate: percentage of requests served from cache
  (Nordstrom Content API: ~97% cache hit rate)
```

**Cache strategies:**
```
Cache-aside (lazy loading):
  Read: check cache → if miss, fetch from DB → store in cache
  Write: write to DB (don't update cache — let it expire)
  Used for: read-heavy data (product catalog, content)

Write-through:
  Every write goes to BOTH cache and DB simultaneously.
  Cache is always up to date.
  Used for: data that must be consistent (user sessions)

Write-behind (write-back):
  Write to cache immediately, write to DB asynchronously later.
  Faster writes, risk of data loss if cache fails before DB write.
  Used for: high-write systems where small data loss is acceptable
```

**TTL — Time to Live:**
```
How long a cache entry is valid before it expires.
After expiry, the next request is a cache miss and fetches fresh data.

Examples:
  Nordstrom product images:   24 hours (images rarely change)
  Nordstrom product prices:   60 seconds (sale prices change)
  Nordstrom homepage content: 300 seconds (5 min via SWR)
  Uber driver locations:      30 seconds (driver goes offline)
  Session tokens:             1 hour (JWT expiry)
```

---

### Message Queue

**What it is:** A system that holds messages from producers until consumers are ready to process them. Decouples senders from receivers.

**Plain English:** "A mailbox between two services — leave a message, I'll process it when I'm ready."

```
Without message queue (tight coupling):
  When an order is placed, the Order Service calls:
  → Inventory Service (reserve stock)
  → Payment Service (charge card)
  → Notification Service (send email)
  → Loyalty Service (award points)
  All synchronously. If any one is slow, checkout is slow.
  If any one is down, checkout fails.

With Kafka (message queue):
  Order Service publishes "order.created" event and returns 200 immediately.
  Each downstream service subscribes and processes when ready:
  → Inventory Service processes independently
  → Notification Service processes independently
  → Loyalty Service processes independently
  Checkout is fast. If Notification Service is down, it processes the
  backlog when it comes back up. No order is lost.

Kafka vs SQS:
  Kafka: log-based, messages retained (replayable), partitioned, high throughput
         Used when: you need to replay events, multiple consumers, high volume
  SQS:   queue-based, messages deleted after consumption, simpler, managed
         Used when: simple task queues, AWS-native, don't need replay
```

---

### Object Storage vs Block Storage vs File Storage

**What it is:** Three different ways to store data, each optimized for different use cases.

**Plain English:** "Three different kinds of storage, like boxes vs. hard drives vs. filing cabinets."

```
Object Storage (S3, GCS):
  Stores files as immutable objects with metadata and a unique key.
  No hierarchy (though keys can have "/" to simulate folders).
  Accessed via HTTP API (PUT to upload, GET to download).
  Unlimited scale. Cheap. CDN-friendly.
  Best for: images, videos, backups, ML training data, Yjs snapshots
  Nordstrom: product images, content snapshots, media assets

Block Storage (AWS EBS):
  Raw storage attached to a virtual machine, like a hard drive.
  Low latency, high IOPS.
  Best for: databases, OS disks, applications needing fast random reads
  Nordstrom: Postgres data files, Redis persistence

File Storage (EFS, NFS):
  Shared file system accessible by multiple servers simultaneously.
  Like a network drive.
  Best for: shared configuration, log aggregation, legacy apps
  Less common in modern cloud-native architectures.
```

---

### Primary vs. Replica (Master vs. Slave)

**What it is:** In a replicated database, the primary accepts writes; replicas receive copies and serve reads.

**Plain English:** "One writer, many readers."

```
Architecture:
  Primary (one): handles all INSERT, UPDATE, DELETE operations
  Replicas (N):  receive copies of all writes asynchronously
                 serve SELECT (read) queries

Read/write split:
  Application: writes → Primary
               reads  → Round-robin across replicas

Why use replicas:
  Scale reads beyond what one server can handle
  Geographic distribution (replica in US-East, EU-West, Asia)
  Failover: if primary fails, promote a replica

Replication lag:
  Time between write on Primary and availability on Replica.
  Typically < 1 second on same datacenter.
  If a user writes data and immediately reads it, they might
  read from a replica before the write has propagated.
  Solution: read-your-own-writes — route a user's reads to
  primary immediately after their write.
```

---

### Indexing

**What it is:** A data structure that makes database queries faster by pre-sorting data on specific columns.

**Plain English:** "A book's index — instead of reading every page, jump to the right section."

```
Without index:
  "Find all orders for customer_id = 12345"
  → Postgres scans every row in the orders table (full table scan)
  → At 80M rows: slow (seconds)

With index on customer_id:
  → Postgres uses B-tree index to jump directly to matching rows
  → At 80M rows: milliseconds

Types of indexes:
  B-tree (default): ordered index, good for equality and range queries
    Example: WHERE customer_id = 12345
             WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'

  Hash index: exact equality only, faster than B-tree for lookups
    Example: WHERE session_token = 'abc123'

  Full-text index (Elasticsearch): tokenizes text for search
    Example: Search for products containing "ankle boots"

  Composite index: index on multiple columns together
    Example: INDEX ON orders(customer_id, created_at DESC)
             Optimizes: WHERE customer_id = X ORDER BY created_at DESC

Cost of indexes:
  Writes become slower (must update the index on every insert/update)
  Index takes disk space
  Rule of thumb: index columns you filter or sort by frequently
```

---

## Category 6 — Distributed Systems Terms

---

### Partition Tolerance

**What it is:** A system's ability to continue operating even when network messages between nodes are delayed or dropped.

**Plain English:** "The system keeps working even when some nodes can't talk to each other."

```
Network partition: a network failure that splits nodes into groups
that can't communicate.

Example: Nordstrom has servers in US-East and US-West.
If the network link between them fails (partition):
  Without partition tolerance: system shuts down to prevent inconsistency
  With partition tolerance: both regions keep serving requests
                            with potentially different data
                            (eventual consistency)

In the CAP theorem, P (partition tolerance) is almost always required
because network failures are inevitable. The real choice is C vs. A.
```

---

### Consensus

**What it is:** The process by which distributed nodes agree on a single value or decision.

**Plain English:** "Getting all the servers to agree on something."

```
Why it's hard: Messages can be lost. Nodes can crash. Timing is uncertain.

Real example: Uber's hash ring for routing drivers to Collab Nodes.
  When a new Collab Node starts, all gateway nodes must agree on the
  new ring configuration. If some gateways use the old ring and others
  use the new one, drivers get routed inconsistently.

Consensus algorithms:
  Raft:   Used by etcd (Kubernetes), CockroachDB.
          Leader-based: one node is the leader, others follow.
  Paxos:  Mathematical foundation of Raft.
          More complex to implement correctly.
  Zookeeper (ZAB): Used by Kafka for broker coordination.

You rarely implement consensus yourself — you use a system
(etcd, Zookeeper, Consul) that implements it for you.
```

---

### Distributed Lock

**What it is:** A mechanism to ensure only one process across multiple servers can execute a critical section at a time.

**Plain English:** "A mutex (lock) that works across many servers."

```
Why needed: On one server, use a mutex. On 10 servers, need a
distributed lock so only one server runs the critical code.

Real example — Nordstrom Compaction Worker:
  Multiple compaction workers run in parallel for efficiency.
  But two workers must not compact the same document simultaneously
  (they'd both write a new snapshot, causing conflicts).

  Solution: Postgres advisory lock on document_id before starting.
  Worker A: SELECT pg_try_advisory_lock(doc_id) → true → proceed
  Worker B: SELECT pg_try_advisory_lock(doc_id) → false → skip

Redis-based distributed lock (Redlock):
  SET lock:resource_name {random_value} NX PX 30000
  NX = only set if not exists (atomic acquire)
  PX 30000 = auto-expire after 30 seconds (in case process crashes)

Caveats: Distributed locks are tricky.
  If the lock holder crashes after acquiring but before releasing:
  → TTL ensures lock eventually expires
  But if the operation takes longer than the TTL:
  → Another process acquires the lock while first is still running
  → Both processes think they hold the lock
```

---

### Heartbeat

**What it is:** A periodic signal sent by a node to indicate it's still alive and working.

**Plain English:** "A regular 'I'm still here' ping."

```
Real example — Uber gateway detecting Collab Node failures:
  Each Collab Node sends a heartbeat to the gateway every 5 seconds.
  If gateway doesn't receive a heartbeat for 15 seconds:
  → Node is considered failed
  → Removed from the consistent hash ring
  → New connections routed to other nodes

Without heartbeats:
  A crashed node would remain in the routing table.
  Clients would be routed to a dead node and get connection refused.
  Takes a long time to discover the failure.

With heartbeats:
  Failure detected within 15 seconds (3× heartbeat interval).
  Routing table updated. Minimal disruption.
```

---

### Fanout

**What it is:** Taking one event or message and delivering copies to many recipients.

**Plain English:** "One tweet → delivered to millions of followers' feeds."

```
Fanout on write (push model):
  When Alice tweets, immediately write to all 10M followers' feed caches.
  Reads are instant (pre-computed). Writes are expensive for celebrities.
  Used for: normal users (< 1M followers)

Fanout on read (pull model):
  When Bob opens his feed, fetch tweets from everyone he follows.
  Reads are slower. Writes are cheap.
  Used for: celebrities (> 1M followers)

Fanout factor: how many copies of one event are created.
  Tweet to 10M followers = fanout factor of 10M
  WhatsApp message to 256-person group = fanout factor of 255
  Nordstrom "new product" event to search index = fanout factor of 1
    (one event, one index update)
```

---

### Idempotency Key

**What it is:** A unique identifier attached to a request that allows the server to deduplicate retries.

**Plain English:** "A reference number that means: if you've seen this before, return the same answer."

```
Problem without idempotency keys:
  Client sends: POST /charges {amount: 100}
  Network timeout: client doesn't know if it succeeded
  Client retries: POST /charges {amount: 100}
  → Customer is charged twice!

Solution with idempotency keys:
  Client sends: POST /charges {amount: 100, idempotency_key: "order_abc_payment_1"}
  Server: first time → process charge → store result against key
  Client retries: POST /charges {amount: 100, idempotency_key: "order_abc_payment_1"}
  Server: key already seen → return stored result → no new charge

Used by: Stripe (every mutating API call), Uber (trip creation),
         any system where double-execution is dangerous.

Storage: Redis (TTL 24h) for fast lookup + Postgres for permanent audit log.
```

---

### Bloom Filter

**What it is:** A space-efficient probabilistic data structure that tells you whether an item is definitely NOT in a set, or possibly in a set.

**Plain English:** "A quick 'probably yes / definitely no' check before doing something expensive."

```
Properties:
  False positives possible: "yes" sometimes when the answer is "no"
  False negatives impossible: "no" always means definitely not in the set

Real example — Dropbox deduplication:
  Before uploading a 4MB chunk, check if it already exists in S3.
  Naive approach: query S3 for every chunk → expensive
  With Bloom filter: first check the Bloom filter (in memory, < 1ms)
    → "definitely not in S3" → upload it
    → "possibly in S3" → do the actual S3 check to confirm

  Bloom filter holds hashes of all 500B existing chunks.
  Size: ~1.2 GB for 500B items (vs. storing all chunk IDs: would be TBs)
  Eliminates most unnecessary S3 API calls.

Another example: Chrome's Safe Browsing.
  Bloom filter of malicious URLs stored locally on your browser.
  False positive rate: ~1% (1 in 100 safe URLs triggers a server check).
  99% of lookups are handled locally without a network request.
```

---

## Category 7 — Observability Terms

---

### Observability

**What it is:** The ability to understand what's happening inside a system from its external outputs.

**Plain English:** "Can you tell what's wrong from the data the system produces?"

```
The three pillars:
  Metrics:  Aggregated numbers over time (QPS, latency p99, error rate)
  Logs:     Structured records of individual events (per-request, per-error)
  Traces:   End-to-end request paths across multiple services

Observable system: when something goes wrong at 3am, the on-call can
                   diagnose the cause from dashboards and logs alone,
                   without calling the engineer who built it.

Non-observable system: "It's slow but we don't know why."
```

---

### Distributed Tracing

**What it is:** Following a single request through all the services it touches, with timing for each step.

**Plain English:** "A receipt that shows everywhere your request went and how long each stop took."

```
Real example — Nordstrom checkout slow:
  Without tracing: "Checkout is slow" (no idea why)

  With distributed tracing (Jaeger, Datadog APM, AWS X-Ray):
  Trace ID: abc123, total: 2,847ms

  Span 1: API Gateway JWT validation         12ms  ✓
  Span 2: Promotion rules evaluation         45ms  ✓
  Span 3: Inventory check (DB query)          8ms  ✓
  Span 4: Stripe charge API call          2,598ms  ← problem here
  Span 5: Order record write (Postgres)       8ms  ✓

  Immediately obvious: Stripe is slow today, not our code.
  Alert: escalate to Stripe status page, not our on-call.

Implementation: each service adds a trace_id to outbound calls.
  The next service logs receipt time with the same trace_id.
  Tracing system correlates all spans by trace_id.
```

---

### MTTD and MTTR

**What they are:** Mean Time To Detect (how long to notice a problem) and Mean Time To Recover (how long to fix it).

**Plain English:** MTTD = how long until you know something is wrong. MTTR = how long to fix it.

```
MTTD:
  Bad:  You learn about an outage from a customer tweet (hours after it started)
  Good: Automated alerting fires within 2 minutes of SLO violation

MTTR:
  Bad:  Finding the root cause takes 4 hours of log diving
  Good: Distributed tracing shows the cause in 5 minutes,
        runbook shows the fix in another 10 minutes

Nordstrom CMS example:
  Before (legacy system): MTTD ~45 minutes (someone on Slack notices site issue)
                          MTTR ~2 hours (no runbooks, no traces)
  After (Sanity + observability): MTTD ~2 minutes (alert on content propagation lag)
                                  MTTR ~15 minutes (trace shows which component)
```

---

## Quick Reference — Term Relationships

```
SLI → the measurement
SLO → the target for that measurement
SLA → the SLO with contractual consequences

Latency  → time for one operation
Throughput → volume per unit time
Bandwidth → capacity of the pipe

Strong consistency → everyone sees the same data immediately
Eventual consistency → everyone sees the same data eventually
CAP theorem → during a partition, choose C or A

Primary → handles writes
Replica → handles reads, provides failover
Shard → horizontal partition (each shard has a subset of data)

Cache hit  → data found in cache (fast)
Cache miss → data not in cache, must fetch from source (slow)
Cache TTL  → how long before cached data expires

Fanout on write → push to all recipients when event occurs (fast reads)
Fanout on read  → pull from sources when reader requests (simple writes)

Heartbeat → periodic "I'm alive" signal
Circuit breaker → stops requests to failing service
Bulkhead → isolates failures so one component doesn't take down others

Idempotency → same operation twice = same result as once
Idempotency key → the deduplication identifier that makes it work
```

---

## Category 2 Additions — More Performance Terms

---

### Cold Start

**What it is:** The initial performance penalty when a service/function starts up for the first time or after being idle.

**Plain English:** "The first request is slow because the system needs to wake up."

**Real example — AWS Lambda:**
```
User makes request → Lambda function hasn't run in 15 minutes
  → AWS must allocate container, load code, initialize runtime
  → First request: 2000ms
  → Subsequent requests: 50ms (container is warm)

This is why Stripe keeps critical Lambda functions "warm" by pinging them
every 5 minutes—they never want cold starts on payment API calls.
```

**Real examples:**
```
AWS Lambda:         ~500ms-3s cold start (depends on runtime/size)
Application cache:  First query hits database (100ms), subsequent hit cache (1ms)
JVM application:    JIT compiler needs time to optimize hot paths
Connection pool:    First request creates connections (200ms), later reuse (1ms)
CDN:               First request fetches from origin (500ms), then serves from edge (20ms)
```

**Common mistake:** Not distinguishing between cold start latency and steady-state latency in system design discussions.

---

### Tail Latency

**What it is:** The latency experienced by the slowest requests—typically measured at p99 or p999.

**Plain English:** "The worst experience your unluckiest users have."

**Real example — Nordstrom Product API:**
```
p50 latency: 20ms   → half of users see this or better
p95 latency: 45ms   → 95% see this or better
p99 latency: 300ms  → 1% of users wait this long (tail latency)

Why tail latency matters:
  If a page makes 100 API calls, probability that at least one hits p99:
    1 - (0.99)^100 = 63%
  
  So even though only 1% of *requests* are slow, 63% of *pages* see a slow request.
```

**Real examples:**
```
Google Search:    p99 latency = 200ms (but page makes 1 request, so user sees it)
Amazon homepage:  p99 latency = 50ms per service, but page calls 150+ services
                  → Almost guaranteed one service hits tail latency
                  → Must handle via timeouts and fallbacks

Stripe:          p999 latency for charges monitored closely—even 0.1% affects revenue
```

---

### Jitter

**What it is:** Variation or unpredictability in latency over time.

**Plain English:** "Sometimes fast, sometimes slow—inconsistent performance."

**Real example — Nordstrom API:**
```
Low jitter (good):
  Request 1: 20ms
  Request 2: 22ms
  Request 3: 19ms
  Request 4: 21ms
  → Predictable, users see consistent experience

High jitter (bad):
  Request 1: 20ms
  Request 2: 300ms  ← garbage collection pause
  Request 3: 18ms
  Request 4: 450ms  ← network congestion
  → Unpredictable, poor user experience
```

**Common causes:**
```
Garbage collection:    JVM/Node.js pauses create latency spikes
Network congestion:    Shared network creates variable latency
Noisy neighbor:        Other VMs on same host compete for CPU
Database cache miss:   Sometimes hit cache (1ms), sometimes hit disk (100ms)
```

---

### Back Pressure

**What it is:** When a downstream service can't keep up with incoming requests, it signals upstream to slow down.

**Plain English:** "I'm overwhelmed, please stop sending so fast."

**Real example — Nordstrom order processing:**
```
Flow:
  Web API → Kafka → Order Processing Service → Database

Scenario: Black Friday traffic spike
  → Web API produces 10,000 orders/sec to Kafka
  → Order Processing Service can only handle 2,000/sec
  → Kafka queue grows to millions of messages
  → Processing lag increases from seconds to hours

Back pressure solution:
  → Order Processing Service signals it's overloaded
  → Kafka limits how fast Web API can produce
  → Web API returns 503 (Service Unavailable) to some customers
  → Better to fail fast than accept orders that won't process for hours
```

**Real examples:**
```
HTTP/2:          Flow control frames tell sender to slow down
TCP:             Window size controls how much data sender can send
Reactive Streams: Subscriber signals how many items it can handle
Kafka:           Consumer lag monitoring triggers rate limiting
```

---

### Thundering Herd

**What it is:** Many clients simultaneously trying to access the same resource, overwhelming it.

**Plain English:** "Everyone rushes to the door at once."

**Real example — Nordstrom Anniversary Sale:**
```
Scenario: Sale starts at 12:00 AM
  → 500,000 users refresh the homepage simultaneously
  → All hit the same cache key at once
  → Cache key expired at midnight (bad timing)
  → All 500,000 requests hit the database
  → Database overwhelmed, goes down
  → Site outage

Solution:
  → Cache key expires at 11:58 PM (before sale)
  → First request at 11:58 PM warms cache
  → 500,000 requests at midnight all hit warm cache
  → Database handles 1 request, not 500,000
```

**Real examples:**
```
Cache expiration:     All keys expire at same time
Service restart:      All clients reconnect simultaneously
Scheduled job:        All workers start at top of hour
COVID vaccine:        Appointment system opens, millions hit F5
Concert tickets:      Sale starts, Ticketmaster goes down
```

**Mitigation strategies:**
```
Jitter:               Random delay before retry (100ms ± 50ms)
Staggered expiration: Cache keys expire at different times
Queue:                Limit concurrent access to resource
Rate limiting:        Control request rate per client
```

---

### Connection Pooling

**What it is:** Reusing established connections to a service instead of creating new ones for each request.

**Plain English:** "Keep connections open and reuse them instead of constantly reconnecting."

**Real example — Nordstrom API to Database:**
```
Without pool:
  Request 1 → Open TCP connection (50ms) → Query (5ms) → Close connection
  Request 2 → Open TCP connection (50ms) → Query (5ms) → Close connection
  Total: 110ms

With pool:
  Request 1 → Borrow connection from pool (0.1ms) → Query (5ms) → Return to pool
  Request 2 → Borrow connection from pool (0.1ms) → Query (5ms) → Return to pool
  Total: 10.2ms
```

**Configuration example:**
```
Connection pool settings:
  Min connections: 10    → Keep at least 10 warm connections
  Max connections: 50    → Don't exceed 50 (database limit is 100)
  Idle timeout: 600s     → Close connections unused for 10 minutes
  Max lifetime: 1800s    → Recycle connections after 30 minutes
```

**Real examples:**
```
JDBC (Java):      HikariCP manages database connections
Node.js:          pg-pool for PostgreSQL
Redis:            Connection pool for Redis clients
HTTP:             Keep-Alive connections in HTTP/1.1
```

---

### Debouncing vs Throttling

**What it is:** Two strategies for limiting how often a function executes.

**Plain English:**
```
Debouncing: "Wait until they stop before doing anything"
Throttling: "Do it at most once per time period"
```

**Real example — Search autocomplete:**
```
Scenario: User types "laptop"
  Keystroke: l → a → p → t → o → p (6 keystrokes in 600ms)

Debouncing (wait 200ms after last keystroke):
  Type "l"      → wait
  Type "a"      → wait
  Type "p"      → wait
  Type "t"      → wait
  Type "o"      → wait
  Type "p"      → wait 200ms → SEND API REQUEST for "laptop"
  
  Result: 1 API call

Throttling (max 1 request per 200ms):
  Type "l"      → SEND API REQUEST (1)
  Type "a"      → skip (too soon)
  Type "p"      → SEND API REQUEST (2) (200ms elapsed)
  Type "t"      → skip
  Type "o"      → SEND API REQUEST (3) (200ms elapsed)
  Type "p"      → skip
  
  Result: 3 API calls
```

**When to use:**
```
Debouncing:
  - Search autocomplete (wait for user to finish typing)
  - Window resize events (wait for user to finish resizing)
  - Form validation (wait for user to finish entering field)

Throttling:
  - Scroll events (update UI max once per 100ms while scrolling)
  - Mouse move tracking (sample position max 10 times/second)
  - API rate limiting (max 100 requests/minute)
```

---

### Batching

**What it is:** Grouping multiple operations together and executing them as one to reduce overhead.

**Plain English:** "Do many things at once instead of one at a time."

**Real example — Nordstrom order notifications:**
```
Without batching:
  Order 1 → Send email (50ms overhead + 5ms actual send)
  Order 2 → Send email (50ms overhead + 5ms actual send)
  Order 3 → Send email (50ms overhead + 5ms actual send)
  Total: 165ms for 3 emails

With batching:
  Collect orders 1, 2, 3 → Send batch (50ms overhead + 15ms for 3 emails)
  Total: 65ms for 3 emails
```

**Real examples:**
```
Database inserts:
  Single INSERT: 100 operations = 100 round trips = 5000ms
  Batch INSERT:  100 rows in 1 INSERT = 1 round trip = 100ms

Kafka:
  Producer batches 100 messages before sending to reduce network overhead

React:
  Batches multiple setState() calls into single re-render

GraphQL DataLoader:
  User 1 needs Post A → queue request
  User 2 needs Post B → queue request  
  User 3 needs Post A → queue request
  → Single database query: SELECT * FROM posts WHERE id IN ('A', 'B')
```

**Trade-off:**
```
Batching increases latency of individual requests but increases throughput.

Single request:  10ms latency, 100 requests/sec throughput
Batched (10):    50ms latency, 500 requests/sec throughput

Choose batching when throughput matters more than latency.
```

---

## Category 3 Additions — More Consistency and Data Terms

---

### Eventual Consistency

**What it is:** A consistency model where replicas may temporarily have different data, but will eventually converge to the same state.

**Plain English:** "Everyone will see the same data eventually, but not immediately."

**Real example — Nordstrom product price:**
```
Scenario: Price changes from $100 to $80

t=0ms:  Write to primary database in US-East: $80
t=5ms:  Customer in New York queries: sees $80 (read from primary)
t=10ms: Customer in London queries: sees $100 (read from replica, not yet synced)
t=50ms: Customer in London queries: sees $80 (replica caught up)

During the 50ms window, two customers saw different prices.
This is eventual consistency.
```

**Real examples:**
```
DNS:              Update propagates across nameservers over minutes/hours
DynamoDB:         Default mode—reads may return stale data
Cassandra:        Prioritizes availability over consistency
Social media:     Like count may differ across users temporarily
S3:               After upload, GET may return old version briefly
```

**When acceptable:**
```
✓ Social media feeds (who cares if like count is off by 1 for a second)
✓ Product catalog (price from 5 seconds ago is fine)
✓ Analytics (dashboard being 30s stale is acceptable)

✗ Bank balance (can't show wrong balance even for 1 second)
✗ Inventory (can't sell the same item twice)
✗ Trading (stale price causes wrong trades)
```

---

### Strong Consistency

**What it is:** Every read receives the most recent write—all replicas always have the same data.

**Plain English:** "Everyone sees the same data at the same time, always."

**Real example — Bank account balance:**
```
Scenario: Transfer $100 from Account A to Account B

Strong consistency approach:
  t=0ms:   Lock both accounts
  t=10ms:  Deduct $100 from Account A
  t=20ms:  Add $100 to Account B
  t=30ms:  Unlock both accounts
  t=31ms:  Any read of Account A or B shows updated balance

If someone queries at t=15ms while transaction is in progress:
  → Query waits until t=30ms
  → Returns consistent view: both updated or neither updated
  → Never shows A debited but B not yet credited
```

**Real examples:**
```
PostgreSQL:               Default mode—all reads see latest writes
DynamoDB strong read:     Specify ConsistentRead=true
Google Spanner:           Globally distributed strong consistency
Banking systems:          Account balances must always be correct
Inventory systems:        Can't oversell by showing stale inventory
```

**Trade-off:**
```
Strong consistency:
  ✓ Correctness guaranteed
  ✗ Higher latency (must wait for all replicas)
  ✗ Lower availability (can't read if primary down)

Eventual consistency:
  ✓ Lower latency (read from nearest replica)
  ✓ Higher availability (read even if primary down)
  ✗ May return stale data
```

---

### Linearizability

**What it is:** The strongest consistency guarantee—operations appear to happen atomically and in real-time order.

**Plain English:** "Operations happen instantly and in exactly the order they occurred in real time."

**Real example — Ticket sales:**
```
Strong consistency (not linearizable):
  User A at t=100ms: buys last ticket → Success
  User B at t=200ms: buys last ticket → checks inventory, sees 0, Failure
  
  But User B's query might read from replica that hasn't synced yet,
  temporarily shows 1 ticket available, then fails on write.
  Strong consistency ensures correctness, but B briefly saw stale data.

Linearizable:
  User A at t=100ms: buys last ticket → Success
  User B at t=200ms: queries inventory → sees 0 tickets (never sees 1)
  
  Every read after A's write completes sees 0 tickets—real-time ordering preserved.
```

**Real examples:**
```
Google Spanner:    Linearizable distributed database
etcd:              Linearizable key-value store (used by Kubernetes)
ZooKeeper:         Linearizable coordination service
Compare-and-swap:  Linearizable atomic operation

Contrast:
  DynamoDB:        Eventually consistent (not linearizable)
  Cassandra:       Eventually consistent (not linearizable)
  Most caches:     Not linearizable
```

**Why it matters:**
```
Use linearizability when operation order is critical:
  ✓ Leader election (exactly one winner)
  ✓ Distributed locking (only one holder at a time)
  ✓ Ticket sales (no overselling)
  ✓ Inventory management (accurate real-time counts)

Don't need it for:
  ✗ Social media feeds (who cares about exact ordering of posts)
  ✗ Analytics (approximate counts are fine)
  ✗ Caching (stale data for seconds is acceptable)
```

---

### Read-Your-Writes Consistency

**What it is:** After you write something, your subsequent reads will see that write—but others may not.

**Plain English:** "You always see your own changes, but others might not immediately."

**Real example — Social media post:**
```
Scenario: You post "Hello World" on Twitter

t=0ms:   You post → Write to primary database (US-East)
t=1ms:   You refresh your profile → You see "Hello World"
         (Your session routes to primary or uses session tracking)
t=5ms:   Your friend in Europe refreshes your profile → doesn't see post yet
         (Their request hits EU replica, not yet synced)
t=100ms: Your friend refreshes again → sees "Hello World"
         (Replica has caught up)

You immediately saw your post (read-your-writes).
Your friend eventually saw it (eventual consistency).
```

**Implementation:**
```
Approach 1: Session affinity
  After user writes, their session sticks to primary for next 5 minutes
  
Approach 2: Version tracking
  Write returns version number v=1234
  Read includes "I need at least v=1234"
  If replica has v<1234, wait or forward to primary
  
Approach 3: Read from primary
  After write, read from primary for next 10 seconds
  Then fall back to eventual consistency reads from replicas
```

**Real examples:**
```
Facebook:         You see your post immediately
Instagram:        You see your photo immediately
Twitter:          You see your tweet immediately
Nordstrom cart:   You see items you added immediately (session state)
```

---

### Two-Phase Commit (2PC)

**What it is:** A distributed transaction protocol that ensures all participants commit or all abort.

**Plain English:** "Everyone agrees before anyone commits—all or nothing."

**Real example — E-commerce order:**
```
Scenario: User buys item for $50

Participants:
  1. Inventory service (decrement stock)
  2. Payment service (charge card)
  3. Order service (create order record)

Phase 1 — Prepare:
  Coordinator to Inventory: "Can you decrement stock?"
    → Inventory: "Yes, locked row, ready to commit"
  Coordinator to Payment: "Can you charge $50?"
    → Payment: "Yes, authorized, ready to commit"
  Coordinator to Order: "Can you create order?"
    → Order: "Yes, ready to commit"

Phase 2 — Commit:
  Coordinator: "All agreed, everyone commit"
  Inventory → commits (stock decremented)
  Payment → commits (charge processed)
  Order → commits (order created)

If any participant said "No" in Phase 1:
  Coordinator: "Someone said no, everyone abort/rollback"
```

**The problem with 2PC:**
```
Blocking protocol—if coordinator crashes after Phase 1:
  → All participants are stuck waiting (holding locks)
  → Can't commit (didn't receive commit message)
  → Can't abort (might be the only one that failed)
  → System hangs until coordinator recovers
  
This is why modern systems prefer Saga pattern over 2PC.
```

---

### Saga Pattern

**What it is:** A sequence of local transactions where each transaction publishes an event or message that triggers the next step. If one fails, compensating transactions undo previous steps.

**Plain English:** "Try each step, if one fails, undo the previous steps."

**Real example — Travel booking:**
```
Saga: Book flight + hotel + car

Step 1: Book flight
  → Success: Flight booked, payment authorized
  → Emit event: FlightBooked
  
Step 2: Book hotel (triggered by FlightBooked)
  → Success: Hotel booked
  → Emit event: HotelBooked
  
Step 3: Book car (triggered by HotelBooked)
  → FAILURE: No cars available
  → Emit event: SagaFailed
  
Compensating transactions:
  → Receive SagaFailed
  → Cancel hotel booking (compensate step 2)
  → Cancel flight booking (compensate step 1)
  → Refund payment

User sees: "Unable to complete booking, no cars available. Your card was not charged."
```

**Saga vs 2PC:**
```
Two-Phase Commit (2PC):
  → Synchronous, blocking
  → Locks resources during transaction
  → If coordinator crashes, participants stuck
  → Used within single database or trusted cluster

Saga:
  → Asynchronous, non-blocking
  → No locks held across steps
  → Each step commits immediately
  → Uses compensating transactions for rollback
  → Used across multiple independent services
```

**Real examples:**
```
Amazon order:
  1. Authorize payment
  2. Reserve inventory
  3. Create shipment
  If step 3 fails → Release inventory, Cancel authorization

Uber ride:
  1. Reserve driver
  2. Start trip
  3. End trip
  4. Charge rider
  If step 4 fails → Refund reservation, Compensate driver from Uber funds

Netflix subscription:
  1. Charge card
  2. Activate subscription
  3. Send welcome email
  If step 2 fails → Refund charge
```


---

## Category 8 — Scalability and Deployment (New)

---

### Horizontal Scaling vs Vertical Scaling

**What it is:** Two approaches to increasing system capacity.

**Plain English:**
```
Vertical scaling (scale up):    "Buy a bigger machine"
Horizontal scaling (scale out): "Buy more machines"
```

**Real example — Nordstrom product API:**
```
Vertical scaling:
  Current: 16 CPU, 64GB RAM server handles 10K requests/second
  Scale up: 32 CPU, 128GB RAM server handles 20K requests/second
  
  Pros: Simple—same code, same deployment
  Cons: Expensive, hits hardware limits, single point of failure

Horizontal scaling:
  Current: 10 servers × 2K requests/second each = 20K total
  Scale out: 20 servers × 2K requests/second each = 40K total
  
  Pros: Cheaper (commodity hardware), unlimited scale, fault tolerant
  Cons: Requires load balancing, stateless design, distributed systems complexity
```

**Real examples:**
```
Vertical scaling examples:
  Postgres primary:    Start with 8 cores → upgrade to 64 cores
  Redis cache:         16GB RAM → 128GB RAM
  
Horizontal scaling examples:
  Web servers:         10 instances → 100 instances (stateless)
  Kafka brokers:       3 brokers → 12 brokers
  Microservices:       Each service independently scalable
```

**When to use:**
```
Vertical scaling:
  ✓ Single-node databases (Postgres, MySQL primary)
  ✓ In-memory caches (Redis, Memcached)
  ✓ Quick fix to buy time before architectural changes

Horizontal scaling:
  ✓ Stateless web servers
  ✓ Distributed databases (Cassandra, DynamoDB)
  ✓ Message queues (Kafka, SQS)
  ✓ Long-term solution for unlimited growth
```

---

### Stateless vs Stateful Services

**What it is:** Whether a service stores user data between requests.

**Plain English:**
```
Stateless: "Doesn't remember you—treat every request as new"
Stateful:  "Remembers you—session persists across requests"
```

**Real example — Web servers:**
```
Stateless web server:
  Request 1 from User A → Server 1 → No session stored on server
  Request 2 from User A → Server 2 → Works fine (no dependency on Server 1)
  Authentication: JWT in cookie (client holds state, not server)
  
  Benefits: Easy to scale horizontally, any server handles any request
  Load balancer doesn't need session affinity

Stateful web server:
  Request 1 from User A → Server 1 → Session stored in Server 1's memory
  Request 2 from User A → Server 2 → Session missing, user logged out
  
  Problem: Must use sticky sessions (load balancer pins user to one server)
           Can't easily scale or replace servers without losing sessions
```

**Real examples:**
```
Stateless:
  Nordstrom API gateway:    JWT for auth, no server-side session
  Stripe API:               API key in request, no session
  AWS Lambda:               Each invocation independent

Stateful:
  WebSocket servers:        Open connection per user, must stay on same server
  Figma Collab Nodes:       Document state in memory, consistent hashing required
  Game servers:             Player state held in server memory
```

**How to scale stateful services:**
```
Option 1: Consistent hashing
  User ID → hash → routes to same server every time
  (Figma's approach)

Option 2: External state store
  Session stored in Redis, not server memory
  Any server can fetch session from Redis
  (Common approach for web apps)

Option 3: Sticky sessions
  Load balancer remembers which server a user is on
  Routes all their requests there
  (Fragile—server restart loses sessions)
```

---

### Blue-Green Deployment

**What it is:** Running two identical production environments ("blue" and "green") and switching traffic between them for zero-downtime deployments.

**Plain English:** "Deploy to the idle environment, test it, then flip the switch."

**Real example — Nordstrom platform:**
```
Current state:
  Blue environment:  Current production (version 1.0), handling 100% traffic
  Green environment: Idle

Deployment process:
  Step 1: Deploy version 2.0 to Green environment
  Step 2: Green is now running version 2.0, Blue still has traffic
  Step 3: Smoke test Green (hit a test endpoint, check logs)
  Step 4: Switch load balancer: route 100% traffic to Green
  Step 5: Blue is now idle (still running 1.0 as a backup)

If something goes wrong:
  → Switch load balancer back to Blue (1.0)
  → Instant rollback, no downtime
```

**Pros and cons:**
```
Pros:
  ✓ Zero downtime
  ✓ Instant rollback (just flip switch back)
  ✓ Full testing of new version before going live

Cons:
  ✗ Requires 2× infrastructure cost
  ✗ Database migrations are tricky (both versions may need same schema)
  ✗ Not suitable for stateful systems (WebSockets, long-lived connections)
```

---

### Canary Deployment

**What it is:** Gradually rolling out a new version to a small percentage of users before full release.

**Plain English:** "Test it on 5% of users first, then expand if it looks good."

**Real example — Stripe charge API:**
```
Version 1.0 handles 100% traffic

Canary rollout:
  t=0:     Version 2.0 deployed to 5% of servers
           95% of traffic → v1.0, 5% → v2.0
           Monitor error rates, latency for the 5%
           
  t=30min: If 5% looks good, increase to 25%
  t=1hr:   If 25% looks good, increase to 50%
  t=2hr:   If 50% looks good, increase to 100%

If canary shows problems:
  → Roll back immediately (95% of users unaffected)
  → Debug on the small canary population

Common canary rules:
  - Route internal employees to canary first
  - Route low-value users before high-value
  - Gradually increase: 5% → 25% → 50% → 100%
```

**Canary vs Blue-Green:**
```
Blue-Green:
  → All or nothing switch
  → Requires 2× infrastructure
  → Instant rollback

Canary:
  → Gradual rollout
  → Limits blast radius of bugs
  → Can catch issues with small user sample before full release
```

---

### Feature Flags / Feature Toggles

**What it is:** Configuration that enables/disables features at runtime without redeploying code.

**Plain English:** "An if-statement that you can flip on/off from a dashboard."

**Real example — Nordstrom new search algorithm:**
```
Code:
  if (featureFlags.isEnabled('new_search_algorithm', userId)) {
    return newSearchAlgorithm(query);
  } else {
    return oldSearchAlgorithm(query);
  }

Rollout plan:
  Week 1: Enable for internal employees (testing)
  Week 2: Enable for 1% of users (canary)
  Week 3: Enable for 10% of users
  Week 4: Enable for 50% of users
  Week 5: Enable for 100% of users
  
If bugs appear at 10%, immediately disable flag → everyone back to old algorithm
```

**Use cases:**
```
Gradual rollout:
  Release feature to 5% → 25% → 50% → 100%
  
A/B testing:
  50% users see version A, 50% see version B
  Measure which performs better
  
Kill switch:
  Feature causing issues? Disable it instantly, no deployment needed
  
Ops readiness:
  Code deployed, feature off until ops team ready (migrated data, scaled DB)
```

**Nordstrom example:**
```
Feature: AI-generated product descriptions

Deploy code with flag OFF:
  → Code in production, feature disabled for all users
  
Content team ready to review AI output:
  → Enable flag for internal content team only
  
AI output quality validated:
  → Enable for 10% of product pages
  → Monitor bounce rates, conversion
  
Looks good:
  → Enable for 100%
```

---

### Auto-Scaling

**What it is:** Automatically adjusting the number of servers based on current demand.

**Plain English:** "Add servers when traffic increases, remove them when it decreases."

**Real example — Nordstrom platform during Anniversary Sale:**
```
Normal traffic: 5,000 requests/second
  → Auto-scaler maintains 20 pods (250 req/s per pod)

Anniversary Sale starts:
  → Traffic spikes to 50,000 requests/second
  → CPU usage on pods hits 80% (trigger threshold)
  → Auto-scaler adds pods: 20 → 40 → 80 → 150 → 200
  → 200 pods @ 250 req/s = 50,000 req/s capacity
  → CPU usage drops to 60% (healthy)

Sale ends:
  → Traffic drops to 10,000 requests/second
  → CPU usage drops to 30% (scale-down threshold)
  → Auto-scaler removes pods: 200 → 100 → 50 → 40
```

**Scaling policies:**
```
CPU-based:
  Scale up when CPU > 70%
  Scale down when CPU < 30%
  
Request-based:
  Scale up when requests/pod > 500
  Scale down when requests/pod < 100
  
Custom metrics:
  Scale based on queue depth, latency p99, or business metrics
```

**Configuration:**
```
Min replicas: 10    → Never go below 10 (baseline capacity)
Max replicas: 200   → Never exceed 200 (cost control)
Target CPU: 60%     → Try to keep CPU around 60%
Scale-up: Fast      → Add pods quickly when needed
Scale-down: Slow    → Remove pods gradually (avoid thrashing)
```

---

### Health Checks: Readiness vs Liveness

**What it is:** Two types of checks Kubernetes uses to determine if a pod is working correctly.

**Plain English:**
```
Liveness:  "Is the app still running, or should we restart it?"
Readiness: "Is the app ready to receive traffic?"
```

**Real example — Nordstrom API pod:**
```
Liveness probe:
  Endpoint: GET /health/alive
  Checks: Is the process running? Is it responding at all?
  Failure action: Kill the pod and restart it
  
  Example failure: App deadlocked, can't respond to requests
  → Liveness probe times out → Kubernetes kills and restarts pod

Readiness probe:
  Endpoint: GET /health/ready
  Checks: Is the app fully initialized and ready for traffic?
  Failure action: Remove from load balancer (but don't kill it)
  
  Example scenario: Pod starting up, still loading data from database
  → Readiness probe fails → Pod NOT added to load balancer yet
  → Once data loaded → Readiness succeeds → Pod receives traffic
```

**Why both are needed:**
```
Liveness without readiness:
  Problem: Pod added to load balancer before it's ready
  → Users get errors while app initializes

Readiness without liveness:
  Problem: App deadlocks, never recovers
  → Pod stays running but broken forever

Both together:
  → Readiness: don't send traffic until ready
  → Liveness: restart if it stops responding
```

---

## Category 9 — Caching Strategies (New)

---

### Cache-Aside (Lazy Loading)

**What it is:** Application checks cache first, fetches from database on miss, then stores in cache.

**Plain English:** "Check the cache, if not there, get it from the database and save it for next time."

**Real example — Nordstrom product page:**
```
Request for product ID 12345:
  
  1. Check Redis: GET product:12345
     → Cache miss (not in cache)
  
  2. Query Postgres: SELECT * FROM products WHERE id = 12345
     → Returns product data (15ms)
  
  3. Store in Redis: SET product:12345 {data} EX 3600
     → Cached for 1 hour
  
  4. Return product data to user
  
Next request for product 12345:
  1. Check Redis: GET product:12345
     → Cache hit (0.5ms)
  2. Return immediately (no database query)
```

**Pros and cons:**
```
Pros:
  ✓ Simple to implement
  ✓ Only cache what's actually requested (no wasted cache space)
  ✓ Cache failures don't break the app (fallback to DB)

Cons:
  ✗ Cache miss penalty: user waits for DB query + cache write
  ✗ Cache stampede risk (many requests for same expired key hit DB simultaneously)
```

---

### Write-Through Cache

**What it is:** Every write goes to cache AND database synchronously.

**Plain English:** "When you save something, update both the cache and database at the same time."

**Real example — User session:**
```
User logs in:
  1. Write session to database (Postgres): 10ms
  2. Write session to cache (Redis): 1ms
  3. Both complete before responding to user
  
Session always in sync:
  → Read from cache (fast)
  → If cache fails, read from database (slow but correct)
```

**Pros and cons:**
```
Pros:
  ✓ Cache always has latest data
  ✓ No stale reads

Cons:
  ✗ Slower writes (must wait for both cache and DB)
  ✗ Wastes cache space (stores data that might never be read)
```

---

### Write-Behind / Write-Back Cache

**What it is:** Writes go to cache immediately, then asynchronously written to database later.

**Plain English:** "Save to cache now, save to database later."

**Real example — Nordstrom analytics events:**
```
User views product:
  1. Write event to Redis (1ms)
  2. Return success to user immediately
  3. Background worker reads from Redis queue
  4. Batch-write events to Postgres/ClickHouse every 10 seconds

User experience: Instant response
Backend: Processes 10,000 events in one batch write instead of 10,000 individual writes
```

**Pros and cons:**
```
Pros:
  ✓ Very fast writes (cache-speed, not DB-speed)
  ✓ Can batch writes for efficiency

Cons:
  ✗ Risk of data loss (if cache fails before DB write)
  ✗ Complex to implement
  ✗ Not suitable for critical data (payments, inventory)
```

---

### Cache Invalidation

**What it is:** Removing or updating cached data when the source data changes.

**Plain English:** "Making sure the cache doesn't show old data after an update."

**Real example — Nordstrom product price change:**
```
Product price changes from $100 to $80:

Option 1: TTL-based expiration (passive)
  Cache entry has TTL of 10 minutes
  → Wait up to 10 minutes for cache to expire
  → Next request fetches new price and caches it
  Problem: Users see old price for up to 10 minutes

Option 2: Active invalidation
  → Price updated in database
  → Send message to Redis: DEL product:12345
  → Next request is a cache miss, fetches new price
  Problem: Requires coordination between write and cache

Option 3: Write-through
  → Update database AND cache simultaneously
  → Cache always has latest data
```

**The two hard things in computer science:**
```
"There are only two hard things in Computer Science:
 cache invalidation and naming things."
 — Phil Karlton

Cache invalidation is hard because:
  - Timing: when do you invalidate?
  - Scope: which cache entries are affected?
  - Coordination: how do all cache nodes know to invalidate?
  - Thundering herd: mass cache miss after invalidation
```

---

### Cache Eviction Policies

**What it is:** Rules for which cached items to remove when the cache is full.

**Plain English:** "When the cache is full, decide what to delete."

**Algorithms:**
```
LRU (Least Recently Used):
  Evict the item that hasn't been accessed in the longest time
  Example: Redis default
  Good for: Most workloads (recently used → likely used again soon)

LFU (Least Frequently Used):
  Evict the item accessed least number of times
  Good for: Data with stable popularity patterns

FIFO (First In, First Out):
  Evict the oldest item, regardless of access pattern
  Simple but not optimal for most workloads

Random:
  Evict a random item
  Surprisingly effective, very simple

TTL (Time To Live):
  Evict based on expiration time
  Used alongside other policies
```

**Real example — Nordstrom CDN:**
```
Cache size: 100GB per edge node
Current usage: 99GB (almost full)

New 5GB video asset requested:
  → Need to evict 5GB to make room
  → LRU policy: find items not accessed in > 24 hours
  → Evict old product images from last season's sale
  → Cache new video asset
```

---

## Category 10 — API Design (New)

---

### REST vs GraphQL vs gRPC

**What it is:** Three different API architecture styles.

**Plain English:** "Three ways for clients to talk to servers."

**REST (Representational State Transfer):**
```
HTTP-based, resource-oriented, multiple endpoints

Example — Nordstrom product API:
  GET    /products/12345          → Get product
  POST   /products                → Create product
  PUT    /products/12345          → Update product
  DELETE /products/12345          → Delete product
  GET    /products/12345/reviews  → Get reviews

Pros: Simple, cacheable (HTTP caching), widely supported
Cons: Over-fetching (get more data than needed),
      under-fetching (need multiple requests for related data)
```

**GraphQL:**
```
Query language, single endpoint, client specifies exact data needed

Example — Nordstrom product query:
  POST /graphql
  {
    product(id: "12345") {
      name
      price
      images(limit: 3) { url }
      reviews(limit: 5) {
        author
        rating
      }
    }
  }
  
  Returns exactly what was requested, in one request

Pros: No over/under-fetching, flexible, strong typing
Cons: Complex to implement, caching harder, can enable expensive queries
```

**gRPC (Google Remote Procedure Call):**
```
Binary protocol (Protocol Buffers), strongly typed, bidirectional streaming

Example — Uber driver location updates:
  service DriverLocation {
    rpc UpdateLocation (LocationUpdate) returns (Ack);
    rpc StreamLocations (DriverID) returns (stream Location);
  }
  
Pros: Fast (binary), type-safe, bidirectional streaming, code generation
Cons: Not browser-friendly (needs grpc-web), binary not human-readable
```

**When to use:**
```
REST:
  ✓ Public APIs (GitHub, Stripe, Twilio)
  ✓ CRUD operations
  ✓ Cacheable resources

GraphQL:
  ✓ Mobile apps (reduce over-fetching on slow networks)
  ✓ Frontends with complex data requirements
  ✓ APIs with many different client needs

gRPC:
  ✓ Internal microservice communication (low latency critical)
  ✓ Real-time streaming (Uber driver locations)
  ✓ High-throughput systems
```

---

### Pagination: Cursor-Based vs Offset-Based

**What it is:** Two ways to retrieve large result sets in chunks.

**Plain English:** "How to say 'give me the next 20 results'."

**Offset-based (page numbers):**
```
Request page 1: GET /products?limit=20&offset=0      → Products 1-20
Request page 2: GET /products?limit=20&offset=20     → Products 21-40
Request page 3: GET /products?limit=20&offset=40     → Products 41-60

SQL: SELECT * FROM products LIMIT 20 OFFSET 40;

Pros: Simple, users can jump to any page
Cons: 
  ✗ Slow for large offsets (database must skip 1M rows to get to page 50K)
  ✗ Inconsistent results if data changes (item added → page 2 shifts)
```

**Cursor-based (continuation token):**
```
Request page 1: GET /products?limit=20
  → Returns products 1-20 + cursor: "eyJpZCI6MTIzNH0="
  
Request page 2: GET /products?limit=20&cursor=eyJpZCI6MTIzNH0=
  → Cursor decoded: "WHERE id > 1234 LIMIT 20"
  → Returns next 20 products

SQL: SELECT * FROM products WHERE id > 1234 ORDER BY id LIMIT 20;

Pros: 
  ✓ Consistent results even if data changes
  ✓ Fast for any page (uses index, no OFFSET)
  
Cons: 
  ✗ Can't jump to arbitrary page (no "page 50")
  ✗ Slightly more complex to implement
```

**When to use:**
```
Offset-based:
  ✓ Small datasets (< 100K rows)
  ✓ UI needs page numbers (e.g., Google search: "Page 1 of 10")
  ✓ Data rarely changes during pagination

Cursor-based:
  ✓ Large datasets (millions of rows)
  ✓ Infinite scroll UIs (Twitter, Instagram feed)
  ✓ Data frequently changes (social feeds, real-time data)
  ✓ APIs (Stripe, GitHub, most modern APIs use cursors)
```

---

### API Versioning Strategies

**What it is:** How to evolve an API without breaking existing clients.

**Plain English:** "How to make changes without angry customers."

**Strategies:**
```
1. URL versioning:
   GET /v1/products/12345
   GET /v2/products/12345
   
   Pros: Clear, easy to route different versions to different servers
   Cons: Verbose, not RESTful (resource identity changes)

2. Header versioning:
   GET /products/12345
   Headers: Accept: application/vnd.nordstrom.v2+json
   
   Pros: RESTful (same URL), flexible
   Cons: Less visible, harder to test in browser

3. Query parameter:
   GET /products/12345?version=2
   
   Pros: Simple, easy to test
   Cons: Not standard, can conflict with other query params

4. Subdomain:
   api-v1.nordstrom.com/products/12345
   api-v2.nordstrom.com/products/12345
   
   Pros: Easy to route, clear separation
   Cons: More complex infrastructure (certs, DNS)
```

**Stripe's approach (URL versioning with date):**
```
Initial release: 2024-01-15
  GET /v1/charges → uses 2024-01-15 behavior

Breaking change made: 2024-06-01
  Client specifies version:
  Headers: Stripe-Version: 2024-01-15 → old behavior
  Headers: Stripe-Version: 2024-06-01 → new behavior
  
  Client upgrades when ready, not forced immediately
```

**Backward vs Forward Compatibility:**
```
Backward compatible: New server works with old clients
  Example: Adding optional field to response (old clients ignore it)
  
Forward compatible: Old server works with new clients  
  Example: Server ignores unknown fields in request

Best practice: Always backward compatible, sometimes forward compatible
```

---

## Category 11 — Message Queues and Event Processing (New)

---

### At-Least-Once vs At-Most-Once vs Exactly-Once Delivery

**What it is:** Guarantees about message delivery in distributed systems.

**Plain English:** "Will my message be delivered zero, one, or multiple times?"

**At-Most-Once:**
```
"Fire and forget — message may be lost, never duplicated"

Example — Analytics event:
  Client sends: "user viewed product 12345"
  → Network fails before ack received
  → Client doesn't retry (assumes it was delivered)
  → Event lost (but who cares — analytics can tolerate data loss)

Used for: Logs, metrics, non-critical events
```

**At-Least-Once:**
```
"Retry until acknowledged — may deliver duplicates"

Example — Order creation:
  Client sends: "create order for $100"
  → Network timeout, no ack received
  → Client retries
  → Server might have processed first attempt
  → Order might be created twice!

Solution: Make consumer idempotent (use idempotency keys)
  → Duplicate messages OK because consumer deduplicates

Used for: Most production systems (Kafka default, SQS)
```

**Exactly-Once:**
```
"Guaranteed to deliver exactly one time, never duplicated or lost"

Example — Payment processing:
  Must charge customer exactly once (not zero, not twice)
  
Very hard to achieve in distributed systems.
Usually implemented as "at-least-once + idempotent consumer"

Kafka exactly-once: Requires transactions, comes with performance cost
```

**In practice:**
```
Most systems use at-least-once + idempotency:
  Kafka: at-least-once by default
  Consumer: checks idempotency key before processing
  Result: Effectively exactly-once behavior
```

---

### Dead Letter Queue (DLQ)

**What it is:** A queue that holds messages that couldn't be processed after multiple retries.

**Plain English:** "A graveyard for failed messages so they don't clog the main queue."

**Real example — Nordstrom order notification:**
```
Main flow:
  Order created → Message published to SQS
  → Email service consumes message, sends email

Failure scenario:
  Email service tries to send email → SMTP server down
  → Retry 1 (after 10s): still down
  → Retry 2 (after 30s): still down
  → Retry 3 (after 60s): still down
  → After 3 retries: Move message to DLQ

DLQ behavior:
  Message sits in DLQ for manual inspection
  On-call investigates: "Why are these emails failing?"
  Fix SMTP config, replay messages from DLQ
```

**Benefits:**
```
Without DLQ:
  ✗ Poison pill messages block the queue
  ✗ Same message retried forever, consuming resources
  ✗ Can't process newer messages (head-of-line blocking)

With DLQ:
  ✓ Failing messages removed from main queue
  ✓ Main queue keeps processing
  ✓ Failed messages can be debugged and replayed later
```

---

### Pub/Sub vs Message Queue

**What it is:** Two messaging patterns with different delivery semantics.

**Plain English:**
```
Message Queue: "One sender → one receiver (work queue)"
Pub/Sub:       "One publisher → many subscribers (broadcast)"
```

**Message Queue (SQS, RabbitMQ):**
```
Producer adds message to queue
→ One consumer picks it up and processes it
→ Message removed from queue

Example — Background jobs:
  Web server adds "resize image" job to queue
  → Worker 1, 2, or 3 picks it up (whichever is free)
  → Only ONE worker processes the job

Use case: Task distribution, load balancing
```

**Pub/Sub (Kafka, SNS, Google Pub/Sub):**
```
Publisher publishes event to topic
→ ALL subscribers receive a copy of the event
→ Each subscriber processes independently

Example — Order created event:
  Order service publishes "order.created"
  → Inventory service subscribes (decrements stock)
  → Email service subscribes (sends confirmation)
  → Analytics service subscribes (logs event)
  → All three receive the SAME event, process independently

Use case: Event broadcasting, event-driven architecture
```

**Comparison:**
```
Feature            | Message Queue    | Pub/Sub
-------------------|------------------|------------------
Consumers          | One              | Many
Message deleted    | After consumed   | After retention period
Use case           | Task queue       | Event broadcasting
Examples           | SQS, RabbitMQ    | Kafka, SNS
```

---

## Final Note

This glossary now contains **~140 terms** across **11 categories**, covering the essential vocabulary for senior/staff engineer system design interviews. Each term includes:

- Technical definition
- Plain English explanation
- Real-world example (often from Nordstrom, Stripe, or other recognizable systems)
- When to use / trade-offs

Use this as a reference before interviews. Read through once, then revisit specific terms as needed.


---

## More Critical Additions

---

## Category 3 (More Data Terms)

### Write-Ahead Log (WAL)

**What it is:** A log that records all changes before they're applied to the database, ensuring durability.

**Plain English:** "Write everything down in a notebook before actually doing it, so you can recover if you crash."

**Real example — Postgres crash recovery:**
```
Transaction: UPDATE products SET price = 80 WHERE id = 12345

Step 1: Write to WAL on disk:
  "Transaction 5678: Change product 12345 price to 80"
  → WAL write is sequential, fast, durable

Step 2: Write to data files (can happen later, asynchronously):
  Update actual row in database

Crash scenario:
  → Postgres crashes after WAL write but before data file update
  → On restart: Postgres reads WAL
  → "Transaction 5678 was committed but not applied to data files"
  → Replays the change from WAL
  → Database is consistent

Without WAL:
  → Crash loses in-flight transactions
  → Database corrupted
```

**Used in:**
```
Postgres:   Write-Ahead Log (pg_wal/)
MySQL:      Binary Log and Redo Log
Kafka:      Commit Log (this is what Kafka IS—a distributed WAL)
Redis:      AOF (Append-Only File) mode
```

---

### LSM Tree (Log-Structured Merge Tree)

**What it is:** A write-optimized data structure that batches writes in memory then flushes to disk in sorted files.

**Plain English:** "Collect writes in memory, periodically dump to disk in sorted chunks, merge chunks over time."

**How it works:**
```
Writes:
  → Insert goes to MemTable (in-memory sorted structure) — fast
  → When MemTable full → flush to disk as SSTable (Sorted String Table)
  → Many SSTables accumulate over time
  → Background compaction merges small SSTables into larger ones

Reads:
  → Check MemTable first
  → If not found, check SSTables (newest to oldest)
  → May need to check multiple files (slower than B-tree)
```

**Real example — Cassandra:**
```
Write path (fast):
  INSERT INTO products (id, price) VALUES (12345, 80);
  → Append to commit log (WAL) for durability
  → Write to MemTable (in-memory)
  → Return success immediately (< 1ms)

Background compaction:
  → MemTable full → flush to SSTable-1
  → Later: SSTable-1 + SSTable-2 → merge into SSTable-3
  → Discard old data, tombstones during compaction
```

**LSM vs B-Tree:**
```
LSM Tree (Cassandra, RocksDB, LevelDB, HBase):
  ✓ Fast writes (in-memory, sequential disk writes)
  ✗ Slower reads (may check multiple SSTables)
  ✓ Good write amplification (less disk I/O per write)
  Use case: Write-heavy workloads

B-Tree (Postgres, MySQL, Oracle):
  ✗ Slower writes (random disk writes)
  ✓ Fast reads (index lookup, single location)
  ✗ Higher write amplification (must update index in-place)
  Use case: Read-heavy workloads
```

---

### Quorum

**What it is:** A majority of nodes that must agree for an operation to succeed in a distributed system.

**Plain English:** "More than half must agree before we proceed."

**Real example — Cassandra write:**
```
Replication factor: 3 (data stored on 3 nodes)
Quorum: 2 (majority of 3)

Write operation:
  Client writes key=12345
  → Coordinator sends write to all 3 replicas
  → Wait for 2 out of 3 to acknowledge
  → Return success to client

Why quorum reads + quorum writes guarantees consistency:
  Write quorum: 2 nodes
  Read quorum: 2 nodes
  → At least 1 node overlaps
  → Read always sees the latest write
```

**Formulas:**
```
Quorum size: (N / 2) + 1

N=3 nodes → Quorum = 2
N=5 nodes → Quorum = 3
N=7 nodes → Quorum = 4

Read + Write quorums must overlap:
  Write quorum (W) + Read quorum (R) > N
  
Common configurations:
  - W=2, R=2, N=3 (strong consistency)
  - W=1, R=1, N=3 (fast but eventual consistency)
  - W=3, R=1, N=3 (prioritize read speed, slow writes)
```

---

### Optimistic Locking vs Pessimistic Locking

**What it is:** Two strategies for handling concurrent access to data.

**Plain English:**
```
Optimistic:  "Assume no conflicts, check at the end"
Pessimistic: "Assume conflicts, lock upfront"
```

**Pessimistic locking:**
```
SQL:
  BEGIN TRANSACTION;
  SELECT * FROM inventory WHERE product_id = 12345 FOR UPDATE;
    → Row is locked, other transactions wait
  UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 12345;
  COMMIT;
    → Lock released

Use case: High contention (everyone wants the same row)
Example: Ticketmaster ticket sales (everyone buying last ticket)
```

**Optimistic locking:**
```
SQL with version column:
  SELECT quantity, version FROM inventory WHERE product_id = 12345;
    → Read: quantity=10, version=5
  
  UPDATE inventory 
  SET quantity = 9, version = 6
  WHERE product_id = 12345 AND version = 5;
    → If version still 5: update succeeds
    → If version changed: update fails (someone else modified it)
    → Retry from the beginning

Use case: Low contention (conflicts rare)
Example: Nordstrom content edits (rarely do two editors edit same content)
```

**Comparison:**
```
Pessimistic:
  ✓ Guarantees no conflicts (locks prevent them)
  ✗ Lower throughput (locks block other transactions)
  ✗ Risk of deadlocks

Optimistic:
  ✓ Higher throughput (no locks)
  ✗ Must retry on conflict
  ✗ Wasted work if conflict rate high
```

---

### CRDTs (Conflict-free Replicated Data Types)

**What it is:** Data structures designed to be replicated across multiple nodes and merged automatically without conflicts.

**Plain English:** "Magic data types that multiple people can edit simultaneously and it just works."

**Real example — Google Docs collaborative editing:**
```
Problem without CRDTs:
  User A types "Hello" at position 0
  User B types "World" at position 0 (same time, different network partition)
  → Merge conflict: "HelloWorld" or "WorldHello"?

With CRDTs (Yjs, Automerge):
  Each character has a unique ID and a position relative to others
  User A inserts: [A1:H] [A2:e] [A3:l] [A4:l] [A5:o]
  User B inserts: [B1:W] [B2:o] [B3:r] [B4:l] [B5:d]
  → Merge is deterministic based on IDs and rules
  → Both users converge to same state automatically
```

**Types of CRDTs:**
```
G-Counter (Grow-only Counter):
  Each node increments its own counter
  Total = sum of all node counters
  Example: Page view count

PN-Counter (Positive-Negative Counter):
  Tracks increments and decrements separately
  Example: Like/unlike button

LWW-Register (Last-Write-Wins):
  Each write has a timestamp
  Latest timestamp wins
  Example: User profile field

OR-Set (Observed-Remove Set):
  Add and remove operations commute
  Example: Shopping cart items
```

**Use cases:**
```
✓ Collaborative editing (Figma, Google Docs, Notion)
✓ Offline-first apps (local edits sync later)
✓ Multi-leader replication
✓ Eventually consistent systems

✗ Not suitable for: financial transactions (need ACID, not eventual consistency)
```

---

## Category 6 (More Distributed Systems Terms)

### Split-Brain

**What it is:** A network partition that results in multiple nodes thinking they're the leader.

**Plain English:** "Two parts of the system both think they're in charge."

**Real example — Database failover:**
```
Normal:
  Primary database in US-East (handles writes)
  Replica database in US-West (handles reads)
  Heartbeat between them confirms primary is alive

Network partition:
  → Link between US-East and US-West breaks
  → US-West: "I can't reach primary, it must be down, I'll promote myself"
  → US-East: Still running, still accepting writes
  → Now TWO primaries accepting writes!

Result:
  → Conflicting writes to both databases
  → Data divergence
  → When network heals: which data is correct?

Prevention:
  → Quorum: Need majority of nodes to agree before promotion
  → If cluster has 3 nodes, partition with 1 node can't elect leader
  → Only partition with 2+ nodes can elect leader
```

---

### Consistent Hashing

**What it is:** A hashing scheme that minimizes data movement when nodes are added or removed from a distributed system.

**Plain English:** "A clever way to assign data to servers so that adding/removing servers doesn't move everything around."

**Problem without consistent hashing:**
```
Hash function: server_id = hash(key) % N

3 servers (N=3):
  Key "abc" → hash("abc") = 12345 → 12345 % 3 = 0 → Server 0

Add 1 server (N=4):
  Key "abc" → hash("abc") = 12345 → 12345 % 4 = 1 → Server 1
  → Data moved!
  → ALL keys need to be rehashed and moved
```

**With consistent hashing:**
```
Hash ring: 0 to 2^32
  Each server gets a position on the ring
  Each key gets a position on the ring
  Key is assigned to the next server clockwise

Example:
  Server A at position 0
  Server B at position 1,000,000,000
  Server C at position 2,000,000,000

  Key "abc" hashes to 500,000,000
    → Next server clockwise: Server B

Add Server D at position 1,500,000,000:
  → Only keys between 1,000,000,000 and 1,500,000,000 move
  → Keys on other parts of ring unaffected
  → ~25% of keys move instead of 100%
```

**Used in:**
```
Cassandra:  Partition keys → nodes
DynamoDB:   Partition keys → nodes  
Memcached:  Cache keys → cache servers
Chord DHT:  Peer-to-peer file sharing
Figma:      User ID → Collab Node (for WebSocket affinity)
```

---

### Leader Election

**What it is:** The process by which distributed nodes choose one node to be the leader/coordinator.

**Plain English:** "How servers vote to decide who's in charge."

**Why needed:**
```
Scenarios requiring a single leader:
  - Database cluster: one node accepts writes (primary)
  - Distributed lock manager: one node coordinates locks
  - Task scheduler: one node assigns work to avoid duplicates
```

**Real example — Kafka broker election:**
```
3 Kafka brokers: A, B, C
ZooKeeper coordinates election

Initial state:
  → Broker A is elected leader for partition 0
  → Broker B is elected leader for partition 1

Broker A crashes:
  → ZooKeeper detects (no heartbeat for 10 seconds)
  → Triggers election for partition 0
  → Remaining brokers (B, C) propose themselves
  → ZooKeeper picks Broker B as new leader
  → Broker B promoted from follower → leader

Broker A comes back online:
  → Rejoins as follower (not leader)
  → Catches up on missed data from new leader
```

**Consensus algorithms for leader election:**
```
Raft:
  → Nodes vote for leader
  → Candidate with majority votes becomes leader
  → Used in: etcd, Consul

Paxos:
  → More complex, mathematically proven correct
  → Used in: Google Chubby, Google Spanner

ZooKeeper (ZAB):
  → Centralized coordinator
  → Used in: Kafka, HBase
```

---

### Gossip Protocol

**What it is:** A protocol where each node periodically exchanges state information with a few random neighbors, eventually propagating to all nodes.

**Plain English:** "Spread information like rumors—tell a few friends, they tell their friends, soon everyone knows."

**How it works:**
```
Every 1 second:
  1. Node A picks 3 random nodes (B, C, D)
  2. Sends: "Here's what I know about the cluster"
  3. Receives: "Here's what B knows"
  4. Merges information

After log₂(N) rounds, all nodes have the information
  - 1,000 nodes → ~10 rounds → ~10 seconds
  - 1,000,000 nodes → ~20 rounds → ~20 seconds
```

**Real example — Cassandra cluster membership:**
```
New node joins:
  → Node A learns about new node
  → A gossips to B, C, D (tells them about new node)
  → B gossips to E, F, G
  → Within seconds, all nodes know about new node

Node failure:
  → Node Z crashes
  → Neighbors notice no heartbeat
  → Gossip: "Z is down"
  → Within seconds, all nodes mark Z as down
  → Cluster rebalances without Z
```

**Used in:**
```
Cassandra:  Cluster membership, failure detection
Redis:      Cluster mode
DynamoDB:   Membership, failure detection
Bitcoin:    Transaction propagation
```

**Pros and cons:**
```
Pros:
  ✓ Scalable (doesn't require centralized coordinator)
  ✓ Fault tolerant (no single point of failure)
  ✓ Eventually consistent

Cons:
  ✗ Eventual propagation (not instant)
  ✗ Network overhead (constant gossip traffic)
```

---

## Category 4 (More Architecture Patterns)

### Strangler Fig Pattern

**What it is:** Incrementally replacing a legacy system by gradually migrating functionality to a new system.

**Plain English:** "Slowly build the new system around the old one, piece by piece, until the old one can be removed."

**Named after:** Strangler fig trees that grow around host trees, eventually replacing them.

**Real example — Nordstrom CMS migration:**
```
Legacy system: Custom CMS
Target: Sanity CMS

Step 1: New writes go to Sanity, reads fall back to legacy
  → Content editors use new Sanity UI
  → Public website reads from Sanity first, falls back to legacy if not found
  → Both systems running in parallel

Step 2: Backfill old content to Sanity
  → Migrate homepage content
  → Migrate product category content
  → Migrate promotion content
  (All over 6 months, one section at a time)

Step 3: Once Sanity has all data, remove legacy fallback
  → All reads from Sanity only
  → Legacy system decommissioned

If anything goes wrong at any step:
  → Fall back to legacy system
  → No big-bang failure
```

**Key principle:**
```
Routing layer decides: old system or new system?

Initial state: 100% to old system
  → Add feature 1 to new system → route feature 1 to new
  → Add feature 2 to new system → route feature 2 to new
  ...
  → Eventually 100% on new system → decommission old
```

**Vs. Big-Bang Rewrite:**
```
Big-bang:
  → Rewrite entire system in secret
  → Switch everything over on launch day
  → If anything breaks: catastrophic failure
  → High risk

Strangler fig:
  → Migrate one feature at a time
  → Run old and new in parallel
  → Can roll back any feature independently
  → Low risk
```

---

### BFF (Backend for Frontend)

**What it is:** A separate backend service for each frontend (web, mobile, etc.) that aggregates and transforms data to match that frontend's needs.

**Plain English:** "Each type of app gets its own custom backend API."

**Problem without BFF:**
```
Single API for all clients:

Mobile app needs:
  { productId, name, price, thumbnailImage }

Web app needs:
  { productId, name, price, description, largeImages[], reviews[], similarProducts[] }

Generic API returns everything:
  → Mobile app wastes bandwidth downloading data it doesn't use
  → Mobile app makes multiple API calls to get related data
```

**With BFF pattern:**
```
Mobile BFF:
  GET /mobile/products/12345
  → Returns minimal data optimized for mobile (smaller payload)
  → Aggregates from: Product API + Inventory API + Pricing API
  → Returns exactly what mobile app needs

Web BFF:
  GET /web/products/12345
  → Returns full rich data optimized for desktop
  → Aggregates from: Product API + Reviews API + Similar Products API
  → Includes high-res images

Each BFF is maintained by the team owning that frontend
```

**Benefits:**
```
✓ Each frontend gets exactly what it needs (no over-fetching)
✓ Frontend team controls their BFF (no cross-team dependencies)
✓ Can evolve mobile/web BFFs independently
✓ Reduces frontend complexity (no data aggregation logic)
```

**Real example — Netflix:**
```
TV BFF:       Optimized for 10-foot UI, large thumbnails, limited text
Mobile BFF:   Optimized for small screens, low bandwidth
Web BFF:      Optimized for desktop, rich content, search

Each BFF talks to the same backend microservices but transforms differently
```

---

## Category 12 — Network and Protocols (New)

### WebSocket

**What it is:** A protocol that enables full-duplex (two-way) communication over a single TCP connection.

**Plain English:** "A persistent connection where both client and server can send messages anytime."

**HTTP vs WebSocket:**
```
HTTP:
  Client: "GET /messages" (request)
  Server: "{messages}" (response)
  → Connection closes
  → For new data, client must poll: request every 5 seconds

WebSocket:
  Client: Opens connection
  Server: Keeps connection open
  → Either can send messages anytime
  → Server pushes updates immediately when they happen
  → No polling needed
```

**Real example — Figma collaborative editing:**
```
HTTP approach (bad):
  User A types a character
  → Client polls: "any updates?" every 200ms
  → Server: "User B moved a shape"
  → High latency, lots of wasted requests

WebSocket approach:
  User A types "H"
  → Client sends over WebSocket: "insert H at position 10"
  → Server receives immediately
  → Server broadcasts to all connected clients: "User A inserted H"
  → User B's client receives update instantly
  → User B sees "H" appear in real-time
```

**Use cases:**
```
✓ Real-time collaboration (Figma, Google Docs, Notion)
✓ Chat applications (Slack, Discord)
✓ Live feeds (Twitter, stock prices)
✓ Multiplayer games
✓ Live sports scores

✗ Don't use for: REST APIs, file uploads, anything HTTP works fine for
```

**Challenges:**
```
Load balancing:
  → Must use sticky sessions (same user → same server)
  → Or use Redis Pub/Sub to broadcast across servers

Scaling:
  → Each connection holds a socket open (resource intensive)
  → 100K concurrent connections = careful resource management

Reconnection:
  → Network drops, user reconnects
  → Must handle: "What did I miss while disconnected?"
```

---

### HTTP/2 vs HTTP/1.1

**What it is:** Major improvements to the HTTP protocol.

**HTTP/1.1 problems:**
```
1. Head-of-line blocking:
   Request 1 (slow) blocks Request 2,3,4
   Browser workaround: Open 6 connections per domain

2. No header compression:
   Same headers (cookies, user-agent) sent with every request

3. No server push:
   Server can't proactively send resources client will need
```

**HTTP/2 improvements:**
```
1. Multiplexing:
   Many requests over single connection
   Request 2,3,4 don't wait for Request 1 to finish

2. Header compression (HPACK):
   Headers compressed, repeated headers sent once

3. Server push:
   Server: "You requested index.html, you'll also need style.css"
   Pushes style.css before client requests it

4. Binary protocol (not text):
   More efficient parsing
```

**Real example — Nordstrom product page:**
```
HTTP/1.1:
  GET /product/12345 → Response
  (Wait for above)
  GET /api/reviews?productId=12345 → Response
  (Wait for above)
  GET /api/inventory?productId=12345 → Response
  
  Sequential, slow

HTTP/2:
  Single connection, all requests in parallel:
  GET /product/12345
  GET /api/reviews?productId=12345
  GET /api/inventory?productId=12345
  → All responses stream back concurrently
  
  Parallelized, fast
```

**HTTP/3 (QUIC):**
```
Further improvement: Built on UDP instead of TCP
  → Faster connection establishment
  → Better handling of packet loss
  → Mobile-friendly (survives IP address changes)

Used by: Google, Facebook, Cloudflare CDN
```

---

## Category 13 — Security Essentials (New)

### OAuth 2.0 / OpenID Connect

**What it is:** A protocol for authorization (OAuth 2.0) and authentication (OpenID Connect).

**Plain English:**
```
OAuth: "Let an app access your data without giving it your password"
OpenID Connect: "Log in with Google/Facebook"
```

**Real example — "Log in with Google":**
```
User clicks "Log in with Google" on Nordstrom.com

Step 1: Nordstrom redirects to Google:
  https://accounts.google.com/authorize?
    client_id=nordstrom_client_id&
    redirect_uri=https://nordstrom.com/callback&
    scope=openid email profile

Step 2: User logs into Google, approves access

Step 3: Google redirects back to Nordstrom with authorization code:
  https://nordstrom.com/callback?code=abc123

Step 4: Nordstrom exchanges code for tokens:
  POST https://oauth2.googleapis.com/token
  → Receives: access_token, id_token (JWT with user info)

Step 5: Nordstrom validates id_token, creates session

Result: User logged in, Nordstrom never saw Google password
```

**OAuth 2.0 grant types:**
```
Authorization Code (most common):
  → User redirected to auth server, back with code
  → Used for: web apps, mobile apps

Client Credentials:
  → Service-to-service auth (no user involved)
  → Used for: backend microservices

Refresh Token:
  → Access token expires after 1 hour
  → Use refresh token to get new access token without re-login
```

---

### JWT (JSON Web Token)

**What it is:** A self-contained token that carries user identity and claims, signed to prevent tampering.

**Plain English:** "A secure package that says 'this person is who they claim to be'."

**Structure:**
```
JWT = header.payload.signature

Header (Base64):
  { "alg": "HS256", "typ": "JWT" }

Payload (Base64):
  { 
    "userId": "12345",
    "email": "user@example.com",
    "exp": 1704067200
  }

Signature:
  HMAC-SHA256(header + payload, secret_key)

Full JWT:
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxMjM0NSIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTcwNDA2NzIwMH0.signature_here
```

**How it's used:**
```
Login:
  → User logs in with username/password
  → Server validates, generates JWT
  → Returns JWT to client
  → Client stores in cookie or localStorage

API request:
  → Client sends: Authorization: Bearer <JWT>
  → Server validates signature (ensures not tampered)
  → Server reads userId from JWT (no database lookup needed)
  → Server processes request
```

**JWT vs Session:**
```
Session (stateful):
  → Server stores session in database/Redis
  → Client sends session_id cookie
  → Server looks up session on every request
  → Pros: Can revoke immediately
  → Cons: Database lookup on every request

JWT (stateless):
  → Server doesn't store anything
  → Client sends JWT
  → Server validates signature
  → Pros: No database lookup, scales horizontally
  → Cons: Can't revoke until expiration (set short exp time)
```

**Security considerations:**
```
✓ Set short expiration (15 min for access token)
✓ Use refresh token for long-lived sessions
✓ Store in httpOnly cookie (not localStorage—XSS risk)
✓ Validate signature on every request
✗ Don't put sensitive data in payload (it's Base64, not encrypted)
```

---

This expanded glossary now has **~160 terms**, making it a truly exhaustive reference for senior/staff system design interviews. Every term includes real-world examples and practical context.


---

## Complete Term Index

**Category 1 — Reliability & Service Level (6 terms)**
- SLI, SLO, SLA
- Error Budget
- Availability
- (See also: MTTD, MTTR in Category 7)

**Category 2 — Performance (16 terms)**
- Latency (p50, p95, p99, p999)
- Throughput
- Bandwidth
- TTFB
- QPS / RPS
- Cold Start
- Tail Latency
- Jitter
- Back Pressure
- Thundering Herd
- Connection Pooling
- Debouncing vs Throttling
- Batching

**Category 3 — Consistency & Data (24 terms)**
- Consistency (Strong, Eventual, Causal, Read-Your-Writes, Linearizability)
- CAP Theorem
- ACID
- BASE
- Idempotency
- Sharding / Horizontal Partitioning
- Replication
- Dimensionality
- Two-Phase Commit (2PC)
- Saga Pattern
- Write-Ahead Log (WAL)
- LSM Tree
- Quorum
- Optimistic vs Pessimistic Locking
- CRDTs

**Category 4 — Architecture Patterns (11 terms)**
- Microservices
- Event-Driven Architecture
- CQRS
- Circuit Breaker
- Bulkhead Pattern
- Rate Limiting
- Load Balancing
- CDN
- Strangler Fig Pattern
- BFF (Backend for Frontend)

**Category 5 — Storage (5 terms)**
- Cache (Cache-Aside, Write-Through, Write-Back, TTL, Eviction Policies)
- Message Queue
- Object vs Block vs File Storage
- Primary vs Replica
- Indexing

**Category 6 — Distributed Systems (12 terms)**
- Partition Tolerance
- Consensus (Raft, Paxos, ZooKeeper)
- Distributed Lock
- Heartbeat
- Fanout
- Idempotency Key
- Bloom Filter
- Split-Brain
- Consistent Hashing
- Leader Election
- Gossip Protocol

**Category 7 — Observability (3 terms)**
- Observability (Metrics, Logs, Traces)
- Distributed Tracing
- MTTD and MTTR

**Category 8 — Scalability & Deployment (9 terms)**
- Horizontal vs Vertical Scaling
- Stateless vs Stateful Services
- Blue-Green Deployment
- Canary Deployment
- Feature Flags
- Auto-Scaling
- Health Checks (Readiness vs Liveness)

**Category 9 — Caching Strategies (5 terms)**
- Cache-Aside (Lazy Loading)
- Write-Through
- Write-Behind / Write-Back
- Cache Invalidation
- Cache Eviction Policies (LRU, LFU, FIFO)

**Category 10 — API Design (3 terms)**
- REST vs GraphQL vs gRPC
- Pagination (Cursor-Based vs Offset-Based)
- API Versioning
- Backward/Forward Compatibility

**Category 11 — Message Queues & Events (3 terms)**
- At-Least-Once vs At-Most-Once vs Exactly-Once
- Dead Letter Queue (DLQ)
- Pub/Sub vs Message Queue

**Category 12 — Network & Protocols (2 terms)**
- WebSocket
- HTTP/2 vs HTTP/1.1 vs HTTP/3

**Category 13 — Security (2 terms)**
- OAuth 2.0 / OpenID Connect
- JWT (JSON Web Token)

---

## Total: 88+ core terms with 50+ sub-concepts

Every term includes:
✓ Technical definition
✓ Plain English explanation  
✓ Real-world example (Nordstrom, Stripe, or recognizable system)
✓ When to use / trade-offs
✓ Common mistakes or gotchas

---

## How to Use This Glossary

**Before a system design interview:**
1. Read through once (takes ~2 hours)
2. Mark terms you're unfamiliar with
3. Deep-dive those terms with additional research

**During interview prep:**
- Reference specific categories based on problem domain
- E-commerce system → Categories 2, 3, 5, 8
- Chat system → Categories 4, 6, 11, 12
- Financial system → Categories 1, 3, 6

**During actual interviews:**
- Use precise terminology (interviewers notice)
- Explain trade-offs using these concepts
- Reference real examples when it strengthens your point

**Example usage in interview:**
```
Bad:  "We'll use a cache to make it faster"

Good: "We'll use Redis as a cache-aside layer with a 5-minute TTL.
       This gives us sub-millisecond p99 latency for reads while
       ensuring data freshness. For write-heavy workloads, we'd
       consider write-through caching instead, but since our read:write
       ratio is 100:1, cache-aside optimizes for the common path."
```

Using this glossary vocabulary signals staff-level thinking to interviewers.


---
---

# PART 2: PRODUCTION-READY GO CODE EXAMPLES

> Practical implementations of the key patterns discussed above.
> Each example is concise but production-quality, showing real-world usage.

---

## 1. Circuit Breaker

**Pattern:** Prevent cascading failures by stopping requests to failing services.

```go
package resilience

import (
    "context"
    "errors"
    "sync"
    "time"
)

type CircuitBreaker struct {
    maxFailures  int
    resetTimeout time.Duration
    mu           sync.RWMutex
    failures     int
    lastFailTime time.Time
    state        string // "closed", "open", "half-open"
}

func NewCircuitBreaker(maxFailures int, resetTimeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        maxFailures:  maxFailures,
        resetTimeout: resetTimeout,
        state:        "closed",
    }
}

func (cb *CircuitBreaker) Call(ctx context.Context, fn func() error) error {
    cb.mu.RLock()
    state := cb.state
    lastFailTime := cb.lastFailTime
    cb.mu.RUnlock()

    // Circuit is open - reject request
    if state == "open" {
        if time.Since(lastFailTime) > cb.resetTimeout {
            cb.mu.Lock()
            cb.state = "half-open"
            cb.mu.Unlock()
        } else {
            return errors.New("circuit breaker is open")
        }
    }

    // Execute the function
    err := fn()

    cb.mu.Lock()
    defer cb.mu.Unlock()

    if err != nil {
        cb.failures++
        cb.lastFailTime = time.Now()
        if cb.failures >= cb.maxFailures {
            cb.state = "open"
        }
        return err
    }

    // Success - reset
    cb.failures = 0
    cb.state = "closed"
    return nil
}

// Usage Example
func main() {
    cb := NewCircuitBreaker(3, 30*time.Second)

    err := cb.Call(context.Background(), func() error {
        return paymentAPI.Charge(userID, 100.00)
    })

    if err != nil {
        // Circuit is open or request failed
        return fallbackResponse()
    }
}
```

---

## 2. Rate Limiter (Token Bucket)

**Pattern:** Control request rate using token bucket algorithm.

```go
package ratelimit

import (
    "math"
    "sync"
    "time"
)

type RateLimiter struct {
    tokens     float64
    capacity   float64
    refillRate float64    // tokens per second
    lastRefill time.Time
    mu         sync.Mutex
}

func NewRateLimiter(capacity, refillRate float64) *RateLimiter {
    return &RateLimiter{
        tokens:     capacity,
        capacity:   capacity,
        refillRate: refillRate,
        lastRefill: time.Now(),
    }
}

func (rl *RateLimiter) Allow() bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()

    now := time.Now()
    elapsed := now.Sub(rl.lastRefill).Seconds()

    // Refill tokens based on elapsed time
    rl.tokens = math.Min(rl.capacity, rl.tokens + elapsed*rl.refillRate)
    rl.lastRefill = now

    if rl.tokens >= 1.0 {
        rl.tokens--
        return true
    }
    return false
}

// HTTP Middleware
func RateLimitMiddleware(limiter *RateLimiter) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}

// Usage: 100 requests per second
limiter := NewRateLimiter(100, 100)
http.ListenAndServe(":8080", RateLimitMiddleware(limiter)(handler))
```

---

## 3. Cache-Aside Pattern

**Pattern:** Application manages cache explicitly - check cache, fallback to DB, update cache.

```go
package cache

import (
    "context"
    "database/sql"
    "encoding/json"
    "time"

    "github.com/go-redis/redis/v8"
)

type ProductCache struct {
    redis *redis.Client
    db    *sql.DB
}

func (c *ProductCache) GetProduct(ctx context.Context, id string) (*Product, error) {
    cacheKey := "product:" + id

    // 1. Try cache first
    cached, err := c.redis.Get(ctx, cacheKey).Result()
    if err == nil {
        var product Product
        if err := json.Unmarshal([]byte(cached), &product); err == nil {
            return &product, nil
        }
    }

    // 2. Cache miss - query database
    var product Product
    err = c.db.QueryRowContext(ctx,
        "SELECT id, name, price, description FROM products WHERE id = $1", id,
    ).Scan(&product.ID, &product.Name, &product.Price, &product.Description)

    if err != nil {
        return nil, err
    }

    // 3. Store in cache for future requests (TTL: 10 minutes)
    data, _ := json.Marshal(product)
    c.redis.Set(ctx, cacheKey, data, 10*time.Minute)

    return &product, nil
}

// Cache invalidation on update
func (c *ProductCache) UpdateProduct(ctx context.Context, product *Product) error {
    // Update database first
    _, err := c.db.ExecContext(ctx,
        "UPDATE products SET name=$1, price=$2, description=$3 WHERE id=$4",
        product.Name, product.Price, product.Description, product.ID,
    )
    if err != nil {
        return err
    }

    // Invalidate cache
    c.redis.Del(ctx, "product:"+product.ID)
    return nil
}
```

---

## 4. Idempotent Payment Processing

**Pattern:** Use idempotency keys to safely retry payment operations.

```go
package payments

import (
    "context"
    "database/sql"
    "encoding/json"
    "errors"
    "time"

    "github.com/go-redis/redis/v8"
    "github.com/google/uuid"
)

type PaymentService struct {
    db    *sql.DB
    redis *redis.Client
}

type PaymentRequest struct {
    IdempotencyKey string
    UserID         string
    Amount         float64
}

func (s *PaymentService) ProcessPayment(ctx context.Context, req PaymentRequest) (*Payment, error) {
    resultKey := "payment:result:" + req.IdempotencyKey
    lockKey := "payment:lock:" + req.IdempotencyKey

    // Check if already processed
    cached, err := s.redis.Get(ctx, resultKey).Result()
    if err == nil {
        var payment Payment
        json.Unmarshal([]byte(cached), &payment)
        return &payment, nil // Return cached result
    }

    // Acquire distributed lock (prevents concurrent processing)
    locked, err := s.redis.SetNX(ctx, lockKey, "1", 30*time.Second).Result()
    if !locked {
        return nil, errors.New("payment already being processed")
    }
    defer s.redis.Del(ctx, lockKey)

    // Process payment
    payment := &Payment{
        ID:             uuid.New().String(),
        IdempotencyKey: req.IdempotencyKey,
        UserID:         req.UserID,
        Amount:         req.Amount,
        Status:         "completed",
        CreatedAt:      time.Now(),
    }

    // Store in database with idempotency key constraint
    _, err = s.db.ExecContext(ctx,
        `INSERT INTO payments (id, idempotency_key, user_id, amount, status, created_at)
         VALUES ($1, $2, $3, $4, $5, $6)
         ON CONFLICT (idempotency_key) DO NOTHING`,
        payment.ID, payment.IdempotencyKey, payment.UserID,
        payment.Amount, payment.Status, payment.CreatedAt,
    )

    if err != nil {
        return nil, err
    }

    // Cache result for 24 hours
    data, _ := json.Marshal(payment)
    s.redis.Set(ctx, resultKey, data, 24*time.Hour)

    return payment, nil
}
```

---

## 5. Retry with Exponential Backoff

**Pattern:** Retry failed operations with increasing delays and jitter.

```go
package retry

import (
    "context"
    "fmt"
    "math/rand"
    "time"
)

func RetryWithBackoff(ctx context.Context, maxRetries int, fn func() error) error {
    var err error

    for attempt := 0; attempt < maxRetries; attempt++ {
        err = fn()
        if err == nil {
            return nil // Success
        }

        if ctx.Err() != nil {
            return ctx.Err() // Context cancelled
        }

        // Calculate exponential backoff: 100ms, 200ms, 400ms, 800ms...
        backoff := time.Duration(100*(1<<attempt)) * time.Millisecond

        // Add jitter (random ±50%) to prevent thundering herd
        jitter := time.Duration(rand.Int63n(int64(backoff)))
        backoff = backoff + jitter - (backoff / 2)

        // Cap maximum backoff at 10 seconds
        if backoff > 10*time.Second {
            backoff = 10 * time.Second
        }

        select {
        case <-time.After(backoff):
            // Continue to next retry
        case <-ctx.Done():
            return ctx.Err()
        }
    }

    return fmt.Errorf("max retries exceeded: %w", err)
}

// Usage
err := RetryWithBackoff(ctx, 5, func() error {
    return externalAPI.CreateOrder(order)
})
```

---

## 6. Database Connection Pool

**Pattern:** Reuse database connections for performance.

```go
package database

import (
    "context"
    "database/sql"
    "time"

    _ "github.com/lib/pq"
)

func NewDatabasePool(connString string) (*sql.DB, error) {
    db, err := sql.Open("postgres", connString)
    if err != nil {
        return nil, err
    }

    // Connection pool configuration
    db.SetMaxOpenConns(50)                 // Max concurrent connections
    db.SetMaxIdleConns(10)                 // Keep 10 idle connections warm
    db.SetConnMaxLifetime(1 * time.Hour)   // Recycle connections after 1 hour
    db.SetConnMaxIdleTime(10 * time.Minute) // Close idle after 10 minutes

    // Verify connection
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := db.PingContext(ctx); err != nil {
        return nil, err
    }

    return db, nil
}

// Usage with context and timeout
func GetUser(db *sql.DB, userID string) (*User, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()

    var user User
    // Connection automatically borrowed from pool and returned
    err := db.QueryRowContext(ctx,
        "SELECT id, email, name FROM users WHERE id = $1", userID,
    ).Scan(&user.ID, &user.Email, &user.Name)

    return &user, err
}
```

---

## 7. Optimistic Locking

**Pattern:** Handle concurrent updates with version numbers.

```go
package inventory

import (
    "database/sql"
    "errors"
    "time"
)

func DecrementInventory(db *sql.DB, productID string, quantity int) error {
    maxRetries := 3

    for attempt := 0; attempt < maxRetries; attempt++ {
        // Read current state with version
        var currentQty, version int
        err := db.QueryRow(
            "SELECT quantity, version FROM inventory WHERE product_id = $1",
            productID,
        ).Scan(&currentQty, &version)

        if err != nil {
            return err
        }

        if currentQty < quantity {
            return errors.New("insufficient inventory")
        }

        // Optimistic update - only succeeds if version unchanged
        result, err := db.Exec(
            `UPDATE inventory
             SET quantity = quantity - $1, version = version + 1
             WHERE product_id = $2 AND version = $3`,
            quantity, productID, version,
        )

        if err != nil {
            return err
        }

        rowsAffected, _ := result.RowsAffected()
        if rowsAffected == 1 {
            return nil // Success
        }

        // Version conflict - someone else updated it, retry with backoff
        time.Sleep(time.Duration(attempt*50) * time.Millisecond)
    }

    return errors.New("max retries exceeded due to concurrent updates")
}
```

---

## 8. Consistent Hashing

**Pattern:** Distribute data/requests evenly with minimal reshuffling when nodes change.

```go
package consistent

import (
    "fmt"
    "hash/crc32"
    "sort"
    "sync"
)

type ConsistentHash struct {
    circle     map[uint32]string // hash -> server
    sortedKeys []uint32
    servers    map[string]bool
    replicas   int // virtual nodes per server
    mu         sync.RWMutex
}

func NewConsistentHash(replicas int) *ConsistentHash {
    return &ConsistentHash{
        circle:   make(map[uint32]string),
        servers:  make(map[string]bool),
        replicas: replicas,
    }
}

func (ch *ConsistentHash) AddServer(server string) {
    ch.mu.Lock()
    defer ch.mu.Unlock()

    // Add virtual nodes for even distribution
    for i := 0; i < ch.replicas; i++ {
        hash := ch.hash(fmt.Sprintf("%s:%d", server, i))
        ch.circle[hash] = server
        ch.sortedKeys = append(ch.sortedKeys, hash)
    }

    sort.Slice(ch.sortedKeys, func(i, j int) bool {
        return ch.sortedKeys[i] < ch.sortedKeys[j]
    })

    ch.servers[server] = true
}

func (ch *ConsistentHash) GetServer(key string) string {
    ch.mu.RLock()
    defer ch.mu.RUnlock()

    if len(ch.sortedKeys) == 0 {
        return ""
    }

    hash := ch.hash(key)

    // Binary search for first server >= hash
    idx := sort.Search(len(ch.sortedKeys), func(i int) bool {
        return ch.sortedKeys[i] >= hash
    })

    // Wrap around to start if at end
    if idx == len(ch.sortedKeys) {
        idx = 0
    }

    return ch.circle[ch.sortedKeys[idx]]
}

func (ch *ConsistentHash) hash(key string) uint32 {
    return crc32.ChecksumIEEE([]byte(key))
}

// Usage - WebSocket server affinity
ch := NewConsistentHash(150) // 150 virtual nodes per server
ch.AddServer("ws-1")
ch.AddServer("ws-2")
ch.AddServer("ws-3")

userID := "user-12345"
server := ch.GetServer(userID) // Always returns same server for this user
```

---

## 9. Health Check Handlers (Kubernetes-style)

**Pattern:** Separate liveness (is it running?) from readiness (can it serve traffic?).

```go
package health

import (
    "context"
    "database/sql"
    "net/http"
    "time"

    "github.com/go-redis/redis/v8"
)

type HealthChecker struct {
    db    *sql.DB
    redis *redis.Client
}

// Liveness: Is the app alive? (if not, Kubernetes restarts it)
func (h *HealthChecker) LivenessHandler(w http.ResponseWriter, r *http.Request) {
    // Don't check dependencies - we don't want to restart if DB is down
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("alive"))
}

// Readiness: Can the app serve traffic? (if not, remove from load balancer)
func (h *HealthChecker) ReadinessHandler(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
    defer cancel()

    // Check database
    if err := h.db.PingContext(ctx); err != nil {
        http.Error(w, "database unhealthy", http.StatusServiceUnavailable)
        return
    }

    // Check Redis
    if err := h.redis.Ping(ctx).Err(); err != nil {
        http.Error(w, "redis unhealthy", http.StatusServiceUnavailable)
        return
    }

    w.WriteHeader(http.StatusOK)
    w.Write([]byte("ready"))
}

// Setup
func main() {
    checker := &HealthChecker{db: db, redis: redisClient}

    http.HandleFunc("/health/live", checker.LivenessHandler)
    http.HandleFunc("/health/ready", checker.ReadinessHandler)

    http.ListenAndServe(":8080", nil)
}
```

---

## 10. JWT Authentication Middleware

**Pattern:** Validate JWT tokens in HTTP requests.

```go
package auth

import (
    "context"
    "errors"
    "net/http"
    "strings"

    "github.com/golang-jwt/jwt/v5"
)

type Claims struct {
    UserID string `json:"userId"`
    Email  string `json:"email"`
    jwt.RegisteredClaims
}

func ValidateJWT(tokenString string, secretKey []byte) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        // Verify signing method
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, errors.New("unexpected signing method")
        }
        return secretKey, nil
    })

    if err != nil || !token.Valid {
        return nil, errors.New("invalid token")
    }

    claims, ok := token.Claims.(*Claims)
    if !ok {
        return nil, errors.New("invalid claims")
    }

    return claims, nil
}

// HTTP Middleware
func AuthMiddleware(secretKey []byte) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            authHeader := r.Header.Get("Authorization")
            if !strings.HasPrefix(authHeader, "Bearer ") {
                http.Error(w, "unauthorized", http.StatusUnauthorized)
                return
            }

            tokenString := strings.TrimPrefix(authHeader, "Bearer ")
            claims, err := ValidateJWT(tokenString, secretKey)
            if err != nil {
                http.Error(w, "invalid token", http.StatusUnauthorized)
                return
            }

            // Add user info to context
            ctx := context.WithValue(r.Context(), "userID", claims.UserID)
            ctx = context.WithValue(ctx, "email", claims.Email)

            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

---

## 11. Distributed Lock (Redis)

**Pattern:** Coordinate work across multiple instances.

```go
package distributed

import (
    "context"
    "errors"
    "time"

    "github.com/go-redis/redis/v8"
    "github.com/google/uuid"
)

type DistributedLock struct {
    redis *redis.Client
    key   string
    value string // Unique token to prevent accidental unlock
    ttl   time.Duration
}

func NewDistributedLock(redis *redis.Client, resource string, ttl time.Duration) *DistributedLock {
    return &DistributedLock{
        redis: redis,
        key:   "lock:" + resource,
        value: uuid.New().String(),
        ttl:   ttl,
    }
}

func (dl *DistributedLock) Acquire(ctx context.Context) (bool, error) {
    // SET key value NX EX ttl
    return dl.redis.SetNX(ctx, dl.key, dl.value, dl.ttl).Result()
}

func (dl *DistributedLock) Release(ctx context.Context) error {
    // Lua script ensures we only delete our own lock
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `
    return dl.redis.Eval(ctx, script, []string{dl.key}, dl.value).Err()
}

// Usage: Ensure only one worker processes a job
func ProcessJobExclusively(redis *redis.Client, jobID string) error {
    lock := NewDistributedLock(redis, "job:"+jobID, 30*time.Second)

    acquired, err := lock.Acquire(context.Background())
    if err != nil {
        return err
    }
    if !acquired {
        return errors.New("job already being processed")
    }
    defer lock.Release(context.Background())

    // Only one worker executes this
    return processJob(jobID)
}
```

---

## 12. Saga Pattern (Distributed Transaction)

**Pattern:** Coordinate multi-service transactions with compensating actions.

```go
package saga

import (
    "context"
    "fmt"
)

type BookingSaga struct {
    flightSvc *FlightService
    hotelSvc  *HotelService
    carSvc    *CarService
}

func (s *BookingSaga) BookTrip(ctx context.Context, req TripRequest) error {
    var flightID, hotelID string

    // Step 1: Book flight
    flightID, err := s.flightSvc.Book(ctx, req.FlightDetails)
    if err != nil {
        return fmt.Errorf("flight booking failed: %w", err)
    }

    // Step 2: Book hotel
    hotelID, err = s.hotelSvc.Book(ctx, req.HotelDetails)
    if err != nil {
        // Compensate: Cancel flight
        s.flightSvc.Cancel(ctx, flightID)
        return fmt.Errorf("hotel booking failed: %w", err)
    }

    // Step 3: Book car
    _, err = s.carSvc.Book(ctx, req.CarDetails)
    if err != nil {
        // Compensate: Cancel hotel and flight
        s.hotelSvc.Cancel(ctx, hotelID)
        s.flightSvc.Cancel(ctx, flightID)
        return fmt.Errorf("car booking failed: %w", err)
    }

    // All steps succeeded
    return nil
}

// In production, use orchestration frameworks like:
// - Temporal (temporal.io)
// - Cadence
// - Netflix Conductor
```

---

## Quick Reference: When to Use Each Pattern

```
Circuit Breaker:       Calling flaky external APIs (payments, partners)
Rate Limiter:          Public APIs, preventing abuse
Cache-Aside:           Read-heavy workloads (product catalogs, user profiles)
Idempotency Keys:      Financial transactions, order creation
Retry + Backoff:       Network calls, eventual consistency operations
Connection Pooling:    Database access (always use this)
Optimistic Locking:    Low-contention updates (content editing)
Consistent Hashing:    Distributed caches, WebSocket routing
Health Checks:         Kubernetes deployments (liveness + readiness)
JWT Middleware:        Stateless authentication
Distributed Lock:      Job processing, leader election
Saga Pattern:          Multi-service transactions (booking, checkout)
```

---

**Next Steps:**
1. Copy these examples into your codebase
2. Adjust configuration (timeouts, retries, TTLs) based on your SLOs
3. Add metrics/logging to each pattern
4. Write tests for failure scenarios

All examples are production-ready starting points. Adapt to your specific requirements.

