# Quick Navigation Guide

Visual overview of the low-level-design structure - find what you need fast!

## 📂 Directory Structure

```
low-level-design/
│
├── 📖 README.md                     ← Start here (overview)
├── 🎯 LEARNING-GUIDE.md             ← Natural learning path (recommended)
├── 📍 NAVIGATION.md                 ← This file (quick reference)
│
├── 01-introduction/                 ← What is LLD?
│   └── what-is-lld.md
│
├── 02-interview-types/              ← Types of LLD interviews
│   ├── object-oriented-design.md
│   ├── machine-coding.md
│   └── concurrency-design/
│
├── 03-oop-fundamentals/             ← Core OOP concepts ⭐⭐⭐
│   ├── README.md
│   ├── classes-and-objects/         Multi-language (Python, Go, Java, JS)
│   ├── four-pillars/                Multi-language (Python, Go, Java, JS)
│   ├── special-methods.md           Python dunder methods
│   ├── interfaces-abstract-classes.md
│   ├── access-modifiers.md          Public, protected, private
│   └── relationships.md             Association, Composition, etc.
│
├── 04-design-principles/            ← SOLID, DRY, KISS, YAGNI
│   ├── README.md
│   └── solid.md                     ⭐ Critical for interviews!
│
├── 05-uml-diagrams/                 ← Class, Sequence, Use Case diagrams
│   └── README.md
│
├── 06-design-patterns/              ← Essential patterns ⭐⭐⭐
│   ├── README.md                    Pattern overview & learning path
│   │
│   ├── Creational Patterns/
│   │   ├── factory.md               ⭐⭐⭐ Start here!
│   │   ├── singleton.md             ⭐⭐⭐ Common but often misused
│   │   └── builder.md               ⭐⭐ Complex construction
│   │
│   └── Structural Patterns/
│       ├── adapter.md               ⭐⭐ API integration
│       ├── decorator.md             ⭐⭐⭐ Add behavior
│       ├── facade.md                ⭐⭐ Simplify complexity
│       └── proxy.md                 ⭐⭐ Access control
│
├── python-must-knows.md             ← ⭐ NEW! Python language refresher
├── async-patterns.md                ← ⭐ NEW! Asyncio & concurrency
│
└── 07-practice-problems/            ← Real interview questions
    ├── parking-lot/
    ├── lru-cache/
    ├── vending-machine/
    └── elevator-system/

⭐⭐⭐ = Critical     ⭐⭐ = Important     ⭐ = Good to know
```

---

## 🎯 I Want to Learn...

### OOP Basics
→ [`03-oop-fundamentals/classes-and-objects/`](./03-oop-fundamentals/classes-and-objects/)

### Four Pillars (Encapsulation, Abstraction, Inheritance, Polymorphism)
→ [`03-oop-fundamentals/four-pillars/`](./03-oop-fundamentals/four-pillars/)

### Python Dunder Methods (`__init__`, `__str__`, etc.)
→ [`03-oop-fundamentals/special-methods.md`](./03-oop-fundamentals/special-methods.md)

### Abstract Classes & Interfaces
→ [`03-oop-fundamentals/interfaces-abstract-classes.md`](./03-oop-fundamentals/interfaces-abstract-classes.md)

### Public/Private/Protected
→ [`03-oop-fundamentals/access-modifiers.md`](./03-oop-fundamentals/access-modifiers.md)

### Class Relationships (Composition, Aggregation, etc.)
→ [`03-oop-fundamentals/relationships.md`](./03-oop-fundamentals/relationships.md)

### SOLID Principles ⭐ CRITICAL!
→ [`04-design-principles/solid.md`](./04-design-principles/solid.md)

---

## 🎨 I Need a Design Pattern for...

### Creating Objects
| Need | Pattern | File |
|------|---------|------|
| Create different types of objects | **Factory** | [`factory.md`](./06-design-patterns/factory.md) |
| Need exactly one instance | **Singleton** | [`singleton.md`](./06-design-patterns/singleton.md) |
| Complex object construction | **Builder** | [`builder.md`](./06-design-patterns/builder.md) |

