# Proximity Service Design

A service to find nearby places/businesses based on user location (similar to Yelp, Google Maps, Uber driver matching).

## 📁 Files in this Directory

| File | Description |
|------|-------------|
| [README.md](README.md) | Complete system design documentation |
| [openapi.yaml](openapi.yaml) | OpenAPI 3.0 specification (machine-readable) |
| [OPENAPI_GUIDE.md](OPENAPI_GUIDE.md) | How to use the OpenAPI spec |
| [client_example.py](client_example.py) | Python client usage examples |

## Table of Contents
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [Back-of-Envelope Estimation](#back-of-envelope-estimation)
- [API Design](#api-design)
- [High-Level Architecture](#high-level-architecture)
- [Database Schema](#database-schema)
- [Geospatial Indexing](#geospatial-indexing)
- [Deep Dive](#deep-dive)

---

## Functional Requirements

### Core Features

**1. Search Nearby Places**
- Users can search for places within a radius (e.g., "restaurants within 5km")
- Support filtering by type (restaurant, gas station, hotel, etc.)
- Return results sorted by distance

**2. Add/Update/Delete Places**
- Business owners can add new places
- Update place information (name, address, hours, etc.)
- Remove places that no longer exist

**3. View Place Details**
- Get detailed information about a specific place
- Include: name, address, rating, photos, reviews, hours

**4. Optional Features (Phase 2)**
- Real-time updates (e.g., Uber drivers' live locations)
- Geofencing (notify when user enters/exits area)
- Route optimization (visit multiple places)

### Out of Scope (for this design)
- Reviews and ratings system (separate service)
- Payment processing
- Booking/reservations
- Social features

---

## Non-Functional Requirements

### Performance
- **Low latency:** P99 < 200ms for search queries
- **High throughput:** Handle 100,000 QPS (queries per second)
- **Fast reads:** Read-heavy system (read:write ratio = 100:1)

### Scalability
- **Horizontal scaling:** Add more servers as traffic grows
- **Data size:** Support 500M places globally
- **Geographic distribution:** Deploy in multiple regions for low latency

### Availability
- **High availability:** 99.99% uptime (< 52 minutes downtime/year)
- **Fault tolerance:** No single point of failure
- **Disaster recovery:** Data replicated across regions

### Consistency
- **Eventual consistency acceptable:** New places may take a few seconds to appear
- **Strong consistency for writes:** Prevent duplicate place additions

### Other Requirements
- **Accuracy:** Return results within specified radius
- **Freshness:** Place data updated within 1 minute
- **Security:** API authentication, rate limiting

---

## Back-of-Envelope Estimation

### Assumptions
- **Daily Active Users (DAU):** 100 million
- **Searches per user per day:** 5
- **Total daily searches:** 100M × 5 = 500M searches/day
- **Seconds per day:** 10^5 seconds ≈ 86,400 seconds (simplified)

### QPS Calculations

**Average QPS:**
```
500M searches / 10^5 seconds = 5,000 QPS
```

**Peak QPS (3x average):**
```
5,000 × 3 = 15,000 QPS
```

**Design for:** 20,000 QPS (buffer for growth)

### Storage Estimation

**Number of places:**
```
Total places worldwide: 500M
```

**Storage per place:**
```
place_id: 8 bytes
name: 256 bytes
address: 512 bytes
latitude: 8 bytes
longitude: 8 bytes
category: 64 bytes
metadata: 500 bytes
Total: ~1.5 KB per place
```

**Total storage:**
```
500M places × 1.5 KB = 750 GB
With indexes (2x): 1.5 TB
With replicas (3x): 4.5 TB
```

### Bandwidth

**Average request size:** 100 bytes (lat, lon, radius, filters)  
**Average response size:** 5 KB (20 places × 250 bytes each)

**Incoming traffic:**
```
20,000 QPS × 100 bytes = 2 MB/s = 16 Mbps
```

**Outgoing traffic:**
```
20,000 QPS × 5 KB = 100 MB/s = 800 Mbps
```

### Memory (Caching)

**Cache hot places (20% accessed frequently):**
```
500M × 0.2 × 1.5 KB = 150 GB
Distributed across servers: ~10 GB per cache node
```

### Server Estimation

**Application servers (20,000 QPS):**
```
Assume 1 server handles 1,000 QPS
20,000 / 1,000 = 20 servers
With redundancy: 30 servers
```

**Database servers:**
```
Read QPS: 20,000
Write QPS: 200 (read:write = 100:1)
With read replicas: 5 primary + 15 read replicas
```

### Summary Table

| Metric | Value |
|--------|-------|
| Daily searches | 500M |
| Average QPS | 5,000 |
| Peak QPS | 15,000 |
| Design target | 20,000 QPS |
| Total places | 500M |
| Storage (with replicas) | 4.5 TB |
| Incoming bandwidth | 16 Mbps |
| Outgoing bandwidth | 800 Mbps |
| Cache memory | 150 GB |
| Application servers | 30 |
| Database servers | 20 |

---

## API Design

### OpenAPI 3.0 Specification

> **Full spec:** [openapi.yaml](openapi.yaml)  
> **Usage guide:** [OPENAPI_GUIDE.md](OPENAPI_GUIDE.md)  
> **Try online:** [Swagger Editor](https://editor.swagger.io/) (import openapi.yaml)

**Quick Overview:**
```yaml
openapi: 3.0.0
info:
  title: Proximity Service API
  version: 1.0.0
  description: Find nearby places based on location
servers:
  - url: https://api.proximity.example.com/v1
    description: Production
  - url: https://api-staging.proximity.example.com/v1
    description: Staging
```

**Interactive Documentation:**
- **Swagger UI:** `https://api.proximity.example.com/docs`
- **ReDoc:** `https://api.proximity.example.com/redoc`
- **Postman Collection:** Import OpenAPI spec directly

**Getting Started:**
```bash
# View docs locally
docker run -p 8080:8080 -v $(pwd):/app -e SWAGGER_JSON=/app/openapi.yaml swaggerapi/swagger-ui
open http://localhost:8080

# Generate Python client
openapi-generator-cli generate -i openapi.yaml -g python -o ./client

# Validate API responses
prism mock openapi.yaml -p 8080
```

### RESTful API

#### 1. Search Nearby Places

```http
GET /v1/places/nearby
```

**Query Parameters:**
```json
{
  "latitude": 37.7749,      // Required
  "longitude": -122.4194,   // Required
  "radius": 5000,           // Optional, default 5000 (meters)
  "type": "restaurant",     // Optional, filter by type
  "limit": 20,              // Optional, default 20
  "offset": 0               // Optional, for pagination
}
```

**Response (200 OK):**
```json
{
  "places": [
    {
      "place_id": "chIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "Blue Bottle Coffee",
      "address": "66 Mint St, San Francisco, CA 94103",
      "location": {
        "latitude": 37.7764,
        "longitude": -122.4172
      },
      "distance": 450,         // meters
      "rating": 4.5,
      "type": "cafe",
      "is_open": true
    },
    {
      "place_id": "chIJPZDrEzeuEmsRwMRrY83frB2",
      "name": "Foreign Cinema",
      "address": "2534 Mission St, San Francisco, CA 94110",
      "location": {
        "latitude": 37.7584,
        "longitude": -122.4188
      },
      "distance": 1850,
      "rating": 4.3,
      "type": "restaurant",
      "is_open": false
    }
  ],
  "total": 156,
  "has_more": true
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "INVALID_COORDINATES",
  "message": "Latitude must be between -90 and 90"
}
```

---

#### 2. Get Place Details

```http
GET /v1/places/{place_id}
```

**Path Parameters:**
- `place_id`: Unique identifier for the place

**Response (200 OK):**
```json
{
  "place_id": "chIJN1t_tDeuEmsRUsoyG83frY4",
  "name": "Blue Bottle Coffee",
  "address": "66 Mint St, San Francisco, CA 94103",
  "location": {
    "latitude": 37.7764,
    "longitude": -122.4172
  },
  "phone": "+1 415-495-3394",
  "website": "https://bluebottlecoffee.com",
  "rating": 4.5,
  "type": "cafe",
  "hours": {
    "monday": "07:00-19:00",
    "tuesday": "07:00-19:00",
    "wednesday": "07:00-19:00",
    "thursday": "07:00-19:00",
    "friday": "07:00-19:00",
    "saturday": "08:00-18:00",
    "sunday": "08:00-18:00"
  },
  "photos": [
    "https://cdn.example.com/photos/abc123.jpg",
    "https://cdn.example.com/photos/def456.jpg"
  ],
  "created_at": "2020-05-15T10:30:00Z",
  "updated_at": "2026-02-01T14:20:00Z"
}
```

---

#### 3. Add Place

```http
POST /v1/places
```

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Cafe",
  "address": "123 Main St, San Francisco, CA 94102",
  "location": {
    "latitude": 37.7850,
    "longitude": -122.4100
  },
  "phone": "+1 415-555-0123",
  "website": "https://newcafe.com",
  "type": "cafe",
  "hours": {
    "monday": "08:00-20:00",
    "tuesday": "08:00-20:00",
    "wednesday": "08:00-20:00",
    "thursday": "08:00-20:00",
    "friday": "08:00-20:00",
    "saturday": "09:00-21:00",
    "sunday": "09:00-21:00"
  }
}
```

**Response (201 Created):**
```json
{
  "place_id": "chIJXYZ123newPlaceId",
  "message": "Place created successfully",
  "created_at": "2026-02-08T12:00:00Z"
}
```

---

#### 4. Update Place

```http
PUT /v1/places/{place_id}
```

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:** (partial updates allowed)
```json
{
  "name": "New Cafe - Updated",
  "hours": {
    "monday": "07:00-21:00"
  }
}
```

**Response (200 OK):**
```json
{
  "place_id": "chIJXYZ123newPlaceId",
  "message": "Place updated successfully",
  "updated_at": "2026-02-08T15:30:00Z"
}
```

---

#### 5. Delete Place

```http
DELETE /v1/places/{place_id}
```

**Headers:**
```
Authorization: Bearer {token}
```

**Response (204 No Content)**

---

#### 6. Search by Area (Polygon)

```http
POST /v1/places/search-area
```

**Request Body:**
```json
{
  "polygon": [
    {"latitude": 37.7749, "longitude": -122.4194},
### Benefits of OpenAPI

```mermaid
graph LR
    OpenAPI[OpenAPI Spec<br/>openapi.yaml]
    
    OpenAPI --> SwaggerUI[Swagger UI<br/>Interactive Docs]
    OpenAPI --> ReDoc[ReDoc<br/>Beautiful Docs]
    OpenAPI --> Postman[Postman<br/>Collection Import]
    OpenAPI --> ClientSDK[Client SDK<br/>Generation]
    OpenAPI --> ServerStub[Server Stub<br/>Generation]
    OpenAPI --> Validation[Request/Response<br/>Validation]
    OpenAPI --> Testing[Automated<br/>API Testing]
    OpenAPI --> Mock[Mock Server<br/>Prism/Stoplight]
    
    style OpenAPI fill:#4CAF50
    style SwaggerUI fill:#FF9800
    style ClientSDK fill:#2196F3
    style Validation fill:#9C27B0
```

**Key Benefits:**
- 📖 **Auto-generated docs** - No manual doc updates
- 🔧 **SDK generation** - Python, Java, JavaScript clients
- ✅ **Validation** - Request/response validation at runtime
- 🧪 **Testing** - Contract testing, mock servers
- 🤝 **Team collaboration** - Single source of truth

    {"latitude": 37.7849, "longitude": -122.4094},
    {"latitude": 37.7649, "longitude": -122.4094}
  ],
  "type": "restaurant",
  "limit": 50
}
```

**Response:** Similar to nearby search

---

### API Design Principles

✅ **RESTful conventions:** Use HTTP verbs correctly  
✅ **Versioning:** `/v1/` prefix for future compatibility  
✅ **Pagination:** Support `limit` and `offset` for large results  
✅ **Filtering:** Allow filtering by type, open/closed, rating  
✅ **Rate limiting:** 1000 requests/hour per user  
✅ **Authentication:** JWT tokens for write operations  
✅ **HTTPS only:** Secure communication  
✅ **Error codes:** Standard HTTP status codes with descriptive messages

---

## High-Level Architecture

```mermaid
graph TB
    Client["Mobile/Web Clients"]
    LB["Load Balancer<br/>NGINX/AWS ALB"]
    API1["API Server 1"]
    API2["API Server 2"]
    API3["API Server N"]
    
    Cache["(Redis Cache<br/>Geospatial Index)"]
    GeoIndex["In-Memory<br/>Geospatial Service<br/>QuadTree/Geohash"]
    
    DBPrimary["(PostgreSQL Primary<br/>PostGIS)"]
    DBReplica1["(Read Replica 1<br/>North America)"]
    DBReplica2["(Read Replica 2<br/>Europe)"]
    DBReplica3["(Read Replica 3<br/>Asia)"]
    
    CDN["CDN<br/>CloudFront/CloudFlare"]
    S3["(S3<br/>Place Photos)"]
    
    Client --> LB
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> Cache
    API2 --> Cache
    API3 --> Cache
    
    API1 --> GeoIndex
    API2 --> GeoIndex
    API3 --> GeoIndex
    
    API1 -.->|"Writes"| DBPrimary
    API2 -.->|"Writes"| DBPrimary
    API3 -.->|"Writes"| DBPrimary
    
    API1 -->|"Reads"| DBReplica1
    API2 -->|"Reads"| DBReplica2
    API3 -->|"Reads"| DBReplica3
    
    DBPrimary -.->|"Replication"| DBReplica1
    DBPrimary -.->|"Replication"| DBReplica2
    DBPrimary -.->|"Replication"| DBReplica3
    
    GeoIndex -.->|"Sync every 5min"| DBReplica1
    
    Client -->|"Static Content"| CDN
    CDN --> S3
    
    style Client fill:#e1f5ff
    style LB fill:#fff4e1
    style Cache fill:#ffe1e1
    style GeoIndex fill:#ffe1e1
    style DBPrimary fill:#e1ffe1
    style CDN fill:#f0e1ff
```

### Components

**1. Load Balancer (NGINX/AWS ALB)**
- Distribute traffic across API servers
- Health checks
- SSL termination

**2. API Servers (Stateless)**
- Handle HTTP requests
- Business logic
- Coordinate between cache, index, database
- Horizontally scalable

**3. Cache Layer (Redis)**
- Cache popular places
- Cache recent search results
- TTL: 5 minutes for search results, 1 hour for place details
- LRU eviction policy

**4. Geospatial Index**
- Fast proximity search
- In-memory data structure (QuadTree or Geohash)
- Periodically synchronized with database
- Options: Redis Geospatial, custom QuadTree service

**5. Database (PostgreSQL with PostGIS)**
- Primary: Handle writes
- Read replicas: Handle read queries
- PostGIS extension for geospatial queries
- Sharding by geographic region

**6. CDN (Optional)**
- Cache place photos
- Reduce latency for static content

---

## Request Flow Diagrams

### Entity Relationship Diagram

```mermaid
erDiagram
    PLACES ||--o{ BUSINESS_HOURS : has
    PLACES ||--o{ PLACE_METADATA : has
    PLACES ||--o| PLACE_GEOHASH : has
    
    PLACES {
        varchar place_id PK
        varchar name
        text address
        double latitude
        double longitude
        geography location
        varchar phone
        varchar website
        varchar type
        decimal rating
        boolean is_open
        timestamp created_at
        timestamp updated_at
    }
    
    BUSINESS_HOURS {
        bigserial id PK
        varchar place_id FK
        integer day_of_week
        time open_time
        time close_time
        boolean is_closed
    }
    
    PLACE_METADATA {
        varchar place_id FK
        varchar key_name
        text value
    }
    
    PLACE_GEOHASH {
        varchar place_id PK "FK to PLACES"
        varchar geohash
    }
```

### Search Nearby Places Flow

```mermaid
sequenceDiagram
    participant Client
    participant LB as Load Balancer
    participant API as API Server
    participant Cache as Redis Cache
    participant GeoIdx as Geospatial Index
    participant DB as PostgreSQL
    
    Client->>LB: GET /v1/places/nearby?lat=37.77&lon=-122.41&radius=5000
    LB->>API: Forward request
    
    API->>Cache: Check cache<br/>key: "nearby:37.77:-122.41:5000"
    
    alt Cache Hit
        Cache-->>API: Return cached results
        API-->>Client: 200 OK (cached results)
    else Cache Miss
        API->>GeoIdx: Query geospatial index<br/>nearby(37.77, -122.41, 5km)
        
        alt Index has data
            GeoIdx-->>API: Return place IDs
            API->>DB: Batch fetch place details<br/>SELECT * WHERE place_id IN (...)
            DB-->>API: Place details
        else Index sync needed
            API->>DB: PostGIS query<br/>ST_DWithin(location, point, 5000)
            DB-->>API: Places within radius
            API->>GeoIdx: Warm up index
        end
        
        API->>API: Filter by type<br/>Sort by distance<br/>Apply pagination
        API->>Cache: Store results (TTL: 5min)
        API-->>Client: 200 OK (fresh results)
    end
```

### Add Place Flow

```mermaid
sequenceDiagram
    participant Client
    participant LB as Load Balancer
    participant API as API Server
    participant Auth as Auth Service
    participant Queue as Message Queue
    participant DB as PostgreSQL Primary
    participant GeoIdx as Geospatial Index
    participant Cache as Redis Cache
    
    Client->>LB: POST /v1/places<br/>Authorization: Bearer token
    LB->>API: Forward request
    
    API->>Auth: Verify JWT token
    Auth-->>API: Token valid ✓
    
    API->>API: Validate payload<br/>(lat/lon, required fields)
    
    API->>DB: BEGIN TRANSACTION
    API->>DB: INSERT INTO places(...)
    API->>DB: INSERT INTO business_hours(...)
    API->>DB: COMMIT
    DB-->>API: place_id: "xyz123"
    
    API->>Queue: Publish event<br/>{type: "place_created", id: "xyz123"}
    
    par Async Updates
        Queue->>GeoIdx: Update index with new place
        Queue->>Cache: Invalidate nearby caches
    end
    
    API-->>Client: 201 Created<br/>{place_id: "xyz123"}
```

### Real-Time Location Update (Uber-style)

```mermaid
sequenceDiagram
    participant Driver as Driver App
    participant Gateway as WebSocket Gateway
    participant LocationSvc as Location Service
    participant Redis as Redis Geospatial
    participant Rider as Rider App
    
    Driver->>Gateway: WebSocket connect
    Gateway-->>Driver: Connected
    
    loop Every 5 seconds
        Driver->>Gateway: Update location<br/>{lat, lon, driver_id}
        Gateway->>LocationSvc: Process location
        LocationSvc->>Redis: GEOADD drivers {lon} {lat} {driver_id}
        Redis-->>LocationSvc: OK
    end
    
    Rider->>LocationSvc: GET /drivers/nearby<br/>{lat, lon, radius}
    LocationSvc->>Redis: GEORADIUS drivers {lon} {lat} {radius}
    Redis-->>LocationSvc: [{driver_id, distance}]
    LocationSvc-->>Rider: Nearby drivers
    
    Note over Redis: TTL: 5 minutes<br/>Auto-expire old locations
```

---

### Geospatial Indexing Comparison

```mermaid
graph LR
    A[Geospatial<br/>Indexing<br/>Approaches] --> B[Geohash]
    A --> C[QuadTree]
    A --> D[Google S2]
    A --> E[R-Tree]
    
    B --> B1[Simple<br/>String-based]
    B --> B2[Redis GEORADIUS]
    B --> B3[Grid cells]
    
    C --> C1[Hierarchical<br/>4 quadrants]
    C --> C2[Dynamic<br/>balancing]
    C --> C3[In-memory]
    
    D --> D1[Sphere projection]
    D --> D2[Best coverage]
    D --> D3[Complex]
    
    E --> E1[PostgreSQL<br/>PostGIS]
    E --> E2[B-tree variant]
    E --> E3[Good for DB]
    
    style B fill:#90EE90
    style B2 fill:#FFD700
    style C fill:#87CEEB
    style D fill:#DDA0DD
    style E fill:#F0E68C
``` loop Every 5 seconds
        Driver->>Gateway: Send location<br/>{driver_id, lat, lon, timestamp}
        Gateway->>LocationSvc: Update location
        
        LocationSvc->>LocationSvc: Check if moved > 50m
        
        alt Significant movement
            LocationSvc->>Redis: GEOADD drivers {lon} {lat} {driver_id}
            LocationSvc->>Redis: EXPIRE drivers:{driver_id} 300
        else No significant movement
            LocationSvc->>LocationSvc: Skip update
        end
    end
    
    Rider->>Gateway: Search nearby drivers<br/>{lat, lon, radius: 2000m}
    Gateway->>LocationSvc: Find nearby
    LocationSvc->>Redis: GEORADIUS drivers {lon} {lat} 2000m
    Redis-->>LocationSvc: [driver1: 500m, driver2: 1200m]
    LocationSvc-->>Gateway: Available drivers
    Gateway-->>Rider: Show drivers on map
```

---

## Database Schema

### PostgreSQL Schema

```sql
-- Places table
CREATE TABLE places (
    place_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326),  -- PostGIS type
    phone VARCHAR(50),
    website VARCHAR(500),
    type VARCHAR(50) NOT NULL,
    rating DECIMAL(2, 1) DEFAULT 0,
    is_open BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (latitude >= -90 AND latitude <= 90),
    CHECK (longitude >= -180 AND longitude <= 180)
);

-- Spatial index for fast proximity queries
CREATE INDEX idx_places_location ON places USING GIST(location);

-- Regular indexes
CREATE INDEX idx_places_type ON places(type);
CREATE INDEX idx_places_created_at ON places(created_at);

-- Business hours table
CREATE TABLE business_hours (
    id BIGSERIAL PRIMARY KEY,
    place_id VARCHAR(255) REFERENCES places(place_id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL,  -- 0=Monday, 6=Sunday
    open_time TIME,
    close_time TIME,
    is_closed BOOLEAN DEFAULT false,
    
    UNIQUE(place_id, day_of_week)
);

CREATE INDEX idx_business_hours_place ON business_hours(place_id);

-- Place metadata (extensible)
CREATE TABLE place_metadata (
    place_id VARCHAR(255) REFERENCES places(place_id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    
    PRIMARY KEY(place_id, key)
);

-- Geohash index table (alternative to QuadTree)
CREATE TABLE place_geohash (
    place_id VARCHAR(255) REFERENCES places(place_id) ON DELETE CASCADE,
    geohash VARCHAR(12) NOT NULL,
    
    PRIMARY KEY(place_id)
);

CREATE INDEX idx_geohash ON place_geohash(geohash);
```

### Sample Queries

**1. Find nearby places (PostGIS):**
```sql
SELECT 
    place_id,
    name,
    address,
    latitude,
    longitude,
    ST_Distance(
        location,
        ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography
    ) AS distance
FROM places
WHERE 
    ST_DWithin(
        location,
        ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography,
        5000  -- 5km radius in meters
    )
    AND type = 'restaurant'
ORDER BY distance
LIMIT 20;
```

**2. Find places by geohash prefix:**
```sql
SELECT p.*
FROM places p
JOIN place_geohash gh ON p.place_id = gh.place_id
WHERE gh.geohash LIKE '9q8yy%'  -- Geohash prefix
LIMIT 20;
```

**3. Check if place is currently open:**
```sql
SELECT p.*, 
    CASE 
        WHEN bh.is_closed THEN false
        WHEN CURRENT_TIME BETWEEN bh.open_time AND bh.close_time THEN true
        ELSE false
    END as is_currently_open
FROM places p
LEFT JOIN business_hours bh 
    ON p.place_id = bh.place_id 
    AND bh.day_of_week = EXTRACT(DOW FROM CURRENT_DATE)
WHERE p.place_id = 'chIJN1t_tDeuEmsRUsoyG83frY4';
```

---

## Geospatial Indexing

### Why Geospatial Indexing?

**Naive approach (scan all places):**
```python
for place in all_places:  # 500M places!
    if distance(user_location, place.location) < radius:
        results.append(place)
# Time complexity: O(n) - Too slow! ❌
```

**With geospatial index:**
```python
# Only check places in nearby grid cells
results = geospatial_index.search(user_location, radius)
# Time complexity: O(log n) or O(1) - Fast! ✅
```

---

### Approach 1: QuadTree

**QuadTree Visualization:**

```mermaid
graph TD
    Root["Root Node<br/>World<br/>Capacity: 50"]
    
    Root --> NW["Northwest<br/>North America"]
    Root --> NE["Northeast<br/>Europe/Asia"]
    Root --> SW["Southwest<br/>South America"]
    Root --> SE["Southeast<br/>Africa/Oceania"]
    
    NW --> NW_NW["NW-NW<br/>Canada"]
    NW --> NW_NE["NW-NE<br/>Northeast US"]
    NW --> NW_SW["NW-SW<br/>Southwest US"]
    NW --> NW_SE["NW-SE<br/>Southeast US"]
    
    NW_SW --> CA["California<br/>50 places"]
    NW_SW --> NV[Nevada<br/>30 places]
    
    CA --> SF[San Francisco<br/>Places: 12<br/>p1, p2, ..., p12]
    CA --> LA[Los Angeles<br/>Places: 25<br/>p13, p14, ..., p38]
    
    style SF fill:#90EE90
    style LA fill:#90EE90
    style CA fill:#FFD700
    style Root fill:#87CEEB
    
    classDef leafNode fill:#90EE90,stroke:#333,stroke-width:2px
    class SF,LA leafNode
```

**QuadTree Search Process:**

```mermaid
graph TD
    Start([User searches near<br/>San Francisco<br/>lat: 37.77, lon: -122.41<br/>radius: 5km])
    
    Start --> Root{Root intersects<br/>search circle?}
    Root -->|Yes| CheckNW{NW quadrant<br/>intersects?}
    Root -->|No| Skip1[Skip quadrant]
    
    CheckNW -->|Yes| CheckNW_SW{NW-SW<br/>intersects?}
    CheckNW -->|No| Skip2[Skip NW]
    
    CheckNW_SW -->|Yes| CheckCA{California<br/>intersects?}
    CheckNW_SW -->|No| Skip3[Skip NW-SW]
    
    CheckCA -->|Yes| CheckSF{SF node<br/>intersects?}
    
    CheckSF -->|Yes| GetPlaces[Get places from SF node:<br/>p1, p2, ..., p12]
    
    GetPlaces --> Filter[Filter by exact distance:<br/>haversine_distance < 5km]
    
    Filter --> Sort[Sort by distance]
    Sort --> Return([Return results])
    
    style Start fill:#e1f5ff
    style GetPlaces fill:#90EE90
    style Return fill:#90EE90
```

---

### Approach 1: Geohash

**What is Geohash?**
- Encode coordinates into a short string
- Similar locations have similar prefixes
- Hierarchical: longer geohash = more precise

**Example:**
```
San Francisco: "9q8yy" (5 chars ≈ 5km precision)
- 9q8yy9: Specific block
- 9q8yy: Neighborhood
- 9q8y: District
- 9q8: City
- 9q: Region
```

**Geohash Hierarchy Visualization:**

```mermaid
graph TB
    subgraph "World - Precision 1"
        A["9"] --> B["9q - California"]
    end
    
    subgraph "California - Precision 2"
        B --> C["9q8 - SF Bay Area"]
        B --> D["9qh - San Diego"]
    end
    
    subgraph "SF Bay Area - Precision 3"
        C --> E["9q8y - San Francisco"]
        C --> F["9q9p - Oakland"]
    end
    
    subgraph "San Francisco - Precision 4"
        E --> G["9q8yy - Mission District"]
        E --> H["9q8yz - SOMA"]
        E --> I["9q8yu - Marina"]
    end
    
    subgraph "Mission District - Precision 5"
        G --> J["9q8yy9 - 16th & Valencia<br/>±4.9m precision"]
        G --> K["9q8yyd - 24th & Mission<br/>±4.9m precision"]
    end
    
    style J fill:#90EE90
    style K fill:#90EE90
```

**Implementation:**
```python
import pygeohash as pgh

def find_nearby_places(lat, lon, radius_km):
    # Get geohash at appropriate precision
    precision = get_precision_for_radius(radius_km)
    center_hash = pgh.encode(lat, lon, precision=precision)
    
    # Get neighboring geohashes
    neighbors = pgh.get_adjacent(center_hash)
    search_hashes = [center_hash] + neighbors
    
    # Query database
    results = []
    for geohash in search_hashes:
        places = db.query(
            "SELECT * FROM place_geohash WHERE geohash LIKE %s",
            (geohash + '%',)
        )
        results.extend(places)
    
    # Filter by exact distance
    filtered = [
        p for p in results 
        if haversine_distance(lat, lon, p.lat, p.lon) <= radius_km
    ]
    
    return sorted(filtered, key=lambda p: p.distance)

def get_precision_for_radius(radius_km):
    # Geohash precision mapping
    if radius_km <= 0.02:    return 9  # ~20m
    elif radius_km <= 0.15:  return 7  # ~150m
    elif radius_km <= 1.2:   return 6  # ~1.2km
    elif radius_km <= 5:     return 5  # ~5km
    elif radius_km <= 20:    return 4  # ~20km
    else:                    return 3  # ~150km
```

**Geohash Index in Redis:**
```python
import redis
import pygeohash as pgh

redis_client = redis.Redis()

# Add place to Redis geospatial index
def add_place(place_id, lat, lon):
    redis_client.geoadd('places', (lon, lat, place_id))

# Search nearby
def search_nearby(lat, lon, radius_m):
    results = redis_client.georadius(
        'places',
        lon, lat,
        radius_m,
        unit='m',
        withdist=True,
        count=20
    )
    return results

# Example
add_place('place1', 37.7749, -122.4194)
add_place('place2', 37.7849, -122.4094)

nearby = search_nearby(37.7749, -122.4194, 5000)
print(nearby)  # [(b'place1', 0.0), (b'place2', 1345.6)]
```

**Pros/Cons:**

✅ Simple to implement  
✅ Works well with Redis GEOADD/GEORADIUS  
✅ Human-readable (can see location from hash)  
❌ Edge cases near boundaries (need to check neighbors)  
❌ Not perfect for arbitrary radiuses

---

### Approach 2: QuadTree

**What is QuadTree?**
- Recursively divide 2D space into 4 quadrants
- Each node represents a region
- Leaf nodes contain actual places

**Structure:**
```
                    [Root: World]
                    /     |     \
           [NW]    [NE]   [SW]    [SE]
          /  |  \
    [NW] [NE] [SW] [SE]
      |
    [Places: p1, p2, p3]
```

**Implementation:**
```python
class QuadTreeNode:
    def __init__(self, boundary, capacity=50):
        self.boundary = boundary  # (min_lat, max_lat, min_lon, max_lon)
        self.capacity = capacity
        self.places = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None
    
    def insert(self, place):
        # If place not in boundary, reject
        if not self.boundary.contains(place):
            return False
        
        # If capacity not reached, add here
        if len(self.places) < self.capacity:
            self.places.append(place)
            return True
        
        # Otherwise, subdivide and add
        if not self.divided:
            self.subdivide()
        
        # Try to insert into children
        if self.northwest.insert(place): return True
        if self.northeast.insert(place): return True
        if self.southwest.insert(place): return True
        if self.southeast.insert(place): return True
        
        return False  # Should never reach here
```

**Pros/Cons:**

✅ Fast for sparse data  
✅ Automatically adapts to data density  
✅ Good for arbitrary radiuses  
❌ Complex to implement  
❌ Requires rebuilding on updates  
❌ Memory intensive for dense areas

---

### Approach Comparison

| Feature | Geohash | QuadTree |
|---------|---------|----------|
| **Implementation** | Simple | Complex |
| **Search Speed** | O(log n) | O(log n) |
| **Update Speed** | O(1) | O(log n) |
| **Memory Usage** | Low | Medium-High |
| **Boundary Issues** | Yes (check neighbors) | Minimal |
| **Best For** | Redis-backed systems | In-memory services |
| **Recommended** | ✅ For most cases | Advanced use cases |

**Recommendation:** Use **Geohash with Redis** for simplicity and scalability.

---

### Multi-Level Caching Architecture

```mermaid
graph TD
    Client["Client Request<br/>GET /v1/places/nearby"]
    
    L1{"Level 1:<br/>Application<br/>In-Memory Cache<br/>TTL: 1min"}
    L2{"Level 2:<br/>Redis Cache<br/>TTL: 5min"}
    L3{"Level 3:<br/>Database<br/>PostGIS"}
    
    CDN{"CDN Cache<br/>Static Content<br/>TTL: 1hr"}
    S3["(S3<br/>Place Photos)"]
    
    Client --> L1
    
    L1 -->|"Cache Hit<br/>~5% requests"| Return1["Return<br/>< 1ms"]
    L1 -->|"Cache Miss"| L2
    
    L2 -->|"Cache Hit<br/>~75% requests"| Return2["Return<br/>< 10ms"]
    L2 -->|"Cache Miss"| L3
    
    L3 -->|"Database Query<br/>~20% requests"| Return3["Return<br/>< 50ms"]
    
    L3 --> UpdateL2["Update L2 Cache"]
    UpdateL2 --> UpdateL1["Update L1 Cache"]
    
    Client -.->|"Photos"| CDN
    CDN -->|"Hit"| ReturnCDN["Return from CDN"]
    CDN -->|"Miss"| S3
    S3 --> CDNUpdate["Update CDN"]
    
    style Return1 fill:#90EE90
    style Return2 fill:#FFD700
    style Return3 fill:#FFA07A
    style L1 fill:#e1f5ff
    style L2 fill:#ffe1e1
    style CDN fill:#f0e1ff
```

**Cache Key Strategy:**
```
Level 1 (App): "nearby:{lat}:{lon}:{radius}"
Level 2 (Redis): "nearby:{lat_rounded}:{lon_rounded}:{radius}"
  - Round lat/lon to 2 decimal places (~1km precision)
```

---

### Scaling Strategy

```mermaid
graph LR
    subgraph "Phase 1: MVP<br/>0-1K QPS"
        A1[Single API Server]
        A2[(Single PostgreSQL<br/>with PostGIS)]
        A1 --> A2
    end
    
    subgraph "Phase 2: Growth<br/>1K-5K QPS"
        B1[Load Balancer]
        B2[API Server 1]
        B3[API Server 2]
        B4[(Redis Cache)]
        B5[(PostgreSQL<br/>Primary)]
        B6[(Read Replica)]
        
        B1 --> B2
        B1 --> B3
        B2 --> B4
        B3 --> B4
        B2 --> B5
        B2 --> B6
        B3 --> B5
        B3 --> B6
        B5 -.->|Replication| B6
    end
    
    subgraph "Phase 3: Scale<br/>5K-20K QPS"
        C1[Load Balancer]
        C2[API Servers<br/>Auto-scaling]
        C3[(Redis Cluster<br/>3 nodes)]
        C4[Geospatial Service<br/>In-Memory Index]
        C5[(DB Shard 1<br/>North America)]
        C6[(DB Shard 2<br/>Europe)]
        C7[(DB Shard 3<br/>Asia)]
        C8[CDN]
        
        C1 --> C2
        C2 --> C3
        C2 --> C4
        C2 --> C5
        C2 --> C6
        C2 --> C7
        C2 --> C8
    end
    
    style A1 fill:#90EE90
    style B1 fill:#FFD700
    style C1 fill:#FF6B6B
```

**Key Improvements per Phase:**

**Phase 1 (MVP):**
- Single server, single database
- Simple to deploy
- Good for 0-1K QPS

**Phase 2 (Growth):**
- Load balancer for high availability
- Redis cache (80% hit rate)
- Read replica for read scaling
- Good for 1K-5K QPS

**Phase 3 (Scale):**
- Auto-scaling API servers
- Redis cluster for distributed caching
- Database sharding by geographic region
- CDN for static content
- Good for 5K-20K+ QPS

---

### Database Sharding Architecture

```mermaid
graph TB
    subgraph "Global Router"
        Router["Query Router<br/>Determines shard by lat/lon"]
    end
    
    subgraph "Shard 1: North America"
        DB1["(PostgreSQL<br/>North America<br/>lat: 15°N to 85°N<br/>lon: -170°W to -50°W)"]
        Replica1["(Read Replicas)"]
    end
    
    subgraph "Shard 2: Europe"
        DB2["(PostgreSQL<br/>Europe<br/>lat: 35°N to 71°N<br/>lon: -10°W to 40°E)"]
        Replica2["(Read Replicas)"]
    end
    
    subgraph "Shard 3: Asia"
        DB3["(PostgreSQL<br/>Asia<br/>lat: -10°S to 55°N<br/>lon: 60°E to 145°E)"]
        Replica3["(Read Replicas)"]
    end
    
    subgraph "Shard 4: Rest of World"
        DB4["(PostgreSQL<br/>Rest of World<br/>Other regions)"]
        Replica4["(Read Replicas)"]
    end
    
    Router --> DB1
    Router --> DB2
    Router --> DB3
    Router --> DB4
    
    DB1 --> Replica1
    DB2 --> Replica2
    DB3 --> Replica3
    DB4 --> Replica4
    
    style Router fill:#FFD700
    style DB1 fill:#90EE90
    style DB2 fill:#87CEEB
    style DB3 fill:#DDA0DD
    style DB4 fill:#FFA07A
```

**Benefits:**
- Most queries stay within one shard
- Easy to understand and manage
- Natural data isolation by geography

**Challenges:**
- Uneven load (more places in dense cities)
- Cross-region searches (rare but need to query multiple shards)

**Cache Strategy:**
```
Level 1 (App): "nearby:{lat_rounded}:{lon_rounded}:{radius}"
  - Round lat/lon to 2 decimal places (~1km precision)
  - Increases cache hit rate

Level 2 (Redis): 
  - Place details: "place:{place_id}"
  - Popular places: "popular:places" (sorted set by access count)
  - Geospatial index: GEOADD places {lon} {lat} {place_id}
```

---

### QuadTree Complete Implementation

```python
class QuadTreeNode:
    def __init__(self, boundary, capacity=50):
        self.boundary = boundary  # (min_lat, max_lat, min_lon, max_lon)
        self.capacity = capacity
        self.places = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None
    
    def subdivide(self):
        min_lat, max_lat, min_lon, max_lon = self.boundary
        mid_lat = (min_lat + max_lat) / 2
        mid_lon = (min_lon + max_lon) / 2
        
        self.northwest = QuadTreeNode((min_lat, mid_lat, min_lon, mid_lon))
        self.northeast = QuadTreeNode((min_lat, mid_lat, mid_lon, max_lon))
        self.southwest = QuadTreeNode((mid_lat, max_lat, min_lon, mid_lon))
        self.southeast = QuadTreeNode((mid_lat, max_lat, mid_lon, max_lon))
        
        self.divided = True
        
        # Move places to children
        for place in self.places:
            self.northwest.insert(place) or \
            self.northeast.insert(place) or \
            self.southwest.insert(place) or \
            self.southeast.insert(place)
        
        self.places = []
    
    def query_range(self, center_lat, center_lon, radius_km):
        results = []
        
        # If range doesn't intersect boundary, skip
        if not self.boundary.intersects_circle(center_lat, center_lon, radius_km):
            return results
        
        # Check places in this node
        for place in self.places:
            if haversine_distance(center_lat, center_lon, place.lat, place.lon) <= radius_km:
                results.append(place)
        
        # Check children
        if self.divided:
            results.extend(self.northwest.query_range(center_lat, center_lon, radius_km))
            results.extend(self.northeast.query_range(center_lat, center_lon, radius_km))
            results.extend(self.southwest.query_range(center_lat, center_lon, radius_km))
            results.extend(self.southeast.query_range(center_lat, center_lon, radius_km))
        
        return results
```

**Pros/Cons:**

✅ Fast queries: O(log n)  
✅ Dynamic (handles inserts/deletes well)  
✅ Works for any radius  
✅ No edge cases like geohash  
❌ More complex to implement  
❌ Requires memory (entire tree in memory)  
❌ Needs rebalancing

---

### Approach 3: Google S2

**Used by:** Google Maps, Uber, Foursquare

**What is S2?**
- Projects Earth onto a cube
- Divides cube into hierarchical cells
- Each cell has unique ID
- Better coverage than geohash

**Pros:**
✅ Best performance for complex queries  
✅ No gaps/overlaps in coverage  
✅ Supports polygons, not just circles  

**Cons:**
❌ Complex to implement  
❌ Heavy library

---

### Recommendation

**For this design:**

**Use Geohash + Redis** for simplicity and performance:
1. Redis GEOADD for fast in-memory lookups
2. PostgreSQL PostGIS for persistent storage
3. Sync Redis from PostgreSQL every 5 minutes

**Flow:**
```
1. Search request → Check Redis (fast)
2. If cache miss → Query PostGIS (ST_DWithin)
3. Warm up Redis with results
4. Return to client
```

---

## Deep Dive

### Database Sharding Strategy

**Shard by geographic region:**

```
Shard 1: North America (lat/lon ranges)
Shard 2: Europe
Shard 3: Asia
Shard 4: Rest of world

Benefits:
- Most queries stay within one shard
- Easy to understand
- Natural data isolation

Challenges:
- Uneven load (more places in cities)
- Cross-region searches (rare)
```

### Caching Strategy

**Multi-level caching:**

```
Level 1: Application cache (in-memory, 1 min TTL)
- Recently searched locations

Level 2: Redis (5 min TTL)
- Popular places
- Recent search results
- Key: "nearby:{lat}:{lon}:{radius}"

Level 3: CDN (1 hour TTL)
- Place photos
- Static place details
```

### Real-time Updates (Uber-style)

**For live location updates (drivers, delivery):**

```
1. Drivers send location every 5 seconds
2. Location Service → Redis Geospatial
3. Store only recent locations (TTL: 5 minutes)
4. User searches → Query Redis for live drivers
5. Don't persist every location (too much data)

Optimization:
- Only update if driver moved > 50m
- Batch updates every 10 seconds
```

### Handling High Load

**Read-heavy optimizations:**
- Read replicas (5-10x write throughput)
- Aggressive caching (80% cache hit rate)
- CDN for static content

**Write optimizations:**
- Batch writes
- Async processing (queue)
- De-duplicate updates

---

## Summary

### System Design Decision Matrix

```mermaid
graph TB
    subgraph "Key Design Decisions"
        D1[Database<br/>PostgreSQL + PostGIS]
        D2[Cache<br/>Redis Cluster]
        D3[Index<br/>Geohash + Redis GEORADIUS]
        D4[API<br/>REST]
        D5[Sharding<br/>Geographic]
        D6[Consistency<br/>Eventual]
    end
    
    subgraph "Rationale"
        R1[✓ Mature, ACID<br/>✓ PostGIS support<br/>✓ Strong community]
        R2[✓ Fast in-memory<br/>✓ GEORADIUS built-in<br/>✓ TTL support]
        R3[✓ Simple implementation<br/>✓ Battle-tested<br/>✓ Redis integration]
        R4[✓ Standard, cacheable<br/>✓ Wide adoption<br/>✓ Easy debugging]
        R5[✓ Natural locality<br/>✓ Most queries single-shard<br/>✓ Easy to understand]
        R6[✓ Better availability<br/>✓ Lower latency<br/>✓ Read-heavy OK]
    end
    
    subgraph "Trade-offs"
        T1[⚠️ Not as fast as NoSQL<br/>⚠️ Vertical scaling limits]
        T2[⚠️ In-memory cost<br/>⚠️ Need clustering]
        T3[⚠️ Edge case handling<br/>⚠️ Not perfect circles]
        T4[⚠️ Chattier than gRPC<br/>⚠️ Verbose responses]
        T5[⚠️ Uneven load<br/>⚠️ Cross-shard queries hard]
        T6[⚠️ Not strongly consistent<br/>⚠️ Stale reads possible]
    end
    
    D1 --> R1
    D2 --> R2
    D3 --> R3
    D4 --> R4
    D5 --> R5
    D6 --> R6
    
    R1 --> T1
    R2 --> T2
    R3 --> T3
    R4 --> T4
    R5 --> T5
    R6 --> T6
    
    style D1 fill:#90EE90
    style D2 fill:#90EE90
    style D3 fill:#90EE90
    style D4 fill:#90EE90
    style D5 fill:#90EE90
    style D6 fill:#90EE90
    style R1 fill:#87CEEB
    style T1 fill:#FFD700
```

### Performance Metrics Target

```mermaid
graph LR
    subgraph "Latency SLA"
        L1[P50: < 50ms]
        L2[P95: < 100ms]
        L3[P99: < 200ms]
    end
    
    subgraph "Availability SLA"
        A1[99.99% uptime<br/>~52 min/year downtime]
        A2[Multi-region<br/>Active-Active]
        A3[Auto-failover<br/>< 30 seconds]
    end
    
    subgraph "Throughput"
        T1[20K QPS peak]
        T2[100:1 read/write]
        T3[Cache hit rate: 80%]
    end
    
    subgraph "Data"
        D1[500M places]
        D2[4.5 TB storage]
        D3[150 GB cache]
    end
    
    style L3 fill:#90EE90
    style A1 fill:#90EE90
    style T1 fill:#90EE90
    style D1 fill:#87CEEB
```

**Key Decisions:**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Database | PostgreSQL + PostGIS | Mature, geospatial support, ACID |
| Cache | Redis | Fast, GEORADIUS command, TTL |
| Index | Geohash + Redis | Simple, performant, battle-tested |
| API | REST | Standard, easy to use, cacheable |
| Sharding | Geographic | Natural data locality |
| Consistency | Eventual | Acceptable for read-heavy system |

**Tradeoffs:**
- Chose simplicity over perfection (Geohash vs S2)
- Eventual consistency for better availability
- Read replicas for scalability vs consistency

**Next Steps:**
1. Implement MVP with single region
2. Add caching layer
3. Horizontal scaling with load balancer
4. Multi-region deployment
5. Add monitoring and alerts

---

## Viewing These Diagrams

**On GitHub:**
- All Mermaid diagrams render automatically in GitHub markdown
- Just push to GitHub and view the README

**Locally:**
- **VS Code:** Install "Markdown Preview Mermaid Support" extension
- **IntelliJ/PyCharm:** Built-in Mermaid support
- **Chrome:** Use Markdown Preview Plus extension
- **Online:** Copy to [Mermaid Live Editor](https://mermaid.live)

**Export Options:**
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG/SVG
mmdc -i README.md -o diagrams/architecture.png
mmdc -i README.md -o diagrams/architecture.svg
```

**Embedding in Presentations:**
- Export as SVG for crisp scaling
- Use Mermaid Live Editor to customize colors
- Screenshots work for quick sharing

---

## OpenAPI Workflow

```mermaid
graph TB
    Start[Write OpenAPI Spec<br/>openapi.yaml]
    
    Start --> Validate[Validate<br/>spectral lint]
    Start --> Docs[Generate Docs<br/>Swagger UI / ReDoc]
    Start --> ClientGen[Generate Clients<br/>Python, JS, Java, Go]
    Start --> ServerGen[Generate Server Stubs<br/>Express, Flask, Spring]
    Start --> Mock[Mock Server<br/>Prism]
    Start --> Test[Contract Testing<br/>Dredd]
    
    Validate --> CI[CI/CD Pipeline]
    Docs --> Deploy[Deploy Docs<br/>GitHub Pages]
    ClientGen --> SDK[SDK Distribution<br/>npm, PyPI]
    ServerGen --> Implement[Implement Handlers]
    Mock --> ParallelDev[Parallel Development<br/>Frontend + Backend]
    Test --> QA[Automated QA]
    
    CI --> Pass{Tests Pass?}
    Pass -->|Yes| Release[Release to Production]
    Pass -->|No| Fix[Fix Issues]
    Fix --> Start
    
    style Start fill:#4CAF50
    style Docs fill:#FF9800
    style ClientGen fill:#2196F3
    style Mock fill:#9C27B0
    style Release fill:#4CAF50
```


