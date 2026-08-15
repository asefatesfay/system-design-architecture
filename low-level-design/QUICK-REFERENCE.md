# Quick Reference Card

Print this or keep it open while studying! One-page overview of key concepts.

## 🎯 The 4 Pillars of OOP

| Pillar | What | Example |
|--------|------|---------|
| **Encapsulation** | Hide internal details | Private attributes, getters/setters |
| **Abstraction** | Hide complexity | Abstract classes, interfaces |
| **Inheritance** | Reuse code | `class Dog(Animal)` |
| **Polymorphism** | Same interface, different behavior | Method overriding |

## 🔒 SOLID Principles (Critical!)

| Letter | Principle | Remember This |
|--------|-----------|---------------|
| **S** | Single Responsibility | One class, one job |
| **O** | Open/Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subclass should work where parent works |
| **I** | Interface Segregation | Many small interfaces > one big interface |
| **D** | Dependency Inversion | Depend on abstractions, not concrete classes |

## 🎨 Design Patterns At a Glance

### Creational (Object Creation)

| Pattern | One-Liner | When to Use |
|---------|-----------|-------------|
| **Factory** | Create objects without specifying class | Multiple types (Car, Truck, Bus) |
| **Singleton** | Only one instance | DB connection, logger, config |
| **Builder** | Step-by-step construction | Many optional parameters |

### Structural (Object Composition)

| Pattern | One-Liner | When to Use |
|---------|-----------|-------------|
| **Adapter** | Make incompatible interfaces compatible | Integrate third-party API |
| **Decorator** | Add behavior dynamically | Logging, caching, validation |
| **Facade** | Simplify complex subsystem | Hide complexity from client |
| **Proxy** | Control access to object | Lazy loading, access control, caching |

## 🔗 Class Relationships

| Type | Strength | Lifetime | Example | UML |
|------|----------|----------|---------|-----|
| **Dependency** | Weakest | Temporary | Method parameter | `----→` |
| **Association** | Weak | Independent | Teacher knows Students | `────→` |
| **Aggregation** | Medium | Independent | Team has Players | `◇───→` |
| **Composition** | Strong | Dependent | Car owns Engine | `♦───→` |

## 🐍 Python-Specific

### Access Modifiers
```python
self.public          # Anyone can access
self._protected      # Convention: internal use
self.__private       # Name mangling
```

### Special Methods (Dunder)
```python
__init__()           # Constructor
__str__()            # User-friendly string (print)
__repr__()           # Developer string (debug)
__eq__()             # Equality (==)
__lt__()             # Less than (<)
__len__()            # Length (len())
__getitem__()        # Index access ([])
__call__()           # Make callable ()
```

### Decorators
```python
@property            # Getter
@attr.setter         # Setter
@staticmethod        # No self/cls
@classmethod         # Receives cls
@abstractmethod      # Must override
```

## ⚡ Async Quick Reference

```python
# Define async function
async def func():
    await operation()

# Run async function
asyncio.run(func())

# Run concurrently
await asyncio.gather(op1(), op2(), op3())

# Timeout
await asyncio.wait_for(operation(), timeout=5.0)

# Queue
queue = asyncio.Queue()
await queue.put(item)
item = await queue.get()
```

## 🎯 Pattern Comparison

### Factory vs Builder
- **Factory**: One step, create complete object → `factory.create('car')`
- **Builder**: Multiple steps, configure → `builder.setEngine().setColor().build()`

### Adapter vs Decorator vs Proxy
- **Adapter**: Changes interface → Makes old API work with new code
- **Decorator**: Adds behavior → Wraps to add logging/caching
- **Proxy**: Controls access → Lazy loading, security check

### Composition vs Inheritance
- **Inheritance**: "is-a" → `Dog is-a Animal`
- **Composition**: "has-a" → `Car has-a Engine`
- **Rule**: Favor composition over inheritance

## 📝 Interview Checklist

### Before Coding
- [ ] Clarify requirements (ask questions!)
- [ ] Identify main entities (classes)
- [ ] Define relationships
- [ ] Consider SOLID principles

### While Coding
- [ ] Start simple, extend later
- [ ] Use meaningful names
- [ ] Apply appropriate patterns
- [ ] Explain your decisions

### After Coding
- [ ] Review for SOLID violations
- [ ] Consider edge cases
- [ ] Discuss trade-offs
- [ ] Suggest improvements

## 🚨 Common Mistakes to Avoid

❌ Forcing patterns where not needed
❌ Over-engineering simple problems
❌ Not following SOLID principles
❌ Tight coupling between classes
❌ God objects (doing too much)
❌ Using Singleton for everything
❌ Deep inheritance hierarchies (>3 levels)

## ✅ Best Practices

✅ Single Responsibility - one class, one job
✅ Composition over Inheritance
✅ Program to interfaces, not implementations
✅ Encapsulate what varies
✅ Keep it simple (KISS)
✅ Don't repeat yourself (DRY)
✅ Use meaningful names

## 📚 Pattern Selection Flowchart

```
Need to create objects?
├─ Multiple types? → Factory
├─ Only one instance? → Singleton
└─ Complex construction? → Builder

Need to connect objects?
├─ Incompatible interfaces? → Adapter
├─ Add features dynamically? → Decorator
├─ Simplify complex system? → Facade
└─ Control access? → Proxy

Objects changing behavior?
├─ Based on state? → State (not covered yet)
├─ Multiple algorithms? → Strategy (not covered yet)
└─ Notify observers? → Observer (not covered yet)
```

## 🎓 Study Order

1. **OOP Basics** → Classes, Objects, Four Pillars
2. **SOLID** → Critical for explaining designs
3. **Factory** → Most common creation pattern
4. **Decorator** → Very flexible, common in Python
5. **Adapter** → Real-world API integration
6. **Other Patterns** → Singleton, Builder, Facade, Proxy
7. **Practice** → Parking Lot, LRU Cache, Elevator

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Read one pattern | 20-30 min |
| Practice one pattern | 30-60 min |
| Solve practice problem | 60-90 min |
| Full pattern review | 3-4 hours |
| Complete prep (8 weeks) | 100-120 hours |

## 🔗 Quick Links

- [Learning Guide](./LEARNING-GUIDE.md) - Natural learning path
- [Navigation](./NAVIGATION.md) - Find what you need
- [OOP Fundamentals](./03-oop-fundamentals/) - Start here if new
- [Design Patterns](./06-design-patterns/) - Essential patterns
- [Async Patterns](./async-patterns.md) - Concurrency
- [Practice Problems](./07-practice-problems/) - Apply knowledge

---

## 💡 One-Line Summaries

**OOP**: Bundle data and methods together, control access, reuse code

**SOLID**: Principles for maintainable, flexible, testable code

**Factory**: "Give me an Animal" → Returns Dog/Cat/Bird

**Singleton**: "Only one instance allowed" → DB connection pool

**Builder**: "Construct step-by-step" → Pizza with toppings

**Adapter**: "Make it fit" → Plug adapter for different outlets

**Decorator**: "Add features" → Gift wrapping adds layers

**Facade**: "Simplify interface" → Remote control hides TV complexity

**Proxy**: "Gatekeeper" → Security guard controls access

**Composition**: "Has-a" → Car has Engine

**Inheritance**: "Is-a" → Dog is Animal

---

**Print this page and keep it handy while coding!** 📄

[Back to Main](./README.md) | [Learning Guide](./LEARNING-GUIDE.md) | [Navigation](./NAVIGATION.md)
