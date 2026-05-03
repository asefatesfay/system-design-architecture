# Requirements Document

## Introduction

This document defines requirements for a Figma-like collaborative design tool. The core focus is real-time multi-user editing of vector-based design documents, where multiple users can simultaneously create, modify, and delete design elements with changes reflected across all connected clients with minimal latency. The system must handle concurrent edits without data loss, support presence awareness (cursors, selections), and maintain document consistency under network partitions and reconnections.

---

## Glossary

- **Canvas**: The infinite 2D workspace where design elements are placed and manipulated.
- **Document**: A named, versioned collection of frames and layers stored persistently.
- **Frame**: A bounded rectangular container on the Canvas that represents a screen, component, or artboard.
- **Layer**: A single design element (rectangle, ellipse, text, image, group, component instance) within a Document.
- **Operation (Op)**: An atomic, serializable mutation to the Document state (e.g., move layer, change fill color).
- **CRDT_Engine**: The conflict-free replicated data type subsystem that merges concurrent Operations without coordination.
- **Collaboration_Node**: A stateful server process that holds the in-memory CRDT state for a set of Documents and manages WebSocket connections.
- **Presence_Service**: The subsystem that tracks and broadcasts per-user cursor position, selection, and online status.
- **Op_Log**: An append-only, durable sequence of Operations used for replay, recovery, and audit.
- **Snapshot**: A serialized, point-in-time binary representation of a Document's full CRDT state.
- **Client**: A browser-based application that renders the Canvas and communicates with the Collaboration_Node.
- **Session**: An authenticated, active WebSocket connection between a Client and a Collaboration_Node.
- **Room**: The logical grouping of all Sessions connected to the same Document.
- **Vector_Clock**: A per-client logical clock used to establish causal ordering of Operations.
- **Compaction_Worker**: A background process that merges Op_Log segments into Snapshots and removes tombstones.
- **API_Gateway**: The entry-point service that handles authentication, TLS termination, and routes connections to Collaboration_Nodes.
- **Auth_Service**: The service responsible for user identity, JWT issuance, and permission enforcement.
- **Asset_Store**: An object storage service (e.g., S3-compatible) used to persist Snapshots and uploaded image assets.
- **Metadata_DB**: A relational database storing Document metadata, user accounts, team memberships, and ACLs.

---

## Requirements

### Requirement 1: User Authentication and Authorization

**User Story:** As a user, I want to authenticate and have my permissions enforced, so that only authorized users can view or edit Documents.

#### Acceptance Criteria

1. THE Auth_Service SHALL issue a signed JWT containing `user_id`, `team_id`, and a list of document-scoped permissions (`doc:read`, `doc:write`, `doc:admin`) upon successful login.
2. WHEN a Client attempts to open a WebSocket Session, THE API_Gateway SHALL validate the JWT signature and expiry before upgrading the connection.
3. IF a JWT is expired or invalid, THEN THE API_Gateway SHALL reject the connection with HTTP 401 and close the socket.
4. WHILE a Session is active, THE Collaboration_Node SHALL enforce that Operations submitted by a Client match the `doc:write` permission in the Client's JWT.
5. IF a Client submits an Operation on a Document for which the Client holds only `doc:read` permission, THEN THE Collaboration_Node SHALL reject the Operation and return an error message to the Client without broadcasting the Operation.
6. THE Auth_Service SHALL support token refresh, issuing a new JWT before the current token expires, so that long-lived Sessions are not interrupted.

---

### Requirement 2: Document Management

**User Story:** As a user, I want to create, open, rename, duplicate, and delete Documents, so that I can organize my design work.

#### Acceptance Criteria

1. THE Metadata_DB SHALL store each Document with a unique `document_id`, `owner_id`, `team_id`, `name`, `created_at`, `updated_at`, and `is_deleted` flag.
2. WHEN a user creates a Document, THE API_Gateway SHALL persist a new Document record in the Metadata_DB and return the `document_id` within 500ms.
3. WHEN a user renames a Document, THE API_Gateway SHALL update the `name` field in the Metadata_DB and propagate the new name to all active Sessions in the Document's Room within 1 second.
4. WHEN a user duplicates a Document, THE API_Gateway SHALL create a new Document record and copy the latest Snapshot to the Asset_Store, completing the operation within 5 seconds for Documents up to 50MB.
5. WHEN a user deletes a Document, THE API_Gateway SHALL set the `is_deleted` flag to true in the Metadata_DB and close all active Sessions in the Document's Room within 2 seconds.
6. IF a Client requests a Document marked `is_deleted`, THEN THE API_Gateway SHALL return HTTP 404.
7. THE API_Gateway SHALL list all Documents accessible to a user, filtered by team membership and ACL entries, returning results within 300ms for up to 1000 Documents.

---

### Requirement 3: Real-Time Collaborative Editing

**User Story:** As a designer, I want my edits to appear on all collaborators' screens in real time, so that the team can work together without conflicts or data loss.

