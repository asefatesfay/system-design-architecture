# System Design Walkthrough — Dropbox (File Sync & Storage)

> Language-agnostic. Focus is on architecture, data flow, and trade-offs.

---

## The Question

> "Design a file storage and synchronization service like Dropbox. Users upload files from one device and they appear on all their other devices automatically."

---

## Core Insight

Dropbox looks simple — it's just file storage. The hard problems are:

1. **Sync correctness** — if two devices edit the same file simultaneously while offline, what happens? The system must detect conflicts and resolve them without data loss.
2. **Bandwidth efficiency** — uploading a 1GB file every time you change one line is unacceptable. The system must only transfer the changed parts (delta sync).
3. **Metadata vs. content separation** — file metadata (name, path, size, modified time) has completely different access patterns than file content. They need separate storage systems.

---

## Step 1 — Requirements

### Functional
- Upload files from any device
- Sync files to all other devices automatically
- Share files and folders with other users
- Version history (restore previous versions)
- Conflict detection and resolution
- Offline editing (sync when reconnected)
- Web interface for access without client

### Non-Functional

| Attribute | Target |
|-----------|--------|
| Users | 700M registered, 15M paying |
| Files stored | 500B+ files |
| Storage | Exabyte scale |
| Upload throughput | ~1 GB/s aggregate |
| Sync latency | < 30s from upload to sync on other devices |
| Availability | 99.99% |
| Durability | 99.999999999% (11 nines) — files must never be lost |

---

## Step 2 — Estimates

```
Storage:
  700M users × avg 2GB used = 1.4 EB total
  → S3 or equivalent; no other option at this scale

Upload traffic:
  Assume 1% of users upload daily: 7M users
  Avg upload: 10MB
  7M × 10MB = 70 TB/day → ~810 MB/s ingress

Metadata:
  500B files × 200 bytes metadata = 100 TB
  → Too large for a single Postgres instance; needs sharding

Sync notifications:
  When a file changes, all devices of that user must be notified
  15M paying users × 3 devices avg = 45M device connections
  → Need a notification/push system for sync triggers
```

---

## Step 3 — High-Level Design

```mermaid
graph TD
    Client["Desktop/Mobile Client\n(sync daemon)"]
    API["API Gateway"]
    MetaSvc["Metadata Service\n(file tree, versions)"]
    BlockSvc["Block Service\n(chunked upload/download)"]
    NotifSvc["Notification Service\n(sync triggers)"]
    MetaDB["Metadata DB\n(Postgres, sharded)\nfile paths, versions, chunks"]
    BlockStore["Block Store\n(S3)\ncontent-addressed chunks"]
    Cache["Cache\n(Redis)\nhot metadata"]
    MQ["Message Queue\n(Kafka)\nsync events"]
    CDN["CDN\n(download acceleration)"]

    Client -->|"upload chunks"| API --> BlockSvc --> BlockStore
    Client -->|"metadata ops"| API --> MetaSvc --> MetaDB
    MetaSvc --> MQ --> NotifSvc --> Client
    Client -->|"download"| CDN --> BlockStore
    MetaSvc --> Cache
```

### Happy Path — User Uploads a File

```mermaid
sequenceDiagram
    participant C as Client (Device A)
    participant BS as Block Service
    participant S3 as Block Store
    participant MS as Metadata Service
    participant NS as Notification Service
    participant D as Device B (same user)

    C->>C: Split file into 4MB chunks\nCompute SHA-256 of each chunk
    C->>BS: Check which chunks already exist\n(upload only new chunks)
    BS-->>C: [chunk_1: exists, chunk_2: missing, chunk_3: missing]
    C->>BS: Upload chunk_2, chunk_3
    BS->>S3: Store chunks (key = SHA-256 hash)
    C->>MS: Commit file {path, chunks:[hash1,hash2,hash3], size, modified}
    MS->>MS: Create new version record
    MS-->>C: {version_id} ✓
    MS->>MQ: Publish {user_id, file_changed, version_id}
    MQ->>NS: Notify all devices of user
    NS->>D: "File changed, sync needed"
    D->>MS: Fetch new version metadata
    D->>BS: Download only missing chunks
```

---

## Step 4 — Detailed Design

### 4.1 Chunking and Deduplication — The Bandwidth Saver

Files are split into fixed-size chunks (4MB). Each chunk is identified by its SHA-256 hash (content-addressed storage).

