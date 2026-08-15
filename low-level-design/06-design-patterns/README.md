# Design Patterns

> **🌍 Multi-Language Support:** Design patterns work in all languages:
> - **Python, Go, Java, JavaScript** - See [Language Comparison - Design Patterns](../lld-coding/multi-language/LANGUAGE-COMPARISON.md#4-design-patterns-syntax)
> - **Strategy Pattern Examples** - See [strategy.md](./strategy.md) and [Four Pillars - Abstraction](../03-oop-fundamentals/four-pillars/#2-abstraction)
> - **Observer Pattern Examples** - See [observer.md](./observer.md)
> - **Complete Implementations** - [Interview Walkthroughs Multi-Language](../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md)

Design patterns are proven solutions to recurring problems in software design. For LLD interviews, you need to know the most commonly used patterns.

## Why Design Patterns Matter

1. **Common vocabulary**: "Let's use Strategy pattern" - everyone understands
2. **Proven solutions**: Battle-tested approaches
3. **Interview expectation**: You'll be asked about them
4. **Better design**: Make code more maintainable and flexible

## Design Patterns in This Guide

### ✅ Creational Patterns (Object Creation)
1. **[Singleton](./singleton.md)** ⭐⭐⭐ - Ensure only one instance exists
   - Thread-safe implementations
   - Metaclass approach
   - Module-level singleton (Pythonic way)

2. **[Factory](./factory.md)** ⭐⭐⭐ - Create objects without specifying exact class
   - Simple Factory
   - Factory Method
   - Abstract Factory

3. **[Builder](./builder.md)** ⭐⭐ - Construct complex objects step-by-step
   - Fluent interface
   - Method chaining
   - Validation

### ✅ Structural Patterns (Object Composition)
4. **[Adapter](./adapter.md)** ⭐⭐ - Make incompatible interfaces work together
   - Object adapter (composition)
   - Class adapter (inheritance)
   - Real-world API integration

5. **[Decorator](./decorator.md)** ⭐⭐⭐ - Add behavior dynamically
   - Classic decorator pattern
   - Python @decorator syntax
   - Logging, caching, validation

6. **[Facade](./facade.md)** ⭐⭐ - Simplified interface to complex subsystem
   - Hide complexity
   - Subsystem coordination
   - Common operations

7. **[Proxy](./proxy.md)** ⭐⭐ - Control access to objects
   - Virtual proxy (lazy loading)
   - Protection proxy (access control)
   - Remote proxy
   - Caching proxy

### 📋 Additional Patterns (Coming Soon)
- **Composite** - Tree structures (files/folders)
- **Strategy** - Switch algorithms at runtime
- **Observer** - Event notification
- **State** - Behavior changes with state
- **Command** - Encapsulate requests
- **Template Method** - Algorithm skeleton

## Pattern Categories

```
Creational (How objects are created)
├── Singleton          ⭐ Very common
├── Factory Method     ⭐ Very common
├── Abstract Factory
├── Builder
└── Prototype

Structural (How objects are composed)
├── Decorator          ⭐ Common
├── Facade             ⭐ Common
├── Composite          ⭐ Common
├── Adapter
├── Bridge
├── Flyweight
└── Proxy

Behavioral (How objects interact)
├── Strategy           ⭐⭐⭐ Most common!
├── Observer           ⭐⭐⭐ Most common!
├── State              ⭐ Common
├── Command            ⭐ Common
├── Template Method    ⭐ Common
├── Chain of Responsibility
├── Iterator
├── Mediator
├── Memento
└── Visitor

⭐⭐⭐ = Critical for interviews
⭐ = Common in interviews
```

## Quick Pattern Selection Guide

### When to Use Each Pattern

| Problem | Pattern | Example |
|---------|---------|---------|
| Need only one instance | Singleton | Database connection pool |
| Create different types of objects | Factory | Vehicle factory (Car, Truck, Bus) |
| Add features dynamically | Decorator | Coffee with milk, sugar |
| Hide complex subsystem | Facade | Payment processing facade |
| Tree-like structures | Composite | File system (files and folders) |
| Different ways to do same thing | Strategy | Sorting algorithms, payment methods |
| Notify multiple objects | Observer | Newsletter subscribers |
| Behavior depends on state | State | Order states (Pending, Shipped, Delivered) |
| Undo/redo operations | Command | Text editor commands |
| Steps are same, details differ | Template Method | Data processing pipeline |
| Request through multiple handlers | Chain of Responsibility | Approval workflow |

## Pattern Comparison

### Strategy vs State
```python
# Strategy: Client chooses algorithm
payment_processor = PaymentProcessor(CreditCardStrategy())  # Client picks

# State: Object changes its own behavior
order = Order()  # Order changes state internally
order.ship()     # Moves to SHIPPED state automatically
```

### Decorator vs Inheritance
```python
# Inheritance: Static, compile-time
class MilkCoffee(Coffee):  # Fixed combination

# Decorator: Dynamic, runtime
coffee = SimpleCoffee()
coffee = MilkDecorator(coffee)      # Can add/remove at runtime
coffee = SugarDecorator(coffee)
```

### Factory vs Builder
```python
# Factory: Create complete object in one step
car = VehicleFactory.create("car")

# Builder: Construct complex object step-by-step
car = CarBuilder()
    .set_engine("V8")
    .set_color("red")
    .set_wheels(4)
    .build()
```

## Interview Tips

### How to Discuss Patterns

**❌ Don't say**: "I used Strategy pattern because it's cool"

**✅ Do say**: "I used Strategy pattern here because we have multiple payment methods (credit card, PayPal, UPI) and the client needs to choose at runtime. This follows the Open/Closed Principle - we can add new payment methods without modifying existing code."

### When Asked "Which Pattern Would You Use?"

**Good Answer Structure**:
1. **Understand the problem**: "So we need to..."
2. **Identify the core need**: "The key requirement is..."
3. **Suggest pattern**: "I'd use [Pattern] because..."
4. **Explain benefits**: "This gives us [flexibility/extensibility/etc.]"
5. **Discuss alternatives**: "We could also consider [Other Pattern], but..."

### Common Interview Questions

1. **"What's the difference between Strategy and State?"**
   - Strategy: Client decides which algorithm
   - State: Object changes behavior based on internal state

2. **"When would you use Singleton?"**
   - Database connection pool, logger, configuration manager
   - But mention: Can make testing harder, consider alternatives

3. **"How does Decorator differ from inheritance?"**
   - Decorator: Dynamic, runtime, can combine multiple
   - Inheritance: Static, compile-time, single parent

4. **"Why use Factory pattern?"**
   - Decouple object creation from usage
   - Single place to control object creation
   - Easy to extend with new types

## Recommended Learning Path

### Phase 1: Creational Patterns (Start Here!)
1. **[Factory](./factory.md)** - Most versatile creation pattern
   - Start with Simple Factory
   - Then Factory Method
   - Finally Abstract Factory

2. **[Singleton](./singleton.md)** - Common but often misused
   - Understand when to use
   - Thread-safety concerns
   - Alternatives (dependency injection)

3. **[Builder](./builder.md)** - Complex object construction
   - Fluent interfaces
   - Validation
   - Immutable objects

### Phase 2: Structural Patterns
4. **[Adapter](./adapter.md)** - Integration essential
   - Third-party API integration
   - Legacy code integration

5. **[Decorator](./decorator.md)** - Very flexible pattern
   - Both OOP pattern and Python syntax
   - Logging, caching examples
   - Stacking decorators

6. **[Facade](./facade.md)** - Simplification pattern
   - Hide subsystem complexity
   - Common in large systems

7. **[Proxy](./proxy.md)** - Access control
   - Lazy loading (performance)
   - Access control (security)
   - Caching (optimization)

## Practice Exercise

**Design a Coffee Shop Ordering System**

Apply the patterns you've learned:
- **Factory**: Create different coffee types (Espresso, Latte, Cappuccino)
- **Builder**: Build complex orders step-by-step with customizations
- **Decorator**: Add extras dynamically (Milk, Sugar, Whipped Cream, Caramel)
- **Singleton**: Coffee shop configuration/settings
- **Facade**: Simplify the ordering process (hide payment, inventory, preparation)
- **Proxy**: Lazy load customer loyalty data, control access to premium features

Try designing this yourself before looking at pattern implementations!

## Pattern Anti-Patterns

### When NOT to Use Patterns

❌ **Don't**: Force patterns where they don't fit
✅ **Do**: Use patterns when they solve a real problem

❌ **Don't**: Use Singleton for everything
✅ **Do**: Consider dependency injection instead

❌ **Don't**: Create patterns for premature optimization
✅ **Do**: Refactor to patterns when need arises

## Quick Reference

### One-Line Pattern Summaries

- **Singleton**: One instance only
- **Factory**: Create objects without specifying class
- **Decorator**: Wrap object to add features
- **Facade**: Simple interface to complex system
- **Composite**: Tree of objects treated uniformly
- **Strategy**: Switchable algorithms
- **Observer**: Notify multiple subscribers
- **State**: Behavior changes with state
- **Command**: Requests as objects
- **Template Method**: Override steps of algorithm
- **Chain of Responsibility**: Pass request through handlers

## Next Steps

### Start Here (Natural Learning Order)

**Phase 1 - Creational Patterns:**
1. [Factory Pattern →](./factory.md) - Master object creation first
2. [Singleton Pattern →](./singleton.md) - Simple but important
3. [Builder Pattern →](./builder.md) - Complex object construction

**Phase 2 - Structural Patterns:**
4. [Adapter Pattern →](./adapter.md) - Integration problems
5. [Decorator Pattern →](./decorator.md) - Adding behavior
6. [Facade Pattern →](./facade.md) - Simplification
7. [Proxy Pattern →](./proxy.md) - Access control

### Before Moving On

Make sure you can:
- ✅ Explain WHEN to use each pattern
- ✅ Identify patterns in real code
- ✅ Implement patterns without reference
- ✅ Compare similar patterns (e.g., Proxy vs Decorator vs Adapter)

---

**Remember**: Understanding WHEN to use a pattern is more important than memorizing HOW to implement it!
