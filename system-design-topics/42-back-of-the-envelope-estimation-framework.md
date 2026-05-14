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

---

## 17) Complete Walkthrough: WhatsApp-Style Messaging (Real-World Interview Flow)

This section shows the full chain from assumptions to architecture decisions using:

Users -> Requests -> Data -> Bottleneck -> Design

Use this as a template for any other product.

### Step 0: Scope (what we are designing)

In scope (v1):
- 1:1 messaging
- Group messaging
- Online presence (last seen / online)
- Delivery states (sent, delivered, read)
- Multi-device login

Out of scope (v1):
- Voice/video calls
- Stories/status media pipeline
- Search over all historical messages

Why scope matters:
- It keeps assumptions realistic and prevents over-design.

### Step 1: Users

Assume:
- Registered users = 2B
- DAU = 800M
- Peak concurrent connected users = 120M
- Average messages sent per DAU/day = 60
- Peak factor = 4x average traffic

Immediate interpretation:
- This is a connection-heavy system, not just a storage system.
- We must plan both message throughput and persistent socket scale.

### Step 2: Requests

#### 2.1 Message send rate

Messages/day:
- 800M x 60 = 48B messages/day

Average send QPS:
- 48B / 86,400 ~= 556K sends/sec

Peak send QPS:
- 556K x 4 ~= 2.22M sends/sec

#### 2.2 Delivery fanout effect

Assume effective fanout multiplier = 2.5x
(mix of 1:1 chats, small groups, and multi-device delivery)

Effective delivery operations/day:
- 48B x 2.5 = 120B delivery ops/day

Average delivery ops/sec:
- 120B / 86,400 ~= 1.39M ops/sec

Peak delivery ops/sec:
- 1.39M x 4 ~= 5.56M ops/sec

#### 2.3 Presence heartbeat traffic

Assume:
- 120M concurrent users at peak
- Heartbeat every 30 seconds
- 150 bytes payload/heartbeat (compressed protocol)

Heartbeat requests/sec:
- 120M / 30 = 4M heartbeats/sec

Presence ingress bandwidth:
- 4M x 150 bytes = 600 MB/sec (protocol overhead not included)

Decision implication from requests:
- Presence and delivery traffic can exceed raw send traffic.
- We need protocol efficiency, connection gateways, and async fanout.

### Step 3: Data

#### 3.1 Message payload storage

Assume:
- Average stored message envelope = 700 bytes
(text + metadata + ids + timestamps; media stored separately)

Raw message data/day:
- 48B x 700 bytes = 33.6 TB/day

With replication factor (RF) = 3:
- 33.6 x 3 = 100.8 TB/day

Yearly replicated footprint (messages only):
- 100.8 x 365 ~= 36.8 PB/year

#### 3.2 Metadata and index overhead

Assume index + secondary metadata overhead = 1.5x base

Total effective yearly footprint:
- 36.8 PB x 1.5 ~= 55.2 PB/year

Decision implication from data:
- Storage growth is massive but predictable.
- We need partitioned storage, tiering, and retention controls.

### Step 4: Identify the first bottleneck

From steps 1-3, likely first bottlenecks are:
- Connection gateway saturation (millions of concurrent sockets)
- Fanout pipeline pressure (millions of delivery ops/sec at peak)
- Hot partitions for celebrity/group chats

Not the first bottleneck:
- Raw disk capacity (important, but scales more linearly)

Interview-quality statement:
- "The first system break is the real-time path (connections + fanout), not long-term storage."

### Step 5: Design (smallest changes that remove bottlenecks)

#### 5.1 Edge connection tier

Decision:
- Use regional WebSocket (or QUIC) gateway clusters behind anycast/global LB.
- Sticky routing by userId hash to reduce cross-node session lookups.

Why this follows from numbers:
- 120M concurrent users and high heartbeat rates require specialized stateful gateway fleets.

#### 5.2 Durable write path with idempotency

