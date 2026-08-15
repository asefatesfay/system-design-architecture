# Low-Level Design (LLD) - Complete Learning Path

Welcome to your comprehensive guide to mastering Low-Level Design! This resource will take you from zero to interview-ready with structured content, practical examples, and hands-on problems.

## 🧭 Navigation Guides (NEW!)

**Choose your path:**
- 📖 **[LEARNING-GUIDE.md](./LEARNING-GUIDE.md)** - Natural learning path with checkpoints (Recommended!)
- 📍 **[NAVIGATION.md](./NAVIGATION.md)** - Quick topic finder and directory structure
- 📄 **[QUICK-REFERENCE.md](./QUICK-REFERENCE.md)** - One-page cheat sheet (print this!)

## 🌍 Multi-Language Support

**All examples now available in Python, Go, Java, and JavaScript!**

- **Python** 🐍 - Most common for interviews (Google, Meta, startups)
- **Go** 🔷 - Systems roles (Google, Uber, cloud companies)
- **Java** ☕ - Enterprise (Amazon, Microsoft, banks)
- **JavaScript** 💛 - Full-stack/web roles

**Key Multi-Language Resources:**
- [Four Pillars of OOP - All Languages](./03-oop-fundamentals/four-pillars/) ⭐⭐⭐
- [Classes and Objects - All Languages](./03-oop-fundamentals/classes-and-objects/) ⭐⭐⭐
- [Complete Interview Walkthroughs - Multi-Language](./COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md) ⭐⭐⭐
- [Language Comparison Guide](./lld-coding/multi-language/LANGUAGE-COMPARISON.md) ⭐⭐⭐

## 📚 What You'll Learn

This guide covers everything you need to excel in LLD interviews at top tech companies like Google, Amazon, Meta, Microsoft, and leading startups.

## 🗺️ Learning Path

Follow this structured path to build your LLD skills systematically:

### 1. [Introduction](./01-introduction/)
- What is Low-Level Design?
- LLD vs High-Level Design (System Design)
- Why LLD matters for your career

### 2. [Interview Types](./02-interview-types/)
- Object-Oriented Design Interviews
- Machine Coding Rounds
- Concurrency Design Questions

### 3. [OOP Fundamentals](./03-oop-fundamentals/) ⭐⭐⭐
Essential foundation - master these first!
- **[Classes and Objects](./03-oop-fundamentals/classes-and-objects/)** - Building blocks
- **[Four Pillars](./03-oop-fundamentals/four-pillars/)** - Encapsulation, Abstraction, Inheritance, Polymorphism
- **[Special Methods](./03-oop-fundamentals/special-methods.md)** - Python dunder methods (`__init__`, `__str__`, etc.)
- **[Interfaces & Abstract Classes](./03-oop-fundamentals/interfaces-abstract-classes.md)** - Define contracts
- **[Access Modifiers](./03-oop-fundamentals/access-modifiers.md)** - Public, protected, private
- **[Relationships](./03-oop-fundamentals/relationships.md)** - Association, Aggregation, Composition, Dependency

### 4. [Design Principles](./04-design-principles/)
- DRY, KISS, YAGNI
- Law of Demeter
- Coupling and Cohesion
- **[SOLID Principles](./04-design-principles/solid.md)** ⭐⭐⭐ Critical for interviews!

### 5. [UML Diagrams](./05-uml-diagrams/)
- Class Diagrams
- Use Case Diagrams
- Sequence Diagrams

### 6. [Design Patterns](./06-design-patterns/) ⭐⭐⭐
Master the essential patterns - all with complete implementations:

**Creational Patterns (Object Creation):**
1. **[Factory](./06-design-patterns/factory.md)** - Create objects without specifying class
2. **[Singleton](./06-design-patterns/singleton.md)** - Ensure only one instance exists
3. **[Builder](./06-design-patterns/builder.md)** - Construct complex objects step-by-step

**Structural Patterns (Object Composition):**
4. **[Adapter](./06-design-patterns/adapter.md)** - Make incompatible interfaces work together
5. **[Decorator](./06-design-patterns/decorator.md)** - Add behavior dynamically
6. **[Facade](./06-design-patterns/facade.md)** - Simplified interface to complex subsystem
7. **[Proxy](./06-design-patterns/proxy.md)** - Control access to objects

**Behavioral Patterns (Coming Soon):**
- Strategy, Observer, State, Command, Template Method

