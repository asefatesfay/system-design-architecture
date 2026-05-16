# API Design Walkthrough — Uber

> Detailed API design for the critical paths of a ride-hailing platform. Focus areas: ride request, real-time driver matching, live trip tracking, fare estimation, and payment. These paths are latency-sensitive, geo-distributed, and have strong consistency requirements around money.

---

## 1. Overview & Scope

### In Scope

| Capability | Critical? |
|------------|-----------|
| Fare estimation | Yes — first thing a rider sees |
| Ride request (booking) | Yes — core transaction |
| Driver matching & acceptance | Yes — real-time, latency-sensitive |
| Trip tracking (driver location) | Yes — WebSocket push |
| Trip completion & fare capture | Yes — involves payment |
| Payment method management | Yes |
| Trip history | Secondary |
| Driver onboarding | Out of scope |
| Surge pricing algorithm | Out of scope |
| Driver earnings | Out of scope |

### Traffic Profile (assumed)

| Metric | Value |
|--------|-------|
| Active markets | 70+ countries |
| Trips / day | ~25 M |
| Peak ride requests / s | ~3,000 |
| Driver location updates / s | ~500,000 |
| Fare estimates / s | ~10,000 |
| Matching latency SLO | p99 < 5 s end-to-end |
| Location update latency | p99 < 1 s |

---

## 2. Data Model

```mermaid
erDiagram
    User {
        UUID id PK
        string phone
        string display_name
        string email
        UUID default_payment FK
        timestamp created_at
    }
    Driver {
        UUID id PK
        UUID user_id FK
        string license_plate
        enum vehicle_type
        enum status
        geo_point location
        timestamp updated_at
    }
    PaymentMethod {
        UUID id PK
        UUID owner_id FK
        enum type
        string display_name
        bool is_default
        string provider_token
    }
    Estimate {
        UUID id PK
        UUID rider_id FK
        geo_point pickup
        geo_point dropoff
        enum vehicle_type
        decimal fare_min
        decimal fare_max
        string currency
        int eta_seconds
        int distance_m
        int duration_s
        decimal surge_multiplier
        timestamp expires_at
    }
    Trip {
        UUID id PK
        UUID rider_id FK
        UUID driver_id FK
        UUID estimate_id FK
        UUID payment_method_id FK
        geo_point pickup
        geo_point dropoff
        enum vehicle_type
        enum status
        decimal fare_estimate
        decimal fare_final
        string currency
        string cancel_reason
        timestamp started_at
        timestamp completed_at
        timestamp created_at
    }
    TripEvent {
        UUID id PK
        UUID trip_id FK
        enum type
        UUID actor_id
        jsonb metadata
        timestamp occurred_at
    }
    DriverLocation {
        UUID driver_id FK
        float lat
        float lng
        int heading
        float speed_kmh
        timestamp recorded_at
    }

    User ||--o| Driver : "is a"
    User ||--o{ PaymentMethod : owns
    User ||--o{ Estimate : requests
    User ||--o{ Trip : "rides as rider"
    Driver ||--o{ Trip : drives
    Driver ||--o{ DriverLocation : reports
    Estimate ||--o| Trip : "used for"
    Trip ||--o{ TripEvent : generates
    PaymentMethod ||--o{ Trip : "charged for"
```

### Trip Status State Machine

```mermaid
stateDiagram-v2
    [*] --> matching : POST /v1/trips
    matching --> accepted : driver accepts offer
    matching --> cancelled : rider cancels
    accepted --> driver_arriving : driver confirms pickup_reached
    accepted --> cancelled : rider cancels (fee may apply)
    driver_arriving --> in_progress : driver confirms trip_started
    driver_arriving --> cancelled : rider cancels (fee applies)
    in_progress --> completed : driver confirms trip_completed
    completed --> [*]
    cancelled --> [*]
```

### 2.1 Estimate vs Trip: API and System Design Impact

`Estimate` and `Trip` are related but optimized for different goals.

| Dimension | Estimate | Trip |
|-----------|----------|------|
| Product intent | Fast preview before booking | Actual booked ride lifecycle |
| Lifetime | Short-lived (minutes) | Durable and auditable |
| Consistency need | Approximate is acceptable | Strong correctness needed |
| Main read pattern | Quick comparison across vehicle types | Status updates, history, and receipt |
| Main write pattern | Side-effect-light request | Stateful transitions and money movement |

#### API design perspective

| API aspect | Estimate design | Trip design |
|------------|-----------------|------------|
| Endpoint behavior | Synchronous request/response | Async create (`202`) + realtime updates |
| Response shape | Multiple options (economy/comfort/xl) | Single trip state object |
| Expiration | TTL-based (`expires_at`) | State machine (`matching -> accepted -> in_progress -> completed`) |
| Idempotency need | Usually not required | Required for booking, accept, and trip events |
| Error sensitivity | Service area/supply variability | Matching races, cancellation semantics, payment correctness |

