# Back-of-the-Envelope Estimation Cheat Sheet

Use this when you have 5 to 10 minutes before an interview.

## 1) Core Flow

Users -> Requests -> Data -> Bottleneck -> Design

If you only remember one thing, remember this flow.

## 2) Must-Memorize Constants

Time:
- 1 day = 86,400 seconds

Storage (decimal):
- 1 KB = 10^3 bytes
- 1 MB = 10^6 bytes
- 1 GB = 10^9 bytes
- 1 TB = 10^12 bytes
- 1 PB = 10^15 bytes

Network:
- 1 Mbps = 125 KB/sec
- 100 Mbps = 12.5 MB/sec
- 1 Gbps = 125 MB/sec

PB/day intuition:
- 1 PB/day ~= 11.6 GB/sec ~= 93 Gbps
- 10 PB/day ~= 116 GB/sec ~= 930 Gbps
- 100 PB/day ~= 1.16 TB/sec ~= 9.3 Tbps

## 3) Core Formulas

QPS:
- QPS = requests/day / 86,400

Throughput:
- Ingress bytes/sec = write QPS x write size
- Egress bytes/sec = read QPS x read size

Storage growth:
- Raw/day = writes/day x bytes/write
- Replicated/day = raw/day x replication factor

Peak model:
- Peak QPS ~= 2x to 5x average QPS

## 4) Fast Size Intuition

- Small JSON: ~1 KB
- Profile object: ~1 to 2 KB
- Profile image: ~100 KB to 1 MB
- HD image: ~2 to 5 MB
- 1 minute HD video: ~50 to 100 MB

## 5) What Breaks First (Decision Triggers)

Bandwidth bottleneck:
- Choose CDN, compression, caching, edge serving

Read bottleneck:
- Choose cache, read replicas, materialized views

Write burst bottleneck:
- Choose queue, async workers, backpressure

Data growth bottleneck:
- Choose object storage tiers, partitioning, retention/lifecycle policy

Hot partition bottleneck:
- Choose sharding key redesign and load-aware routing

Connection bottleneck:
- Choose WebSocket gateway scaling, sticky sessions, fanout control

## 6) SQL vs NoSQL Shortcut

Prefer SQL when:
- Strong consistency and transactions are first-class
- Complex joins are core to product behavior

Prefer NoSQL when:
- Very high write throughput and key-based access dominate
- Flexible schema and horizontal partitioning are primary needs

## 7) 30-Second Script

- I will estimate users, requests, and payload size.
- I will compute average and peak QPS.
- I will convert to throughput and storage/day.
- I will name the first bottleneck.
- I will apply one architecture change to remove that bottleneck.
- I will validate with one production metric.

## 8) Six Product Prompts to Rehearse

- YouTube: egress and transcoding dominate -> CDN + async media pipeline
- Uber: regional hotspots dominate -> partition by city + streaming backbone
- Slack: fanout dominates -> WebSocket gateways + async fanout
- Figma: sync path dominates -> sticky sessions + CRDT/OT + delta coalescing
- Dropbox: storage growth dominates -> chunking + dedup + lifecycle tiers
- WhatsApp: connections and fanout dominate -> store-forward queues + idempotent delivery

## 9) Senior-Level Closing Lines

- The estimate does not need perfect precision; it must reveal the first bottleneck.
- I optimize architecture for the bottleneck first, then verify with metrics.
- If assumptions vary, I provide low/mid/high and verify the same design decision still holds.
