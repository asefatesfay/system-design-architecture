# System Design Walkthrough — Zoom (Video Conferencing)

> Language-agnostic. Focus is on architecture, data flow, and trade-offs.

---

## The Question

> "Design a video conferencing platform like Zoom. Multiple participants join a meeting, see and hear each other in real time, and can share their screens."

---

## Core Insight

Video conferencing is the hardest real-time system to design because it combines:

1. **Ultra-low latency requirements** — audio delay > 150ms is perceptible and disruptive. This rules out TCP for media transport.
2. **Adaptive quality** — participants have wildly different network conditions. The system must degrade gracefully.
3. **Media routing at scale** — in a 100-person meeting, naively sending each participant's video to all others = 100 × 99 = 9,900 streams. This doesn't scale.
4. **Global infrastructure** — participants are worldwide; routing media across continents adds unacceptable latency.

---

## Step 1 — Requirements

### Functional
- Video/audio calls with up to 1,000 participants
- Screen sharing
- Chat during meetings
- Recording (local and cloud)
- Breakout rooms
- Virtual backgrounds
- Waiting room / host controls

### Non-Functional

| Attribute | Target |
|-----------|--------|
| Concurrent meetings | 3M+ |
| Participants per meeting | Up to 1,000 (typical: 2-50) |
| Audio latency | < 150ms end-to-end |
| Video latency | < 300ms end-to-end |
| Availability | 99.99% |
| Packet loss tolerance | Graceful degradation up to 10% loss |

---

## Step 2 — Estimates

```
Concurrent meetings: 3M
Average participants: 5 (most meetings are small)
Total concurrent participants: 15M

Video bandwidth per participant:
  Sending: 1 Mbps (720p)
  Receiving: 1 Mbps × (N-1) participants
  For 5-person meeting: 4 Mbps receive

Total bandwidth:
  15M participants × 1 Mbps send = 15 Tbps ingress
  15M × 4 Mbps receive = 60 Tbps egress
  → Must be served from edge media servers, not a central data center

Signaling (meeting control):
  15M participants × 1 signal/s = 15M signals/s
  Each signal: ~200 bytes → 3 GB/s (manageable)
```

**Key observation:** 60 Tbps of video egress cannot come from a central location. Media servers must be distributed globally, close to participants.

---

## Step 3 — High-Level Design

```mermaid
graph TD
    ClientA["Participant A\n(sends + receives video/audio)"]
    ClientB["Participant B"]
    ClientC["Participant C"]
    Signal["Signaling Server\n(WebSocket)\nmeeting control, SDP exchange"]
    Media["Media Server\n(SFU/MCU)\nroutes video/audio streams"]
    TURN["TURN Server\n(relay for NAT traversal)"]
    MeetingDB["Meeting DB\n(Postgres)\nmeeting metadata, participants"]
    RecordSvc["Recording Service"]
    RecordStore["Recording Store\n(S3)"]

    ClientA -->|"UDP/WebRTC"| Media
    ClientB -->|"UDP/WebRTC"| Media
    ClientC -->|"UDP/WebRTC"| Media
    Media -->|"video/audio"| ClientA
    Media -->|"video/audio"| ClientB
    Media -->|"video/audio"| ClientC
    ClientA -->|"WSS signaling"| Signal
    Signal --> MeetingDB
    ClientA -->|"UDP relay"| TURN --> Media
    Media --> RecordSvc --> RecordStore
```

### Happy Path — Joining a Meeting

```mermaid
sequenceDiagram
    participant C as Client
    participant SS as Signaling Server
    participant MS as Media Server
    participant DB as Meeting DB

    C->>SS: WS connect + {meeting_id, token}
    SS->>DB: Validate meeting, check participant limit
    SS->>SS: Select nearest media server for participant
    SS-->>C: {media_server_ip, ice_candidates}
    C->>MS: WebRTC handshake (ICE, DTLS, SRTP setup)
    MS-->>C: Connection established
    C->>MS: Start sending video/audio (UDP)
    MS->>MS: Forward streams to other participants
    MS->>C: Receive other participants' streams
    Note over C: Video call active
```

