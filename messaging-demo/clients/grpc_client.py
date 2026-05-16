"""
clients/grpc_client.py — demonstrates gRPC Unary and Server-streaming RPCs.

Pattern 5a — Unary RPC
  One typed request → one typed response.
  Same shape as REST POST but:
    - schema enforced by protobuf (no runtime JSON surprises)
    - binary wire format (~3-5x smaller than JSON)
    - generated stub — no hand-rolling URLs or headers

Pattern 5b — Server-streaming RPC
  One typed request → the server yields multiple responses over time.
  Think of it as a typed, schema-enforced WebSocket stream.
  Great for: progress bars, log tailing, live feed of ride status.

Run (gRPC server must be started first):
  # Terminal 1
  uv run python -m server.grpc_server

  # Terminal 2 — unary call
  uv run python -m clients.grpc_client unary

  # Terminal 2 — streaming call
  uv run python -m clients.grpc_client stream
"""

import asyncio
import logging
import sys

import grpc
from grpc import aio

from server.proto import notify_pb2, notify_pb2_grpc

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

GRPC_ADDR = "localhost:50051"
ORDER_ID = "1234"


async def demo_unary() -> None:
    log.info("=== Pattern: gRPC Unary RPC ===")
    async with aio.insecure_channel(GRPC_ADDR) as channel:
        stub = notify_pb2_grpc.NotifyServiceStub(channel)
        request = notify_pb2.NotifyRequest(
            order_id=ORDER_ID,
            status="completed",
            message="Delivered — gRPC unary call",
        )
        log.info("Sending unary RPC: %s", request)
        response = await stub.SendNotification(request)
        log.info("Response: success=%s  detail=%s", response.success, response.detail)


async def demo_stream() -> None:
    log.info("=== Pattern: gRPC Server-Streaming RPC ===")
    log.info("Server will push one status per second…")
    async with aio.insecure_channel(GRPC_ADDR) as channel:
        stub = notify_pb2_grpc.NotifyServiceStub(channel)
        request = notify_pb2.StreamRequest(subscriber_id="client-001")
        async for response in stub.StreamNotifications(request):
            log.info("Stream push → detail=%s", response.detail)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "unary"
    if mode == "unary":
        asyncio.run(demo_unary())
    elif mode == "stream":
        asyncio.run(demo_stream())
    else:
        print("Usage: python -m clients.grpc_client <unary|stream>")
        sys.exit(1)
