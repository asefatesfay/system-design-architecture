# Strategy Pattern

## Overview

**Strategy Pattern** allows you to define a family of algorithms, encapsulate each one, and make them interchangeable. The algorithm can vary independently from clients that use it.

**Type**: Behavioral Pattern
**Interview Frequency**: ⭐⭐⭐ VERY HIGH

> **🌍 Multi-Language Note:** Examples use Python. For other languages:
> - [Language Comparison - Strategy Pattern](../lld-coding/multi-language/LANGUAGE-COMPARISON.md#design-patterns-syntax)
> - [Abstraction Multi-Language](../03-oop-fundamentals/four-pillars/#2-abstraction) - Shows interface-based patterns in all languages

## When to Use

- You have multiple ways to accomplish the same task
- You want to switch between algorithms at runtime
- You want to avoid conditional statements (if/else, switch)
- Different behaviors should be easily swappable

## Real-World Examples

- Payment methods (Credit Card, PayPal, UPI)
- Sorting algorithms (Quick Sort, Merge Sort, Bubble Sort)
- Compression algorithms (ZIP, RAR, 7Z)
- Route finding (Fastest, Shortest, Scenic)
- Discount calculations (Seasonal, Member, Bulk)

## Structure

```
Context
  └── uses Strategy interface
       ├── ConcreteStrategyA
       ├── ConcreteStrategyB
       └── ConcreteStrategyC
```

## Implementation

### Basic Example: Payment Processing

```python
from abc import ABC, abstractmethod

# Strategy Interface
class PaymentStrategy(ABC):
    """Defines the interface for all payment methods"""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

# Concrete Strategy 1
class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str, cvv: str, expiry: str):
        self.card_number = card_number
        self.cvv = cvv
        self.expiry = expiry

    def validate(self) -> bool:
        # Validate card details
        return len(self.card_number) == 16 and len(self.cvv) == 3

    def pay(self, amount: float) -> bool:
        if self.validate():
            print(f"Paid ${amount:.2f} using Credit Card ending in {self.card_number[-4:]}")
            return True
        return False

# Concrete Strategy 2
class PayPalPayment(PaymentStrategy):
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def validate(self) -> bool:
        return "@" in self.email

    def pay(self, amount: float) -> bool:
        if self.validate():
            print(f"Paid ${amount:.2f} using PayPal account {self.email}")
            return True
        return False

# Concrete Strategy 3
class UPIPayment(PaymentStrategy):
    def __init__(self, upi_id: str):
        self.upi_id = upi_id

    def validate(self) -> bool:
        return "@" in self.upi_id

    def pay(self, amount: float) -> bool:
        if self.validate():
            print(f"Paid ${amount:.2f} using UPI ID {self.upi_id}")
            return True
        return False

# Concrete Strategy 4
class CryptoPayment(PaymentStrategy):
    def __init__(self, wallet_address: str, crypto_type: str):
        self.wallet_address = wallet_address
        self.crypto_type = crypto_type

    def validate(self) -> bool:
        return len(self.wallet_address) > 20

    def pay(self, amount: float) -> bool:
        if self.validate():
            print(f"Paid ${amount:.2f} using {self.crypto_type}")
            return True
        return False

# Context
class ShoppingCart:
    def __init__(self):
        self.items = []
        self.payment_strategy: PaymentStrategy = None

    def add_item(self, item: str, price: float):
        self.items.append((item, price))

    def calculate_total(self) -> float:
        return sum(price for _, price in self.items)

    def set_payment_strategy(self, strategy: PaymentStrategy):
        """Client sets the strategy at runtime"""
        self.payment_strategy = strategy

    def checkout(self) -> bool:
        if not self.payment_strategy:
            print("Please select a payment method")
            return False

        total = self.calculate_total()
        print(f"\nTotal: ${total:.2f}")
        return self.payment_strategy.pay(total)

# Usage
cart = ShoppingCart()
cart.add_item("Laptop", 999.99)
cart.add_item("Mouse", 29.99)

# User chooses payment method at runtime
print("=== Payment with Credit Card ===")
cart.set_payment_strategy(CreditCardPayment("1234567812345678", "123", "12/25"))
cart.checkout()

print("\n=== Payment with PayPal ===")
cart.set_payment_strategy(PayPalPayment("user@example.com", "password"))
cart.checkout()

print("\n=== Payment with UPI ===")
cart.set_payment_strategy(UPIPayment("user@paytm"))
cart.checkout()

print("\n=== Payment with Crypto ===")
cart.set_payment_strategy(CryptoPayment("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "Bitcoin"))
cart.checkout()
```

**Output**:
```
=== Payment with Credit Card ===
Total: $1029.98
Paid $1029.98 using Credit Card ending in 5678

=== Payment with PayPal ===
Total: $1029.98
Paid $1029.98 using PayPal account user@example.com

=== Payment with UPI ===
Total: $1029.98
Paid $1029.98 using UPI ID user@paytm

=== Payment with Crypto ===
Total: $1029.98
Paid $1029.98 using Bitcoin
```

## Advanced Example: Navigation System

```python
from abc import ABC, abstractmethod
from typing import List, Tuple

# Strategy Interface
class RouteStrategy(ABC):
    @abstractmethod
    def calculate_route(self, start: str, end: str) -> List[str]:
        pass

    @abstractmethod
    def estimate_time(self, distance: float) -> float:
        pass

# Concrete Strategies
class FastestRoute(RouteStrategy):
    def calculate_route(self, start: str, end: str) -> List[str]:
        return [start, "Highway", "Express Lane", end]

    def estimate_time(self, distance: float) -> float:
        avg_speed = 80  # km/h on highway
        return distance / avg_speed

class ShortestRoute(RouteStrategy):
    def calculate_route(self, start: str, end: str) -> List[str]:
        return [start, "Direct Road", end]

    def estimate_time(self, distance: float) -> float:
        avg_speed = 60  # km/h on direct road
        return distance / avg_speed

class ScenicRoute(RouteStrategy):
    def calculate_route(self, start: str, end: str) -> List[str]:
        return [start, "Beach Road", "Mountain Pass", "Lake View", end]

    def estimate_time(self, distance: float) -> float:
        avg_speed = 40  # km/h on scenic route (slower, more stops)
        return distance / avg_speed * 1.5  # Add 50% for sightseeing

class EcoFriendlyRoute(RouteStrategy):
    def calculate_route(self, start: str, end: str) -> List[str]:
        return [start, "Flat Roads", "City Center", end]

    def estimate_time(self, distance: float) -> float:
        avg_speed = 50  # km/h, optimized for fuel efficiency
        return distance / avg_speed

# Context
class NavigationSystem:
    def __init__(self, route_strategy: RouteStrategy):
        self.route_strategy = route_strategy

    def set_route_strategy(self, strategy: RouteStrategy):
        """Change strategy at runtime"""
        self.route_strategy = strategy

    def navigate(self, start: str, end: str, distance: float):
        print(f"\nNavigating from {start} to {end} ({distance} km)")
        print(f"Strategy: {self.route_strategy.__class__.__name__}")

        route = self.route_strategy.calculate_route(start, end)
        time = self.route_strategy.estimate_time(distance)

        print(f"Route: {' → '.join(route)}")
        print(f"Estimated time: {time:.1f} hours")

# Usage
nav = NavigationSystem(FastestRoute())

# Try different strategies
nav.navigate("Home", "Office", 100)

nav.set_route_strategy(ShortestRoute())
nav.navigate("Home", "Office", 100)

nav.set_route_strategy(ScenicRoute())
nav.navigate("Home", "Office", 100)

nav.set_route_strategy(EcoFriendlyRoute())
nav.navigate("Home", "Office", 100)
```

## Real Interview Example: Sorting Strategy

```python
from abc import ABC, abstractmethod
from typing import List

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        pass

class BubbleSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class QuickSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class MergeSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        if len(data) <= 1:
            return data

        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])

        return self._merge(left, right)

    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

# Context with smart strategy selection
class DataSorter:
    def __init__(self):
        self.strategy = None

    def sort(self, data: List[int]) -> List[int]:
        # Auto-select strategy based on data size
        if len(data) < 10:
            self.strategy = BubbleSort()
            print("Using Bubble Sort (small dataset)")
        elif len(data) < 1000:
            self.strategy = QuickSort()
            print("Using Quick Sort (medium dataset)")
        else:
            self.strategy = MergeSort()
            print("Using Merge Sort (large dataset)")

        return self.strategy.sort(data)

    def sort_with_strategy(self, data: List[int], strategy: SortStrategy) -> List[int]:
        """Let user choose specific strategy"""
        self.strategy = strategy
        return self.strategy.sort(data)

# Usage
sorter = DataSorter()

# Auto strategy selection
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = sorter.sort(data)
print(f"Sorted: {sorted_data}\n")

# Manual strategy selection
large_data = list(range(1000, 0, -1))
sorted_data = sorter.sort_with_strategy(large_data, QuickSort())
print(f"First 10: {sorted_data[:10]}")
```

## Benefits

✅ **Open/Closed Principle**: Can add new strategies without modifying context
✅ **Single Responsibility**: Each strategy encapsulates one algorithm
✅ **Runtime flexibility**: Switch strategies dynamically
✅ **Eliminates conditionals**: No big if/else or switch statements
✅ **Testable**: Each strategy can be tested independently

## Drawbacks

❌ Client must be aware of different strategies
❌ Increased number of classes
❌ Overhead if strategies are simple

## Strategy vs Other Patterns

### Strategy vs State
```python
# Strategy: Client chooses
cart.set_payment_strategy(CreditCardPayment())  # External choice

# State: Object changes internally
order.ship()  # Order changes its own state to SHIPPED
```

### Strategy vs Template Method
```python
# Strategy: Entire algorithm is replaced
sorter.set_strategy(QuickSort())  # Complete different algorithm

# Template Method: Steps are overridden
class DataProcessor(ABC):
    def process(self):
        self.load()      # Template defines flow
        self.transform() # Subclass overrides steps
        self.save()
```

## Interview Questions

**Q: When would you use Strategy pattern?**
A: When you have multiple algorithms for the same task and want to switch between them at runtime. For example, different payment methods in an e-commerce system.

**Q: How does Strategy relate to SOLID?**
A: It follows:
- **Open/Closed**: Add new strategies without modifying existing code
- **Single Responsibility**: Each strategy does one thing
- **Dependency Inversion**: Context depends on abstraction (Strategy interface)

**Q: Can you give a real-world example?**
A: Yes! A navigation app offering Fastest, Shortest, and Scenic routes. The user chooses, but the app implements each strategy differently.

## Key Takeaways

1. Use Strategy when you have multiple interchangeable algorithms
2. Client chooses which strategy to use
3. Eliminates conditional logic
4. Makes adding new strategies easy
5. Each strategy is independently testable

## Practice Exercise

**Design a Discount System** with these strategies:
- No Discount
- Percentage Discount (10%, 20%, etc.)
- Fixed Amount Discount ($10 off, $50 off)
- Buy 2 Get 1 Free
- Seasonal Discount (varies by date)

Implement the Strategy pattern to handle all discount types!

---

**Next Pattern**: [Observer Pattern →](./observer.md)
