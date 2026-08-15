# Page View Counter - Race Condition Demo

The classic race condition example in Python, Go, Java, and JavaScript showing:
1. ❌ **Broken version** (no synchronization)
2. ✅ **Fixed version** (with proper locking)

## What This Example Shows

- ✅ Race conditions and why they're dangerous
- ✅ Thread/goroutine creation
- ✅ Synchronization primitives (Lock, Mutex, synchronized, Atomics)
- ✅ Why "it works on my machine" isn't enough

## Concurrency Comparison

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Concurrency Model** | Threads (GIL limited) | Goroutines (true parallel) | Threads | Single-threaded (event loop) |
| **Lock Type** | `threading.Lock()` | `sync.Mutex` | `synchronized` | `Atomics` or `Worker threads` |
| **Syntax** | `with lock:` | `mutex.Lock()` / `mutex.Unlock()` | `synchronized(obj)` | `Atomics.add()` |
| **Lightweight** | No (OS threads) | Yes (goroutines) | No (OS threads) | N/A (single thread) |
| **True Parallel** | No (GIL) | Yes | Yes | No (event loop) |

## Key Differences

### Python
- **GIL (Global Interpreter Lock)** makes some races less likely
- But races still happen! Don't rely on GIL
- Use `threading.Lock()` for safety

### Go
- **Goroutines** are extremely lightweight (thousands possible)
- `sync.Mutex` for locking
- Also has channels for message passing
- True parallelism on multi-core

### Java
- **Traditional threads** (heavyweight)
- `synchronized` keyword or `ReentrantLock`
- `ExecutorService` for thread pools
- Verbose but explicit

### JavaScript
- **Single-threaded** by default (event loop)
- For race conditions, need `Worker threads`
- `Atomics` for shared memory operations
- Usually avoid with async/await patterns

## Expected Output

### Broken Version (All Languages)
```
Expected: 1000
Actual: 437    ← Lost 563 increments!
```

### Fixed Version (All Languages)
```
Expected: 1000
Actual: 1000   ← Correct!
```

## Running the Examples

```bash
# Python
python3 page_view_counter.py

# Go
go run page_view_counter.go

# Java
javac PageViewCounter.java && java PageViewCounter

# JavaScript (requires Node.js 12+)
node page_view_counter.js
```

## Interview Tips

1. **Always mention thread safety** in system design
2. **Don't assume languages are thread-safe** (they're not!)
3. **Race conditions are intermittent** - hard to test
4. **Use locks/mutexes** for critical sections
5. **Keep critical sections small** for performance

## Real-World Impact

This simple bug has caused:
- $60M cryptocurrency hack
- $440M Knight Capital trading loss
- Lost analytics data
- Bank overdrafts

**Learn it. Fix it. Don't cause the next disaster!**
