# API & Messaging Patterns — Complete Guide

Every pattern here answers the same question using the same domain event:
> "Order `#1234` changed status to `completed`"

Use this as a reference when deciding which communication style to reach for.

---

## Quick-reference table

| Pattern | Direction | Connection | Latency | Client complexity | Best for |
|---------|-----------|------------|---------|-------------------|----------|
| REST | → | New per request | Medium | Low | CRUD, public APIs |
| GraphQL | → | New per request | Medium | Medium | Flexible data fetching |
| Polling | → (loop) | New per request | High (interval-based) | Low | Simple clients, slow data |
| Long Polling | ⇌ (held open) | One per interval | Low–Medium | Low | Near-real-time without WS |
| SSE | ← | One persistent | Low | Low | Server→client live feed |
| WebSocket | ↔ | One persistent | Very low | Medium | Chat, live tracking |
| Webhook | ← | New (server→client) | Low | Low | Server-to-server async |
| gRPC (unary) | → | HTTP/2 stream | Low | Medium | Internal microservices |
| gRPC (streaming) | ← or ↔ | HTTP/2 stream | Very low | Medium | Typed live streams |
| Pub/Sub | broadcast | Broker-mediated | Low | Medium | Fan-out, decoupling |

---

## 1. REST

### What it is
The most common API style. Client sends **one HTTP request**, server returns **one response**, connection closes. Stateless — the server remembers nothing between requests.

```
Client          Server
  │──── POST /orders/1234/status ────▶│
  │◀───────── 200 { status: "ok" } ───│
  │ (connection closes)               │
```

### How it works in this project
```bash
# Trigger:
uv run python -m clients.rest_client rest
# Endpoint: POST /orders/{id}/status
```

### When to use
- Public APIs (Stripe, GitHub, Twitter all use REST)
- CRUD operations (create, read, update, delete a resource)
- When the response is needed immediately and synchronously
- When simplicity and cacheability matter

### When NOT to use
- You need the server to push data without being asked
- Very high-frequency calls (new TCP connection each time is expensive)

### Scale notes
- **Stateless** → any instance can serve any request → horizontal scaling is trivial
- Put a **CDN** in front of GET endpoints (cacheable)
- Use **connection pooling** to reuse TCP connections (HTTP/1.1 keep-alive, HTTP/2)

### Real examples
Stripe payments, GitHub API, most public APIs you have ever used.

---

## 2. GraphQL

### What it is
A **query language** that sits on top of HTTP (usually a single POST `/graphql` endpoint). Instead of the server deciding what data to return, the **client specifies exactly the fields it needs**.

```
Client                         Server
  │── POST /graphql ──────────▶│
  │   { query: "{ order(id: "1234") { status message } }" }
  │◀── { data: { order: { status: "completed", message: "..." } } }
  │
```

### Why it exists
With REST you often need multiple round-trips:
```
GET /orders/1234        → get order (but no driver info)
GET /drivers/456        → get driver
GET /locations/456      → get driver location
```
With GraphQL you do this in **one request**:
```graphql
query {
  order(id: "1234") {
    status
    driver { name location { lat lng } }
  }
}
```

### When to use
- A mobile client and a web client need different shapes of the same data
- You want to avoid over-fetching (getting more fields than you need) or under-fetching (needing extra requests)
- Rapid product iteration — frontend can change data requirements without a backend deploy

### When NOT to use
- Simple CRUD — REST is less overhead
- Real-time data — use GraphQL Subscriptions (WebSocket under the hood) or SSE
- File uploads — REST is cleaner

### How it works in this project

The schema is in [server/graphql_schema.py](server/graphql_schema.py) using **Strawberry** (Python-first GraphQL). Mounted at `/graphql` in the FastAPI server.

```bash
# Query — read current status, ask only for the fields you want
uv run python -m clients.graphql_client query

# Mutation — write + read the result back in one round-trip
uv run python -m clients.graphql_client mutation

# Subscription — real-time stream over WebSocket (graphql-ws protocol)
# Terminal A:
uv run python -m clients.graphql_client subscription
# Terminal B (trigger the change):
uv run python -m clients.rest_client rest
```

Open **http://localhost:8000/graphql** in your browser for the interactive Playground.

### Real examples
GitHub API v4, Shopify Storefront API, Facebook API.

---

## 3. Polling

### What it is
The client **asks on a timer**: "Has anything changed?" The server answers immediately with whatever the current state is, whether or not it changed.

```
Client          Server
  │── GET /orders/1234/status ▶│
  │◀── { status: "pending" } ──│   (nothing changed yet)
  │   (wait 1 second)          │
  │── GET /orders/1234/status ▶│
  │◀── { status: "pending" } ──│   (still nothing)
  │   (wait 1 second)          │
  │── GET /orders/1234/status ▶│
  │◀── { status: "completed" } │   (changed!)
```

