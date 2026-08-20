# Design Patterns - Quick Start

Learn cloud design patterns with practical Python examples!

## Installation

```bash
cd design-patterns
pip install -r requirements.txt
```

## Start with Ambassador Pattern

The **Ambassador Pattern** is perfect for beginners. It centralizes common connectivity tasks like retries, logging, and monitoring.

### Run the Demo

```bash
# Terminal 1: Start mock API
cd 01-ambassador
python demo/mock_api.py

# Terminal 2: Run comparison demo
python demo/run_demo.py
```

### What You'll Learn

✅ Why duplicate retry logic is bad
✅ How Ambassador centralizes connectivity
✅ Circuit breaker pattern basics
✅ Rate limiting implementation
✅ Centralized metrics collection

## Pattern Progression

**Beginner Track** (Start here!)
1. **Ambassador** ← Start here
2. Cache-Aside
3. Retry
4. Circuit Breaker

**Intermediate Track**
5. Gateway Aggregation
6. Queue-Based Load Leveling
7. Competing Consumers
8. Throttling

**Advanced Track**
9. CQRS
10. Event Sourcing
11. Sharding
12. Bulkhead

## Each Pattern Includes

- 📖 **README.md** - Full explanation with diagrams
- ❌ **without_pattern/** - The problem (code without pattern)
- ✅ **with_pattern/** - The solution (code with pattern)
- 🧪 **demo/** - Interactive demonstration
- 📈 **benchmarks/** - Performance comparison

## Quick Pattern Selector

**I need to...**

| Goal | Pattern |
|------|---------|
| Add retries to API calls | **Ambassador** |
| Cache data | Cache-Aside |
| Prevent cascade failures | Circuit Breaker |
| Combine multiple API calls | Gateway Aggregation |
| Handle burst traffic | Queue-Based Load Leveling |
| Process messages in parallel | Competing Consumers |

## Tips for Learning

1. **Start with the demo** - See it in action first
2. **Read the README** - Understand why it matters
3. **Compare the code** - See the before/after
4. **Run benchmarks** - Measure the difference
5. **Modify and experiment** - Make it your own!

## Project Structure

```
design-patterns/
├── README.md                          # Overview of all patterns
├── QUICKSTART.md                      # This file
├── requirements.txt                   # Common dependencies
│
├── 01-ambassador/                     # Ambassador Pattern
│   ├── README.md                     # Pattern docs
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── without_pattern/main.py       # Problem code
│   ├── with_pattern/main.py          # Solution code
│   ├── demo/
│   │   ├── mock_api.py              # Mock API server
│   │   └── run_demo.py              # Interactive demo
│   └── benchmarks/benchmark.py       # Performance tests
│
├── 02-gateway-aggregation/           # Coming soon...
├── 03-gateway-offloading/            # Coming soon...
└── ...
```

## Need Help?

- **Stuck?** Check the pattern's QUICKSTART.md
- **Want more depth?** Read the full README.md
- **Have questions?** Review the code comments

## Next Steps

After completing Ambassador pattern:
1. Read the [full pattern catalog](./README.md)
2. Try implementing your own Ambassador features
3. Move to the next pattern in your track

Happy learning! 🚀
