# Interfaces and Abstract Classes

Python doesn't have interfaces like Java, but uses **Abstract Base Classes (ABC)** and **Protocols** to define contracts.

## Why Use Interfaces/Abstract Classes?

**Benefits:**
- Define contracts that subclasses must implement
- Prevent instantiation of incomplete classes
- Document expected behavior
- Enable polymorphism with type checking

---

## 1. Abstract Base Classes (ABC)

### Basic ABC

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """Abstract base class - cannot instantiate"""

    @abstractmethod
    def process_payment(self, amount: float) -> str:
        """All subclasses MUST implement this"""
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        """All subclasses MUST implement this"""
        pass

    # Concrete method - shared by all subclasses
    def validate_amount(self, amount: float) -> bool:
        return amount > 0

# Cannot instantiate abstract class
# processor = PaymentProcessor()  # TypeError!

class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> str:
        if not self.validate_amount(amount):
            raise ValueError("Invalid amount")
        print(f"Processing ${amount} via credit card")
        return f"CC-{id(self)}"

    def refund(self, transaction_id: str) -> bool:
        print(f"Refunding {transaction_id}")
        return True

# Now we can instantiate
processor = CreditCardProcessor()
processor.process_payment(100.0)
```

### Abstract Properties

```python
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @property
    @abstractmethod
    def max_speed(self) -> int:
        """Abstract property - must override"""
        pass

    @abstractmethod
    def start_engine(self) -> None:
        pass

class Car(Vehicle):
    def __init__(self):
        self._max_speed = 120

    @property
    def max_speed(self) -> int:
        return self._max_speed

    def start_engine(self) -> None:
        print("Car engine started")

car = Car()
print(car.max_speed)  # 120
car.start_engine()    # Car engine started
```

---

## 2. Multiple Abstract Methods

```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self) -> None:
        pass

class Resizable(ABC):
    @abstractmethod
    def resize(self, width: int, height: int) -> None:
        pass

