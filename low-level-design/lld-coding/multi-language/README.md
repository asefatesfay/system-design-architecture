# Multi-Language LLD Examples

Side-by-side implementations of Low-Level Design examples in Python, Go, Java, and JavaScript.

## Why Multiple Languages?

Learning the same concept in different languages helps you:
- ✅ Understand the **underlying principles** (not language-specific syntax)
- ✅ See different approaches to the same problem
- ✅ Choose the best language for your interviews/projects
- ✅ Become language-agnostic in your design thinking

## Language Comparison Quick Reference

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **OOP Style** | Class-based | Struct + methods | Class-based | Prototype/Class-based |
| **Concurrency** | threading, asyncio | goroutines, channels | threads, executors | async/await, workers |
| **Type System** | Dynamic (+ type hints) | Static, strong | Static, strong | Dynamic (+ TypeScript) |
| **Memory** | Garbage collected | Garbage collected | Garbage collected | Garbage collected |
| **Best For** | Rapid dev, scripting | Systems, concurrency | Enterprise, Android | Web, Node.js |
| **Interview Use** | Google, Meta | Google, Uber | Amazon, Microsoft | Frontend, Full-stack |

## Examples Included

### 1. Basic OOP Concepts
- [Basic Classes](./01-basic-classes/) - Classes, objects, constructors
- [Inheritance](./02-inheritance/) - Extending classes
- [Polymorphism](./03-polymorphism/) - Interface/abstract classes

### 2. Concurrency Examples
- [Page View Counter](./04-page-view-counter/) - Race conditions and fixes
- [Producer-Consumer](./05-producer-consumer/) - Buffer with synchronization
- [Connection Pool](./06-connection-pool/) - Real production pattern

### 3. Design Patterns
- [Strategy Pattern](./07-strategy-pattern/) - Payment processors
- [Observer Pattern](./08-observer-pattern/) - Event system
- [Factory Pattern](./09-factory-pattern/) - Object creation

## How to Use

1. **Start with Python** - Most readable, best for learning concepts
2. **Compare with Go** - See how structs + methods work differently
3. **Look at Java** - Classic OOP, verbose but explicit
4. **Check JavaScript** - Prototype-based, modern ES6+ classes

## Running Examples

### Python
```bash
python3 example.py
```

### Go
```bash
go run example.go
```

### Java
```bash
javac Example.java
java Example
```

### JavaScript (Node.js)
```bash
node example.js
```

## Language-Specific Notes

### Python
- `self` is explicit first parameter
- `__init__` for constructor
- Multiple inheritance supported
- Duck typing (if it quacks like a duck...)

### Go
- No classes, use structs with methods
- Composition over inheritance
- Interfaces are implicit
- Goroutines for concurrency (lightweight)

### Java
- Everything is a class
- Explicit interfaces
- Strong type system
- Verbose but IDE-friendly

### JavaScript
- Prototype-based (can use class syntax)
- `this` binding can be tricky
- Async-first with Promises
- Node.js for backend, browser for frontend

## Quick Syntax Comparison

### Defining a Class/Struct

**Python:**
```python
class Dog:
    def __init__(self, name):
        self.name = name
```

**Go:**
```go
type Dog struct {
    Name string
}
```

**Java:**
```java
public class Dog {
    private String name;
    public Dog(String name) {
        this.name = name;
    }
}
```

**JavaScript:**
```javascript
class Dog {
    constructor(name) {
        this.name = name;
    }
}
```

### Thread Safety

**Python:**
```python
import threading
lock = threading.Lock()
with lock:
    # critical section
```

**Go:**
```go
var mutex sync.Mutex
mutex.Lock()
// critical section
mutex.Unlock()
```

**Java:**
```java
synchronized(lock) {
    // critical section
}
```

**JavaScript:**
```javascript
// No built-in locks, use atomics or message passing
// Or use async/await to avoid race conditions
```

## Next Steps

1. Start with `01-basic-classes/` to see fundamental differences
2. Move to `04-page-view-counter/` to understand concurrency
3. Study `06-connection-pool/` for production patterns
4. Pick the language that fits your needs best

---

**Remember**: The design principles (SOLID, patterns) are the same across all languages. Only the syntax and idioms differ!