### Connecting Objects
| Need | Pattern | File |
|------|---------|------|
| Make incompatible interfaces work | **Adapter** | [`adapter.md`](./06-design-patterns/adapter.md) |
| Add behavior without modifying class | **Decorator** | [`decorator.md`](./06-design-patterns/decorator.md) |
| Simplify complex subsystem | **Facade** | [`facade.md`](./06-design-patterns/facade.md) |
| Control access (lazy load, cache) | **Proxy** | [`proxy.md`](./06-design-patterns/proxy.md) |

### Async/Concurrent Programming
| Need | Topic | File |
|------|-------|------|
| `async`/`await` basics | Async fundamentals | [`async-patterns.md`](./async-patterns.md) |
| Producer-Consumer | Async queue | [`async-patterns.md`](./async-patterns.md#3-async-producer-consumer-pattern) |
| Rate limiting | Async rate limiter | [`async-patterns.md`](./async-patterns.md#7-async-rate-limiting) |
| Retry logic | Async retry | [`async-patterns.md`](./async-patterns.md#8-async-retry-pattern) |
| Threading vs Asyncio | Comparison | [`async-patterns.md`](./async-patterns.md#10-threading-vs-asyncio) |

---

## 📚 Common Interview Topics

### Asked About SOLID?
→ [`solid.md`](./04-design-principles/solid.md)

### Asked "Design a Parking Lot"?
→ [`07-practice-problems/parking-lot/`](./07-practice-problems/parking-lot/)

### Asked "Implement LRU Cache"?
→ [`07-practice-problems/lru-cache/`](./07-practice-problems/lru-cache/)

### Asked "What's the difference between Adapter and Decorator?"
→ [`adapter.md`](./06-design-patterns/adapter.md) + [`decorator.md`](./06-design-patterns/decorator.md) (both have comparisons)

### Asked "When would you use Factory?"
→ [`factory.md`](./06-design-patterns/factory.md)

### Asked About Composition vs Inheritance?
→ [`relationships.md`](./03-oop-fundamentals/relationships.md)

---

## 🔍 By Difficulty Level

### Beginner (Week 1-2)
1. [Classes and Objects](./03-oop-fundamentals/classes-and-objects/)
2. [Four Pillars](./03-oop-fundamentals/four-pillars/)
3. [Special Methods](./03-oop-fundamentals/special-methods.md)

### Intermediate (Week 3-4)
1. [Interfaces & Abstract Classes](./03-oop-fundamentals/interfaces-abstract-classes.md)
2. [Relationships](./03-oop-fundamentals/relationships.md)
3. [SOLID Principles](./04-design-principles/solid.md)
4. [Factory Pattern](./06-design-patterns/factory.md)
5. [Decorator Pattern](./06-design-patterns/decorator.md)

### Advanced (Week 5+)
1. [Builder Pattern](./06-design-patterns/builder.md)
2. [Adapter Pattern](./06-design-patterns/adapter.md)
3. [Facade Pattern](./06-design-patterns/facade.md)
4. [Proxy Pattern](./06-design-patterns/proxy.md)
5. [Async Patterns](./async-patterns.md)

---

## 🏃 Fast Track (Already Know OOP)

Skip to patterns in this order:
1. [Factory](./06-design-patterns/factory.md) (30 min)
2. [Singleton](./06-design-patterns/singleton.md) (20 min)
3. [Builder](./06-design-patterns/builder.md) (30 min)
4. [Adapter](./06-design-patterns/adapter.md) (30 min)
5. [Decorator](./06-design-patterns/decorator.md) (40 min)
6. [Facade](./06-design-patterns/facade.md) (30 min)
7. [Proxy](./06-design-patterns/proxy.md) (30 min)

Then: [Practice Problems](./07-practice-problems/)

---

## 📖 Documentation Navigation

### README Files (Start Here)
- [`low-level-design/README.md`](./README.md) - Main overview
- [`03-oop-fundamentals/README.md`](./03-oop-fundamentals/README.md) - OOP overview
- [`06-design-patterns/README.md`](./06-design-patterns/README.md) - Patterns overview

### Learning Paths
- [`LEARNING-GUIDE.md`](./LEARNING-GUIDE.md) - Detailed learning path with checkpoints
- This file - Quick navigation reference

### Multi-Language Support
- [`03-oop-fundamentals/four-pillars/`](./03-oop-fundamentals/four-pillars/) - Python, Go, Java, JavaScript
- [`03-oop-fundamentals/classes-and-objects/`](./03-oop-fundamentals/classes-and-objects/) - Python, Go, Java, JavaScript

---

## 🎯 Interview Prep Checklists

### 1 Week Before Interview
- [ ] Review all [SOLID principles](./04-design-principles/solid.md)
- [ ] Can explain when to use [Factory](./06-design-patterns/factory.md) vs [Builder](./06-design-patterns/builder.md)
- [ ] Understand [Decorator](./06-design-patterns/decorator.md) vs [Proxy](./06-design-patterns/proxy.md) vs [Adapter](./06-design-patterns/adapter.md)
- [ ] Solve 2-3 problems from [`07-practice-problems/`](./07-practice-problems/)

### 1 Day Before Interview
- [ ] Review [LEARNING-GUIDE.md](./LEARNING-GUIDE.md) checkpoints
- [ ] Practice explaining designs out loud
- [ ] Review your own solutions to practice problems

---

## 💡 Tips for Navigation

1. **Bookmark these files:**
   - [`LEARNING-GUIDE.md`](./LEARNING-GUIDE.md) - Natural learning order
   - [`NAVIGATION.md`](./NAVIGATION.md) - This file (quick reference)
   - [`06-design-patterns/README.md`](./06-design-patterns/README.md) - Pattern overview

2. **Use CMD/CTRL+F** to search within files

3. **Follow the README files** - They guide you through each section

4. **Check the "Related Patterns" section** at the bottom of each pattern file

---

## 🆘 Help! I'm Stuck

### "I don't understand Composition vs Aggregation"
→ Read [`relationships.md`](./03-oop-fundamentals/relationships.md) - has clear examples

### "When do I use Factory vs Builder?"
→ Check [`factory.md#comparison`](./06-design-patterns/factory.md) and [`builder.md`](./06-design-patterns/builder.md)

### "What's the difference between Adapter and Decorator?"
→ Both files have comparison sections:
  - [`adapter.md#comparison`](./06-design-patterns/adapter.md)
  - [`decorator.md#comparison`](./06-design-patterns/decorator.md)

### "I need to learn async/concurrency fast"
→ [`async-patterns.md`](./async-patterns.md) - Start with section 1 (basics)

---

## 🚀 Quick Start

**Absolute Beginner?**
→ [`LEARNING-GUIDE.md`](./LEARNING-GUIDE.md) then [`03-oop-fundamentals/classes-and-objects/`](./03-oop-fundamentals/classes-and-objects/)

**Know OOP, need patterns?**
→ [`06-design-patterns/README.md`](./06-design-patterns/README.md) then start with [`factory.md`](./06-design-patterns/factory.md)

**Interview in 1 week?**
→ Review [`LEARNING-GUIDE.md#2-week-interview-prep`](./LEARNING-GUIDE.md) + solve 3-4 practice problems

**Just browsing?**
→ Check out [`async-patterns.md`](./async-patterns.md) - newest content!

---

Happy learning! 🎓

[Back to Main README](./README.md) | [Go to Learning Guide](./LEARNING-GUIDE.md)

### Python Language Features ⭐ NEW!
| Need | Topic | File |
|------|-------|------|
| Collections (defaultdict, Counter, deque) | Data structures | [`python-must-knows.md`](./python-must-knows.md#1-collections--data-structures) |
| List/Dict comprehensions | Transform data | [`python-must-knows.md`](./python-must-knows.md#2-list--dictionary-comprehensions) |
| Generators & yield | Memory efficiency | [`python-must-knows.md`](./python-must-knows.md#3-generators--iterators) |
| @lru_cache, @dataclass | Decorators | [`python-must-knows.md`](./python-must-knows.md#4-decorators--functools) |

