/**
 * Shared TypeScript types for the Figma Clone collaborative editor.
 * These types mirror the Go types in backend/internal/types/types.go and
 * the Yjs CRDT data model described in the design document (Section 4).
 */

// ---------------------------------------------------------------------------
// Canvas / CRDT data model types
// ---------------------------------------------------------------------------

/**
 * Transform describes the geometric properties of a Layer on the canvas.
 */
export interface Transform {
  x: number
  y: number
  w: number
  h: number
  rotation: number
}

/**
 * LayerStyle holds the visual styling properties of a Layer.
 */
export interface LayerStyle {
  fill?: string
  stroke?: string
  strokeWidth?: number
  opacity?: number
  borderRadius?: number
  fontSize?: number
  fontFamily?: string
  fontWeight?: string | number
  textAlign?: 'left' | 'center' | 'right'
  color?: string
}

/**
 * LayerType enumerates all supported design element types.
 * Matches Requirement 4.1.
 */
export type LayerType =
  | 'rectangle'
  | 'ellipse'
  | 'text'
  | 'image'
  | 'vector'
  | 'group'
  | 'component_instance'

/**
 * Layer represents a single design element within a Document.
 * Stored as a Y.Map inside the Yjs document under the "layers" key.
 * The `deleted` flag is a tombstone — layers are never hard-deleted from the
 * CRDT to preserve causal history (Requirement 4.5).
 */
export interface Layer {
  /** Globally unique identifier, client-generated UUID (Requirement 4.2). */
  layer_id: string

  /** The type of design element this layer represents. */
  type: LayerType

  /** The frame this layer belongs to. */
  frame_id: string

  /**
   * Fractional index string used for z-ordering within a frame.
   * Lexicographic sort order determines render order (Requirement 4.4).
   */
  z_index: string

  /** Geometric transform: position, size, and rotation. */
  transform: Transform

  /** Visual styling properties. */
  style: LayerStyle

  /**
   * Tombstone flag. When true the layer has been deleted but is retained in
   * the CRDT for causal consistency (Requirement 4.5).
   */
  deleted: boolean

  /**
   * Stable CDN URL for image layers. Stored as an immutable reference
   * within the layer's CRDT properties (Requirement 9.4).
   */
  asset_url?: string
}

/**
 * Frame is a bounded rectangular container on the canvas (artboard / screen).
 * Frames are stored as an ordered Y.Array of frame_ids in the Yjs document.
 */
export interface Frame {
  /** Globally unique identifier, client-generated UUID. */
  frame_id: string

  /** Human-readable name shown in the layers panel. */
  name: string

  /** Canvas X coordinate of the frame's top-left corner. */
  x: number

  /** Canvas Y coordinate of the frame's top-left corner. */
  y: number

  /** Width of the frame in canvas units. */
  width: number

  /** Height of the frame in canvas units. */
  height: number
}

/**
 * Document is the top-level metadata record stored in the Metadata DB.
 * Matches the `documents` table schema (Requirement 2.1).
 */
export interface Document {
  /** Globally unique identifier assigned by the server. */
  document_id: string

  /** The team this document belongs to. */
  team_id: string

  /** The user who created this document. */
  owner_id: string

  /** Human-readable document name. */
  name: string

  /** ISO 8601 creation timestamp. */
  created_at: string

  /** ISO 8601 last-updated timestamp. */
  updated_at: string

  /**
   * Soft-delete flag. When true the document is not accessible to clients
   * (Requirement 2.5, 2.6).
   */
  is_deleted: boolean
}

// ---------------------------------------------------------------------------
// Presence types
// ---------------------------------------------------------------------------

/**
 * CursorPosition holds the canvas-space coordinates of a user's cursor.
 */
export interface CursorPosition {
  x: number
  y: number
}

/**
 * PresencePayload is the data broadcast by the Presence Service for each
 * connected user. It is ephemeral and never persisted to the Op-Log
 * (Requirement 5.1, 5.2, design Section 6).
 */
export interface PresencePayload {
  /** The user's unique identifier. */
  user_id: string

  /** The user's display name shown next to their cursor. */
  display_name: string

  /**
   * Hex color string assigned to this user for cursor and selection
   * highlight rendering (e.g. "#FF6B6B").
   */
  color: string

  /** Current cursor position in canvas coordinates. */
  cursor: CursorPosition

  /** List of layer_ids currently selected by this user. */
  selection: string[]
}

// ---------------------------------------------------------------------------
// WebSocket protocol types
// ---------------------------------------------------------------------------

/**
 * WsMessageType enumerates all valid WebSocket message type strings.
 * Matches the sync protocol described in design Section 5.
 */
export type WsMessageType =
  | 'delta'
  | 'ack'
  | 'presence'
  | 'snapshot_request'
  | 'snapshot_response'
  | 'join'
  | 'ping'
  | 'pong'
  | 'error'

/**
 * WsMessage is the envelope for all WebSocket messages exchanged between
 * the client and the Collaboration Node (design Section 5).
 *
 * For `delta` messages, `payload` is a base64-encoded Yjs binary update.
 * For `presence` messages, `payload` is a serialized PresencePayload.
 * For `ack` messages, `payload` contains `{ op_id, seq }`.
 * For `join` messages, `payload` contains `{ since_seq }`.
 * For `error` messages, `payload` contains `{ code, message }`.
 */
export interface WsMessage<T = unknown> {
  /** Message type discriminator. */
  type: WsMessageType

  /** UUID of the document this message belongs to. */
  doc_id: string

  /** UUID of the originating client. */
  client_id: string

  /** Message-specific payload. Shape depends on `type`. */
  payload: T
}

// ---------------------------------------------------------------------------
// Convenience payload types
// ---------------------------------------------------------------------------

export interface AckPayload {
  op_id: string
  seq: number
}

export interface JoinPayload {
  since_seq: number
}

export interface ErrorPayload {
  code: string
  message: string
}

export interface SnapshotResponsePayload {
  /** Base64-encoded Yjs state snapshot binary. */
  data: string
  /** Op-log sequence number at which this snapshot was taken. */
  seq: number
}
