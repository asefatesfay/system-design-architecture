"""
server/graphql_schema.py — GraphQL schema with three operation types.

GraphQL has three fundamental operations:

  Operation    | HTTP equivalent     | When to use
  ------------ | ------------------- | ----------------------------------------
  Query        | GET                 | Fetch data (read-only)
  Mutation     | POST / PUT / DELETE | Change data and get the result back
  Subscription | WebSocket           | Stream real-time events to the client

All three are declared in ONE schema — the client picks which operation it needs.
This is the key difference from REST, where you must know which URL + method to call.

Wire protocol
─────────────
  Query / Mutation → plain HTTP POST to /graphql  (JSON body)
  Subscription     → WebSocket upgrade at /graphql (graphql-ws subprotocol)

Mounted in server/main.py at /graphql
"""

import asyncio
from typing import AsyncGenerator

import strawberry
from strawberry.fastapi import GraphQLRouter

# ---------------------------------------------------------------------------
# Shared state (same dicts as main.py — imported there, not duplicated)
# We define them here so the schema module is self-contained for testing.
# main.py will replace these references after import.
# ---------------------------------------------------------------------------

_orders: dict[str, str] = {}
_subscribers: dict[str, list[asyncio.Queue]] = {}


def get_orders_store() -> dict[str, str]:
    return _orders


def get_subscribers_store() -> dict[str, list[asyncio.Queue]]:
    return _subscribers


# ---------------------------------------------------------------------------
# GraphQL types
# Strawberry turns a plain Python dataclass into a GraphQL type automatically.
# ---------------------------------------------------------------------------

@strawberry.type
class Order:
    order_id: str
    status: str
    message: str = ""


# ---------------------------------------------------------------------------
# Query — read current state
# Equivalent to: GET /orders/{id}/status
#
# GraphQL advantage: the client can ask for exactly the fields it wants.
# With REST you always get the full object even if you only need `status`.
# ---------------------------------------------------------------------------

@strawberry.type
class Query:
    @strawberry.field(
        description="Get the current status of an order. Equivalent to REST GET."
    )
    def order(self, order_id: str) -> Order:
        orders = get_orders_store()
        status = orders.get(order_id, "unknown")
        return Order(order_id=order_id, status=status)


# ---------------------------------------------------------------------------
# Mutation — change state and get the new state back in one round-trip
# Equivalent to: POST /orders/{id}/status
#
# GraphQL advantage: you can chain reads after writes in one request.
# e.g. "update status AND return the new status + driver info" in one call.
# ---------------------------------------------------------------------------

@strawberry.type
class Mutation:
    @strawberry.mutation(
        description="Update an order's status. Equivalent to REST POST. "
                    "Also notifies all active Subscriptions for this order."
    )
    def update_order_status(
        self,
        order_id: str,
        status: str,
        message: str = "",
    ) -> Order:
        orders = get_orders_store()
        subscribers = get_subscribers_store()

        orders[order_id] = status

        # Fan-out to every active subscription queue for this order
        for queue in subscribers.get(order_id, []):
            queue.put_nowait(Order(order_id=order_id, status=status, message=message))

        return Order(order_id=order_id, status=status, message=message)


# ---------------------------------------------------------------------------
# Subscription — real-time stream of status changes
# Uses WebSocket under the hood (graphql-ws subprotocol).
# Equivalent to SSE or WebSocket, but the event shape is schema-enforced.
#
# How it works:
#   1. Client opens a WebSocket to /graphql with subprotocol "graphql-ws"
#   2. Client sends: { type: "subscribe", payload: { query: "subscription { ... }" } }
#   3. Server yields Order objects whenever update_order_status mutation fires
#   4. Client receives typed, validated JSON — not raw bytes
# ---------------------------------------------------------------------------

@strawberry.type
class Subscription:
    @strawberry.subscription(
        description="Stream status changes for an order in real time. "
                    "Uses WebSocket under the hood (graphql-ws protocol)."
    )
    async def order_status_changed(
        self, order_id: str
    ) -> AsyncGenerator[Order, None]:
        queue: asyncio.Queue[Order] = asyncio.Queue()
        subscribers = get_subscribers_store()
        subscribers.setdefault(order_id, []).append(queue)
        try:
            while True:
                order = await queue.get()
                yield order
                if order.status == "completed":
                    break
        finally:
            subscribers[order_id].remove(queue)


# ---------------------------------------------------------------------------
# Build the router — mounted into FastAPI in server/main.py
# ---------------------------------------------------------------------------

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)

# GraphQL Playground (interactive browser IDE) is available at /graphql in dev
# In Strawberry ≥0.200 the IDE is enabled by default; no extra argument needed.
graphql_router = GraphQLRouter(schema)
