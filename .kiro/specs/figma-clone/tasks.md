# Implementation Plan: Figma Clone (Collaborative Editing)

## Overview

Incremental implementation starting from infrastructure and auth, building up through the collaboration core (CRDT + WebSocket), then the client, and finally wiring everything together. Each task builds on the previous and ends with integration.

## Tasks

- [x] 1. Project scaffolding and shared types
  - Initialize Go module for backend services (`figma-clone/backend/go.mod`)
  - Initialize React + TypeScript Vite project for the client (`figma-clone/client/`)
  - Define shared TypeScript types: `Layer`, `Frame`, `Document`, `PresencePayload`, `WsMessage` envelope
  - Define shared Go types/interfaces: `WsMessage`, `OpLogMessage`, `SnapshotMeta`
  - Add `docker-compose.yml` with Postgres, Redis, Kafka, and Zookeeper services
  - _Requirements: 2.1, 3.1, 10.1_

- [ ] 2. Metadata DB schema and migrations
  - [x] 2.1 Write SQL migration files for all tables
    - Create `users`, `teams`, `team_members`, `documents`, `document_acl` tables exactly as specified in the design schema
    - Add indexes on `documents(team_id)`, `documents(owner_id)`, `document_acl(user_id)`
    - _Requirements: 2.1, 1.1_
  - [x] 2.2 Implement Go DB layer (`internal/db/`)
    - Write `db.go` with connection pool setup via `pgx` and PgBouncer-compatible config
    - Write typed query functions: `CreateDocument`, `GetDocument`, `UpdateDocumentName`, `SoftDeleteDocument`, `ListDocumentsForUser`, `UpsertSnapshotMeta`
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 7.2_
  - [x] 2.3 Write unit tests for DB query functions
    - Test each query function against a real Postgres instance (use `testcontainers-go`)
    - Test soft-delete and ACL filtering
    - _Requirements: 2.1, 2.6, 2.7_

- [ ] 3. Auth Service and JWT handling
  - [ ] 3.1 Implement Auth Service HTTP handlers (`services/auth/`)
    - `POST /auth/login` — validate credentials, issue RS256 JWT with `user_id`, `team_id`, `permissions` claims
    - `POST /auth/refresh` — validate refresh token (HttpOnly cookie), issue new JWT
    - Store refresh tokens in Postgres with expiry
    - _Requirements: 1.1, 1.6_
  - [ ] 3.2 Implement JWT middleware (`internal/middleware/jwt.go`)
    - Parse and validate RS256 JWT on every request
    - Expose `user_id`, `team_id`, `permissions` via request context
    - Return HTTP 401 on invalid or expired token
    - _Requirements: 1.2, 1.3_
  - [ ] 3.3 Write unit tests for JWT middleware
    - Test valid token, expired token, wrong algorithm, missing scope
    - _Requirements: 1.2, 1.3, 1.4_

- [ ] 4. Metadata REST API (`services/api/`)
  - [ ] 4.1 Implement document CRUD endpoints
    - `POST /api/documents` — create document, return `document_id` within 500ms
    - `GET /api/documents` — list documents for user (team + ACL filtered), within 300ms
    - `PATCH /api/documents/:id` — rename document
    - `DELETE /api/documents/:id` — soft delete, close active sessions
    - `POST /api/documents/:id/duplicate` — copy latest snapshot to new document
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [ ] 4.2 Implement version history endpoint
    - `GET /api/documents/:id/history` — return list of snapshot checkpoints with timestamps
    - _Requirements: 7.5_
  - [ ] 4.3 Write integration tests for document API
    - Test create/rename/delete/duplicate flows end-to-end with real DB
    - Test 404 on deleted document
    - _Requirements: 2.2, 2.5, 2.6_

- [ ] 5. Asset upload and CDN integration (`services/api/assets.go`)
  - [ ] 5.1 Implement asset upload endpoint
    - `POST /api/assets` — validate MIME type (PNG, JPEG, WebP, SVG) and size ≤ 20MB server-side
    - Sanitize SVG to strip embedded scripts before storing
    - Store to S3 under `assets/{team_id}/{uuid}.{ext}`, return stable CDN URL
    - Enforce per-team quota; return HTTP 429 when exceeded
    - _Requirements: 9.1, 9.2, 9.5_
  - [ ] 5.2 Write unit tests for asset validation
    - Test MIME validation, size rejection, SVG sanitization, quota enforcement
    - _Requirements: 9.1, 9.2, 9.5_

