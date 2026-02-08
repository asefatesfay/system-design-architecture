"""
Write-Behind (Write-Back) Pattern

Writes are buffered in cache and asynchronously written to database:
1. Write to cache immediately (fast response)
2. Queue write for background processing
3. Batch writes are periodically flushed to database

Pros:
- Very low write latency
- Can batch writes for efficiency
- Handles traffic spikes well

Cons:
- Risk of data loss if cache fails
- Eventual consistency
- Complex error handling
- Need write queue management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import json
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/caching"
REDIS_URL = "redis://localhost:6379/3"
CACHE_TTL = 600
FLUSH_INTERVAL = 5  # seconds
BATCH_SIZE = 10

db_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int

class WriteStats(BaseModel):
    cached_writes: int
    db_flushes: int
    pending_writes: int
    last_flush: Optional[str]

write_stats = {
    "cached_writes": 0,
    "db_flushes": 0,
    "pending_writes": 0,
    "last_flush": None
}

class WriteBehindCache:
    """
    Cache with write-behind (write-back) logic.
    Writes go to cache immediately, then asynchronously to database.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db = db_pool
        self.write_queue_key = "write_queue"
        self.flush_task = None
    
    async def start_flush_worker(self):
        """Start background worker to flush writes to database."""
        self.flush_task = asyncio.create_task(self._flush_worker())
    
    async def stop_flush_worker(self):
        """Stop background worker."""
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
    
    async def _flush_worker(self):
        """
        Background worker that periodically flushes writes to database.
        """
        logger.info("Write-behind flush worker started")
        
        while True:
            try:
                await asyncio.sleep(FLUSH_INTERVAL)
                await self._flush_to_database()
            except asyncio.CancelledError:
                logger.info("Flush worker cancelled")
                break
            except Exception as e:
                logger.error(f"Flush worker error: {e}")
    
    async def _flush_to_database(self):
        """
        Flush pending writes from queue to database in batches.
        """
        # Get pending writes
        writes = []
        for _ in range(BATCH_SIZE):
            data = await self.redis.lpop(self.write_queue_key)
            if not data:
                break
            writes.append(json.loads(data))
        
        if not writes:
            return
        
        logger.info(f"Flushing {len(writes)} writes to database")
        
        # Process writes
        for write in writes:
            try:
                operation = write["operation"]
                user_data = write["user"]
                
                if operation == "create":
                    await self.db.execute(
                        """
                        INSERT INTO users (name, email, age)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (email) DO UPDATE
                        SET name = EXCLUDED.name, age = EXCLUDED.age
                        """,
                        user_data["name"], user_data["email"], user_data["age"]
                    )
                
                elif operation == "update":
                    await self.db.execute(
                        """
                        UPDATE users
                        SET name = $1, email = $2, age = $3, updated_at = CURRENT_TIMESTAMP
                        WHERE id = $4
                        """,
                        user_data["name"], user_data["email"], 
                        user_data["age"], user_data["id"]
                    )
                
                elif operation == "delete":
                    await self.db.execute(
                        "DELETE FROM users WHERE id = $1",
                        user_data["id"]
                    )
                
                write_stats["db_flushes"] += 1
                
            except Exception as e:
                logger.error(f"Failed to flush write: {e}")
                # Re-queue failed write (optional retry logic)
                await self.redis.rpush(self.write_queue_key, json.dumps(write))
        
        write_stats["last_flush"] = datetime.now().isoformat()
        
        # Update pending count
        write_stats["pending_writes"] = await self.redis.llen(self.write_queue_key)
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Read from cache first."""
        cache_key = f"user:{user_id}"
        
        cached = await self.redis.get(cache_key)
        if cached:
            return User(**json.loads(cached))
        
        # Fallback to database
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
        
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(user.model_dump())
        )
        
        return user
    
    async def create_user(self, user: User) -> User:
        """
        Write-Behind Create:
        1. Write to cache immediately (fast!)
        2. Queue for async database write
        """
        # Generate temporary ID (in real scenario, use distributed ID generator)
        user.id = await self.redis.incr("user_id_counter")
        
        cache_key = f"user:{user.id}"
        
        # Step 1: Write to cache immediately
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(user.model_dump())
        )
        
        # Step 2: Queue for database write
        write_operation = {
            "operation": "create",
            "user": user.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.redis.rpush(
            self.write_queue_key,
            json.dumps(write_operation)
        )
        
        write_stats["cached_writes"] += 1
        write_stats["pending_writes"] = await self.redis.llen(self.write_queue_key)
        
        logger.info(f"Write-behind: User {user.id} written to cache, queued for DB")
        return user
    
    async def update_user(self, user_id: int, user: User) -> User:
        """
        Write-Behind Update:
        1. Update cache immediately
        2. Queue for async database update
        """
        user.id = user_id
        cache_key = f"user:{user_id}"
        
        # Update cache
        await self.redis.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(user.model_dump())
        )
        
        # Queue for database
        write_operation = {
            "operation": "update",
            "user": user.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.redis.rpush(
            self.write_queue_key,
            json.dumps(write_operation)
        )
        
        write_stats["cached_writes"] += 1
        write_stats["pending_writes"] = await self.redis.llen(self.write_queue_key)
        
        logger.info(f"Write-behind: User {user_id} updated in cache, queued for DB")
        return user
    
    async def delete_user(self, user_id: int):
        """
        Write-Behind Delete:
        1. Delete from cache immediately
        2. Queue for async database delete
        """
        cache_key = f"user:{user_id}"
        
        # Delete from cache
        await self.redis.delete(cache_key)
        
        # Queue for database
        write_operation = {
            "operation": "delete",
            "user": {"id": user_id},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.redis.rpush(
            self.write_queue_key,
            json.dumps(write_operation)
        )
        
        write_stats["cached_writes"] += 1
        write_stats["pending_writes"] = await self.redis.llen(self.write_queue_key)
        
        logger.info(f"Write-behind: User {user_id} deleted from cache, queued for DB")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    app.state.cache = WriteBehindCache(redis_client, db_pool)
    
    # Start flush worker
    await app.state.cache.start_flush_worker()
    
    yield
    
    # Stop flush worker and flush remaining writes
    await app.state.cache.stop_flush_worker()
    await app.state.cache._flush_to_database()
    
    await db_pool.close()
    await redis_client.close()

app = FastAPI(title="Write-Behind Pattern", lifespan=lifespan)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Read user."""
    user = await app.state.cache.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    """
    Write-behind: Instant response (write to cache only).
    Database write happens asynchronously in background.
    """
    return await app.state.cache.create_user(user)

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    """Write-behind update."""
    return await app.state.cache.update_user(user_id, user)

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Write-behind delete."""
    await app.state.cache.delete_user(user_id)

@app.post("/flush", status_code=202)
async def force_flush():
    """Manually trigger flush to database."""
    await app.state.cache._flush_to_database()
    return {"message": "Flush triggered"}

@app.get("/stats", response_model=WriteStats)
async def get_stats():
    """Get write-behind statistics."""
    return WriteStats(**write_stats)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
