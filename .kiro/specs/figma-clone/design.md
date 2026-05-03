# Design Document — Figma Clone (Collaborative Editing)

## Overview

This document describes the technical architecture for a Figma-like collaborative design tool. The design prioritizes real-time multi-user editing correctness, low-latency synchronization, and horizontal scalability. The core insight is that collaborative editing is a distributed systems problem first and a UI problem second — the data model and sync protocol must be correct before the canvas rendering matters.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Clients (Browser)                          │
│  Canvas Renderer │ CRDT Engine (Yjs) │ Presence UI │ Asset Uploader │
└────────────────────────────┬────────────────────────────────────────┘
                             │  HTTPS / WSS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway / LB                            │
│   TLS Termination │ JWT Validation │ WS Routing (consistent hash)   │
└──────┬──────────────────────┬───────────────────────────────────────┘
       │ REST                 │ WebSocket (sticky by document_id)
       ▼                      ▼
┌─────────────┐    ┌──────────────────────────────────────────────┐
│  Auth       │    │         Collaboration Node Pool               │
│  Service    │    │  Node A          Node B          Node C       │
│  (stateless)│    │  [Doc 1,2,3]     [Doc 4,5]       [Doc 6,7]   │
└──────┬──────┘    │  CRDT in-mem     CRDT in-mem     CRDT in-mem  │
       │           └──────┬───────────────────────────────────────┘
       │                  │ pub/sub (cross-node presence)
       ▼                  ▼
┌─────────────┐    ┌──────────────────────────────────────────────┐
│  Metadata   │    │              Redis Cluster                    │
│  DB         │    │  Presence state │ Session routing map         │
│  (Postgres) │    │  Rate limit counters │ Ephemeral pub/sub      │
└─────────────┘    └──────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Op-Log (Kafka)      │
              │  Partitioned by       │
              │  document_id          │
              └──────────┬────────────┘
                         │
              ┌──────────▼────────────┐
              │  Compaction Workers   │
              │  (background jobs)    │
              └──────────┬────────────┘
                         │
              ┌──────────▼────────────┐
              │   Asset Store (S3)    │
              │  Snapshots + Images   │
              │  served via CDN       │
              └───────────────────────┘
```

---

## Component Design

### 1. Client Architecture

The browser client is a single-page application built with React + TypeScript. The canvas is rendered using a retained-mode scene graph on top of a `<canvas>` element (not SVG, for performance at scale).

**Key modules:**

- `CanvasRenderer` — scene graph, hit testing, viewport transforms, 60fps render loop via `requestAnimationFrame`.
- `CRDTEngine` — wraps Yjs `Y.Doc`. Owns the authoritative local document state. All mutations go through here.
- `SyncProvider` — manages the WebSocket connection, sends Yjs update deltas, applies incoming deltas to `CRDTEngine`.
- `PresenceManager` — sends cursor/selection awareness updates, renders remote cursors.
- `OfflineQueue` — persists unsynced Yjs updates to IndexedDB; drains on reconnect.
- `AssetUploader` — handles multipart upload to the REST API, returns stable CDN URLs.

**Data flow (local edit):**
```
User interaction
  → CanvasRenderer (hit test, compute transform)
  → CRDTEngine.applyLocal(op)   ← optimistic render happens here
  → SyncProvider.send(delta)
  → Collaboration Node
  → ack received → mark op as confirmed
```

**Data flow (remote edit):**
```
Collaboration Node → SyncProvider.receive(delta)
  → CRDTEngine.applyRemote(delta)
  → CanvasRenderer.invalidate(affectedLayers)
  → next rAF tick → re-render
