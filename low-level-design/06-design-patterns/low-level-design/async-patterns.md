# Async Patterns in Python

Modern asynchronous programming patterns using `asyncio`, `async`/`await`, and concurrent execution.

## Why Async?

**Problems it solves:**
- I/O-bound operations blocking execution
- Concurrent network requests
- Handling many connections efficiently
- Responsive applications
- Resource efficiency vs threading

```python
# SYNC - blocking, slow
def fetch_all():
    data1 = fetch_url(url1)  # Waits...
    data2 = fetch_url(url2)  # Waits...
    data3 = fetch_url(url3)  # Waits...
    # Total time: 3 seconds

# ASYNC - concurrent, fast
async def fetch_all():
    data1, data2, data3 = await asyncio.gather(
        fetch_url(url1),
        fetch_url(url2),
        fetch_url(url3)
    )
    # Total time: ~1 second (concurrent!)
```

---

## 1. Async/Await Basics

### Simple Async Function

```python
import asyncio


async def say_hello():
    """Async function (coroutine)"""
    print("Hello")
    await asyncio.sleep(1)  # Non-blocking sleep!
    print("World")


# Run async function
asyncio.run(say_hello())
# Hello
# (1 second pause)
# World
```

### Multiple Concurrent Tasks

```python
import asyncio
import time


async def task(name: str, delay: float):
    """Simulate async task"""
    print(f"{name}: Starting")
    await asyncio.sleep(delay)
    print(f"{name}: Completed after {delay}s")
    return f"{name} result"


async def main():
    """Run tasks concurrently"""
    start = time.time()

    # Sequential - slow
    # result1 = await task("Task 1", 2)
    # result2 = await task("Task 2", 1)
    # Total: 3 seconds

    # Concurrent - fast!
    results = await asyncio.gather(
        task("Task 1", 2),
        task("Task 2", 1),
        task("Task 3", 1.5)
    )

    elapsed = time.time() - start
    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Results: {results}")


asyncio.run(main())
# Task 1: Starting
# Task 2: Starting
# Task 3: Starting
# Task 2: Completed after 1s
# Task 3: Completed after 1.5s
# Task 1: Completed after 2s
# Completed in 2.0s (not 4.5s!)
# Results: ['Task 1 result', 'Task 2 result', 'Task 3 result']
```

---

## 2. Async HTTP Requests

### Using aiohttp

```python
import asyncio
import aiohttp
import time


async def fetch_url(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetch single URL asynchronously"""
    print(f"Fetching {url}...")

    async with session.get(url) as response:
        data = await response.json()
        print(f"Completed {url}")
        return {"url": url, "status": response.status, "data": data}


async def fetch_all_urls(urls: list) -> list:
    """Fetch multiple URLs concurrently"""
    async with aiohttp.ClientSession() as session:
        # Create tasks for all URLs
        tasks = [fetch_url(session, url) for url in urls]

        # Run concurrently
        results = await asyncio.gather(*tasks)

        return results


# Usage
urls = [
    "https://api.github.com/users/torvalds",
    "https://api.github.com/users/gvanrossum",
    "https://api.github.com/users/kennethreitz"
]

start = time.time()
results = asyncio.run(fetch_all_urls(urls))
elapsed = time.time() - start

print(f"\nFetched {len(results)} URLs in {elapsed:.2f}s")
# Fetched 3 URLs in ~1s (concurrent) instead of ~3s (sequential)
```

---

## 3. Async Producer-Consumer Pattern

