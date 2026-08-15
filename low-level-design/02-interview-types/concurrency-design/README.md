# Concurrency Design Interviews - Multi-Language Guide

Complete guide to concurrency design interviews in **Python, Go, Java, and JavaScript** with language-specific concurrency primitives and patterns.

## 🎯 Overview

Concurrency interviews focus on designing systems that work correctly when multiple threads/goroutines access shared data simultaneously. These can appear as standalone problems or as extensions to regular LLD questions.

**Common at:** Google, Amazon, Microsoft, high-frequency trading firms
**Level:** Usually mid-level to senior positions
**Duration:** 30-60 minutes

---

## 📚 Choose Your Language

Each language guide includes:
- ✅ Language-specific concurrency primitives
- ✅ Race conditions and how to fix them
- ✅ Deadlock prevention strategies
- ✅ 6 complete concurrency problems
- ✅ Thread-safe implementations
- ✅ Best practices and common pitfalls

### [🐍 Python - Concurrency](./python.md)
**Primitives:**
- `threading.Lock`, `RLock`, `Semaphore`
- `threading.Condition`, `Event`
- `Queue` for thread-safe communication
- `ThreadPoolExecutor`
- **GIL** (Global Interpreter Lock) implications

**Best for:** I/O-bound tasks, web scraping, API calls

---

### [🔷 Go - Concurrency](./go.md)
**Primitives:**
- **Goroutines** (lightweight threads)
- **Channels** (communication, not memory)
- `sync.Mutex`, `sync.RWMutex`
- `sync.WaitGroup`
- `select` statement for channel operations

**Best for:** High-concurrency servers, distributed systems

---

### [☕ Java - Concurrency](./java.md)
**Primitives:**
- `synchronized` keyword
- `ReentrantLock`, `ReadWriteLock`
- `Semaphore`, `CountDownLatch`
- `AtomicInteger`, `AtomicLong`
- `BlockingQueue`
- `ExecutorService`

**Best for:** Enterprise applications, Android, multi-threaded services

---

### [💛 JavaScript - Concurrency](./javascript.md)
**Primitives:**
- **Event loop** (single-threaded)
- **Worker threads** for true parallelism
- `SharedArrayBuffer` + `Atomics`
- `async`/`await` for coordination
- Promise-based patterns

**Best for:** Web applications, Node.js servers, I/O operations

---

## 📊 Language Comparison

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Threading Model** | OS threads + GIL | Goroutines (M:N) | OS threads | Event loop + Workers |
| **Lightweight?** | No (heavy) | Yes (very light) | No (heavy) | Yes (event loop) |
| **True Parallelism** | ❌ GIL limits | ✅ Native | ✅ Native | ✅ Workers only |
| **Primary Lock** | `Lock` | `sync.Mutex` | `synchronized` | N/A (single-thread) |
| **Communication** | `Queue` | Channels | `BlockingQueue` | Messages/Events |
| **Best Use Case** | I/O-bound | High concurrency | Enterprise | Web/Node.js |

---

## 🔑 Key Concepts (Universal)

### 1. Race Conditions
**What:** Multiple threads accessing shared data, at least one writing, without synchronization.

**Example Problem:** Bank account deposits getting lost.

**Solutions:**
- **Python:** `threading.Lock()`
- **Go:** `sync.Mutex` or channels
- **Java:** `synchronized` or `ReentrantLock`
- **JavaScript:** `Atomics` or single-threaded design

### 2. Deadlocks
**What:** Two or more threads waiting for each other to release resources.

**Prevention:**
- Always acquire locks in consistent order
- Use timeouts when acquiring locks
- Avoid nested locks if possible
- Use higher-level constructs (channels, queues)

### 3. Thread Safety Patterns
- **Immutability:** Can't change = inherently safe
- **Thread-local storage:** Each thread has its own copy
- **Message passing:** Communicate via channels/queues
- **Atomic operations:** Hardware-level synchronization

---

## 💡 Common Problems (All Languages)

### Problem 1: Thread-Safe Counter
Increment counter from multiple threads without losing counts.

**Key Concepts:** Locks, atomic operations, race conditions

### Problem 2: Producer-Consumer
Producers add items to buffer, consumers remove them.

**Key Concepts:** Bounded buffers, signaling, queues

### Problem 3: Thread-Safe Singleton
Ensure only one instance exists across all threads.

**Key Concepts:** Double-checked locking, lazy initialization

### Problem 4: Read-Write Lock
Allow multiple readers OR one writer.

**Key Concepts:** Reader preference, writer preference, fairness

### Problem 5: Rate Limiter
Limit requests per second from multiple threads.

**Key Concepts:** Token bucket, sliding window, thread safety

### Problem 6: Thread Pool
Pool of worker threads processing tasks.

**Key Concepts:** Work queues, thread lifecycle, shutdown

---

## 🎓 Interview Approach

### Step 1: Identify Shared State
**Ask:** What data is accessed by multiple threads?

