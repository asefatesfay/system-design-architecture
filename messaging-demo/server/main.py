"""
server/main.py — FastAPI server demonstrating six communication patterns.

Pattern        | Endpoint                        | How it works
-------------- | ------------------------------- | -------------------------------------------
REST           | POST /orders/{id}/status        | Client sends request, gets instant response
Polling        | GET  /orders/{id}/status        | Client calls this repeatedly until done
Long Polling   | GET  /orders/{id}/status/wait   | Server holds request open until status changes
SSE            | GET  /orders/{id}/stream        | Server streams events over a plain HTTP connection
WebSocket      | WS   /ws/{id}                   | Server pushes status changes in real time
Webhook        | POST /orders/{id}/webhook       | Register a URL; server calls you back
GraphQL Query  | POST /graphql                   | Typed query — client picks exactly which fields it wants
GraphQL Mutation | POST /graphql                 | Typed write — change data + read result in one round-trip
GraphQL Sub    | WS   /graphql                   | Real-time stream, schema-enforced (graphql-ws protocol)
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared in-process state (swap these for Redis/DB in production)
# ---------------------------------------------------------------------------

# order_id → current status string
orders: dict[str, str] = {}

# order_id → list of registered webhook URLs
webhooks: dict[str, list[str]] = {}

# order_id → list of connected WebSocket clients
ws_connections: dict[str, list[WebSocket]] = {}

# order_id → list of asyncio Events waiting for any status change (long polling + SSE)
_status_events: dict[str, asyncio.Event] = {}

# Redis client (lazy — only used by event-bus demo)
redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    try:
        redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        await redis_client.ping()
        log.info("Redis connected")
    except Exception:
        log.warning("Redis not available — event-bus demo will be skipped")
        redis_client = None
    yield
    if redis_client:
        await redis_client.aclose()


app = FastAPI(title="Messaging Demo", lifespan=lifespan)

# Wire GraphQL schema to the same shared state dicts, then mount the router.
# Import is deferred until after `orders` and _subscribers exist.
from server import graphql_schema as _gql  # noqa: E402
_gql._orders = orders
_gql._subscribers = {}   # GraphQL subscription queues (separate from WS connections)
graphql_subscribers = _gql._subscribers
from server.graphql_schema import graphql_router  # noqa: E402
app.include_router(graphql_router, prefix="/graphql")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class StatusUpdate(BaseModel):
    status: str          # e.g. "pending", "in_transit", "completed"
    message: str = ""


class WebhookRegistration(BaseModel):
    callback_url: HttpUrl


# ---------------------------------------------------------------------------
# Helper: fan-out a status change to every waiting client
# ---------------------------------------------------------------------------

async def _broadcast_and_webhook(order_id: str, status: str, message: str) -> None:
    """Push the update to WebSocket clients, wake long-poll/SSE waiters, and call webhooks."""

    # Wake up any long-polling or SSE connections waiting on this order
    # Each waiter calls event.clear() itself after waking, so we only set() here.
    event = _status_events.get(order_id)
    if event:
        event.set()

    # Notify GraphQL subscription queues for this order
    from server.graphql_schema import Order as GQLOrder
    for queue in graphql_subscribers.get(order_id, []):
        queue.put_nowait(GQLOrder(order_id=order_id, status=status, message=message))

    payload = {"order_id": order_id, "status": status, "message": message}

    # 1. WebSocket push — O(connected clients)
    for ws in ws_connections.get(order_id, []):
        try:
            await ws.send_json(payload)
        except Exception:
            pass  # client already disconnected

    # 2. Webhook fan-out — fire-and-forget HTTP POST to each registered URL
    urls = webhooks.get(order_id, [])
    if urls:
        async with httpx.AsyncClient(timeout=5) as client:
            tasks = [client.post(str(url), json=payload) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    log.warning("Webhook to %s failed: %s", url, result)
                else:
                    log.info("Webhook to %s → HTTP %s", url, result.status_code)

    # 3. Publish to Redis channel so event-bus subscribers receive it too
    if redis_client:
        await redis_client.publish(f"order:{order_id}", json.dumps(payload))
        log.info("Published to Redis channel order:%s", order_id)


# ---------------------------------------------------------------------------
# Pattern 1 — REST  (request → response, synchronous)
# ---------------------------------------------------------------------------

@app.post("/orders/{order_id}/status")
async def update_order_status(order_id: str, body: StatusUpdate) -> dict[str, Any]:
    """
    REST: client sends one request, gets one response.
    Use when: the caller needs confirmation immediately.
    Scale note: stateless — put any number of instances behind a load balancer.
    """
    orders[order_id] = body.status
    asyncio.create_task(_broadcast_and_webhook(order_id, body.status, body.message))
    return {"order_id": order_id, "status": body.status, "pattern": "REST"}


# ---------------------------------------------------------------------------
# Pattern 2 — Polling  (client calls GET on a loop until status changes)
# ---------------------------------------------------------------------------

@app.get("/orders/{order_id}/status")
async def get_order_status(order_id: str) -> dict[str, Any]:
    """
    Polling: client calls this every N seconds.
    Use when: WebSocket infra is unavailable or the client is a simple cron job.
    Scale note: add Cache-Control / ETag so unchanged responses are served from
                a CDN without touching your origin server.
    """
    status = orders.get(order_id, "unknown")
    return {"order_id": order_id, "status": status, "pattern": "polling"}


# ---------------------------------------------------------------------------
# Pattern 2b — Long Polling  (server holds the request open until something changes)
# ---------------------------------------------------------------------------

@app.get("/orders/{order_id}/status/wait")
async def long_poll_order_status(order_id: str, timeout: float = 30) -> dict[str, Any]:
    """
    Long Polling: instead of returning immediately, the server suspends the
    request until the status changes OR the timeout expires.

    Use when: you want near-real-time delivery but cannot use WebSocket
              (e.g., corporate proxies that close persistent connections).
    Scale note: each waiting request holds a goroutine/coroutine. Use an async
                event (not a thread sleep) so the server is not blocked.
    """
    event = _status_events.setdefault(order_id, asyncio.Event())
    current = orders.get(order_id, "unknown")
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout)
        status = orders.get(order_id, current)
        return {"order_id": order_id, "status": status, "pattern": "long-polling", "changed": True}
    except asyncio.TimeoutError:
        return {"order_id": order_id, "status": current, "pattern": "long-polling", "changed": False}


# ---------------------------------------------------------------------------
# Pattern 3b — SSE  (Server-Sent Events: HTTP stream, server pushes, one-directional)
# ---------------------------------------------------------------------------

@app.get("/orders/{order_id}/stream")
async def sse_order_stream(order_id: str, request: Request):
    """
    SSE: a plain HTTP GET that never closes. The server writes text/event-stream
    lines whenever something changes. The browser EventSource API handles
    reconnection automatically.

    Compare to WebSocket:
      SSE   — one-directional (server→client), works over plain HTTP/1.1,
              auto-reconnects, firewall/proxy-friendly.
      WS    — bidirectional, requires upgrade handshake, more complex infra.

    Use when: you only need server→client push (notifications, live feeds,
              progress bars). Use WebSocket when you also need client→server.
    """
    async def event_generator():
        # Send initial state immediately
        status = orders.get(order_id, "unknown")
        yield f"data: {{\"order_id\": \"{order_id}\", \"status\": \"{status}\", \"pattern\": \"SSE\"}}\n\n"

        event = _status_events.setdefault(order_id, asyncio.Event())
        while True:
            if await request.is_disconnected():
                log.info("SSE client disconnected for order %s", order_id)
                break
            try:
                await asyncio.wait_for(event.wait(), timeout=25)
                event.clear()
                status = orders.get(order_id, "unknown")
                payload = json.dumps({"order_id": order_id, "status": status, "pattern": "SSE"})
                yield f"data: {payload}\n\n"
                if status == "completed":
                    break
            except asyncio.TimeoutError:
                # Send a comment keep-alive so proxies don't close the connection
                yield ": keep-alive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Pattern 3 — WebSocket  (persistent bidirectional channel, server pushes)
# ---------------------------------------------------------------------------

@app.websocket("/ws/{order_id}")
async def websocket_endpoint(websocket: WebSocket, order_id: str):
    """
    WebSocket: one TCP connection stays open; server pushes every status change.
    Use when: latency matters (chat, live tracking, dashboards).
    Scale note: each instance only knows its own connections.
                Use Redis pub/sub (see event_bus.py) to fan-out across instances.
    """
    await websocket.accept()
    ws_connections.setdefault(order_id, []).append(websocket)
    log.info("WS client connected for order %s", order_id)
    current = orders.get(order_id, "unknown")
    await websocket.send_json({"order_id": order_id, "status": current, "note": "initial state"})
    try:
        while True:
            # Keep the connection alive; we only send on status changes
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections[order_id].remove(websocket)
        log.info("WS client disconnected for order %s", order_id)


# ---------------------------------------------------------------------------
# Pattern 4 — Webhook  (server calls you when something happens)
# ---------------------------------------------------------------------------

@app.post("/orders/{order_id}/webhook")
async def register_webhook(order_id: str, body: WebhookRegistration) -> dict[str, Any]:
    """
    Webhook registration: give us your URL; we will POST to it on every change.
    Use when: the caller is a server itself (Stripe, GitHub, Shopify all do this).
    Scale note: send webhooks via a queue (Celery / SQS) so a slow receiver
                cannot block your request handlers.
    """
    webhooks.setdefault(order_id, []).append(str(body.callback_url))
    return {
        "order_id": order_id,
        "callback_url": str(body.callback_url),
        "pattern": "webhook",
        "note": "you will receive a POST every time the order status changes",
    }