#### System design perspective

| System aspect | Estimate impact | Trip impact |
|---------------|-----------------|------------|
| Storage | TTL cache/table entries | Durable trip row + event log |
| Compute | Parallel reads from geo/pricing/supply | Async workflow across matching, location, and payment |
| First scaling bottleneck | Read fanout latency | Match latency and write coordination |
| Failure mode | Stale or expired estimate | Driver double-assignment or payment inconsistency |

Design rule:

- Model `Estimate` for speed and expiry.
- Model `Trip` for correctness and lifecycle state transitions.

---

## 3. Authentication

Uber has two actor types: **Riders** (mobile client) and **Drivers** (driver app). Both use OAuth 2.0 with JWT access tokens.

### Rider Token

```
POST /v1/auth/token
Content-Type: application/json

{
  "grant_type": "otp",
  "phone":      "+12025550182",
  "otp":        "847291"
}
```

```json
HTTP/1.1 200 OK
{
  "access_token":  "eyJ...",
  "token_type":    "Bearer",
  "expires_in":    3600,
  "refresh_token": "dGhp...",
  "actor_type":    "rider"
}
```

### Driver Token

Same endpoint; `actor_type` will be `driver` in the returned token claims.

All requests carry:

```
Authorization: Bearer <access_token>
X-Actor-Type: rider | driver
```

Server validates `actor_type` claim on every request. A rider token cannot call driver-only endpoints and vice-versa.

---

## 4. Versioning Strategy

- URL prefix versioning: `/v1/`, `/v2/`
- Breaking changes trigger a major version; additive changes do not
- Deprecated endpoints carry `Sunset` header (12-month support window)
- Driver app and rider app pin to a version; forced-upgrade mechanism exists outside the API

### 4.1 API Style Selection (REST vs WebSocket vs gRPC)

Uber-like systems are hybrid. Each protocol maps to a specific traffic pattern.

| Style | Best For | Why | Common Tradeoff |
|-------|----------|-----|-----------------|
| REST | Estimates, booking, payment methods, trip events | Simple public API contracts and broad client support | Polling-heavy flows can be inefficient |
| WebSocket | Rider trip state and live location | Low-latency push for realtime UX | Connection lifecycle and fanout complexity |
| gRPC | Internal geo/pricing/supply/matching/payment calls | Fast service-to-service communication with strong contracts | Not ideal for direct browser/mobile public clients |

#### Uber-specific recommendation

- Use REST for rider/driver control-plane actions.
- Use WebSocket for rider-facing realtime updates.
- Use gRPC for internal low-latency service calls.
- Use event bus topics for asynchronous trip lifecycle propagation.

### 4.2 Delivery Mechanisms (Polling, WebSocket, Webhooks, Streams)

| Mechanism | Model | Direction | Best use cases in ride hailing | Avoid When |
|-----------|-------|-----------|--------------------------------|------------|
| Polling | Pull | Client -> Server | Fallback trip status checks | Live map updates |
| WebSocket | Push/pull | Client <-> Server | Driver location and trip state push | Infra cannot handle persistent connections |
| Webhook | Push callback | Server -> Server | External partner callbacks and payment notifications | Consumer endpoint reliability is weak |
| Event stream/queue | Async event bus | Service -> Service | Ride requested, driver assigned, trip completed, payment captured | Immediate synchronous response is required |

Quick selection rule:

- Need immediate user response: REST.
- Need live UI updates: WebSocket.
- Need async backend propagation: event stream.
- Need external async notification: webhook.

---

## 5. Critical Path 1 — Fare Estimation

The fare estimate is the **entry point** for every ride. It must be fast (< 500 ms p99) and accurate enough that the actual fare is almost never a surprise.

### 5.1 Endpoint

```
POST /v1/estimates
Authorization: Bearer <token>
Content-Type: application/json

{
  "pickup": {
    "lat": 40.748817,
    "lng": -73.985428,
    "address": "350 5th Ave, New York, NY 10118"
  },
  "dropoff": {
    "lat": 40.712776,
    "lng": -74.005974,
    "address": "1 World Trade Center, New York, NY 10007"
  },
  "vehicle_types": ["economy", "comfort", "xl"]
}
```

> `vehicle_types` is optional. Omitting it returns estimates for all available types.

### 5.2 Response — 200 OK