---

## Step 4 — Detailed Design

### 4.1 Media Architecture — SFU vs. MCU vs. P2P

This is the most important architectural decision in video conferencing.

```mermaid
graph TD
    P2P["P2P (Peer-to-Peer)\nEach participant sends\nto every other participant\ndirectly"]
    MCU["MCU (Multipoint Control Unit)\nServer decodes all streams,\nmixes into one stream,\nre-encodes and sends\none stream to each participant"]
    SFU["SFU (Selective Forwarding Unit)\nServer receives streams\nand forwards selectively\nto each participant\n(no decode/re-encode)"]

    P2P -->|"Pro"| P2P_Pro["No server needed\nLowest latency"]
    P2P -->|"Con"| P2P_Con["N² connections\nBreaks at 4+ participants"]
    MCU -->|"Pro"| MCU_Pro["One stream per participant\nLow client bandwidth"]
    MCU -->|"Con"| MCU_Con["High server CPU\n(decode + re-encode all streams)"]
    SFU -->|"Pro"| SFU_Pro["Low server CPU\nFlexible quality per participant"]
    SFU -->|"Con"| SFU_Con["Higher client bandwidth\n(receives N streams)"]
```

**Zoom uses SFU** for most meetings. The SFU receives one stream from each participant and forwards selectively — it only sends you the streams you need (active speaker + a few others), not all 100 streams in a large meeting.

**Active speaker detection:** The SFU monitors audio levels and identifies who is speaking. It prioritizes sending the active speaker's video at high quality and reduces quality for silent participants. This is why Zoom automatically switches the large video tile to whoever is talking.

### 4.2 NAT Traversal — Getting Through Firewalls

Most participants are behind NAT (home routers, corporate firewalls). Direct UDP connections between participants often fail. The solution: ICE (Interactive Connectivity Establishment) with STUN and TURN servers.

```mermaid
flowchart TD
    Try1["Try direct connection\n(host candidates)"]
    Try2["Try STUN\n(discover public IP/port,\nattempt hole-punching)"]
    Try3["TURN relay\n(all traffic relayed\nthrough TURN server)"]
    Success["Connection established"]

    Try1 -->|"fails (NAT)"| Try2
    Try2 -->|"fails (symmetric NAT)"| Try3
    Try1 & Try2 & Try3 --> Success
```

TURN servers are expensive (they relay all media traffic). Zoom minimizes TURN usage by trying direct and STUN connections first. Only ~10-15% of connections need TURN.

### 4.3 Adaptive Bitrate — Handling Bad Networks

Participants have different network conditions. The SFU uses simulcast to handle this:

```mermaid
graph TD
    Sender["Participant A\nsends 3 quality levels simultaneously:\n- High: 1080p @ 3 Mbps\n- Medium: 720p @ 1 Mbps\n- Low: 360p @ 300 Kbps"]
    SFU["SFU\nmonitors each receiver's\nbandwidth and packet loss"]
    RecvGood["Participant B\n(good connection)\nreceives High quality"]
    RecvBad["Participant C\n(poor connection)\nreceives Low quality"]

    Sender --> SFU
    SFU --> RecvGood
    SFU --> RecvBad
```

**Simulcast:** The sender encodes and sends 3 quality levels simultaneously. The SFU selects which level to forward to each receiver based on their current bandwidth. Quality switches happen at keyframe boundaries (every ~1s) to avoid visual artifacts.

### 4.4 Global Media Server Distribution

```mermaid
graph TD
    ParticipantUS["US Participant"]
    ParticipantEU["EU Participant"]
    ParticipantAS["Asia Participant"]
    MediaUS["Media Server\nUS-East"]
    MediaEU["Media Server\nEurope"]
    MediaAS["Media Server\nAsia"]
    Cascade["Cascade link\n(server-to-server)\nfor cross-region meetings"]

    ParticipantUS --> MediaUS
    ParticipantEU --> MediaEU
    ParticipantAS --> MediaAS
    MediaUS <-->|"cascade"| MediaEU
    MediaEU <-->|"cascade"| MediaAS
```

