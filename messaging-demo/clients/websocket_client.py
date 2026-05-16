"""
clients/websocket_client.py — demonstrates the WebSocket push pattern.

Pattern 3 — WebSocket
  Open a persistent connection to the server.
  Server pushes every status change in real time — no polling needed.

Compare to polling:
  Polling: client asks "anything new?" every second → wasted requests when nothing changed
  WebSocket: server says "here's an update" the moment it happens → zero wasted round-trips

Run (in one terminal):
  uv run python -m clients.websocket_client

Then in another terminal trigger a status change:
  uv run python -m clients.rest_client rest

You will see the message appear in the WebSocket client immediately.
"""

import asyncio
import json
import logging
import sys

import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

ORDER_ID = sys.argv[1] if len(sys.argv) > 1 else "1234"
WS_URL = f"ws://localhost:8000/ws/{ORDER_ID}"


async def listen() -> None:
    log.info("=== Pattern: WebSocket ===")
    log.info("Connecting to %s", WS_URL)
    log.info("Waiting for server push events (Ctrl+C to stop)…")

    async with websockets.connect(WS_URL) as ws:
        while True:
            raw = await ws.recv()
            event = json.loads(raw)
            log.info(
                "PUSH received → order=%s  status=%s  note=%s",
                event.get("order_id"),
                event.get("status"),
                event.get("note", event.get("message", "")),
            )
            if event.get("status") == "completed":
                log.info("Order completed — closing connection.")
                break


if __name__ == "__main__":
    try:
        asyncio.run(listen())
    except KeyboardInterrupt:
        log.info("Disconnected.")
