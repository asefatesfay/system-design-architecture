# REST vs RPC

## Definition

**REST (Representational State Transfer):** Architectural style using HTTP methods to operate on resources (nouns). Resource-oriented.

**RPC (Remote Procedure Call):** Call functions/methods on remote server as if they were local. Action-oriented.

## Core Differences

| Aspect | REST | RPC |
|--------|------|-----|
| **Paradigm** | Resource-oriented | Action-oriented |
| **URL Structure** | `/users/123` | `/getUser` or `/user.get` |
| **HTTP Methods** | GET, POST, PUT, DELETE | Mostly POST |
| **Focus** | Resources (nouns) | Actions (verbs) |
| **Coupling** | Loose (stateless) | Can be tight |
| **Discovery** | Self-describing | Needs documentation |

## REST Example

```http
# Get user
GET /api/users/123
Response: { "id": 123, "name": "John" }

# Create user
POST /api/users
Body: { "name": "Jane" }
Response: { "id": 124, "name": "Jane" }

# Update user
PUT /api/users/123
Body: { "name": "John Updated" }

# Delete user
DELETE /api/users/123
```

**Characteristics:**
- HTTP verbs have meaning (GET = read, POST = create)
- Resources as URLs (`/users`, `/products`)
- Stateless (each request independent)

## RPC Example

### Traditional RPC

```http
# All actions as POST
POST /api/getUser
Body: { "userId": 123 }

POST /api/createUser
Body: { "name": "Jane" }

POST /api/updateUser
Body: { "userId": 123, "name": "John Updated" }

POST /api/deleteUser
Body: { "userId": 123 }
```

### gRPC (Modern RPC)

```protobuf
// Define service
service UserService {
  rpc GetUser (UserRequest) returns (User);
  rpc CreateUser (CreateUserRequest) returns (User);
  rpc UpdateUser (UpdateUserRequest) returns (User);
  rpc DeleteUser (DeleteUserRequest) returns (Empty);
}

// Client call (feels like local function)
user = client.GetUser(userId=123)
```

## Real-World Examples

### REST: Public APIs

**Stripe API:**
```http
GET https://api.stripe.com/v1/customers/cus_123
POST https://api.stripe.com/v1/charges
DELETE https://api.stripe.com/v1/customers/cus_123
```

**GitHub API:**
```http
GET https://api.github.com/users/octocat
GET https://api.github.com/repos/facebook/react/issues
POST https://api.github.com/repos/owner/repo/issues
```

**Twitter API:**
```http
GET https://api.twitter.com/2/tweets/1234567890
POST https://api.twitter.com/2/tweets
```

**Why REST for public APIs:**
- Standardized (developers know HTTP verbs)
- Cache-friendly (GET requests cached)
- Stateless (easy to scale)
- Human-readable URLs

### RPC: Internal Microservices

**Google (gRPC internally):**
```
Service A → gRPC → Service B
- Fast binary protocol (Protocol Buffers)
- Strongly typed
- Bi-directional streaming
```

**Netflix:** Uses gRPC between microservices
```
API Gateway → gRPC → Profile Service
              gRPC → Recommendation Service
              gRPC → Video Service
```

**Uber:** gRPC for service-to-service communication
```
- Low latency critical
- Type safety important
- 1000s of internal API calls
```

## When to Use REST

✅ **Public APIs** (third-party developers)
✅ **CRUD operations** (simple Create/Read/Update/Delete)
✅ **Web applications** (browser clients)
✅ **Caching important** (GET requests cacheable)
✅ **Human-readable** (debugging, documentation)

**Example: E-commerce API**
```http
GET /api/products?category=electronics
GET /api/products/123
POST /api/cart/items
GET /api/orders/456
```

## When to Use RPC (gRPC)

✅ **Microservices communication** (internal)
✅ **Performance critical** (binary protocol faster)
✅ **Streaming** (bi-directional, real-time)
✅ **Polyglot environments** (multiple languages)
✅ **Type safety** (strongly typed contracts)

