"""
Read-Through Pattern

Cache acts as a proxy between application and database:
1. Application always reads from cache
2. Cache handles database reads transparently
3. Cache automatically populates itself on misses

Pros:
- Application code is simpler
- Cache logic is centralized
- Consistent cache loading

Cons:
- More complex cache implementation
- Initial cache miss penalty
- Tight coupling between cache and database
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/caching"
REDIS_URL = "redis://localhost:6379/1"
CACHE_TTL = 300

db_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int

class CacheStats(BaseModel):
    reads: int
    cache_hits: int
    database_hits: int

cache_stats = {"reads": 0, "cache_hits": 0, "database_hits": 0}

class ReadThroughCache:
    """
    Cache abstraction that handles read-through logic.
    Application doesn't need to know about cache misses.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db = db_pool
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Read-Through logic:
        1. Try cache first
        2. On miss, automatically load from database
        3. Populate cache transparently
        """
        cache_key = f"user:{user_id}"
        
        # Try cache
        cached = await self.redis.get(cache_key)
        
        if cached:
            cache_stats["cache_hits"] += 1
            return User(**json.loads(cached))
        
        # Cache miss - load from database automatically
        cache_stats["database_hits"] += 1
        row = await self.db.fetchrow(
            "SELECT id, name, email, age FROM users WHERE id = $1",
            user_id
        )
        
        if not row:
            return None
        
        user = User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            age=row["age"]
        )
        
        # Automatically populate cache
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(user.model_dump())
        )
        
        return user
    
    async def invalidate_user(self, user_id: int):
        """Invalidate cache entry."""
        await self.redis.delete(f"user:{user_id}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    app.state.cache = ReadThroughCache(redis_client, db_pool)
    yield
    await db_pool.close()
    await redis_client.close()

app = FastAPI(title="Read-Through Pattern", lifespan=lifespan)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Application just calls cache.get() - cache handles everything.
    No need to check if cache hit or miss.
    """
    cache_stats["reads"] += 1
    
    user = await app.state.cache.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    """Create user - cache will be populated on first read."""
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
    """Update user and invalidate cache."""
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
    
    await app.state.cache.invalidate_user(user_id)
    
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        age=row["age"]
    )

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Delete user and invalidate cache."""
    result = await db_pool.execute(
        "DELETE FROM users WHERE id = $1",
        user_id
    )
    
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="User not found")
    
    await app.state.cache.invalidate_user(user_id)

@app.get("/stats", response_model=CacheStats)
async def get_stats():
    """Get cache statistics."""
    return CacheStats(**cache_stats)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
