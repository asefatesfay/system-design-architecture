"""
Refresh-Ahead Pattern

Proactively refresh cache before expiration:
1. Track popular/frequently accessed items
2. Refresh cache before TTL expires
3. Users always get cached data (no cache miss penalty)

Pros:
- Minimizes cache miss latency
- Always fast reads for hot data
- Predictable performance

Cons:
- Complex implementation
- May refresh data that won't be used
- Need accurate prediction of hot items
- Resource overhead
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Set
import json
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/caching"
REDIS_URL = "redis://localhost:6379/4"
CACHE_TTL = 60  # 1 minute (short for demo)
REFRESH_THRESHOLD = 0.75  # Refresh when 75% of TTL has elapsed
REFRESH_INTERVAL = 10  # Check every 10 seconds
ACCESS_THRESHOLD = 3  # Item accessed 3+ times = hot

db_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int

class RefreshStats(BaseModel):
    total_reads: int
    cache_hits: int
    cache_misses: int
    proactive_refreshes: int
    hot_items: int

refresh_stats = {
    "total_reads": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "proactive_refreshes": 0,
    "hot_items": 0
}

class RefreshAheadCache:
    """
    Cache with proactive refresh-ahead logic.
    Monitors popular items and refreshes before expiration.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db = db_pool
        self.access_count_key = "access_counts"
        self.hot_items_key = "hot_items"
        self.refresh_task = None
    
    async def start_refresh_worker(self):
        """Start background worker for proactive refresh."""
        self.refresh_task = asyncio.create_task(self._refresh_worker())
    
    async def stop_refresh_worker(self):
        """Stop background worker."""
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
    
    async def _refresh_worker(self):
        """
        Background worker that proactively refreshes hot items.
        """
        logger.info("Refresh-ahead worker started")
        
        while True:
            try:
                await asyncio.sleep(REFRESH_INTERVAL)
                await self._refresh_hot_items()
            except asyncio.CancelledError:
                logger.info("Refresh worker cancelled")
                break
            except Exception as e:
                logger.error(f"Refresh worker error: {e}")
    
    async def _refresh_hot_items(self):
        """
        Find hot items and refresh them before they expire.
        """
        # Get hot items
        hot_items = await self.redis.smembers(self.hot_items_key)
        
        if not hot_items:
            return
        
        logger.info(f"Checking {len(hot_items)} hot items for refresh")
        
        for item_key in hot_items:
            try:
                # Check TTL
                ttl = await self.redis.ttl(item_key)
                
                if ttl <= 0:
                    # Already expired, remove from hot items
                    await self.redis.srem(self.hot_items_key, item_key)
                    continue
                
                # Calculate if we should refresh (75% of TTL elapsed)
                if ttl < (CACHE_TTL * (1 - REFRESH_THRESHOLD)):
                    user_id = int(item_key.split(":")[1])
                    await self._refresh_user(user_id)
                    refresh_stats["proactive_refreshes"] += 1
                    logger.info(f"Proactively refreshed user {user_id} (TTL: {ttl}s)")
                
            except Exception as e:
                logger.error(f"Failed to refresh {item_key}: {e}")
        
        # Update hot items count
        refresh_stats["hot_items"] = await self.redis.scard(self.hot_items_key)
    
    async def _refresh_user(self, user_id: int):
        """
        Refresh user data from database to cache.
        """
        row = await self.db.fetchrow(
            "SELECT id, name, email, age FROM users WHERE id = $1",
            user_id
        )
        
        if row:
            user = User(
                id=row["id"],
                name=row["name"],
                email=row["email"],
                age=row["age"]
            )
            
            cache_key = f"user:{user_id}"
            await self.redis.setex(
                cache_key,
                CACHE_TTL,
                json.dumps(user.model_dump())
            )
    
    async def _track_access(self, user_id: int):
        """
        Track item access and mark as hot if accessed frequently.
        """
        cache_key = f"user:{user_id}"
        
        # Increment access count
        access_count = await self.redis.hincrby(
            self.access_count_key,
            cache_key,
            1
        )
        
        # Mark as hot if accessed frequently
        if access_count >= ACCESS_THRESHOLD:
            await self.redis.sadd(self.hot_items_key, cache_key)
            refresh_stats["hot_items"] = await self.redis.scard(self.hot_items_key)
            logger.info(f"User {user_id} marked as HOT (accessed {access_count} times)")
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Read with access tracking for refresh-ahead.
        """
        cache_key = f"user:{user_id}"
        
        # Track access
        await self._track_access(user_id)
        
        # Try cache
        cached = await self.redis.get(cache_key)
        
        if cached:
            refresh_stats["cache_hits"] += 1
            return User(**json.loads(cached))
        
        # Cache miss
        refresh_stats["cache_misses"] += 1
        
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
        
        # Populate cache
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(user.model_dump())
        )
        
        return user
    
    async def create_user(self, user: User) -> User:
        """Create user."""
        row = await self.db.fetchrow(
            """
            INSERT INTO users (name, email, age)
            VALUES ($1, $2, $3)
            RETURNING id, name, email, age
            """,
            user.name, user.email, user.age
        )
        
        created_user = User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            age=row["age"]
        )
        
        # Add to cache
        cache_key = f"user:{created_user.id}"
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(created_user.model_dump())
        )
        
        return created_user
    
    async def update_user(self, user_id: int, user: User) -> Optional[User]:
        """Update user and refresh cache."""
        row = await self.db.fetchrow(
            """
            UPDATE users
            SET name = $1, email = $2, age = $3, updated_at = CURRENT_TIMESTAMP
            WHERE id = $4
            RETURNING id, name, email, age
            """,
            user.name, user.email, user.age, user_id
        )
        
        if not row:
            return None
        
        updated_user = User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            age=row["age"]
        )
        
        # Refresh cache
        cache_key = f"user:{user_id}"
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(updated_user.model_dump())
        )
        
        return updated_user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        result = await self.db.execute(
            "DELETE FROM users WHERE id = $1",
            user_id
        )
        
        if result == "DELETE 0":
            return False
        
        # Remove from cache and hot items
        cache_key = f"user:{user_id}"
        await self.redis.delete(cache_key)
        await self.redis.srem(self.hot_items_key, cache_key)
        await self.redis.hdel(self.access_count_key, cache_key)
        
        return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    app.state.cache = RefreshAheadCache(redis_client, db_pool)
    
    # Start refresh worker
    await app.state.cache.start_refresh_worker()
    
    yield
    
    # Stop refresh worker
    await app.state.cache.stop_refresh_worker()
    
    await db_pool.close()
    await redis_client.close()

app = FastAPI(title="Refresh-Ahead Pattern", lifespan=lifespan)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Read user with refresh-ahead.
    Popular items will be refreshed automatically before expiration.
    """
    refresh_stats["total_reads"] += 1
    
    user = await app.state.cache.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    """Create user."""
    return await app.state.cache.create_user(user)

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    """Update user."""
    updated_user = await app.state.cache.update_user(user_id, user)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Delete user."""
    success = await app.state.cache.delete_user(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/stats", response_model=RefreshStats)
async def get_stats():
    """Get refresh-ahead statistics."""
    return RefreshStats(**refresh_stats)

@app.get("/hot-items")
async def get_hot_items():
    """Get list of hot items being proactively refreshed."""
    hot_items = await redis_client.smembers(app.state.cache.hot_items_key)
    access_counts = await redis_client.hgetall(app.state.cache.access_count_key)
    
    return {
        "hot_items": list(hot_items),
        "access_counts": access_counts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
