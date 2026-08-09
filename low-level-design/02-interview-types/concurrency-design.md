# Concurrency Design Interviews

## Overview

Concurrency interviews focus on designing systems that work correctly when multiple threads access shared data simultaneously. These can appear as standalone problems or as extensions to regular LLD questions.

## Format

- **Duration**: 30-60 minutes (or added to existing LLD problem)
- **Focus**: Thread safety, race conditions, deadlocks
- **Common at**: Google, Amazon, Microsoft, high-frequency trading firms
- **Level**: Usually mid-level to senior positions

## Key Concepts to Master

### 1. Race Conditions

**What**: Multiple threads accessing shared data, at least one writing, without proper synchronization.

```python
# PROBLEM: Race condition
class BankAccount:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        # NOT THREAD-SAFE!
        current = self.balance  # Thread 1 reads: 100
        # Context switch here...  # Thread 2 reads: 100
        self.balance = current + amount  # Both write, one deposit lost!

# SOLUTION: Use locks
import threading

class BankAccount:
    def __init__(self):
        self.balance = 0
        self._lock = threading.Lock()

    def deposit(self, amount):
        with self._lock:  # Only one thread can execute this at a time
            current = self.balance
            self.balance = current + amount
```

### 2. Deadlocks

**What**: Two or more threads waiting for each other to release resources.

```python
# PROBLEM: Deadlock scenario
class BankTransfer:
    def transfer(self, from_account, to_account, amount):
        with from_account.lock:  # Thread 1 locks A
            with to_account.lock:  # Thread 2 locks B, waits for A
                # Thread 1 waits for B
                from_account.balance -= amount
                to_account.balance += amount

# SOLUTION: Always acquire locks in consistent order
class BankTransfer:
    def transfer(self, from_account, to_account, amount):
        # Always lock accounts in consistent order (by ID)
        first = from_account if from_account.id < to_account.id else to_account
        second = to_account if from_account.id < to_account.id else from_account

        with first.lock:
            with second.lock:
                from_account.balance -= amount
                to_account.balance += amount
```

### 3. Thread Synchronization Primitives

```python
import threading
from queue import Queue
from collections import deque
import time

# 1. Lock - Mutual exclusion
lock = threading.Lock()
with lock:
    # Critical section
    pass

# 2. RLock - Reentrant lock (same thread can acquire multiple times)
rlock = threading.RLock()

# 3. Semaphore - Limit concurrent access
semaphore = threading.Semaphore(3)  # Allow 3 threads
with semaphore:
    # At most 3 threads can be here
    pass

# 4. Event - Signal between threads
event = threading.Event()
event.wait()  # Block until set
event.set()   # Wake up waiting threads
event.clear() # Reset

# 5. Condition - Wait for specific condition
condition = threading.Condition()
with condition:
    condition.wait()    # Wait for notification
    condition.notify()  # Wake one thread
    condition.notify_all()  # Wake all threads
```

## Common Concurrency Problems

### Problem 1: Thread-Safe Counter

```python
class Counter:
    """A thread-safe counter"""

    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1

    def decrement(self):
        with self._lock:
            self._value -= 1

    def get_value(self):
        with self._lock:
            return self._value

# Test with multiple threads
def test_counter():
    counter = Counter()
    threads = []

    def increment_many():
        for _ in range(10000):
            counter.increment()

    # Create 10 threads
    for _ in range(10):
        t = threading.Thread(target=increment_many)
        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    print(f"Final count: {counter.get_value()}")  # Should be 100000
```

### Problem 2: Producer-Consumer Pattern

```python
from queue import Queue
import threading
import time
import random

class ProducerConsumer:
    """Classic producer-consumer problem"""

    def __init__(self, buffer_size=10):
        self.buffer = Queue(maxsize=buffer_size)
        self.is_running = True

    def producer(self, producer_id):
        """Produce items and add to buffer"""
        while self.is_running:
            item = f"Item-{random.randint(1, 100)}"
            self.buffer.put(item)  # Blocks if buffer is full
            print(f"Producer {producer_id} produced: {item}")
            time.sleep(random.uniform(0.1, 0.5))

    def consumer(self, consumer_id):
        """Consume items from buffer"""
        while self.is_running:
            try:
                item = self.buffer.get(timeout=1)  # Wait up to 1 second
                print(f"Consumer {consumer_id} consumed: {item}")
                time.sleep(random.uniform(0.2, 0.7))
                self.buffer.task_done()
            except:
                pass

    def run(self, num_producers=2, num_consumers=3, duration=5):
        """Run the simulation"""
        threads = []

        # Start producers
        for i in range(num_producers):
            t = threading.Thread(target=self.producer, args=(i,))
            t.start()
            threads.append(t)

        # Start consumers
        for i in range(num_consumers):
            t = threading.Thread(target=self.consumer, args=(i,))
            t.start()
            threads.append(t)

        # Run for specified duration
        time.sleep(duration)
        self.is_running = False

        # Wait for all threads
        for t in threads:
            t.join()

# Usage
pc = ProducerConsumer(buffer_size=5)
pc.run(num_producers=2, num_consumers=3, duration=5)
```