```python
import asyncio
import random
from typing import Any


async def producer(queue: asyncio.Queue, producer_id: int):
    """Produce items and put in queue"""
    for i in range(5):
        # Simulate work
        await asyncio.sleep(random.uniform(0.1, 0.5))

        item = f"Item-{producer_id}-{i}"
        await queue.put(item)
        print(f"Producer {producer_id}: Produced {item}")

    # Signal completion
    await queue.put(None)


async def consumer(queue: asyncio.Queue, consumer_id: int):
    """Consume items from queue"""
    while True:
        # Get item from queue
        item = await queue.get()

        # Check for completion signal
        if item is None:
            queue.task_done()
            break

        # Process item
        print(f"Consumer {consumer_id}: Processing {item}")
        await asyncio.sleep(random.uniform(0.1, 0.3))

        queue.task_done()

    print(f"Consumer {consumer_id}: Finished")


async def main():
    """Run producer-consumer"""
    queue = asyncio.Queue(maxsize=10)

    # Create 2 producers and 3 consumers
    producers = [
        asyncio.create_task(producer(queue, i))
        for i in range(2)
    ]

    consumers = [
        asyncio.create_task(consumer(queue, i))
        for i in range(3)
    ]

    # Wait for producers to finish
    await asyncio.gather(*producers)

    # Wait for queue to be processed
    await queue.join()

    # Cancel consumers (they're waiting for more items)
    for c in consumers:
        c.cancel()


asyncio.run(main())
```

---

## 4. Async Context Manager

```python
import asyncio


class AsyncDatabase:
    """Async context manager for database connection"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    async def __aenter__(self):
        """Async enter - called on 'async with'"""
        print(f"Connecting to {self.connection_string}...")
        await asyncio.sleep(0.5)  # Simulate connection delay
        self.connection = f"Connection to {self.connection_string}"
        print("Connected!")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit - called when leaving 'async with'"""
        print("Closing connection...")
        await asyncio.sleep(0.2)  # Simulate cleanup
        self.connection = None
        print("Connection closed!")

    async def execute(self, query: str):
        """Execute query"""
        print(f"Executing: {query}")
        await asyncio.sleep(0.1)
        return f"Results for: {query}"


async def main():
    """Use async context manager"""

    # Automatically handles connection and cleanup
    async with AsyncDatabase("postgresql://localhost/mydb") as db:
        result = await db.execute("SELECT * FROM users")
        print(result)
    # Connection automatically closed

# Usage
asyncio.run(main())
# Connecting to postgresql://localhost/mydb...
# Connected!
# Executing: SELECT * FROM users
# Results for: SELECT * FROM users
# Closing connection...
# Connection closed!
```

---

## 5. Async Iterator/Generator

```python
import asyncio


class AsyncRange:
    """Async iterator"""

    def __init__(self, count: int):
        self.count = count
        self.current = 0

    def __aiter__(self):
        """Return async iterator (self)"""
        return self

    async def __anext__(self):
        """Get next item"""
        if self.current >= self.count:
            raise StopAsyncIteration

        await asyncio.sleep(0.1)  # Simulate async work
        value = self.current
        self.current += 1
        return value


async def async_generator(n: int):
    """Async generator function"""
    for i in range(n):
        await asyncio.sleep(0.1)  # Simulate async work
        yield i


async def main():
    """Use async iterators"""

    # Using async iterator
    print("Async Iterator:")
    async for num in AsyncRange(5):
        print(f"Got: {num}")

    print("\nAsync Generator:")
    async for num in async_generator(5):
        print(f"Got: {num}")


asyncio.run(main())
```

---

## 6. Async Timeout Pattern

```python
import asyncio


async def long_running_task():
    """Simulate long task"""
    print("Task: Starting long operation...")
    await asyncio.sleep(5)
    print("Task: Completed!")
    return "Success"


async def task_with_timeout():
    """Run task with timeout"""
    try:
        # Timeout after 2 seconds
        result = await asyncio.wait_for(
            long_running_task(),
            timeout=2.0
        )
        print(f"Result: {result}")

    except asyncio.TimeoutError:
        print("Task timed out after 2 seconds!")


# Usage
asyncio.run(task_with_timeout())
# Task: Starting long operation...
# Task timed out after 2 seconds!
```

---

## 7. Async Rate Limiting

