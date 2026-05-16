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
