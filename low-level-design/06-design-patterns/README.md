# Design Patterns

> **🌍 Multi-Language Support:** Design patterns work in all languages:
> - **Python, Go, Java, JavaScript** - See [Language Comparison - Design Patterns](../lld-coding/multi-language/LANGUAGE-COMPARISON.md#4-design-patterns-syntax)
> - **Strategy Pattern Examples** - See [strategy.md](./strategy.md) and [Four Pillars - Abstraction](../03-oop-fundamentals/four-pillars.md#2-abstraction)
> - **Observer Pattern Examples** - See [observer.md](./observer.md)
> - **Complete Implementations** - [Interview Walkthroughs Multi-Language](../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md)

Design patterns are proven solutions to recurring problems in software design. For LLD interviews, you need to know the most commonly used patterns.

## Why Design Patterns Matter

1. **Common vocabulary**: "Let's use Strategy pattern" - everyone understands
2. **Proven solutions**: Battle-tested approaches
3. **Interview expectation**: You'll be asked about them
4. **Better design**: Make code more maintainable and flexible

## The 10 Essential Patterns for Interviews

### Creational Patterns (Object Creation)
1. **[Singleton](./singleton.md)** - Ensure only one instance exists
2. **[Factory Method](./factory.md)** - Create objects without specifying exact class

### Structural Patterns (Object Composition)
3. **[Decorator](./decorator.md)** - Add behavior without modifying class
4. **[Facade](./facade.md)** - Simplified interface to complex subsystem
5. **[Composite](./composite.md)** - Tree structures (files/folders)

### Behavioral Patterns (Object Interaction)
6. **[Strategy](./strategy.md)** - Switch between algorithms at runtime
7. **[Observer](./observer.md)** - Notify multiple objects of changes
8. **[State](./state.md)** - Object behavior changes with state
9. **[Command](./command.md)** - Encapsulate requests as objects
10. **[Template Method](./template-method.md)** - Define algorithm skeleton
11. **[Chain of Responsibility](./chain-of-responsibility.md)** - Pass request through chain

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

## Learning Path

### Week 1: Master These First (Most Common)
1. **Strategy** - Payment methods, sorting algorithms
2. **Observer** - Event notification systems
3. **Factory** - Object creation

### Week 2: Important Patterns
4. **Singleton** - Single instance
5. **Decorator** - Add features dynamically
6. **Facade** - Simplify complex systems

### Week 3: Complete Your Knowledge
7. **State** - Object state management
8. **Command** - Undo/redo functionality
9. **Composite** - Tree structures
10. **Template Method** - Algorithm skeleton

## Practice Exercise

**Design a Coffee Shop Ordering System**

Apply these patterns:
- **Factory**: Create different coffee types (Espresso, Latte, Cappuccino)
- **Decorator**: Add extras (Milk, Sugar, Whipped Cream)
- **Strategy**: Different pricing strategies (Regular, Happy Hour, Member)
- **Observer**: Notify kitchen when order placed
- **Singleton**: Coffee shop itself

Try it yourself before looking at solutions!

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

Start with the most important pattern for interviews:
**[Strategy Pattern →](./strategy.md)**

Then move through the patterns in order of importance.

---

**Remember**: Understanding WHEN to use a pattern is more important than memorizing HOW to implement it!
