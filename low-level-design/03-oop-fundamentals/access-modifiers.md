# Access Modifiers in Python

Python doesn't have strict access modifiers like Java (`private`, `protected`, `public`). Instead, it uses **naming conventions** and **properties** to control access.

## Python's Access Control Philosophy

**"We're all consenting adults here"** - Python trusts programmers not to access internal implementation.

---

## 1. Public Attributes (Default)

No underscore prefix = **public** (accessible everywhere).

```python
class Person:
    def __init__(self, name, age):
        self.name = name  # Public
        self.age = age    # Public

person = Person("Alice", 30)
print(person.name)  # ✓ Accessible
person.age = 31     # ✓ Can modify
```

**When to use:** Attributes that are part of the public API.

---

## 2. Protected Attributes (Convention)

Single underscore `_` prefix = **protected** (internal, but accessible).

```python
class BankAccount:
    def __init__(self, account_number, balance):
        self.account_number = account_number  # Public
        self._balance = balance                # Protected (convention)

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount

    def get_balance(self):
        return self._balance

account = BankAccount("12345", 1000)
print(account._balance)  # ✓ Works, but discouraged

# IDE/linter will warn you!
# "Protected member '_balance' accessed outside class"
```

**Convention:**
- `_` means "internal implementation, may change"
- Still accessible, but signals "use at your own risk"
- Not imported by `from module import *`

---

## 3. Private Attributes (Name Mangling)

Double underscore `__` prefix = **private** (name mangling applied).

```python
class BankAccount:
    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.__balance = balance  # Private (name mangled)

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount

    def get_balance(self):
        return self.__balance

account = BankAccount("12345", 1000)
# print(account.__balance)  # ❌ AttributeError!

# But can still access via mangled name (not recommended!)
print(account._BankAccount__balance)  # ✓ 1000
```

### How Name Mangling Works

```python
class MyClass:
    def __init__(self):
        self.__private = "secret"

obj = MyClass()

# Python internally renames:
# __private → _MyClass__private
print(obj._MyClass__private)  # ✓ Works (but don't do this!)
```

**When to use:**
- Avoid name collisions in inheritance
- Truly sensitive internal state
- Not for "security" (still accessible!)

---

## 4. Comparison Table

| Prefix | Name | Access Level | Use Case |
|--------|------|--------------|----------|
| None | `name` | Public | Part of public API |
| `_` | `_name` | Protected | Internal, may change |
| `__` | `__name` | Private | Name mangling, avoid collisions |

```python
class Example:
    def __init__(self):
        self.public = "Everyone can access"
        self._protected = "Internal use"
        self.__private = "Name mangled"

obj = Example()
print(obj.public)      # ✓ Recommended
print(obj._protected)  # ⚠️ Works, but discouraged
# print(obj.__private) # ❌ AttributeError
```

---

## 5. Properties - Controlled Access

Use `@property` for computed attributes or validation.

### Basic Property

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius  # Protected backing field

    @property
    def radius(self):
        """Getter - read access"""
        return self._radius

    @radius.setter
    def radius(self, value):
        """Setter - write access with validation"""
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def diameter(self):
        """Computed property (read-only)"""
        return self._radius * 2

    @property
    def area(self):
        """Another computed property"""
        return 3.14159 * self._radius ** 2

circle = Circle(5)
print(circle.radius)    # 5 (calls getter)
print(circle.diameter)  # 10 (computed)
print(circle.area)      # 78.54 (computed)

circle.radius = 10      # Calls setter with validation
# circle.radius = -5    # ❌ ValueError
# circle.diameter = 20  # ❌ AttributeError (no setter)
```

### Read-Only Property

```python
class Person:
    def __init__(self, name, birth_year):
        self._name = name
        self._birth_year = birth_year

    @property
    def name(self):
        """Read-only property"""
        return self._name

    @property
    def age(self):
        """Computed read-only property"""
        from datetime import datetime
        return datetime.now().year - self._birth_year

person = Person("Alice", 1990)
print(person.name)  # Alice
print(person.age)   # 34 (computed)

# person.name = "Bob"  # ❌ AttributeError: can't set attribute
# person.age = 25      # ❌ AttributeError: can't set attribute
```

### Property with Validation

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = None
        self.celsius = celsius  # Use setter for validation

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        # Convert and validate through celsius
        self.celsius = (value - 32) * 5/9

temp = Temperature(25)
print(temp.celsius)      # 25
print(temp.fahrenheit)   # 77.0

temp.fahrenheit = 86
print(temp.celsius)      # 30.0

# temp.celsius = -300   # ❌ ValueError!
```

---

## 6. Property Deleters

```python
class Resource:
    def __init__(self):
        self._data = "Important data"

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @data.deleter
    def data(self):
        """Called when 'del obj.data' is used"""
        print("Clearing data...")
        self._data = None

resource = Resource()
print(resource.data)  # Important data
del resource.data     # Calls deleter: "Clearing data..."
print(resource.data)  # None
```

---

## 7. Real-World Example: BankAccount

