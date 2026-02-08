# Distributed Locking

## Definition

**Distributed Locking** enables multiple processes or services across different machines to coordinate access to shared resources, ensuring only one process can access a resource at a time.

## The Problem

```
Without locking:
Service A → Update inventory count → Read: 10 → Write: 9
Service B → Update inventory count → Read: 10 → Write: 9

Expected: 8 (both decreased)
Actual: 9 (race condition) ❌
```

```
With distributed lock:
Service A → Acquire lock → Read: 10 → Write: 9 → Release lock ✓
Service B → Try acquire lock (blocked) → Wait → Acquire → Read: 9 → Write: 8 ✓

Result: 8 (correct) ✅
```

## Use Cases

✅ **Preventing duplicate work**
```
Job: Send daily email report
Multiple workers → Only one should send
Use lock to ensure single execution
```

✅ **Leader election**
```
Multiple service instances → One becomes leader
Leader processes tasks, others standby
```

✅ **Rate limiting (distributed)**
```
Max 1000 API calls/minute across all servers
Lock to increment global counter atomically
```

✅ **Resource allocation**
```
Assign tasks to workers
Lock to ensure task not assigned twice
```

✅ **Database migrations**
```
Multiple app instances starting up
Only one should run migrations
```

## Real-World Examples

### Uber (Redis Locks)
```python
# Prevent duplicate ride assignment
def assign_driver(ride_id, driver_id):
    lock = redis_lock(f"ride:{ride_id}")
    
    if lock.acquire(timeout=5):
        try:
            # Only one worker assigns driver
            if ride.status == "pending":
                ride.assign_driver(driver_id)
                ride.status = "assigned"
        finally:
            lock.release()
```

### Stripe (Leader Election for Background Jobs)
```
Multiple job processor instances
- Instance 1: Acquires lock → Becomes leader → Processes jobs
- Instance 2, 3: Fail to acquire → Standby
- Instance 1 crashes → Instance 2 acquires lock → New leader
```

### Netflix (Distributed Cron)
```
Run batch job once daily across cluster
- Service instance acquires lock
- Runs job
- Other instances skip (lock already held)

Prevents duplicate execution ✓
```

## Implementation Approaches

### 1. Redis (Most Common)

**Using SETNX (SET if Not eXists):**

```python
import redis
import uuid
import time

client = redis.Redis()

def acquire_lock(lock_name, timeout=10):
    lock_id = str(uuid.uuid4())  # Unique identifier
    end_time = time.time() + timeout
    
    while time.time() < end_time:
        # Try to acquire lock (expires in 10 seconds)
        if client.set(lock_name, lock_id, nx=True, ex=10):
            return lock_id  # Lock acquired!
        time.sleep(0.1)  # Wait before retry
    
    return None  # Timeout

def release_lock(lock_name, lock_id):
    # Lua script for atomic check-and-delete
    lua_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    client.eval(lua_script, 1, lock_name, lock_id)

# Usage
lock_id = acquire_lock("inventory:product123")
if lock_id:
    try:
        # Critical section
        update_inventory()
    finally:
        release_lock("inventory:product123", lock_id)
```

**Redlock Algorithm (Multi-Master):**

```
Problem: Single Redis instance fails → Lock lost
Solution: Redlock with 5 Redis masters

1. Get current timestamp
2. Try to acquire lock on all 5 instances
3. If acquired on majority (3/5) within timeout → Success
4. Else release all locks and retry

Survives 2/5 Redis failures ✓
```

```python
from redlock import Redlock

locks = Redlock([
    "redis://node1:6379",
    "redis://node2:6379",
    "redis://node3:6379",
    "redis://node4:6379",
    "redis://node5:6379"
])

lock = locks.lock("resource_name", 10000)  # 10 second TTL
if lock:
    try:
        # Critical section
        process_payment()
    finally:
        locks.unlock(lock)
```

### 2. ZooKeeper

**Ephemeral nodes for locking:**

```python
from kazoo.client import KazooClient

zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()

lock = zk.Lock("/locks/my_resource")

with lock:
    # Critical section
    # Lock automatically released if client disconnects (ephemeral)
    update_shared_resource()
```

**Benefits:**
- Lock automatically released on client crash
- Supports watch (notify when lock available)

**Used by:** Kafka, HBase, Hadoop

### 3. etcd (Kubernetes)

**Lease-based locking:**

```python
import etcd3

etcd = etcd3.client()

# Create lease (auto-expires)
lease = etcd.lease(ttl=10)

# Try to acquire lock
lock = etcd.lock('my_lock', ttl=10)
lock.acquire()

try:
    # Critical section
    deploy_config()
finally:
    lock.release()
```

**Used by:** Kubernetes for leader election

### 4. Database

**Using database row with FOR UPDATE:**

```sql
-- PostgreSQL
BEGIN;
SELECT * FROM locks WHERE resource = 'inventory' FOR UPDATE NOWAIT;
-- If succeeds, lock acquired
-- Do work
UPDATE inventory SET count = count - 1 WHERE product_id = 123;
COMMIT;
-- Lock released
```

**Benefits:**
- Reuse existing infrastructure
- ACID guarantees