```

---

### 2. API Gateway

A stateless reverse proxy (Nginx or Envoy) that:

- Terminates TLS.
- Validates JWT on every WebSocket upgrade request (checks signature, expiry, `doc:read`/`doc:write` scopes).
- Routes WebSocket connections to the correct Collaboration Node using consistent hashing on `document_id`. The hash ring is stored in Redis so all gateway instances share the same routing table.
- Proxies REST calls to Auth Service and Metadata API.
- Enforces per-client rate limits (stored in Redis) to prevent message flooding.

**Routing table update:** When a Collaboration Node joins or leaves the cluster, it updates its slot ownership in Redis. The gateway reads this on each new connection (cached with a 1s TTL).

---

### 3. Collaboration Node

The most complex component. Each node is a stateful Go (or Node.js) process that:

- Maintains an in-memory `Y.Doc` (Yjs document) per active Document.
- Manages a set of WebSocket connections (the Room) per Document.
- Persists Operations to Kafka before broadcasting.
- Periodically triggers Snapshots.

**Per-document in-memory state:**
```
DocumentRoom {
  doc_id:       string
  ydoc:         Y.Doc          // Yjs CRDT instance
  sessions:     Map<client_id, WebSocket>
  last_seq:     int64          // last persisted op sequence
  snapshot_seq: int64          // sequence of last snapshot
  dirty_ops:    int            // ops since last snapshot
}
```

**Operation handling (per incoming delta):**
```
1. Deserialize Yjs binary update from WebSocket frame
2. Validate JWT scope (doc:write)
3. Apply update to ydoc (Yjs handles CRDT merge)
4. Produce message to Kafka topic `ops.{document_id}` (key = document_id)
5. Wait for Kafka ack (or fire-and-forget for low-latency mode)
6. Broadcast binary update to all other sessions in Room
7. Send `ack` message back to originating client
```

**Snapshot trigger:** After every 500 ops or 5 minutes, the node serializes `Y.encodeStateAsUpdate(ydoc)` and writes it to S3 with key `snapshots/{doc_id}/{seq}.bin`. It then commits the snapshot sequence to Postgres.

**Node startup / rehydration:**
```
1. Load latest snapshot from S3 (keyed by doc_id)
2. Apply snapshot to fresh Y.Doc
3. Replay Kafka messages from snapshot_seq to latest offset
4. Mark node as ready, begin accepting connections
```

---

### 4. CRDT Data Model (Yjs)

Yjs is used as the CRDT engine. The Document is modeled as a `Y.Map` at the top level:

```
Y.Doc
└── Y.Map("document")
    ├── "meta"     → Y.Map  { name, created_at, owner_id }
    ├── "frames"   → Y.Array of frame_ids (ordered)
    └── "layers"   → Y.Map<layer_id, Y.Map>
                         ├── "type"       → string
                         ├── "frame_id"   → string
                         ├── "z_index"    → string (fractional index)
                         ├── "transform"  → Y.Map { x, y, w, h, rotation }
                         ├── "style"      → Y.Map { fill, stroke, opacity, ... }
                         ├── "text"       → Y.Text  (for text layers)
                         ├── "deleted"    → boolean (tombstone flag)
                         └── "asset_url"  → string (for image layers)
```

**Why Y.Map for layers instead of Y.Array:** Maps give O(1) lookup by `layer_id` and allow independent property updates without conflicts. Z-ordering is handled separately via fractional indexing strings stored in `z_index`, which sort lexicographically and can always be bisected to insert between any two existing values.

**Fractional indexing for z-order:** When inserting a layer between z-index `"a"` and `"b"`, the new index is the lexicographic midpoint (e.g., `"am"`). This is conflict-free because two concurrent inserts at the same position produce two distinct keys that both survive and sort deterministically.

**Text layers:** `Y.Text` is a sequence CRDT that handles character-level concurrent edits (insertions, deletions) with correct merge semantics — essential for collaborative text editing within a design element.

---

### 5. Sync Protocol

Transport: WebSocket (binary frames, MessagePack or raw Yjs binary encoding).

**Message envelope:**
```json
{
  "type": "delta | ack | presence | snapshot_request | snapshot_response | error",
  "doc_id": "<uuid>",
  "client_id": "<uuid>",
  "payload": "<base64 binary or JSON object>"
}
```

**Connection lifecycle:**
```
Client                          Collaboration Node
  |                                     |
  |-- HTTP GET /ws?doc_id=X&token=JWT ->|
  |                                     | validate JWT
  |<-- 101 Switching Protocols ---------|
  |                                     |
  |-- { type: "join", since_seq: N } -->| send snapshot if N is stale
  |<-- { type: "snapshot", data: ... }--|
  |<-- { type: "delta", ... } ----------| replay ops since snapshot
  |                                     |
  |-- { type: "delta", ops: [...] } --->| apply + persist + broadcast
  |<-- { type: "ack", op_id: "..." } ---|
  |                                     |
  |-- { type: "presence", cursor: {} } >| broadcast to room (no persist)
  |                                     |
  |-- { type: "ping" } ---------------->|
  |<-- { type: "pong" } ----------------|
