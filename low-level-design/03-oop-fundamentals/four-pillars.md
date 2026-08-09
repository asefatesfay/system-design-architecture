# The Four Pillars of OOP

The four fundamental principles of Object-Oriented Programming are the foundation of good software design. Mastering these is **critical** for LLD interviews.

## Overview

1. **Encapsulation** - Hide internal details, expose only what's necessary
2. **Abstraction** - Show only essential features, hide complexity
3. **Inheritance** - Reuse and extend existing code
4. **Polymorphism** - Same interface, different implementations

---

## 1. Encapsulation

### Definition
**Encapsulation** means bundling data (attributes) and methods that operate on that data within a single unit (class), and restricting direct access to some of the object's components.

### Why It Matters
- **Data Protection**: Prevent invalid states
- **Maintainability**: Change implementation without affecting users
- **Modularity**: Clear boundaries between components

### Python Implementation

Python uses naming conventions for access control:
- `public`: No underscore (accessible everywhere)
- `_protected`: Single underscore (accessible but discouraged)
- `__private`: Double underscore (name mangling, harder to access)

```python
class BankAccount:
    def __init__(self, account_number, initial_balance):
        self.account_number = account_number  # Public
        self._balance = initial_balance        # Protected
        self.__transaction_history = []       # Private

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

    # Public getter - controlled access to private data
    def get_balance(self):
        return self._balance

    # Private method - implementation detail
    def __add_transaction(self, type, amount):
        self.__transaction_history.append({
            'type': type,
            'amount': amount
        })

    # Property - pythonic way to encapsulate
    @property
    def balance(self):
        """Read-only access to balance"""
        return self._balance

# Usage
account = BankAccount("123456", 1000)

# Good - using public interface
account.deposit(500)
print(account.get_balance())  # 1500
print(account.balance)         # 1500 (using property)

# Bad - direct access (but Python allows it)
account._balance = 1000000  # NOT RECOMMENDED!

# Very difficult to access
# account.__transaction_history  # AttributeError
```

### Benefits of Encapsulation

```python
# WITHOUT Encapsulation - BAD
class User:
    def __init__(self, email):
        self.email = email  # Anyone can set invalid email!

user = User("john@example.com")
user.email = "invalid-email"  # No validation!


# WITH Encapsulation - GOOD
class User:
    def __init__(self, email):
        self.__email = None
        self.set_email(email)  # Validation in setter

    def set_email(self, email):
        if "@" in email and "." in email:
            self.__email = email
        else:
            raise ValueError("Invalid email format")

    def get_email(self):
        return self.__email

    # Pythonic way using property
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if "@" in value and "." in value:
            self.__email = value
        else:
            raise ValueError("Invalid email format")

# Usage
user = User("john@example.com")
# user.email = "invalid"  # Raises ValueError
user.email = "new@example.com"  # Validates first
```

---

## 2. Abstraction

### Definition
**Abstraction** means hiding complex implementation details and showing only the essential features of an object.

### Why It Matters
- **Simplicity**: Users don't need to know how it works internally
- **Flexibility**: Implementation can change without affecting users
- **Reduced Complexity**: Focus on what an object does, not how

### Key Difference from Encapsulation
- **Encapsulation**: About data hiding and access control
- **Abstraction**: About hiding complexity and showing only relevant details

```python
from abc import ABC, abstractmethod

# Abstract class - defines WHAT to do, not HOW
class PaymentProcessor(ABC):
    """Abstract class for payment processing"""

    @abstractmethod
    def process_payment(self, amount):
        """Process payment - must be implemented by subclasses"""
        pass

    @abstractmethod
    def refund(self, transaction_id, amount):
        """Refund payment - must be implemented by subclasses"""
        pass

# Concrete implementations - define HOW to do it
class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount):
        # Complex credit card processing logic hidden
        print(f"Processing ${amount} via Credit Card")
        # Validate card, contact payment gateway, etc.
        return True

    def refund(self, transaction_id, amount):
        print(f"Refunding ${amount} to credit card")
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount):
        # Complex PayPal API logic hidden
        print(f"Processing ${amount} via PayPal")
        # OAuth, API calls, etc.
        return True

    def refund(self, transaction_id, amount):
        print(f"Refunding ${amount} via PayPal")
        return True

# High-level code doesn't care about implementation details
class OrderService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def checkout(self, amount):
        # Abstraction: We know WHAT it does, not HOW
        return self.payment_processor.process_payment(amount)

# Usage - interchangeable implementations
order1 = OrderService(CreditCardProcessor())
order1.checkout(100)

order2 = OrderService(PayPalProcessor())
order2.checkout(200)
```

### Real-World Example: Database Abstraction

