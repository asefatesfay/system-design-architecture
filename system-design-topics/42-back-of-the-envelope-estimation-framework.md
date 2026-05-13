# Back-of-the-Envelope Estimation for Senior and Staff Interviews

Most engineers know architecture patterns. The gap in interviews is turning rough numbers into concrete decisions:
- How many servers?
- How much DB storage?
- How much bandwidth?
- Can this fit in memory?
- Do we need cache, sharding, CDN, or multi-region?
- What breaks first?

The goal is not perfect math. The goal is engineering intuition.

---

## 1) Core Mindset

Convert product behavior into architecture decisions in this order:

Users -> Requests -> Data -> Bottleneck -> Design

Everything starts from:
- Users
- Requests
- Data size
- Time

---

## 2) Foundational Numbers to Memorize (Decimal First)

Use decimal units in interviews for speed unless explicitly asked for binary units.

Storage (quick mental math):
- 1 KB ~= 10^3 bytes
- 1 MB ~= 10^6 bytes
- 1 GB ~= 10^9 bytes
- 1 TB ~= 10^12 bytes
- 1 PB ~= 10^15 bytes

Human-size intuition:
- Small JSON response: ~1 KB
- Profile image: ~100 KB to 1 MB
- HD image: ~2 MB to 5 MB
- 1 minute HD video: ~50 MB to 100 MB

Network intuition:
- 1 Mbps ~= 125 KB/sec
- 100 Mbps ~= 12.5 MB/sec
- 1 Gbps ~= 125 MB/sec

PB-scale intuition:
- 1 PB/day ~= 11.6 GB/sec ~= 93 Gbps
- 10 PB/day ~= 116 GB/sec ~= 930 Gbps
- 100 PB/day ~= 1.16 TB/sec ~= 9.3 Tbps

Example:
- If response size is 100 KB and traffic is 10,000 requests/sec:
- Throughput = 100 KB x 10,000 = 1,000,000 KB/sec ~= 1 GB/sec

This is exactly why bandwidth becomes a first-order design constraint.

---

## 3) Most Important Formula

QPS (Queries Per Second):

QPS = Requests per day / 86,400

Where 86,400 is seconds in one day:
- 24 x 60 x 60 = 86,400

---

## 4) Example: Instagram Feed Traffic

Assume:
- 100M DAU
- 10 app opens per user per day
- 20 posts loaded per session

Requests/day:
- 100M x 10 x 20 = 20B/day

Average QPS:
- 20B / 86,400 ~= 231K QPS

Design consequence:
- Massive read scale
- Cache is mandatory
- CDN is mandatory
- Database cannot serve all traffic directly

---

## 5) Storage Estimation Example

Assume:
- Average photo size = 2 MB
- 100M uploads/day

Daily storage:
- 100M x 2 MB = 200 TB/day

Yearly storage:
- 200 TB/day x 365 ~= 73 PB/year

Design consequence:
- Object storage is mandatory
- Compression and lifecycle tiering are mandatory
- Replication and backup policy dominate cost

---

## 6) Memory vs Disk Intuition

Senior instinct:
- RAM is expensive and low-latency
- Disk is cheaper and high-capacity
- Network is often the practical bottleneck

Example: can all user profiles fit in cache?
- 50M active users
- 2 KB profile object
- Memory needed = 50M x 2 KB = 100 GB

Design consequence:
- Feasible in a distributed in-memory cache cluster

---

## 7) Latency Hierarchy You Should Know

- CPU cache: nanoseconds
- RAM: ~100 ns
- SSD: ~100 microseconds
- Network call: milliseconds
- Cross-region network: ~50 to 200 ms

Design consequence:
- Cache and batching reduce expensive network hops
- Chatty APIs hurt p95 latency
- Geo strategy must match latency SLOs

---

## 8) Design Decisions Estimation Should Drive

### A) Do we need caching?

