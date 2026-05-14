# Comprehensive API Design Playbook (Interview + Production)

> A practical guide for designing APIs end-to-end: contracts, scalability, reliability, security, and operability.

---

## 1) What "Comprehensive API Design" Means

A strong API design is not only endpoint naming. It must answer:
- What resources and operations exist?
- How clients authenticate and authorize
- How contracts evolve safely over time
- How APIs behave under retries, failures, and spikes
- How pagination, filtering, and sorting work at scale
- How errors are modeled for humans and machines
- How to observe, test, and govern the API in production

A simple interview sequence:

Requirements -> Resource model -> Contract -> Reliability -> Security -> Scale -> Observability

---

## 2) Requirements First (Before Endpoints)

### Functional
- Core use cases (create/read/update/delete, workflows)
- Query patterns (single object, collections, search)
- Async operations (imports, exports, batch jobs)
- Integrations (webhooks, third-party callbacks)

### Non-Functional
- Traffic profile (average + peak RPS)
- Latency SLO (p50/p95/p99)
- Availability target (e.g., 99.9/99.99)
- Consistency needs (strong vs eventual)
- Data retention/compliance (PII, GDPR, auditability)

If requirements are unclear, endpoint design will look clean but fail in production.

---

## 3) Resource Modeling (Nouns Before Verbs)

Good APIs model business entities and relations.

Example domain: task management
- Workspace
- Project
- Task
- Comment
- User

Resource hierarchy:
- `/workspaces/{workspace_id}`
- `/workspaces/{workspace_id}/projects/{project_id}`
- `/projects/{project_id}/tasks/{task_id}`

Rules:
- Use nouns for resources
- Keep IDs opaque and stable
- Avoid over-nesting (usually max 2 levels)

---

## 4) Endpoint Contract Design

### HTTP Methods
- `GET`: read
- `POST`: create or command-style action
- `PUT`: full replace
- `PATCH`: partial update
- `DELETE`: remove (or soft-delete based on policy)

### Response Semantics
- Deterministic schema
- Consistent status codes
- Stable field names and types

### Example

```http
POST /v1/projects/{project_id}/tasks
Content-Type: application/json
Idempotency-Key: 9b6a2f44-0f54-4f28-8c8f-5ca07f6ec8a1

{
  "title": "Design API",
  "assignee_id": "usr_123",
  "priority": "high",
  "due_at": "2026-06-01T12:00:00Z"
}
```

```http
201 Created
Location: /v1/tasks/tsk_789
ETag: "v3-9aa13"

{
  "id": "tsk_789",
  "project_id": "prj_456",
  "title": "Design API",
  "assignee_id": "usr_123",
  "priority": "high",
  "status": "open",
  "created_at": "2026-05-13T10:00:00Z",
  "updated_at": "2026-05-13T10:00:00Z"
}
```

---

## 5) Query Design: Filtering, Sorting, Pagination

### Filtering
- Use explicit query params: `status=open&assignee_id=usr_123`
- Define supported operators clearly (`eq`, `lt`, `gte`, etc.)

### Sorting
- `sort=-created_at` for descending
- Allow only indexed/safe fields

### Pagination
- Prefer cursor pagination for large changing datasets
- Offset pagination is acceptable for small static lists

Cursor example:

```http
GET /v1/tasks?project_id=prj_456&limit=50&cursor=eyJjcmVhdGVkX2F0IjoiMjAyNi0wNS0xM1QxMDowMDowMFoifQ
```

Response:

```json
{
  "items": [ ... ],
  "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNi0wNS0xM1QwOTowMDowMFoifQ",
  "has_more": true
}
```

Design note:
- Cursor design must match index order to keep queries O(log n) + O(page_size).

---

## 6) Error Model (Machine-Readable + Human-Useful)

