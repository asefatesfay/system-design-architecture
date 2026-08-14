"""
Race Condition Demo - Guaranteed to show the bug
This demonstrates why race conditions are dangerous - they're intermittent!
"""
import threading
import time

print("="*70)
print("          RACE CONDITION DEMONSTRATION")
print("="*70)

# ============================================================================
# Version 1: BROKEN - Race condition (sometimes works!)
# ============================================================================
class PageViewCounterBroken:
    def __init__(self):
        self.views = 0

    def increment(self):
        # Read current value
        temp = self.views

        # THIS IS THE CRITICAL RACE WINDOW!
        # Another thread can read the same value here
        time.sleep(0.0001)  # Simulate work / network delay

        # Write new value
        self.views = temp + 1

    def get_views(self):
        return self.views

print("\n1. BROKEN VERSION (No Lock)")
print("-" * 70)

# Run 10 times to show it's intermittent
results_broken = []
for run in range(10):
    counter = PageViewCounterBroken()
    threads = [threading.Thread(target=counter.increment) for _ in range(100)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    result = counter.get_views()
    results_broken.append(result)
    status = "✅" if result == 100 else "❌"
    print(f"  Run {run+1}: {result}/100 {status}")

print(f"\nExpected: 100 every time")
print(f"Correct: {results_broken.count(100)}/10 runs")
print(f"Lost increments: {1000 - sum(results_broken)} total")

# ============================================================================
# Version 2: CORRECT - Using Lock
# ============================================================================
class PageViewCounterCorrect:
    def __init__(self):
        self.views = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            # Atomic: Read, compute, write
            temp = self.views
            time.sleep(0.0001)  # Even with delay, no race!
            self.views = temp + 1

    def get_views(self):
        with self.lock:
            return self.views

print("\n2. CORRECT VERSION (With Lock)")
print("-" * 70)

results_correct = []
for run in range(10):
    counter = PageViewCounterCorrect()
    threads = [threading.Thread(target=counter.increment) for _ in range(100)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    result = counter.get_views()
    results_correct.append(result)
    print(f"  Run {run+1}: {result}/100 ✅")

print(f"\nExpected: 100 every time")
print(f"Correct: {results_correct.count(100)}/10 runs")

# ============================================================================
# Version 3: EXTREME - Guaranteed race condition
# ============================================================================
print("\n3. EXTREME VERSION (Guaranteed to Fail)")
print("-" * 70)
print("Using barrier to force simultaneous access\n")

class PageViewCounterExtreme:
    def __init__(self):
        self.views = 0

    def increment_with_barrier(self, barrier):
        # Read value
        temp = self.views

        # Wait for all threads to reach this point
        barrier.wait()

        # Now ALL threads write at once!
        self.views = temp + 1

    def get_views(self):
        return self.views

counter = PageViewCounterExtreme()
num_threads = 50
barrier = threading.Barrier(num_threads)

threads = [threading.Thread(target=counter.increment_with_barrier, args=(barrier,))
           for _ in range(num_threads)]

for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Expected: {num_threads}")
print(f"Actual: {counter.get_views()}")
print(f"Lost: {num_threads - counter.get_views()} increments")
print("\n⚠️  This shows ALL threads read 0, then all write 1!")

# ============================================================================
# Real-World Simulation: Bank Account
# ============================================================================
print("\n4. REAL-WORLD: Bank Account Overdraft")
print("-" * 70)

class BankAccountBroken:
    def __init__(self, balance):
        self.balance = balance

    def withdraw(self, amount):
        # Check balance
        if self.balance >= amount:
            # RACE WINDOW HERE!
            time.sleep(0.001)

            # Withdraw
            self.balance -= amount
            return True
        return False

account = BankAccountBroken(100)

def withdraw_60():
    result = account.withdraw(60)
    print(f"  Thread {threading.current_thread().name}: {'✅ Withdrew $60' if result else '❌ Insufficient funds'}")

# Two threads try to withdraw $60 from $100 account
thread1 = threading.Thread(target=withdraw_60, name="ATM-1")
thread2 = threading.Thread(target=withdraw_60, name="ATM-2")

thread1.start()
thread2.start()
thread1.join()
thread2.join()

print(f"\nFinal balance: ${account.balance}")
print(f"Expected: $40 (one succeeds) or $100 (both fail)")
print(f"Actual: OVERDRAFT! Both withdrew money!" if account.balance < 0 else "By luck, worked correctly")

# ============================================================================
# The Fix
# ============================================================================
print("\n5. FIXED: Bank Account with Lock")
print("-" * 70)

class BankAccountFixed:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()

    def withdraw(self, amount):
        with self.lock:  # Atomic check-and-withdraw
            if self.balance >= amount:
                time.sleep(0.001)
                self.balance -= amount
                return True
            return False

account = BankAccountFixed(100)

def withdraw_60_fixed():
    result = account.withdraw(60)
    print(f"  Thread {threading.current_thread().name}: {'✅ Withdrew $60' if result else '❌ Insufficient funds'}")

thread1 = threading.Thread(target=withdraw_60_fixed, name="ATM-1")
thread2 = threading.Thread(target=withdraw_60_fixed, name="ATM-2")

thread1.start()
thread2.start()
thread1.join()
thread2.join()

print(f"\nFinal balance: ${account.balance}")
print(f"✅ Correct! One withdrawal succeeded, one failed")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*70)
print("                          SUMMARY")
print("="*70)
print("""
🎯 Key Lessons:

1. Race conditions are INTERMITTENT
   - Sometimes work, sometimes fail
   - Makes them hard to debug
   - Can't rely on testing alone

2. The race happens between READ and WRITE
   - Not during computation
   - The smaller the window, the rarer the bug
   - But rare ≠ impossible!

3. Python's GIL hides some races
   - But NOT ALL!
   - Can still have data races
   - Don't rely on GIL for correctness

4. Real consequences:
   - Lost page views (analytics wrong)
   - Overdraft (money lost)
   - Double booking (angry customers)
   - Data corruption (system broken)

5. The fix: Locks
   - Use threading.Lock() for critical sections
   - Keep critical sections small
   - Always use with context manager

⚠️  "It works on my machine" is NOT enough for concurrent code!
""")
