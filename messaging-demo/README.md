# Messaging & API Styles Demo

One Python project showing **6 communication patterns** using the same domain event:
> "Order `#1234` status changed to `completed`"

---

## Patterns covered

| # | Pattern | File | When to use |
|---|---------|------|-------------|
| 1 | REST (request/response) | `server/main.py` | Client needs immediate confirmation |
| 2 | Polling | `clients/rest_client.py` | Simple clients, no WebSocket infra |
| 3 | WebSocket (server push) | `server/main.py` + `clients/websocket_client.py` | Low-latency live updates |
| 4 | Webhook (callback) | `server/main.py` + `clients/rest_client.py` | Server-to-server async notification |
| 5a | gRPC Unary | `server/grpc_server.py` + `clients/grpc_client.py` | Typed service-to-service calls |
| 5b | gRPC Server-streaming | same files | Typed live stream (progress, logs) |
| 6 | Redis Pub/Sub (event bus) | `server/event_bus.py` | Fan-out across multiple server instances |

---

## Quick start

```bash
# 1. Start Redis
docker compose up -d

# 2. Start the FastAPI server (REST + WebSocket + webhook)
uv run uvicorn server.main:app --reload

# 3. In another terminal — start the gRPC server
uv run python -m server.grpc_server
```

---

## Run each pattern

### Pattern 1 — REST
```bash
uv run python -m clients.rest_client rest
```
What happens: two POST requests, each gets an instant synchronous reply.

---

### Pattern 2 — Polling
```bash
# Terminal A: keep polling
uv run python -m clients.rest_client poll

# Terminal B: trigger the change after a few seconds
uv run python -m clients.rest_client rest
```
What happens: terminal A asks "anything new?" every second; it stops when status reaches `completed`.

---

### Pattern 3 — WebSocket
```bash
# Terminal A: open WebSocket connection and wait for pushes
uv run python -m clients.websocket_client

# Terminal B: trigger a status change
uv run python -m clients.rest_client rest
```
What happens: terminal A receives the update the instant it is posted — no polling.

---

### Pattern 4 — Webhook
```bash
uv run python -m clients.rest_client webhook
```
What happens: the client starts a tiny HTTP server on port 9000, registers it with the main server, then triggers a status change. The main server POSTs back to port 9000.

---

### Pattern 5a — gRPC Unary
```bash
uv run python -m clients.grpc_client unary
```
What happens: one typed protobuf request, one typed response. Same as REST but schema-enforced and binary.

---

### Pattern 5b — gRPC Server-streaming
```bash
uv run python -m clients.grpc_client stream
```
What happens: the server sends one status per second (pending → accepted → in_transit → arrived → completed). One open call, multiple typed responses.

---

### Pattern 6 — Redis Pub/Sub (event bus)
```bash
# Terminal A: subscribe
uv run python -m server.event_bus subscribe 1234

# Terminal B: publish an event
uv run python -m server.event_bus publish 1234 completed
```
What happens: the publisher fires one event; every subscriber receives it instantly.
Open three terminals with `subscribe` to see fan-out — one publish reaches all of them.

**Why this matters at scale:** each FastAPI instance subscribes to Redis. A status change posted to instance #3 is fanned out to instances #1 and #2, which push to their own WebSocket clients. This is how Discord/Slack scale real-time delivery.

---

## Project structure

```
messaging-demo/
├── docker-compose.yml       # Redis only
├── pyproject.toml           # uv-managed dependencies
├── server/
│   ├── main.py              # FastAPI: REST + WebSocket + Webhook (patterns 1-4)
│   ├── grpc_server.py       # gRPC server (patterns 5a, 5b)
│   ├── event_bus.py         # Redis pub/sub publisher + subscriber (pattern 6)
│   └── proto/
│       ├── notify.proto     # Schema definition
│       ├── notify_pb2.py    # Generated message classes
│       └── notify_pb2_grpc.py  # Generated server/client stubs
└── clients/
    ├── rest_client.py       # Patterns 1 (REST), 2 (polling), 4 (webhook receiver)
    ├── websocket_client.py  # Pattern 3 (WebSocket)
    └── grpc_client.py       # Patterns 5a (unary), 5b (streaming)
```

---

## How patterns connect to system design

| Interview topic | Pattern to cite | Why |
|-----------------|-----------------|-----|
| Feed / live tracking | WebSocket | Server pushes; client never polls |
| Payment callback | Webhook | Stripe, Shopify model |
| Internal microservices | gRPC | Typed, fast, HTTP/2 multiplexing |
| Simple CRUD | REST | Stateless, cacheable, easy to load-balance |
| Cross-instance fan-out | Redis Pub/Sub | Decouples producers from consumers |
| Fallback / simple clients | Polling | No persistent connection needed |
