# Concurrency in Low-Level Design: From Basics to Advanced

Real-world examples showing why concurrency matters and how to handle it correctly.

---

## Table of Contents

1. [Why Concurrency Matters - The Bank Heist](#why-concurrency-matters---the-bank-heist)
2. [The Fundamentals - Building Intuition](#the-fundamentals---building-intuition)
3. [Basic: Single Resource Protection](#basic-single-resource-protection)
4. [Intermediate: Multiple Resources](#intermediate-multiple-resources)
5. [Advanced: Complex Coordination](#advanced-complex-coordination)
6. [Real-World Patterns](#real-world-patterns)
7. [Common Interview Problems](#common-interview-problems)
8. [Production Disasters](#production-disasters)

---

# Why Concurrency Matters - The Bank Heist

## The $60 Million Mistake

**Real Story**: In 2016, a cryptocurrency exchange had a race condition in their withdrawal system. Here's what happened:

### Without Concurrency Control

```python
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        # Check balance
        if self.balance >= amount:
            # DANGER: Another thread can run here!
            print(f"Approved withdrawal of ${amount}")
            time.sleep(0.001)  # Simulating network delay
            self.balance -= amount
            return True
        return False

# The Attack
account = BankAccount(1000)

# Hacker creates 10 threads, all trying to withdraw $1000 simultaneously
def attack():
    account.withdraw(1000)

threads = [threading.Thread(target=attack) for _ in range(10)]
for t in threads:
    t.start()

# Result: All 10 withdrawals approved!
# Balance: -9000 (should be 1000 or 0)
# Loss: $10,000 from $1,000 account
```

**What Went Wrong:**
1. Thread 1 checks balance (1000 >= 1000) ✅
2. Thread 2 checks balance (1000 >= 1000) ✅ **BEFORE Thread 1 subtracts**
3. Thread 3 checks balance (1000 >= 1000) ✅ **BEFORE Threads 1 & 2 subtract**
4. All 10 threads see balance = 1000 and approve!
5. All 10 threads subtract 1000, resulting in -9000

**Real Cost**: The exchange lost **$60 million** before they discovered the bug.

---

# The Fundamentals - Building Intuition

## What is Concurrency?

**Real-World Analogy**: Your kitchen.

### Sequential (No Concurrency)
```
You: Boil water → Wait 10 min → Make pasta → Wait 15 min → Make sauce
Total: 25 minutes
```

### Concurrent
```
You: Start boiling water | Start making sauce (while water boils) | Add pasta when ready
Total: 15 minutes

BUT: You need to coordinate!
- Don't add pasta before water boils (race condition)
- Don't grab the same spoon simultaneously (resource conflict)
- Don't start two burners if you only have one pot (resource limitation)
```

## Core Concurrency Problems

### Problem 1: Race Condition
**Real-World**: Two chefs trying to grab the last egg at the same time.

```python
# Counter example
counter = 0

def increment():
    global counter
    temp = counter      # Read
    temp = temp + 1     # Modify
    counter = temp      # Write

# What happens with 2 threads?
# Thread 1: Read (0) → Modify (1) → ...
# Thread 2: Read (0) → ... → Write (1)  ← Overwrites Thread 1's work!
# Thread 1: ... → Write (1)
# Expected: 2, Actual: 1
```

### Problem 2: Deadlock
**Real-World**: Two people in a narrow hallway, each waiting for the other to move.

```python
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    with lock_a:
        print("Thread 1 has lock A, waiting for lock B...")
        time.sleep(0.1)
        with lock_b:  # Waits forever
            print("Thread 1 has both locks")

def thread2():
    with lock_b:
        print("Thread 2 has lock B, waiting for lock A...")
        time.sleep(0.1)
        with lock_a:  # Waits forever
            print("Thread 2 has both locks")
```

### Problem 3: Starvation
**Real-World**: VIP customers always cutting in line, regular customers never get served.

```python
# Writer-preferred lock: Readers starve
class UnfairLock:
    def __init__(self):
        self.writer_waiting = False

    def read(self):
        while self.writer_waiting:  # Readers wait forever if writers keep coming
            time.sleep(0.001)
```

---

# Basic: Single Resource Protection

## Example 1: Counter (The Simplest Case)

### The Problem - Real World: Page View Counter

**Scenario**: Website tracking page views. Multiple users hitting the page simultaneously.

```python
# ❌ WRONG: Race condition
class PageViewCounter:
    def __init__(self):
        self.views = 0

    def increment(self):
        # This is NOT atomic!
        self.views = self.views + 1  # Read, Add, Write = 3 operations

    def get_views(self):
        return self.views

# Test with 1000 threads, each incrementing once
counter = PageViewCounter()
threads = [threading.Thread(target=counter.increment) for _ in range(1000)]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter.get_views())  # Expected: 1000, Actual: ~850-950 (varies!)
```

**Why It Fails:**
```
Thread 1: Read (0) → Add (1) → ...
Thread 2: Read (0) → Add (1) → ...  ← Both read 0!
Thread 1: ... → Write (1)
Thread 2: ... → Write (1)  ← Lost increment!
```

### Solution 1: Lock (Mutex)

```python
# ✅ CORRECT: Using Lock
import threading

class PageViewCounter:
    def __init__(self):
        self.views = 0
        self.lock = threading.Lock()  # Mutex (mutual exclusion)

    def increment(self):
        with self.lock:  # Only one thread at a time
            self.views = self.views + 1

    def get_views(self):
        with self.lock:
            return self.views

# Now it works!
counter = PageViewCounter()
threads = [threading.Thread(target=counter.increment) for _ in range(1000)]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter.get_views())  # Always 1000!
```

**Intuition**: Lock is like a bathroom door. Only one person inside at a time. Others wait outside.

### Solution 2: Atomic Operations (When Available)

```python
# ✅ BETTER: Using atomic operations (Python 3.9+)
from threading import Lock

class PageViewCounter:
    def __init__(self):
        self.views = 0
        self._lock = Lock()

    def increment(self):
        # In languages like Java/C++, use AtomicInteger
        # In Python, still need lock for integers
        with self._lock:
            self.views += 1

# In Java (for comparison):
# AtomicInteger views = new AtomicInteger(0);
# views.incrementAndGet();  // Thread-safe, no lock needed!
```

**Intuition**: Atomic operations are like a bank deposit machine. The entire operation happens as one indivisible action.

---

## Example 2: Bank Account (Slightly More Complex)

### The Problem - Real World: ATM Withdrawals

**Scenario**: Two ATMs processing withdrawals from the same account simultaneously.

```python
# ❌ WRONG: Race condition allows overdraft
import time
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        if self.balance >= amount:
            # Simulate network delay (checking with central bank, etc.)
            print(f"Checking balance... ${self.balance}")
            time.sleep(0.01)  # 10ms delay

            self.balance -= amount
            print(f"Withdrew ${amount}, new balance: ${self.balance}")
            return True
        else:
            print(f"Insufficient funds!")
            return False

# Scenario: $100 in account, two $60 withdrawals
account = BankAccount(100)

def atm_transaction(amount):
    account.withdraw(amount)

# Two ATMs try to withdraw $60 simultaneously
thread1 = threading.Thread(target=atm_transaction, args=(60,))
thread2 = threading.Thread(target=atm_transaction, args=(60,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print(f"Final balance: ${account.balance}")
# Expected: $40 (only one withdrawal should succeed)
# Actual: -$20 (both succeed! Overdraft!)
```

**What Happens:**
```
Time 0ms: Thread 1 checks balance ($100 >= $60) ✅
Time 1ms: Thread 2 checks balance ($100 >= $60) ✅  ← Still $100!
Time 10ms: Thread 1 withdraws → Balance = $40
Time 11ms: Thread 2 withdraws → Balance = -$20  ← Overdraft!
```

### Solution: Lock for Atomic Check-And-Withdraw

```python
# ✅ CORRECT: Using Lock
import time
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()

    def withdraw(self, amount):
        with self.lock:  # Entire check-and-withdraw is atomic
            if self.balance >= amount:
                print(f"[{threading.current_thread().name}] Checking balance... ${self.balance}")
                time.sleep(0.01)

                self.balance -= amount
                print(f"[{threading.current_thread().name}] Withdrew ${amount}, new balance: ${self.balance}")
                return True
            else:
                print(f"[{threading.current_thread().name}] Insufficient funds!")
                return False

# Now it works correctly
account = BankAccount(100)

def atm_transaction(amount):
    account.withdraw(amount)

thread1 = threading.Thread(target=atm_transaction, args=(60,), name="ATM-1")
thread2 = threading.Thread(target=atm_transaction, args=(60,), name="ATM-2")

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print(f"\nFinal balance: ${account.balance}")
# Correct: $40 (one succeeds, one fails)
```

**Output:**
```
[ATM-1] Checking balance... $100
[ATM-1] Withdrew $60, new balance: $40
[ATM-2] Insufficient funds!

Final balance: $40
```

**Intuition**: The lock ensures "check balance" and "withdraw money" happen together, like a single operation. No one can check balance while another thread is withdrawing.

---

## Example 3: Connection Pool (Resource Management)

### The Problem - Real World: Database Connection Pool

**Scenario**: Web server with 10 database connections, 1000 requests come in.

```python
# ❌ WRONG: No synchronization
class ConnectionPool:
    def __init__(self, size):
        self.connections = [f"Connection-{i}" for i in range(size)]
        self.available = list(self.connections)

    def acquire(self):
        if self.available:
            conn = self.available.pop()  # NOT thread-safe!
            return conn
        return None

    def release(self, conn):
        self.available.append(conn)  # NOT thread-safe!

# Test: 20 threads trying to get 10 connections
pool = ConnectionPool(10)
acquired = []

def worker():
    conn = pool.acquire()
    if conn:
        acquired.append(conn)
        time.sleep(0.01)
        pool.release(conn)

threads = [threading.Thread(target=worker) for _ in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Acquired {len(acquired)} connections")
print(f"Unique: {len(set(acquired))}")
# Problem: Same connection might be given to multiple threads!
```

### Solution: Thread-Safe Connection Pool

```python
# ✅ CORRECT: Thread-safe pool
import threading
import time

class ConnectionPool:
    def __init__(self, size):
        self.connections = [f"Connection-{i}" for i in range(size)]
        self.available = list(self.connections)
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def acquire(self, timeout=None):
        with self.condition:
            # Wait until a connection is available
            while not self.available:
                print(f"[{threading.current_thread().name}] Waiting for connection...")
                if not self.condition.wait(timeout):
                    return None  # Timeout

            conn = self.available.pop()
            print(f"[{threading.current_thread().name}] Acquired {conn}")
            return conn

    def release(self, conn):
        with self.condition:
            self.available.append(conn)
            print(f"[{threading.current_thread().name}] Released {conn}")
            self.condition.notify()  # Wake up one waiting thread

# Demo
pool = ConnectionPool(3)

def worker(worker_id):
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Starting...")

    conn = pool.acquire(timeout=2.0)
    if conn:
        time.sleep(0.5)  # Simulate work
        pool.release(conn)
    else:
        print(f"[{thread_name}] Timeout waiting for connection")

threads = [threading.Thread(target=worker, args=(i,), name=f"Worker-{i}")
           for i in range(10)]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("\n✅ All workers completed successfully")
```

**Output:**
```
[Worker-0] Starting...
[Worker-0] Acquired Connection-2
[Worker-1] Starting...
[Worker-1] Acquired Connection-1
[Worker-2] Starting...
[Worker-2] Acquired Connection-0
[Worker-3] Starting...
[Worker-3] Waiting for connection...
[Worker-4] Starting...
[Worker-4] Waiting for connection...
[Worker-0] Released Connection-2
[Worker-3] Acquired Connection-2
...
```

**Intuition**: This is like a car rental. Only 3 cars available. 10 people want cars. First 3 get them immediately. Others wait at the counter. When someone returns a car, the next person in line gets notified.

---

# Intermediate: Multiple Resources

## Example 4: Dining Philosophers (Classic Problem)

### The Problem - Real World: Restaurant with Shared Utensils

**Scenario**: 5 philosophers sitting around a table. One fork between each pair. Need 2 forks to eat.

```python
# ❌ WRONG: Causes deadlock
import threading
import time

class DiningPhilosophers:
    def __init__(self, num_philosophers=5):
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.num_philosophers = num_philosophers

    def philosopher(self, philosopher_id):
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.num_philosophers

        while True:
            # Think
            print(f"Philosopher {philosopher_id} is thinking...")
            time.sleep(0.1)

            # Try to eat
            print(f"Philosopher {philosopher_id} is hungry")

            # Grab left fork
            self.forks[left_fork].acquire()
            print(f"Philosopher {philosopher_id} picked up left fork {left_fork}")

            # Grab right fork
            self.forks[right_fork].acquire()
            print(f"Philosopher {philosopher_id} picked up right fork {right_fork}")

            # Eat
            print(f"Philosopher {philosopher_id} is eating...")
            time.sleep(0.1)

            # Put down forks
            self.forks[left_fork].release()
            self.forks[right_fork].release()

            break  # Exit after one meal

# Deadlock scenario
dining = DiningPhilosophers(5)
threads = [threading.Thread(target=dining.philosopher, args=(i,))
           for i in range(5)]

for t in threads:
    t.start()

# DEADLOCK! All philosophers grab left fork, all wait for right fork forever
```

**What Goes Wrong:**
```
Philosopher 0: Grabs fork 0, waits for fork 1
Philosopher 1: Grabs fork 1, waits for fork 2
Philosopher 2: Grabs fork 2, waits for fork 3
Philosopher 3: Grabs fork 3, waits for fork 4
Philosopher 4: Grabs fork 4, waits for fork 0
→ DEADLOCK! Everyone waiting in a cycle
```

### Solution 1: Ordered Resource Acquisition

```python
# ✅ CORRECT: Always acquire locks in same order
import threading
import time

class DiningPhilosophers:
    def __init__(self, num_philosophers=5):
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.num_philosophers = num_philosophers

    def philosopher(self, philosopher_id):
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.num_philosophers

        # KEY: Always acquire lower-numbered fork first
        first_fork = min(left_fork, right_fork)
        second_fork = max(left_fork, right_fork)

        for meal in range(3):
            # Think
            print(f"🤔 Philosopher {philosopher_id} is thinking...")
            time.sleep(0.1)

            # Try to eat
            print(f"😋 Philosopher {philosopher_id} is hungry")

            # Acquire in order
            self.forks[first_fork].acquire()
            print(f"  Philosopher {philosopher_id} picked up fork {first_fork}")

            self.forks[second_fork].acquire()
            print(f"  Philosopher {philosopher_id} picked up fork {second_fork}")

            # Eat
            print(f"🍝 Philosopher {philosopher_id} is eating (meal {meal + 1})...")
            time.sleep(0.1)

            # Release in reverse order
            self.forks[second_fork].release()
            self.forks[first_fork].release()
            print(f"✅ Philosopher {philosopher_id} finished eating")

# Works perfectly!
dining = DiningPhilosophers(5)
threads = [threading.Thread(target=dining.philosopher, args=(i,), name=f"Phil-{i}")
           for i in range(5)]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("\n🎉 All philosophers ate without deadlock!")
```

**Why It Works:**
- Philosopher 4 tries to grab fork 4 first, then fork 0
- But now needs to grab fork 0 first (lower number), then fork 4
- If philosopher 0 already has fork 0, philosopher 4 waits
- No circular dependency!

**Intuition**: It's like a rule that you always pick up the lighter object first, then the heavier one. This prevents the circular waiting.

---

## Example 5: Producer-Consumer (Queue)

### The Problem - Real World: Print Queue

**Scenario**: Multiple people sending documents to printer (producers). One printer processing them (consumer).

```python
# ❌ WRONG: Race conditions on queue
import threading
import time
from collections import deque

class PrintQueue:
    def __init__(self):
        self.queue = deque()

    def submit(self, document):
        self.queue.append(document)  # NOT thread-safe!
        print(f"Submitted: {document}")

    def process(self):
        if self.queue:
            doc = self.queue.popleft()  # NOT thread-safe!
            print(f"Printing: {doc}")
            time.sleep(0.1)
            return doc
        return None

# Problem: Multiple producers and consumer access queue simultaneously
queue = PrintQueue()

def producer(producer_id):
    for i in range(3):
        queue.submit(f"Doc-{producer_id}-{i}")
        time.sleep(0.05)

def consumer():
    for _ in range(15):  # Process 15 documents
        doc = queue.process()
        if not doc:
            time.sleep(0.05)

# Race conditions will occur!
producers = [threading.Thread(target=producer, args=(i,)) for i in range(5)]
consumer_thread = threading.Thread(target=consumer)

for p in producers:
    p.start()
consumer_thread.start()

for p in producers:
    p.join()
consumer_thread.join()
```

### Solution: Thread-Safe Queue with Condition Variable

```python
# ✅ CORRECT: Using queue with synchronization
import threading
import time
from collections import deque

class PrintQueue:
    def __init__(self, max_size=10):
        self.queue = deque()
        self.max_size = max_size
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)

    def submit(self, document):
        with self.not_full:
            # Wait if queue is full
            while len(self.queue) >= self.max_size:
                print(f"⚠️ Queue full! {threading.current_thread().name} waiting...")
                self.not_full.wait()

            self.queue.append(document)
            print(f"📄 [{threading.current_thread().name}] Submitted: {document}")

            # Notify consumer that queue is not empty
            self.not_empty.notify()

    def process(self):
        with self.not_empty:
            # Wait if queue is empty
            while not self.queue:
                print(f"⏳ Queue empty, printer waiting...")
                self.not_empty.wait()

            doc = self.queue.popleft()
            print(f"🖨️ Printing: {doc}")
            time.sleep(0.1)  # Simulate printing

            # Notify producers that queue is not full
            self.not_full.notify()
            return doc

# Demo
queue = PrintQueue(max_size=5)

def producer(producer_id):
    for i in range(5):
        queue.submit(f"Doc-{producer_id}-{i}")
        time.sleep(0.05)

def consumer():
    for _ in range(15):  # Process 15 total documents
        queue.process()

# Start multiple producers and one consumer
producers = [threading.Thread(target=producer, args=(i,), name=f"User-{i}")
            for i in range(3)]
consumer_thread = threading.Thread(target=consumer, name="Printer")

consumer_thread.start()
for p in producers:
    p.start()

for p in producers:
    p.join()
consumer_thread.join()

print("\n✅ All documents printed successfully!")
```

**Output:**
```
📄 [User-0] Submitted: Doc-0-0
📄 [User-1] Submitted: Doc-1-0
📄 [User-2] Submitted: Doc-2-0
🖨️ Printing: Doc-0-0
📄 [User-0] Submitted: Doc-0-1
...
⚠️ Queue full! User-1 waiting...
🖨️ Printing: Doc-2-3
📄 [User-1] Submitted: Doc-1-4
...
✅ All documents printed successfully!
```

**Intuition**:
- **Queue full** = Parking lot full. Cars (producers) wait at entrance until spot opens.
- **Queue empty** = Restaurant with no customers. Waiter (consumer) waits until customers arrive.
- **Condition variables** = Notification system. "Spot available!" or "Customer arrived!"

---

# Advanced: Complex Coordination

## Example 6: Read-Write Lock (Readers-Writers Problem)

### The Problem - Real World: Shared Cache

**Scenario**: Website cache. Many threads reading, few threads writing. Reading is safe in parallel, writing needs exclusive access.

```python
# ❌ WRONG: Using simple lock (inefficient)
import threading
import time

class Cache:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()  # One lock for everything

    def get(self, key):
        with self.lock:  # Readers block each other unnecessarily!
            time.sleep(0.01)  # Simulate read time
            return self.data.get(key)

    def set(self, key, value):
        with self.lock:
            time.sleep(0.01)  # Simulate write time
            self.data[key] = value

# Problem: 100 readers can't read simultaneously even though reads are safe!
cache = Cache()
cache.set("config", "value1")

def reader(reader_id):
    for _ in range(10):
        value = cache.get("config")

def writer():
    for i in range(10):
        cache.set("config", f"value{i}")
        time.sleep(0.1)

start = time.time()
readers = [threading.Thread(target=reader, args=(i,)) for i in range(50)]
writer_thread = threading.Thread(target=writer)

for r in readers:
    r.start()
writer_thread.start()

for r in readers:
    r.join()
writer_thread.join()

print(f"Time with simple lock: {time.time() - start:.2f}s")
# Slow! ~50 readers × 10 reads × 0.01s = ~5 seconds
```

### Solution: Read-Write Lock

```python
# ✅ CORRECT: Using Read-Write Lock
import threading
import time

class ReadWriteLock:
    def __init__(self):
        self.readers = 0
        self.writers = 0
        self.write_ready = threading.Condition(threading.Lock())

    def acquire_read(self):
        with self.write_ready:
            # Wait while any writer is active
            while self.writers > 0:
                self.write_ready.wait()
            self.readers += 1

    def release_read(self):
        with self.write_ready:
            self.readers -= 1
            # If last reader, notify writers
            if self.readers == 0:
                self.write_ready.notify_all()

    def acquire_write(self):
        with self.write_ready:
            # Wait while any readers or writers are active
            while self.readers > 0 or self.writers > 0:
                self.write_ready.wait()
            self.writers += 1

    def release_write(self):
        with self.write_ready:
            self.writers -= 1
            # Notify all waiting readers and writers
            self.write_ready.notify_all()

class Cache:
    def __init__(self):
        self.data = {}
        self.rw_lock = ReadWriteLock()

    def get(self, key):
        self.rw_lock.acquire_read()
        try:
            time.sleep(0.01)  # Simulate read time
            return self.data.get(key)
        finally:
            self.rw_lock.release_read()

    def set(self, key, value):
        self.rw_lock.acquire_write()
        try:
            time.sleep(0.01)  # Simulate write time
            self.data[key] = value
        finally:
            self.rw_lock.release_write()

# Now readers can read in parallel!
cache = Cache()
cache.set("config", "value1")

def reader(reader_id):
    for _ in range(10):
        value = cache.get("config")

def writer():
    for i in range(10):
        cache.set("config", f"value{i}")
        time.sleep(0.1)

start = time.time()
readers = [threading.Thread(target=reader, args=(i,)) for i in range(50)]
writer_thread = threading.Thread(target=writer)

for r in readers:
    r.start()
writer_thread.start()

for r in readers:
    r.join()
writer_thread.join()

print(f"Time with RW lock: {time.time() - start:.2f}s")
# Fast! Readers read in parallel, only ~1 second
```

**Performance:**
- **Simple lock**: 5+ seconds (readers block each other)
- **Read-Write lock**: ~1 second (readers in parallel)

**Intuition**:
- **Reading** = Looking at a whiteboard. Multiple people can look simultaneously.
- **Writing** = Erasing and rewriting the whiteboard. Need the room to yourself.

---

## Example 7: Double-Checked Locking (Singleton Pattern)

### The Problem - Real World: Database Connection Singleton

**Scenario**: Expensive database connection. Want only one instance. Need thread-safe lazy initialization.

```python
# ❌ WRONG: Race condition in singleton creation
import threading
import time

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Expensive initialization
            print(f"[{threading.current_thread().name}] Creating database instance...")
            time.sleep(0.1)  # Simulate expensive operation
            cls._instance = super().__new__(cls)
        return cls._instance

# Race condition!
def get_database():
    return Database()

threads = [threading.Thread(target=get_database, name=f"Thread-{i}")
           for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Output: Multiple threads create instance!
# Creating database instance...
# Creating database instance...
# Creating database instance...
```

### Solution 1: Simple Lock (Inefficient)

```python
# ✅ WORKS but SLOW: Lock every time
import threading
import time

class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:  # Acquire lock EVERY time
            if cls._instance is None:
                print(f"[{threading.current_thread().name}] Creating instance...")
                time.sleep(0.1)
                cls._instance = super().__new__(cls)
        return cls._instance

# Works but lock contention slows down all getInstance() calls
```

### Solution 2: Double-Checked Locking (Efficient)

```python
# ✅ CORRECT and FAST: Double-checked locking
import threading
import time

class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # First check (no lock)
        if cls._instance is None:
            # Only acquire lock if instance doesn't exist
            with cls._lock:
                # Second check (with lock)
                if cls._instance is None:
                    print(f"[{threading.current_thread().name}] Creating instance...")
                    time.sleep(0.1)  # Expensive operation
                    cls._instance = super().__new__(cls)

        return cls._instance

# Test
def get_database():
    db = Database()
    print(f"[{threading.current_thread().name}] Got database instance: {id(db)}")

threads = [threading.Thread(target=get_database, name=f"Thread-{i}")
           for i in range(10)]

start = time.time()
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"Time: {time.time() - start:.2f}s")

# Output: Only ONE instance created, all threads get same instance
# [Thread-0] Creating instance...
# [Thread-0] Got database instance: 140123456789
# [Thread-1] Got database instance: 140123456789
# ...all threads get same ID...
```

**Why Double-Check?**
1. **First check (no lock)**: Fast path for when instance exists (99.9% of calls after initialization)
2. **Lock**: Only acquired once during initialization
3. **Second check (with lock)**: Prevents race where two threads both see None and try to create

**Intuition**: Like checking if a store is open:
1. Look through window (fast, no lock)
2. If lights are off, try the door (acquire lock)
3. Check again from inside (second check) - maybe someone just opened while you were walking to door

---

## Example 8: Semaphore (Limited Resources)

### The Problem - Real World: Parking Lot with Limited Spots

**Scenario**: Parking lot with 5 spots. 20 cars trying to park.

```python
# ✅ Using Semaphore
import threading
import time
import random

class ParkingLot:
    def __init__(self, capacity):
        self.semaphore = threading.Semaphore(capacity)
        self.capacity = capacity
        self.parked_cars = []
        self.lock = threading.Lock()

    def park(self, car_id):
        print(f"🚗 {car_id} looking for parking...")

        # Try to acquire a spot
        self.semaphore.acquire()

        with self.lock:
            self.parked_cars.append(car_id)
            print(f"✅ {car_id} parked! ({len(self.parked_cars)}/{self.capacity} spots occupied)")

        # Park for random duration
        duration = random.uniform(1, 3)
        time.sleep(duration)

        # Leave
        with self.lock:
            self.parked_cars.remove(car_id)
            print(f"🚙 {car_id} leaving... ({len(self.parked_cars)}/{self.capacity} spots occupied)")

        self.semaphore.release()

# Demo
parking_lot = ParkingLot(capacity=5)

def car(car_id):
    parking_lot.park(car_id)

# 20 cars trying to use 5 spots
threads = [threading.Thread(target=car, args=(f"Car-{i}",)) for i in range(20)]

for t in threads:
    t.start()

for t in threads:
    t.join()

print("\n🏁 All cars have parked and left!")
```

**Output:**
```
🚗 Car-0 looking for parking...
🚗 Car-1 looking for parking...
...
✅ Car-0 parked! (1/5 spots occupied)
✅ Car-1 parked! (2/5 spots occupied)
✅ Car-2 parked! (3/5 spots occupied)
✅ Car-3 parked! (4/5 spots occupied)
✅ Car-4 parked! (5/5 spots occupied)
🚗 Car-5 looking for parking...  ← Waits!
🚙 Car-0 leaving... (4/5 spots occupied)
✅ Car-5 parked! (5/5 spots occupied)  ← Now can park
...
```

**Intuition**: Semaphore is like tokens/tickets. 5 spots = 5 tokens. To park, you need a token. When you leave, you return the token for others to use.

**Lock vs Semaphore:**
- **Lock**: Binary (0 or 1). Either available or taken.
- **Semaphore**: Counter (0 to N). Multiple resources available.

---

# Real-World Patterns

## Pattern 1: Rate Limiter (Token Bucket)

**Real Companies**: Twitter, GitHub, Stripe

```python
import threading
import time

class TokenBucketRateLimiter:
    def __init__(self, capacity, refill_rate):
        """
        capacity: Maximum tokens
        refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        """Add tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def allow_request(self, tokens=1):
        """Try to consume tokens for a request"""
        with self.lock:  # Thread-safe
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

# Demo: 5 requests per second
rate_limiter = TokenBucketRateLimiter(capacity=5, refill_rate=5)

def make_request(request_id):
    if rate_limiter.allow_request():
        print(f"✅ Request {request_id} allowed")
    else:
        print(f"❌ Request {request_id} rate limited")

# Burst of 10 requests
threads = [threading.Thread(target=make_request, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("\nWaiting 1 second for refill...")
time.sleep(1)

# Try again
print("\nAfter 1 second:")
threads = [threading.Thread(target=make_request, args=(i,)) for i in range(10, 20)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**Output:**
```
✅ Request 0 allowed
✅ Request 1 allowed
✅ Request 2 allowed
✅ Request 3 allowed
✅ Request 4 allowed
❌ Request 5 rate limited
❌ Request 6 rate limited
❌ Request 7 rate limited
❌ Request 8 rate limited
❌ Request 9 rate limited

Waiting 1 second for refill...

After 1 second:
✅ Request 10 allowed
✅ Request 11 allowed
✅ Request 12 allowed
✅ Request 13 allowed
✅ Request 14 allowed
❌ Request 15 rate limited
...
```

---

## Pattern 2: LRU Cache (Concurrent)

**Real Companies**: Redis, Memcached, CDNs

```python
import threading
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.move_to_end(key)
            else:
                # Add new
                if len(self.cache) >= self.capacity:
                    # Evict least recently used (first item)
                    self.cache.popitem(last=False)

            self.cache[key] = value

    def __str__(self):
        with self.lock:
            return f"LRU: {list(self.cache.keys())}"

# Demo
cache = LRUCache(capacity=3)

def worker(worker_id, key, value):
    cache.put(key, value)
    print(f"[Worker-{worker_id}] Put {key}={value}, {cache}")

    retrieved = cache.get(key)
    print(f"[Worker-{worker_id}] Got {key}={retrieved}, {cache}")

# Multiple threads accessing cache
threads = [
    threading.Thread(target=worker, args=(0, "a", 1)),
    threading.Thread(target=worker, args=(1, "b", 2)),
    threading.Thread(target=worker, args=(2, "c", 3)),
    threading.Thread(target=worker, args=(3, "d", 4)),  # This evicts 'a'
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"\nFinal cache: {cache}")
```

---

## Pattern 3: Thread Pool (Job Scheduler)

**Real Companies**: Web servers, Task queues (Celery, RabbitMQ)

```python
import threading
import queue
import time

class ThreadPool:
    def __init__(self, num_workers):
        self.task_queue = queue.Queue()
        self.workers = []

        # Start worker threads
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self, worker_id):
        """Worker thread that processes tasks"""
        while True:
            try:
                # Get task from queue (blocks if empty)
                task, args = self.task_queue.get(timeout=1)

                print(f"[Worker-{worker_id}] Processing {task.__name__}{args}")
                task(*args)

                self.task_queue.task_done()
            except queue.Empty:
                continue

    def submit(self, task, *args):
        """Submit a task to the pool"""
        self.task_queue.put((task, args))

    def wait_completion(self):
        """Wait for all tasks to complete"""
        self.task_queue.join()

# Demo
def process_order(order_id):
    print(f"  Processing order {order_id}...")
    time.sleep(0.5)  # Simulate work
    print(f"  ✅ Order {order_id} completed")

# Create pool with 3 workers
pool = ThreadPool(num_workers=3)

# Submit 10 tasks
print("Submitting 10 orders...")
for i in range(10):
    pool.submit(process_order, i)

# Wait for completion
pool.wait_completion()
print("\n✅ All orders processed!")
```

**Output:**
```
Submitting 10 orders...
[Worker-0] Processing process_order(0,)
[Worker-1] Processing process_order(1,)
[Worker-2] Processing process_order(2,)
  Processing order 0...
  Processing order 1...
  Processing order 2...
  ✅ Order 0 completed
[Worker-0] Processing process_order(3,)
  Processing order 3...
  ✅ Order 1 completed
[Worker-1] Processing process_order(4,)
...
✅ All orders processed!
```

---

# Common Interview Problems

## Problem 1: Hotel Booking System (Thread-Safe)

**Companies**: Airbnb, Booking.com, Expedia

**Challenge**: Prevent double-booking of rooms.

```python
import threading
from datetime import date, timedelta

class Hotel:
    def __init__(self):
        self.rooms = {f"Room-{i}": [] for i in range(5)}  # room_id -> list of bookings
        self.lock = threading.Lock()

    def check_available(self, room_id, check_in, check_out):
        """Check if room is available for dates"""
        for booking_start, booking_end in self.rooms[room_id]:
            # Check if dates overlap
            if check_in < booking_end and booking_start < check_out:
                return False
        return True

    def book_room(self, room_id, guest, check_in, check_out):
        """Book a room (thread-safe)"""
        with self.lock:  # Atomic check-and-book
            if self.check_available(room_id, check_in, check_out):
                self.rooms[room_id].append((check_in, check_out))
                print(f"✅ {guest} booked {room_id} from {check_in} to {check_out}")
                return True
            else:
                print(f"❌ {guest} couldn't book {room_id} (already booked)")
                return False

# Test concurrent bookings
hotel = Hotel()

def try_book(guest, room_id, check_in, check_out):
    hotel.book_room(room_id, guest, check_in, check_out)

# Two guests trying to book same room for overlapping dates
today = date.today()
threads = [
    threading.Thread(target=try_book, args=("Alice", "Room-1", today, today + timedelta(3))),
    threading.Thread(target=try_book, args=("Bob", "Room-1", today + timedelta(2), today + timedelta(5))),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

# Output: Only one books, other is rejected (no double-booking!)
```

---

## Problem 2: Web Crawler (Parallel with URL Dedup)

**Companies**: Google, Bing, DuckDuckGo

**Challenge**: Crawl web pages in parallel, avoid crawling same URL twice.

```python
import threading
import queue
import time

class WebCrawler:
    def __init__(self, num_workers=5):
        self.to_crawl = queue.Queue()
        self.crawled = set()
        self.lock = threading.Lock()
        self.workers = []

        # Start workers
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self, worker_id):
        while True:
            try:
                url = self.to_crawl.get(timeout=1)
                self._crawl_page(worker_id, url)
                self.to_crawl.task_done()
            except queue.Empty:
                break

    def _crawl_page(self, worker_id, url):
        """Crawl a single page"""
        print(f"[Worker-{worker_id}] Crawling {url}")
        time.sleep(0.1)  # Simulate HTTP request

        # Extract links (simulated)
        links = [f"{url}/page{i}" for i in range(2)]

        for link in links:
            with self.lock:
                if link not in self.crawled:
                    self.crawled.add(link)
                    self.to_crawl.put(link)

    def crawl(self, start_url):
        """Start crawling from a URL"""
        with self.lock:
            self.crawled.add(start_url)
        self.to_crawl.put(start_url)

        # Wait for completion
        self.to_crawl.join()

        print(f"\n✅ Crawled {len(self.crawled)} unique URLs")

# Demo
crawler = WebCrawler(num_workers=3)
crawler.crawl("https://example.com")
```

---

# Production Disasters

## Disaster 1: Therac-25 (1985-1987)

**What**: Medical radiation machine
**Bug**: Race condition in safety checks
**Result**: **6 patients killed, 21 injured**

**Code (Simplified)**:
```python
# ❌ DEADLY: Race condition
class RadiationMachine:
    def __init__(self):
        self.power_level = 0
        self.safety_checked = False

    def set_power(self, level):
        self.power_level = level

    def safety_check(self):
        if self.power_level < MAX_SAFE:
            self.safety_checked = True

    def fire_beam(self):
        if self.safety_checked:  # Race condition!
            # Another thread could change power_level here!
            fire_radiation(self.power_level)

# What happened:
# Thread 1: safety_check() → power=10 → safe ✅
# Thread 2: set_power(1000)  ← BEFORE fire_beam()!
# Thread 1: fire_beam() → fires at 1000! ☠️
```

**Lesson**: Concurrency bugs can **kill**.

---

## Disaster 2: Knight Capital (2012)

**What**: Stock trading firm
**Bug**: Race condition in trading algorithm
**Result**: **$440 million lost in 45 minutes**

**What Happened:**
- Multiple threads executing trades
- Shared counter for order tracking
- Race condition caused same order ID to be used multiple times
- Bought and sold same stock repeatedly at loss

**Lesson**: In high-frequency systems, even tiny race conditions = massive losses.

---

## Disaster 3: Cloudflare Outage (2020)

**What**: CDN serving 10% of web traffic
**Bug**: Deadlock in certificate renewal
**Result**: **27% of requests failed for 27 minutes**

**What Happened:**
- Thread 1: Acquired lock A, waiting for lock B
- Thread 2: Acquired lock B, waiting for lock A
- Deadlock!
- Certificate couldn't renew
- HTTPS connections failed

**Lesson**: Always acquire locks in same order.

---

# Interview Checklist

## Questions to Ask Yourself

For any concurrent system design:

**1. What shared resources exist?**
- Variables, files, network connections, database rows

**2. Which operations need to be atomic?**
- Check-and-update (bank withdrawal, booking)
- Read-modify-write (counter increment)

**3. What are the critical sections?**
- Code that accesses shared resources

**4. Can deadlock occur?**
- Multiple locks acquired in different orders

**5. Can race conditions occur?**
- Time-of-check to time-of-use (TOCTOU) bugs

**6. What's the worst case if synchronization fails?**
- Money lost, data corrupted, security breach

## Common Interview Red Flags

**❌ Red Flags:**
- "This doesn't need synchronization" (without analysis)
- "Race conditions are rare, we'll be fine"
- Acquiring locks in inconsistent order
- Long critical sections (holding locks too long)
- Not handling lock acquisition failures

**✅ Green Flags:**
- Identifies all shared resources upfront
- Chooses appropriate synchronization (lock vs semaphore vs atomic)
- Discusses trade-offs (correctness vs performance)
- Mentions testing strategies for concurrency
- Knows when NOT to use locks (embarrassingly parallel problems)

---

# Key Takeaways

## The Hierarchy of Concurrency

**Level 1: Avoid Shared State**
- Best solution: No shared state = no synchronization needed
- Use message passing, immutable data

**Level 2: Atomic Operations**
- Use atomic primitives when available (AtomicInteger, etc.)
- Faster than locks

**Level 3: Locks/Mutexes**
- Protect critical sections
- Keep critical sections small

**Level 4: Advanced Patterns**
- Read-Write locks, semaphores, condition variables
- For specific use cases

**Level 5: Lock-Free Data Structures**
- Complex but highest performance
- Use established libraries (don't write your own!)

## The Golden Rules

1. **Minimize Shared State**: Less sharing = fewer bugs
2. **Make Critical Sections Small**: Don't hold locks longer than needed
3. **Acquire Locks in Order**: Prevents deadlocks
4. **Test with Race Detectors**: Tools like ThreadSanitizer, Helgrind
5. **Prefer Higher-Level Abstractions**: Use `queue.Queue`, thread pools, etc. over raw locks

---

## Next Steps

**For Practice:**
1. Implement these examples from scratch
2. Break them (remove locks, create race conditions)
3. Fix them again

**For Interviews:**
1. Always ask: "Do we need to handle concurrent access?"
2. Identify shared resources immediately
3. Discuss synchronization strategy before coding

**For Production:**
1. Use proven libraries (don't roll your own locks)
2. Write concurrency tests
3. Use race detectors in CI/CD
4. Document thread-safety guarantees

---

**Remember**: Concurrency bugs are:
- Hard to reproduce
- Hard to debug
- Easy to cause catastrophic failures

**When in doubt**: Be conservative. Add synchronization. Test thoroughly.

The cost of a bug is far greater than the cost of a lock. 🔒
