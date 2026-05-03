Sync Protocol — messages and workflows

Overview
- Transport: WebSocket for low-latency bidirectional messages. Optional WebRTC/DataChannel for P2P in restricted topologies.
- Auth: short-lived JWT bearer token obtained from HTTP auth endpoint; gateway validates before upgrading to WS.

Message types (JSON-over-WS)
- `join` — client joins a document room
  - { "type": "join", "document_id": "<id>", "client_id": "<cid>", "cursor": {"pos":123} }
- `delta` — CRDT delta payload
  - { "type": "delta", "document_id": "<id>", "client_id": "<cid>", "ops": [...], "clock": {"lamport": 42} }
- `ack` — acknowledgement of persisted op
  - { "type": "ack", "op_id": "<uuid>", "persisted_at": "iso" }
- `presence` — cursor/selection/presence broadcast
  - { "type": "presence", "client_id": "<cid>", "cursor": {"pos": 12, "sel": [10,14]} }
- `snapshot_request` / `snapshot_response` — request or return a full checkpoint

Reliability & Ordering
- Clients send deltas with causal metadata (vectors/clocks). Collaboration nodes enforce causal application locally and broadcast deltas in causal order.
- Server persists op to append-log before broadcasting to reduce data loss window (ack on durable write). For ultra-low-latency, broadcast pre-persist with eventual ack.

Conflict-Free Guarantees
- CRDT deltas are commutative, associative, and idempotent — server applies and rebroadcasts them as-is. Clients merge incoming deltas into local state.

Heartbeat and reconnection
- `ping`/`pong` keepalive. On reconnect, client requests `snapshot` since last known sequence or replays missed ops from server using `since_seq`.

Security
- Use TLS and validate JWT scopes (`doc:read`, `doc:write`). Rate-limit message rate per client to avoid DoS.