```json
{
  "estimates": [
    {
      "id":               "est_4kL5mN",
      "vehicle_type":     "economy",
      "fare_min":         14.50,
      "fare_max":         18.00,
      "currency":         "USD",
      "eta_seconds":      240,
      "distance_m":       6800,
      "duration_s":       1080,
      "surge_multiplier": 1.0,
      "surge_active":     false,
      "expires_at":       "2026-05-15T16:02:00Z"
    },
    {
      "id":               "est_6oP7qR",
      "vehicle_type":     "comfort",
      "fare_min":         19.00,
      "fare_max":         24.00,
      "currency":         "USD",
      "eta_seconds":      180,
      "distance_m":       6800,
      "duration_s":       1080,
      "surge_multiplier": 1.2,
      "surge_active":     true,
      "expires_at":       "2026-05-15T16:02:00Z"
    }
  ]
}
```

### 5.3 Internal Flow

```mermaid
flowchart LR
    C([Client]) --> G[API Gateway]
    G --> ES[Estimate Service]

    subgraph parallel [" "]
        GEO[Geo Service\nroute distance + duration]
        PRC[Pricing Service\nbase fare × surge × distance]
        SUP[Supply Service\nnearest drivers → ETA]
    end

    ES --> parallel
    parallel --> ES
    ES --> DB[(Store Estimate\nTTL 2 min)]
    ES --> R([200 OK to Client])
```

#### Plain-English definitions used below

| Term | Plain-English definition | Example |
|------|--------------------------|---------|
| `ETA` | Estimated time for a driver to reach pickup. | `eta_seconds = 240` means about 4 minutes away. |
| `surge multiplier` | Demand/supply price multiplier applied to base fare. | `1.4x` surge increases a $10 base to about $14 before other fees. |
| `TTL` | How long temporary data remains valid. | Estimates are often valid for only about 2 minutes. |
| `parallel fan-out` | Calling multiple backend services at the same time. | Estimate service queries geo, pricing, and supply in parallel. |
| `service area` | Geographic boundary where the platform operates. | Pickup outside the market returns `outside_service_area`. |

#### Example latency budget for fare estimation

| Step | Target Budget | What happens here |
|------|---------------|-------------------|
| API Gateway auth + validation | 20 ms | Validate token and input |
| Geo route compute | 120 ms | Distance and duration estimate |
| Supply ETA lookup | 80 ms | Nearby available driver availability and ETA |
| Pricing compute | 60 ms | Fare min/max calculation with surge |
| Compose + TTL store write | 40 ms | Build estimate response and store short-lived estimate |
| Network + tail margin | 180 ms | Real-world jitter buffer |

Total target: about `500 ms p99`

Annotated request path:

```mermaid
flowchart LR
  C[Client]
  G[API Gateway\n~20 ms]
  ES[Estimate Service]
  GEO[Geo Service\n~120 ms]
  SUP[Supply Service\n~80 ms]
  PRC[Pricing Service\n~60 ms]
  DB[Estimate TTL Store\n~40 ms]
  N[Network and tail margin\n~180 ms]
  O[Estimate response]

  C --> G --> ES
  ES --> GEO
  ES --> SUP
  ES --> PRC
  GEO --> ES
  SUP --> ES
  PRC --> ES
  ES --> DB --> N --> O
```

### 5.4 Edge Cases

| Scenario | Behavior |
|----------|----------|
| No drivers available in area | `eta_seconds` absent; `"available": false` |
| Unsupported vehicle type | Excluded from response (not an error) |
| Pickup outside service area | `422` with `{ "code": "outside_service_area" }` |
| Estimate expired and used for booking | `409` with `{ "code": "estimate_expired" }` |

---

## 6. Critical Path 2 — Ride Request & Driver Matching

This is the **most critical write path** in the system. A ride request must be atomic, matched quickly, and never double-booked.

### 6.1 Step-by-step flow

```mermaid
sequenceDiagram
    participant R as Rider Client
    participant G as API Gateway
    participant T as Trip Service
    participant K as Kafka
    participant MS as Matching Service
    participant D as Driver App

    R->>G: POST /v1/trips (estimate_id, payment_method_id)
    G->>T: create Trip (status=matching)
    T->>K: publish RideRequested event
    T-->>G: trip_id
    G-->>R: 202 { trip_id, status: matching }

    K-->>MS: consume RideRequested
    MS->>MS: query S2 geospatial index for drivers
    MS->>D: dispatch ride offer to top-N drivers
    D-->>MS: driver accepts
    MS->>T: DriverAssigned event
    T->>T: update Trip status = accepted
    T-->>R: WS push trip_updated { driver, eta }
```

### 6.2 Request a Ride

```
POST /v1/trips
Authorization: Bearer <token>
Content-Type: application/json
Idempotency-Key: a3f1b2c4-d5e6-7890-abcd-ef1234567890

{
  "estimate_id":         "est_4kL5mN",
  "payment_method_id":   "pm_8sT9uV",
  "notes":               "Gate code is 1234"
}
```

