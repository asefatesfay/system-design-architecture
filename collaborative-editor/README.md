Collaborative Editor — High-level design

This folder contains a concise design for a real-time collaborative document editor supporting multiple simultaneous editors.

Contents:
- `architecture.md` — Components, flows, and scaling
- `protocol.md` — WebSocket/HTTP message formats and sync protocol
- `data-model.md` — Document model, CRDT choice and representation
- `components.md` — Infrastructure, storage, security, monitoring
- `diagram.mmd` — Mermaid architecture diagram

Recommendation summary:
- Use CRDTs (e.g., a sequence CRDT like RGA/LSEQ or a proven library like Yjs) as the primary convergence mechanism for rich-text and structured docs — simpler offline support and easier merging compared to OT.
- Real-time sync over WebSockets (fallback to WebRTC/DataChannel for P2P where needed). Server nodes manage document rooms, persist checkpoints, and broadcast deltas.
- Partition by `document_id` and route to collaboration nodes via consistent hashing; store durable snapshots in object storage and an append-only operation log in Kafka/Redis Streams for replay and recovery.

See the other files for details and tradeoffs.
Collaborative Editor — High-level design

This folder contains a concise design for a real-time collaborative document editor supporting multiple simultaneous editors.

Contents:
- `architecture.md` — Components, flows, and scaling
- `protocol.md` — WebSocket/HTTP message formats and sync protocol
- `data-model.md` — Document model, CRDT choice and representation
- `components.md` — Infrastructure, storage, security, monitoring
- `diagram.mmd` — Mermaid architecture diagram

Recommendation summary:
- Use CRDTs (e.g., a sequence CRDT like RGA/LSEQ or a proven library like Yjs) as the primary convergence mechanism for rich-text and structured docs — simpler offline support and easier merging compared to OT.
- Real-time sync over WebSockets (fallback to WebRTC/DataChannel for P2P where needed). Server nodes manage document rooms, persist checkpoints, and broadcast deltas.
- Partition by `document_id` and route to collaboration nodes via consistent hashing; store durable snapshots in object storage and an append-only operation log in Kafka/Redis Streams for replay and recovery.

See the other files for details and tradeoffs.
