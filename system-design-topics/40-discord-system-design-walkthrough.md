# System Design Walkthrough — Discord (Real-Time Chat & Voice)

> Language-agnostic. Focus is on architecture, data flow, and trade-offs.

---

## The Question

> "Design a real-time messaging and voice platform like Discord. Users join servers with channels, send messages, and participate in voice/video calls."

---

## Core Insight

Discord is architecturally different from WhatsApp in one critical way: **messages are stored permanently server-side and are the source of truth**. Unlike WhatsApp (delete after delivery), Discord is a persistent chat history platform. This changes the storage model entirely.

The hard problems:
1. **Message fan-out to server members** — a Discord server can have 500K members. When someone posts in a channel, who gets notified?
2. **Voice/video at scale** — real-time audio/video requires fundamentally different infrastructure than text (WebRTC, media servers, UDP)
3. **Presence at scale** — showing online/offline status for millions of users across thousands of servers

---

## Step 1 — Requirements

### Functional
- Text channels: send/receive messages, persistent history
- Voice channels: join/leave, real-time audio
- Video: screen share, camera
- Servers (guilds) with multiple channels
- Direct messages between users
- Roles and permissions per server
- Reactions, threads, file attachments
- Push notifications for mentions

### Non-Functional

| Attribute | Target |
|-----------|--------|
| Registered users | 500M |
| Concurrent users | 19M |
| Messages/day | 4B |
| Concurrent voice users | 8M |
| Message delivery latency | < 100ms |
| Message history | Permanent (never deleted by default) |
| Availability | 99.99% |

---

## Step 2 — Estimates

```
Messages:
  4B/day → ~46,000/s
  Average message: 500 bytes
  46K × 500B = 23 MB/s write ingress

Message storage (permanent):
  4B/day × 500B = 2 TB/day
  5 years: ~3.6 PB total
  → Cassandra (time-series, append-only, scales to PB)

Voice:
  8M concurrent voice users
  Opus codec: ~32 Kbps per stream
  8M × 32 Kbps = 256 Gbps audio bandwidth
  → Requires dedicated media servers (WebRTC SFU)

Presence:
  19M concurrent users × presence updates every 30s = ~633K updates/s
  → Must be handled in-memory, never touch the DB
```

---

## Step 3 — High-Level Design

```mermaid
graph TD
    Client["Discord Client\n(desktop/mobile/web)"]
    GW["Gateway Service\n(WebSocket)\npersistent connection\nper client"]
    API["REST API\n(message history,\nserver management)"]
    MsgSvc["Message Service"]
    PresenceSvc["Presence Service\n(Redis)"]
    VoiceSvc["Voice Service\n(WebRTC SFU)"]
    MsgDB["Message Store\n(Cassandra)\npermanent history"]
    ServerDB["Server/Channel DB\n(Postgres)\nmetadata, permissions"]
    Cache["Cache\n(Redis)\nhot messages,\npresence state"]
    MQ["Message Queue\n(Kafka)\nfan-out events"]
    FanOut["Fan-out Workers"]
    Push["Push Notification\nService"]

    Client -->|"WSS persistent"| GW
    Client -->|"HTTPS"| API
    GW --> MsgSvc --> MsgDB
    MsgSvc --> MQ --> FanOut --> GW
    GW --> PresenceSvc --> Cache
    Client -->|"WebRTC"| VoiceSvc
    API --> ServerDB
    FanOut --> Push
```

### Happy Path — User Sends a Message

```mermaid
sequenceDiagram
    participant U as User (Alice)
    participant GW_A as Gateway (Alice's node)
    participant MS as Message Service
    participant DB as Cassandra
    participant MQ as Kafka
    participant FO as Fan-out Worker
    participant GW_B as Gateway (Bob's node)
    participant B as Bob

    U->>GW_A: WS: {type:"MESSAGE_CREATE", channel_id, content}
    GW_A->>MS: Store message
    MS->>DB: INSERT message (channel_id, message_id, user_id, content)
    MS-->>GW_A: {message_id} ✓
    GW_A-->>U: Message confirmed
    MS->>MQ: Publish {channel_id, message_id, guild_id}
    MQ->>FO: Fan-out worker
    FO->>FO: Get all online members of channel
    FO->>GW_B: Dispatch MESSAGE_CREATE event to Bob's gateway
    GW_B->>B: Push message over WebSocket
```

---

## Step 4 — Detailed Design

### 4.1 Message Storage — Cassandra Schema

Discord famously migrated from MongoDB to Cassandra, then from Cassandra to ScyllaDB (a Cassandra-compatible engine written in C++). The schema:

