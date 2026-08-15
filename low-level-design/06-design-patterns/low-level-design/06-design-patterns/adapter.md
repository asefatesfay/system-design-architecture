# Adapter Pattern

Convert the interface of a class into another interface clients expect. Make incompatible interfaces work together.

**Also Known As:** Wrapper

## Why Adapter?

**Problems it solves:**
- Interface incompatibility between classes
- Integrate third-party libraries without modifying them
- Reuse existing classes with different interfaces
- Support legacy code with new interfaces

```python
# WITHOUT Adapter - incompatible interfaces
class OldPrinter:
    def print_document(self, text):  # Old interface
        pass

class NewSystem:
    def send_to_device(self, device):
        device.render(text)  # Expects render() method
        # ❌ Can't use OldPrinter - no render() method!

# WITH Adapter - make it compatible
class PrinterAdapter:
    def __init__(self, old_printer):
        self.old_printer = old_printer

    def render(self, text):  # New interface
        self.old_printer.print_document(text)  # Calls old interface

# ✓ Now it works!
adapter = PrinterAdapter(OldPrinter())
system.send_to_device(adapter)
```

---

## 1. Object Adapter (Composition)

Uses composition - wraps the adaptee.

```python
from abc import ABC, abstractmethod


# Target interface - what client expects
class MediaPlayer(ABC):
    @abstractmethod
    def play(self, filename: str) -> None:
        pass


# Adaptee - existing incompatible class
class Mp3Player:
    """Old MP3 player with different interface"""

    def play_mp3(self, filename: str) -> None:
        print(f"Playing MP3 file: {filename}")


class VlcPlayer:
    """VLC player with yet another interface"""

    def play_video(self, filename: str) -> None:
        print(f"Playing video file: {filename}")


# Adapter - makes Mp3Player compatible with MediaPlayer
class Mp3Adapter(MediaPlayer):
    """Adapts Mp3Player to MediaPlayer interface"""

    def __init__(self, mp3_player: Mp3Player):
        self.mp3_player = mp3_player

    def play(self, filename: str) -> None:
        """Translate play() to play_mp3()"""
        self.mp3_player.play_mp3(filename)


# Adapter - makes VlcPlayer compatible with MediaPlayer
class VlcAdapter(MediaPlayer):
    """Adapts VlcPlayer to MediaPlayer interface"""

    def __init__(self, vlc_player: VlcPlayer):
        self.vlc_player = vlc_player

    def play(self, filename: str) -> None:
        """Translate play() to play_video()"""
        self.vlc_player.play_video(filename)


# Client code - works with MediaPlayer interface
def play_media(player: MediaPlayer, filename: str):
    """Client expects MediaPlayer interface"""
    player.play(filename)


# Usage - adapters make everything compatible
mp3_adapter = Mp3Adapter(Mp3Player())
play_media(mp3_adapter, "song.mp3")
# Playing MP3 file: song.mp3

vlc_adapter = VlcAdapter(VlcPlayer())
play_media(vlc_adapter, "movie.mp4")
# Playing video file: movie.mp4
```

---

## 2. Class Adapter (Inheritance)

Uses multiple inheritance - inherits from both target and adaptee.

```python
from abc import ABC, abstractmethod


# Target
class Shape(ABC):
    @abstractmethod
    def draw(self) -> None:
        pass


# Adaptee - legacy drawing library
class LegacyRectangle:
    """Old rectangle class with different interface"""

    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int) -> None:
        print(f"Drawing rectangle: ({x1},{y1}) to ({x2},{y2})")


# Class Adapter - inherits from both
class RectangleAdapter(Shape, LegacyRectangle):
    """Adapts LegacyRectangle to Shape interface"""

    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self) -> None:
        """Adapt draw() to draw_rectangle()"""
        self.draw_rectangle(self.x1, self.y1, self.x2, self.y2)


# Usage
def render_shape(shape: Shape):
    shape.draw()


rect = RectangleAdapter(0, 0, 100, 50)
render_shape(rect)
# Drawing rectangle: (0,0) to (100,50)
```

**Note:** Object adapter (composition) is generally preferred in Python over class adapter (multiple inheritance).

---

## 3. Real-World Example: Payment Gateway Adapter