**Response — 202 Accepted**

```json
{
  "trip_id":    "trp_2wX3yZ",
  "status":     "matching",
  "created_at": "2026-05-15T16:00:00Z"
}
```

`202` because matching is **asynchronous**. The client must subscribe to updates via WebSocket (see §8) or poll `GET /v1/trips/trp_2wX3yZ`.

### 6.3 Poll Trip Status

```
GET /v1/trips/trp_2wX3yZ
Authorization: Bearer <token>
```

**Response — 200 OK (matching)**

```json
{
  "id":     "trp_2wX3yZ",
  "status": "matching"
}
```

**Response — 200 OK (driver accepted)**

```json
{
  "id":     "trp_2wX3yZ",
  "status": "accepted",
  "driver": {
    "id":            "drv_1aB2cD",
    "display_name":  "Marcus T.",
    "avatar_url":    "https://cdn.uber.example/avatars/drv_1aB2cD.jpg",
    "rating":        4.87,
    "vehicle": {
      "make":         "Toyota",
      "model":        "Camry",
      "color":        "Silver",
      "license_plate":"ABC-1234",
      "type":         "economy"
    }
  },
  "eta_seconds":      190,
  "pickup": {
    "lat":     40.748817,
    "lng":    -73.985428,
    "address": "350 5th Ave, New York, NY 10118"
  },
  "dropoff": {
    "lat":     40.712776,
    "lng":    -74.005974,
    "address": "1 World Trade Center, New York, NY 10007"
  },
  "fare_estimate": 14.50,
  "currency":      "USD",
  "created_at":    "2026-05-15T16:00:00Z"
}
```

### 6.4 Cancel a Trip

```
DELETE /v1/trips/trp_2wX3yZ
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "plans_changed"
}
```

`reason` ∈ `{ "plans_changed", "driver_too_far", "wrong_vehicle", "other" }`

**Response — 200 OK**

```json
{
  "trip_id":          "trp_2wX3yZ",
  "status":           "cancelled",
  "cancellation_fee": 0.00,
  "currency":         "USD"
}
```

> Cancellation fee may be non-zero if driver has already arrived (configurable per market).

### 6.5 Driver: Accept a Ride (Driver App)

```
POST /v1/driver/trips/trp_2wX3yZ/accept
Authorization: Bearer <driver_token>
Idempotency-Key: <uuid>
```

**Response — 200 OK**

```json
{
  "trip_id":  "trp_2wX3yZ",
  "status":   "accepted",
  "rider": {
    "display_name": "Alice M.",
    "avatar_url":   "https://cdn.uber.example/avatars/usr_4xK8mN.jpg",
    "rating":       4.9
  },
  "pickup": {
    "lat":     40.748817,
    "lng":    -73.985428,
    "address": "350 5th Ave, New York, NY 10118"
  }
}
```

**Response — 409 Conflict** (trip already claimed by another driver)

```json
{
  "type":   "https://developers.uber.example/errors/trip_already_claimed",
  "title":  "Trip Already Claimed",
  "status": 409,
  "detail": "Another driver accepted this trip first."
}
```

### 6.6 Matching Algorithm (context)

Matching runs outside the REST layer, in a dedicated service. The REST API is the **control plane**; the matching engine is the **data plane**.

```mermaid
flowchart TD
    A([RideRequested event\nfrom Kafka]) --> B[Query S2 geospatial index\ndrivers within 5 km]
    B --> C[Score candidates\ndistance × eta + acceptance_rate]
    C --> D[Dispatch offer to\ntop-N drivers in parallel]
    D --> E{First driver\naccepts?}
    E -- yes --> F[Optimistic lock\non Trip row]
    F --> G{Lock\nacquired?}
    G -- yes --> H[Publish DriverAssigned event]
    G -- no: race lost --> I([Return 409 to that driver])
    H --> J[Trip Service\nstatus = accepted]
    J --> K([WS push to rider])
    E -- timeout / all reject --> L([No match: notify rider])
```

#### Plain-English definitions used below

| Term | Plain-English definition | Example |
|------|--------------------------|---------|
| `control plane` | API path that starts or changes workflow state. | `POST /v1/trips` starts matching. |
| `data plane` | Internal realtime path that executes matching and assignment. | Matching service selecting drivers is data-plane work. |
| `S2 geospatial index` | Earth is split into cells so nearby entities are found quickly. | Querying nearby cells returns candidate drivers within ~5 km. |
| `optimistic locking` | First valid updater wins; later conflicting updaters fail cleanly. | Two drivers accept; one succeeds, one receives `409`. |
| `dispatch offer` | Temporary request sent to a driver to accept a trip. | Matching sends offer to top 3 candidates. |