```python
from abc import ABC, abstractmethod

class Database(ABC):
    """Abstract database interface"""

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass

    @abstractmethod
    def close(self):
        pass

class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL...")
        # Complex connection logic

    def execute_query(self, query):
        print(f"Executing in PostgreSQL: {query}")
        # PostgreSQL-specific query execution

    def close(self):
        print("Closing PostgreSQL connection")

class MongoDatabase(Database):
    def connect(self):
        print("Connecting to MongoDB...")
        # Different connection logic

    def execute_query(self, query):
        print(f"Executing in MongoDB: {query}")
        # MongoDB-specific query execution

    def close(self):
        print("Closing MongoDB connection")

# Application code works with abstraction
class UserRepository:
    def __init__(self, database: Database):
        self.db = database

    def get_user(self, user_id):
        self.db.connect()
        result = self.db.execute_query(f"SELECT * FROM users WHERE id={user_id}")
        self.db.close()
        return result

# Can switch database without changing UserRepository code!
repo1 = UserRepository(PostgreSQLDatabase())
repo2 = UserRepository(MongoDatabase())
```

---

## 3. Inheritance

### Definition
**Inheritance** allows a class to inherit attributes and methods from another class, promoting code reuse and establishing relationships.

### Why It Matters
- **Code Reuse**: Don't repeat yourself
- **Extensibility**: Add new features without modifying existing code
- **Hierarchy**: Model real-world relationships

```python
# Base class (Parent/Superclass)
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        print(f"{self.name} is eating")

    def sleep(self):
        print(f"{self.name} is sleeping")

    def make_sound(self):
        print("Some generic sound")

# Derived class (Child/Subclass)
class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # Call parent constructor
        self.breed = breed

    # Override parent method
    def make_sound(self):
        print(f"{self.name} says: Woof!")

    # Add new method
    def fetch(self):
        print(f"{self.name} is fetching the ball")

class Cat(Animal):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color

    # Override parent method
    def make_sound(self):
        print(f"{self.name} says: Meow!")

    # Add new method
    def scratch(self):
        print(f"{self.name} is scratching the furniture")

# Usage
dog = Dog("Buddy", 3, "Golden Retriever")
cat = Cat("Whiskers", 2, "Black")

# Inherited methods
dog.eat()    # Buddy is eating
cat.sleep()  # Whiskers is sleeping

# Overridden methods
dog.make_sound()  # Buddy says: Woof!
cat.make_sound()  # Whiskers says: Meow!

# New methods
dog.fetch()      # Buddy is fetching the ball
cat.scratch()    # Whiskers is scratching the furniture
```

### Inheritance in LLD: Vehicle Hierarchy

```python
class Vehicle:
    """Base class for all vehicles"""

    def __init__(self, vehicle_id, brand, model, year):
        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self.year = year
        self._is_running = False

    def start(self):
        if not self._is_running:
            self._is_running = True
            print(f"{self.brand} {self.model} started")

    def stop(self):
        if self._is_running:
            self._is_running = False
            print(f"{self.brand} {self.model} stopped")

class Car(Vehicle):
    def __init__(self, vehicle_id, brand, model, year, num_doors):
        super().__init__(vehicle_id, brand, model, year)
        self.num_doors = num_doors
        self.trunk_open = False

    def open_trunk(self):
        self.trunk_open = True
        print("Trunk opened")

class Motorcycle(Vehicle):
    def __init__(self, vehicle_id, brand, model, year, has_sidecar):
        super().__init__(vehicle_id, brand, model, year)
        self.has_sidecar = has_sidecar

    def wheelie(self):
        if self._is_running:
            print("Performing wheelie!")

class ElectricCar(Car):
    def __init__(self, vehicle_id, brand, model, year, num_doors, battery_capacity):
        super().__init__(vehicle_id, brand, model, year, num_doors)
        self.battery_capacity = battery_capacity
        self.charge_level = 100

    def charge(self, amount):
        self.charge_level = min(100, self.charge_level + amount)
        print(f"Charged to {self.charge_level}%")

    # Override start to check battery
    def start(self):
        if self.charge_level > 0:
            super().start()
        else:
            print("Battery depleted! Cannot start.")

# Usage
tesla = ElectricCar("EV001", "Tesla", "Model 3", 2024, 4, 75)
tesla.start()        # Inherited from Vehicle
tesla.open_trunk()   # Inherited from Car
tesla.charge(50)     # Specific to ElectricCar
```

### Multiple Inheritance

Python supports multiple inheritance (inheriting from multiple classes):

```python
class Flyable:
    def fly(self):
        print("Flying...")

class Swimmable:
    def swim(self):
        print("Swimming...")

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name):
        Animal.__init__(self, name, 1)

    def make_sound(self):
        print(f"{self.name} says: Quack!")

# Duck can do everything
duck = Duck("Donald")
duck.eat()    # From Animal
duck.fly()    # From Flyable
duck.swim()   # From Swimmable
duck.make_sound()  # Overridden
```

---

## 4. Polymorphism

### Definition
**Polymorphism** means "many forms." It allows objects of different classes to be treated as objects of a common base class, with each implementing behavior in their own way.

### Why It Matters
- **Flexibility**: Write code that works with multiple types
- **Extensibility**: Add new types without changing existing code
- **Clean Code**: Same interface, different implementations

### Types of Polymorphism