class Shape(Drawable, Resizable):
    """Can inherit from multiple ABCs"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def draw(self) -> None:
        print(f"Drawing {self.width}x{self.height} rectangle")

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

rect = Rectangle(10, 5)
rect.draw()
rect.resize(20, 10)
print(f"Area: {rect.area()}")
```

---

## 3. Protocol (Python 3.8+) - Structural Subtyping

**Protocol** allows duck typing with type checking. No need to inherit!

```python
from typing import Protocol

class Drawable(Protocol):
    """Protocol - defines interface without inheritance"""

    def draw(self) -> None:
        ...

    def get_area(self) -> float:
        ...

# No need to inherit from Drawable!
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> None:
        print(f"Drawing circle with radius {self.radius}")

    def get_area(self) -> float:
        return 3.14159 * self.radius ** 2

class Square:
    def __init__(self, side: float):
        self.side = side

    def draw(self) -> None:
        print(f"Drawing square with side {self.side}")

    def get_area(self) -> float:
        return self.side ** 2

def render(shape: Drawable) -> None:
    """Accepts any object with draw() and get_area()"""
    shape.draw()
    print(f"Area: {shape.get_area()}")

# Both work - they have the right methods!
render(Circle(5))
render(Square(4))
```

### ABC vs Protocol

| Feature | ABC | Protocol |
|---------|-----|----------|
| **Inheritance Required** | Yes | No (structural) |
| **Runtime Check** | Yes | Optional |
| **Prevents Instantiation** | Yes | No |
| **Type Checking** | Yes | Yes (mypy) |
| **Use When** | Enforce contract | Duck typing with types |

```python
from abc import ABC, abstractmethod
from typing import Protocol

# ABC - explicit inheritance
class Flyable(ABC):
    @abstractmethod
    def fly(self) -> None:
        pass

class Bird(Flyable):  # Must inherit
    def fly(self) -> None:
        print("Bird flying")

# Protocol - structural typing
class Swimmable(Protocol):
    def swim(self) -> None:
        ...

class Fish:  # No inheritance needed!
    def swim(self) -> None:
        print("Fish swimming")

def make_swim(animal: Swimmable) -> None:
    animal.swim()

make_swim(Fish())  # Works!
```

---

## 4. Abstract Class Methods

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @classmethod
    @abstractmethod
    def connect(cls, host: str) -> 'Database':
        """Abstract class method"""
        pass

    @abstractmethod
    def query(self, sql: str) -> list:
        pass

class PostgreSQL(Database):
    @classmethod
    def connect(cls, host: str) -> 'PostgreSQL':
        print(f"Connecting to PostgreSQL at {host}")
        return cls()

    def query(self, sql: str) -> list:
        print(f"Executing: {sql}")
        return []

# Use class method to connect
db = PostgreSQL.connect("localhost")
db.query("SELECT * FROM users")
```

---

## 5. Mixing Concrete and Abstract Methods

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    """Base repository with some concrete methods"""

    def __init__(self):
        self._cache = {}

    # Concrete methods
    def clear_cache(self) -> None:
        """Shared implementation"""
        self._cache.clear()

    def get_from_cache(self, key: str):
        """Shared implementation"""
        return self._cache.get(key)

    # Abstract methods
    @abstractmethod
    def find_by_id(self, id: int):
        pass

    @abstractmethod
    def save(self, entity) -> None:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass

class UserRepository(Repository):
    def find_by_id(self, id: int):
        # Check cache first
        cached = self.get_from_cache(f"user_{id}")
        if cached:
            return cached

        # Fetch from database
        user = {"id": id, "name": "Alice"}
        self._cache[f"user_{id}"] = user
        return user

    def save(self, entity) -> None:
        print(f"Saving user: {entity}")
        # Clear cache on save
        self.clear_cache()

    def delete(self, id: int) -> None:
        print(f"Deleting user {id}")
        self.clear_cache()

repo = UserRepository()
user = repo.find_by_id(1)
repo.save(user)
```

---

## 6. Real-World Example: Strategy Pattern with ABC

```python
from abc import ABC, abstractmethod
from typing import List

class SortStrategy(ABC):
    """Abstract strategy interface"""

    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        pass

class QuickSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class BubbleSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        data = data.copy()
        n = len(data)
        for i in range(n):
            for j in range(0, n-i-1):
                if data[j] > data[j+1]:
                    data[j], data[j+1] = data[j+1], data[j]
        return data

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self.strategy = strategy

    def sort_data(self, data: List[int]) -> List[int]:
        return self.strategy.sort(data)

# Usage
data = [64, 34, 25, 12, 22, 11, 90]

sorter = Sorter(QuickSort())
print("QuickSort:", sorter.sort_data(data))

sorter.set_strategy(BubbleSort())
print("BubbleSort:", sorter.sort_data(data))
```

---

## 7. Template Method Pattern

```python
from abc import ABC, abstractmethod

class DataParser(ABC):
    """Template method pattern with ABC"""

    def parse(self, data: str) -> dict:
        """Template method - defines algorithm skeleton"""
        # Step 1: Validate
        if not self.validate(data):
            raise ValueError("Invalid data")

        # Step 2: Extract (abstract - subclasses implement)
        extracted = self.extract_data(data)

        # Step 3: Transform (abstract)
        transformed = self.transform(extracted)

        # Step 4: Save (concrete - shared)
        self.save_to_cache(transformed)

        return transformed

    def validate(self, data: str) -> bool:
        """Concrete - shared validation"""
        return data is not None and len(data) > 0

    @abstractmethod
    def extract_data(self, data: str) -> dict:
        """Abstract - must implement"""
        pass

    @abstractmethod
    def transform(self, data: dict) -> dict:
        """Abstract - must implement"""
        pass

    def save_to_cache(self, data: dict) -> None:
        """Concrete - shared caching"""
        print(f"Saving to cache: {data}")

class JSONParser(DataParser):
    def extract_data(self, data: str) -> dict:
        import json
        return json.loads(data)

    def transform(self, data: dict) -> dict:
        # Add timestamp
        data['parsed_at'] = '2024-01-01'
        return data

class XMLParser(DataParser):
    def extract_data(self, data: str) -> dict:
        # Simplified XML parsing
        return {'xml_data': data}

    def transform(self, data: dict) -> dict:
        # Convert XML format
        return {'type': 'xml', 'content': data}

# Usage
json_parser = JSONParser()
result = json_parser.parse('{"name": "Alice"}')
print(result)

xml_parser = XMLParser()
result = xml_parser.parse('<person><name>Bob</name></person>')
print(result)
```

---

## 8. When to Use ABC vs Protocol

### Use ABC When:
✅ You want to **prevent instantiation** of incomplete classes
✅ You want to **share concrete methods** among subclasses
✅ You want **runtime enforcement** of interface
✅ You're building a **framework** where others extend your classes

### Use Protocol When:
✅ You want **duck typing with type checking**
✅ You can't modify existing classes (third-party code)
✅ You want **structural subtyping** (no inheritance)
✅ You're writing **type hints** for flexible functions

```python
from abc import ABC, abstractmethod
from typing import Protocol

# ABC - for framework/library
class Handler(ABC):
    """Framework users must extend this"""

    @abstractmethod
    def handle(self, request):
        pass

    def log(self, message):
        """Shared logging"""
        print(f"[LOG] {message}")

# Protocol - for type hints
class Closeable(Protocol):
    """Type hint for anything with close()"""

    def close(self) -> None:
        ...

def cleanup(resource: Closeable) -> None:
    """Works with any object that has close()"""
    resource.close()

# Works with file objects, connections, etc.
# No inheritance needed!
```

---

## 9. Common Patterns

### Factory with ABC

```python
from abc import ABC, abstractmethod
from typing import Dict, Type

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        pass

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return "Meow!"

class AnimalFactory:
    _animals: Dict[str, Type[Animal]] = {
        'dog': Dog,
        'cat': Cat
    }

    @classmethod
    def create(cls, animal_type: str) -> Animal:
        animal_class = cls._animals.get(animal_type.lower())
        if not animal_class:
            raise ValueError(f"Unknown animal: {animal_type}")
        return animal_class()

# Usage
animal = AnimalFactory.create('dog')
print(animal.speak())  # Woof!
```

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Generic repository interface"""

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class UserRepository(Repository[User]):
    def __init__(self):
        self._users: Dict[int, User] = {}

    def find_by_id(self, id: int) -> Optional[User]:
        return self._users.get(id)

    def find_all(self) -> List[User]:
        return list(self._users.values())

    def save(self, entity: User) -> User:
        self._users[entity.id] = entity
        return entity

    def delete(self, id: int) -> bool:
        if id in self._users:
            del self._users[id]
            return True
        return False