### 6.5 [Async Patterns](./async-patterns.md) ⭐ NEW!
Modern Python asynchronous programming:
- `async`/`await` fundamentals
- Producer-Consumer with asyncio
- Async context managers and iterators
- Rate limiting, retry patterns, worker pools
- Threading vs Asyncio comparison

### 7. [Practice Problems](./07-practice-problems/)
Real interview questions with complete solutions:
1. Parking Lot System
2. Vending Machine
3. Elevator System
4. LRU Cache
5. Chess Game
6. Snake and Ladders
7. Splitwise
8. Logging Framework
9. Hotel Management System
10. Movie Ticket Booking System

## 🎯 How to Use This Guide

### For Beginners
1. **Start here**: [LEARNING-GUIDE.md](./LEARNING-GUIDE.md) - Follow the natural path
2. **Sequential Learning**: Don't skip sections - each builds on previous
3. **Hands-On Practice**: Code every example, don't just read
4. **Use Checkpoints**: Verify understanding before moving on

### For Experienced Developers
1. **Quick Assessment**: Review [QUICK-REFERENCE.md](./QUICK-REFERENCE.md)
2. **Identify Gaps**: Use [NAVIGATION.md](./NAVIGATION.md) to find weak areas
3. **Deep Dive**: Focus on patterns you don't know well
4. **Practice**: Jump to [Practice Problems](./07-practice-problems/)

### For Interview Prep
1. **1 Week Out**: Review [SOLID](./04-design-principles/solid.md) and [Design Patterns](./06-design-patterns/)
2. **3 Days Out**: Solve 2-3 [Practice Problems](./07-practice-problems/)
3. **1 Day Out**: Review [QUICK-REFERENCE.md](./QUICK-REFERENCE.md) cheat sheet
4. **Morning Of**: Relax, review pattern comparisons

## 📖 Recommended Study Plan

### 8-Week Complete Preparation

**Week 1-2: OOP Foundations**
- Day 1-3: [Classes and Objects](./03-oop-fundamentals/classes-and-objects/) + [Four Pillars](./03-oop-fundamentals/four-pillars/)
- Day 4-5: [Special Methods](./03-oop-fundamentals/special-methods.md) + [Interfaces](./03-oop-fundamentals/interfaces-abstract-classes.md)
- Day 6-7: [Access Modifiers](./03-oop-fundamentals/access-modifiers.md) + [Relationships](./03-oop-fundamentals/relationships.md)
- Checkpoint: Can you design a simple Library system?

**Week 3: Creational Patterns**
- Day 1-2: [Factory Pattern](./06-design-patterns/factory.md) - All three types
- Day 3-4: [Singleton Pattern](./06-design-patterns/singleton.md) - Thread-safety
- Day 5-7: [Builder Pattern](./06-design-patterns/builder.md) + Practice
- Checkpoint: Know when to use Factory vs Builder vs Singleton?

**Week 4: Structural Patterns**
- Day 1-2: [Adapter Pattern](./06-design-patterns/adapter.md)
- Day 3-4: [Decorator Pattern](./06-design-patterns/decorator.md)
- Day 5: [Facade Pattern](./06-design-patterns/facade.md)
- Day 6-7: [Proxy Pattern](./06-design-patterns/proxy.md)
- Checkpoint: Can you explain differences between Adapter/Decorator/Proxy?

**Week 5: Advanced & Review**
- Day 1-3: [Async Patterns](./async-patterns.md) (if needed for role)
- Day 4-5: Compare patterns, review SOLID
- Day 6-7: Pattern selection practice
- Checkpoint: Can you choose right pattern for a problem?

**Week 6-7: Practice Problems**
- Week 6: Parking Lot, LRU Cache, Vending Machine
- Week 7: Elevator System, Chess Game, Splitwise
- Time yourself: 60 min for design, 90 min for full code
- Checkpoint: Can you complete Parking Lot in 60 minutes?

**Week 8: Mock Interviews & Polish**
- Day 1-3: Mock interviews with peers
- Day 4-5: Review feedback, strengthen weak areas
- Day 6-7: Final review of [QUICK-REFERENCE.md](./QUICK-REFERENCE.md)

### 4-Week Crash Course (Know OOP)

**Week 1:** All 7 design patterns
**Week 2:** Async patterns + pattern comparisons
**Week 3-4:** 6-8 practice problems

### 2-Week Final Prep (Review Only)

**Week 1:** Review patterns, solve 3-4 problems
**Week 2:** Mock interviews, weak area focus

## 🎓 Success Tips

