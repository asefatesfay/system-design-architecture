# The Four Pillars of OOP - Python

The four fundamental principles of Object-Oriented Programming in Python with Python-specific explanations.

## Overview

1. **Encapsulation** - Hide internal details using naming conventions
2. **Abstraction** - Define interfaces with ABC and @abstractmethod
3. **Inheritance** - Extend classes with super() and method overriding
4. **Polymorphism** - Duck typing and explicit interfaces

---

## 1. Encapsulation 🔒

### Definition
**Encapsulation** in Python means bundling data and methods within a class, using naming conventions to control access.

### Python-Specific Access Control

Python uses **naming conventions** rather than strict access modifiers:
- `public`: No underscore - accessible everywhere
- `_protected`: Single underscore - accessible but discouraged (convention only)
- `__private`: Double underscore - name mangling applied

```python
class BankAccount:
    def __init__(self, account_number, initial_balance):
        self.account_number = account_number  # Public
        self._balance = initial_balance        # Protected (convention)
        self.__transaction_history = []       # Private (name mangling)

    # Public method - part of the API
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            self.__add_transaction("deposit", amount)
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            self.__add_transaction("withdraw", amount)
            return True
        return False

    # Protected method - internal use
    def _calculate_interest(self):
        return self._balance * 0.03

    # Private method - truly hidden via name mangling
    def __add_transaction(self, type, amount):
        self.__transaction_history.append({
            'type': type,
            'amount': amount
        })

    # Property decorator - controlled access
    @property
    def balance(self):
        """Read-only access to balance"""
        return self._balance

    # Setter with validation
    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value


# Usage
account = BankAccount("12345", 1000)
print(account.balance)        # ✓ 1000 (via property)
account.deposit(500)          # ✓ Works
print(account.balance)        # ✓ 1500

# These work but are discouraged:
print(account._balance)       # ✓ 1500 (protected - but discouraged)

# This doesn't work directly (name mangling):
# print(account.__transaction_history)  # ❌ AttributeError

# But can still access via name mangling (not recommended):
print(account._BankAccount__transaction_history)  # Shows the mangled name
```

### Python Threading and Locks

When working with shared state across threads, use `threading.Lock`:

```python
import threading

class ThreadSafeBankAccount:
    def __init__(self, account_number, initial_balance):
        self.account_number = account_number
        self._balance = initial_balance
        self._lock = threading.Lock()  # Lock for thread safety

    def deposit(self, amount):
        with self._lock:  # Acquire lock automatically
            if amount > 0:
                self._balance += amount
                return True
        return False

    def withdraw(self, amount):
        with self._lock:  # Context manager handles lock/unlock
            if 0 < amount <= self._balance:
                self._balance -= amount
                return True
        return False

    @property
    def balance(self):
        with self._lock:
            return self._balance
```

**Key Python Threading Concepts:**
- `threading.Lock()`: Creates a mutual exclusion lock
- `with lock:`: Context manager that automatically acquires/releases lock
- `lock.acquire()` / `lock.release()`: Manual lock control (use with caution)
- `threading.RLock()`: Reentrant lock (can be acquired multiple times by same thread)

---

## 2. Abstraction 🎭

### Definition
**Abstraction** in Python means defining interfaces and hiding implementation details using Abstract Base Classes (ABC).

### Python's ABC Module

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """Abstract base class - cannot be instantiated"""

    @abstractmethod
    def process_payment(self, amount):
        """All subclasses MUST implement this"""
        pass

    @abstractmethod
    def refund(self, transaction_id):
        """All subclasses MUST implement this"""
        pass

    # Concrete method - shared by all subclasses
    def validate_amount(self, amount):
        return amount > 0


class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount):
        print(f"Processing ${amount} via credit card")
        return f"CC-{id(self)}"

    def refund(self, transaction_id):
        print(f"Refunding transaction {transaction_id}")
        return True


class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount):
        print(f"Processing ${amount} via PayPal")
        return f"PP-{id(self)}"

    def refund(self, transaction_id):
        print(f"Refunding PayPal transaction {transaction_id}")
        return True


# Usage
def checkout(processor: PaymentProcessor, amount: float):
    """Works with ANY payment processor"""
    if processor.validate_amount(amount):
        return processor.process_payment(amount)

# Works with any processor
cc = CreditCardProcessor()
paypal = PayPalProcessor()

checkout(cc, 100)      # Credit card processing
checkout(paypal, 200)  # PayPal processing

# Cannot instantiate abstract class:
# processor = PaymentProcessor()  # ❌ TypeError
```

### Python-Specific ABC Features

```python
from abc import ABC, abstractmethod, abstractproperty

class Vehicle(ABC):
    @abstractmethod
    def start(self):
        """Abstract method - must override"""
        pass

    @property
    @abstractmethod
    def max_speed(self):
        """Abstract property - must override"""
        pass

    # Can have concrete methods too
    def stop(self):
        """Concrete method - can use as-is or override"""
        print("Vehicle stopped")


class Car(Vehicle):
    def __init__(self):
        self._max_speed = 120

    def start(self):
        print("Car engine started")

    @property
    def max_speed(self):
        return self._max_speed


car = Car()
car.start()             # Car engine started
print(car.max_speed)    # 120
car.stop()              # Vehicle stopped
```

---

## 3. Inheritance 👨‍👩‍👧

### Definition
**Inheritance** in Python allows classes to inherit attributes and methods from parent classes using simple syntax.

### Python Inheritance with super()

```python
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        print(f"{self.name} is eating")

    def sleep(self):
        print(f"{self.name} is sleeping")


class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # Call parent constructor
        self.breed = breed

    def bark(self):
        print(f"{self.name} says: Woof!")

    # Override parent method
    def eat(self):
        print(f"{self.name} the {self.breed} is eating dog food")


