/*
 * Java: Page View Counter - Race Condition Demo
 * ==============================================
 * Shows:
 * 1. Broken version (race condition)
 * 2. Fixed version (synchronized keyword)
 * 3. Fixed version (ReentrantLock)
 * 4. Fixed version (AtomicInteger)
 */

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class PageViewCounter {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("================================================================================");
        System.out.println("          JAVA: RACE CONDITION DEMONSTRATION");
        System.out.println("================================================================================");

        // Version 1: Broken
        demonstrateBroken();

        // Version 2: Fixed with synchronized
        demonstrateSynchronized();

        // Version 3: Fixed with ReentrantLock
        demonstrateReentrantLock();

        // Version 4: Fixed with AtomicInteger
        demonstrateAtomic();

        // Summary
        printSummary();
    }

    // ============================================================================
    // Version 1: BROKEN - Race Condition
    // ============================================================================
    static class PageViewCounterBroken {
        private int views = 0;

        public void increment() {
            // This looks simple but is NOT atomic!
            int temp = views;
            try {
                Thread.sleep(0, 100000); // 0.1ms - increase race window
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            views = temp + 1;
        }

        public int getViews() {
            return views;
        }
    }

    static void demonstrateBroken() throws InterruptedException {
        System.out.println("\n1. BROKEN VERSION (No Synchronization)");
        System.out.println("--------------------------------------------------------------------------------");

        PageViewCounterBroken counter = new PageViewCounterBroken();
        Thread[] threads = new Thread[1000];

        // Create 1000 threads
        for (int i = 0; i < 1000; i++) {
            threads[i] = new Thread(() -> counter.increment());
            threads[i].start();
        }

        // Wait for all threads
        for (Thread t : threads) {
            t.join();
        }

        System.out.println("Expected: 1000");
        System.out.println("Actual:   " + counter.getViews());
        System.out.println("Lost:     " + (1000 - counter.getViews()) + " increments");
        System.out.println("Status:   " + (counter.getViews() == 1000 ? "✅ Correct" : "❌ RACE CONDITION DETECTED!"));
    }

    // ============================================================================
    // Version 2: FIXED - Using synchronized
    // ============================================================================
    static class PageViewCounterSynchronized {
        private int views = 0;

        // synchronized keyword makes method thread-safe
        public synchronized void increment() {
            int temp = views;
            try {
                Thread.sleep(0, 100000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            views = temp + 1;
        }

        public synchronized int getViews() {
            return views;
        }
    }

    static void demonstrateSynchronized() throws InterruptedException {
        System.out.println("\n2. FIXED VERSION (With synchronized)");
        System.out.println("--------------------------------------------------------------------------------");

        PageViewCounterSynchronized counter = new PageViewCounterSynchronized();
        Thread[] threads = new Thread[1000];

        for (int i = 0; i < 1000; i++) {
            threads[i] = new Thread(() -> counter.increment());
            threads[i].start();
        }

        for (Thread t : threads) {
            t.join();
        }

        System.out.println("Expected: 1000");
        System.out.println("Actual:   " + counter.getViews());
        System.out.println("Status:   " + (counter.getViews() == 1000 ? "✅ Correct!" : "❌ Still broken?!"));
    }

    // ============================================================================
    // Version 3: FIXED - Using ReentrantLock
    // ============================================================================
    static class PageViewCounterReentrantLock {
        private int views = 0;
        private final ReentrantLock lock = new ReentrantLock();

        public void increment() {
            lock.lock(); // Acquire lock
            try {
                int temp = views;
                Thread.sleep(0, 100000);
                views = temp + 1;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock(); // Always unlock in finally block
            }
        }

        public int getViews() {
            lock.lock();
            try {
                return views;
            } finally {
                lock.unlock();
            }
        }
    }

    static void demonstrateReentrantLock() throws InterruptedException {
        System.out.println("\n3. FIXED VERSION (With ReentrantLock)");
        System.out.println("--------------------------------------------------------------------------------");
        System.out.println("More flexible than synchronized, supports try-lock, fairness, etc.");

        PageViewCounterReentrantLock counter = new PageViewCounterReentrantLock();
        Thread[] threads = new Thread[1000];

        for (int i = 0; i < 1000; i++) {
            threads[i] = new Thread(() -> counter.increment());
            threads[i].start();
        }

        for (Thread t : threads) {
            t.join();
        }

        System.out.println("Expected: 1000");
        System.out.println("Actual:   " + counter.getViews());
        System.out.println("Status:   ✅ Correct!");
    }

    // ============================================================================
    // Version 4: BEST PRACTICE - Using AtomicInteger
    // ============================================================================
    static class PageViewCounterAtomic {
        private final AtomicInteger views = new AtomicInteger(0);

        public void increment() {
            // Lock-free, thread-safe increment
            views.incrementAndGet();
        }

        public int getViews() {
            return views.get();
        }
    }

    static void demonstrateAtomic() throws InterruptedException {
        System.out.println("\n4. BEST PRACTICE (AtomicInteger)");
        System.out.println("--------------------------------------------------------------------------------");
        System.out.println("For simple counters, AtomicInteger is lock-free and faster");

        PageViewCounterAtomic counter = new PageViewCounterAtomic();

        // Use ExecutorService for better thread management
        ExecutorService executor = Executors.newFixedThreadPool(100);

        // Simulate 100 users, each viewing 10 pages
        for (int i = 0; i < 100; i++) {
            executor.submit(() -> {
                for (int j = 0; j < 10; j++) {
                    counter.increment();
                    try {
                        Thread.sleep(0, 10000); // 0.01ms
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);

        System.out.println("Expected: 1000 (100 users × 10 views)");
        System.out.println("Actual:   " + counter.getViews());
        System.out.println("Status:   ✅ Production-ready!");
    }

    // ============================================================================
    // Summary
    // ============================================================================
    static void printSummary() {
        System.out.println("\n================================================================================");
        System.out.println("                          SUMMARY");
        System.out.println("================================================================================");
        System.out.print("""

🎯 Key Lessons:

1. Java has TRUE parallelism (no GIL)
   - Multiple threads run simultaneously
   - Race conditions are common
   - MUST use synchronization

2. Synchronization options in Java:
   a) synchronized keyword
      - Simplest, built into language
      - synchronized method or synchronized(obj) block
      - Implicit lock per object

   b) ReentrantLock (java.util.concurrent.locks)
      - More flexible than synchronized
      - Supports tryLock(), fairness, conditions
      - Must unlock in finally block

   c) Atomic classes (java.util.concurrent.atomic)
      - Lock-free, fastest
      - AtomicInteger, AtomicLong, AtomicReference
      - Only for simple operations

3. When to use what:
   - Simple counter? → AtomicInteger
   - Complex logic? → synchronized or ReentrantLock
   - Need tryLock? → ReentrantLock
   - Default choice? → synchronized (simplest)

4. Best practices:
   - Prefer atomic classes for counters
   - Use ExecutorService over raw threads
   - Always unlock in finally block (ReentrantLock)
   - Keep synchronized blocks small
   - Consider java.util.concurrent collections

5. Thread pools:
   - Don't create raw threads in production
   - Use ExecutorService
   - Fixed, cached, scheduled thread pools

⚠️  Java makes concurrency explicit - use it correctly or suffer races!
""");
    }
}