### Step 2: Identify Critical Sections
**Ask:** Which operations must be atomic?

### Step 3: Choose Synchronization
**Options:**
- **Python:** Lock, RLock, Semaphore, Queue
- **Go:** Mutex, channels, sync.WaitGroup
- **Java:** synchronized, ReentrantLock, Atomic*
- **JavaScript:** Workers, Atomics, single-threaded design

### Step 4: Prevent Deadlocks
- Lock ordering
- Timeout mechanisms
- Avoid nested locks
- Use message passing

### Step 5: Test Mentally
Walk through scenarios with 2-3 threads/goroutines.

---

## 🚫 Red Flags to Avoid

### ❌ No Synchronization
```
Shared mutable state without protection
→ Race conditions guaranteed
```

### ❌ Too Coarse-Grained Locking
```
One big lock for everything
→ Poor performance, no concurrency
```

### ❌ Nested Locks Without Ordering
```
Lock A then B in one place
Lock B then A in another
→ Deadlock waiting to happen
```

### ❌ Ignoring Deadlocks
```
Not discussing prevention
→ Shows lack of experience
```

---

## 💭 Discussion Points

### Performance Trade-offs
- **Fine-grained locking:** Better concurrency, more complex
- **Coarse-grained locking:** Simpler, less concurrency
- **Lock-free:** Best performance, hardest to implement

### Language-Specific Considerations
- **Python GIL:** Limits CPU-bound parallelism
- **Go channels:** "Don't communicate by sharing memory"
- **Java Atomic*:** Lock-free for simple cases
- **JavaScript event loop:** Single-threaded but non-blocking

### Scalability
- How does solution scale with threads/cores?
- What are bottlenecks?
- Can we eliminate locks? (immutability, message passing)

---

## 📖 Problem Mapping

| Problem | Python Guide | Go Guide | Java Guide | JS Guide |
|---------|-------------|----------|------------|----------|
| Counter | [Link](./python.md#problem-1-thread-safe-counter) | [Link](./go.md#problem-1-thread-safe-counter) | [Link](./java.md#problem-1-thread-safe-counter) | [Link](./javascript.md#problem-1-thread-safe-counter) |
| Producer-Consumer | [Link](./python.md#problem-2-producer-consumer) | [Link](./go.md#problem-2-producer-consumer) | [Link](./java.md#problem-2-producer-consumer) | [Link](./javascript.md#problem-2-producer-consumer) |
| Singleton | [Link](./python.md#problem-3-thread-safe-singleton) | [Link](./go.md#problem-3-thread-safe-singleton) | [Link](./java.md#problem-3-thread-safe-singleton) | [Link](./javascript.md#problem-3-thread-safe-singleton) |
| Read-Write Lock | [Link](./python.md#problem-4-read-write-lock) | [Link](./go.md#problem-4-read-write-lock) | [Link](./java.md#problem-4-read-write-lock) | [Link](./javascript.md#problem-4-read-write-lock) |
| Rate Limiter | [Link](./python.md#problem-5-rate-limiter) | [Link](./go.md#problem-5-rate-limiter) | [Link](./java.md#problem-5-rate-limiter) | [Link](./javascript.md#problem-5-rate-limiter) |
| Thread Pool | [Link](./python.md#problem-6-thread-pool) | [Link](./go.md#problem-6-thread-pool) | [Link](./java.md#problem-6-thread-pool) | [Link](./javascript.md#problem-6-thread-pool) |

---

## 🎯 Tips for Success

### For Interview Preparation
1. **Master ONE language first** - understand its concurrency model deeply
2. **Practice problems** - implement all 6 in your language
3. **Understand trade-offs** - when to use which primitive
4. **Think about edge cases** - what can go wrong?

### During Interview
1. **Start simple** - single-threaded first, then add concurrency
2. **Ask questions** - "Should this be thread-safe?" "What's the scale?"
3. **Identify shared state** - explicitly list what's shared
4. **Choose right tool** - lock vs channel vs atomic vs queue
5. **Discuss deadlocks** - how to prevent them
6. **Test mentally** - walk through with 2-3 threads

### Common Mistakes
❌ Not asking about concurrency requirements
❌ Using wrong primitives (e.g., Lock where Semaphore fits better)
❌ Ignoring deadlock scenarios
❌ Over-complicating with unnecessary synchronization
❌ Not testing the concurrent design mentally

---

## 🌟 Why This Matters

### In Interviews
- **Google/Amazon/Microsoft:** Frequently ask concurrency questions
- **Shows depth:** Understanding of OS, threading, synchronization
- **Real-world relevance:** Production systems are concurrent
- **Problem-solving:** Requires careful thinking and attention to detail

### In Real Work
- **Correctness:** Bugs in concurrent code are hard to reproduce
- **Performance:** Proper concurrency scales with hardware
- **Reliability:** Thread safety prevents production issues
- **Design:** Influences architecture decisions

---

**Ready to dive in? Pick your language above and start learning! 🚀**

[Back to Interview Types](../)