**Example: Video streaming backend**
```protobuf
service VideoService {
  rpc GetVideo (VideoRequest) returns (Video);
  rpc StreamVideo (stream VideoChunk) returns (stream VideoChunk);
}
```

## gRPC Deep Dive

### Benefits Over Traditional RPC

✅ **Fast:** Protocol Buffers (binary) vs JSON (text)
```
JSON: {"id": 123, "name": "John"} (30 bytes)
Protobuf: binary (15 bytes, much faster parsing)
```

✅ **Strongly typed:**
```protobuf
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
// Compile-time type checking
```

✅ **Streaming:**
```protobuf
// Server streaming (live updates)
rpc GetLiveScores (GameRequest) returns (stream Score);

// Client streaming (file upload)
rpc UploadFile (stream FileChunk) returns (UploadStatus);

// Bi-directional
rpc Chat (stream Message) returns (stream Message);
```

✅ **Code generation:** Auto-generate client/server code
```bash
protoc --go_out=. user.proto  # Go code
protoc --python_out=. user.proto  # Python code
```

### gRPC Example

```protobuf
// user.proto
syntax = "proto3";

service UserService {
  rpc GetUser (UserRequest) returns (User);
}

message UserRequest {
  int32 user_id = 1;
}

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

```python
# Python client (auto-generated)
import grpc
import user_pb2
import user_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = user_pb2_grpc.UserServiceStub(channel)

# Call looks like local function!
response = stub.GetUser(user_pb2.UserRequest(user_id=123))
print(response.name)
```

## GraphQL (Alternative)

**Flexible alternative to REST:**
```graphql
# Single endpoint: /graphql
# Client specifies exactly what data needed

query {
  user(id: 123) {
    name
    email
    posts {
      title
      comments {
        text
      }
    }
  }
}

# No over-fetching or under-fetching
```

**Used by:** Facebook, GitHub, Shopify, Airbnb

## REST vs RPC vs GraphQL

```
REST:
✅ Simple, widely understood
✅ Cacheable
❌ Over-fetching (GET /users returns all fields)
❌ Multiple requests (user + posts = 2 calls)

RPC (gRPC):
✅ Fast, efficient
✅ Streaming support
❌ Not browser-friendly (binary protocol)
❌ Needs code generation

GraphQL:
✅ Flexible queries
✅ Single endpoint
❌ Complex caching
❌ Can be overused (complex queries slow)
```

## Best Practices

### REST
✅ Use HTTP methods correctly (GET = read only, no side effects)
✅ Use plural nouns (`/users` not `/user`)
✅ Version your API (`/v1/users`)
✅ Return meaningful status codes (200, 201, 404, 500)

```http
POST /api/v1/users
Response: 201 Created
Location: /api/v1/users/124
```

### gRPC
✅ Use for internal services (not public APIs)
✅ Define clear .proto contracts
✅ Version your service definitions
✅ Implement proper error handling

```protobuf
enum ErrorCode {
  NOT_FOUND = 0;
  INVALID_ARGUMENT = 1;
}
```

## Interview Tips

**Q: "REST vs RPC?"**

**A:** REST is resource-oriented using HTTP verbs (`GET /users/123`), good for public APIs, human-readable, cacheable. RPC is action-oriented (`getUser(123)`), faster (gRPC uses binary), better for internal microservices. REST = CRUD operations, gRPC = performance-critical internal services.

**Q: "When would you use gRPC?"**

**A:** Use gRPC for internal microservices where performance matters. Benefits: faster than JSON (binary Protocol Buffers), strongly typed, supports streaming, code generation for multiple languages. Not for public APIs (not browser-friendly). Examples: Google, Netflix, Uber use internally.

**Q: "Design an API for a social media app"**

**A:** Public API = REST (mobile apps, third-party devs). Internal services = gRPC (profile service ↔ feed service). REST endpoints: `GET /users/:id`, `POST /posts`, `GET /feed`. gRPC for fast internal calls, streaming for real-time features.

**Key Takeaway:** REST for public APIs (simple, standard), gRPC for internal services (fast, typed). Choose based on use case!