#### 1. Method Overriding (Runtime Polymorphism)

```python
class Shape:
    def area(self):
        pass

    def perimeter(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def area(self):
        # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5

    def perimeter(self):
        return self.a + self.b + self.c

# Polymorphism in action
def print_shape_info(shape: Shape):
    """Works with ANY shape - polymorphism!"""
    print(f"Area: {shape.area()}")
    print(f"Perimeter: {shape.perimeter()}")

# All shapes can be used interchangeably
shapes = [
    Rectangle(5, 10),
    Circle(7),
    Triangle(3, 4, 5)
]

for shape in shapes:
    print_shape_info(shape)  # Same code, different behavior!
```

#### 2. Duck Typing (Python-specific)

"If it walks like a duck and quacks like a duck, it must be a duck."

```python
# No inheritance needed in Python!
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

class Robot:
    def speak(self):
        return "Beep boop!"

# Works with any object that has speak() method
def make_it_speak(thing):
    print(thing.speak())

# All work even though they're unrelated
make_it_speak(Dog())    # Woof!
make_it_speak(Cat())    # Meow!
make_it_speak(Robot())  # Beep boop!
```

#### 3. Operator Overloading

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Overload + operator"""
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Overload * operator"""
        return Vector(self.x * scalar, self.y * scalar)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)

v3 = v1 + v2      # Uses __add__
v4 = v1 * 3       # Uses __mul__

print(v3)  # Vector(4, 6)
print(v4)  # Vector(3, 6)
```

### Real-World Example: Notification System

```python
from abc import ABC, abstractmethod

class NotificationSender(ABC):
    @abstractmethod
    def send(self, recipient, message):
        pass

class EmailNotification(NotificationSender):
    def send(self, recipient, message):
        print(f"Sending email to {recipient}: {message}")
        # SMTP logic here

class SMSNotification(NotificationSender):
    def send(self, recipient, message):
        print(f"Sending SMS to {recipient}: {message}")
        # Twilio API logic here

class PushNotification(NotificationSender):
    def send(self, recipient, message):
        print(f"Sending push notification to {recipient}: {message}")
        # FCM/APNS logic here

class SlackNotification(NotificationSender):
    def send(self, recipient, message):
        print(f"Sending Slack message to {recipient}: {message}")
        # Slack API logic here

# Service that uses polymorphism
class NotificationService:
    def __init__(self):
        self.senders = []

    def add_sender(self, sender: NotificationSender):
        self.senders.append(sender)

    def notify_all(self, recipient, message):
        """Send via all registered channels - polymorphism!"""
        for sender in self.senders:
            sender.send(recipient, message)

# Usage - easy to extend with new notification types
service = NotificationService()
service.add_sender(EmailNotification())
service.add_sender(SMSNotification())
service.add_sender(PushNotification())

service.notify_all("user@example.com", "Your order has shipped!")

# Adding new notification type? Just implement the interface!
service.add_sender(SlackNotification())
```

---

## How They Work Together

All four pillars work together in real applications:

```python
from abc import ABC, abstractmethod

# ABSTRACTION: Define interface
class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

# ENCAPSULATION: Hide implementation details
class CreditCard(PaymentMethod):
    def __init__(self, card_number, cvv):
        self.__card_number = card_number  # Private
        self.__cvv = cvv                  # Private

    def process(self, amount):
        # Complex processing hidden
        if self.__validate_card():
            print(f"Charged ${amount} to card ****{self.__card_number[-4:]}")
            return True
        return False

    def __validate_card(self):  # Private method
        # Validation logic
        return True

# INHERITANCE: Reuse and extend
class DebitCard(CreditCard):
    def __init__(self, card_number, cvv, bank_account):
        super().__init__(card_number, cvv)
        self.bank_account = bank_account

    def process(self, amount):
        if self.__check_balance(amount):
            return super().process(amount)
        print("Insufficient funds")
        return False

    def __check_balance(self, amount):
        # Check account balance
        return True

# POLYMORPHISM: Same interface, different implementations
def process_payment(payment_method: PaymentMethod, amount):
    """Works with ANY payment method"""
    return payment_method.process(amount)

# Works with any PaymentMethod!
process_payment(CreditCard("1234567890123456", "123"), 100)
process_payment(DebitCard("9876543210987654", "456", "ACC001"), 50)
```

## Interview Tips

1. **Know the definitions**: Be able to explain each pillar clearly
2. **Use examples**: Always provide code examples when explaining
3. **Relate to SOLID**: These pillars connect to SOLID principles
4. **Identify in problems**: Point out where you're using each pillar
5. **Trade-offs**: Discuss when NOT to use inheritance (favor composition)

## Key Takeaways

1. **Encapsulation** = Data hiding + controlled access
2. **Abstraction** = Hide complexity, show essentials
3. **Inheritance** = "IS-A" relationship, code reuse
4. **Polymorphism** = Same interface, different implementations

---

**Next**: Learn about [Interfaces and Abstract Classes →](./interfaces-abstract-classes.md)