Decision:
- Client send -> API -> append to durable message log/queue -> ack as "sent".
- Use client-generated message IDs for idempotent retries.

Why:
- At 2.22M peak send QPS, retries and duplicate sends are guaranteed.
- Idempotency prevents retry storms from duplicating messages.

#### 5.3 Async fanout workers

Decision:
- Dedicated fanout consumers read from queue/log and route to recipient partitions.
- Separate send path from delivery path.

Why:
- Peak delivery ops (~5.56M/sec) is much higher than send ops.
- Async fanout smooths bursts and isolates failures.

#### 5.4 Recipient-based partitioning

Decision:
- Partition by recipientId (or conversationId for large groups) with regional affinity.

Why:
- Balances traffic and keeps reads/writes local.
- Avoids single hot node failures from uneven key distribution.

#### 5.5 Group chat hot-key mitigation

Decision:
- Split large-group fanout into shard batches.
- Rate-limit super-groups and apply per-group delivery budgets.

Why:
- One 500K-member group can create burst amplification.
- Controlled fanout protects tail latency for normal chats.

#### 5.6 Presence service separation

Decision:
- Keep presence in memory-first distributed store with aggressive TTL.
- Do not couple presence writes to durable message DB.

Why:
- Presence is ultra-high-write, low-value historical data.
- TTL state avoids expensive long-term storage and reduces write amplification.

#### 5.7 Storage architecture

Decision:
- Hot recent messages in low-latency KV/LSM store.
- Warm/cold history in cheaper object/archive tiers.
- Media in object storage + CDN, referenced by message metadata.

Why:
- 55+ PB/year trend requires lifecycle tiering from day one.

### Step 6: Reliability and failure behavior (real-world constraints)

Required behaviors:
- At-least-once delivery internally + idempotent clients for exactly-once user experience
- Per-recipient ordered delivery within conversation partition
- Backpressure when downstream is slow (queue depth thresholds)
- Circuit breakers around notification/presence dependencies

Why:
- These controls prevent cascading retry storms during partial outages.

### Step 7: Capacity sketch (how many servers, interview style)

Assume one gateway node safely supports:
- 150K concurrent sockets

Gateway nodes for 120M concurrent users:
- 120M / 150K = 800 nodes

With N+1 headroom and regional failover buffer (~2x):
- Plan ~1,600 gateway nodes globally

Assume one fanout worker handles 15K delivery ops/sec sustained.

Fanout workers for 5.56M peak ops/sec:
- 5.56M / 15K ~= 371 workers

With 50% headroom:
- Plan ~560 fanout workers

Why this matters:
- Converts abstract architecture into deployable capacity targets.

### Step 8: What to monitor (proof your design works)

Top production metrics:
- End-to-end delivery latency p95/p99
- Queue lag (fanout backlog age)
- Active socket count and gateway saturation
- Duplicate message rate (idempotency misses)
- Undelivered message age p95
- Hot-partition skew (top shard load / median shard load)

Alert examples:
- Queue lag > 5 sec for 10 min
- Gateway CPU > 75% and socket utilization > 85%
- Duplicate rate > baseline + 3 sigma

### Step 9: Final interview answer (30-second close)

"Given 800M DAU and 48B messages/day, average send load is ~556K/sec and peak is ~2.22M/sec. With fanout, peak delivery operations reach ~5.56M/sec, so the first bottleneck is real-time fanout and connection gateways, not raw storage. I would use regional sticky gateways, durable idempotent writes, async fanout workers, recipient-based partitioning, and a separate in-memory presence system with TTL. I would validate the design with delivery p95 latency, queue lag, and partition skew metrics."

### Step 10: Interview Checklist Answers (Directly from This Walkthrough)

How many servers?
- Gateway servers: ~1,600 globally (includes headroom and failover)
- Fanout workers: ~560
- Plus supporting control-plane services (auth, metadata, observability) sized separately

How much DB storage?
- Messages only: ~100.8 TB/day replicated (RF=3)
- Yearly messages + index overhead: ~55.2 PB/year
- Media is separate in object storage and typically dominates long-term bytes