For a meeting with participants in the US, Europe, and Asia:
- Each participant connects to their nearest media server
- Media servers are linked via cascade connections (server-to-server streams)
- Each participant receives streams from their local media server, not from across the world
- This keeps end-to-end latency low even for global meetings

### 4.5 Recording

```mermaid
flowchart LR
    SFU["SFU\n(receives all streams)"]
    Recorder["Recording Service\n(subscribes to SFU\nas a special participant)"]
    Mix["Mix audio + video\n(MCU-style, only for recording)"]
    Store["Store to S3\n(MP4 format)"]
    Process["Post-processing:\ntranscription, chapters,\nsearch indexing"]

    SFU --> Recorder --> Mix --> Store --> Process
```

Recording is handled by a special "participant" that subscribes to all streams from the SFU. It mixes them server-side (MCU-style) to produce a single MP4 file. This is acceptable for recording because latency doesn't matter — it's post-processed.

---

## Step 5 — Decision Log

| Decision | Options | Choice | Rationale |
|----------|---------|--------|-----------|
| Media architecture | P2P / MCU / SFU | SFU | P2P breaks at scale; MCU is too CPU-intensive; SFU balances server cost and client bandwidth |
| Transport protocol | TCP / UDP (WebRTC) | UDP | Audio latency < 150ms requires UDP; TCP retransmission adds unacceptable delay |
| Quality adaptation | Fixed / Simulcast | Simulcast | Sender encodes once at 3 levels; SFU selects per-receiver; no re-encoding needed |
| Global distribution | Centralized / Edge media servers | Edge media servers | 60 Tbps cannot come from one location; latency requires proximity |
| Recording | Client-side / Server-side | Server-side (SFU subscriber) | Client recording depends on client staying connected; server recording is reliable |

---

## Step 6 — Bottlenecks

| Bottleneck | Mitigation |
|------------|-----------|
| Large meeting (1,000 participants) | SFU only forwards active speaker + gallery view subset; most participants receive 25 streams max, not 999 |
| Media server overload | Each media server handles ~500 concurrent meetings; auto-scale; consistent hash meeting_id to server |
| TURN server bandwidth | TURN is last resort; minimize usage; TURN servers are bandwidth-heavy, scale separately |
| Cross-region cascade latency | Minimize cascade hops; route participants to nearest server; accept slightly higher latency for cross-region meetings |
| Packet loss | FEC (Forward Error Correction) adds redundancy; NACK (negative acknowledgment) requests retransmission for video; audio uses PLC (packet loss concealment) |

---

## Interviewer Mode — Hard Follow-Up Questions

---

**Q1: "You said Zoom uses UDP for audio/video. UDP has no delivery guarantee. A packet is lost. What happens to the audio — does the user hear a glitch?"**

> It depends on the loss rate and the recovery mechanism. For audio, Zoom uses two techniques. First, FEC (Forward Error Correction): the sender adds redundant data to every N packets so that any single lost packet can be reconstructed from the others. For example, every 5th packet contains a XOR of the previous 4 — if packet 3 is lost, it can be reconstructed from packets 1, 2, 4, and the parity packet. This adds ~20% bandwidth overhead but eliminates audible glitches for single packet losses. Second, PLC (Packet Loss Concealment): if a packet is lost and can't be recovered via FEC (e.g., burst loss), the audio codec (Opus) generates a synthetic continuation of the audio based on the previous frames. For speech, this sounds like a very brief stutter — barely noticeable at < 5% loss. At > 10% loss, audio quality degrades noticeably. For video, lost packets cause visual artifacts (blocky frames) rather than freezes — the decoder renders what it has. The key insight: UDP + FEC + PLC gives better perceived quality than TCP for real-time audio, because TCP's retransmission adds 100-200ms of latency (waiting for the retransmit), which is far more disruptive than a brief audio glitch.

---

**Q2: "A 500-person all-hands meeting on Zoom. The CEO is presenting. 499 people are watching. How many video streams are being transmitted, and how does the SFU manage this?"**

