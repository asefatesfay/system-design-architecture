# SOLID Principles

SOLID is an acronym for five design principles that make software more maintainable, flexible, and scalable. These principles are **CRITICAL** for LLD interviews - you must know them well!

## Overview

- **S** - Single Responsibility Principle
- **O** - Open/Closed Principle
- **L** - Liskov Substitution Principle
- **I** - Interface Segregation Principle
- **D** - Dependency Inversion Principle

---

## S - Single Responsibility Principle (SRP)

### Definition
**A class should have only one reason to change.** Each class should have only one responsibility or job.

### Why It Matters
- Easier to understand
- Easier to test
- Less coupling between different concerns
- Changes in one area don't affect others

### ❌ Bad Example: Multiple Responsibilities

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    # Responsibility 1: Validate user data
    def validate_email(self):
        return "@" in self.email and "." in self.email

    # Responsibility 2: Save to database
    def save_to_database(self):
        print(f"Saving {self.name} to database")
        # Database logic

    # Responsibility 3: Send email
    def send_welcome_email(self):
        print(f"Sending welcome email to {self.email}")
        # Email sending logic

    # Responsibility 4: Generate reports
    def generate_report(self):
        return f"User Report: {self.name}"

# Problem: User class has 4 reasons to change!
# - Email format changes
# - Database structure changes
# - Email service changes
# - Report format changes
```

### ✅ Good Example: Single Responsibility

```python
class User:
    """Represents user data - ONE responsibility"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserValidator:
    """Validates user data - ONE responsibility"""
    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email

    @staticmethod
    def validate_name(name):
        return len(name) > 0

class UserRepository:
    """Handles user persistence - ONE responsibility"""
    def save(self, user):
        print(f"Saving {user.name} to database")
        # Database logic

    def find_by_email(self, email):
        # Database query logic
        pass

class EmailService:
    """Sends emails - ONE responsibility"""
    def send_welcome_email(self, user):
        print(f"Sending welcome email to {user.email}")
        # Email sending logic

class UserReportGenerator:
    """Generates user reports - ONE responsibility"""
    def generate(self, user):
        return f"User Report: {user.name}"

# Now each class has ONE reason to change!
```

### Real-World Example: Order Processing

```python
from datetime import datetime

# BAD: OrderProcessor does everything
class BadOrderProcessor:
    def process_order(self, order):
        # Validate order
        if not order.items:
            return False

        # Calculate total
        total = sum(item.price * item.quantity for item in order.items)

        # Process payment
        print(f"Processing payment of ${total}")

        # Update inventory
        for item in order.items:
            print(f"Reducing inventory for {item.name}")

        # Send confirmation email
        print(f"Sending confirmation to {order.customer.email}")

        # Log to database
        print(f"Logging order {order.id} to database")

        return True

# GOOD: Separate responsibilities
class Order:
    def __init__(self, order_id, customer, items):
        self.order_id = order_id
        self.customer = customer
        self.items = items
        self.created_at = datetime.now()

class OrderValidator:
    def validate(self, order):
        if not order.items:
            raise ValueError("Order must have at least one item")
        return True

class PriceCalculator:
    def calculate_total(self, order):
        return sum(item.price * item.quantity for item in order.items)

class PaymentProcessor:
    def process(self, amount):
        print(f"Processing payment of ${amount}")
        return True

class InventoryService:
    def update_inventory(self, order):
        for item in order.items:
            print(f"Reducing inventory for {item.name}")

class NotificationService:
    def send_order_confirmation(self, order):
        print(f"Sending confirmation to {order.customer.email}")

class OrderLogger:
    def log(self, order):
        print(f"Logging order {order.order_id} to database")

# Usage - coordinated by a service
class OrderService:
    def __init__(self):
        self.validator = OrderValidator()
        self.calculator = PriceCalculator()
        self.payment_processor = PaymentProcessor()
        self.inventory = InventoryService()
        self.notifications = NotificationService()
        self.logger = OrderLogger()

    def process_order(self, order):
        self.validator.validate(order)
        total = self.calculator.calculate_total(order)
        self.payment_processor.process(total)
        self.inventory.update_inventory(order)
        self.notifications.send_order_confirmation(order)
        self.logger.log(order)
```

---

## O - Open/Closed Principle (OCP)

### Definition
**Software entities should be open for extension but closed for modification.** You should be able to add new functionality without changing existing code.

### Why It Matters
- Reduces risk of breaking existing code
- Easier to add features
- Better maintainability

### ❌ Bad Example: Modification Required

```python
class DiscountCalculator:
    def calculate_discount(self, customer_type, amount):
        if customer_type == "regular":
            return amount * 0.05
        elif customer_type == "premium":
            return amount * 0.10
        elif customer_type == "vip":
            return amount * 0.20
        # Problem: Adding new customer type requires modifying this method!
        elif customer_type == "corporate":  # New requirement
            return amount * 0.15
        return 0
```

### ✅ Good Example: Extension Without Modification

```python
from abc import ABC, abstractmethod

# Base abstraction - CLOSED for modification
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, amount):
        pass

# OPEN for extension - just add new classes
class RegularCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.05

class PremiumCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.10

class VIPCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.20

# New customer type? Just add a new class - no modification needed!
class CorporateCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.15

class DiscountCalculator:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def calculate(self, amount):
        return self.strategy.calculate_discount(amount)

# Usage
calc = DiscountCalculator(VIPCustomerDiscount())
discount = calc.calculate(1000)  # 200
```

### Real-World Example: Report Generator

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, data):
        pass

# Different report formats - extending, not modifying
class PDFReport(ReportGenerator):
    def generate(self, data):
        return f"PDF Report: {data}"

class ExcelReport(ReportGenerator):
    def generate(self, data):
        return f"Excel Report: {data}"

class HTMLReport(ReportGenerator):
    def generate(self, data):
        return f"HTML Report: {data}"

# New format? Just add a class!
class JSONReport(ReportGenerator):
    def generate(self, data):
        import json
        return json.dumps({"report": data})

class ReportService:
    def __init__(self, generator: ReportGenerator):
        self.generator = generator

    def create_report(self, data):
        return self.generator.generate(data)

# Easy to switch formats
service = ReportService(PDFReport())
service = ReportService(JSONReport())  # Just change the generator!
```

---

## L - Liskov Substitution Principle (LSP)

### Definition
**Objects of a superclass should be replaceable with objects of a subclass without breaking the application.** Subclasses should extend, not weaken, parent class behavior.

### Why It Matters
- Ensures inheritance is used correctly
- Prevents unexpected behavior
- Maintains contracts

### ❌ Bad Example: Violates LSP

```python
class Bird:
    def fly(self):
        return "Flying..."

class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying"

class Penguin(Bird):
    def fly(self):
        # Problem: Penguins can't fly!
        raise Exception("Penguins can't fly")

# This breaks LSP
def make_bird_fly(bird: Bird):
    print(bird.fly())

make_bird_fly(Sparrow())  # Works
make_bird_fly(Penguin())  # Crashes! Violates LSP
```

### ✅ Good Example: Follows LSP

```python
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        return self.fly()

    def fly(self):
        return "Flying..."

class Sparrow(FlyingBird):
    def fly(self):
        return "Sparrow flying"

class FlightlessBird(Bird):
    def move(self):
        return self.walk()

    def walk(self):
        return "Walking..."

class Penguin(FlightlessBird):
    def walk(self):
        return "Penguin waddling"

    def swim(self):
        return "Penguin swimming"

# Now it works correctly
def make_bird_move(bird: Bird):
    print(bird.move())

make_bird_move(Sparrow())  # Sparrow flying
make_bird_move(Penguin())  # Penguin waddling - works!
```

### Real-World Example: Rectangle-Square Problem

```python
# BAD: Square violates LSP
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def set_width(self, width):
        self._width = width

    def set_height(self, height):
        self._height = height

    def area(self):
        return self._width * self._height

class Square(Rectangle):
    def set_width(self, width):
        self._width = width
        self._height = width  # Problem: changes height too!

    def set_height(self, height):
        self._width = height
        self._height = height  # Problem: changes width too!

# This breaks expectations
def test_rectangle(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20  # Expected for rectangle

test_rectangle(Rectangle(0, 0))  # Works
test_rectangle(Square(0, 0))     # Fails! Area is 16, not 20

# GOOD: Don't use inheritance
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2
```

---

## I - Interface Segregation Principle (ISP)

### Definition
**Clients should not be forced to depend on interfaces they don't use.** Create specific interfaces rather than one general-purpose interface.

### Why It Matters
- Prevents bloated interfaces
- Reduces coupling
- More flexible design

### ❌ Bad Example: Fat Interface

```python
from abc import ABC, abstractmethod

class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass

class Human(Worker):
    def work(self):
        print("Human working")

    def eat(self):
        print("Human eating")

    def sleep(self):
        print("Human sleeping")

class Robot(Worker):
    def work(self):
        print("Robot working")

    def eat(self):
        # Problem: Robots don't eat!
        pass  # Forced to implement unused method

    def sleep(self):
        # Problem: Robots don't sleep!
        pass  # Forced to implement unused method
```

### ✅ Good Example: Segregated Interfaces

```python
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    def work(self):
        print("Human working")

    def eat(self):
        print("Human eating")

    def sleep(self):
        print("Human sleeping")

class Robot(Workable):  # Only implements what it needs
    def work(self):
        print("Robot working")

class Animal(Eatable, Sleepable):  # Different combination
    def eat(self):
        print("Animal eating")

    def sleep(self):
        print("Animal sleeping")
```

### Real-World Example: Printer Interfaces

```python
from abc import ABC, abstractmethod

# BAD: All-in-one interface
class MultiFunctionDevice(ABC):
    @abstractmethod
    def print_document(self):
        pass

    @abstractmethod
    def scan_document(self):
        pass

    @abstractmethod
    def fax_document(self):
        pass

    @abstractmethod
    def copy_document(self):
        pass

# Simple printer forced to implement everything
class SimplePrinter(MultiFunctionDevice):
    def print_document(self):
        print("Printing...")

    def scan_document(self):
        raise NotImplementedError("No scanner")

    def fax_document(self):
        raise NotImplementedError("No fax")

    def copy_document(self):
        raise NotImplementedError("No copier")

# GOOD: Segregated interfaces
class Printer(ABC):
    @abstractmethod
    def print_document(self):
        pass

class Scanner(ABC):
    @abstractmethod
    def scan_document(self):
        pass

class Fax(ABC):
    @abstractmethod
    def fax_document(self):
        pass

class SimplePrinter(Printer):
    def print_document(self):
        print("Printing...")

class AllInOnePrinter(Printer, Scanner, Fax):
    def print_document(self):
        print("Printing...")

    def scan_document(self):
        print("Scanning...")

    def fax_document(self):
        print("Faxing...")
```

---

## D - Dependency Inversion Principle (DIP)

### Definition
**High-level modules should not depend on low-level modules. Both should depend on abstractions.** Also, abstractions should not depend on details; details should depend on abstractions.

### Why It Matters
- Reduces coupling
- Easier to test (can mock dependencies)
- More flexible and extensible

### ❌ Bad Example: High-Level Depends on Low-Level

```python
# Low-level module
class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL")

    def query(self, sql):
        print(f"Executing: {sql}")

# High-level module depends on concrete class
class UserRepository:
    def __init__(self):
        self.db = MySQLDatabase()  # Hard dependency!

    def get_user(self, user_id):
        self.db.connect()
        self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# Problems:
# 1. Can't easily switch to PostgreSQL
# 2. Can't test without real MySQL
# 3. Tightly coupled to MySQL implementation
```

### ✅ Good Example: Both Depend on Abstraction

```python
from abc import ABC, abstractmethod

# Abstraction
class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def query(self, sql):
        pass

# Low-level implementations
class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL")

    def query(self, sql):
        print(f"MySQL: {sql}")

class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL")

    def query(self, sql):
        print(f"PostgreSQL: {sql}")

class MockDatabase(Database):
    """For testing"""
    def connect(self):
        pass

    def query(self, sql):
        return {"id": 1, "name": "Test User"}

# High-level module depends on abstraction
class UserRepository:
    def __init__(self, database: Database):
        self.db = database  # Depends on abstraction!

    def get_user(self, user_id):
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# Easy to switch implementations
repo1 = UserRepository(MySQLDatabase())
repo2 = UserRepository(PostgreSQLDatabase())
repo3 = UserRepository(MockDatabase())  # For testing!
```

### Real-World Example: Notification System

```python
from abc import ABC, abstractmethod

# Abstraction
class MessageSender(ABC):
    @abstractmethod
    def send(self, recipient, message):
        pass

# Concrete implementations
class EmailSender(MessageSender):
    def send(self, recipient, message):
        print(f"Email to {recipient}: {message}")

class SMSSender(MessageSender):
    def send(self, recipient, message):
        print(f"SMS to {recipient}: {message}")

# High-level service depends on abstraction
class NotificationService:
    def __init__(self, sender: MessageSender):
        self.sender = sender  # Depends on abstraction

    def notify_user(self, user, message):
        self.sender.send(user.contact, message)

# Dependency injection - flexible!
service1 = NotificationService(EmailSender())
service2 = NotificationService(SMSSender())
```

---

## All Principles Together

```python
from abc import ABC, abstractmethod
from typing import List

# Interface Segregation: Small, focused interfaces
class Readable(ABC):
    @abstractmethod
    def read(self):
        pass

class Writable(ABC):
    @abstractmethod
    def write(self, data):
        pass

# Open/Closed: Open for extension
class DataStore(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self):
        pass

# Concrete implementations
class FileStore(DataStore):
    def save(self, data):
        print(f"Saving to file: {data}")

    def load(self):
        return "File data"

class DatabaseStore(DataStore):
    def save(self, data):
        print(f"Saving to database: {data}")

    def load(self):
        return "Database data"

# Single Responsibility: Each class has one job
class DataValidator:
    def validate(self, data):
        return len(data) > 0

class DataLogger:
    def log(self, message):
        print(f"LOG: {message}")

# Dependency Inversion: Depend on abstractions
class DataService:
    def __init__(self, store: DataStore, validator: DataValidator, logger: DataLogger):
        self.store = store
        self.validator = validator
        self.logger = logger

    def save_data(self, data):
        if self.validator.validate(data):
            self.store.save(data)
            self.logger.log(f"Saved: {data}")
            return True
        return False

# Liskov Substitution: Subclasses work correctly
def process_data(store: DataStore, data):
    store.save(data)  # Works with ANY DataStore

# Usage - all principles applied
service = DataService(
    FileStore(),
    DataValidator(),
    DataLogger()
)

service.save_data("Important data")
```

## Interview Tips

1. **Memorize the acronym**: S-O-L-I-D
2. **Provide examples**: Always have code examples ready
3. **Identify in designs**: Point out where you're applying SOLID
4. **Explain benefits**: Know why each principle matters
5. **Recognize violations**: Be able to spot when SOLID is violated

## Quick Reference

| Principle | What | How |
|-----------|------|-----|
| SRP | One reason to change | Separate concerns into different classes |
| OCP | Extend, don't modify | Use abstraction and polymorphism |
| LSP | Subclasses must work | Don't break parent class contracts |
| ISP | Small interfaces | Split large interfaces into smaller ones |
| DIP | Depend on abstractions | Use interfaces/abstract classes |

---

**Next**: Learn about [Design Patterns →](../06-design-patterns/)
