"""
server/grpc_server.py — gRPC server demonstrating two RPC styles.

Pattern               | Description
--------------------- | ---------------------------------------------------
Unary RPC             | One request → one response (like REST but typed)
Server-streaming RPC  | One request → stream of responses (like WebSocket
                      | but schema-enforced and over HTTP/2 multiplexing)

Why gRPC over REST?
  - Proto schema enforced at compile time — no runtime JSON surprises
  - HTTP/2 multiplexing: many streams over one TCP connection (no head-of-line blocking)
  - Binary encoding ~3-5x smaller than JSON
  - Generated client stubs in 10+ languages from one .proto file

Run with:
  uv run python -m server.grpc_server
"""

import asyncio
import logging
import time

import grpc
from grpc import aio

from server.proto import notify_pb2, notify_pb2_grpc

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PORT = 50051


class NotifyServicer(notify_pb2_grpc.NotifyServiceServicer):
    """Implements the two RPCs declared in notify.proto."""

    # ------------------------------------------------------------------
    # Pattern 5a — Unary RPC  (one request, one response)
    # Analogous to a REST POST but the schema is enforced by protobuf.
    # ------------------------------------------------------------------
    async def SendNotification(self, request, context):
        log.info(
            "Unary RPC received: order=%s status=%s",
            request.order_id,
            request.status,
        )
        # In a real system you would persist to DB, push to queue, etc.
        return notify_pb2.NotifyResponse(
            success=True,
            detail=f"Order {request.order_id} marked as '{request.status}'",
        )

    # ------------------------------------------------------------------
    # Pattern 5b — Server-streaming RPC  (one request, many responses)
    # The client opens one call; the server yields updates over time.
    # Great for live dashboards, log tailing, progress streams.
    # ------------------------------------------------------------------
    async def StreamNotifications(self, request, context):
        log.info("Stream RPC opened by subscriber: %s", request.subscriber_id)
        statuses = ["pending", "accepted", "in_transit", "arrived", "completed"]
        for status in statuses:
            if context.cancelled():
                break
            log.info("Streaming status: %s", status)
            yield notify_pb2.NotifyResponse(
                success=True,
                detail=f"[stream] order status → {status}",
            )
            await asyncio.sleep(1)   # simulate real-time progression


async def serve():
    server = aio.server()
    notify_pb2_grpc.add_NotifyServiceServicer_to_server(NotifyServicer(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    await server.start()
    log.info("gRPC server listening on port %d", PORT)
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