- [ ] 6. Op-Log (Kafka) producer and consumer (`internal/oplog/`)
  - [ ] 6.1 Implement Kafka producer
    - Write `Producer` struct wrapping `confluent-kafka-go`
    - Produce to topic `ops.{document_id}` with `document_id` as key
    - Support both sync (wait for ack) and fire-and-forget modes
    - _Requirements: 7.1, 3.2_
  - [ ] 6.2 Implement Kafka consumer for rehydration
    - Write `Consumer` struct that reads from a given offset range for a `document_id`
    - Deserialize `OpLogMessage` and return ordered slice of Yjs binary updates
    - _Requirements: 7.3, 6.5_
  - [ ] 6.3 Write property test for idempotent op delivery
    - **Property 4: Idempotent delivery** — applying the same Yjs update delta N times produces the same Y.Doc state as applying it once
    - **Validates: Requirements 3.8, 8.1**

- [ ] 7. Collaboration Node — core WebSocket server (`services/collab/`)
  - [ ] 7.1 Implement `DocumentRoom` and session management
    - Define `DocumentRoom` struct with `ydoc`, `sessions` map, `last_seq`, `snapshot_seq`, `dirty_ops`
    - Implement `AddSession`, `RemoveSession`, `BroadcastToRoom` (fan-out via goroutines)
    - _Requirements: 3.6, 5.5_
  - [ ] 7.2 Implement WebSocket upgrade and connection lifecycle
    - Handle `GET /ws?doc_id=X&token=JWT` — validate JWT, route to correct `DocumentRoom`
    - Handle `join` message: send snapshot if `since_seq < snapshot_seq`, else replay delta ops
    - Handle `ping`/`pong` keepalive
    - On disconnect: remove session, publish presence removal to Redis pub/sub
    - _Requirements: 1.2, 1.3, 6.5, 5.4_
  - [ ] 7.3 Implement operation handling pipeline
    - Deserialize incoming `delta` message (Yjs binary update)
    - Enforce `doc:write` JWT scope; reject with error if missing
    - Apply update to in-memory `Y.Doc` via `yjs-go` or CGo Yjs binding
    - Produce to Kafka (sync mode); on timeout (>2s) return error to client, do not broadcast
    - Broadcast binary update to all other sessions in room
    - Send `ack` with `op_id` and server sequence number to originating client
    - Increment `dirty_ops`; trigger snapshot if `dirty_ops >= 500`
    - _Requirements: 3.2, 3.7, 7.1, 7.6, 1.4, 1.5_
  - [ ] 7.4 Write property test for CRDT convergence
    - **Property 1: Convergence** — for any set of concurrent Yjs update deltas applied in any order across N simulated clients, all clients converge to the same final Y.Doc state
    - **Validates: Requirements 3.3, 8.1, 8.5**
  - [ ] 7.5 Write property test for causal consistency
    - **Property 2: Causal consistency** — if update B's vector clock includes update A, then A is always applied before B in every simulated delivery order
    - **Validates: Requirements 8.4, 3.3**

- [ ] 8. Collaboration Node — rehydration and snapshot trigger
  - [ ] 8.1 Implement node startup rehydration
    - On `DocumentRoom` init: fetch latest snapshot from S3, apply to fresh `Y.Doc`
    - Replay Kafka ops from `snapshot_seq` to latest offset
    - Mark room as ready before accepting connections
    - Complete within 10 seconds for documents up to 50MB
    - _Requirements: 7.3_
  - [ ] 8.2 Implement snapshot serialization and S3 write
    - Serialize `Y.encodeStateAsUpdate(ydoc)` to bytes
    - Write to S3 key `snapshots/{doc_id}/{seq}.bin`
    - Update `snapshot_seq` and `last_snapshot_at` in Postgres via `UpsertSnapshotMeta`
    - Reset `dirty_ops` counter
    - _Requirements: 7.2, 7.3_
  - [ ] 8.3 Write property test for snapshot round-trip fidelity
    - **Property 6: Round-trip snapshot fidelity** — `decode(encode(ydoc_state))` produces a Y.Doc that is state-equivalent to the original (same document map contents)
    - **Validates: Requirements 7.3, 6.5**