### Problem 3: Thread-Safe Singleton

```python
class Singleton:
    """Thread-safe singleton implementation"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

# Alternative: Use decorator
def synchronized(func):
    """Decorator to make method thread-safe"""
    func.__lock__ = threading.Lock()

    def wrapper(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)
    return wrapper

class Database:
    def __init__(self):
        self.connections = 0

    @synchronized
    def connect(self):
        self.connections += 1
        print(f"Connected. Total: {self.connections}")
```

### Problem 4: Read-Write Lock

```python
class ReadWriteLock:
    """Allow multiple readers OR one writer"""

    def __init__(self):
        self._readers = 0
        self._writers = 0
        self._read_ready = threading.Condition(threading.Lock())
        self._write_ready = threading.Condition(threading.Lock())

    def acquire_read(self):
        """Acquire read lock"""
        self._read_ready.acquire()
        while self._writers > 0:
            self._read_ready.wait()
        self._readers += 1
        self._read_ready.release()

    def release_read(self):
        """Release read lock"""
        self._read_ready.acquire()
        self._readers -= 1
        if self._readers == 0:
            self._write_ready.notify()
        self._read_ready.release()

    def acquire_write(self):
        """Acquire write lock"""
        self._write_ready.acquire()
        while self._writers > 0 or self._readers > 0:
            self._write_ready.wait()
        self._writers += 1
        self._write_ready.release()

    def release_write(self):
        """Release write lock"""
        self._write_ready.acquire()
        self._writers -= 1
        self._write_ready.notify()
        self._read_ready.notify_all()
        self._write_ready.release()

# Usage
class SharedResource:
    def __init__(self):
        self.data = {}
        self.lock = ReadWriteLock()

    def read(self, key):
        self.lock.acquire_read()
        try:
            return self.data.get(key)
        finally:
            self.lock.release_read()

    def write(self, key, value):
        self.lock.acquire_write()
        try:
            self.data[key] = value
        finally:
            self.lock.release_write()
```

### Problem 5: Rate Limiter

```python
import time
from collections import deque

class TokenBucketRateLimiter:
    """Thread-safe rate limiter using token bucket algorithm"""

    def __init__(self, rate, capacity):
        """
        rate: tokens per second
        capacity: maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = threading.Lock()

    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_update
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now

    def allow_request(self) -> bool:
        """Check if request is allowed"""
        with self._lock:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

class SlidingWindowRateLimiter:
    """Thread-safe sliding window rate limiter"""

    def __init__(self, max_requests, window_size_seconds):
        self.max_requests = max_requests
        self.window_size = window_size_seconds
        self.requests = deque()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        """Check if request is allowed"""
        with self._lock:
            now = time.time()

            # Remove old requests outside window
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()

            # Check if under limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True

            return False

# Usage
limiter = TokenBucketRateLimiter(rate=10, capacity=10)  # 10 req/sec

def make_request(request_id):
    if limiter.allow_request():
        print(f"Request {request_id}: Allowed")
    else:
        print(f"Request {request_id}: Rate limited")
```

### Problem 6: Thread Pool

```python
from queue import Queue
import threading

class ThreadPool:
    """Simple thread pool implementation"""

    def __init__(self, num_threads):
        self.tasks = Queue()
        self.threads = []
        self.is_shutdown = False

        # Create worker threads
        for _ in range(num_threads):
            t = threading.Thread(target=self._worker)
            t.start()
            self.threads.append(t)

    def _worker(self):
        """Worker thread that processes tasks"""
        while not self.is_shutdown:
            try:
                task, args, kwargs = self.tasks.get(timeout=1)
                try:
                    task(*args, **kwargs)
                except Exception as e:
                    print(f"Error in task: {e}")
                finally:
                    self.tasks.task_done()
            except:
                pass

    def submit(self, task, *args, **kwargs):
        """Submit a task to the pool"""
        if self.is_shutdown:
            raise RuntimeError("ThreadPool is shutdown")
        self.tasks.put((task, args, kwargs))

    def shutdown(self, wait=True):
        """Shutdown the thread pool"""
        self.is_shutdown = True
        if wait:
            for t in self.threads:
                t.join()

# Usage
def process_item(item_id):
    print(f"Processing item {item_id}")
    time.sleep(1)

pool = ThreadPool(num_threads=5)
for i in range(20):
    pool.submit(process_item, i)

pool.shutdown(wait=True)
```

