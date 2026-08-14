"""
Python threading.Condition() - Simple to Advanced Examples
===========================================================

What is Condition?
------------------
A Condition is a Lock + a way for threads to WAIT for something to happen.

Think of it like a waiting room:
- Lock: Only one person can talk to the doctor at a time
- wait(): "I'll sit in the waiting room until called"
- notify(): "Next patient, please!"

Why not just use Lock?
----------------------
Lock:      "I'll keep checking if data is ready" (busy waiting - wastes CPU)
Condition: "Wake me up when data is ready" (efficient waiting)

Real-world analogy:
- Bad (Lock only): Constantly checking your mailbox every second
- Good (Condition): Mail carrier rings doorbell when package arrives
"""

import threading
import time
import random
from queue import Queue
from typing import List, Optional

print("=" * 80)
print("          PYTHON CONDITION - SIMPLE TO ADVANCED")
print("=" * 80)

# ============================================================================
# Example 1: SIMPLE - Print Queue (Single Item)
# ============================================================================
print("\n" + "=" * 80)
print("1. SIMPLE: Print Queue - One Job at a Time")
print("=" * 80)
print("""
Scenario: A printer that waits for print jobs
- Printer thread waits for jobs
- User threads submit jobs
- Printer wakes up when job arrives
""")

class SimplePrintQueue:
    def __init__(self):
        self.job = None
        self.condition = threading.Condition()

    def submit_job(self, job_name):
        with self.condition:
            while self.job is not None:
                # Wait if printer is busy
                self.condition.wait()

            self.job = job_name
            print(f"  📄 Job submitted: {job_name}")
            self.condition.notify()  # Wake up printer

    def print_job(self):
        with self.condition:
            while self.job is None:
                # Wait for a job
                print("  🖨️  Printer waiting for jobs...")
                self.condition.wait()

            job = self.job
            self.job = None
            print(f"  ✅ Printing: {job}")
            time.sleep(0.5)  # Simulate printing
            self.condition.notify()  # Wake up waiting submitters

printer = SimplePrintQueue()

def printer_thread():
    for _ in range(3):
        printer.print_job()

def user_thread(user_id):
    time.sleep(random.uniform(0.1, 0.3))
    printer.submit_job(f"Document_{user_id}")

print("\nStarting:")
threading.Thread(target=printer_thread, daemon=True).start()
time.sleep(0.1)  # Let printer start waiting

users = [threading.Thread(target=user_thread, args=(i,)) for i in range(3)]
for t in users:
    t.start()
for t in users:
    t.join()

time.sleep(1)
print("\n✅ Simple example complete!\n")

# ============================================================================
# Example 2: INTERMEDIATE - Producer-Consumer (Buffer)
# ============================================================================
print("=" * 80)
print("2. INTERMEDIATE: Producer-Consumer with Buffer")
print("=" * 80)
print("""
Scenario: Restaurant kitchen
- Chefs (producers) cook dishes
- Waiters (consumers) serve dishes
- Limited counter space (buffer)
- Use wait() when buffer is full/empty
""")

class RestaurantKitchen:
    def __init__(self, max_dishes=3):
        self.dishes = []
        self.max_dishes = max_dishes
        self.condition = threading.Condition()
        self.order_number = 0

    def cook_dish(self, chef_name):
        with self.condition:
            # Wait while counter is full
            while len(self.dishes) >= self.max_dishes:
                print(f"  👨‍🍳 {chef_name}: Counter full, waiting...")
                self.condition.wait()

            self.order_number += 1
            dish = f"Order#{self.order_number}"
            self.dishes.append(dish)
            print(f"  🍳 {chef_name} cooked {dish} (Counter: {len(self.dishes)}/{self.max_dishes})")

            # Wake up waiters
            self.condition.notify()

    def serve_dish(self, waiter_name):
        with self.condition:
            # Wait while no dishes available
            while len(self.dishes) == 0:
                print(f"  🙋 {waiter_name}: No dishes, waiting...")
                self.condition.wait()

            dish = self.dishes.pop(0)
            print(f"  ✅ {waiter_name} served {dish} (Counter: {len(self.dishes)}/{self.max_dishes})")

            # Wake up chefs
            self.condition.notify()

kitchen = RestaurantKitchen(max_dishes=3)

def chef(name, num_dishes):
    for _ in range(num_dishes):
        time.sleep(random.uniform(0.1, 0.3))
        kitchen.cook_dish(name)

def waiter(name, num_serves):
    for _ in range(num_serves):
        time.sleep(random.uniform(0.2, 0.4))
        kitchen.serve_dish(name)

