"""
clients/rest_client.py — demonstrates REST and Polling patterns.

Pattern 1 — REST
  POST /orders/{id}/status  →  get a synchronous reply

Pattern 2 — Polling
  GET  /orders/{id}/status  →  call in a loop until the status changes

Pattern 4 — Webhook receiver
  We start a tiny HTTP server on localhost:9000 so the main server can
  POST back to us when an order status changes.

Run:
  # REST only
  uv run python -m clients.rest_client rest

  # Polling (watches order 1234 until it reaches "completed")
  uv run python -m clients.rest_client poll

  # Webhook (starts receiver, then registers the URL, then triggers a change)
  uv run python -m clients.rest_client webhook
"""

import asyncio
import sys
import logging
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
ORDER_ID = "1234"
WEBHOOK_PORT = 9000


# ---------------------------------------------------------------------------
# Pattern 1 — REST
# ---------------------------------------------------------------------------

async def demo_rest() -> None:
    log.info("=== Pattern: REST ===")
    async with httpx.AsyncClient() as client:
        # Set initial status
        r = await client.post(
            f"{BASE_URL}/orders/{ORDER_ID}/status",
            json={"status": "in_transit", "message": "Driver en route"},
        )
        log.info("POST response: %s", r.json())

        # Then update to completed
        r = await client.post(
            f"{BASE_URL}/orders/{ORDER_ID}/status",
            json={"status": "completed", "message": "Delivered!"},
        )
        log.info("POST response: %s", r.json())


# ---------------------------------------------------------------------------
# Pattern 2 — Polling
# ---------------------------------------------------------------------------

async def demo_poll() -> None:
    log.info("=== Pattern: Polling ===")
    log.info("Watching order %s — will poll every second until status=completed", ORDER_ID)
    async with httpx.AsyncClient() as client:
        for attempt in range(30):
            r = await client.get(f"{BASE_URL}/orders/{ORDER_ID}/status")
            data = r.json()
            log.info("Poll #%d → status=%s", attempt + 1, data["status"])
            if data["status"] == "completed":
                log.info("Done! Order is completed.")
                return
            await asyncio.sleep(1)
    log.warning("Gave up polling after 30 attempts.")


# ---------------------------------------------------------------------------
# Pattern 4 — Webhook receiver
# ---------------------------------------------------------------------------

received_events: list[dict] = []


@asynccontextmanager
async def _lifespan(app: FastAPI):
    yield


webhook_app = FastAPI(lifespan=_lifespan)


@webhook_app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()
    log.info("WEBHOOK RECEIVED: %s", body)
    received_events.append(body)
    return {"ok": True}


async def demo_webhook() -> None:
    log.info("=== Pattern: Webhook ===")

    # Start the webhook receiver in the background
    config = uvicorn.Config(webhook_app, host="0.0.0.0", port=WEBHOOK_PORT, log_level="warning")
    server = uvicorn.Server(config)
    receiver_task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.5)  # let the receiver start

    async with httpx.AsyncClient() as client:
        # Register our callback URL with the main server
        callback = f"http://localhost:{WEBHOOK_PORT}/webhook"
        r = await client.post(
            f"{BASE_URL}/orders/{ORDER_ID}/webhook",
            json={"callback_url": callback},
        )
        log.info("Webhook registered: %s", r.json())

        # Now trigger a status change — the server will POST back to us
        log.info("Triggering status change…")
        await client.post(
            f"{BASE_URL}/orders/{ORDER_ID}/status",
            json={"status": "completed", "message": "Delivered via REST, notified via webhook"},
        )

        await asyncio.sleep(1)  # give the server time to call us back

    log.info("Events received via webhook: %s", received_events)
    server.should_exit = True
    await receiver_task


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "rest"
    demos = {"rest": demo_rest, "poll": demo_poll, "webhook": demo_webhook}
    if mode not in demos:
        print(f"Usage: python -m clients.rest_client <{'|'.join(demos)}>")
        sys.exit(1)
    asyncio.run(demos[mode]())
