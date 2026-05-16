"""
clients/graphql_client.py — demonstrates all three GraphQL operation types.

GraphQL has exactly three operations. All go to /graphql but do different things:

  Operation    | What it does                          | Run with
  ------------ | ------------------------------------- | --------------------------
  query        | Read current state                    | python -m … query
  mutation     | Write + read result back in one call  | python -m … mutation
  subscription | Stream real-time events (WebSocket)   | python -m … subscription

Key insight vs REST
───────────────────
  REST forces the server to decide what data is in the response.
  GraphQL lets the CLIENT specify exactly which fields it wants — nothing more,
  nothing less. This eliminates over-fetching and under-fetching.

  REST:  GET /orders/1234  →  { order_id, status, message, driver, eta, ... }
         (you wanted status only, but got everything)

  GQL:   query { order(orderId:"1234") { status } }
         →  { data: { order: { status: "completed" } } }
         (you get exactly what you asked for)

Run:
  # 1. Start the FastAPI server first:
  #    uv run uvicorn server.main:app --port 8000 --reload

  # 2. Run each demo:
  uv run python -m clients.graphql_client query
  uv run python -m clients.graphql_client mutation
  uv run python -m clients.graphql_client subscription
  # Then in another terminal trigger a change:
  uv run python -m clients.rest_client rest

Tip: open http://localhost:8000/graphql in your browser for the interactive
     GraphQL Playground — you can write and run queries manually there.
"""

import asyncio
import json
import sys
import logging

import httpx
import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/graphql"
WS_URL   = "ws://localhost:8000/graphql"
ORDER_ID = "1234"


# ---------------------------------------------------------------------------
# Helper: send a GraphQL request over plain HTTP POST
# Every Query and Mutation is just a JSON POST — no special client needed.
# ---------------------------------------------------------------------------

async def gql_post(query: str, variables: dict | None = None) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            BASE_URL,
            json={"query": query, "variables": variables or {}},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Operation 1 — Query (read)
#
# The client declares EXACTLY which fields it wants.
# Try removing "message" from the query string and re-running — you'll get
# only order_id and status. The server never returns more than asked.
# ---------------------------------------------------------------------------

QUERY = """
query GetOrder($orderId: String!) {
  order(orderId: $orderId) {
    orderId
    status
    message
  }
}
"""

async def demo_query() -> None:
    log.info("=== GraphQL: Query (read) ===")
    log.info("Fetching only the fields we care about — orderId, status, message")
    result = await gql_post(QUERY, {"orderId": ORDER_ID})
    log.info("Response: %s", json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Operation 2 — Mutation (write + read back in one round-trip)
#
# Compare to REST: with REST you POST to update, then GET to confirm.
# With GraphQL you write and read the result in a single network call.
# ---------------------------------------------------------------------------

MUTATION = """
mutation UpdateStatus($orderId: String!, $status: String!, $message: String!) {
  updateOrderStatus(orderId: $orderId, status: $status, message: $message) {
    orderId
    status
    message
  }
}
"""

async def demo_mutation() -> None:
    log.info("=== GraphQL: Mutation (write + read back) ===")
    log.info("Updating status to 'completed' and reading the result back — one round-trip")
    result = await gql_post(
        MUTATION,
        {"orderId": ORDER_ID, "status": "completed", "message": "Delivered via GraphQL mutation"},
    )
    log.info("Response: %s", json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Operation 3 — Subscription (real-time stream over WebSocket)
#
# GraphQL subscriptions use the graphql-ws protocol over WebSocket.
# The server sends typed Order events whenever update_order_status is called.
# This is schema-enforced SSE — same idea as SSE/WebSocket but the shape
# of every message is validated against the schema.
#
# graphql-ws message flow:
#   client → { type: "connection_init" }
#   server → { type: "connection_ack" }
#   client → { type: "subscribe", id: "1", payload: { query: "..." } }
#   server → { type: "next", id: "1", payload: { data: { ... } } }  (repeated)
#   server → { type: "complete", id: "1" }   (when stream ends)
# ---------------------------------------------------------------------------

SUBSCRIPTION = """
subscription WatchOrder($orderId: String!) {
  orderStatusChanged(orderId: $orderId) {
    orderId
    status
    message
  }
}
"""

async def demo_subscription() -> None:
    log.info("=== GraphQL: Subscription (real-time via WebSocket / graphql-ws) ===")
    log.info("Waiting for status changes on order %s … (trigger with: uv run python -m clients.rest_client rest)", ORDER_ID)

    # graphql-ws is a sub-protocol on top of WebSocket
    async with websockets.connect(WS_URL, subprotocols=["graphql-ws"]) as ws:
        # Step 1: initialise the connection
        await ws.send(json.dumps({"type": "connection_init", "payload": {}}))
        ack = json.loads(await ws.recv())
        log.info("Server ack: type=%s", ack.get("type"))

        # Step 2: start the subscription
        await ws.send(json.dumps({
            "type": "start",
            "id": "sub-1",
            "payload": {
                "query": SUBSCRIPTION,
                "variables": {"orderId": ORDER_ID},
            },
        }))

        # Step 3: receive events
        while True:
            raw = await ws.recv()
            msg = json.loads(raw)
            msg_type = msg.get("type")

            if msg_type == "data":
                order = msg["payload"]["data"]["orderStatusChanged"]
                log.info(
                    "SUBSCRIPTION event → orderId=%s  status=%s  message=%s",
                    order["orderId"], order["status"], order.get("message", ""),
                )
                if order["status"] == "completed":
                    log.info("Order completed — closing subscription.")
                    await ws.send(json.dumps({"type": "stop", "id": "sub-1"}))
                    break

            elif msg_type in ("complete", "error"):
                log.info("Subscription ended: %s", msg)
                break


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "query"
    demos = {
        "query":        demo_query,
        "mutation":     demo_mutation,
        "subscription": demo_subscription,
    }
    if mode not in demos:
        print(f"Usage: python -m clients.graphql_client <{'|'.join(demos)}>")
        sys.exit(1)
    asyncio.run(demos[mode]())