### How it works in this project
```bash
# Terminal A — keep polling:
uv run python -m clients.rest_client poll

# Terminal B — trigger a change:
uv run python -m clients.rest_client rest
```

### When to use
- Very simple clients (shell scripts, cron jobs)
- Data changes slowly (daily reports, batch jobs)
- WebSocket / SSE infrastructure is not available

### When NOT to use
- Data changes frequently — you waste requests on "nothing changed" replies
- Low latency is required — you always lag by one poll interval

### Scale notes
- Each poll is a **fresh HTTP request** → easy to cache with `ETag` / `Last-Modified`
- High poll rates × many clients = thundering herd. Stagger with jitter: `sleep(interval + random(0, 0.5 * interval))`

---

## 4. Long Polling

### What it is
A clever middle ground. The client sends a request, but instead of the server answering immediately, it **holds the connection open** until the status changes (or a timeout expires). The client gets near-real-time delivery using plain HTTP.

```
Client              Server
  │── GET /orders/1234/status/wait ──▶│
  │                                   │  (server suspends — waits internally)
  │                                   │  ... 4 seconds later, status changes ...
  │◀────── { status: "completed" } ───│
  │── GET /orders/1234/status/wait ──▶│  (immediately opens another request)
```

### How it works in this project
```bash
# Terminal A — open a long-poll:
curl "http://localhost:8000/orders/1234/status/wait?timeout=30"

# Terminal B — trigger the change:
uv run python -m clients.rest_client rest
```

### When to use
- Need near-real-time delivery but cannot use WebSocket (corporate proxies, strict firewalls that close persistent connections)
- The client environment only supports HTTP (old mobile apps, some IoT)

### When NOT to use
- Very high concurrency — each held request consumes a file descriptor and coroutine
- Bidirectional communication needed

### Scale notes
- Use **async** (like asyncio) not threads — a held request costs ~1KB of memory async vs ~1MB per thread
- Server-side timeout (30s typical) prevents zombie connections
- The client **must immediately re-open** after each response

### Real examples
Facebook Chat used long polling before moving to WebSocket. GitHub's streaming API originally used long polling.

---

## 5. SSE — Server-Sent Events

### What it is
A plain HTTP response that **never closes**. The server writes lines in the `text/event-stream` format whenever something happens. The browser's built-in `EventSource` API handles reconnection automatically.

```
Client              Server
  │── GET /orders/1234/stream ──▶│
  │                              │ (connection stays open)
  │◀── data: {"status":"pending"}│
  │◀── data: {"status":"transit"}│
  │◀── data: {"status":"done"}   │
  │ (client closes OR server ends)
```

Wire format (what actually travels over TCP):
```
data: {"order_id":"1234","status":"in_transit"}\n\n
data: {"order_id":"1234","status":"completed"}\n\n
: keep-alive\n\n          ← comment line, keeps proxy from timing out
```

### How it works in this project
```bash
# Terminal A — subscribe to SSE stream:
curl -N http://localhost:8000/orders/1234/stream

# Terminal B — trigger status changes:
uv run python -m clients.rest_client rest
```

### Compare SSE vs WebSocket

| | SSE | WebSocket |
|---|---|---|
| Direction | Server → Client only | Bidirectional |
| Protocol | Plain HTTP/1.1 or HTTP/2 | Upgrade to WS protocol |
| Browser support | `EventSource` built-in | `WebSocket` built-in |
| Auto-reconnect | Yes (browser handles it) | No (you write it) |
| Proxy/firewall | Friendly (regular HTTP) | Sometimes blocked |
| Use for | Notifications, feeds, progress | Chat, live collab, gaming |

### When to use
- Notifications, activity feeds, live scores, progress bars
- Server only needs to push (no client→server messages needed)
- You want auto-reconnect for free (browser EventSource reconnects)

### Scale notes
- Each SSE connection is one open HTTP response — use async I/O
- Add `keep-alive` comments every 25s so load balancers don't close idle connections
- Behind a load balancer: same cross-instance fan-out problem as WebSocket → use Redis pub/sub

### Real examples
GitHub feed, Twitter streaming API, live sports scores, CI/CD build logs.

---

## 6. WebSocket

### What it is
A **persistent, bidirectional** connection. After an initial HTTP handshake ("upgrade"), both sides can send messages at any time with very low overhead (no HTTP headers on every message).