> The CEO sends 1 video stream (simulcast: 3 quality levels). The SFU receives these 3 streams. For the 499 viewers: each viewer receives 1 stream — the CEO's video at the quality level appropriate for their bandwidth. The SFU forwards the CEO's stream to all 499 viewers. Total streams: 3 sent by CEO + 499 received by viewers = 502 streams through the SFU. But the 499 viewers also each send their own video (even if their camera is off, they send a minimal stream for presence). So total: 500 streams into the SFU + 500 streams out = 1,000 streams. The SFU's bandwidth: 500 × 1Mbps in + 500 × 1Mbps out = 1Gbps. A single SFU server handles this easily (modern servers have 10Gbps NICs). The CPU load: the SFU doesn't decode/re-encode — it just forwards packets. CPU usage is minimal. The real constraint is the viewer's experience: each viewer receives only the CEO's stream (active speaker) plus small thumbnails of other participants. The SFU uses active speaker detection to decide which stream to prioritize for each viewer.

---

**Q3: "Zoom's end-to-end encryption feature means the server can't decrypt video. But Zoom also offers cloud recording. How can you record something you can't decrypt?"**

> These two features are mutually exclusive — you can't have both simultaneously. When E2E encryption is enabled, cloud recording is disabled. The recording button is grayed out. This is an intentional design decision, not a limitation to be engineered around. When E2E encryption is off (the default for most meetings), the SFU can decrypt the streams (it holds the session keys) and the Recording Service subscribes to the SFU as a special participant, receives the decrypted streams, mixes them, and writes to S3. When E2E encryption is on, the SFU only sees encrypted packets it cannot decrypt. Recording is only possible locally — the meeting host's client decrypts the streams (it has the keys) and records locally. The architectural lesson: security and convenience are genuinely in tension. Zoom made the right call by being explicit about the trade-off rather than trying to engineer around it with a backdoor.

---

**Q4: "A participant's internet connection drops mid-meeting. They reconnect 30 seconds later. What did they miss, and how does the system handle their reconnection?"**

> They missed 30 seconds of audio/video — this is unrecoverable for real-time streams. Unlike messaging (where you can replay missed messages), video frames are ephemeral. The SFU doesn't buffer video for reconnecting participants. On reconnection: the client re-establishes the WebSocket signaling connection, re-does the WebRTC handshake with the SFU (ICE, DTLS, SRTP), and starts receiving the live stream again. This takes 2-5 seconds. During this window, the participant sees a "reconnecting" spinner. The meeting continues without them — other participants see their video tile as frozen or blank. The participant's audio is muted automatically during reconnection to prevent noise. For the missed content: if cloud recording is enabled, the participant can watch the recording later. If not, they missed it. The host can also use the "recap" feature (if enabled) to summarize what was discussed. The key design point: real-time video is not a store-and-forward system. Reconnection means rejoining the live stream, not replaying the missed portion.

---

**Q5: "Zoom has a waiting room feature — the host must admit each participant. With 500 participants joining simultaneously (large webinar), how does the waiting room scale?"**

> The waiting room is a state machine per participant, not a queue. Each participant who joins is in `WAITING` state, stored in Redis: `waiting_room:{meeting_id}` → set of `{participant_id, name, join_time}`. The host's client subscribes to this set and receives real-time updates as participants join. For 500 simultaneous joins: 500 writes to Redis (fast, sub-millisecond each), 500 notifications pushed to the host's client via WebSocket. The host's UI shows a list of 500 waiting participants. The host can "Admit All" (one click → 500 state transitions from WAITING to ADMITTED) or admit individually. The "Admit All" operation: the Signaling Service receives the command, updates all 500 participant states in Redis in a pipeline (batch operation), and sends 500 WebSocket messages to the waiting participants' clients. Each client receives "admitted" and initiates the WebRTC handshake. The 500 simultaneous WebRTC handshakes are the real bottleneck — each requires CPU for DTLS key exchange. The SFU handles this by queuing handshakes and processing them at ~100/second, so all 500 are admitted within 5 seconds.