### 6.7 Matching and Geo Services (deeper design)

High-level matching pipeline:

1. Candidate lookup
2. Eligibility filtering
3. Candidate scoring
4. Offer dispatch
5. Winner commit

#### 1) Candidate lookup

Use geospatial index over live driver locations to find nearby available drivers quickly.

#### 2) Eligibility filtering

Remove candidates that cannot take the ride:

- wrong vehicle type
- offline or already assigned
- too far from pickup
- zone/market restrictions

#### 3) Candidate scoring

A simple conceptual scoring model:

$$
score(driver, trip) =
w_1 \cdot proximity(driver, pickup)
+ w_2 \cdot eta(driver, pickup)^{-1}
+ w_3 \cdot acceptance\_rate(driver)
+ w_4 \cdot reliability(driver)
- w_5 \cdot detour\_cost(driver)
$$

#### 4) Offer dispatch

- Sequential offers reduce race conflicts but add latency.
- Small parallel batches reduce latency but increase conflict handling.

Most large systems choose small parallel batches because rider latency is critical.

#### 5) Winner commit

Use atomic compare-and-set on the trip row so only one driver assignment wins.

Example pseudo-flow:

```text
trip = TripStore.Get(trip_id)
candidates = GeoIndex.FindAvailableDrivers(trip.pickup, radius=5km)
eligible = FilterByEligibility(candidates, trip.vehicle_type)
scored = ScoreDrivers(eligible, trip)
offers = TopN(scored, 3)
DispatchOffers(offers, trip_id)

on DriverAccept(driver_id, trip_id):
  ok = TripStore.CompareAndSet(trip_id, expected="matching", next="accepted")
  if ok: publish DriverAssigned
  else: return conflict
```

Worked example:

| Driver | Distance | ETA | Acceptance rate | Likely rank |
|--------|----------|-----|-----------------|-------------|
| D1 | 400 m | 3 min | 0.62 | High proximity but weaker reliability |
| D2 | 650 m | 4 min | 0.92 | Often best overall pick |
| D3 | 900 m | 6 min | 0.95 | Reliable but potentially too far |

### 6.8 Example latency budget for ride request and matching

| Step | Target Budget | What happens here |
|------|---------------|-------------------|
| Trip create API | 50 ms | Validate request and create `matching` trip |
| Event publish | 20 ms | Publish `RideRequested` |
| Candidate lookup | 500 ms | Geo index nearby driver search |
| Eligibility + scoring | 300 ms | Filter and rank candidates |
| Offer dispatch + accept | 1 s to 3 s | Driver acceptance window |
| Winner commit | 50 ms | Atomic update to `accepted` |
| Rider update push | 100 ms | Notify rider via WebSocket |

Annotated request path:

```mermaid
flowchart LR
    R[Rider Client]
    T[Trip Create API\n~50 ms]
    E[Publish RideRequested\n~20 ms]
    G[Geo Candidate Lookup\n~500 ms]
    S[Eligibility and Scoring\n~300 ms]
    D[Dispatch and Driver Accept\n~1 to 3 s]
    C[Winner Commit\n~50 ms]
    P[Push to Rider\n~100 ms]
    O[Trip accepted]

    R --> T --> E --> G --> S --> D --> C --> P --> O
```

---

## 7. Critical Path 3 — Live Trip Tracking

### 7.1 Location Tracking Flow

```mermaid
sequenceDiagram
    participant DA as Driver App
    participant IG as Ingestion Gateway
    participant R as Redis
    participant K as Kafka
    participant WS as WebSocket Server
    participant RA as Rider App

    RA->>WS: GET /v1/ws (WebSocket upgrade)
    WS-->>RA: 101 Switching Protocols

    loop every ~1 second
        DA->>IG: POST /v1/driver/location
        IG-->>DA: 204 No Content
        IG->>R: update driver:{id} lat/lng (hot cache)
        IG->>K: publish LocationUpdated event
        K-->>WS: consume LocationUpdated
        WS-->>RA: push driver_location { lat, lng, eta_seconds }
    end
```

### 7.2 Driver Location Publish (Driver App → Server)

Driver app sends location at ~1 Hz.

```
POST /v1/driver/location
Authorization: Bearer <driver_token>
Content-Type: application/json

{
  "lat":       40.750123,
  "lng":      -73.987456,
  "heading":   215,
  "speed_kmh": 32.5,
  "recorded_at": "2026-05-15T16:05:00.000Z"
}
```

**Response — 204 No Content**

This endpoint is optimized for throughput: no response body, fire-and-forget from the driver app's perspective. The server persists to Redis (hot) and Kafka (durable) asynchronously.