#### Acceptance Criteria

1. WHEN a Client applies a local Operation, THE Client SHALL optimistically render the change immediately without waiting for server acknowledgement.
2. WHEN a Client sends an Operation to the Collaboration_Node, THE Collaboration_Node SHALL apply the Operation to the in-memory CRDT state, persist it to the Op_Log, and broadcast it to all other Sessions in the Room within 100ms under normal network conditions.
3. THE CRDT_Engine SHALL merge concurrent Operations from different Clients such that all Clients converge to the same Document state regardless of the order in which Operations are received.
4. WHEN two Clients concurrently move the same Layer to different positions, THE CRDT_Engine SHALL resolve the conflict deterministically using last-write-wins semantics based on Vector_Clock ordering, ensuring all Clients converge to the same final position.
5. WHEN a Client receives an Operation from the Collaboration_Node, THE Client SHALL apply the Operation to its local CRDT state and re-render the affected Canvas region within 16ms (one frame at 60fps).
6. THE Collaboration_Node SHALL support at least 100 concurrent Sessions per Room without degrading broadcast latency beyond 200ms at the 99th percentile.
7. WHEN the Collaboration_Node persists an Operation to the Op_Log, THE Collaboration_Node SHALL send an `ack` message to the originating Client containing the `op_id` and server-assigned sequence number.
8. IF a Client does not receive an `ack` within 5 seconds of sending an Operation, THEN THE Client SHALL retransmit the Operation with the same `op_id` to enable idempotent deduplication on the server.

---

### Requirement 4: Layer and Canvas Operations

**User Story:** As a designer, I want to create, move, resize, reorder, group, and delete design elements, so that I can build complex layouts collaboratively.

#### Acceptance Criteria

1. THE Client SHALL support the following Layer types: rectangle, ellipse, text, image, vector path, group, and component instance.
2. WHEN a user creates a Layer, THE CRDT_Engine SHALL assign a globally unique `layer_id` using a client-generated UUID and insert the Layer into the Document's layer tree at the specified z-index position.
3. WHEN a user moves or resizes a Layer, THE CRDT_Engine SHALL record the transform (x, y, width, height, rotation) as an Operation with the originating Client's Vector_Clock value.
4. WHEN a user reorders Layers within a Frame, THE CRDT_Engine SHALL use a fractional indexing scheme to assign z-index values, preventing conflicts when two Clients reorder concurrently.
5. WHEN a user deletes a Layer, THE CRDT_Engine SHALL mark the Layer as a tombstone rather than removing it immediately, preserving causal history for concurrent Operations that reference the deleted Layer.
6. WHEN a user groups Layers, THE CRDT_Engine SHALL create a new group Layer and re-parent the selected Layers under it as a single atomic Operation.
7. THE Client SHALL render the Canvas at 60fps during idle state and maintain at least 30fps while receiving a continuous stream of remote Operations from 10 concurrent collaborators.

---

### Requirement 5: Presence and Awareness

**User Story:** As a designer, I want to see where my collaborators' cursors are and what they have selected, so that I can coordinate work without verbal communication.

#### Acceptance Criteria

1. WHEN a Client moves the cursor on the Canvas, THE Presence_Service SHALL broadcast the cursor position (x, y in Canvas coordinates) and the user's display name and avatar color to all other Sessions in the Room within 50ms.
2. WHEN a Client selects one or more Layers, THE Presence_Service SHALL broadcast the selected `layer_id` list to all other Sessions in the Room within 50ms.
3. THE Client SHALL render each collaborator's cursor as a labeled pointer using the collaborator's assigned color, updating position at up to 30 frames per second.
4. WHEN a Session disconnects, THE Presence_Service SHALL remove the user's cursor and selection from all other Clients' displays within 3 seconds.
5. THE Presence_Service SHALL support presence broadcasts for up to 50 concurrent users in a single Room without exceeding 100ms broadcast latency at the 95th percentile.
6. WHERE a user has enabled "focus mode", THE Client SHALL suppress incoming presence broadcasts from other users without affecting the underlying collaborative state.

---

### Requirement 6: Offline Editing and Reconnection

**User Story:** As a designer, I want to continue editing when my network connection drops and have my changes merged when I reconnect, so that I don't lose work due to connectivity issues.

#### Acceptance Criteria

1. WHILE a Client is disconnected from the Collaboration_Node, THE Client SHALL continue to accept and apply local Operations to its local CRDT state.
2. WHILE a Client is disconnected, THE Client SHALL queue all local Operations with their Vector_Clock values in local browser storage (IndexedDB).
3. WHEN a Client reconnects to the Collaboration_Node, THE Client SHALL send all queued Operations in causal order to the Collaboration_Node for merging.
4. WHEN the Collaboration_Node receives queued Operations from a reconnecting Client, THE CRDT_Engine SHALL merge them with the current Document state using CRDT semantics, resolving any conflicts without data loss.
5. WHEN a Client reconnects after a disconnection longer than 30 seconds, THE Collaboration_Node SHALL send the Client a full Snapshot followed by any Operations that occurred after the Snapshot's sequence number, rather than replaying the entire Op_Log.
6. IF the local browser storage quota is exceeded during offline editing, THEN THE Client SHALL notify the user that offline capacity is limited and that the oldest unsynced Operations may be lost upon reconnection.

