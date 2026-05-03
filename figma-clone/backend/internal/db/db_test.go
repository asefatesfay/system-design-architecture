// Package db_test contains integration tests for the db package.
// Tests run against a real Postgres 16 instance managed by testcontainers-go.
//
// Requirements: 2.1, 2.6, 2.7
package db_test

import (
	"context"
	"fmt"
	"log"
	"os"
	"testing"
	"time"

	"github.com/figma-clone/backend/internal/db"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

// testDB is the shared DB instance used across all tests in this package.
var testDB *db.DB

// testPool is a raw pgxpool used by test helpers to insert prerequisite data
// (users, teams, team_members, document_acl) without going through the typed
// DB layer.
var testPool *pgxpool.Pool

// TestMain starts a Postgres 16 container, runs the migration, then runs all
// tests. The container is terminated after all tests complete.
func TestMain(m *testing.M) {
	ctx := context.Background()

	// Read migration SQL.
	migrationSQL, err := os.ReadFile("../../migrations/001_initial_schema.sql")
	if err != nil {
		log.Fatalf("read migration: %v", err)
	}

	// Start Postgres 16 container.
	pgContainer, err := postgres.Run(ctx,
		"postgres:16-alpine",
		postgres.WithDatabase("figma_test"),
		postgres.WithUsername("figma"),
		postgres.WithPassword("figma_secret"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(60*time.Second),
		),
	)
	if err != nil {
		log.Fatalf("start postgres container: %v", err)
	}
	defer func() {
		if err := pgContainer.Terminate(ctx); err != nil {
			log.Printf("terminate postgres container: %v", err)
		}
	}()

	// Build connection string.
	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		log.Fatalf("get connection string: %v", err)
	}

	// Apply migration using a single raw connection (DDL + simple protocol).
	if err := applyMigration(ctx, connStr, string(migrationSQL)); err != nil {
		log.Fatalf("apply migration: %v", err)
	}

	// Connect the typed DB layer.
	testDB, err = db.New(ctx, connStr)
	if err != nil {
		log.Fatalf("connect testDB: %v", err)
	}
	defer testDB.Close()

	// Connect a raw pool for test helpers.
	testPool, err = pgxpool.New(ctx, connStr)
	if err != nil {
		log.Fatalf("connect testPool: %v", err)
	}
	defer testPool.Close()

	os.Exit(m.Run())
}

// applyMigration executes the migration SQL using a single pgx connection with
// the simple query protocol so that DDL statements work correctly.
func applyMigration(ctx context.Context, connStr, sql string) error {
	cfg, err := pgx.ParseConfig(connStr)
	if err != nil {
		return fmt.Errorf("parse config: %w", err)
	}
	cfg.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol

	conn, err := pgx.ConnectConfig(ctx, cfg)
	if err != nil {
		return fmt.Errorf("connect: %w", err)
	}
	defer conn.Close(ctx)

	if _, err := conn.Exec(ctx, sql); err != nil {
		return fmt.Errorf("exec migration: %w", err)
	}
	return nil
}

// ---- test helper functions ----

// insertUser inserts a test user and returns the user_id.
func insertUser(ctx context.Context, t *testing.T, email, displayName string) string {
	t.Helper()
	userID := uuid.New().String()
	_, err := testPool.Exec(ctx,
		`INSERT INTO users (user_id, email, display_name) VALUES ($1, $2, $3)`,
		userID, email, displayName,
	)
	if err != nil {
		t.Fatalf("insertUser %q: %v", email, err)
	}
	return userID
}

// insertTeam inserts a test team and returns the team_id.
func insertTeam(ctx context.Context, t *testing.T, name string) string {
	t.Helper()
	teamID := uuid.New().String()
	_, err := testPool.Exec(ctx,
		`INSERT INTO teams (team_id, name) VALUES ($1, $2)`,
		teamID, name,
	)
	if err != nil {
		t.Fatalf("insertTeam %q: %v", name, err)
	}
	return teamID
}

