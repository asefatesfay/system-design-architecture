/*
Go: Page View Counter - Race Condition Demo
============================================
Shows:
1. Broken version (race condition)
2. Fixed version (with Mutex)
3. Go's race detector
4. Alternative: atomic operations
*/

package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

func main() {
	fmt.Println("================================================================================")
	fmt.Println("          GO: RACE CONDITION DEMONSTRATION")
	fmt.Println("================================================================================")

	// Version 1: Broken
	demonstrateBroken()

	// Version 2: Fixed with Mutex
	demonstrateFixed()

	// Version 3: Fixed with Atomic
	demonstrateAtomic()

	// Summary
	printSummary()
}

// ============================================================================
// Version 1: BROKEN - Race Condition
// ============================================================================
type PageViewCounterBroken struct {
	views int
}

func (c *PageViewCounterBroken) Increment() {
	// This is NOT atomic!
	temp := c.views
	time.Sleep(100 * time.Microsecond) // Increase race window
	c.views = temp + 1
}

func demonstrateBroken() {
	fmt.Println("\n1. BROKEN VERSION (No Mutex)")
	fmt.Println("--------------------------------------------------------------------------------")

	counter := &PageViewCounterBroken{views: 0}
	var wg sync.WaitGroup

	// Create 1000 goroutines (much lighter than threads!)
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Increment()
		}()
	}

	// Wait for all goroutines to complete
	wg.Wait()

	fmt.Printf("Expected: 1000\n")
	fmt.Printf("Actual:   %d\n", counter.views)
	fmt.Printf("Lost:     %d increments\n", 1000-counter.views)
	if counter.views == 1000 {
		fmt.Println("Status:   ✅ Correct (got lucky!)")
	} else {
		fmt.Println("Status:   ❌ RACE CONDITION DETECTED!")
	}
	fmt.Println("\n💡 Run with: go run -race page_view_counter.go")
	fmt.Println("   Go's race detector will catch this!")
}

// ============================================================================
// Version 2: FIXED - Using Mutex
// ============================================================================
type PageViewCounterFixed struct {
	views int
	mu    sync.Mutex // Mutex for synchronization
}

func (c *PageViewCounterFixed) Increment() {
	c.mu.Lock() // Acquire lock
	defer c.mu.Unlock() // Release lock when function returns

	temp := c.views
	time.Sleep(100 * time.Microsecond)
	c.views = temp + 1
}

func (c *PageViewCounterFixed) GetViews() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.views
}

func demonstrateFixed() {
	fmt.Println("\n2. FIXED VERSION (With Mutex)")
	fmt.Println("--------------------------------------------------------------------------------")

	counter := &PageViewCounterFixed{}
	var wg sync.WaitGroup

	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			counter.Increment()
		}()
	}

	wg.Wait()

	fmt.Printf("Expected: 1000\n")
	fmt.Printf("Actual:   %d\n", counter.GetViews())
	if counter.GetViews() == 1000 {
		fmt.Println("Status:   ✅ Correct!")
	} else {
		fmt.Println("Status:   ❌ Still broken?!")
	}
}

// ============================================================================
// Version 3: BEST PRACTICE - Using Atomic Operations
// ============================================================================
type PageViewCounterAtomic struct {
	views int64 // Must be int64 for atomic operations
}

func (c *PageViewCounterAtomic) Increment() {
	// atomic.AddInt64 is lock-free and faster than mutex
	atomic.AddInt64(&c.views, 1)
}

func (c *PageViewCounterAtomic) GetViews() int64 {
	return atomic.LoadInt64(&c.views)
}

func demonstrateAtomic() {
	fmt.Println("\n3. BEST PRACTICE (Atomic Operations)")
	fmt.Println("--------------------------------------------------------------------------------")
	fmt.Println("For simple counters, atomic operations are faster than mutex")

	counter := &PageViewCounterAtomic{}
	var wg sync.WaitGroup

	// Simulate 100 users, each viewing 10 pages
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			// Each goroutine increments 10 times
			for j := 0; j < 10; j++ {
				counter.Increment()
				time.Sleep(10 * time.Microsecond)
			}
		}()
	}

	wg.Wait()

	fmt.Printf("Expected: 1000 (100 users × 10 views)\n")
	fmt.Printf("Actual:   %d\n", counter.GetViews())
	fmt.Println("Status:   ✅ Production-ready and lock-free!")
}

// ============================================================================
// Summary
// ============================================================================
func printSummary() {
	fmt.Println("\n================================================================================")
	fmt.Println("                          SUMMARY")
	fmt.Println("================================================================================")
	fmt.Print(`
🎯 Key Lessons:

1. Go has TRUE parallelism (no GIL like Python)
   - Multiple goroutines run simultaneously on multiple cores
   - Race conditions are very common
   - ALWAYS use synchronization

2. Goroutines are lightweight
   - Can create thousands easily
   - Much lighter than OS threads
   - Managed by Go runtime

3. Synchronization options:
   a) sync.Mutex - General purpose locking
      - Use for complex operations
      - Explicit Lock()/Unlock()

   b) atomic package - For simple operations
      - Lock-free, faster
      - Only for basic types (int32, int64, pointers)

   c) Channels - For message passing
      - "Don't communicate by sharing memory; share memory by communicating"
      - Idiomatic Go way

4. Go race detector is your friend!
   - go run -race program.go
   - go test -race
   - Catches races at runtime

5. Best practices:
   - Embed sync.Mutex in structs
   - Use defer to unlock
   - Prefer atomic for counters
   - Use channels for coordination

⚠️  Go makes concurrency easy - but race conditions are still dangerous!
    Always test with -race flag!
`)
}
