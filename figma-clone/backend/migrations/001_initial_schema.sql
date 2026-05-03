-- Migration: 001_initial_schema
-- Creates all core tables for the Figma Clone metadata database.
-- Requirements: 2.1, 1.1

-- Users
CREATE TABLE users (
  user_id      UUID PRIMARY KEY,
  email        TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- Teams
CREATE TABLE teams (
  team_id    UUID PRIMARY KEY,
  name       TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Team membership
CREATE TABLE team_members (
  team_id UUID REFERENCES teams(team_id),
  user_id UUID REFERENCES users(user_id),
  role    TEXT NOT NULL CHECK (role IN ('owner', 'editor', 'viewer')),
  PRIMARY KEY (team_id, user_id)
);

-- Documents
CREATE TABLE documents (
  document_id          UUID PRIMARY KEY,
  team_id              UUID REFERENCES teams(team_id),
  owner_id             UUID REFERENCES users(user_id),
  name                 TEXT NOT NULL,
  is_deleted           BOOLEAN DEFAULT false,
  snapshot_seq         BIGINT DEFAULT 0,
  last_snapshot_at     TIMESTAMPTZ,
  ops_since_snapshot   INT DEFAULT 0,
  created_at           TIMESTAMPTZ DEFAULT now(),
  updated_at           TIMESTAMPTZ DEFAULT now()
);

-- Per-document ACL overrides (beyond team role)
CREATE TABLE document_acl (
  document_id UUID REFERENCES documents(document_id),
  user_id     UUID REFERENCES users(user_id),
  permission  TEXT NOT NULL CHECK (permission IN ('read', 'write', 'admin')),
  PRIMARY KEY (document_id, user_id)
);

-- Refresh tokens for Auth Service (Requirement 1.6)
CREATE TABLE refresh_tokens (
  token_id   UUID PRIMARY KEY,
  user_id    UUID REFERENCES users(user_id),
  token_hash TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX ON documents(team_id);
CREATE INDEX ON documents(owner_id);
CREATE INDEX ON document_acl(user_id);
CREATE INDEX ON refresh_tokens(user_id);