## Interview Approach

### Step 1: Identify Shared State

```python
# Question: Make parking lot thread-safe

# Identify what's shared:
# - Available spots (read/write by multiple threads)
# - Active tickets (read/write by multiple threads)
# - Vehicle assignments (write by one thread, read by many)
```

### Step 2: Identify Critical Sections

```python
# Operations that modify shared state:
def park_vehicle(self, vehicle):
    # CRITICAL: Check + modify spot availability
    if spot.is_available:  # READ
        spot.is_available = False  # WRITE
        spot.vehicle = vehicle  # WRITE
```

### Step 3: Choose Synchronization Mechanism

```python
# Options:
# 1. Lock - Simple mutual exclusion
# 2. RLock - If same thread needs to re-acquire
# 3. Semaphore - Limit concurrent access
# 4. ReadWriteLock - Multiple readers, one writer
# 5. Atomic operations - For simple counters

# For parking lot:
class ParkingSpot:
    def __init__(self):
        self._lock = threading.Lock()  # Protect this spot

    def park_vehicle(self, vehicle):
        with self._lock:
            if not self.is_available:
                return False
            self.is_available = False
            self.vehicle = vehicle
            return True
```

### Step 4: Prevent Deadlocks

```python
# Rules to avoid deadlocks:
# 1. Lock ordering - Always acquire in same order
# 2. Lock timeout - Don't wait forever
# 3. No nested locks - Avoid if possible
# 4. Use higher-level constructs (Queue, etc.)
```

## Common Interview Questions

1. **Make X thread-safe**: Take existing LLD design, make it thread-safe
2. **Design rate limiter**: Handle concurrent requests
3. **Design connection pool**: Limit and reuse connections
4. **Design task executor**: Thread pool with scheduling
5. **Design cache**: Thread-safe LRU cache
6. **Producer-consumer**: Classic synchronization problem
7. **Reader-writer**: Allow multiple readers or one writer
8. **Dining philosophers**: Deadlock avoidance problem

## Red Flags to Avoid

### ❌ No synchronization
```python
# WRONG: Shared state without protection
class Counter:
    def __init__(self):
        self.count = 0  # Shared, no lock!

    def increment(self):
        self.count += 1  # RACE CONDITION!
```

### ❌ Too coarse-grained locking
```python
# WRONG: One lock for everything
class ParkingLot:
    def __init__(self):
        self.lock = threading.Lock()  # Global lock

    def park(self):
        with self.lock:  # Blocks ALL operations
            # Only need to lock specific spot
            pass
```

### ❌ Nested locks without ordering
```python
# WRONG: Can cause deadlock
def transfer(from_acc, to_acc):
    with from_acc.lock:  # Thread 1: A->B
        with to_acc.lock:  # Thread 2: B->A
            # DEADLOCK!
            pass
```

## Interview Tips

1. **Start simple**: Single-threaded first, then add concurrency
2. **Ask about concurrency**: "Should this be thread-safe?"
3. **Identify shared state**: What data is accessed by multiple threads?
4. **Choose right tool**: Lock, Semaphore, Queue, etc.
5. **Discuss trade-offs**: Performance vs simplicity
6. **Consider deadlocks**: How to prevent them?
7. **Test mentally**: Walk through scenarios with 2-3 threads

## Python-Specific Tools

```python
# Built-in thread-safe structures
from queue import Queue, LifoQueue, PriorityQueue
from threading import Lock, RLock, Semaphore, Event, Condition
from concurrent.futures import ThreadPoolExecutor

# Thread-safe collections
from collections import deque  # Thread-safe for append/pop
# Note: Regular dict is NOT thread-safe for all operations

# Atomic operations (with GIL)
# Simple operations like count += 1 are atomic in CPython
# But don't rely on this! Use locks for clarity
```

---

**Next**: Now that you understand interview types, let's dive into [OOP Fundamentals](../03-oop-fundamentals/)