```python
from abc import ABC, abstractmethod
from typing import Dict


# Target interface
class PaymentProcessor(ABC):
    """Standard payment interface for our system"""

    @abstractmethod
    def process_payment(self, amount: float, currency: str) -> Dict:
        pass

    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> Dict:
        pass


# Adaptee 1 - Stripe API (third-party)
class StripeAPI:
    """Stripe's actual API (can't modify this)"""

    def charge(self, amount_cents: int, currency: str) -> Dict:
        print(f"Stripe: Charging {amount_cents} cents {currency}")
        return {
            "stripe_id": "ch_123456",
            "status": "succeeded",
            "amount_cents": amount_cents
        }

    def create_refund(self, charge_id: str, amount_cents: int) -> Dict:
        print(f"Stripe: Refunding {amount_cents} cents for {charge_id}")
        return {
            "refund_id": "re_123456",
            "status": "succeeded"
        }


# Adaptee 2 - PayPal SDK (third-party)
class PayPalSDK:
    """PayPal's actual SDK (can't modify this)"""

    def make_payment(self, amount_dollars: float, currency_code: str) -> Dict:
        print(f"PayPal: Processing ${amount_dollars} {currency_code}")
        return {
            "paypal_transaction_id": "PAY-12345",
            "state": "approved",
            "amount": amount_dollars
        }

    def refund_payment(self, transaction_id: str, amount_dollars: float) -> Dict:
        print(f"PayPal: Refunding ${amount_dollars} for {transaction_id}")
        return {
            "refund_transaction_id": "REFUND-12345",
            "state": "completed"
        }


# Adapter 1 - Makes Stripe compatible
class StripeAdapter(PaymentProcessor):
    """Adapts Stripe API to our PaymentProcessor interface"""

    def __init__(self):
        self.stripe = StripeAPI()

    def process_payment(self, amount: float, currency: str) -> Dict:
        # Convert dollars to cents
        amount_cents = int(amount * 100)

        # Call Stripe's charge method
        stripe_response = self.stripe.charge(amount_cents, currency)

        # Transform to our standard format
        return {
            "transaction_id": stripe_response["stripe_id"],
            "status": "success" if stripe_response["status"] == "succeeded" else "failed",
            "amount": amount,
            "currency": currency,
            "provider": "stripe"
        }

    def refund(self, transaction_id: str, amount: float) -> Dict:
        amount_cents = int(amount * 100)
        stripe_response = self.stripe.create_refund(transaction_id, amount_cents)

        return {
            "refund_id": stripe_response["refund_id"],
            "status": "success" if stripe_response["status"] == "succeeded" else "failed",
            "amount": amount
        }


# Adapter 2 - Makes PayPal compatible
class PayPalAdapter(PaymentProcessor):
    """Adapts PayPal SDK to our PaymentProcessor interface"""

    def __init__(self):
        self.paypal = PayPalSDK()

    def process_payment(self, amount: float, currency: str) -> Dict:
        # PayPal uses different currency format
        currency_code = currency.upper()

        # Call PayPal's make_payment
        paypal_response = self.paypal.make_payment(amount, currency_code)

        # Transform to our standard format
        return {
            "transaction_id": paypal_response["paypal_transaction_id"],
            "status": "success" if paypal_response["state"] == "approved" else "failed",
            "amount": amount,
            "currency": currency,
            "provider": "paypal"
        }

    def refund(self, transaction_id: str, amount: float) -> Dict:
        paypal_response = self.paypal.refund_payment(transaction_id, amount)

        return {
            "refund_id": paypal_response["refund_transaction_id"],
            "status": "success" if paypal_response["state"] == "completed" else "failed",
            "amount": amount
        }


# Client code - works with any payment processor
class PaymentService:
    def __init__(self, processor: PaymentProcessor):
        self.processor = processor

    def charge_customer(self, amount: float, currency: str):
        """Process payment using any provider"""
        print(f"\nProcessing payment of {amount} {currency}...")
        result = self.processor.process_payment(amount, currency)
        print(f"Result: {result}")
        return result

    def refund_customer(self, transaction_id: str, amount: float):
        """Refund using any provider"""
        print(f"\nProcessing refund of {amount}...")
        result = self.processor.refund(transaction_id, amount)
        print(f"Result: {result}")
        return result


# Usage - same interface, different implementations
stripe_service = PaymentService(StripeAdapter())
stripe_service.charge_customer(99.99, "USD")
# Processing payment of 99.99 USD...
# Stripe: Charging 9999 cents USD
# Result: {'transaction_id': 'ch_123456', 'status': 'success', ...}

paypal_service = PaymentService(PayPalAdapter())
paypal_service.charge_customer(99.99, "USD")
# Processing payment of 99.99 USD...
# PayPal: Processing $99.99 USD
# Result: {'transaction_id': 'PAY-12345', 'status': 'success', ...}
```

---

## 4. Two-Way Adapter

Adapter that works in both directions.

