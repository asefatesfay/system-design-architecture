PoC: Yjs + WebSocket + Redis Streams

This PoC demonstrates a minimal collaborative editor using Yjs with a WebSocket server and a bridge that writes document deltas into Redis Streams.

Services
- `yserver` — Yjs WebSocket server running on ws://localhost:1234
- `static` — static file server exposing `index.html` at http://localhost:8000
- `redis` — Redis for Streams (port 6379)
- `bridge` — Node process that subscribes to Yjs updates and writes to Redis Stream `ops`

Run locally (install Node 18+):

1. Install deps:

```bash
cd collaborative-editor/poc
npm install
```

2. Start Yjs server:

```bash
npm run start-server
```

3. Start bridge (writes updates to Redis):

```bash
# make sure a redis server is running locally
npm run start-bridge
```

4. Serve static files and open the demo:

```bash
npm run start-static
# then open http://localhost:8000/index.html
```

Docker-compose (quick):

```bash
# from collaborative-editor/poc
docker-compose up --build
```

Notes
- This is intentionally minimal. The `bridge.js` writes base64-encoded Yjs updates into a Redis Stream named `ops` for archival/replay.
- For production: add auth, persistence snapshots, op-log retention, compaction, and sticky routing.
