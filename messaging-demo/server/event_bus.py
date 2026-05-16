"""
server/event_bus.py — Redis Pub/Sub event bus demo.

This is Pattern 6: async event-driven messaging.

How it works
────────────
  Publisher  →  Redis channel  →  Subscriber(s)

Why this matters at scale
─────────────────────────
  In the WebSocket pattern one server instance only knows about ITS OWN
  connected clients. If you have 10 instances behind a load balancer and
  a status change hits instance #3, clients on instances #1 and #2 never
  hear about it.

  Fix: every instance SUBSCRIBES to Redis. A status change published once
  is fanned out to ALL instances, which each push to their local clients.
  This is exactly how Discord, Slack, and similar apps scale real-time
  delivery across many servers.

Topology visualised
───────────────────
  [REST POST] → FastAPI instance #3
                    └─ redis.publish("order:1234", payload)
                              ├─ instance #1 receives → pushes to local WS clients
                              ├─ instance #2 receives → pushes to local WS clients
                              └─ instance #3 receives → pushes to local WS clients

Run publisher:
  uv run python -m server.event_bus publish 1234 completed

Run subscriber (in a separate terminal):
  uv run python -m server.event_bus subscribe 1234
"""

import asyncio
import json
import logging
import sys

import redis.asyncio as aioredis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REDIS_URL = "redis://localhost:6379"


async def publish(order_id: str, status: str) -> None:
    """Fire one event onto the bus. Any subscriber will receive it."""
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    payload = json.dumps({"order_id": order_id, "status": status})
    receivers = await r.publish(f"order:{order_id}", payload)
    log.info("Published → channel=order:%s  payload=%s  receivers=%d", order_id, payload, receivers)
    await r.aclose()


async def subscribe(order_id: str) -> None:
    """Listen forever on one channel and print every message that arrives."""
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    channel = f"order:{order_id}"
    await pubsub.subscribe(channel)
    log.info("Subscribed to channel: %s  (waiting for messages…)", channel)
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            log.info("Received event: %s", data)
            # In a real server instance you would fan this out to local WS clients here


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m server.event_bus <publish|subscribe> <order_id> [status]")
        sys.exit(1)

    mode, order_id = sys.argv[1], sys.argv[2]

    if mode == "publish":
        status = sys.argv[3] if len(sys.argv) > 3 else "completed"
        asyncio.run(publish(order_id, status))
    elif mode == "subscribe":
        asyncio.run(subscribe(order_id))
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