```python
import asyncio
import time
from collections import deque


class AsyncRateLimiter:
    """Async rate limiter"""

    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        """Acquire rate limit slot"""
        async with self._lock:
            now = time.time()

            # Remove old calls
            while self.calls and now - self.calls[0] > self.period:
                self.calls.popleft()

            # Wait if at limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                print(f"Rate limit: Waiting {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

                # Remove old call
                self.calls.popleft()

            # Record this call
            self.calls.append(time.time())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        pass


async def api_call(limiter: AsyncRateLimiter, call_id: int):
    """Make rate-limited API call"""
    async with limiter:
        print(f"Call {call_id}: Making request")
        await asyncio.sleep(0.1)
        print(f"Call {call_id}: Completed")


async def main():
    """Test rate limiter"""
    # Max 3 calls per 2 seconds
    limiter = AsyncRateLimiter(max_calls=3, period=2.0)

    # Try to make 6 calls
    tasks = [api_call(limiter, i) for i in range(6)]
    await asyncio.gather(*tasks)


asyncio.run(main())
# Call 0: Making request
# Call 1: Making request
# Call 2: Making request
# Call 0: Completed
# Call 1: Completed
# Call 2: Completed
# Rate limit: Waiting 1.90s
# Call 3: Making request
# ...
```

---

## 8. Async Retry Pattern

```python
import asyncio
import random


async def flaky_operation():
    """Operation that randomly fails"""
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Random failure")
    return "Success!"


async def retry_async(
    coro_func,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
):
    """Retry async operation with exponential backoff"""

    attempt = 0
    current_delay = delay

    while attempt < max_attempts:
        try:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts}")

            result = await coro_func()
            print(f"Success on attempt {attempt}!")
            return result

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

            if attempt >= max_attempts:
                print("Max attempts reached!")
                raise

            # Wait with exponential backoff
            print(f"Retrying in {current_delay:.1f}s...")
            await asyncio.sleep(current_delay)
            current_delay *= backoff


async def main():
    """Test retry"""
    try:
        result = await retry_async(
            flaky_operation,
            max_attempts=5,
            delay=0.5,
            backoff=2.0
        )
        print(f"Final result: {result}")
    except Exception as e:
        print(f"Failed: {e}")


asyncio.run(main())
```

---

## 9. Async Worker Pool

```python
import asyncio
from typing import Callable, Any, List


class AsyncWorkerPool:
    """Pool of async workers"""

    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.queue = asyncio.Queue()
        self.results = []

    async def worker(self, worker_id: int, task_func: Callable):
        """Worker that processes tasks from queue"""
        while True:
            # Get task
            task_data = await self.queue.get()

            if task_data is None:  # Poison pill
                self.queue.task_done()
                break

            # Process task
            print(f"Worker {worker_id}: Processing {task_data}")
            try:
                result = await task_func(task_data)
                self.results.append(result)
            except Exception as e:
                print(f"Worker {worker_id}: Error - {e}")

            self.queue.task_done()

        print(f"Worker {worker_id}: Shutting down")

    async def map(self, task_func: Callable, items: List[Any]) -> List[Any]:
        """Map function over items using worker pool"""

        # Add items to queue
        for item in items:
            await self.queue.put(item)

        # Add poison pills for workers
        for _ in range(self.num_workers):
            await self.queue.put(None)

        # Create workers
        workers = [
            asyncio.create_task(self.worker(i, task_func))
            for i in range(self.num_workers)
        ]

        # Wait for completion
        await self.queue.join()
        await asyncio.gather(*workers)

        return self.results


# Example task
async def process_item(item: int) -> int:
    """Simulate processing"""
    await asyncio.sleep(random.uniform(0.1, 0.5))
    return item * 2


async def main():
    """Use worker pool"""
    pool = AsyncWorkerPool(num_workers=3)

    items = list(range(10))
    results = await pool.map(process_item, items)

    print(f"\nResults: {sorted(results)}")


asyncio.run(main())
```

---

## 10. Threading vs Asyncio

### When to Use What

```python
import asyncio
import time
import threading


# CPU-Bound - Use Threading/Multiprocessing
def cpu_intensive(n: int) -> int:
    """CPU-bound operation"""
    total = 0
    for i in range(n):
        total += i ** 2
    return total


# I/O-Bound - Use Asyncio
async def io_intensive(url: str) -> str:
    """I/O-bound operation"""
    # Simulated network request
    await asyncio.sleep(1)
    return f"Data from {url}"


# Comparison
def compare():
    """Compare threading vs asyncio"""

    # Threading for CPU-bound
    start = time.time()
    threads = []
    for i in range(3):
        t = threading.Thread(target=cpu_intensive, args=(1000000,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Threading (CPU-bound): {time.time() - start:.2f}s")

    # Asyncio for I/O-bound
    async def test_async():
        start = time.time()
        await asyncio.gather(
            io_intensive("url1"),
            io_intensive("url2"),
            io_intensive("url3")
        )
        print(f"Asyncio (I/O-bound): {time.time() - start:.2f}s")

    asyncio.run(test_async())
```

