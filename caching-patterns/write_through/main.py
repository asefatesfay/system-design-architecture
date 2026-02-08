"""
Write-Through Pattern

All writes go through cache to database synchronously:
1. Write to cache first
2. Write to database immediately (synchronously)
3. Both succeed or both fail (transactional)

Pros:
- Strong consistency (cache always reflects database)
- No data loss risk
- Simple to reason about

Cons:
- Higher write latency (2 operations)
- Cache contains data that may never be read
- Database write failures break the cache
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/caching"
REDIS_URL = "redis://localhost:6379/2"
CACHE_TTL = 600  # 10 minutes

db_pool: Optional[asyncpg.Pool] = None
redis_client: Optional[redis.Redis] = None

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    age: int

class WriteStats(BaseModel):
    total_writes: int
    successful_writes: int
    failed_writes: int

write_stats = {"total_writes": 0, "successful_writes": 0, "failed_writes": 0}

class WriteThroughCache:
    """
    Cache that ensures writes go to both cache and database synchronously.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db = db_pool
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Read from cache first, then database."""
        cache_key = f"user:{user_id}"
        
        cached = await self.redis.get(cache_key)
        if cached:
            return User(**json.loads(cached))
        
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
        """
        Write-Through Create:
        1. Insert into database first
        2. Immediately write to cache
        Both must succeed
        """
        try:
            # Step 1: Write to database
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
            
            # Step 2: Write to cache immediately
            cache_key = f"user:{created_user.id}"
            await self.redis.setex(
                cache_key,
                CACHE_TTL,
                json.dumps(created_user.model_dump())
            )
            
            logger.info(f"Write-through: Created user {created_user.id} in DB and cache")
            return created_user
            
        except Exception as e:
            logger.error(f"Write-through failed: {e}")
            raise
    
    async def update_user(self, user_id: int, user: User) -> User:
        """
        Write-Through Update:
        1. Update database
        2. Update cache immediately
        Both operations are synchronous
        """
        cache_key = f"user:{user_id}"
        
        try:
            # Step 1: Update database
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
            
            # Step 2: Update cache immediately
            await self.redis.setex(
                cache_key,
                CACHE_TTL,
                json.dumps(updated_user.model_dump())
            )
            
            logger.info(f"Write-through: Updated user {user_id} in DB and cache")
            return updated_user
            
        except Exception as e:
            logger.error(f"Write-through update failed: {e}")
            # On failure, invalidate cache to maintain consistency
            await self.redis.delete(cache_key)
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Write-Through Delete:
        1. Delete from database
        2. Delete from cache
        """
        cache_key = f"user:{user_id}"
        
        try:
            result = await self.db.execute(
                "DELETE FROM users WHERE id = $1",
                user_id
            )
            
            if result == "DELETE 0":
                return False
            
            # Delete from cache
            await self.redis.delete(cache_key)
            
            logger.info(f"Write-through: Deleted user {user_id} from DB and cache")
            return True
            
        except Exception as e:
            logger.error(f"Write-through delete failed: {e}")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    app.state.cache = WriteThroughCache(redis_client, db_pool)
    yield
    await db_pool.close()
    await redis_client.close()

app = FastAPI(title="Write-Through Pattern", lifespan=lifespan)

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Read user (cache-first)."""
    user = await app.state.cache.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    """
    Write-through: Write to both DB and cache synchronously.
    Higher latency but strong consistency.
    """
    write_stats["total_writes"] += 1
    
    try:
        created_user = await app.state.cache.create_user(user)
        write_stats["successful_writes"] += 1
        return created_user
    except Exception as e:
        write_stats["failed_writes"] += 1
        raise HTTPException(status_code=500, detail=f"Write failed: {str(e)}")

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    """Write-through update."""
    write_stats["total_writes"] += 1
    
    try:
        updated_user = await app.state.cache.update_user(user_id, user)
        
        if not updated_user:
            write_stats["failed_writes"] += 1
            raise HTTPException(status_code=404, detail="User not found")
        
        write_stats["successful_writes"] += 1
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        write_stats["failed_writes"] += 1
        raise HTTPException(status_code=500, detail=f"Write failed: {str(e)}")

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """Write-through delete."""
    write_stats["total_writes"] += 1
    
    try:
        success = await app.state.cache.delete_user(user_id)
        
        if not success:
            write_stats["failed_writes"] += 1
            raise HTTPException(status_code=404, detail="User not found")
        
        write_stats["successful_writes"] += 1
    except HTTPException:
        raise
    except Exception as e:
        write_stats["failed_writes"] += 1
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.get("/stats", response_model=WriteStats)
async def get_stats():
    """Get write statistics."""
    return WriteStats(**write_stats)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