```

---

## 10. Interview Tips

### Common Questions

**Q: "What's the difference between ABC and regular classes?"**
- ABC prevents instantiation if abstract methods not implemented
- Forces subclasses to implement specific methods
- Documents contract clearly

**Q: "When to use ABC vs Protocol?"**
- ABC: Inheritance-based, runtime checks, shared code
- Protocol: Structural typing, no inheritance, type hints

**Q: "Can you have multiple abstract base classes?"**
- Yes! Python supports multiple inheritance
- Common pattern for mixins and interfaces

### Best Practices
✅ Use `@abstractmethod` for must-implement methods
✅ Mix concrete and abstract methods for code reuse
✅ Document why a class is abstract
✅ Consider Protocol for type hints
✅ Use `pass` not `raise NotImplementedError` in abstract methods

### Red Flags
❌ Not marking methods as `@abstractmethod`
❌ Trying to instantiate abstract class
❌ Overusing inheritance (prefer composition)
❌ Abstract methods that are never actually abstract

---

## Quick Reference

```python
from abc import ABC, abstractmethod
from typing import Protocol

# ABC - explicit contract
class MyABC(ABC):
    @abstractmethod
    def required_method(self):
        pass

    def concrete_method(self):
        # Shared implementation
        pass

# Protocol - structural typing
class MyProtocol(Protocol):
    def required_method(self):
        ...

# Usage
class Implementation(MyABC):  # Must inherit
    def required_method(self):
        return "Implemented"

class DuckTyped:  # No inheritance
    def required_method(self):
        return "Works with Protocol"
```

---

**Next:** [Class Relationships →](./relationships.md)
**Previous:** [Special Methods ←](./special-methods.md)