- [ ] 9. Compaction Worker (`services/compaction/`)
  - [ ] 9.1 Implement compaction polling loop
    - Poll Postgres every 60 seconds for documents where `ops_since_snapshot > 500` OR `last_snapshot_at < now() - 5min`
    - For each candidate: fetch latest snapshot from S3, replay Kafka ops, write new snapshot, update Postgres
    - Run as horizontally scalable background process (use Postgres advisory locks to avoid duplicate work)
    - _Requirements: 7.2_
  - [ ] 9.2 Write integration test for compaction worker
    - Seed a document with >500 ops in Kafka, run worker, verify new snapshot written to S3 and Postgres updated
    - _Requirements: 7.2, 7.4_

- [ ] 10. Presence Service — in-process and cross-node (`internal/presence/`)
  - [ ] 10.1 Implement in-process presence fan-out
    - On `presence` message: validate payload, broadcast directly to all other sessions in `DocumentRoom` (no Kafka)
    - Throttle incoming presence to 30/s per client server-side; drop excess silently
    - _Requirements: 5.1, 5.2, 5.5_
  - [ ] 10.2 Implement Redis pub/sub for cross-node presence
    - Subscribe to `presence.{doc_id}` on node startup
    - Publish presence payloads to Redis channel; fan-out to local sessions on receive
    - On session disconnect: publish presence removal message
    - _Requirements: 5.1, 5.4_
  - [ ] 10.3 Write unit tests for presence isolation
    - **Property 5: Presence isolation** — injecting arbitrary presence messages must not mutate the Y.Doc state
    - **Validates: Requirements 5.1, 5.4, 8.1 (presence does not affect document state)**

- [ ] 11. API Gateway routing and consistent hashing (`services/gateway/`)
  - [ ] 11.1 Implement consistent hash ring in Redis
    - On Collaboration Node startup: register `node_id` + capacity in Redis sorted set
    - Implement `GetNodeForDocument(doc_id)` using consistent hashing (jump hash or ketama)
    - Cache ring locally with 1s TTL
    - _Requirements: 10.1, 10.2_
  - [ ] 11.2 Implement WebSocket proxy with sticky routing
    - Route `GET /ws?doc_id=X` to the correct Collaboration Node based on hash ring
    - On node failure: reroute to next node in ring, trigger rehydration
    - _Requirements: 10.1, 10.2, 10.3_
  - [ ] 11.3 Implement per-client rate limiting
    - Use Redis counters (sliding window) to enforce 100 ops/s per client
    - Return HTTP 429 on excess; apply to both REST and WebSocket op messages
    - _Requirements: 10.3_

- [ ] 12. Client — CRDT engine and sync provider (`client/src/crdt/`)
  - [ ] 12.1 Implement `CRDTEngine` wrapper around Yjs `Y.Doc`
    - Expose `applyLocal(update: Uint8Array)`, `applyRemote(update: Uint8Array)`, `getState(): Uint8Array`
    - Wire Yjs `observe` callbacks to emit `documentChanged` events
    - _Requirements: 3.1, 3.3, 4.2, 4.3, 4.4, 4.5_
  - [ ] 12.2 Implement `SyncProvider` WebSocket client
    - Connect to `wss://.../ws?doc_id=X&token=JWT`
    - Send `join` with `since_seq` from IndexedDB on connect
    - Handle `snapshot` and `delta` messages: apply to `CRDTEngine`
    - Send local Yjs updates as `delta` messages; track pending acks
    - Retransmit unacked ops after 5s timeout with same `op_id`
    - _Requirements: 3.1, 3.2, 3.7, 3.8_
  - [ ] 12.3 Implement `OfflineQueue` with IndexedDB persistence
    - Persist unsynced Yjs updates to IndexedDB on every local op
    - Drain queue in causal order on reconnect
    - Notify user when storage quota is exceeded
    - _Requirements: 6.1, 6.2, 6.3, 6.6_
  - [ ] 12.4 Write property test for client-side CRDT convergence
    - **Property 1 (client): Convergence** — simulate two `CRDTEngine` instances exchanging updates in random order; both must reach identical final state
    - **Validates: Requirements 3.3, 8.1, 8.5**