class Cat(Animal):
    def __init__(self, name, age, indoor):
        super().__init__(name, age)
        self.indoor = indoor

    def meow(self):
        print(f"{self.name} says: Meow!")


# Usage
dog = Dog("Buddy", 3, "Golden Retriever")
cat = Cat("Whiskers", 2, True)

dog.eat()    # Overridden: "Buddy the Golden Retriever is eating dog food"
cat.eat()    # Inherited: "Whiskers is eating"
dog.sleep()  # Inherited: "Buddy is sleeping"
dog.bark()   # Dog-specific: "Buddy says: Woof!"
cat.meow()   # Cat-specific: "Whiskers says: Meow!"
```

### Multiple Inheritance and MRO

Python supports **multiple inheritance** and uses Method Resolution Order (MRO):

```python
class Flyable:
    def fly(self):
        print("Flying...")


class Swimmable:
    def swim(self):
        print("Swimming...")


class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name, age):
        super().__init__(name, age)

    def quack(self):
        print(f"{self.name} says: Quack!")


duck = Duck("Donald", 5)
duck.eat()    # From Animal
duck.fly()    # From Flyable
duck.swim()   # From Swimmable
duck.quack()  # Duck-specific

# Check MRO (Method Resolution Order)
print(Duck.__mro__)
# Shows: Duck -> Animal -> Flyable -> Swimmable -> object
```

---

## 4. Polymorphism 🦎

### Definition
**Polymorphism** in Python comes in two forms: duck typing (implicit) and explicit interfaces (ABC).

### Duck Typing (Python's Default)

Python uses **duck typing**: "If it walks like a duck and quacks like a duck, it's a duck"

```python
class Dog:
    def speak(self):
        return "Woof!"


class Cat:
    def speak(self):
        return "Meow!"


class Duck:
    def speak(self):
        return "Quack!"


def make_it_speak(animal):
    """Works with ANY object that has speak() method"""
    print(animal.speak())


# No inheritance needed!
make_it_speak(Dog())   # Woof!
make_it_speak(Cat())   # Meow!
make_it_speak(Duck())  # Quack!
```

### Explicit Polymorphism with ABC

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def area(self):
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5

    def perimeter(self):
        return self.a + self.b + self.c


def print_shape_info(shape: Shape):
    """Polymorphism - works with ANY shape"""
    print(f"Area: {shape.area():.2f}")
    print(f"Perimeter: {shape.perimeter():.2f}")


# All work through same interface
shapes = [
    Circle(5),
    Rectangle(4, 6),
    Triangle(3, 4, 5)
]

for shape in shapes:
    print_shape_info(shape)
```

### Method Overriding

```python
class Vehicle:
    def start(self):
        print("Vehicle starting...")


class Car(Vehicle):
    def start(self):
        print("Car engine starting with key...")


class ElectricCar(Car):
    def start(self):
        print("Electric car silently powering on...")
        # Can still call parent method if needed:
        # super().start()


# Same method name, different behavior
vehicles = [Vehicle(), Car(), ElectricCar()]

for v in vehicles:
    v.start()
# Output:
# Vehicle starting...
# Car engine starting with key...
# Electric car silently powering on...
```

---

## Python-Specific Concepts Summary

### 1. Name Mangling
```python
class Example:
    def __init__(self):
        self.__private = "hidden"  # Becomes _Example__private

ex = Example()
# ex.__private  # ❌ AttributeError
# ex._Example__private  # ✓ Works but don't do this
```

### 2. Properties
```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32

temp = Temperature(25)
print(temp.celsius)      # 25
print(temp.fahrenheit)   # 77.0
temp.celsius = 30        # Uses setter
```

### 3. Threading and Concurrency
```python
import threading
from threading import Lock, RLock, Condition

class Counter:
    def __init__(self):
        self._value = 0
        self._lock = Lock()  # Basic lock

    def increment(self):
        with self._lock:
            self._value += 1

    def get_value(self):
        with self._lock:
            return self._value


# RLock - Reentrant Lock (can acquire multiple times)
class ReentrantExample:
    def __init__(self):
        self._lock = RLock()

    def outer(self):
        with self._lock:
            print("Outer")
            self.inner()  # Can acquire lock again

    def inner(self):
        with self._lock:
            print("Inner")


# Condition - For thread communication
class BoundedQueue:
    def __init__(self, max_size):
        self._queue = []
        self._max_size = max_size
        self._condition = Condition()

    def put(self, item):
        with self._condition:
            while len(self._queue) >= self._max_size:
                self._condition.wait()  # Wait for space
            self._queue.append(item)
            self._condition.notify()  # Wake up waiting threads

    def get(self):
        with self._condition:
            while len(self._queue) == 0:
                self._condition.wait()  # Wait for items
            item = self._queue.pop(0)
            self._condition.notify()
            return item
```

---

## Key Takeaways for Python

✅ **Encapsulation**: Use `_protected` and `__private` naming conventions
✅ **Abstraction**: Use `ABC` and `@abstractmethod` for interfaces
✅ **Inheritance**: Use `super()` for parent class access, supports multiple inheritance
✅ **Polymorphism**: Duck typing by default, or use ABC for explicit contracts

✅ **Threading**: Use `threading.Lock()` with `with` statement for thread safety
✅ **Properties**: Use `@property` decorator for controlled attribute access
✅ **Name Mangling**: `__private` becomes `_ClassName__private`

---

**Related Files:**
- [Go Implementation](./go.md)
- [Java Implementation](./java.md)
- [JavaScript Implementation](./javascript.md)
- [Back to OOP Fundamentals](../README.md)
