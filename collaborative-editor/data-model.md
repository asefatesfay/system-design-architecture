Data Model — CRDT choice and representation

Recommendation
- Use a Sequence CRDT (e.g., RGA, LSEQ) or a production-ready library such as Yjs for rich-text and structured documents. Yjs provides compact binary deltas, awareness (presence), and many adapters.

Document representation
- In-memory: keep CRDT instance per document with metadata: `doc_id`, `version` (snapshot sequence), `last_op_seq`.
- Persistent snapshot: serialized CRDT state (binary) stored in object store.
- Operation log: append-only stream of deltas with increasing sequence numbers and op IDs.

CRDT metadata
- Each op contains: `op_id` (UUID), `client_id`, `timestamp`, `causal_clock` (vector or lamport), `delta`.

Handling tombstones and GC
- Use periodic compaction workers to merge tombstones and create fresh snapshots; after snapshot and log truncation, GC tombstones safely.

Offline edits
- Clients can work offline: locally accumulate deltas with causal context and send them on reconnect. Server will merge using CRDT semantics.
