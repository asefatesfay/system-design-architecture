# API Design — Critical Path Walkthroughs

> End-to-end API design for real-world systems. Each document focuses on the **critical paths** that carry the most traffic, have the tightest latency budgets, and fail the most spectacularly when designed poorly.

---

## What This Folder Covers

Each document answers:

1. **Resource model** — what entities exist, how they relate
2. **Endpoint contracts** — full request/response shapes with example payloads
3. **Authentication & Authorization** — how tokens, scopes, and ownership work
4. **Critical path deep-dives** — step-by-step flow for the highest-stakes operations
5. **Pagination, filtering, sorting** — at scale
6. **Error handling** — machine-readable errors with retry guidance
7. **Rate limiting & quotas** — per-token and per-IP strategies
8. **Idempotency** — safe retries for mutating operations
9. **Versioning** — how the API evolves without breaking clients
10. **Real-time / Webhooks** — push alternatives where REST falls short

---

## Documents

| # | App | Critical Paths Covered |
|---|-----|------------------------|
| [01](./01-instagram-api-design.md) | **Instagram** | Post creation, Feed retrieval, Stories, Follow graph, Media upload |
| [02](./02-uber-api-design.md) | **Uber** | Ride request, Driver matching, Trip tracking, Fare estimation, Payment |
| [03](./03-figma-api-design.md) | **Figma** | File load, Realtime collaboration, Presence, Comments, Version snapshots |
| [04](./04-google-docs-api-design.md) | **Google Docs** | Document hydrate, Co-editing, Suggestions, Comments, Revision history |
| [05](./05-whatsapp-api-design.md) | **WhatsApp** | Message send/delivery, Receipts, Reconnect sync, Group fan-out |
| [06](./06-youtube-api-design.md) | **YouTube** | Upload-to-watchable pipeline, Playback manifests, Home feed, Engagement |
| [07](./07-spotify-api-design.md) | **Spotify** | Catalog lookup, Playback control, Multi-device sync, Recommendations |
| [08](./08-netflix-api-design.md) | **Netflix** | Home rows, Playback authorization, Adaptive streaming, Progress sync |
| [09](./09-twitter-api-design.md) | **Twitter/X** | Tweet publish, Timeline ranking, Engagement writes, Notifications |
| [10](./10-discord-api-design.md) | **Discord** | Channel messaging, Realtime gateway, Presence, Voice signaling |
| [11](./11-stripe-api-design.md) | **Stripe** | Payment intent lifecycle, Idempotent writes, Webhooks, Reconciliation |
| [12](./12-dropbox-api-design.md) | **Dropbox** | Resumable upload, Delta sync, Long-poll updates, Conflict handling |
| [13](./13-slack-api-design.md) | **Slack** | Workspace messaging, Realtime events, App events, Thread/history retrieval |
| [14](./14-chatgpt-api-design.md) | **ChatGPT** | Chat runs, Token streaming, Tool calls, Conversation state |
| [15](./15-github-copilot-api-design.md) | **GitHub Copilot** | Context assembly, Completion streaming, Policy filtering, Feedback loop |
| [16](./16-perplexity-api-design.md) | **Perplexity** | Query planning, Retrieval/rerank, Citation-backed answers, Follow-ups |
| [17](./17-zoom-api-design.md) | **Zoom** | Meeting create/join, Signaling, Media session flow, Recording lifecycle |
| [18](./18-ai-recommendation-api-design.md) | **AI Recommendation** | Candidate generation, Ranking, Event ingestion, Model/feature freshness |

---

## How to Read Each Document

Each file follows this structure:

```
1. Overview & Scope
2. Data Model (entities + relationships)
3. Authentication
4. API Versioning Strategy
5. Critical Path 1 — <name>
   ├── Endpoint contract
   ├── Example request/response
   ├── Step-by-step internal flow
   └── Edge cases & failure modes
6. Critical Path 2 — <name>
   └── ...
7. Common Concerns (pagination, errors, rate limits, idempotency)
8. Design Decisions & Trade-offs
```

---

## Key Design Principles Applied

| Principle | How it appears |
|-----------|---------------|
| **Nouns, not verbs** | `/posts`, `/trips` not `/createPost`, `/startTrip` |
| **HTTP semantics** | `POST` creates, `PUT` replaces, `PATCH` updates, `GET` reads, `DELETE` removes |
| **Idempotency keys** | `Idempotency-Key` header on `POST` endpoints that trigger side effects |
| **Cursor pagination** | Opaque cursors instead of offset/limit for large, live feeds |
| **Problem Details (RFC 9457)** | `{ "type", "title", "status", "detail", "instance" }` for all errors |
| **Versioning via URL prefix** | `/v1/`, `/v2/` — simple and cache-friendly |
| **Rate limit headers** | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` |
| **Async for slow ops** | Long-running work returns `202 Accepted` + a polling URL |
