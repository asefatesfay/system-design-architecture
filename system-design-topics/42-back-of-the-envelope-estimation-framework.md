# Back-of-the-Envelope Estimation Framework for System Design Interviews

This is a reusable framework to estimate QPS, bandwidth, and storage, then turn those numbers into architecture decisions.

Use this for interview prompts such as:
- Design chat, feeds, uploads, search, or collaborative editing systems.
- Explain how storage and network grow at scale.
- Justify caching, queues, partitioning, and replication choices.

---

## One Framework, Every Time

1. Define scope and SLO
- Which operation are you sizing (for example: upload, feed read, message send)?
- What p95 latency and availability target apply?

2. Pick traffic assumptions
- Estimate DAU/MAU and derive average activity per user.
- Set peak factor (usually 2x to 5x average).

3. Estimate payload sizes
- Average write size and average read response size.
- Include protocol/index/metadata overhead as a multiplier in later passes.

4. Compute throughput
- Average QPS = total requests/day / 86,400.
- Peak QPS = average QPS x peak factor.
- Ingress = write QPS x write size.
- Egress = read QPS x read size.

5. Compute storage growth
- Daily raw storage = writes/day x bytes/write.
- Durable storage = daily raw x replication factor.
- Monthly/yearly growth from daily baseline.

6. Derive architecture decision
- Read-heavy + repeated keys: cache/CDN.
- Burst writes beyond worker capacity: queue + competing consumers.
- Hot partitions or fast index growth: sharding + lifecycle policies.

7. Sanity check
- Compare against known system scales.
- Revisit one or two assumptions once (not endlessly).

---

## Core Storage and Bandwidth Basics

- 1 KB x 1M requests/day is about 1 GB/day.
- 100 MB/sec is about 0.8 Gbps.
- Replication factor 3 roughly triples raw data before index/backup overhead.
- First-pass total footprint is often 2x to 4x raw payload when including replication, indexes, and metadata.

Useful conversions:
- 1 MB = 1,024 KB
- 1 GB = 1,024 MB
- 1 Gbps = 125 MB/sec

---

## Worked Examples (Popular App Contexts)

These are intentionally rough so you can do them fast in interviews.

### 1) YouTube-like Upload Metadata Pipeline

Assumptions:
- 20M uploads/day
- Metadata event size: 8 KB
- Peak factor: 4x
- Replication factor: 3

Estimate:
- Average write QPS = 20,000,000 / 86,400 = ~231/sec
- Peak write QPS = ~924/sec
- Peak ingress = 924 x 8 KB = ~7.4 MB/sec
- Daily raw storage = 20M x 8 KB = ~160 GB/day
- Durable storage (RF=3) = ~480 GB/day

Design decision:
- Queue-Based Load Leveling + Competing Consumers for bursts.
- Claim Check if event payloads become too large for the bus.

### 2) Discord/Slack-like Message History Reads

Assumptions:
- 80M DAU
- 30 channel/thread reads per user per day
- 25 KB per read response
- Peak factor: 3x

Estimate:
- Reads/day = 80M x 30 = 2.4B/day
- Average read QPS = ~27,778/sec
- Peak read QPS = ~83,334/sec
- Peak egress = 83,334 x 25 KB = ~2.08 GB/sec

Design decision:
- Cache-Aside for hot channels/threads.
- Gateway Aggregation or BFF to reduce chatty client behavior.

### 3) Uber-like Trip Event Stream

Assumptions:
- 100M trips/day
- 40 events/trip
- Event size: 1.2 KB
- Peak factor: 2.5x

Estimate:
- Events/day = 4B
- Average event QPS = ~46,296/sec
- Peak event QPS = ~115,740/sec
- Peak ingress = ~139 MB/sec
- Daily raw stream volume = ~4.8 TB/day

Design decision:
- Pub/Sub with partitioning by region or trip_id.
- Materialized views for timeline queries.

### 4) Amazon/Shopify-like Product Detail Service

Assumptions:
- 250M reads/day
- 90% cache hits at 12 KB, 10% origin at 40 KB
- Peak factor: 3x

Estimate:
- Average QPS = ~2,893/sec
- Peak QPS = ~8,679/sec
- Weighted response size = 14.8 KB
- Peak egress = ~128 MB/sec

Design decision:
- Cache-Aside + CDN.
- If misses are expensive, add read-optimized projections/materialized views.

### 5) Figma-like Real-Time Collaboration

Assumptions:
- 10M concurrent users at peak
- Presence heartbeat: 100 bytes every 10 sec
- 20% actively editing
- Active editor delta stream: 400 bytes/sec/user

Estimate:
- Heartbeat ingress = 100 MB/sec
- Active editors = 2M
- Delta traffic = 800 MB/sec
- Total real-time ingress = ~900 MB/sec

Design decision:
- WebSocket gateways with sticky routing and backpressure.
- Regional deployment with active-active strategy for low latency.

---

## 60-Second Interview Script

1. State assumptions and keep them round.
2. Compute average and peak QPS.
3. Convert to bytes/sec for ingress and egress.
4. Estimate storage/day and apply replication.
5. Name the bottleneck and map it to 2 to 3 design choices.
6. Close with one metric to validate (cache hit rate, queue lag, p95 latency, dropped sessions).

If assumptions are uncertain, present low/mid/high ranges and show your decision still stands.
