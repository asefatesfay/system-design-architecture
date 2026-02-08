# WebSockets

## Definition

**WebSockets** provide full-duplex, bidirectional, real-time communication between client and server over a single TCP connection. Unlike HTTP's request-response model, WebSockets enable servers to push data to clients instantly.

## HTTP vs WebSocket

```
HTTP (Request-Response):
Client → Request → Server
Server → Response → Client
(New connection each time)

WebSocket (Persistent Connection):
Client ←→ Server (bidirectional)
Either can send messages anytime
```

## How WebSockets Work

```
1. Handshake (HTTP Upgrade):
   GET /chat HTTP/1.1
   Upgrade: websocket
   Connection: Upgrade

2. Server accepts:
   HTTP/1.1 101 Switching Protocols
   
3. Connection upgraded to WebSocket
4. Bidirectional messages flow freely
```

## Real-World Examples

### Slack
**Real-time messaging**

```javascript
const ws = new WebSocket('wss://slack.com/messages');

// Receive messages instantly
ws.onmessage = (event) => {
  displayMessage(JSON.parse(event.data));
};

// Send message
ws.send(JSON.stringify({
  channel: '#general',
  message: 'Hello team!'
}));
```

### Trading Platforms (Robinhood, Coinbase)
**Live price updates**

```javascript
ws.onmessage = (event) => {
  const {symbol, price} = JSON.parse(event.data);
  updateChart(symbol, price); // Real-time chart update
};

// Prices pushed by server every second
```

### Google Docs / Figma
**Collaborative editing**

```
User A types → WebSocket → Server → WebSocket → All users
Everyone sees changes in real-time (<100ms)

Operational Transform / CRDTs for conflict resolution
```

### Online Gaming (League of Legends, Fortnite)
**Real-time game state**

```
Player moves → WebSocket → Server
Server → Broadcast to all players
Sub-100ms latency critical
```

### Live Sports Scores
```
Server detects score change → Push to all connected clients
No polling needed!
```

## Implementation

### Server (Node.js)

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Receive message
  ws.on('message', (message) => {
    console.log('Received:', message);
    
    // Broadcast to all clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  });
  
  // Client disconnected
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});
```

### Client (Browser)

```javascript
const socket = new WebSocket('ws://localhost:8080');

// Connection opened
socket.onopen = (event) => {
  console.log('Connected');
  socket.send('Hello Server!');
};

// Receive messages
socket.onmessage = (event) => {
  console.log('Message:', event.data);
  displayMessage(event.data);
};

// Connection closed
socket.onclose = (event) => {
  console.log('Disconnected');
};

// Error
socket.onerror = (error) => {
  console.error('Error:', error);
};
```

## When to Use WebSockets

✅ **Real-time chat** (Slack, Discord, WhatsApp Web)
✅ **Live feeds** (Twitter, Facebook)
✅ **Collaborative tools** (Google Docs, Figma)
✅ **Gaming** (multiplayer real-time)
✅ **Live trading/dashboards** (stocks, crypto)
✅ **IoT device communication**
✅ **Live notifications**

## When NOT to Use WebSockets

❌ **Simple request-response** (use HTTP/REST)
❌ ** fetch data once** (use HTTP GET)
❌ **File uploads** (use HTTP multipart)
❌ **Public APIs** (REST more standard)

## WebSocket vs Alternatives

### Long Polling (Older Technique)
```
Client → Request → Server (waits) → Response
Client → Immediate new request
More overhead than WebSocket ❌
```

### Server-Sent Events (SSE)
```
Server → Client (one-way)
Simpler than WebSocket
Good for notifications, feeds
Can't send client → server
```

### HTTP/2 Server Push
```
Server pushes resources (CSS, JS)
Not for real-time data
```

## Scaling WebSockets

### Challenge: Stateful Connections
```
1000 clients → 1000 open connections on server
Hard to load balance
Can't just move to another server (loses connection)
```

### Solution 1: Sticky Sessions
```
Load Balancer → Route same client to same server
(Based on IP or session cookie)
```

### Solution 2: Message Broker (Redis Pub/Sub)
```
Server 1 ←→ Redis Pub/Sub ←→ Server 2
Client on Server 1 sends message
→ Redis → Broadcast to all servers
→ All clients receive (on any server)
```

### Solution 3: Managed Services
```
AWS API Gateway WebSocket
- Handles connections scaling
- Message routing
- No server management

Pusher, Ably, Socket.IO
- WebSocket as a service
- Easy integration
```

## Best Practices

✅ **Implement reconnection logic**
```javascript
function connect() {
  const socket = new WebSocket(url);
  socket.onclose = () => {
    setTimeout(connect, 1000); // Reconnect after 1s
  };
}
```

✅ **Heartbeat/ping-pong**
```javascript
setInterval(() => {
  socket.send(JSON.stringify({type: 'ping'}));
}, 30000); // Keep connection alive
```

✅ **Authentication**
```javascript
socket.onopen = () => {
  socket.send(JSON.stringify({
    type: 'auth',
    token: 'jwt_token_here'
  }));
};
```

✅ **Message compression**
```
For high-volume: Enable per-message compression
```

✅ **Graceful degradation**
```javascript
if (!window.WebSocket) {
  // Fallback to long polling
  useLongPolling();
}
```

## Interview Tips

**Q: "When would you use WebSockets vs HTTP?"**

**A:** WebSockets for real-time bidirectional communication (chat, live feeds, gaming). HTTP for standard request-response (APIs, file downloads). WebSockets keep connection open, HTTP creates new connection per request.

**Q: "How to scale WebSockets?"**

**A:** Use sticky sessions (route users to same server) or message broker like Redis Pub/Sub to synchronize messages across servers. Managed services like API Gateway WebSocket also handle scaling.

**Q: "WebSocket use cases?"**

**A:** Real-time chat, collaborative editing, live dashboards, online gaming, trading platforms, any scenario needing instant server-to-client updates.

**Key Takeaway:** WebSockets enable real-time bidirectional communication, essential for modern interactive applications!