Use cache when:
- Read-heavy workload
- Expensive or repeated queries
- Hot keys (timelines, profiles, catalog)

### B) SQL or NoSQL?

Prefer SQL when:
- Strong consistency and transactions matter
- Complex joins are required

Prefer NoSQL when:
- Very high write throughput
- Key-value/document access patterns dominate

### C) Do we need CDN?

If serving media or static assets at scale, yes.

### D) Do we need sharding?

Shard when:
- Data size exceeds single-node limits
- Write load exceeds single-node limits
- Hot partitions create saturation

---

## 9) Estimation Categories in Interviews

- Traffic: QPS/RPS
- Storage: TB and PB growth
- Memory: cache sizing
- Bandwidth: ingress and egress throughput
- Compute: server count and headroom
- Availability: replication and failover scope

---

## 10) Practical Mental Models

Peak traffic model:
- Peak QPS ~= 2x to 5x average QPS

Read-write patterns:
- Social feed systems are often read-heavy
- Messaging is more balanced
- Analytics pipelines are often write-heavy

Design consequence:
- Replica counts, cache strategy, and queue depth targets depend on read/write ratio

---

## 11) What Interviewers Actually Evaluate

Not arithmetic speed. They evaluate architectural consequence.

Example:
- If uploads are 200 TB/day and RF=3, replicated raw footprint is ~600 TB/day.
- Consequence: object storage tiers, compression, and retention policy are required from day one.

---

## 12) Daily 30-Minute Practice Loop

Pick one product:
- YouTube
- Uber
- Slack
- Figma
- Dropbox
- WhatsApp

Estimate:
- DAU
- Requests/day
- QPS
- Storage/day
- Cache size
- Bandwidth

Then ask:
- What breaks first?
- What must be distributed?
- What can stay centralized?

---

## 13) Recommended Learning Sequence

Phase 1:
- Internalize constants (86,400 sec/day, unit conversions, bandwidth, latency)

Phase 2:
- Practice estimation drills (URL shortener, Instagram, YouTube, Dropbox, WhatsApp)

Phase 3:
- Connect numbers to architecture
- Why cache?
- Why shard?
- Why async?
- Why CDN?
- Why event stream/object storage?

---

## 14) One Stuck-Proof Interview Framework

When stuck, always use:

Users -> Requests -> Data -> Bottleneck -> Design

Example:
- Users: 100M
- Requests: 20B/day
- Data: 200 TB/day uploads
- Bottleneck: bandwidth + storage growth
- Design: CDN + object storage + async processing

---

## Fast Interview Notes

- Use decimal units for quick estimates unless interviewer requests binary precision.
- Mention peak traffic explicitly.
- State one bottleneck and one concrete mitigation.
- End with one production metric you would track (p95 latency, cache hit rate, queue lag, saturation).

For a one-page revision version, see [52-back-of-the-envelope-estimation-cheat-sheet.md](52-back-of-the-envelope-estimation-cheat-sheet.md).

---

## 15) Six Interview Walkthroughs (Numbers -> Decisions)

Use this exact format for each prompt:
- Assumptions
- Quick math
- First bottleneck
- Design consequences
- One metric to watch

### A) YouTube

Assumptions:
- 300M DAU
- 30 min watch time per DAU per day
- Average stream rate: 2 Mbps
- 20M uploads/day, average 100 MB each

Quick math:
- Watch traffic per user/day = 2 Mbps x 1,800 sec = 3,600 Mb = 450 MB
- Total egress/day = 300M x 450 MB = 135 PB/day
- Upload ingress/day = 20M x 100 MB = 2 PB/day

First bottleneck:
- Global egress bandwidth and transcoding throughput

Design consequences:
- Multi-region CDN and edge caching are mandatory
- Asynchronous transcoding pipeline with queue-based load leveling
- Object storage with lifecycle tiers for old content

One metric to watch:
- CDN hit ratio and rebuffer rate