print("\nStarting restaurant:")
threads = [
    threading.Thread(target=chef, args=("Chef-A", 4)),
    threading.Thread(target=chef, args=("Chef-B", 4)),
    threading.Thread(target=waiter, args=("Waiter-1", 4)),
    threading.Thread(target=waiter, args=("Waiter-2", 4)),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("\n✅ Restaurant closed!\n")

# ============================================================================
# Example 3: ADVANCED - Request-Response Pattern
# ============================================================================
print("=" * 80)
print("3. ADVANCED: Request-Response Pattern (Like HTTP)")
print("=" * 80)
print("""
Scenario: HTTP Connection Pool
- Multiple clients make requests
- Limited number of worker threads
- Each request waits for its specific response
- Uses notify_all() to wake all waiters
""")

class RequestResponse:
    def __init__(self):
        self.request_id = 0
        self.pending_requests = {}  # {request_id: request_data}
        self.responses = {}         # {request_id: response_data}
        self.condition = threading.Condition()

    def make_request(self, client_name, data):
        with self.condition:
            # Create request
            self.request_id += 1
            req_id = self.request_id
            self.pending_requests[req_id] = data
            print(f"  📤 {client_name}: Sent request #{req_id}: {data}")

            # Notify workers
            self.condition.notify()

            # Wait for response
            while req_id not in self.responses:
                print(f"  ⏳ {client_name}: Waiting for response #{req_id}...")
                self.condition.wait()

            response = self.responses.pop(req_id)
            print(f"  📥 {client_name}: Got response #{req_id}: {response}")
            return response

    def process_request(self, worker_name):
        with self.condition:
            # Wait for a request
            while not self.pending_requests:
                self.condition.wait()

            # Get a request
            req_id = list(self.pending_requests.keys())[0]
            data = self.pending_requests.pop(req_id)

            print(f"  🔧 {worker_name}: Processing request #{req_id}")

        # Process outside lock (simulate work)
        time.sleep(0.3)
        response = f"Result of {data}"

        with self.condition:
            # Store response
            self.responses[req_id] = response
            print(f"  ✅ {worker_name}: Completed request #{req_id}")

            # Wake ALL waiting clients (they check their req_id)
            self.condition.notify_all()

rr = RequestResponse()

def client(name, requests):
    for i, req in enumerate(requests):
        time.sleep(random.uniform(0.1, 0.2))
        rr.make_request(name, req)

def worker(name, num_tasks):
    for _ in range(num_tasks):
        rr.process_request(name)

print("\nStarting request-response system:")
threads = [
    threading.Thread(target=worker, args=("Worker-1", 3)),
    threading.Thread(target=worker, args=("Worker-2", 3)),
    threading.Thread(target=client, args=("Client-A", ["Query-1", "Query-2"])),
    threading.Thread(target=client, args=("Client-B", ["Query-3", "Query-4"])),
    threading.Thread(target=client, args=("Client-C", ["Query-5", "Query-6"])),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("\n✅ All requests processed!\n")

# ============================================================================
# Example 4: PRODUCTION - Database Connection Pool
# ============================================================================
print("=" * 80)
print("4. PRODUCTION: Database Connection Pool")
print("=" * 80)
print("""
Scenario: Real production connection pool (like psycopg2, SQLAlchemy)
- Limited database connections (expensive resource)
- Threads wait for available connection
- Connection returned to pool after use
- Timeout support (real-world requirement)
""")

class DatabaseConnection:
    def __init__(self, conn_id):
        self.id = conn_id

    def execute(self, query):
        time.sleep(0.2)  # Simulate query
        return f"Result of {query}"

class ConnectionPool:
    def __init__(self, size=3):
        self.available = [DatabaseConnection(i) for i in range(size)]
        self.in_use = set()
        self.condition = threading.Condition()
        self.total_requests = 0
        self.total_waits = 0

    def acquire(self, client_name, timeout=2.0):
        """Get a connection (wait if none available)"""
        with self.condition:
            self.total_requests += 1
            start_time = time.time()

            # Wait for available connection
            while not self.available:
                elapsed = time.time() - start_time
                remaining = timeout - elapsed

                if remaining <= 0:
                    print(f"  ❌ {client_name}: TIMEOUT waiting for connection")
                    return None

                print(f"  ⏳ {client_name}: Waiting for connection... ({remaining:.1f}s left)")
                self.total_waits += 1
                self.condition.wait(timeout=remaining)

            # Get connection
            conn = self.available.pop()
            self.in_use.add(conn)
            wait_time = time.time() - start_time
            print(f"  🔗 {client_name}: Got connection #{conn.id} (waited {wait_time:.2f}s)")
            return conn

    def release(self, conn, client_name):
        """Return connection to pool"""
        with self.condition:
            self.in_use.remove(conn)
            self.available.append(conn)
            print(f"  ↩️  {client_name}: Released connection #{conn.id}")

            # Wake up ONE waiting thread
            self.condition.notify()

    def stats(self):
        return {
            'total_requests': self.total_requests,
            'total_waits': self.total_waits,
            'available': len(self.available),
            'in_use': len(self.in_use)
        }

pool = ConnectionPool(size=3)

def database_client(client_name, num_queries):
    for i in range(num_queries):
        time.sleep(random.uniform(0.1, 0.3))

        # Acquire connection
        conn = pool.acquire(client_name, timeout=2.0)
        if conn is None:
            continue

        # Use connection
        result = conn.execute(f"SELECT * FROM users WHERE client='{client_name}'")
        print(f"  💾 {client_name}: Query result - {result}")

        # Release connection
        pool.release(conn, client_name)

print("\nStarting database connection pool:")
print(f"Pool size: 3 connections, 5 clients\n")

clients = [
    threading.Thread(target=database_client, args=(f"Client-{i}", 3))
    for i in range(5)
]

for t in clients:
    t.start()
for t in clients:
    t.join()

stats = pool.stats()
print(f"\n📊 Pool Statistics:")
print(f"   Total requests: {stats['total_requests']}")
print(f"   Times waited: {stats['total_waits']}")
print(f"   Wait rate: {stats['total_waits']/stats['total_requests']*100:.1f}%")
print(f"   Final state: {stats['available']} available, {stats['in_use']} in use")

print("\n✅ Connection pool demo complete!\n")

# ============================================================================
# Example 5: ADVANCED - Event Coordinator (Barrier Alternative)
# ============================================================================
print("=" * 80)
print("5. ADVANCED: Event Coordinator - Multi-phase Workflow")
print("=" * 80)
print("""
Scenario: Distributed computation (like MapReduce)
- Multiple workers process data in phases
- All workers must complete Phase 1 before Phase 2 starts
- Coordinator tracks progress
- Uses Condition to synchronize phases
""")

class PhaseCoordinator:
    def __init__(self, num_workers):
        self.num_workers = num_workers
        self.current_phase = 1
        self.workers_ready = 0
        self.condition = threading.Condition()

    def wait_for_phase(self, worker_name, phase):
        """Worker waits until specified phase starts"""
        with self.condition:
            # Mark this worker as ready
            self.workers_ready += 1
            print(f"  ✓ {worker_name}: Ready for phase {phase} ({self.workers_ready}/{self.num_workers})")

            # Check if all workers ready
            if self.workers_ready == self.num_workers:
                print(f"\n  🚀 All workers ready! Starting Phase {phase}\n")
                self.current_phase = phase
                self.workers_ready = 0
                self.condition.notify_all()  # Wake everyone up
            else:
                # Wait for others
                while self.current_phase < phase:
                    print(f"  ⏳ {worker_name}: Waiting for others...")
                    self.condition.wait()

coordinator = PhaseCoordinator(num_workers=3)

def map_reduce_worker(worker_id):
    name = f"Worker-{worker_id}"

    # Phase 1: Map
    coordinator.wait_for_phase(name, phase=1)
    print(f"  🗺️  {name}: Mapping data...")
    time.sleep(random.uniform(0.3, 0.6))

    # Phase 2: Shuffle
    coordinator.wait_for_phase(name, phase=2)
    print(f"  🔀 {name}: Shuffling data...")
    time.sleep(random.uniform(0.3, 0.6))

    # Phase 3: Reduce
    coordinator.wait_for_phase(name, phase=3)
    print(f"  📊 {name}: Reducing data...")
    time.sleep(random.uniform(0.3, 0.6))

    print(f"  ✅ {name}: Complete!")

print("\nStarting MapReduce job:")
workers = [threading.Thread(target=map_reduce_worker, args=(i,)) for i in range(3)]
for t in workers:
    t.start()
for t in workers:
    t.join()

print("\n✅ MapReduce complete!\n")

# ============================================================================
# Summary
# ============================================================================
print("=" * 80)
print("                          SUMMARY")
print("=" * 80)
print("""
🎯 Key Concepts:

1. WHAT is Condition?
   Lock + wait/notify mechanism for thread coordination

2. WHY use Condition over Lock?
   ❌ Lock only: Busy waiting (while not ready: pass)  # Wastes CPU
   ✅ Condition: Efficient waiting (condition.wait())   # Sleeps until notified

3. Core Methods:

   with condition:
       condition.wait()      # Release lock and sleep until notified
       condition.notify()    # Wake up ONE waiting thread
       condition.notify_all()# Wake up ALL waiting threads

4. Common Pattern:

   # Waiter (Consumer)
   with condition:
       while not <condition_is_true>:
           condition.wait()  # Wait for condition
       <use_resource>
       condition.notify()    # Notify others

   # Notifier (Producer)
   with condition:
       <change_state>
       condition.notify()    # Wake up waiters

5. Real-World Use Cases:
   ✅ Producer-Consumer (our restaurant example)
   ✅ Connection pools (database, HTTP)
   ✅ Request-Response patterns
   ✅ Phase synchronization (MapReduce)
   ✅ Event coordination
   ✅ Resource throttling

6. When to use notify() vs notify_all():
   notify()     → Wake ONE waiter (resources are interchangeable)
                  Example: Connection pool - any connection works

   notify_all() → Wake ALL waiters (each checks its own condition)
                  Example: Request-response - each client checks its req_id

7. Common Mistakes:
   ❌ Forgetting while loop: if not ready: condition.wait()
      (Should be: while not ready: condition.wait())

   ❌ Checking condition outside lock
   ❌ Forgetting to notify after changing state
   ❌ Using notify() when you need notify_all()

8. Real Production Examples:
   • SQLAlchemy connection pooling
   • Celery task queues
   • Flask-SocketIO event handling
   • Django channels
   • Thread pools in concurrent.futures

⚠️  Remember: Condition doesn't replace Lock - it EXTENDS Lock with wait/notify!
""")