Use a consistent envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "due_at must be in the future",
    "request_id": "req_abc123",
    "details": [
      { "field": "due_at", "reason": "must_be_future" }
    ]
  }
}
```

Status code guidance:
- `400` invalid request shape
- `401` not authenticated
- `403` authenticated but not allowed
- `404` resource not found (or access-hidden policy)
- `409` conflict/version mismatch/idempotency in-progress
- `422` semantic validation failure
- `429` rate limit exceeded
- `5xx` server or dependency failures

---

## 7) Reliability Patterns Every Serious API Needs

### Idempotency (writes)
- Required for payment/order/create operations
- Key by `Idempotency-Key + endpoint + tenant`
- Return same response for repeated successful calls

### Concurrency Control
- Use `ETag` + `If-Match` for optimistic locking
- Prevent lost updates on `PATCH`/`PUT`

### Timeouts + Retries
- Clients retry on timeouts/5xx with jittered exponential backoff
- Server enforces retry-safe behavior via idempotency

### Async for long operations
- `202 Accepted` + operation resource for status polling

```http
POST /v1/imports
202 Accepted
Location: /v1/operations/op_123
```

---

## 8) Security and Multi-Tenancy

### Authentication
- OAuth2/OIDC or signed service tokens
- Short-lived access tokens; rotate keys

### Authorization
- Tenant boundary checks first
- Role/attribute-based policies per resource action

### Data Protection
- Encrypt in transit (TLS)
- Encrypt at rest
- Redact secrets/PII in logs

### Abuse Protection
- Per-tenant and per-endpoint rate limits
- WAF/bot checks for public APIs

---

## 9) Versioning and Change Management

Preferred:
- Version in path: `/v1/...`
- Backward-compatible changes only inside major version

Compatible changes:
- Add optional fields
- Add new endpoints

Breaking changes:
- Remove/rename fields
- Change field type/semantics
- Tighten validation unexpectedly

Process:
- Publish changelog
- Add deprecation window
- Track old-version usage before shutdown

---

## 10) Performance and Capacity Design

Estimate early:
- Peak RPS per endpoint
- Avg/peak payload size
- Bandwidth per path (edge, service-to-service, DB)
- Read/write ratio

Typical consequences:
- Read-heavy: caching + replica strategy
- Write-heavy: partitioning + async pipelines
- Large payloads: compression + field selection + CDN/object storage

Back-of-envelope:
- Bandwidth ~= RPS x payload size x overhead x fanout

---

## 11) Observability and Operations

### Metrics
- RPS by endpoint/tenant
- Latency p50/p95/p99
- Error rate by status/error code
- Rate-limit reject count
- Dependency latency/error (DB/cache/queue)

### Logs
- Structured logs with `request_id`, `tenant_id`, `endpoint`, `status`, `latency_ms`

### Tracing
- Distributed traces across gateway -> service -> DB/dependencies

### SLOs
- Example: 99.9% of `GET /v1/tasks` under 250ms
- Error budget drives release/rollback decisions

---

## 12) API Gateway and Edge Concerns

Use gateway for:
- Authn/authz pre-checks
- Rate limiting and quotas
- Request validation and schema enforcement
- Routing and canary releases
- Header normalization and request IDs

Avoid putting domain business logic in the gateway.

---

## 13) Webhooks (Outbound APIs)

If your API emits events to clients:
- At-least-once delivery
- Signed webhook payloads
- Retry with backoff
- Dedup by event ID on consumer side
- Replay support for recovery

Include delivery diagnostics in provider dashboard.

---

## 14) Interview-Ready End-to-End Example (Compact)

Question:
- "Design APIs for an order platform."

Answer skeleton:
1. Resources: Customer, Order, Payment, Shipment
2. Core endpoints:
   - `POST /v1/orders`
   - `GET /v1/orders/{id}`
   - `GET /v1/orders?customer_id=...&cursor=...`
   - `POST /v1/orders/{id}/cancel`
3. Reliability:
   - Idempotency on `POST /orders`
   - ETag on order updates
4. Scale:
   - Cursor pagination + indexed filters
   - Cache read-heavy order summary lookups
5. Security:
   - Tenant scoping + role checks
6. Operations:
   - p95 latency + 5xx + dependency dashboards

---

## 15) Common API Design Mistakes

- Endpoint-first design without requirements
- No idempotency for write APIs
- Offset pagination on large/high-churn datasets
- Inconsistent error shapes across teams
- Unbounded filters/sorts causing table scans
- Tight coupling to internal DB schema
- No deprecation/version policy
- Missing per-tenant rate limits

---

## 16) Final Checklist (Before You Ship)

- Is every endpoint tied to a real use case?
- Are authn/authz and tenant boundaries explicit?
- Are write paths idempotent and retry-safe?
- Is pagination/filtering index-friendly?
- Is the error envelope consistent and actionable?
- Are versioning and deprecation policies documented?
- Are SLOs, dashboards, and alerts defined?
- Do failure modes have graceful behavior?

If you can answer yes to this list, your API design is likely production-ready, not just interview-ready.