```

**Reconnection:** On reconnect, the client sends `since_seq: N` where N is the last confirmed sequence number stored in IndexedDB. If `N >= snapshot_seq`, the node replays only the delta ops. If `N < snapshot_seq`, the node sends the full snapshot first.

---

### 6. Presence Service

Presence is ephemeral and does not go through the Op_Log. It is handled entirely in-memory:

- Within a single Collaboration Node, presence broadcasts are direct in-process fan-out to all sessions in the Room.
- Across nodes (if a Document is ever split across nodes, or for cross-document team presence), Redis Pub/Sub is used. Each node subscribes to `presence.{doc_id}` and publishes cursor updates there.

**Presence payload:**
```json
{
  "user_id": "...",
  "display_name": "Alice",
  "color": "#FF6B6B",
  "cursor": { "x": 340.5, "y": 210.0 },
  "selection": ["layer_id_1", "layer_id_2"]
}
```

Presence updates are throttled client-side to 30 per second (one per frame) and server-side to prevent flooding.

---

### 7. Op-Log (Kafka)

Each Kafka topic is `ops.{document_id}`, partitioned by `document_id` (single partition per document to preserve ordering). Retention is set to 30 days.

**Message schema:**
```json
{
  "seq":       1042,
  "op_id":     "uuid",
  "doc_id":    "uuid",
  "client_id": "uuid",
  "timestamp": "ISO8601",
  "update":    "<base64 Yjs binary update>"
}
```

The Collaboration Node is both producer (on write) and consumer (on rehydration). Kafka's log compaction is not used here — the Compaction_Worker handles state compaction at the application level via Snapshots.

---

### 8. Compaction Worker

A background service (separate process, horizontally scalable) that:

1. Polls Postgres for Documents where `ops_since_snapshot > 500` or `last_snapshot_at < now() - 5min`.
2. Fetches the latest Snapshot from S3.
3. Replays Kafka ops since the snapshot to build the latest state.
4. Serializes the new Snapshot and writes to S3.
5. Updates `snapshot_seq` and `last_snapshot_at` in Postgres.
6. Optionally triggers Kafka log segment deletion for offsets before the new snapshot.

This is decoupled from the Collaboration Node to avoid blocking the hot path.

---

### 9. Metadata DB Schema (Postgres)

```sql
-- Users
CREATE TABLE users (
  user_id     UUID PRIMARY KEY,
  email       TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- Teams
CREATE TABLE teams (
  team_id     UUID PRIMARY KEY,
  name        TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- Team membership
CREATE TABLE team_members (
  team_id     UUID REFERENCES teams(team_id),
  user_id     UUID REFERENCES users(user_id),
  role        TEXT NOT NULL CHECK (role IN ('owner','editor','viewer')),
  PRIMARY KEY (team_id, user_id)
);

-- Documents
CREATE TABLE documents (
  document_id   UUID PRIMARY KEY,
  team_id       UUID REFERENCES teams(team_id),
  owner_id      UUID REFERENCES users(user_id),
  name          TEXT NOT NULL,
  is_deleted    BOOLEAN DEFAULT false,
  snapshot_seq  BIGINT DEFAULT 0,
  last_snapshot_at TIMESTAMPTZ,
  ops_since_snapshot INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

-- Per-document ACL overrides (beyond team role)
CREATE TABLE document_acl (
  document_id UUID REFERENCES documents(document_id),
  user_id     UUID REFERENCES users(user_id),
  permission  TEXT NOT NULL CHECK (permission IN ('read','write','admin')),
  PRIMARY KEY (document_id, user_id)
);
```

---

### 10. Asset Store

Images and Snapshots are stored in S3-compatible object storage.

**Key structure:**
```
snapshots/{document_id}/{seq}.bin       ← Yjs state snapshots
assets/{team_id}/{asset_id}.{ext}       ← uploaded images
```

Assets are served via CloudFront (or equivalent CDN) with a 24-hour cache TTL. Snapshot reads bypass the CDN (internal S3 access only).

**Upload flow:**
```
Client → POST /api/assets (multipart)
  → API Gateway validates file type + size
  → Stores in S3 under assets/{team_id}/{uuid}.{ext}
  → Returns { asset_url: "https://cdn.example.com/assets/..." }
Client embeds asset_url in Layer properties via CRDT op
```

---

### 11. Scalability Design

**Horizontal scaling of Collaboration Nodes:**

Consistent hashing on `document_id` maps each document to a node. The hash ring is stored in Redis (using a sorted set). When a new node joins:
1. It registers its node_id and capacity in Redis.
2. The ring rebalances: a subset of document slots are reassigned to the new node.
3. For each reassigned document, the new node rehydrates from S3 + Kafka before the old node closes those sessions (graceful handoff with a 5-second overlap window).

**Hot document handling:**

For documents with >100 concurrent sessions, a single node may become a bottleneck. Mitigation:
- The Collaboration Node fans out broadcasts using worker goroutines (one per session) to parallelize WebSocket writes.
- For extreme cases (viral documents), an active-active multi-node approach can be used: multiple nodes each hold a replica of the Yjs doc and exchange deltas via Kafka. This is complex and only activated above a threshold.

**Database scaling:**

- Postgres uses read replicas for all SELECT queries (document listing, ACL checks).
- Writes (document create/update, snapshot metadata) go to the primary.
- Connection pooling via PgBouncer.

---

### 12. Security Design

- All traffic over TLS 1.3.
- JWTs signed with RS256 (asymmetric), public keys distributed to all services.
- JWT expiry: 1 hour. Refresh tokens: 30 days, stored in HttpOnly cookies.
- WebSocket messages validated for JWT scope on every operation (not just at connection time).
- Asset uploads: MIME type validated server-side (not just by extension). SVG files are sanitized to remove embedded scripts.
- Rate limiting: 100 ops/second per client, 1000 presence updates/second per room.
- CORS: restricted to known frontend origins.

---

### 13. Correctness Properties

These are the key invariants the system must maintain, derived from the acceptance criteria:

1. **Convergence**: For all valid sequences of Operations O₁...Oₙ applied in any order across all Clients, the final Document state is identical on all Clients.
2. **Causal consistency**: If Operation A causally precedes Operation B (B's Vector_Clock includes A), then A is always applied before B on every Client.
3. **No data loss on ack**: If the Collaboration Node sends an `ack` for an Operation, that Operation is durable in the Op_Log and will survive node failure.
4. **Idempotent delivery**: Applying the same Yjs update delta multiple times produces the same result as applying it once (Yjs guarantees this natively).
5. **Presence isolation**: Presence updates never affect Document state. A presence broadcast failure must not cause a Document state inconsistency.
6. **Round-trip snapshot fidelity**: `decode(encode(ydoc_state)) == ydoc_state` — serializing and deserializing a Snapshot produces an equivalent document.