1. **Think Before Coding**: Always clarify requirements and design first
2. **Start Simple**: Begin with core functionality, then extend
3. **Explain Your Reasoning**: Interviewers care more about your thought process than perfect code
4. **Consider Trade-offs**: Every design decision has pros and cons
5. **Use SOLID**: Reference SOLID principles when explaining your design
6. **Don't Force Patterns**: Use patterns only when they genuinely improve the design
7. **Practice Out Loud**: Explain designs verbally, not just in your head

## 🔧 Prerequisites

- Basic programming knowledge in an OOP language
- Understanding of data structures (Arrays, Lists, Maps, Sets)
- Familiarity with basic algorithms

## 🚀 Quick Start

```bash
# 1. Read the learning guide
cat LEARNING-GUIDE.md

# 2. Start with OOP fundamentals
cd 03-oop-fundamentals/classes-and-objects

# 3. Follow the natural progression
# (See LEARNING-GUIDE.md for complete path)
```

## 📝 Daily Practice Schedule

- **Daily**: 1-2 hours on LLD
- **Theory Days** (Mon, Wed, Fri): OOP, Principles, Patterns
- **Practice Days** (Tue, Thu, Sat): Code problems, review solutions
- **Review Day** (Sun): Compare patterns, refactor code, mock interview

## 🎯 Interview Preparation Checklist

### OOP Fundamentals ✅
- [ ] Can explain all 4 pillars with examples
- [ ] Know difference between composition and inheritance
- [ ] Understand when to use abstract classes vs interfaces
- [ ] Can design proper class relationships

### Design Principles ✅
- [ ] Can explain all SOLID principles
- [ ] Can identify SOLID violations in code
- [ ] Know when to apply each principle

### Design Patterns ✅
- [ ] Know when to use Factory vs Builder vs Singleton
- [ ] Understand Adapter vs Decorator vs Proxy differences
- [ ] Can implement patterns without reference
- [ ] Know when NOT to use patterns

### Practice & Interview Skills ✅
- [ ] Solved at least 6-8 LLD problems
- [ ] Can complete Parking Lot in 60 minutes
- [ ] Practice explaining designs out loud
- [ ] Can draw UML diagrams quickly
- [ ] Comfortable discussing trade-offs

## 💡 Pro Tips

### Pattern Selection
- **Don't memorize** - Understand when and why
- **Compare similar patterns** - Know the differences
- **Real-world examples** - Connect to actual use cases

### Interview Strategy
- **Ask questions first** - Clarify requirements
- **Design before code** - Sketch classes and relationships
- **Start simple** - Core functionality first, extend later
- **Explain as you go** - Talk through your decisions

### Common Pitfalls to Avoid
❌ Forcing patterns where not needed
❌ Over-engineering simple problems
❌ Not following SOLID principles
❌ Skipping requirement clarification
❌ Tight coupling between classes

## 🆘 Need Help?

### Stuck on a concept?
- Check [NAVIGATION.md](./NAVIGATION.md) for quick topic lookup
- Review related patterns in the "Related Patterns" section
- Read the "Interview Tips" in each pattern file

### Don't know which pattern?
- Review [Pattern Comparison](./06-design-patterns/README.md#pattern-comparison)
- Check [QUICK-REFERENCE.md](./QUICK-REFERENCE.md) flowchart
- Read "When to Use" section in each pattern

### Running out of time?
- Focus on: SOLID, Factory, Decorator, Adapter
- Solve: Parking Lot, LRU Cache, Vending Machine
- Review: [QUICK-REFERENCE.md](./QUICK-REFERENCE.md)

## 📚 Additional Resources

- Each section has detailed explanations and code examples
- Practice problems include multiple solution approaches
- UML diagrams accompany complex designs
- Pattern files include interview tips and best practices
- All examples are runnable Python code

## 🤝 Contributing

Found an error or want to add more examples? Feel free to contribute!

---

## 🎉 You're Ready!

Choose your starting point:
- 👉 **Absolute Beginner?** → [LEARNING-GUIDE.md](./LEARNING-GUIDE.md)
- 👉 **Know OOP?** → [Design Patterns](./06-design-patterns/)
- 👉 **Need Quick Review?** → [QUICK-REFERENCE.md](./QUICK-REFERENCE.md)
- 👉 **Looking for Something?** → [NAVIGATION.md](./NAVIGATION.md)

---

**Happy Learning! 🚀**

*Remember: Understanding WHEN to use a pattern is more important than memorizing HOW to implement it!*

[Start Your Journey →](./LEARNING-GUIDE.md)
