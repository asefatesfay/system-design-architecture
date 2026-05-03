Architecture Overview — Collaborative Editor

Components:
- Client: browser/editor UI. Maintains local CRDT state, applies local edits immediately (optimistic), sends deltas to server over WebSocket.
- API Gateway / Auth: handles auth, TLS, routes to collaboration nodes; issues short-lived tokens for WebSocket connections.
- Collaboration Nodes (stateful): hold active in-memory CRDT for a set of documents (shard by document_id). Responsibilities:
  - Accept client connections and apply/validate deltas.
  - Merge remote deltas into in-memory CRDT and broadcast deltas to peers in the same room.
  - Persist periodic snapshots and append deltas to an operation log for replay.
- Presence Service (Redis pub/sub or in-node): tracks online users, cursors, selection ranges.
- Durable Storage:
  - Snapshots in object store (S3/GCS/MinIO).
  - Append-only operation log in Kafka/Redis Streams for replay, replication, and recovery.
  - Metadata and ACLs in Postgres.
- Background Workers: compaction, snapshotting, garbage collection of tombstones, analytics.

Flow (typical):
1. Client authenticates via HTTP, receives token.
2. Client opens WebSocket to gateway; gateway routes to a collaboration node for that `document_id`.
3. Client sends local edits as CRDT deltas. Node applies them locally, persists to op-log, broadcasts to room peers.
4. Other clients receive deltas, apply them locally; UI updates immediately.
5. Periodically, node writes a snapshot and truncates op-log segments up to snapshot.

Scaling and routing:
- Partition docs by `document_id` with consistent hashing. Keep collaboration nodes stateful and favor sticky routing for low-latency.
- Use a lightweight routing layer (Envoy/LB) that forwards by `document_id` header or a lookup service.
- For hot docs, use active-active replication across multiple nodes using CRDT deltas + durable log as source of truth.

Resilience:
- Rehydrate node state on failover from latest snapshot + replayed ops from op-log.
- Use leaderless CRDT merging to avoid global locks; accept eventual consistency guarantees with causal ordering for UX.
