package types

import "encoding/json"

// WsMessage is the envelope for all WebSocket messages exchanged between
// clients and the Collaboration Node.
type WsMessage struct {
	// Type identifies the message kind: "delta", "ack", "presence",
	// "snapshot_request", "snapshot_response", "join", "ping", "pong", "error".
	Type string `json:"type"`

	// DocID is the UUID of the document this message belongs to.
	DocID string `json:"doc_id"`

	// ClientID is the UUID of the originating client.
	ClientID string `json:"client_id"`

	// Payload holds the message-specific data. For delta messages this is a
	// base64-encoded Yjs binary update; for presence messages it is a JSON
	// object; for ack messages it contains op_id and seq.
	Payload json.RawMessage `json:"payload"`
}

// OpLogMessage is the schema for messages written to the Kafka op-log topic
// `ops.{document_id}`. Each message represents one Yjs update delta that has
// been durably persisted.
type OpLogMessage struct {
	// Seq is the server-assigned monotonically increasing sequence number for
	// this document.
	Seq int64 `json:"seq"`

	// OpID is the client-generated UUID for this operation, used for
	// idempotent deduplication on retransmit.
	OpID string `json:"op_id"`

	// DocID is the UUID of the document this operation belongs to.
	DocID string `json:"doc_id"`

	// ClientID is the UUID of the client that originated this operation.
	ClientID string `json:"client_id"`

	// Timestamp is the ISO 8601 wall-clock time at which the Collaboration
	// Node received and persisted this operation.
	Timestamp string `json:"timestamp"`

	// Update is the raw Yjs binary update delta. Stored as a byte slice;
	// serialized as base64 in JSON.
	Update []byte `json:"update"`
}

// SnapshotMeta holds the metadata for a document snapshot stored in the
// Asset Store (S3). This is persisted in Postgres and used by the
// Compaction Worker and Collaboration Node rehydration logic.
type SnapshotMeta struct {
	// DocID is the UUID of the document this snapshot belongs to.
	DocID string `json:"doc_id"`

	// SnapshotSeq is the op-log sequence number at which this snapshot was
	// taken. Used to determine which Kafka offsets to replay on rehydration.
	SnapshotSeq int64 `json:"snapshot_seq"`

	// LastSnapshotAt is the ISO 8601 timestamp of when this snapshot was
	// written to the Asset Store.
	LastSnapshotAt string `json:"last_snapshot_at"`

	// OpsSinceSnapshot is the number of operations applied to the document
	// since this snapshot was taken. Used by the Compaction Worker to decide
	// when to create a new snapshot (threshold: 500 ops or 5 minutes).
	OpsSinceSnapshot int `json:"ops_since_snapshot"`
}