```
messages table:
  Partition key: (channel_id, bucket)
    bucket = floor(message_id / BUCKET_SIZE)
    → Prevents hot partitions from unbounded growth
  Clustering key: message_id DESC
  Columns: author_id, content, attachments, reactions, edited_at, deleted

Why bucket?
  A channel with 10 years of messages would be one huge partition.
  Bucketing by time range (e.g., 10-day buckets) keeps partitions bounded.
  "Load messages before cursor X" = query one or two buckets.
```

### 4.2 Fan-out — Server Members vs. Online Members

Discord servers can have 500K members. Fan-out to all 500K on every message would be catastrophic. The key insight: **only fan-out to online members**.

```mermaid
flowchart TD
    Message["New message in channel"]
    GetMembers["Get channel members\nwith permissions"]
    FilterOnline["Filter: only members\ncurrently online\n(check presence service)"]
    Dispatch["Dispatch to each\nonline member's\ngateway node"]
    Queue["Queue push notification\nfor offline members\nwho have notifications enabled"]

    Message --> GetMembers --> FilterOnline --> Dispatch
    FilterOnline --> Queue
```

For very large servers (100K+ members), Discord uses a different model: members "subscribe" to channels they're actively viewing. Fan-out only goes to subscribed members, not all server members.

### 4.3 Voice — WebRTC and Selective Forwarding Units (SFU)

Voice is fundamentally different from text. It requires:
- **UDP** (not TCP) — latency matters more than reliability; a dropped audio packet is better than a delayed one
- **Real-time encoding** — Opus codec, 20ms frames
- **Media servers** — clients can't send audio directly to each other (NAT, firewall); a server relays the streams

```mermaid
graph TD
    A["Alice\n(sends audio stream)"]
    B["Bob\n(receives Alice's stream)"]
    C["Carol\n(receives Alice's stream)"]
    SFU["SFU\n(Selective Forwarding Unit)\nReceives one stream from Alice\nForwards to Bob and Carol\nDoes NOT decode/re-encode"]

    A -->|"UDP/WebRTC"| SFU
    SFU -->|"UDP/WebRTC"| B
    SFU -->|"UDP/WebRTC"| C
```

**SFU vs. MCU (Multipoint Control Unit):**
- MCU: decodes all streams, mixes them, re-encodes → high CPU, low bandwidth for clients
- SFU: forwards raw encoded streams → low CPU, higher bandwidth for clients (each client receives N streams)
- Discord uses SFU — better for voice channels where participants take turns speaking

### 4.4 Presence System

```mermaid
flowchart LR
    Connect["User connects\nWebSocket"]
    Register["Register presence:\nRedis HSET presence:{user_id}\nstatus=online\ngateway_node=X"]
    Heartbeat["Client sends heartbeat\nevery 30s"]
    TTL["Redis TTL: 45s\n(expires if no heartbeat)"]
    Broadcast["Broadcast status change\nto mutual friends\nand shared servers"]

    Connect --> Register --> Heartbeat --> TTL
    Register --> Broadcast
```

Presence is stored in Redis with a TTL. If a client disconnects without sending an explicit "offline" event (e.g., phone dies), the TTL expires and the user appears offline automatically.

---

## Step 5 — Decision Log

| Decision | Options | Choice | Rationale |
|----------|---------|--------|-----------|
| Message storage | MongoDB / Cassandra / ScyllaDB | ScyllaDB (Cassandra-compatible) | Time-series append; PB scale; Discord migrated for better performance |
| Fan-out scope | All members / Online only | Online members only | 500K member servers make full fan-out impossible |
| Voice architecture | P2P / MCU / SFU | SFU | Better CPU efficiency than MCU; acceptable bandwidth for typical voice channels |
| Message history | Delete after delivery / Permanent | Permanent | Discord is a community platform; history is a core feature |
| Gateway connections | HTTP polling / WebSocket | WebSocket | Persistent connection for real-time push; Discord's gateway is the core of the product |

---

## Step 6 — Bottlenecks

| Bottleneck | Mitigation |
|------------|-----------|
| Large server fan-out (500K members) | Fan-out to online members only; subscription model for active channel viewers |
| Voice server capacity | SFU servers are stateless per session; scale horizontally; route to nearest region |
| Message history reads (load 50 messages) | Cassandra partition scan is fast; hot channels cached in Redis |
| Presence at 19M concurrent users | Redis cluster; presence updates batched; eventual consistency (1-2s lag is fine) |
| Attachment storage | S3 + CDN; virus scanning before serving; per-user upload quota |
