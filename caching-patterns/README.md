# Caching Patterns with FastAPI

This project demonstrates various caching patterns using FastAPI, Redis, and PostgreSQL.

## Patterns Covered

1. **Cache-Aside (Lazy Loading)** - Application manages cache explicitly
2. **Read-Through** - Cache sits between application and database
3. **Write-Through** - Write to cache and database synchronously
4. **Write-Behind (Write-Back)** - Write to cache immediately, database asynchronously
5. **Refresh-Ahead** - Proactively refresh cache before expiration

## Setup

### Prerequisites
- Python 3.11+
- Poetry
- Docker & Docker Compose (for PostgreSQL and Redis)

### Installation

```bash
# Install dependencies
poetry install

# Start infrastructure
docker-compose up -d

# Run the application
poetry run uvicorn cache_aside.main:app --reload --port 8000
```

## Running Examples

Each pattern has its own FastAPI application:

```bash
# Cache-Aside Pattern
poetry run uvicorn cache_aside.main:app --reload --port 8001

# Read-Through Pattern
poetry run uvicorn read_through.main:app --reload --port 8002

# Write-Through Pattern
poetry run uvicorn write_through.main:app --reload --port 8003

# Write-Behind Pattern
poetry run uvicorn write_behind.main:app --reload --port 8004

# Refresh-Ahead Pattern
poetry run uvicorn refresh_ahead.main:app --reload --port 8005
```

## API Endpoints

Each pattern typically exposes:
- `GET /users/{user_id}` - Get user by ID
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /stats` - Cache statistics

## Pattern Comparison

| Pattern | Read Performance | Write Performance | Consistency | Complexity |
|---------|------------------|-------------------|-------------|------------|
| Cache-Aside | High (after cache) | Medium | Eventual | Low |
| Read-Through | High | Medium | Eventual | Medium |
| Write-Through | High | Low | Strong | Medium |
| Write-Behind | High | High | Eventual | High |
| Refresh-Ahead | Very High | Medium | Eventual | High |

## Testing

```bash
# Run tests
poetry run pytest

# Load testing
poetry run locust -f locustfile.py
```
