// Package db provides a typed database access layer for the Figma Clone
// metadata database. It wraps pgxpool with PgBouncer-compatible settings
// (simple protocol, no prepared statements) and exposes typed query functions
// for all document-related operations.
//
// Requirements: 2.1, 2.2, 2.3, 2.5, 7.2
package db

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Document represents a row in the documents table.
type Document struct {
	DocumentID       string
	TeamID           string
	OwnerID          string
	Name             string
	IsDeleted        bool
	SnapshotSeq      int64
	LastSnapshotAt   *time.Time
	OpsSinceSnapshot int
	CreatedAt        time.Time
	UpdatedAt        time.Time
}

// SnapshotMeta holds the snapshot-related fields for a document, used by the
// Compaction Worker and Collaboration Node rehydration logic.
type SnapshotMeta struct {
	DocID            string
	SnapshotSeq      int64
	LastSnapshotAt   time.Time
	OpsSinceSnapshot int
}

// DB holds the pgxpool connection pool. All methods are safe for concurrent use.
type DB struct {
	pool *pgxpool.Pool
}

// New creates a new DB by parsing connStr, applying PgBouncer-compatible
// settings (prefer_simple_protocol, no prepared statements), and verifying
// connectivity with a Ping.
//
// The caller is responsible for calling Close when the DB is no longer needed.
func New(ctx context.Context, connStr string) (*DB, error) {
	cfg, err := pgxpool.ParseConfig(connStr)
	if err != nil {
		return nil, fmt.Errorf("db: parse config: %w", err)
	}

	// PgBouncer compatibility: use the simple query protocol and disable
	// server-side prepared statements. PgBouncer in transaction-pooling mode
	// does not support the extended query protocol or named prepared statements.
	cfg.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol

	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("db: create pool: %w", err)
	}

	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("db: ping: %w", err)
	}

	return &DB{pool: pool}, nil
}

// Close releases all connections in the pool. It is safe to call multiple times.
func (db *DB) Close() {
	db.pool.Close()
}

// CreateDocument inserts a new document row. The document_id, team_id,
// owner_id, and name fields must be set on doc; other fields use DB defaults.
//
// Requirement 2.1, 2.2
func (db *DB) CreateDocument(ctx context.Context, doc Document) error {
	const q = `
		INSERT INTO documents (document_id, team_id, owner_id, name)
		VALUES ($1, $2, $3, $4)
	`
	_, err := db.pool.Exec(ctx, q, doc.DocumentID, doc.TeamID, doc.OwnerID, doc.Name)
	if err != nil {
		return fmt.Errorf("db: CreateDocument: %w", err)
	}
	return nil
}

// GetDocument fetches a single document by document_id. Returns nil, nil when
// no row is found (the caller should treat this as a 404).
//
// Requirement 2.1, 2.2
func (db *DB) GetDocument(ctx context.Context, documentID string) (*Document, error) {
	const q = `
		SELECT document_id, team_id, owner_id, name, is_deleted,
		       snapshot_seq, last_snapshot_at, ops_since_snapshot,
		       created_at, updated_at
		FROM   documents
		WHERE  document_id = $1
	`
	row := db.pool.QueryRow(ctx, q, documentID)
	doc, err := scanDocument(row)
	if err != nil {
		return nil, fmt.Errorf("db: GetDocument: %w", err)
	}
	return doc, nil
}

// UpdateDocumentName sets the name field and bumps updated_at for the given
// document. It does not check is_deleted — callers should do that if needed.
//
// Requirement 2.3
func (db *DB) UpdateDocumentName(ctx context.Context, documentID, name string) error {
	const q = `
		UPDATE documents
		SET    name = $1, updated_at = now()
		WHERE  document_id = $2
	`
	_, err := db.pool.Exec(ctx, q, name, documentID)
	if err != nil {
		return fmt.Errorf("db: UpdateDocumentName: %w", err)
	}
	return nil
}

// SoftDeleteDocument sets is_deleted = true and bumps updated_at. Active
// sessions must be closed by the caller (Requirement 2.5).
//
// Requirement 2.5
func (db *DB) SoftDeleteDocument(ctx context.Context, documentID string) error {
	const q = `
		UPDATE documents
		SET    is_deleted = true, updated_at = now()
		WHERE  document_id = $1
	`
	_, err := db.pool.Exec(ctx, q, documentID)
	if err != nil {
		return fmt.Errorf("db: SoftDeleteDocument: %w", err)
	}
	return nil
}

// ListDocumentsForUser returns all non-deleted documents that are either in
// the given team or explicitly shared with the given user via document_acl.
// Results are ordered by updated_at descending.
//
// Requirement 2.1, 2.7
func (db *DB) ListDocumentsForUser(ctx context.Context, userID, teamID string) ([]Document, error) {
	const q = `
		SELECT document_id, team_id, owner_id, name, is_deleted,
		       snapshot_seq, last_snapshot_at, ops_since_snapshot,
		       created_at, updated_at
		FROM   documents
		WHERE  (
		           team_id = $1
		           OR document_id IN (
		               SELECT document_id FROM document_acl WHERE user_id = $2
		           )
		       )
		  AND  is_deleted = false
		ORDER  BY updated_at DESC
	`
	rows, err := db.pool.Query(ctx, q, teamID, userID)
	if err != nil {
		return nil, fmt.Errorf("db: ListDocumentsForUser: %w", err)
	}
	defer rows.Close()

	var docs []Document
	for rows.Next() {
		doc, err := scanDocument(rows)
		if err != nil {
			return nil, fmt.Errorf("db: ListDocumentsForUser scan: %w", err)
		}
		if doc != nil {
			docs = append(docs, *doc)
		}
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("db: ListDocumentsForUser rows: %w", err)
	}
	return docs, nil
}

// UpsertSnapshotMeta updates the snapshot-related columns on a document row.
// It is called by the Compaction Worker and the Collaboration Node after
// writing a new snapshot to S3.
//
// Requirement 7.2
func (db *DB) UpsertSnapshotMeta(ctx context.Context, meta SnapshotMeta) error {
	const q = `
		UPDATE documents
		SET    snapshot_seq       = $1,
		       last_snapshot_at   = $2,
		       ops_since_snapshot = $3,
		       updated_at         = now()
		WHERE  document_id = $4
	`
	_, err := db.pool.Exec(ctx, q,
		meta.SnapshotSeq,
		meta.LastSnapshotAt,
		meta.OpsSinceSnapshot,
		meta.DocID,
	)
	if err != nil {
		return fmt.Errorf("db: UpsertSnapshotMeta: %w", err)
	}
	return nil
}

// rowScanner is satisfied by both pgx.Row and pgx.Rows, allowing scanDocument
// to be used for both QueryRow and Query results.
type rowScanner interface {
	Scan(dest ...any) error
}

// scanDocument reads a document row from a scanner. Returns nil, nil when the
// row is not found (pgx.ErrNoRows).
func scanDocument(row rowScanner) (*Document, error) {
	var doc Document
	err := row.Scan(
		&doc.DocumentID,
		&doc.TeamID,
		&doc.OwnerID,
		&doc.Name,
		&doc.IsDeleted,
		&doc.SnapshotSeq,
		&doc.LastSnapshotAt,
		&doc.OpsSinceSnapshot,
		&doc.CreatedAt,
		&doc.UpdatedAt,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	return &doc, nil
}
