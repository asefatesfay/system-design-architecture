# Factory Pattern

Create objects without specifying the exact class to create. Delegates object creation to specialized methods or classes.

## Three Types

1. **Simple Factory** - One class creates objects
2. **Factory Method** - Subclasses decide which class to instantiate
3. **Abstract Factory** - Family of related objects

---

## 1. Simple Factory

**Problem:** Client code needs to create different types of objects.

```python
from abc import ABC, abstractmethod

# Product interface
class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

# Concrete products
class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

class Duck(Animal):
    def speak(self) -> str:
        return "Quack!"

# Simple Factory
class AnimalFactory:
    """Centralized object creation"""

    @staticmethod
    def create_animal(animal_type: str) -> Animal:
        animals = {
            'dog': Dog,
            'cat': Cat,
            'duck': Duck
        }

        animal_class = animals.get(animal_type.lower())
        if not animal_class:
            raise ValueError(f"Unknown animal type: {animal_type}")

        return animal_class()

# Usage
factory = AnimalFactory()
dog = factory.create_animal('dog')
cat = factory.create_animal('cat')

print(dog.speak())  # Woof!
print(cat.speak())  # Meow!
```

**Advantages:**
- Centralized creation logic
- Easy to add new types
- Client doesn't know concrete classes

---

## 2. Factory Method Pattern

**Problem:** Let subclasses decide which class to instantiate.

```python
from abc import ABC, abstractmethod

# Product
class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class WindowsButton(Button):
    def render(self) -> str:
        return "Rendering Windows button"

class MacButton(Button):
    def render(self) -> str:
        return "Rendering Mac button"

class LinuxButton(Button):
    def render(self) -> str:
        return "Rendering Linux button"

# Creator (Abstract)
class Dialog(ABC):
    """Dialog class with factory method"""

    @abstractmethod
    def create_button(self) -> Button:
        """Factory method - subclasses implement"""
        pass

    def render(self) -> str:
        """Template method using factory method"""
        button = self.create_button()
        return f"Dialog: {button.render()}"

# Concrete Creators
class WindowsDialog(Dialog):
    def create_button(self) -> Button:
        return WindowsButton()

class MacDialog(Dialog):
    def create_button(self) -> Button:
        return MacButton()

class LinuxDialog(Dialog):
    def create_button(self) -> Button:
        return LinuxButton()

# Usage
def show_dialog(dialog: Dialog):
    print(dialog.render())

# Client code doesn't know concrete classes
show_dialog(WindowsDialog())  # Dialog: Rendering Windows button
show_dialog(MacDialog())      # Dialog: Rendering Mac button
show_dialog(LinuxDialog())    # Dialog: Rendering Linux button
```

---

## 3. Abstract Factory Pattern

**Problem:** Create families of related objects without specifying concrete classes.

```python
from abc import ABC, abstractmethod

# Abstract Products
class Button(ABC):
    @abstractmethod
    def paint(self) -> str:
        pass

class Checkbox(ABC):
    @abstractmethod
    def paint(self) -> str:
        pass

# Concrete Products - Windows
class WindowsButton(Button):
    def paint(self) -> str:
        return "Windows Button"

class WindowsCheckbox(Checkbox):
    def paint(self) -> str:
        return "Windows Checkbox"

# Concrete Products - Mac
class MacButton(Button):
    def paint(self) -> str:
        return "Mac Button"

class MacCheckbox(Checkbox):
    def paint(self) -> str:
        return "Mac Checkbox"

# Abstract Factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass

# Concrete Factories
class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

# Application
class Application:
    def __init__(self, factory: GUIFactory):
        self.factory = factory

    def create_ui(self):
        """Creates consistent UI elements"""
        button = self.factory.create_button()
        checkbox = self.factory.create_checkbox()
        return f"UI: {button.paint()}, {checkbox.paint()}"

# Usage
def configure_application(os_type: str) -> Application:
    """Application configured for specific OS"""
    if os_type == "Windows":
        factory = WindowsFactory()
    elif os_type == "Mac":
        factory = MacFactory()
    else:
        raise ValueError(f"Unknown OS: {os_type}")

    return Application(factory)

# Client code
app = configure_application("Windows")
print(app.create_ui())  # UI: Windows Button, Windows Checkbox

app = configure_application("Mac")
print(app.create_ui())  # UI: Mac Button, Mac Checkbox
```