How much bandwidth?
- Peak send path: ~2.22M sends/sec x ~1 KB envelope ~= ~2.2 GB/sec ingress before protocol overhead
- Peak presence path: ~600 MB/sec ingress from heartbeats
- Peak delivery path is operationally larger due to fanout; internal network fabric must handle multi-GB/sec east-west traffic

Can this fit in memory?
- Presence state: yes (TTL-based, memory-first distributed store)
- Entire message history: no (PB scale), so only hot windows and indexes stay in RAM/cache

Do we need cache, sharding, CDN, or multi-region?
- Cache: yes (presence, recent chats, hot metadata)
- Sharding: yes (recipient or conversation partitioning)
- CDN: yes for media attachments and static assets
- Multi-region: yes (latency + resilience + regulatory boundaries)

What breaks first?
- Real-time path first: connection gateways + fanout queues/workers
- Storage capacity growth is serious but is usually not the first outage trigger

### Reusable template you can copy in interviews

- Users: DAU, concurrent users, behavior frequency
- Requests: average and peak QPS for each traffic type
- Data: payload/day, RF-adjusted storage growth, retention effect
- Bottleneck: choose one first break point
- Design: smallest architecture changes that directly remove that bottleneck

---

## 18) Complete Walkthrough: Instagram-Style Feed (Read-Heavy Reality)

This walkthrough uses the same method:

Users -> Requests -> Data -> Bottleneck -> Design

The goal is to show how a read-heavy product leads to very different decisions than messaging.

### Step 0: Scope (what we are designing)

In scope (v1):
- Home feed generation and retrieval
- Photo/video post publishing
- Likes and comments counters
- Ranking service for feed order

Out of scope (v1):
- Stories/reels recommendation stack
- Ads auction system
- Full-text search across all captions/comments

Why scope matters:
- Feed architecture can be solved cleanly only when recommendation and ads are treated separately.

### Step 1: Users

Assume:
- DAU = 300M
- Peak concurrent users = 45M
- Feed opens per DAU/day = 8
- Posts loaded per feed open = 25
- New posts created/day = 120M
- Peak factor = 3x

Immediate interpretation:
- Reads are huge; writes are comparatively small.
- Primary risk is read amplification, not post creation throughput.

### Step 2: Requests

#### 2.1 Feed read volume

Feed item requests/day:
- 300M x 8 x 25 = 60B feed item reads/day

Average feed item QPS:
- 60B / 86,400 ~= 694K reads/sec

Peak feed item QPS:
- 694K x 3 ~= 2.08M reads/sec

#### 2.2 API request view (page-level)

Feed page requests/day:
- 300M x 8 = 2.4B page requests/day

Average page QPS:
- 2.4B / 86,400 ~= 27.8K req/sec

Peak page QPS:
- 27.8K x 3 ~= 83.4K req/sec

#### 2.3 Engagement writes

Assume:
- Likes/day = 10B
- Comments/day = 1B

Average engagement write QPS:
- (10B + 1B) / 86,400 ~= 127K writes/sec

Peak engagement write QPS:
- 127K x 3 ~= 381K writes/sec

Decision implication from requests:
- Feed reads dominate total traffic.
- If cache misses are high, databases and ranking services will collapse under peak load.

### Step 3: Data

#### 3.1 Post storage growth

Assume per new post:
- Media object average = 2.5 MB
- Metadata row = 2 KB

Daily media storage:
- 120M x 2.5 MB = 300 TB/day

Daily metadata storage:
- 120M x 2 KB ~= 240 GB/day

With RF=3 on metadata stores:
- 240 GB x 3 = 720 GB/day

Interpretation:
- Media dominates storage cost, metadata dominates query path behavior.

#### 3.2 Feed cache working set

Assume:
- Active hot users/day = 100M
- Cached feed state per hot user = 15 KB

Required cache memory:
- 100M x 15 KB = 1.5 TB