// insertTeamMember adds a user to a team with the given role.
func insertTeamMember(ctx context.Context, t *testing.T, teamID, userID, role string) {
	t.Helper()
	_, err := testPool.Exec(ctx,
		`INSERT INTO team_members (team_id, user_id, role) VALUES ($1, $2, $3)`,
		teamID, userID, role,
	)
	if err != nil {
		t.Fatalf("insertTeamMember team=%s user=%s: %v", teamID, userID, err)
	}
}

// insertACL inserts a document_acl entry granting userID access to documentID.
func insertACL(ctx context.Context, t *testing.T, documentID, userID, permission string) {
	t.Helper()
	_, err := testPool.Exec(ctx,
		`INSERT INTO document_acl (document_id, user_id, permission) VALUES ($1, $2, $3)`,
		documentID, userID, permission,
	)
	if err != nil {
		t.Fatalf("insertACL doc=%s user=%s: %v", documentID, userID, err)
	}
}

// newDoc returns a Document with a fresh UUID and the given team/owner/name.
func newDoc(teamID, ownerID, name string) db.Document {
	return db.Document{
		DocumentID: uuid.New().String(),
		TeamID:     teamID,
		OwnerID:    ownerID,
		Name:       name,
	}
}

// ---- tests ----

// TestCreateAndGetDocument verifies that a document can be created and
// retrieved with all fields intact.
//
// Requirements: 2.1, 2.2
func TestCreateAndGetDocument(t *testing.T) {
	ctx := context.Background()

	teamID := insertTeam(ctx, t, "team-create-get")
	ownerID := insertUser(ctx, t, "owner-cag@example.com", "Owner CAG")

	doc := newDoc(teamID, ownerID, "My Design")
	if err := testDB.CreateDocument(ctx, doc); err != nil {
		t.Fatalf("CreateDocument: %v", err)
	}

	got, err := testDB.GetDocument(ctx, doc.DocumentID)
	if err != nil {
		t.Fatalf("GetDocument: %v", err)
	}
	if got == nil {
		t.Fatal("GetDocument returned nil, want document")
	}

	if got.DocumentID != doc.DocumentID {
		t.Errorf("DocumentID = %q, want %q", got.DocumentID, doc.DocumentID)
	}
	if got.TeamID != doc.TeamID {
		t.Errorf("TeamID = %q, want %q", got.TeamID, doc.TeamID)
	}
	if got.OwnerID != doc.OwnerID {
		t.Errorf("OwnerID = %q, want %q", got.OwnerID, doc.OwnerID)
	}
	if got.Name != doc.Name {
		t.Errorf("Name = %q, want %q", got.Name, doc.Name)
	}
	if got.IsDeleted {
		t.Error("IsDeleted = true, want false")
	}
	if got.CreatedAt.IsZero() {
		t.Error("CreatedAt is zero")
	}
	if got.UpdatedAt.IsZero() {
		t.Error("UpdatedAt is zero")
	}
}

// TestGetDocument_NotFound verifies that GetDocument returns nil, nil when the
// document does not exist.
//
// Requirements: 2.6
func TestGetDocument_NotFound(t *testing.T) {
	ctx := context.Background()

	nonExistentID := uuid.New().String()
	got, err := testDB.GetDocument(ctx, nonExistentID)
	if err != nil {
		t.Fatalf("GetDocument: unexpected error: %v", err)
	}
	if got != nil {
		t.Errorf("GetDocument returned %+v, want nil", got)
	}
}

// TestUpdateDocumentName verifies that UpdateDocumentName changes the name
// field and that the change is visible via GetDocument.
//
// Requirements: 2.3
func TestUpdateDocumentName(t *testing.T) {
	ctx := context.Background()

	teamID := insertTeam(ctx, t, "team-update-name")
	ownerID := insertUser(ctx, t, "owner-udn@example.com", "Owner UDN")

	doc := newDoc(teamID, ownerID, "Original Name")
	if err := testDB.CreateDocument(ctx, doc); err != nil {
		t.Fatalf("CreateDocument: %v", err)
	}

	newName := "Renamed Design"
	if err := testDB.UpdateDocumentName(ctx, doc.DocumentID, newName); err != nil {
		t.Fatalf("UpdateDocumentName: %v", err)
	}

	got, err := testDB.GetDocument(ctx, doc.DocumentID)
	if err != nil {
		t.Fatalf("GetDocument: %v", err)
	}
	if got == nil {
		t.Fatal("GetDocument returned nil after rename")
	}
	if got.Name != newName {
		t.Errorf("Name = %q, want %q", got.Name, newName)
	}
}