---

## 4. Real-World Example: Payment Processing

```python
from abc import ABC, abstractmethod
from typing import Dict

# Product
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> str:
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> str:
        pass

# Concrete Products
class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> str:
        return f"Processing ${amount} via Credit Card"

    def refund(self, transaction_id: str) -> str:
        return f"Refunding CC transaction {transaction_id}"

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> str:
        return f"Processing ${amount} via PayPal"

    def refund(self, transaction_id: str) -> str:
        return f"Refunding PayPal transaction {transaction_id}"

class CryptoProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> str:
        return f"Processing ${amount} via Cryptocurrency"

    def refund(self, transaction_id: str) -> str:
        return f"Refunding Crypto transaction {transaction_id}"

# Factory with Registry Pattern
class PaymentFactory:
    """Factory with dynamic registration"""

    _processors: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, processor_class: type):
        """Register new payment processor"""
        cls._processors[name] = processor_class

    @classmethod
    def create(cls, processor_type: str) -> PaymentProcessor:
        """Create payment processor"""
        processor_class = cls._processors.get(processor_type.lower())
        if not processor_class:
            raise ValueError(f"Unknown processor: {processor_type}")
        return processor_class()

    @classmethod
    def list_processors(cls):
        """List available processors"""
        return list(cls._processors.keys())

# Register processors
PaymentFactory.register('credit_card', CreditCardProcessor)
PaymentFactory.register('paypal', PayPalProcessor)
PaymentFactory.register('crypto', CryptoProcessor)

# Usage
processor = PaymentFactory.create('paypal')
print(processor.process_payment(100.0))

# Can dynamically add new processors!
class ApplePayProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> str:
        return f"Processing ${amount} via Apple Pay"

    def refund(self, transaction_id: str) -> str:
        return f"Refunding Apple Pay transaction {transaction_id}"

PaymentFactory.register('apple_pay', ApplePayProcessor)
print(PaymentFactory.list_processors())
```

---

## 5. Real-World Example: Document Parser

```python
from abc import ABC, abstractmethod

# Product
class DocumentParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> dict:
        pass

class JSONParser(DocumentParser):
    def parse(self, content: str) -> dict:
        import json
        return json.loads(content)

class XMLParser(DocumentParser):
    def parse(self, content: str) -> dict:
        # Simplified XML parsing
        return {"type": "xml", "content": content}

class CSVParser(DocumentParser):
    def parse(self, content: str) -> dict:
        import csv
        import io
        reader = csv.DictReader(io.StringIO(content))
        return {"type": "csv", "rows": list(reader)}

# Factory with auto-detection
class ParserFactory:
    """Factory that auto-detects format"""

    @staticmethod
    def create_parser(content: str) -> DocumentParser:
        """Auto-detect format and return appropriate parser"""
        content = content.strip()

        if content.startswith('{') or content.startswith('['):
            return JSONParser()
        elif content.startswith('<'):
            return XMLParser()
        elif ',' in content or '\n' in content:
            return CSVParser()
        else:
            raise ValueError("Unable to detect format")

# Usage
json_content = '{"name": "Alice", "age": 30}'
parser = ParserFactory.create_parser(json_content)
result = parser.parse(json_content)
print(result)  # {'name': 'Alice', 'age': 30}
```

---

## 6. Factory with Configuration

```python
class DatabaseConnectionFactory:
    """Factory that reads configuration"""

    @staticmethod
    def create_connection(config: dict):
        """Create connection based on config"""
        db_type = config.get('type', 'sqlite')

        if db_type == 'postgresql':
            return PostgreSQLConnection(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                database=config.get('database')
            )
        elif db_type == 'mysql':
            return MySQLConnection(
                host=config.get('host', 'localhost'),
                port=config.get('port', 3306),
                database=config.get('database')
            )
        elif db_type == 'sqlite':
            return SQLiteConnection(
                database=config.get('database', ':memory:')
            )
        else:
            raise ValueError(f"Unsupported database: {db_type}")

# Usage
config = {
    'type': 'postgresql',
    'host': 'localhost',
    'port': 5432,
    'database': 'myapp'
}

connection = DatabaseConnectionFactory.create_connection(config)
```

---