---

### Requirement 7: Document Persistence and Recovery

**User Story:** As a designer, I want my work to be saved automatically and recoverable after a server failure, so that I never lose more than a few seconds of work.

#### Acceptance Criteria

1. THE Collaboration_Node SHALL persist each Operation to the Op_Log before broadcasting it to the Room, ensuring no acknowledged Operation is lost on node failure.
2. THE Compaction_Worker SHALL create a new Snapshot in the Asset_Store at least every 500 Operations or every 5 minutes, whichever comes first.
3. WHEN a Collaboration_Node restarts, THE Collaboration_Node SHALL rehydrate its in-memory CRDT state by loading the latest Snapshot from the Asset_Store and replaying all subsequent Operations from the Op_Log within 10 seconds for Documents up to 50MB.
4. THE Op_Log SHALL retain Operations for at least 30 days before archival or deletion.
5. WHEN a user requests version history, THE API_Gateway SHALL return a list of Snapshot checkpoints with timestamps, allowing the user to restore the Document to any checkpoint within the retention window.
6. IF the Collaboration_Node fails to persist an Operation to the Op_Log within 2 seconds, THEN THE Collaboration_Node SHALL return an error to the originating Client and not broadcast the Operation to the Room.

---

### Requirement 8: Multiplayer Conflict Resolution

**User Story:** As a designer, I want concurrent edits to be merged automatically and predictably, so that collaborators don't overwrite each other's work unexpectedly.

#### Acceptance Criteria

1. THE CRDT_Engine SHALL guarantee that all Clients in a Room converge to the same Document state after all Operations have been delivered, regardless of network reordering or temporary partitions.
2. WHEN two Clients concurrently edit different properties of the same Layer (e.g., one changes fill color, another changes position), THE CRDT_Engine SHALL merge both changes independently, preserving both edits.
3. WHEN two Clients concurrently delete and modify the same Layer, THE CRDT_Engine SHALL apply the delete Operation and discard the modification, notifying the modifying Client that the target Layer no longer exists.
4. THE CRDT_Engine SHALL use Vector_Clocks to establish causal ordering, ensuring that an Operation that causally depends on a prior Operation is never applied before its dependency.
5. FOR ALL valid sequences of concurrent Operations applied in any order, THE CRDT_Engine SHALL produce the same final Document state (commutativity and associativity invariant).

---

### Requirement 9: Asset Management

**User Story:** As a designer, I want to upload and use images and other assets in my designs, so that I can create rich, realistic mockups.

#### Acceptance Criteria

1. WHEN a user uploads an image asset, THE API_Gateway SHALL validate that the file is a supported format (PNG, JPEG, WebP, SVG) and does not exceed 20MB, then store it in the Asset_Store and return a stable asset URL within 3 seconds.
2. IF an uploaded file exceeds 20MB or is an unsupported format, THEN THE API_Gateway SHALL reject the upload with a descriptive error message and HTTP 400.
3. THE Asset_Store SHALL serve image assets via a CDN with a cache TTL of at least 24 hours to minimize latency for collaborators in different geographic regions.
4. WHEN a Layer references an asset URL, THE CRDT_Engine SHALL store the URL as an immutable reference within the Layer's properties, ensuring the reference is preserved across all CRDT merges.
5. THE API_Gateway SHALL enforce per-team asset storage quotas, returning HTTP 429 when the quota is exceeded.

---

### Requirement 10: Scalability and Performance

**User Story:** As a platform operator, I want the system to scale horizontally to support thousands of concurrent Documents and users, so that the service remains responsive under load.

#### Acceptance Criteria

1. THE API_Gateway SHALL route WebSocket connections to the correct Collaboration_Node using consistent hashing on `document_id`, ensuring all Sessions for a Document land on the same node.
2. THE Collaboration_Node cluster SHALL scale horizontally by adding nodes, with the routing layer redistributing Documents across nodes without dropping active Sessions.
3. WHEN a Collaboration_Node becomes overloaded (CPU > 80% for 60 seconds), THE routing layer SHALL migrate new Document assignments to less-loaded nodes.
4. THE system SHALL support at least 10,000 concurrently active Documents across the cluster, each with up to 100 active Sessions.
5. THE Metadata_DB SHALL use read replicas to serve Document listing and metadata queries, keeping write operations on the primary instance.
6. THE Op_Log storage system SHALL support horizontal partitioning by `document_id` to distribute write throughput across multiple brokers or shards.
