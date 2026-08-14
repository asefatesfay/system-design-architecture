"""
Modified version that WILL show the race condition
"""
import threading
import time

class PageViewCounter:
    def __init__(self):
        self.views = 0

    def increment(self):
        # Split the operation to maximize race window
        temp = self.views              # READ
        time.sleep(0.00001)            # ← RACE WINDOW HERE!
        self.views = temp + 1          # WRITE

    def get_views(self):
        return self.views

print("Running with MAXIMIZED race window...")
print("Expected: 5000")
print("\nActual results from 5 runs:")
print("-" * 40)

for run in range(5):
    counter = PageViewCounter()
    threads = [threading.Thread(target=counter.increment) for _ in range(5000)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    result = counter.get_views()
    lost = 5000 - result
    status = "✅" if result == 5000 else f"❌ Lost {lost} increments"
    print(f"Run {run+1}: {result:4d}/5000  {status}")

print("\n" + "="*70)
print("🎯 Key Point: Your original code has the SAME bug")
print("   It just has a smaller race window, making it rarer")
print("   But rare ≠ impossible! This WILL fail in production.")
print("="*70)