**Drawbacks:**
- Database load
- Not designed for high-concurrency locking

## Challenges

### 1. Deadlocks

```
Service A: Holds Lock1, wants Lock2
Service B: Holds Lock2, wants Lock1
→ Deadlock! ❌

Solutions:
- Always acquire locks in same order
- Lock timeout (give up and retry)
```

### 2. Lock Expiration

```
Service A acquires lock (10 second TTL)
Service A processes... (slow, takes 15 seconds)
Lock expires at 10 seconds
Service B acquires same lock
Both services in critical section! ❌

Solution: Lock extension (renew before expiry)
```

```python
import threading

def extend_lock(redis_client, lock_name, lock_id):
    while True:
        time.sleep(5)  # Extend every 5 seconds
        redis_client.expire(lock_name, 10)  # Reset to 10 seconds

# In main thread
lock_id = acquire_lock("my_lock")
extender = threading.Thread(target=extend_lock, args=(client, "my_lock", lock_id))
extender.daemon = True
extender.start()
```

### 3. Network Partitions

```
Service acquires lock from Redis
Network partition → Service thinks it has lock
But Redis failed over to replica (doesn't have lock)
Another service acquires lock
Two services have lock! ❌

Solution: Redlock (majority of nodes)
```

### 4. Clock Skew

```
Lock with 10 second TTL
Server clock fast → Lock expires early
Server clock slow → Lock held too long

Solution: Use monotonic clocks, not wall clocks
```

## Patterns

### 1. Leader Election

```python
# Multiple instances compete for leader lock
def become_leader():
    while True:
        lock = acquire_lock("leader")
        if lock:
            print("I am the leader!")
            try:
                while True:
                    process_tasks()
                    renew_lock(lock)
            except LockLost:
                print("Lost leadership")
        else:
            print("Follower, waiting...")
            time.sleep(5)
```

### 2. Distributed Mutex

```python
class DistributedMutex:
    def __enter__(self):
        self.lock_id = acquire_lock(self.resource)
        if not self.lock_id:
            raise Exception("Failed to acquire lock")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        release_lock(self.resource, self.lock_id)

# Usage
with DistributedMutex("payment:user123"):
    process_payment()
```

### 3. Fair Queuing (FIFO)

```python
# ZooKeeper sequential nodes
zk.create("/locks/resource-", ephemeral=True, sequence=True)
# Creates: /locks/resource-0000000001

# Check if I have smallest sequence number
my_seq = 1
children = zk.get_children("/locks")
if min(children) == my_seq:
    # I'm first, acquire lock
else:
    # Wait for predecessor to release
    watch_predecessor()
```

## Best Practices

✅ **Always set lock timeout (TTL)**
```
Never hold lock forever
Auto-release if service crashes
```

✅ **Use unique lock identifiers**
```
UUID per lock acquisition
Prevent releasing someone else's lock
```

✅ **Keep critical section small**
```
Acquire lock → Quick operation → Release
Don't hold lock during network I/O
```

✅ **Handle lock renewal**
```
For long operations, extend lock before expiry
Or use fencing tokens
```

✅ **Implement retries with exponential backoff**
```
Failed to acquire → Wait → Retry
Avoid thundering herd
```

✅ **Monitor lock contention**
```
Alert on high lock wait times
Indicates bottleneck
```

## Comparison

| Solution | Complexity | Availability | Performance |
|----------|------------|--------------|-------------|
| **Redis (single)** | Low | Single point of failure | Excellent |
| **Redlock** | Medium | High (survives failures) | Good |
| **ZooKeeper** | Medium | High | Good |
| **etcd** | Medium | High | Good |
| **Database** | Low | Depends on DB | Poor (not designed for locks) |

## Interview Tips

**Q: "What is distributed locking?"**

**A:** Coordinate access to shared resources across multiple machines. Example: Multiple services updating inventory, need lock to prevent race conditions. Common implementations: Redis (SETNX), ZooKeeper (ephemeral nodes), etcd. Used by Uber for ride assignment, Stripe for leader election.

**Q: "How to implement distributed lock with Redis?"**

**A:** Use SETNX (set if not exists) with expiration. Acquire: `SET lock_name unique_id NX EX 10` (10 second TTL). Release: Use Lua script to atomically check ID and delete. Prevents duplicate work, handles crashes (auto-expire). For high availability, use Redlock with 5 Redis instances.

**Q: "What are challenges with distributed locks?"**

**A:** 1) Deadlocks (solution: acquire locks in order, timeouts), 2) Lock expiration (operation slower than TTL, solution: renew lock), 3) Network partitions (solution: Redlock with majority), 4) Clock skew (solution: monotonic clocks). Balance between correctness and availability.

**Q: "Design leader election for distributed system"**

**A:** Use distributed lock. All instances try to acquire lock (Redis/ZooKeeper). Winner becomes leader, processes tasks, renews lock periodically. Others wait. If leader crashes, lock expires/released, new instance acquires and becomes leader. Used by Kafka, Kubernetes, background job processors.

**Key Takeaway:** Distributed locks prevent race conditions in distributed systems. Redis (simple), Redlock (reliable)!