> At 500k updates/s, this endpoint sits behind a dedicated ingestion gateway (no auth middleware overhead — token is validated at the edge and a lightweight session claim propagates inward).

### 7.2 Rider Receives Location (WebSocket)

Rather than polling, the rider client maintains a WebSocket connection.

**Connection**

```
GET /v1/ws
Authorization: Bearer <token>
Upgrade: websocket
```

**Server-pushed message (JSON over WebSocket)**

```json
{
  "event":   "driver_location",
  "trip_id": "trp_2wX3yZ",
  "driver": {
    "lat":       40.750123,
    "lng":      -73.987456,
    "heading":   215,
    "eta_seconds": 140
  },
  "ts": "2026-05-15T16:05:01.000Z"
}
```

**Other events pushed on the same connection**

| Event | When |
|-------|------|
| `trip_updated` | Trip status changes (accepted, driver_arriving, in_progress, completed) |
| `driver_location` | Every driver location update for the active trip |
| `fare_updated` | Surge multiplier changes mid-estimate |
| `ping` | Keepalive every 30s; client replies with `pong` |

### 7.3 WebSocket Reconnect Strategy

Client should reconnect with **exponential backoff** (500ms, 1s, 2s, 4s, max 30s) on disconnect. Reconnect includes the last known `trip_id` so the server can replay any missed events:

```
GET /v1/ws?resume_trip=trp_2wX3yZ&last_event_ts=1715790300000
```

#### Plain-English definitions used below

| Term | Plain-English definition | Example |
|------|--------------------------|---------|
| `ingestion gateway` | A lightweight service dedicated to very high-volume writes. | Driver location updates go to ingestion gateway, not the full API stack. |
| `hot cache` | Fast storage with latest values for realtime reads. | Redis stores the newest location for each driver. |
| `keepalive` | Periodic signal to keep a connection active. | Server sends `ping`, client responds with `pong`. |
| `replay` | Resending events missed during disconnection. | Rider reconnects and receives missed `trip_updated` events. |

### 7.4 Realtime location pipeline design

Separate concerns for scale:

- ingest path: maximize write throughput from driver apps
- fanout path: minimize latency when pushing only relevant updates to riders

Pipeline:

1. Driver sends location (~1 Hz)
2. Gateway validates lightweight session claims
3. Write latest point to hot cache
4. Publish location event to stream
5. WebSocket layer routes only subscribed trip events
6. Rider receives update

This split prevents ingest spikes from degrading rider push latency.

### 7.5 Example latency budget for live location

| Step | Target Budget | What happens here |
|------|---------------|-------------------|
| Driver -> ingestion gateway | 100 ms | Driver update reaches nearest edge |
| Gateway -> Redis/Kafka | 100 ms | Persist latest point and publish event |
| Event stream -> WS fanout | 300 ms | Consumer routing and per-trip filtering |
| WS push -> rider render | 300 ms | Push arrives and UI updates |
| Total target | `<= 1 s p99` | Matches live trip SLA |

Annotated request path:

```mermaid
flowchart LR
  D[Driver App]
  IG[Ingestion Gateway\n~100 ms]
  HC[Hot Cache Redis]
  K[(Event Stream)\n~100 ms publish]
  WS[WebSocket Fanout\n~300 ms routing]
  R[Rider App\n~300 ms push and render]

  D --> IG --> HC
  IG --> K --> WS --> R
```

---

## 8. Critical Path 4 — Trip Completion & Payment

### 8.1 Driver: Mark Pickup Reached

```
POST /v1/driver/trips/trp_2wX3yZ/events
Authorization: Bearer <driver_token>
Content-Type: application/json

{
  "type": "pickup_reached"
}
```

**Response — 200 OK**

```json
{
  "trip_id": "trp_2wX3yZ",
  "status":  "driver_arriving",
  "event_id":"evt_9kL0mN"
}
```

### 8.2 Driver: Start Trip

```
POST /v1/driver/trips/trp_2wX3yZ/events
Authorization: Bearer <driver_token>
Content-Type: application/json

{
  "type": "trip_started"
}
```

**Response — 200 OK**

```json
{
  "trip_id":    "trp_2wX3yZ",
  "status":     "in_progress",
  "started_at": "2026-05-15T16:12:00Z"
}
```

### 8.3 Driver: Complete Trip

```
POST /v1/driver/trips/trp_2wX3yZ/events
Authorization: Bearer <driver_token>
Content-Type: application/json

{
  "type":       "trip_completed",
  "dropoff": {
    "lat": 40.712776,
    "lng": -74.005974
  }
}
```

**Response — 200 OK**

```json
{
  "trip_id":       "trp_2wX3yZ",
  "status":        "completed",
  "fare_final":    15.75,
  "currency":      "USD",
  "completed_at":  "2026-05-15T16:28:00Z",
  "receipt_url":   "https://riders.uber.example/receipts/trp_2wX3yZ"
}
```