### B) Uber

Assumptions:
- 30M trips/day
- 40 trip lifecycle events/trip
- 1 KB/event
- Peak factor: 3x

Quick math:
- Events/day = 30M x 40 = 1.2B
- Average event QPS = 1.2B / 86,400 ~= 13.9K/sec
- Peak event QPS ~= 41.7K/sec
- Event payload/day ~= 1.2 TB/day (before replication/indexes)

First bottleneck:
- Regional hot partitions and dispatch latency

Design consequences:
- Partition by region/city and key by trip/driver/rider identifiers
- Event streaming backbone for decoupled consumers
- In-memory geospatial indexing for low-latency matching

One metric to watch:
- Dispatch p95 latency by city

### C) Slack

Assumptions:
- 50M DAU
- 40 messages/user/day
- 1 KB/message
- Effective fanout: 20 deliveries/message

Quick math:
- Messages/day = 50M x 40 = 2B
- Send QPS = 2B / 86,400 ~= 23.1K/sec
- Deliveries/day = 2B x 20 = 40B
- Delivery QPS = 40B / 86,400 ~= 463K/sec average

First bottleneck:
- Fanout and connection gateway pressure (not raw message storage)

Design consequences:
- WebSocket gateway tier with workspace/channel partitioning
- Asynchronous fanout workers and per-channel backpressure
- Cache-Aside for hot channel history windows

One metric to watch:
- End-to-end message delivery latency p95

### D) Figma

Assumptions:
- 10M concurrent users at peak
- 20% actively editing
- Delta stream: 300 bytes/sec/active editor
- Presence heartbeat: 100 bytes every 10 sec/user

Quick math:
- Active editors = 2M
- Delta ingress = 2M x 300 bytes/sec = 600 MB/sec
- Presence ingress = 10M x 10 bytes/sec = 100 MB/sec
- Total real-time ingress ~= 700 MB/sec (before protocol overhead)

First bottleneck:
- Real-time synchronization and broadcast path efficiency

Design consequences:
- Sticky sessions to collaboration servers
- Region-local editing with conflict-resolution model (CRDT/OT)
- Delta coalescing and throttling for cursor/presence chatter

One metric to watch:
- Sync convergence delay p95

### E) Dropbox

Assumptions:
- 200M DAU
- 2 file changes/user/day
- 8 MB average changed payload after chunking

Quick math:
- Changes/day = 200M x 2 = 400M
- Ingress/day = 400M x 8 MB = 3.2 PB/day (before dedup/compression)

First bottleneck:
- Storage cost growth and cross-device sync throughput

Design consequences:
- Content-addressable chunk storage
- Deduplication and compression in write path
- Resumable uploads plus lifecycle policies for colder objects

One metric to watch:
- Dedup ratio and sync completion time p95

### F) WhatsApp

Assumptions:
- 2B users
- 100B messages/day
- 0.5 KB/message
- Peak factor: 4x
- Effective fanout multiplier: 3x (groups + multi-device)

Quick math:
- Send QPS = 100B / 86,400 ~= 1.16M/sec average
- Peak send QPS ~= 4.63M/sec
- Raw payload/day = 100B x 0.5 KB = 50 TB/day
- Effective delivery operations/day ~= 300B

First bottleneck:
- Concurrent connection management and fanout/retry storms

Design consequences:
- Store-and-forward queues with idempotent delivery semantics
- Recipient-based partitioning and connection-aware routing
- Strict rate limiting and retry budgets to prevent storm amplification

One metric to watch:
- Queue lag and undelivered message age p95

---

## 16) Rehearsal Script (30 Seconds)

For any product, say:
- "I will estimate users, requests, and payload first."
- "I will compute average and peak QPS, then throughput and storage/day."
- "I will identify the first bottleneck."
- "I will pick the smallest architecture change that removes that bottleneck."
- "I will validate with one production metric."
