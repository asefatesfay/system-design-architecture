"""
Cache-Aside Pattern (Lazy Loading)

The application is responsible for managing the cache:
1. Check cache first
2. If miss, read from database
3. Write to cache for future reads
4. On writes, invalidate cache

Pros:
- Simple to implement
- Only caches what's actually requested
- Cache failures don't break the app

Cons:
- Cache miss penalty (read latency)
- Potential stale data
- Cache warming needed after restart
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/caching"
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 300  # 5 minutes

# Global connections
db_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None

# Pydantic models
class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int

class CacheStats(BaseModel):
    hits: int
    misses: int
    hit_rate: float

# Cache statistics
cache_stats = {"hits": 0, "misses": 0}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    yield
    # Shutdown
    await db_pool.close()
    await redis_client.close()

app = FastAPI(title="Cache-Aside Pattern", lifespan=lifespan)

def get_cache_key(user_id: int) -> str:
    return f"user:{user_id}"

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Cache-Aside Read Pattern:
    1. Try to get from cache
    2. If cache miss, get from database
    3. Store in cache for future reads
    """
    cache_key = get_cache_key(user_id)
    
    # Step 1: Try cache first
    cached_user = await redis_client.get(cache_key)
    
    if cached_user:
        # Cache HIT
        cache_stats["hits"] += 1
        return User(**json.loads(cached_user))
    
    # Cache MISS
    cache_stats["misses"] += 1
    
    # Step 2: Get from database
    row = await db_pool.fetchrow(
        "SELECT id, name, email, age FROM users WHERE id = $1",
        user_id
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        age=row["age"]
    )
    
    # Step 3: Store in cache
    await redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(user.model_dump())
    )
    
    return user

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    """
    Create user in database only.
    Cache will be populated on first read (lazy loading).
    """
    row = await db_pool.fetchrow(
        """
        INSERT INTO users (name, email, age)
        VALUES ($1, $2, $3)
        RETURNING id, name, email, age
        """,
        user.name, user.email, user.age
    )
    
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        age=row["age"]
    )

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    """
    Cache-Aside Write Pattern:
    1. Update database
    2. Invalidate cache (delete from cache)
    3. Next read will repopulate cache
    """
    cache_key = get_cache_key(user_id)
    
    # Step 1: Update database
    row = await db_pool.fetchrow(
        """
        UPDATE users
        SET name = $1, email = $2, age = $3, updated_at = CURRENT_TIMESTAMP
        WHERE id = $4
        RETURNING id, name, email, age
        """,
        user.name, user.email, user.age, user_id
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 2: Invalidate cache
    await redis_client.delete(cache_key)
    
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        age=row["age"]
    )

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """
    Delete from database and invalidate cache.
    """
    cache_key = get_cache_key(user_id)
    
    result = await db_pool.execute(
        "DELETE FROM users WHERE id = $1",
        user_id
    )
    
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="User not found")
    
    # Invalidate cache
    await redis_client.delete(cache_key)

@app.get("/stats", response_model=CacheStats)
async def get_stats():
    """Get cache hit/miss statistics."""
    total = cache_stats["hits"] + cache_stats["misses"]
    hit_rate = cache_stats["hits"] / total if total > 0 else 0.0
    
    return CacheStats(
        hits=cache_stats["hits"],
        misses=cache_stats["misses"],
        hit_rate=round(hit_rate, 3)
    )

@app.post("/cache/clear", status_code=204)
async def clear_cache():
    """Clear all user caches."""
    keys = await redis_client.keys("user:*")
    if keys:
        await redis_client.delete(*keys)
    cache_stats["hits"] = 0
    cache_stats["misses"] = 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