// TestSoftDeleteDocument verifies that SoftDeleteDocument sets is_deleted=true
// and that the flag is visible via GetDocument.
//
// Requirements: 2.5, 2.6
func TestSoftDeleteDocument(t *testing.T) {
	ctx := context.Background()

	teamID := insertTeam(ctx, t, "team-soft-delete")
	ownerID := insertUser(ctx, t, "owner-sd@example.com", "Owner SD")

	doc := newDoc(teamID, ownerID, "To Be Deleted")
	if err := testDB.CreateDocument(ctx, doc); err != nil {
		t.Fatalf("CreateDocument: %v", err)
	}

	if err := testDB.SoftDeleteDocument(ctx, doc.DocumentID); err != nil {
		t.Fatalf("SoftDeleteDocument: %v", err)
	}

	got, err := testDB.GetDocument(ctx, doc.DocumentID)
	if err != nil {
		t.Fatalf("GetDocument: %v", err)
	}
	if got == nil {
		t.Fatal("GetDocument returned nil after soft delete")
	}
	if !got.IsDeleted {
		t.Error("IsDeleted = false after SoftDeleteDocument, want true")
	}
}

// TestListDocumentsForUser_TeamFilter verifies that ListDocumentsForUser
// returns all non-deleted documents belonging to the user's team.
//
// Requirements: 2.7
func TestListDocumentsForUser_TeamFilter(t *testing.T) {
	ctx := context.Background()

	teamID := insertTeam(ctx, t, "team-list-team-filter")
	ownerID := insertUser(ctx, t, "owner-ltf@example.com", "Owner LTF")
	userID := insertUser(ctx, t, "user-ltf@example.com", "User LTF")
	insertTeamMember(ctx, t, teamID, userID, "editor")

	doc1 := newDoc(teamID, ownerID, "Doc One")
	doc2 := newDoc(teamID, ownerID, "Doc Two")
	if err := testDB.CreateDocument(ctx, doc1); err != nil {
		t.Fatalf("CreateDocument doc1: %v", err)
	}
	if err := testDB.CreateDocument(ctx, doc2); err != nil {
		t.Fatalf("CreateDocument doc2: %v", err)
	}

	docs, err := testDB.ListDocumentsForUser(ctx, userID, teamID)
	if err != nil {
		t.Fatalf("ListDocumentsForUser: %v", err)
	}

	found := make(map[string]bool)
	for _, d := range docs {
		found[d.DocumentID] = true
	}

	if !found[doc1.DocumentID] {
		t.Errorf("doc1 (%s) not found in list", doc1.DocumentID)
	}
	if !found[doc2.DocumentID] {
		t.Errorf("doc2 (%s) not found in list", doc2.DocumentID)
	}
}