## 7. Factory with Dependency Injection

```python
from typing import Callable, Dict

class NotificationFactory:
    """Factory with dependency injection"""

    def __init__(self):
        self._creators: Dict[str, Callable] = {}

    def register(self, notification_type: str, creator: Callable):
        """Register a notification creator"""
        self._creators[notification_type] = creator

    def create(self, notification_type: str, **kwargs):
        """Create notification with injected dependencies"""
        creator = self._creators.get(notification_type)
        if not creator:
            raise ValueError(f"Unknown type: {notification_type}")
        return creator(**kwargs)

# Notification classes
class EmailNotification:
    def __init__(self, smtp_server: str, from_addr: str):
        self.smtp_server = smtp_server
        self.from_addr = from_addr

    def send(self, to: str, message: str):
        print(f"Email from {self.from_addr} to {to}: {message}")

class SMSNotification:
    def __init__(self, api_key: str, sender_id: str):
        self.api_key = api_key
        self.sender_id = sender_id

    def send(self, to: str, message: str):
        print(f"SMS from {self.sender_id} to {to}: {message}")

# Setup factory with dependencies
factory = NotificationFactory()

# Register with dependency injection
factory.register('email', lambda **kwargs: EmailNotification(
    smtp_server='smtp.gmail.com',
    from_addr='noreply@example.com'
))

factory.register('sms', lambda **kwargs: SMSNotification(
    api_key='secret-key',
    sender_id='MyApp'
))

# Usage
email_notif = factory.create('email')
email_notif.send('user@example.com', 'Hello!')

sms_notif = factory.create('sms')
sms_notif.send('+1234567890', 'Hello!')
```

---

## 8. When to Use Each Type

### Simple Factory
✅ **Use when:**
- Few product types
- Creation logic is simple
- Centralized creation is desired

### Factory Method
✅ **Use when:**
- Subclasses need different products
- Creation logic varies by subclass
- Following Open/Closed Principle

### Abstract Factory
✅ **Use when:**
- Need families of related objects
- Consistency across product families
- Want to enforce constraints

---

## 9. Comparison

| Type | Complexity | Flexibility | Use Case |
|------|------------|-------------|----------|
| **Simple Factory** | Low | Low | Few types, simple logic |
| **Factory Method** | Medium | Medium | Subclass variations |
| **Abstract Factory** | High | High | Related object families |

---

## 10. Interview Tips

### Common Questions

**Q: "Implement a factory for creating database connections"**
```python
class DBFactory:
    @staticmethod
    def create(db_type: str):
        factories = {
            'postgres': PostgresConnection,
            'mysql': MySQLConnection,
            'sqlite': SQLiteConnection
        }
        return factories[db_type]()
```

**Q: "What's the difference between Factory Method and Abstract Factory?"**
- Factory Method: One product, subclasses decide which
- Abstract Factory: Multiple related products, one family

**Q: "How would you extend the factory for new types?"**
- Registry pattern: Register new types dynamically
- Configuration: Read from config file
- Plugin system: Load from external modules

### Best Practices

✅ Use **simple factory** for most cases (Pythonic)
✅ Return **interfaces/abstract classes**, not concrete types
✅ Consider **registry pattern** for extensibility
✅ Use **type hints** for clarity
✅ Make factories **stateless** when possible

### Red Flags

❌ Over-engineering simple object creation
❌ Factory with complex conditional logic
❌ Not following Open/Closed Principle
❌ Returning different types inconsistently
❌ Factory doing more than creation

---

## Quick Reference

```python
# Simple Factory
class Factory:
    @staticmethod
    def create(type: str):
        if type == 'A':
            return ProductA()
        elif type == 'B':
            return ProductB()

# Factory Method
class Creator(ABC):
    @abstractmethod
    def factory_method(self):
        pass

    def operation(self):
        product = self.factory_method()
        return product.use()

# Abstract Factory
class AbstractFactory(ABC):
    @abstractmethod
    def create_product_a(self):
        pass

    @abstractmethod
    def create_product_b(self):
        pass
```

---

**Related Patterns:**
- [Singleton Pattern](./singleton.md) - Single instance
- [Builder Pattern](./builder.md) - Complex construction
- [Strategy Pattern](./strategy.md) - Interchangeable algorithms

**Back to:** [Design Patterns](./README.md)