```python
class CelsiusTemperature:
    """Works in Celsius"""

    def __init__(self, temp: float):
        self.celsius = temp

    def get_temperature(self) -> float:
        return self.celsius


class FahrenheitTemperature:
    """Works in Fahrenheit"""

    def __init__(self, temp: float):
        self.fahrenheit = temp

    def get_temperature(self) -> float:
        return self.fahrenheit


class TemperatureAdapter:
    """Two-way adapter for temperature conversion"""

    def __init__(self, temp_source):
        self.temp_source = temp_source

    def celsius(self) -> float:
        """Get temperature in Celsius"""
        if isinstance(self.temp_source, CelsiusTemperature):
            return self.temp_source.get_temperature()
        elif isinstance(self.temp_source, FahrenheitTemperature):
            fahrenheit = self.temp_source.get_temperature()
            return (fahrenheit - 32) * 5/9
        raise TypeError("Unknown temperature source")

    def fahrenheit(self) -> float:
        """Get temperature in Fahrenheit"""
        if isinstance(self.temp_source, FahrenheitTemperature):
            return self.temp_source.get_temperature()
        elif isinstance(self.temp_source, CelsiusTemperature):
            celsius = self.temp_source.get_temperature()
            return celsius * 9/5 + 32
        raise TypeError("Unknown temperature source")


# Usage
celsius_temp = CelsiusTemperature(25)
adapter = TemperatureAdapter(celsius_temp)
print(f"{adapter.celsius()}°C = {adapter.fahrenheit()}°F")
# 25.0°C = 77.0°F

fahrenheit_temp = FahrenheitTemperature(77)
adapter = TemperatureAdapter(fahrenheit_temp)
print(f"{adapter.fahrenheit()}°F = {adapter.celsius()}°C")
# 77.0°F = 25.0°C
```

---

## 5. Real-World Example: Database Adapter

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any