With 30% headroom:
- ~2 TB distributed RAM cluster

Decision implication from data:
- A distributed feed cache is feasible and mandatory.

### Step 4: Identify the first bottleneck

Likely first bottlenecks:
- Feed read amplification into ranking + metadata stores
- Hot-key celebrities causing cache churn and skew
- Fanout pressure at post-publish time for high-follower accounts

Not the first bottleneck:
- Raw media object storage capacity (it scales well with object storage)

Interview-quality statement:
- "For feed products, the first break is read amplification and hot-key skew, not media storage."

### Step 5: Design (smallest changes that remove bottlenecks)

#### 5.1 Multi-layer caching on read path

Decision:
- CDN for media and static assets
- Edge/API cache for feed page payload fragments
- Redis/Memcached cluster for personalized feed IDs and post metadata

Why this follows from numbers:
- 2.08M peak item reads/sec cannot hit primary databases directly.

#### 5.2 Hybrid fanout model (push + pull)

Decision:
- Fanout-on-write for normal users (precompute follower inbox entries)
- Fanout-on-read for celebrities (compute on demand)

Why:
- Full fanout-on-write explodes for accounts with tens of millions of followers.
- Hybrid policy prevents write storms while keeping most reads fast.

#### 5.3 Timeline/inbox storage partitioning

Decision:
- Partition inbox/timeline tables by userId hash + region.
- Keep recent window in hot storage; older entries in warm tier.

Why:
- Smooths read distribution and keeps p95 lookup latency low.

#### 5.4 Ranking decoupling with pre-ranking

Decision:
- Offline/nearline candidate generation + light online re-rank.
- Cache top-N candidate lists per user/session bucket.

Why:
- Running full ranking models synchronously for every request is too expensive at peak.

#### 5.5 Counter architecture (likes/comments)

Decision:
- Write-optimized counter ingestion via log/queue.
- Asynchronous aggregation and periodic materialization into read stores.

Why:
- 381K peak engagement writes/sec should not lock hot rows directly.

#### 5.6 Hot-key and celebrity isolation

Decision:
- Detect super-hot creators and route to dedicated partitions/queues.
- Apply per-key admission control and adaptive cache TTL.

Why:
- Prevents one viral account from degrading global tail latency.

### Step 6: Reliability and consistency choices (real-world)

Required behaviors:
- Eventual consistency for like/comment counters (seconds acceptable)
- Stronger consistency for post creation ownership and ACL checks
- Idempotent publish and engagement events
- Queue backpressure and replay for ranker/counter consumers

Why:
- This balances user experience and operational safety at scale.

### Step 7: Capacity sketch (interview-style rough sizing)

Assume one feed API node sustains:
- 4K page req/sec at target latency

Nodes for peak page QPS (83.4K):
- 83.4K / 4K ~= 21 nodes

With 2x safety + zonal failover:
- Plan ~45 to 50 feed API nodes

Assume one cache node reliably serves:
- 120K ops/sec at desired p95

Cache nodes for peak item reads (2.08M):
- 2.08M / 120K ~= 18 nodes

With headroom and rebalancing buffer:
- Plan ~30 cache nodes

Why this matters:
- It translates architecture into concrete capacity and cost conversations.

### Step 8: What to monitor (proof the design works)

Top production metrics:
- Feed API latency p95/p99
- Cache hit rate by layer (edge/API/data)
- Ranker timeout rate and fallback rate
- Timeline fanout queue lag
- Hot-key skew (top key QPS / median key QPS)
- Freshness lag (publish-to-feed visible delay)

Alert examples:
- Cache hit rate drops below 92% for 15 min
- Publish-to-feed lag p95 exceeds 10 sec
- Ranker fallback exceeds 5% of requests

### Step 9: Final interview answer (30-second close)

