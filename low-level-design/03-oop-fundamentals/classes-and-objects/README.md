# Classes and Objects - Multi-Language Guide

Complete guide to classes and objects in **Python, Go, Java, and JavaScript** with language-specific features and best practices.

## 🎯 Overview

Classes and objects are the foundation of Object-Oriented Programming:

- **Class** = Blueprint/Template for creating objects
- **Object** = Instance of a class with specific data

---

## 📚 Choose Your Language

Each language guide includes:
- ✅ Class definition syntax
- ✅ Constructor patterns
- ✅ Instance vs class variables/methods
- ✅ Language-specific features
- ✅ Real-world Movie class example
- ✅ Common patterns and best practices

### [🐍 Python Implementation](./python.md)
**Features:**
- `__init__` constructor
- `self` parameter (explicit)
- `@property`, `@classmethod`, `@staticmethod`
- `__str__` and `__repr__`
- Name mangling for privacy
- `@dataclass` for simple classes

**Best for:** Rapid development, data science, scripting

---

### [🔷 Go Implementation](./go.md)
**Features:**
- `struct` instead of classes
- Constructor functions (`NewTypeName`)
- Methods with receivers
- Uppercase/lowercase visibility
- Package-level variables
- Struct embedding

**Best for:** Systems programming, microservices, performance

---

### [☕ Java Implementation](./java.md)
**Features:**
- Explicit access modifiers
- Constructor overloading
- `static` keyword
- `toString()` method
- `final` for immutability
- Records (Java 14+)

**Best for:** Enterprise applications, Android, large systems

---

### [💛 JavaScript Implementation](./javascript.md)
**Features:**
- ES6 `class` syntax
- `#` private fields (ES2022+)
- Getters/setters
- `static` keyword
- Prototype-based inheritance
- Factory functions as alternative

**Best for:** Web development, Node.js, full-stack

---

## 📊 Quick Comparison

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Class Keyword** | `class` | `type...struct` | `class` | `class` |
| **Constructor** | `__init__(self)` | `NewType()` func | `ClassName()` | `constructor()` |
| **Instance Ref** | `self` (explicit) | Receiver `(t *Type)` | `this` (implicit) | `this` |
| **Privacy** | Convention (`_`, `__`) | Case (lower/Upper) | `private` keyword | `#` prefix (ES2022+) |
| **Class Variables** | Class-level | Package-level | `static` | `static` |
| **Static Methods** | `@staticmethod` | Package functions | `static` methods | `static` methods |

---

## 🎓 Learning Path

### Beginner
1. **Pick your language** based on interview/project needs
2. **Understand class vs object** - blueprint vs instance
3. **Learn constructor syntax** - how to initialize objects
4. **Practice with simple classes** - Person, Book, Counter

### Intermediate
1. **Instance vs class members** - when to use each
2. **Methods and behaviors** - how objects do things
3. **String representation** - making objects printable
4. **Real-world example** - Movie class with features

### Advanced
1. **Private fields** - encapsulation mechanisms
2. **Properties/getters/setters** - controlled access
3. **Design patterns** - Builder, Singleton, Factory
4. **Language-specific features** - leverage unique capabilities

---

## 🔥 Common Interview Questions

### Class Basics
- What's the difference between a class and an object?
- Explain constructors in [language]
- How do you control access to class members?

### Instance vs Class
- What's the difference between instance and class variables?
- When would you use a static method?
- How are class variables shared?

### Language-Specific
- **Python:** Explain `self`, `__init__`, and `__str__`
- **Go:** How do struct methods differ from regular functions?
- **Java:** Explain access modifiers and their scope
- **JavaScript:** What's the difference between `#private` and `_convention`?

---

## 💡 Key Concepts Summary

### Universal Concepts
- **Classes** define structure and behavior
- **Objects** are instances with specific data
- **Constructors** initialize new objects
- **Methods** define behavior
- **Fields/Properties** store state

### Language Differences
- **Python:** Duck typing, convention-based privacy
- **Go:** No inheritance, composition via embedding
- **Java:** Strong typing, explicit access control
- **JavaScript:** Prototype-based, flexible privacy options

---

## 🚀 Real-World Example: Movie Class

All four language guides include a complete `Movie` class example with:
- Instance variables (id, title, genre, duration, release date)
- Class/static variables (total movies count)
- Methods (add rating, get average, check if recent)
- String representation
- Full usage demonstration

**Compare implementations to see:**
- Different syntax for same concepts
- Language-specific features
- Trade-offs in design

---

## 📖 Additional Resources

### Related Guides
- [The Four Pillars of OOP](../four-pillars/) - Encapsulation, Abstraction, Inheritance, Polymorphism
- [Interfaces and Abstract Classes](../interfaces-abstract-classes.md)
- [Class Relationships](../relationships.md)
- [Access Modifiers](../access-modifiers.md)

### Practice
- [Complete Interview Walkthroughs](../../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md)
- [Practice Problems](../../07-practice-problems/)
- [Real Company Examples](../../real-company-examples/)

---

## 🎯 Tips for Success

### For Interview Preparation
1. **Master ONE language first** - go deep before going wide
2. **Understand WHY, not just HOW** - explain design decisions
3. **Practice explaining** - talk through code creation
4. **Know the basics cold** - classes, objects, constructors, methods

### For Learning
1. **Type out examples** - don't just read
2. **Modify the code** - add features, experiment
3. **Compare languages** - see patterns across implementations
4. **Build small projects** - apply what you learn

### Common Mistakes to Avoid
❌ Confusing class variables with instance variables
❌ Forgetting `self`/`this` in method calls
❌ Mixing up static and instance contexts
❌ Not understanding scope and visibility
❌ Over-engineering simple problems

---

## 🌟 Why This Matters

### In Interviews
- **Foundation for everything** - All LLD builds on classes
- **Shows basic competence** - Must know to proceed
- **Language proficiency** - Demonstrates actual coding ability
- **Problem-solving** - How you structure solutions

### In Real Work
- **Code organization** - Clean class design
- **Maintainability** - Easy to understand and modify
- **Reusability** - Well-designed classes can be reused
- **Collaboration** - Others can work with your code

---

**Ready to learn? Pick your language above and dive in! 🚀**

[Back to OOP Fundamentals](../README.md)