// TestListDocumentsForUser_ACLFilter verifies that ListDocumentsForUser
// returns documents from a different team when the user has an explicit ACL
// entry for that document.
//
// Requirements: 2.7
func TestListDocumentsForUser_ACLFilter(t *testing.T) {
	ctx := context.Background()

	// The document lives in a different team.
	otherTeamID := insertTeam(ctx, t, "team-acl-other")
	ownerID := insertUser(ctx, t, "owner-acl@example.com", "Owner ACL")

	// The user belongs to their own team (not the document's team).
	userTeamID := insertTeam(ctx, t, "team-acl-user")
	userID := insertUser(ctx, t, "user-acl@example.com", "User ACL")
	insertTeamMember(ctx, t, userTeamID, userID, "editor")

	doc := newDoc(otherTeamID, ownerID, "Shared Doc")
	if err := testDB.CreateDocument(ctx, doc); err != nil {
		t.Fatalf("CreateDocument: %v", err)
	}

	// Grant the user explicit ACL access to the document.
	insertACL(ctx, t, doc.DocumentID, userID, "read")

	// List documents for the user using their own team (not the doc's team).
	docs, err := testDB.ListDocumentsForUser(ctx, userID, userTeamID)
	if err != nil {
		t.Fatalf("ListDocumentsForUser: %v", err)
	}

	found := false
	for _, d := range docs {
		if d.DocumentID == doc.DocumentID {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("ACL-shared doc (%s) not found in list", doc.DocumentID)
	}
}

// TestListDocumentsForUser_ExcludesDeleted verifies that soft-deleted
// documents are not returned by ListDocumentsForUser.
//
// Requirements: 2.6, 2.7
func TestListDocumentsForUser_ExcludesDeleted(t *testing.T) {
	ctx := context.Background()

	teamID := insertTeam(ctx, t, "team-excludes-deleted")
	ownerID := insertUser(ctx, t, "owner-ed@example.com", "Owner ED")
	userID := insertUser(ctx, t, "user-ed@example.com", "User ED")
	insertTeamMember(ctx, t, teamID, userID, "editor")

	doc := newDoc(teamID, ownerID, "Will Be Deleted")
	if err := testDB.CreateDocument(ctx, doc); err != nil {
		t.Fatalf("CreateDocument: %v", err)
	}
	if err := testDB.SoftDeleteDocument(ctx, doc.DocumentID); err != nil {
		t.Fatalf("SoftDeleteDocument: %v", err)
	}

	docs, err := testDB.ListDocumentsForUser(ctx, userID, teamID)
	if err != nil {
		t.Fatalf("ListDocumentsForUser: %v", err)
	}

	for _, d := range docs {
		if d.DocumentID == doc.DocumentID {
			t.Errorf("soft-deleted doc (%s) appeared in list", doc.DocumentID)
		}
	}
}

// TestUpsertSnapshotMeta verifies that UpsertSnapshotMeta updates the
// snapshot-related columns on a document and that the changes are visible via
// GetDocument.
//
// Requirements: 7.2
func TestUpsertSnapshotMeta(t *testing.T) {
	ctx := context.Background()

	teamID := insertTeam(ctx, t, "team-snapshot-meta")
	ownerID := insertUser(ctx, t, "owner-sm@example.com", "Owner SM")

	doc := newDoc(teamID, ownerID, "Snapshot Doc")
	if err := testDB.CreateDocument(ctx, doc); err != nil {
		t.Fatalf("CreateDocument: %v", err)
	}

	snapshotTime := time.Now().UTC().Truncate(time.Millisecond)
	meta := db.SnapshotMeta{
		DocID:            doc.DocumentID,
		SnapshotSeq:      42,
		LastSnapshotAt:   snapshotTime,
		OpsSinceSnapshot: 7,
	}
	if err := testDB.UpsertSnapshotMeta(ctx, meta); err != nil {
		t.Fatalf("UpsertSnapshotMeta: %v", err)
	}

	got, err := testDB.GetDocument(ctx, doc.DocumentID)
	if err != nil {
		t.Fatalf("GetDocument: %v", err)
	}
	if got == nil {
		t.Fatal("GetDocument returned nil after UpsertSnapshotMeta")
	}

	if got.SnapshotSeq != meta.SnapshotSeq {
		t.Errorf("SnapshotSeq = %d, want %d", got.SnapshotSeq, meta.SnapshotSeq)
	}
	if got.OpsSinceSnapshot != meta.OpsSinceSnapshot {
		t.Errorf("OpsSinceSnapshot = %d, want %d", got.OpsSinceSnapshot, meta.OpsSinceSnapshot)
	}
	if got.LastSnapshotAt == nil {
		t.Fatal("LastSnapshotAt is nil after UpsertSnapshotMeta")
	}
	// Compare with millisecond precision to account for Postgres TIMESTAMPTZ
	// rounding.
	if got.LastSnapshotAt.UTC().Truncate(time.Millisecond) != snapshotTime {
		t.Errorf("LastSnapshotAt = %v, want %v",
			got.LastSnapshotAt.UTC().Truncate(time.Millisecond), snapshotTime)
	}
}