```mermaid
graph TD
    File["File: report.docx\n(12MB)"]
    Chunk1["Chunk 1 (4MB)\nSHA256: abc123"]
    Chunk2["Chunk 2 (4MB)\nSHA256: def456"]
    Chunk3["Chunk 3 (4MB)\nSHA256: ghi789"]
    Check["Check S3:\nDoes abc123 exist?"]
    Skip["abc123 exists → skip upload\n(deduplication)"]
    Upload["def456 missing → upload\nghi789 missing → upload"]

    File --> Chunk1 & Chunk2 & Chunk3
    Chunk1 --> Check --> Skip
    Chunk2 & Chunk3 --> Upload
```

**Benefits:**
- **Delta sync:** Only changed chunks are uploaded. Edit one paragraph of a 100MB file → upload one 4MB chunk, not 100MB.
- **Deduplication:** If two users upload the same file, only one copy is stored. The second upload just creates a new metadata record pointing to existing chunks.
- **Parallel upload:** Multiple chunks upload simultaneously.

### 4.2 Metadata Schema — File Tree

```
files table (sharded by user_id):
  user_id, file_id, parent_folder_id, name, is_deleted, current_version_id

file_versions table:
  version_id, file_id, created_at, size, chunk_list (array of SHA-256 hashes)

chunks table:
  chunk_hash (SHA-256), s3_key, size, ref_count
```

The file tree is a recursive structure (folders contain files and folders). Stored as an adjacency list — each file/folder has a `parent_folder_id`. Traversal is done in the application layer, not with recursive SQL.

### 4.3 Conflict Resolution

Two devices edit the same file while offline. When both sync, there's a conflict.

```mermaid
flowchart TD
    DevA["Device A edits file\nwhile offline\n→ version A"]
    DevB["Device B edits file\nwhile offline\n→ version B"]
    Sync["Both devices sync"]
    Detect["Server detects conflict:\nboth versions have same\nparent version but different content"]
    Resolve["Resolution:\n- Keep both versions\n- Rename one: 'file (conflicted copy - Device B)'\n- User resolves manually"]

    DevA --> Sync
    DevB --> Sync
    Sync --> Detect --> Resolve
```

Dropbox's conflict resolution is intentionally simple: **keep both versions**. No automatic merge. The user sees a "conflicted copy" file and decides which to keep. This is the right trade-off for general-purpose file sync — automatic merging only works for specific file types (like Google Docs does for text).

### 4.4 Sync Notification — Long Polling vs. WebSocket

Devices need to know when files change so they can sync. Two approaches:

```mermaid
graph LR
    LP["Long Polling\nClient sends GET /changes\nServer holds request open\nuntil change occurs\nor 30s timeout"]
    WS["WebSocket\nPersistent connection\nServer pushes change events"]

    LP -->|"Simpler"| LP
    LP -->|"Works through firewalls"| LP
    WS -->|"Lower latency"| WS
    WS -->|"Fewer connections"| WS
```

Dropbox historically used long polling (simpler, works through corporate firewalls). Modern clients use WebSocket or SSE for lower latency.

---

## Step 5 — Decision Log

| Decision | Options | Choice | Rationale |
|----------|---------|--------|-----------|
| Content storage | Self-hosted / S3 | S3 | Exabyte scale; 11-nine durability; CDN integration |
| Chunk size | 1MB / 4MB / 10MB | 4MB | Balance between parallelism and overhead; too small = too many chunks; too large = poor delta efficiency |
| Conflict resolution | Auto-merge / Keep both | Keep both | Auto-merge only works for specific formats; keeping both is safe for any file type |
| Metadata DB | Single Postgres / Sharded | Sharded by user_id | 500B files × 200B = 100TB; single instance can't handle this |
| Deduplication | None / Block-level | Block-level (SHA-256) | Significant storage savings; same file uploaded by multiple users stored once |

---

## Step 6 — Bottlenecks

| Bottleneck | Mitigation |
|------------|-----------|
| Large file upload (10GB video) | Chunked parallel upload; resumable (restart from last chunk on failure) |
| Hot user (shared folder with 10K collaborators) | Fan-out notifications to 10K devices; batch notifications; rate limit sync triggers |
| Metadata DB hot partition (power user with 1M files) | Shard by (user_id, folder_id); limit folder size |
| S3 eventual consistency on overwrite | Use versioned S3 keys; never overwrite a chunk (content-addressed = immutable) |
| Sync storm on reconnect (many devices offline) | Stagger sync on reconnect; prioritize recently modified files |

---

## Interviewer Mode — Hard Follow-Up Questions

---

**Q1: "You use SHA-256 hashes as chunk identifiers for deduplication. Two different files could theoretically have the same SHA-256 hash (collision). What happens?"**

