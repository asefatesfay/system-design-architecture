# OOP Fundamentals

> **🌍 Multi-Language Support:** Core concepts now available in multiple languages:
> - **[Four Pillars - All Languages](./four-pillars/)** ⭐⭐⭐ Separate guides for Python, Go, Java, JavaScript
> - **[Classes & Objects - Multi-Language](./classes-and-objects/)** Python, Go, Java, JavaScript
> - **[Language Comparison Guide](../lld-coding/multi-language/LANGUAGE-COMPARISON.md)** - Choose your language
>
> Examples below use Python for clarity. Click the links above for other languages.

Object-Oriented Programming (OOP) is the foundation of Low-Level Design. This section covers everything you need to master OOP concepts for LLD interviews.

## Contents

### 1. [Classes and Objects](./classes-and-objects/)
- What are classes and objects?
- Constructors and initialization
- Instance vs class variables
- Methods and behaviors
- `self` parameter
- `__str__` and `__repr__`

### 2. [The Four Pillars of OOP](./four-pillars/)
Master the core principles in Python, Go, Java, or JavaScript:
- **Encapsulation**: Hide internal details
- **Abstraction**: Show only essential features
- **Inheritance**: Reuse and extend behavior
- **Polymorphism**: Many forms of the same interface

### 3. [Interfaces and Abstract Classes](./interfaces-abstract-classes.md)
- Abstract base classes in Python
- Interface-like behavior with ABCs
- When to use abstract classes
- Contract-based programming

### 4. [Class Relationships](./relationships.md)
- **Association**: Objects work together
- **Aggregation**: "Has-a" relationship (loose coupling)
- **Composition**: "Part-of" relationship (strong coupling)
- **Dependency**: One class uses another

### 5. [Access Modifiers](./access-modifiers.md)
- Public, protected, and private in Python
- Name mangling
- Property decorators
- Getters and setters

### 6. [Special Methods (Dunder Methods)](./special-methods.md)
- `__init__`, `__str__`, `__repr__`
- `__eq__`, `__hash__`, `__lt__`
- `__len__`, `__getitem__`, `__setitem__`
- `__call__`, `__enter__`, `__exit__`

## Learning Path

1. **Start with [Classes and Objects](./classes-and-objects/)** - The building blocks
2. **Master [The Four Pillars](./four-pillars/)** - Essential OOP concepts
3. **Learn [Interfaces and Abstract Classes](./interfaces-abstract-classes.md)** - Design contracts
4. **Understand [Relationships](./relationships.md)** - How objects connect
5. **Study [Access Modifiers](./access-modifiers.md)** - Control visibility
6. **Explore [Special Methods](./special-methods.md)** - Python-specific features

## Why This Matters

In LLD interviews, you'll be expected to:
- Design classes with clear responsibilities
- Apply encapsulation and abstraction
- Use inheritance appropriately
- Define proper relationships between objects
- Explain your design decisions using OOP terminology

## Quick Reference

```python
# Class definition
class Car:
    # Class variable (shared)
    wheels = 4

    # Constructor
    def __init__(self, brand, model):
        # Instance variables (unique per object)
        self.brand = brand
        self.model = model
        self._mileage = 0  # Protected
        self.__vin = self._generate_vin()  # Private

    # Instance method
    def drive(self, miles):
        self._mileage += miles

    # Property (getter)
    @property
    def mileage(self):
        return self._mileage

    # String representation
    def __str__(self):
        return f"{self.brand} {self.model}"

# Inheritance
class ElectricCar(Car):
    def __init__(self, brand, model, battery_capacity):
        super().__init__(brand, model)
        self.battery_capacity = battery_capacity

    # Override method
    def drive(self, miles):
        if self.battery_capacity > 0:
            super().drive(miles)
            self.battery_capacity -= miles * 0.2

# Abstract class
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def start_engine(self):
        pass

# Composition
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

class Car:
    def __init__(self):
        self.engine = Engine(200)  # Car HAS-A Engine
```

## Practice Exercise

Before moving to design principles, practice by designing a **simple Library Management System** using OOP:

```python
# Design classes for:
# - Book (with ISBN, title, author)
# - Member (with member ID, name)
# - Library (manages books and members)
# - Loan (tracks which member borrowed which book)

# Apply:
# - Encapsulation (private attributes)
# - Proper relationships (Library HAS-A books, Member borrows Books)
# - Methods for common operations (borrow, return, search)
```

Try it yourself, then check the solution in the practice problems section!

---

**Start learning**: [Classes and Objects →](./classes-and-objects/)
