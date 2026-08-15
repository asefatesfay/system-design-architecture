"""
Python: Page View Counter - Race Condition Demo
================================================
Shows:
1. Broken version (race condition)
2. Fixed version (with Lock)
3. Why Python's GIL doesn't save you
"""

import threading
import time


print("=" * 80)
print("          PYTHON: RACE CONDITION DEMONSTRATION")
print("=" * 80)


# ============================================================================
# Version 1: BROKEN - Race Condition
# ============================================================================
class PageViewCounterBroken:
    def __init__(self):
        self.views = 0

    def increment(self):
        # This looks atomic but it's NOT!
        # Under the hood: READ, ADD, WRITE (3 operations)
        temp = self.views
        time.sleep(0.0001)  # Simulate work, increase race window
        self.views = temp + 1


print("\n1. BROKEN VERSION (No Lock)")
print("-" * 80)

counter_broken = PageViewCounterBroken()
threads = []

# Create 1000 threads, each incrementing once
for i in range(1000):
    t = threading.Thread(target=counter_broken.increment)
    threads.append(t)
    t.start()

# Wait for all threads
for t in threads:
    t.join()

print(f"Expected: 1000")
print(f"Actual:   {counter_broken.views}")
print(f"Lost:     {1000 - counter_broken.views} increments")
print(f"Status:   {'✅ Correct' if counter_broken.views == 1000 else '❌ RACE CONDITION DETECTED!'}")


# ============================================================================
# Version 2: FIXED - Using Lock
# ============================================================================
class PageViewCounterFixed:
    def __init__(self):
        self.views = 0
        self.lock = threading.Lock()  # Create a lock

    def increment(self):
        with self.lock:  # Acquire lock (only one thread at a time)
            temp = self.views
            time.sleep(0.0001)  # Even with delay, no race!
            self.views = temp + 1
        # Lock automatically released here


print("\n2. FIXED VERSION (With Lock)")
print("-" * 80)

counter_fixed = PageViewCounterFixed()
threads = []

for i in range(1000):
    t = threading.Thread(target=counter_fixed.increment)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Expected: 1000")
print(f"Actual:   {counter_fixed.views}")
print(f"Status:   {'✅ Correct!' if counter_fixed.views == 1000 else '❌ Still broken?!'}")


# ============================================================================
# Version 3: PRODUCTION - Context Manager Pattern
# ============================================================================
class PageViewCounterProduction:
    """Production-ready version with proper encapsulation"""

    def __init__(self):
        self._views = 0  # Private
        self._lock = threading.Lock()

    def increment(self):
        """Thread-safe increment"""
        with self._lock:
            self._views += 1

    def get_views(self):
        """Thread-safe read"""
        with self._lock:
            return self._views

    def reset(self):
        """Thread-safe reset"""
        with self._lock:
            self._views = 0


print("\n3. PRODUCTION VERSION (Best Practices)")
print("-" * 80)

counter_prod = PageViewCounterProduction()


def simulate_user():
    """Simulate a user viewing pages"""
    for _ in range(10):
        counter_prod.increment()
        time.sleep(0.0001)


# Simulate 100 users, each viewing 10 pages
threads = []
for i in range(100):
    t = threading.Thread(target=simulate_user)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"Expected: 1000 (100 users × 10 views)")
print(f"Actual:   {counter_prod.get_views()}")
print(f"Status:   ✅ Production-ready and correct!")


# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("                          SUMMARY")
print("=" * 80)
print("""
🎯 Key Lessons:

1. Python's GIL doesn't prevent all race conditions
   - GIL only prevents simultaneous bytecode execution
   - But threads can still interleave operations
   - ALWAYS use locks for shared data

2. The race happens between READ and WRITE
   - self.views = self.views + 1  # Looks atomic, but isn't!
   - Actually: READ → ADD → WRITE (3 steps)

3. Always use threading.Lock()
   - with lock:  # Pythonic and safe
   - Automatic acquire/release
   - Use for ALL shared mutable data

4. Best practices:
   - Make data private (_variable)
   - Provide thread-safe methods
   - Lock at method level, not caller level
   - Keep critical sections small

⚠️  In production, even a 0.1% failure rate = thousands of bugs!
""")