### 8.4 Payment Flow (Internal — context for the API contract)

```mermaid
flowchart TD
    A([Trip completion event]) --> B[Fare Engine\ncalculate_final_fare\ndistance + duration + surge]
    B --> C[Payment Service\ncharge payment_method\nidempotency_key = trip_id]
    C --> D{Charge\nresult}
    D -- success --> E[Update Trip\nfare_final + status=completed]
    E --> F([Push receipt\nto rider WebSocket])
    E --> G([Credit driver earnings])
    D -- failure --> H[Retry with\nexponential backoff\nmax 3 attempts]
    H --> I{Retries\nexhausted?}
    I -- no --> C
    I -- yes --> J[Mark Trip\npayment_failed]
    J --> K([Trigger async\nrecovery flow])
```

The `idempotency_key = trip_id` ensures the charge is never duplicated even if the payment service is retried.

### 8.5 Rider: Fetch Receipt

```
GET /v1/trips/trp_2wX3yZ/receipt
Authorization: Bearer <token>
```

**Response — 200 OK**

```json
{
  "trip_id":        "trp_2wX3yZ",
  "fare_breakdown": {
    "base_fare":     5.00,
    "distance_fare": 7.20,
    "time_fare":     2.16,
    "surge":         0.00,
    "booking_fee":   1.39,
    "total":        15.75
  },
  "currency":       "USD",
  "payment_method": "Visa ••••4242",
  "charged_at":     "2026-05-15T16:28:45Z",
  "map_url":        "https://riders.uber.example/receipts/trp_2wX3yZ/map.png"
}
```

---

## 9. Payment Method Management

### 9.1 List Payment Methods

```
GET /v1/payment-methods
Authorization: Bearer <token>
```

**Response — 200 OK**

```json
{
  "items": [
    {
      "id":           "pm_8sT9uV",
      "type":         "card",
      "display_name": "Visa ••••4242",
      "is_default":   true
    }
  ]
}
```

### 9.2 Add a Payment Method

```
POST /v1/payment-methods
Authorization: Bearer <token>
Content-Type: application/json
Idempotency-Key: <uuid>

{
  "type":             "card",
  "provider_token":   "tok_visa_4242",
  "set_as_default":   false
}
```

`provider_token` is obtained by the client directly from the payment processor SDK (e.g., Stripe.js). The Uber API never sees raw card data — this is a **PCI-compliant tokenization pattern**.

**Response — 201 Created**

```json
{
  "id":           "pm_1aB2cD",
  "type":         "card",
  "display_name": "Visa ••••4242",
  "is_default":   false
}
```

### 9.3 Delete a Payment Method

```
DELETE /v1/payment-methods/pm_1aB2cD
Authorization: Bearer <token>
```

**Response — 204 No Content**

Error if it is the only payment method or currently attached to an active trip:

```json
{
  "type":   "https://developers.uber.example/errors/payment_method_in_use",
  "title":  "Payment Method In Use",
  "status": 409,
  "detail": "This payment method is attached to an active trip (trp_2wX3yZ)."
}
```

---

## 10. Common API Concerns

### 10.1 Pagination (Trip History)

```
GET /v1/trips?limit=20&cursor=<opaque>
Authorization: Bearer <token>
```

```json
{
  "items": [ /* trip summaries */ ],
  "pagination": {
    "next_cursor": "eyJpZCI6InRycF8xMiIsInRzIjoxNzE1Nzg5OTAwfQ==",
    "has_more": true
  }
}
```

### 10.2 Error Format (RFC 9457)

```json
{
  "type":       "https://developers.uber.example/errors/estimate_expired",
  "title":      "Estimate Expired",
  "status":     409,
  "detail":     "Estimate est_4kL5mN expired at 2026-05-15T16:02:00Z. Request a new estimate.",
  "instance":   "/v1/trips",
  "request_id": "req_a1b2c3d4"
}
```

### 10.3 Rate Limiting

| Actor | Endpoint | Limit |
|-------|----------|-------|
| Rider | `POST /v1/estimates` | 30 req/min |
| Rider | `POST /v1/trips` | 5 req/min |
| Rider | `GET /v1/trips/*` | 120 req/min |
| Driver | `POST /v1/driver/location` | 120 req/min (1 Hz normal) |
| Driver | `POST /v1/driver/trips/*/events` | 20 req/min |

### 10.4 Idempotency