"With 300M DAU, 8 feed opens/day, and 25 items/open, we get about 60B feed item reads/day, or ~694K/sec average and ~2.08M/sec peak. That makes read amplification the first bottleneck, not post-write throughput. I would design a multi-layer cache, hybrid fanout-on-write and fanout-on-read, partitioned timeline storage, and decoupled ranking/counter pipelines. I would validate the design by tracking feed p95 latency, cache hit rates, fanout lag, and hot-key skew."

### Step 10: Interview Checklist Answers (Directly from This Walkthrough)

How many servers?
- Feed API nodes: ~45 to 50
- Cache nodes: ~30
- Additional ranking, fanout, and counter consumers depend on model complexity and SLA targets

How much DB storage?
- Media objects: ~300 TB/day (object storage)
- Feed metadata rows: ~240 GB/day raw, ~720 GB/day with RF=3
- Long-term storage dominated by media retention policy

How much bandwidth?
- Peak feed item delivery: ~2.08M items/sec x ~2 KB metadata+payload fragment ~= ~4.16 GB/sec from app/cache layers (media offloaded to CDN)
- Media egress is the larger cost/throughput driver and should be treated as CDN bandwidth, not origin DB bandwidth

Can this fit in memory?
- Feed hot working set: yes (~2 TB distributed RAM with headroom)
- Full historical feed for all users: no, must be tiered to warm/cold storage

Do we need cache, sharding, CDN, or multi-region?
- Cache: mandatory (multi-layer)
- Sharding: mandatory (timeline/inbox and metadata partitions)
- CDN: mandatory (media egress and edge locality)
- Multi-region: usually yes at this scale for latency, resilience, and compliance

What breaks first?
- Read amplification first: cache misses cascading into ranker + metadata stores
- Then hot-key/celebrity skew causing tail-latency spikes

### Reusable contrast note (Messaging vs Feed)

- Messaging first bottleneck: real-time connection + fanout reliability
- Feed first bottleneck: read amplification + cache effectiveness
- Messaging core metric: undelivered age / delivery latency
- Feed core metric: feed p95 latency / cache hit rate

---

## 19) Bandwidth vs Throughput: Rust-Proof Interview Guide

These are related but not identical.

Throughput:
- Work completed per second
- Examples: requests/sec, messages/sec, rows/sec

Bandwidth:
- Data volume transferred per second
- Examples: MB/sec, Gbps

Simple bridge equation:
- Bandwidth ~= Throughput x Average payload size

Example:
- 200K req/sec x 5 KB ~= 1,000,000 KB/sec ~= ~1 GB/sec

### What architecture choices affect throughput most?

- Async queues and batching
- Horizontal stateless service scaling
- Partitioning/sharding strategy
- DB write path design (append logs, idempotent upserts, bulk operations)
- Backpressure and retry budgets

If throughput is the limit, you usually add:
- Queues/streams
- More consumers/partitions
- Better write/read parallelism

### What architecture choices affect bandwidth most?

- Payload size (schema design, compression, field trimming)
- Response shape (avoid over-fetching, pagination)
- Caching and CDN offload ratio
- Replication topology (cross-region replication multiplies bandwidth)
- Fanout model (one write to many recipients increases total bytes moved)

If bandwidth is the limit, you usually add:
- Compression
- CDN/edge caching
- Smaller payload contracts
- Delta sync instead of full object sync

### Fast interview diagnosis

Symptoms of throughput bottleneck:
- Queue lag grows
- CPU and worker utilization saturate
- Request rates flatten despite demand increase

Symptoms of bandwidth bottleneck:
- Network egress/ingress caps out
- Packet drops/retransmits rise
- Latency spikes without CPU saturation

### Product-pattern intuition

- Messaging: throughput and fanout pipeline are often the first constraints
- Feed/video: bandwidth and cache hit rate dominate cost/performance
- Real-time collaboration: both matter; delta size control and sync fanout are key

### One-liner for interviews

"I first compute throughput (ops/sec), then convert to bandwidth using payload size. That tells me whether I should prioritize parallel processing capacity or byte-reduction and edge-offload architecture."