# Target interface
class Database(ABC):
    """Standard database interface"""

    @abstractmethod
    def connect(self, connection_string: str) -> None:
        pass

    @abstractmethod
    def execute(self, query: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


# Adaptee 1 - MySQL (third-party library)
class MySQLConnection:
    """Simulated MySQL library"""

    def mysql_connect(self, host: str, user: str, password: str, database: str):
        print(f"MySQL: Connected to {database}@{host}")
        self.connected = True

    def mysql_query(self, sql: str) -> List[tuple]:
        """Returns list of tuples"""
        print(f"MySQL: Executing {sql}")
        return [("Alice", 30), ("Bob", 25)]

    def mysql_close(self):
        print("MySQL: Connection closed")
        self.connected = False


# Adaptee 2 - PostgreSQL (third-party library)
class PostgreSQLClient:
    """Simulated PostgreSQL library"""

    def pg_connect(self, conn_string: str):
        print(f"PostgreSQL: Connected with {conn_string}")
        self.connection = conn_string

    def pg_execute(self, query: str) -> List[Dict]:
        """Returns list of dicts"""
        print(f"PostgreSQL: Executing {query}")
        return [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]

    def pg_disconnect(self):
        print("PostgreSQL: Disconnected")
        self.connection = None


# Adapter 1 - MySQL
class MySQLAdapter(Database):
    """Adapts MySQL to our Database interface"""

    def __init__(self):
        self.mysql = MySQLConnection()

    def connect(self, connection_string: str) -> None:
        # Parse connection string: "mysql://user:pass@host/db"
        parts = connection_string.replace("mysql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")

        self.mysql.mysql_connect(
            host=host_db[0],
            user=user_pass[0],
            password=user_pass[1],
            database=host_db[1]
        )

    def execute(self, query: str) -> List[Dict[str, Any]]:
        # Convert tuples to dicts
        results = self.mysql.mysql_query(query)
        return [
            {"name": row[0], "age": row[1]}
            for row in results
        ]

    def close(self) -> None:
        self.mysql.mysql_close()


# Adapter 2 - PostgreSQL
class PostgreSQLAdapter(Database):
    """Adapts PostgreSQL to our Database interface"""

    def __init__(self):
        self.pg = PostgreSQLClient()

    def connect(self, connection_string: str) -> None:
        # PostgreSQL uses connection string directly
        conn_str = connection_string.replace("postgres://", "")
        self.pg.pg_connect(conn_str)

    def execute(self, query: str) -> List[Dict[str, Any]]:
        # Already returns dicts!
        return self.pg.pg_execute(query)

    def close(self) -> None:
        self.pg.pg_disconnect()


# Client code - database agnostic
class UserRepository:
    """Uses Database interface - doesn't care about implementation"""

    def __init__(self, db: Database):
        self.db = db

    def get_all_users(self) -> List[Dict[str, Any]]:
        return self.db.execute("SELECT name, age FROM users")


# Usage - same code works with both databases
print("=== Using MySQL ===")
mysql_db = MySQLAdapter()
mysql_db.connect("mysql://user:pass@localhost/mydb")
repo = UserRepository(mysql_db)
users = repo.get_all_users()
print(f"Users: {users}")
mysql_db.close()

print("\n=== Using PostgreSQL ===")
pg_db = PostgreSQLAdapter()
pg_db.connect("postgres://user:pass@localhost/mydb")
repo = UserRepository(pg_db)
users = repo.get_all_users()
print(f"Users: {users}")
pg_db.close()
```

---

## 6. Adapter vs Other Patterns

| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| **Adapter** | Make interfaces compatible | Integrate existing code |
| **Decorator** | Add responsibilities | Extend behavior |
| **Proxy** | Control access | Lazy loading, security |
| **Facade** | Simplify interface | Hide complexity |

```python
# Adapter - change interface
class Adapter:
    def new_method(self):
        return self.adaptee.old_method()

# Decorator - add behavior
class Decorator:
    def method(self):
        # Extra behavior
        return self.component.method()

# Proxy - control access
class Proxy:
    def method(self):
        if self.check_access():
            return self.real_object.method()

# Facade - simplify
class Facade:
    def simple_method(self):
        self.subsystem1.complex_method()
        self.subsystem2.complex_method()
```

---

## 7. When to Use Adapter Pattern

### ✅ Use When:

1. **Integrate third-party libraries**
   ```python
   # Wrap library with incompatible interface
   adapter = LibraryAdapter(third_party_lib)
   ```

2. **Support legacy code**
   ```python
   # Adapt old code to new interface
   adapter = LegacyAdapter(old_system)
   ```

3. **Interface incompatibility**
   ```python
   # Make incompatible classes work together
   adapter = SystemAdapter(incompatible_class)
   ```

4. **Reuse existing classes**
   ```python
   # Reuse without modifying original
   adapter = ClassAdapter(existing_class)
   ```

### ❌ Don't Use When:

1. **You can modify the source** - just change it directly
2. **Interfaces are already compatible** - no need for adapter
3. **Too many adaptations needed** - consider redesign

---

## 8. Interview Tips

### Common Questions

**Q: "What's the difference between Adapter and Facade?"**
- **Adapter**: Makes one interface match another (changes interface)
- **Facade**: Provides simple interface to complex system (hides complexity)

**Q: "Adapter vs Decorator?"**
- **Adapter**: Changes interface to match expected interface
- **Decorator**: Keeps same interface, adds behavior

**Q: "When to use Object Adapter vs Class Adapter?"**
- **Object Adapter** (composition): More flexible, Python's preferred way
- **Class Adapter** (inheritance): Can override adaptee methods, uses multiple inheritance

**Q: "Implement an adapter for a third-party API"**
```python
class APIAdapter:
    def __init__(self, api):
        self.api = api

    def standard_method(self):
        # Transform call
        return self.api.vendor_specific_method()
```

### Best Practices

✅ Prefer object adapter (composition) over class adapter
✅ Keep adapter focused - one adaptee per adapter
✅ Document what interface is being adapted
✅ Test adapter independently
✅ Consider adapter when integrating third-party code

### Red Flags

❌ Adapter modifying behavior (use Decorator instead)
❌ Too many adapters (consider redesign)
❌ Adapter with business logic (keep it thin)
❌ Bidirectional dependencies

---

## Quick Reference

### Object Adapter Pattern

```python
# Target
class Target(ABC):
    @abstractmethod
    def request(self):
        pass

# Adaptee
class Adaptee:
    def specific_request(self):
        return "Specific"

# Adapter
class Adapter(Target):
    def __init__(self, adaptee: Adaptee):
        self.adaptee = adaptee

    def request(self):
        return self.adaptee.specific_request()
```

### Class Adapter Pattern

```python
# Target
class Target(ABC):
    @abstractmethod
    def request(self):
        pass

# Adaptee
class Adaptee:
    def specific_request(self):
        return "Specific"

# Adapter - inherits from both
class Adapter(Target, Adaptee):
    def request(self):
        return self.specific_request()
```

---

**Related Patterns:**
- [Facade Pattern](./facade.md) - Simplifies interface
- [Proxy Pattern](./proxy.md) - Controls access
- [Decorator Pattern](./decorator.md) - Adds behavior
- [Bridge Pattern](./bridge.md) - Separates interface from implementation

**Back to:** [Design Patterns](./README.md)