| Endpoint | Idempotency-Key required? | Key scope |
|----------|--------------------------|-----------|
| `POST /v1/estimates` | No (reads only, side-effect free) | — |
| `POST /v1/trips` | **Yes** | 24h |
| `POST /v1/driver/trips/*/accept` | **Yes** | Until trip resolved |
| `POST /v1/payment-methods` | **Yes** | 24h |
| `POST /v1/driver/trips/*/events` | **Yes** | Per event type per trip |

### 10.5 Geo Data Conventions

All coordinates use **WGS-84** decimal degrees. Maximum precision accepted: 6 decimal places (~0.1 m).

```json
{ "lat": 40.748817, "lng": -73.985428 }
```

`lng` is always `lng` (not `lon` or `longitude`) for consistency.

---

## 11. Design Decisions & Trade-offs

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| `202 Accepted` on trip creation | Matching is async; no driver may be available immediately | Client must handle matching state; more complex than synchronous |
| WebSocket for location push | ~1 Hz updates at 500k drivers is too much for polling | Requires persistent connection management (scaling with connection-aware load balancer) |
| `POST /v1/driver/location` (REST) | Simpler than WebSocket for a write-only unidirectional stream | Higher overhead than UDP/QUIC; acceptable at 1 Hz |
| Idempotency key = trip_id for payment | Natural idempotency key; avoids double charge on retry | Requires payment service to accept caller-supplied idempotency keys |
| PCI tokenization (provider_token) | Uber never stores raw card data; dramatically reduces PCI scope | Client must integrate payment SDK; server cannot validate card without calling processor |
| Fare min/max range (not exact) | Exact fare requires completed route; estimate is inherently uncertain | Creates UX trust risk if final fare is near or above max |
| Optimistic locking on driver accept | High throughput; minimal DB contention (only one driver wins per trip) | Losers get `409` — driver app must handle gracefully |
| S2 cell geospatial index | Hierarchical; efficient for "all drivers within radius" queries | Requires tuning cell level (L13 ≈ 1.2 km²) for local density |

---

## 12. System Bottlenecks & Scaling Triggers

As load grows, different subsystems become bottlenecks at different times. The key interview skill is to connect a trigger metric to a mitigation.

| Subsystem | Typical bottleneck | Trigger metric | Common mitigation |
|-----------|--------------------|----------------|-------------------|
| Estimate service | Dependency fanout latency | Estimate p99 rises above target | Cache common routes, tighten downstream SLAs, precompute hot corridors |
| Geo lookup | Dense-area spatial query cost | Candidate lookup latency spikes in city centers | Tune S2 levels, shard by market, cache hot pickup zones |
| Matching service | Candidate scoring and dispatch lag | Match time and cancel-before-match rise | Tune dispatch batch size, narrower staged radius expansion |
| Driver accept coordination | Race conflicts | `409` conflict rate grows | Shorter offer TTL, smaller batches, better optimistic lock handling |
| Location ingestion | High write throughput | Gateway saturation and dropped updates | Regional ingest edges, lightweight auth path, compression/batching |
| WebSocket fanout | Connection scale and routing | Push delay and reconnect rate rise | Partition sockets by market/trip, backpressure and degraded update modes |
| Payment path | Processor latency/retry backlog | Completion-to-charge delay grows | Async retries, circuit breakers, idempotent charge keys |
| Trip store | Hot state rows and replication lag | Slow status updates | Shard by trip/market, append-only trip event log, isolate hot tables |
| Event stream | Consumer lag on critical topics | Lag in `RideRequested` or `LocationUpdated` | More partitions, priority consumers, topic isolation |

How to use in interviews:

- name the hottest user path
- identify first bottleneck
- cite one trigger metric
- propose one concrete mitigation

Example:

- "In dense downtown peaks, matching is usually first bottleneck. Trigger is rising match latency and pre-match cancellation rate. Mitigation is tuning candidate radius and dispatch batch strategy with market-local caching."

---

## 13. Interview Summary

### 13.1 Product framing

- `Estimate` is fast, expiring guidance.
- `Trip` is durable transactional state.
- Realtime rider UX depends on low-latency push, not polling.

### 13.2 Protocol choices

- REST for booking, estimates, events, and payment methods.
- WebSocket for rider-facing live updates.
- gRPC/events internally for matching, geo, pricing, and payment workflows.

### 13.3 Matching in one sentence

- Find nearby eligible drivers, score and dispatch top-N, then atomically commit the first accepted driver.

### 13.4 Main scale trade-offs

- Lower rider wait time often means handling more driver accept conflicts.
- Realtime location at scale requires separated ingest and fanout paths.
- Payment reliability and idempotency are more important than absolute speed.

### 13.5 Terms to explain confidently

- `control plane`: API orchestration path
- `data plane`: realtime execution path
- `S2 index`: geospatial neighbor lookup structure
- `optimistic locking`: first successful write wins
- `replay`: resend missed events after reconnect