- [ ] 13. Client — canvas renderer (`client/src/canvas/`)
  - [ ] 13.1 Implement `CanvasRenderer` with scene graph
    - Retained-mode scene graph on `<canvas>` element
    - Implement `requestAnimationFrame` render loop targeting 60fps
    - Implement hit testing and viewport transforms (pan/zoom)
    - Render layer types: rectangle, ellipse, text, image, vector path, group
    - _Requirements: 4.1, 4.7_
  - [ ] 13.2 Wire `CRDTEngine` events to canvas invalidation
    - On `documentChanged`: call `invalidate(affectedLayerIds)`, re-render on next rAF tick
    - Optimistic render: apply local op to scene graph immediately before sending to server
    - _Requirements: 3.1, 3.5_
  - [ ] 13.3 Implement layer operations (create, move, resize, reorder, delete, group)
    - Each operation mutates `CRDTEngine` via Yjs transactions
    - Use fractional indexing for z-order assignment
    - Delete uses tombstone flag (`deleted: true`) not removal
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 14. Client — presence UI (`client/src/presence/`)
  - [ ] 14.1 Implement `PresenceManager`
    - Send cursor position and selection on `mousemove` / selection change, throttled to 30/s
    - Receive presence payloads from `SyncProvider`, maintain `Map<user_id, PresenceState>`
    - Expire stale presence entries after 3s of no update
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [ ] 14.2 Render remote cursors on canvas overlay
    - Render each collaborator's cursor as a labeled pointer in their assigned color
    - Update at up to 30fps; skip render if focus mode is enabled
    - _Requirements: 5.3, 5.6_

- [ ] 15. Checkpoint — integration smoke test
  - Start all services via `docker-compose up`
  - Run automated test: two clients connect to the same document, exchange ops, verify convergence
  - Verify presence broadcasts reach both clients
  - Verify snapshot is written after 500 ops
  - Ensure all tests pass, ask the user if questions arise.
  - _Requirements: 3.3, 5.1, 7.2_

- [ ] 16. Scalability wiring — node registration and graceful handoff
  - [ ] 16.1 Implement Collaboration Node lifecycle hooks
    - On startup: register in Redis hash ring, begin rehydrating assigned documents
    - On shutdown (SIGTERM): mark node as draining, wait for in-flight ops to flush, deregister from ring
    - _Requirements: 10.2_
  - [ ] 16.2 Implement graceful document handoff
    - When ring rebalances: new node rehydrates document (S3 + Kafka replay) within 5s overlap window before old node closes sessions
    - _Requirements: 10.2_
  - [ ] 16.3 Implement overload detection and shedding
    - Monitor CPU usage; if >80% for 60s, mark node as full in Redis so gateway stops assigning new documents
    - _Requirements: 10.3_

- [ ] 17. End-to-end integration and final wiring
  - [ ] 17.1 Wire document delete to session close
    - On soft delete: API calls Collaboration Node to close all sessions in the room within 2s
    - _Requirements: 2.5_
  - [ ] 17.2 Wire document rename to active sessions
    - On rename: broadcast `meta` update via CRDT op to all active sessions within 1s
    - _Requirements: 2.3_
  - [ ] 17.3 Wire asset URL into CRDT layer properties
    - After upload returns CDN URL, client embeds it in the image layer's `asset_url` property via a CRDT op
    - _Requirements: 9.4_
  - [ ] 17.4 Write end-to-end integration tests
    - Test offline edit queue drain on reconnect (Requirement 6.3, 6.4)
    - Test node restart rehydration: kill node, restart, verify document state restored within 10s (Requirement 7.3)
    - Test duplicate document: verify new document has identical snapshot (Requirement 2.4)
    - _Requirements: 6.3, 6.4, 7.3, 2.4_

- [ ] 18. Final checkpoint — ensure all tests pass
  - Run full test suite (`go test ./...` and `vitest --run`)
  - Verify no race conditions under `-race` flag
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests (tasks 6.3, 7.4, 7.5, 8.3, 10.3, 12.4) validate the six correctness properties from the design's Section 13
- Consistent hashing ring (task 11) must be in place before scalability testing
- The Yjs Go binding (task 7.3) is the highest-risk dependency — evaluate `yjs-go` or a CGo wrapper early