> SHA-256 collisions are theoretically possible but practically impossible — the probability is 1 in 2^256, which is less than the probability of a cosmic ray flipping a bit in your RAM. No SHA-256 collision has ever been found in practice. However, if we're being rigorous: a collision would cause one user's chunk to be served to another user — a data corruption and privacy violation. The defense: we don't rely solely on the hash. When a chunk is uploaded, we verify it by re-hashing the stored content and comparing. If there's ever a mismatch (which would indicate either a collision or a storage corruption), we store both chunks under different keys and log an alert. In practice, the real threat isn't hash collisions — it's storage corruption (bit rot). We use checksums at the storage layer (S3 provides MD5 verification on upload) and periodic integrity scans. The SHA-256 is for deduplication efficiency; the storage layer's own checksums handle corruption detection.

---

**Q2: "A user shares a folder with 1,000 collaborators. They upload a 1GB file. How many times is the file stored in S3?"**

> Once. This is the core value of content-addressed storage. The 1GB file is split into ~250 chunks of 4MB each. Each chunk is stored once in S3, keyed by its SHA-256 hash. The 1,000 collaborators each have a metadata record pointing to the same chunk hashes — they don't get their own copies. When any collaborator downloads the file, they fetch the same chunks from S3 (via CDN). The metadata records are cheap (a few KB per user per file). The storage cost is 1GB, not 1TB. The only time we'd store multiple copies is if the file is modified — the modified chunks get new hashes and are stored as new objects. Unchanged chunks continue to point to the existing objects. This is why Dropbox's storage efficiency is so high — a 1GB file shared with 1,000 people costs 1GB of storage, not 1TB.

---

**Q3: "Device A and Device B both edit the same file while offline. Device A changes line 5. Device B changes line 10. When they sync, can these be auto-merged?"**

> In theory yes — they edited different parts of the file. In practice, Dropbox doesn't auto-merge. Here's why: Dropbox is a general-purpose file sync service. It doesn't know the file format. Line 5 and line 10 are meaningful for a text file, but for a binary file (Word document, Photoshop file), "line 5" is meaningless. Auto-merging binary files would corrupt them. The safe approach: detect the conflict (both devices modified the same file from the same base version), keep both versions, and let the user decide. Dropbox creates a "conflicted copy" file. For text files, the user can use a diff tool to merge manually. For binary files, they pick one version. The exception: Google Docs and Figma do auto-merge because they control the file format and have CRDT/OT engines built for it. Dropbox's design choice — be format-agnostic and safe — means no auto-merge. This is the right trade-off for a general-purpose sync tool.

---

**Q4: "A user accidentally deletes their entire Dropbox folder — 500GB of files. They realize 3 days later. How do you restore this?"**

> Dropbox retains deleted files for 30 days (180 days for Business plans). The deletion is a soft delete — files are marked `is_deleted: true` in the metadata DB but the chunks in S3 are not deleted. The S3 lifecycle policy only deletes chunks when their reference count drops to zero AND the soft-delete TTL has expired. Recovery: the user goes to the Dropbox website, navigates to "Deleted Files," selects all files deleted in the last 3 days, and clicks "Restore." The Metadata Service sets `is_deleted: false` for all selected files and updates `updated_at`. The sync daemon on all devices detects the metadata change and re-downloads the files. The chunks are still in S3 — nothing was actually deleted. The restoration is fast (metadata update only) — the files reappear on the website immediately. Re-syncing to devices takes time proportional to the total file size and the device's bandwidth. The 500GB restoration to a device might take hours, but the files are immediately accessible via the web interface.

---

**Q5: "Dropbox has 700M registered users but only 15M paying. The free tier gives 2GB. How do you prevent free users from abusing storage with deduplication — e.g., a free user uploads a file that's already stored by a paid user, effectively getting free storage?"**

> Deduplication is transparent to the user's quota. Each user has a quota counter that tracks their logical storage usage — the sum of file sizes they've uploaded, regardless of whether those chunks are deduplicated. If a free user uploads a 1GB file that's already stored by another user, their quota counter increases by 1GB. They've "used" 1GB of their 2GB quota. The fact that we didn't actually store a new 1GB in S3 is an internal optimization — the user doesn't benefit from it in terms of quota. The quota is based on logical ownership, not physical storage. This is the correct model: the user owns the file and is responsible for its size against their quota. The deduplication savings accrue to Dropbox's infrastructure costs, not to the user's quota. The implementation: the Metadata Service maintains a `quota_used` counter per user, incremented on every file upload by the file's logical size, decremented on deletion. The S3 physical storage is separate from this accounting.