```python
class BankAccount:
    def __init__(self, account_number, initial_balance):
        self.account_number = account_number  # Public
        self._balance = initial_balance        # Protected
        self.__transaction_log = []           # Private

    @property
    def balance(self):
        """Read-only balance - no direct setter"""
        return self._balance

    def deposit(self, amount):
        """Public method to modify balance"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        self.__log_transaction("DEPOSIT", amount)
        return True

    def withdraw(self, amount):
        """Public method to modify balance"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self.__log_transaction("WITHDRAW", amount)
        return True

    def __log_transaction(self, type, amount):
        """Private method - name mangled"""
        self.__transaction_log.append({
            'type': type,
            'amount': amount
        })

    def _calculate_interest(self):
        """Protected method - internal use"""
        return self._balance * 0.03

    def get_transaction_count(self):
        """Public access to private data"""
        return len(self.__transaction_log)

# Usage
account = BankAccount("12345", 1000)

# ✓ Good: Use public API
print(account.balance)  # 1000
account.deposit(500)
account.withdraw(200)

# ⚠️ Discouraged: Access protected
print(account._balance)  # Works, but discouraged

# ❌ Error: Access private
# print(account.__transaction_log)  # AttributeError

# ✓ Good: Use public method
print(account.get_transaction_count())  # 2
```

---

## 8. `@property` vs Methods

### When to Use `@property`

✅ **Use property when:**
- Getting/setting feels like attribute access
- Computing a simple derived value
- Adding validation to attribute access
- Making read-only attributes

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):  # ✓ Property: Simple computation
        return self.width * self.height

    @property
    def perimeter(self):  # ✓ Property: Simple computation
        return 2 * (self.width + self.height)

rect = Rectangle(10, 5)
print(rect.area)  # 50 - feels like attribute access
```

### When to Use Methods

✅ **Use method when:**
- Operation is expensive
- Operation has side effects
- Operation requires parameters
- Operation is an action (verb)

```python
class Database:
    def connect(self):  # ✓ Method: Action with side effects
        print("Connecting to database...")

    def execute_query(self, sql):  # ✓ Method: Requires parameter
        print(f"Executing: {sql}")

    def calculate_statistics(self):  # ✓ Method: Expensive operation
        # Complex calculation...
        pass

db = Database()
db.connect()  # ✓ Clearly an action
```

---

## 9. Descriptor Protocol (Advanced)

Properties are implemented using descriptors. You can create custom descriptors:

```python
class PositiveNumber:
    """Descriptor that validates positive numbers"""

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name, 0)

    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"{self.name} must be positive")
        obj.__dict__[self.name] = value

class Product:
    price = PositiveNumber('price')  # Use descriptor
    quantity = PositiveNumber('quantity')

    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price      # Validated by descriptor
        self.quantity = quantity

product = Product("Laptop", 999.99, 10)
print(product.price)  # 999.99

# product.price = -100  # ❌ ValueError: price must be positive
```

---

## 10. `__slots__` - Memory Optimization

Restrict attributes and save memory:

```python
class Point:
    __slots__ = ['x', 'y']  # Only allow these attributes

    def __init__(self, x, y):
        self.x = x
        self.y = y

point = Point(1, 2)
print(point.x, point.y)  # ✓ Works

# point.z = 3  # ❌ AttributeError: 'Point' object has no attribute 'z'

# Benefits:
# - ~40-50% memory savings
# - Faster attribute access
# - Prevents typos in attribute names

# Drawbacks:
# - No __dict__ attribute
# - Can't add attributes dynamically
```

---

## 11. Comparison with Other Languages

### Python vs Java

```python
# Python - naming conventions
class Person:
    def __init__(self, name):
        self.name = name        # public
        self._age = 0           # protected (convention)
        self.__ssn = ""         # private (name mangling)

# Java - access modifiers
class Person {
    public String name;         // public
    protected int age;          // protected
    private String ssn;         // private
}
```

### Python vs JavaScript

```python
# Python
class Person:
    def __init__(self, name):
        self.__private = name  # Name mangling

# JavaScript (ES2022+)
class Person {
    #private;  // Truly private

    constructor(name) {
        this.#private = name;
    }
}
```

---

## 12. Interview Tips

### Common Questions

**Q: "How do you make attributes private in Python?"**
- Use `__` prefix for name mangling
- Use `_` prefix by convention
- Use `@property` for controlled access
- Remember: Nothing is truly private in Python!

**Q: "What's the difference between `_` and `__`?"**
- `_`: Convention, "internal use", not imported by `*`
- `__`: Name mangling, prevents accidental access in subclasses

**Q: "When to use `@property` vs direct access?"**
- `@property`: Need validation, computation, or future flexibility
- Direct access: Simple attributes with no logic

### Best Practices

✅ Use `_` prefix for internal implementation details
✅ Use `@property` for computed values or validation
✅ Keep public API minimal and well-documented
✅ Use `__` only when necessary (name collision avoidance)
✅ Prefer composition over complex access control

### Red Flags

❌ Overusing `__` private attributes
❌ Not using `@property` when validation needed
❌ Creating unnecessary getters/setters (Java style)
❌ Accessing `_protected` attributes from outside class
❌ Relying on `__private` for "security"

---

## Quick Reference

```python
class Example:
    def __init__(self):
        # Access levels
        self.public = 1          # Public: anyone can access
        self._protected = 2      # Protected: internal use (convention)
        self.__private = 3       # Private: name mangled

    @property
    def computed(self):          # Read-only property
        return self.public * 2

    @property
    def value(self):             # Property with getter
        return self._protected

    @value.setter
    def value(self, val):        # Property with setter
        if val > 0:
            self._protected = val
```

### Summary

| Pattern | Syntax | Access | Use Case |
|---------|--------|--------|----------|
| Public | `self.attr` | Everywhere | Public API |
| Protected | `self._attr` | Convention | Internal implementation |
| Private | `self.__attr` | Name mangled | Avoid collisions |
| Property | `@property` | Controlled | Validation, computation |
| Read-only | `@property` only | Read-only | Computed values |
| Slots | `__slots__` | Memory optimization | Many instances |

---

**Next:** [Class Relationships →](./relationships.md)
**Previous:** [Interfaces & Abstract Classes ←](./interfaces-abstract-classes.md)