```
Client              Server
  │── HTTP GET (Upgrade: websocket) ──▶│
  │◀──── 101 Switching Protocols ───────│
  │                                     │ (TCP connection stays open)
  │◀── {"status":"in_transit"} ─────────│   server push
  │──── "ping" ────────────────────────▶│   client message
  │◀── {"status":"completed"} ──────────│   server push
```

### How it works in this project
```bash
# Terminal A — open WebSocket and wait:
uv run python -m clients.websocket_client

# Terminal B — trigger a status change:
uv run python -m clients.rest_client rest
```

### When to use
- Chat (bidirectional, low latency)
- Live collaborative editing (Google Docs style)
- Multiplayer games
- Live location tracking (Uber driver position)
- Anything where you also need client→server messages

### When NOT to use
- You only need server→client push → use SSE (simpler, proxy-friendly)
- Simple request/response → use REST (much less overhead)
- The client is a server calling another server → use gRPC or webhooks

### Scale notes
**The cross-instance problem**: A status change arrives at instance #3. Clients connected to instances #1 and #2 never hear about it unless you add a broker.

```
Fix: Redis Pub/Sub
  Status change → instance #3 → publish to Redis → all instances subscribe
                                                  → each pushes to local WS clients
```

### Real examples
Slack, Discord, Google Docs live cursors, Figma, Uber driver tracking.

---

## 7. Webhook

### What it is
The reverse of REST. Instead of the client calling the server, **the server calls the client** when something happens. The client gives the server a URL; the server POSTs to it later.

```
Step 1 — Registration (client → server):
  Client ──── POST /orders/1234/webhook { callback_url: "https://myapp.com/cb" } ──▶ Server

Step 2 — Event fires later (server → client):
  Server ──── POST https://myapp.com/cb { order_id: "1234", status: "completed" } ──▶ Client
```

### How it works in this project
```bash
# Start a small HTTP receiver + register + trigger (all-in-one demo):
uv run python -m clients.rest_client webhook
```

### When to use
- Server-to-server async notifications
- You don't want the client to poll
- The event is rare and unpredictable (payment received, build finished, PR merged)