### Comparison Table

| Aspect | Threading | Asyncio |
|--------|-----------|---------|
| **Best For** | CPU-bound, blocking I/O | I/O-bound, many connections |
| **Concurrency** | True parallelism | Cooperative multitasking |
| **Overhead** | Higher (OS threads) | Lower (single thread) |
| **Complexity** | Simpler | More complex (async/await) |
| **Scaling** | Limited by threads | Scales to 10,000+ connections |
| **GIL Impact** | Yes (Python) | No |

---

## 11. Common Async Patterns Summary

### Pattern Cheat Sheet

```python
# 1. Basic async function
async def func():
    await asyncio.sleep(1)

# 2. Run multiple concurrently
await asyncio.gather(func1(), func2(), func3())

# 3. Timeout
await asyncio.wait_for(func(), timeout=5.0)

# 4. Queue (producer-consumer)
queue = asyncio.Queue()
await queue.put(item)
item = await queue.get()

# 5. Context manager
async with AsyncResource() as resource:
    await resource.use()

# 6. Iterator
async for item in async_iterator:
    process(item)

# 7. Create task (fire and forget)
task = asyncio.create_task(func())

# 8. Wait for first completion
done, pending = await asyncio.wait(
    [task1, task2],
    return_when=asyncio.FIRST_COMPLETED
)

# 9. Sleep (non-blocking)
await asyncio.sleep(1)

# 10. Run in executor (for blocking code)
result = await loop.run_in_executor(None, blocking_func)
```

---

## 12. Interview Tips

### Common Questions

**Q: "What's the difference between async and threading?"**
- **Async**: Single-threaded, cooperative, I/O-bound
- **Threading**: Multi-threaded, preemptive, CPU/I/O-bound

**Q: "When to use asyncio vs threading?"**
- **Asyncio**: Many I/O operations (web requests, DB queries)
- **Threading**: CPU-bound tasks, blocking libraries

**Q: "What is async/await?"**
- `async def`: Defines coroutine function
- `await`: Suspends coroutine until result ready
- Non-blocking concurrency

**Q: "Implement async rate limiter"**
```python
class RateLimiter:
    def __init__(self, rate, period):
        self.rate = rate
        self.period = period
        self.calls = deque()

    async def acquire(self):
        async with asyncio.Lock():
            now = time.time()
            while self.calls and now - self.calls[0] > self.period:
                self.calls.popleft()
            if len(self.calls) >= self.rate:
                await asyncio.sleep(self.period - (now - self.calls[0]))
            self.calls.append(time.time())
```

### Best Practices

✅ Use `asyncio.gather()` for concurrent execution
✅ Add timeouts with `asyncio.wait_for()`
✅ Use `async with` for resource management
✅ Handle `CancelledError` in tasks
✅ Use `asyncio.Queue` for producer-consumer
✅ Profile to ensure async is beneficial

### Red Flags

❌ Mixing `async` with blocking code
❌ Not using `await` (creates unawaited coroutine)
❌ Using asyncio for CPU-bound tasks
❌ Forgetting to `await` I/O operations
❌ Not handling task cancellation

---

## Quick Reference

```python
import asyncio

# Basic async function
async def main():
    result = await async_operation()
    return result

# Run async function
asyncio.run(main())

# Concurrent execution
results = await asyncio.gather(op1(), op2(), op3())

# Timeout
result = await asyncio.wait_for(operation(), timeout=5.0)

# Queue
queue = asyncio.Queue()
await queue.put(item)
item = await queue.get()

# Context manager
async with AsyncResource() as r:
    await r.use()

# Iterator
async for item in async_gen():
    process(item)
```

---

**Related Topics:**
- [Concurrency Design](./02-interview-types/concurrency-design/README.md)
- [Threading Patterns](./03-oop-fundamentals/threading.md)
- [Design Patterns](./06-design-patterns/README.md)

**Back to:** [Low-Level Design](./README.md)