### When NOT to use
- The receiver is a browser (browsers can't receive inbound HTTP)
- You need guaranteed delivery — if the receiver is down, the event is lost (use a queue instead)

### Scale notes
- Send webhooks from a **queue** (Celery, SQS) not inline — a slow receiver blocks your request handler
- Add **HMAC signatures** so the receiver can verify the payload came from you
- Implement **retries with exponential backoff** for failed deliveries

### Real examples
Stripe payment notifications, GitHub PR events, Shopify order webhooks, Twilio SMS callbacks.

---

## 8. gRPC — Unary RPC

### What it is
A modern RPC (Remote Procedure Call) framework. You **define a schema** in a `.proto` file, generate client/server code, and call remote methods as if they were local functions. Uses HTTP/2 and binary (protobuf) encoding.

```
Client                          Server
  │── NotifyRequest{order_id, status} ──▶│   (binary protobuf over HTTP/2)
  │◀────── NotifyResponse{success} ───────│
```

### How it works in this project
```bash
# Terminal 1 — start gRPC server:
uv run python -m server.grpc_server

# Terminal 2 — unary call:
uv run python -m clients.grpc_client unary
```

The schema lives in [server/proto/notify.proto](server/proto/notify.proto). Run `grpc_tools.protoc` to regenerate stubs after changing it.

### REST vs gRPC comparison

| | REST | gRPC |
|---|---|---|
| Schema | Optional (OpenAPI) | Mandatory (proto3) |
| Encoding | JSON (text) | Protobuf (binary, ~3–5× smaller) |
| Transport | HTTP/1.1 or HTTP/2 | HTTP/2 only |
| Browser support | Native | Needs grpc-web proxy |
| Code generation | Optional | Built-in (proto → stubs) |
| Streaming | No (use SSE/WS) | Native (4 modes) |

### When to use
- Internal microservice-to-microservice calls
- Performance-critical paths (high volume, low latency)
- Polyglot systems — generate stubs in Go, Java, Python, Rust from one proto file
- You want compile-time type safety across service boundaries

### When NOT to use
- Public browser-facing APIs (browsers can't speak raw gRPC)
- Simple scripts — REST is less setup

### Real examples
Google uses gRPC for nearly all internal services. Netflix, Square, Lyft.

---

## 9. gRPC — Server-Streaming RPC

### What it is
Like SSE, but typed. The client opens **one RPC call** and the server **yields multiple responses** over time. The schema enforces the shape of every message.

```
Client                              Server
  │── StreamRequest{subscriber_id} ──▶│
  │◀── NotifyResponse{status:pending} │
  │◀── NotifyResponse{status:transit} │
  │◀── NotifyResponse{status:done}    │
  │ (stream ends)
```

### How it works in this project
```bash
uv run python -m clients.grpc_client stream
```
The server yields one status per second: `pending → accepted → in_transit → arrived → completed`.

### Four gRPC streaming modes

| Mode | Who streams | Use for |
|------|-------------|---------|
| Unary | Neither | Standard request/response |
| Server-streaming | Server | Live feeds, log tailing, progress |
| Client-streaming | Client | Chunked file upload, sensor telemetry |
| Bidirectional | Both | Chat, collaborative editing (typed WebSocket) |

---

## 10. Redis Pub/Sub — Event Bus

### What it is
A **broker-mediated messaging pattern**. Publishers send events to a named **channel**. Any number of subscribers receive a copy of every event. Publisher and subscriber are fully decoupled — they don't know about each other.

```
Publisher ──▶ Redis channel "order:1234" ──▶ Subscriber A
                                          ├─▶ Subscriber B
                                          └─▶ Subscriber C
```

### How it works in this project
```bash
# Terminal A (subscribe):
uv run python -m server.event_bus subscribe 1234

# Terminal B (publish):
uv run python -m server.event_bus publish 1234 completed
```
Open three subscriber terminals to see the fan-out live.

### Why this matters for WebSocket scaling

```
Without Redis:                    With Redis:
Instance #1  WS clients A, B     Instance #1  WS clients A, B
Instance #2  WS clients C, D     Instance #2  WS clients C, D
Instance #3  WS clients E, F     Instance #3  WS clients E, F

Status change → instance #3       Status change → instance #3
only E, F hear it ❌                → publish to Redis
                                   → all 3 instances receive
                                   → A,B,C,D,E,F all hear it ✓
```

### Pub/Sub vs Message Queue

| | Pub/Sub (Redis) | Message Queue (Kafka, SQS) |
|---|---|---|
| Delivery | Fire and forget | At-least-once, durable |
| If subscriber is offline | Message lost | Message waits in queue |
| Multiple consumers | Each gets a copy | One consumer per message (competing) |
| Use for | Live fan-out, cache invalidation | Job processing, audit log, replay |

### Real examples
Redis Pub/Sub: Socket.io cluster adapter, cache invalidation across nodes.  
Kafka: Uber trip events, LinkedIn activity stream, Airbnb pricing pipeline.

---

## Decision flowchart

```
Does the client need to SEND data to the server during the session?
├── Yes → WebSocket (or gRPC bidirectional)
└── No
    Does the server need to PUSH to the client?
    ├── Yes
    │   Is the client a browser?
    │   ├── Yes → SSE (simpler) or WebSocket
    │   └── No (server-to-server)
    │       → Webhook (if async callback) or gRPC streaming
    └── No (client always initiates)
        How fast does data change?
        ├── Slowly (minutes/hours) → Polling
        ├── Seconds, no WS infra  → Long Polling
        └── Must be instant + client is a server → gRPC Unary or REST

Is the API public-facing?
├── Yes → REST (or GraphQL for flexible querying)
└── No (internal microservice) → gRPC

Do multiple services need to react to the same event?
└── Yes → Pub/Sub event bus (Redis / Kafka)
```

---

## Pattern map to the codebase

| Pattern | Server file | Client file | Endpoint |
|---------|-------------|-------------|----------|
| REST | `server/main.py` | `clients/rest_client.py rest` | `POST /orders/{id}/status` |
| Polling | `server/main.py` | `clients/rest_client.py poll` | `GET /orders/{id}/status` |
| Long Polling | `server/main.py` | `curl …/status/wait` | `GET /orders/{id}/status/wait` |
| SSE | `server/main.py` | `curl -N …/stream` | `GET /orders/{id}/stream` |
| WebSocket | `server/main.py` | `clients/websocket_client.py` | `WS /ws/{id}` |
| Webhook | `server/main.py` | `clients/rest_client.py webhook` | `POST /orders/{id}/webhook` |
| gRPC Unary | `server/grpc_server.py` | `clients/grpc_client.py unary` | port 50051 |
| gRPC Stream | `server/grpc_server.py` | `clients/grpc_client.py stream` | port 50051 |
| Pub/Sub | `server/event_bus.py` | same file (subscribe mode) | Redis channel |
| GraphQL Query | `server/graphql_schema.py` | `clients/graphql_client.py query` | `POST /graphql` |
| GraphQL Mutation | `server/graphql_schema.py` | `clients/graphql_client.py mutation` | `POST /graphql` |
| GraphQL Subscription | `server/graphql_schema.py` | `clients/graphql_client.py subscription` | `WS /graphql` |
