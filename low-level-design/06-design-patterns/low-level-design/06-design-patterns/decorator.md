# Decorator Pattern

Add responsibilities to objects dynamically without modifying their code. Wrap objects to extend behavior.

**Note:** This is the **Decorator design pattern**, not Python's `@decorator` syntax (though Python decorators are inspired by this pattern).

## Why Decorator?

**Problems it solves:**
- Need to add features to objects without changing their class
- Avoid subclass explosion (too many combinations)
- Add/remove responsibilities at runtime
- Follow Open/Closed Principle

```python
# WITHOUT Decorator - subclass explosion
class Coffee: pass
class CoffeeWithMilk(Coffee): pass
class CoffeeWithSugar(Coffee): pass
class CoffeeWithMilkAndSugar(Coffee): pass  # Combinatorial explosion!
class CoffeeWithMilkAndSugarAndWhippedCream(Coffee): pass  # Gets worse...

# WITH Decorator - composable
coffee = Coffee()
coffee = MilkDecorator(coffee)
coffee = SugarDecorator(coffee)
coffee = WhippedCreamDecorator(coffee)
```

---

## 1. Classic Decorator Pattern

```python
from abc import ABC, abstractmethod


# Component interface
class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


# Concrete component
class SimpleCoffee(Coffee):
    def cost(self) -> float:
        return 2.0

    def description(self) -> str:
        return "Simple coffee"


# Decorator base class
class CoffeeDecorator(Coffee):
    """Base decorator - wraps a Coffee"""

    def __init__(self, coffee: Coffee):
        self._coffee = coffee

    def cost(self) -> float:
        return self._coffee.cost()

    def description(self) -> str:
        return self._coffee.description()


# Concrete decorators
class MilkDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.5

    def description(self) -> str:
        return self._coffee.description() + ", milk"


class SugarDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.2

    def description(self) -> str:
        return self._coffee.description() + ", sugar"


class WhippedCreamDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 0.7

    def description(self) -> str:
        return self._coffee.description() + ", whipped cream"


# Usage - wrap dynamically
coffee = SimpleCoffee()
print(f"{coffee.description()}: ${coffee.cost()}")
# Simple coffee: $2.0

# Add milk
coffee = MilkDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost()}")
# Simple coffee, milk: $2.5

# Add sugar
coffee = SugarDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost()}")
# Simple coffee, milk, sugar: $2.7

# Add whipped cream
coffee = WhippedCreamDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost()}")
# Simple coffee, milk, sugar, whipped cream: $3.4
```

---

## 2. Python Function Decorators

Python's `@decorator` syntax is inspired by the decorator pattern.

### Simple Function Decorator

```python
import time
from functools import wraps


def timer(func):
    """Decorator that times function execution"""

    @wraps(func)  # Preserve original function metadata
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result

    return wrapper


@timer  # Syntactic sugar for: slow_function = timer(slow_function)
def slow_function():
    time.sleep(1)
    return "Done"


result = slow_function()
# slow_function took 1.0012 seconds
print(result)  # Done
```

### Decorator with Arguments

```python
def repeat(times):
    """Decorator that repeats function calls"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return decorator


@repeat(times=3)
def greet(name):
    return f"Hello, {name}!"


results = greet("Alice")
print(results)
# ['Hello, Alice!', 'Hello, Alice!', 'Hello, Alice!']
```

### Stacking Decorators

```python
def uppercase(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper


def exclaim(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return f"{result}!"
    return wrapper


@exclaim      # Applied second (outer)
@uppercase    # Applied first (inner)
def greet(name):
    return f"hello, {name}"


print(greet("Alice"))  # HELLO, ALICE!
# Equivalent to: exclaim(uppercase(greet))("Alice")
```

---

## 3. Real-World Example: Logging & Caching

```python
import time
from functools import wraps
from typing import Callable, Any


def log_calls(func: Callable) -> Callable:
    """Log function calls"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned {result}")
        return result

    return wrapper


def cache(func: Callable) -> Callable:
    """Cache function results"""
    cache_dict = {}

    @wraps(func)
    def wrapper(*args):
        if args in cache_dict:
            print(f"[CACHE] Hit for {func.__name__}{args}")
            return cache_dict[args]

        print(f"[CACHE] Miss for {func.__name__}{args}")
        result = func(*args)
        cache_dict[args] = result
        return result

    return wrapper


def timer(func: Callable) -> Callable:
    """Time function execution"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[TIMER] {func.__name__} took {elapsed:.4f}s")
        return result

    return wrapper


# Stack multiple decorators
@log_calls
@cache
@timer
def expensive_computation(n: int) -> int:
    """Simulate expensive computation"""
    time.sleep(0.5)  # Simulate work
    return n * n


# First call - cache miss
result = expensive_computation(5)
# [LOG] Calling expensive_computation with args=(5,), kwargs={}
# [CACHE] Miss for expensive_computation(5,)
# [TIMER] expensive_computation took 0.5012s
# [LOG] expensive_computation returned 25

print()

# Second call - cache hit
result = expensive_computation(5)
# [LOG] Calling expensive_computation with args=(5,), kwargs={}
# [CACHE] Hit for expensive_computation(5,)
# [LOG] expensive_computation returned 25
```

---

## 4. Class Decorators

Decorators that modify classes.

```python
def singleton(cls):
    """Decorator to make a class a singleton"""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Database:
    def __init__(self):
        print("Connecting to database...")
        self.connection = "DB Connection"


# All calls return same instance
db1 = Database()  # Connecting to database...
db2 = Database()  # (no output - same instance)
print(db1 is db2)  # True
```

### Add Methods to Classes

```python
def add_str_method(cls):
    """Add __str__ method to class"""

    def __str__(self):
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"

    cls.__str__ = __str__
    return cls


@add_str_method
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


person = Person("Alice", 30)
print(person)  # Person(name=Alice, age=30)
```

---

## 5. Authorization & Validation Decorators

```python
from functools import wraps


class AuthorizationError(Exception):
    pass


class ValidationError(Exception):
    pass


# Simulated current user
current_user = {"role": "admin", "id": 1}


def require_role(role: str):
    """Decorator to check user role"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.get("role") != role:
                raise AuthorizationError(f"Requires {role} role")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_positive(param_name: str):
    """Decorator to validate parameter is positive"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = kwargs.get(param_name)
            if value is not None and value <= 0:
                raise ValidationError(f"{param_name} must be positive")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@require_role("admin")
@validate_positive("amount")
def process_refund(order_id: int, amount: float):
    """Process refund (admin only, positive amount)"""
    print(f"Processing ${amount} refund for order {order_id}")
    return True


# Success
try:
    process_refund(123, amount=50.0)
    # Processing $50.0 refund for order 123
except (AuthorizationError, ValidationError) as e:
    print(f"Error: {e}")

# Validation error
try:
    process_refund(123, amount=-10.0)
except ValidationError as e:
    print(f"Error: {e}")
    # Error: amount must be positive

# Authorization error
current_user = {"role": "user", "id": 2}
try:
    process_refund(123, amount=50.0)
except AuthorizationError as e:
    print(f"Error: {e}")
    # Error: Requires admin role
```

---

## 6. Retry Decorator

```python
import time
from functools import wraps
from typing import Callable


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions=(Exception,)):
    """Retry decorator for handling transient failures"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        print(f"[RETRY] Failed after {max_attempts} attempts")
                        raise
                    print(f"[RETRY] Attempt {attempts} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


# Simulate flaky API call
call_count = 0


@retry(max_attempts=3, delay=0.5, exceptions=(ConnectionError,))
def flaky_api_call():
    """Fails twice, succeeds on third attempt"""
    global call_count
    call_count += 1

    if call_count < 3:
        raise ConnectionError(f"Network error (attempt {call_count})")

    return "Success!"


# Test
try:
    result = flaky_api_call()
    # [RETRY] Attempt 1 failed: Network error (attempt 1). Retrying in 0.5s...
    # [RETRY] Attempt 2 failed: Network error (attempt 2). Retrying in 0.5s...
    print(result)  # Success!
except ConnectionError as e:
    print(f"Failed: {e}")
```

---

## 7. Rate Limiting Decorator

```python
import time
from functools import wraps
from collections import deque


def rate_limit(calls: int, period: float):
    """Rate limiting decorator"""

    def decorator(func):
        timestamps = deque()

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old timestamps
            while timestamps and now - timestamps[0] > period:
                timestamps.popleft()

            # Check rate limit
            if len(timestamps) >= calls:
                wait_time = period - (now - timestamps[0])
                raise Exception(f"Rate limited. Try again in {wait_time:.1f}s")

            # Record call
            timestamps.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator


@rate_limit(calls=3, period=10.0)  # Max 3 calls per 10 seconds
def api_call(endpoint: str):
    """Simulated API call"""
    print(f"Calling API endpoint: {endpoint}")
    return {"status": "success"}


# Test rate limiting
for i in range(5):
    try:
        result = api_call(f"/endpoint{i}")
        print(f"Call {i+1}: {result}")
    except Exception as e:
        print(f"Call {i+1}: {e}")
    time.sleep(2)  # Wait between calls
```

---

## 8. Decorator Pattern vs Python @decorator

| Aspect | Decorator Pattern | Python @decorator |
|--------|------------------|-------------------|
| **Type** | Object-oriented | Function-based |
| **Wraps** | Objects | Functions/methods |
| **Runtime** | Add behavior at runtime | Applied at definition time |
| **Composition** | Explicit wrapping | @ syntax sugar |
| **Use Case** | Wrap objects | Wrap functions |

```python
# Decorator Pattern - OOP
coffee = SimpleCoffee()
coffee = MilkDecorator(coffee)
coffee = SugarDecorator(coffee)

# Python @decorator - Functional
@timer
@cache
def compute(x):
    return x * x
```

---

## 9. When to Use Decorator Pattern

### ✅ Use When:

1. **Add responsibilities dynamically**
   ```python
   # Different combinations at runtime
   text = PlainText("Hello")
   text = BoldDecorator(text)
   text = ItalicDecorator(text)
   ```

2. **Avoid subclass explosion**
   ```python
   # Instead of: BoldItalicUnderlineText class
   # Use: decorators composed dynamically
   ```

3. **Follow Open/Closed Principle**
   ```python
   # Add new decorators without modifying existing code
   class NewDecorator(BaseDecorator): ...
   ```

4. **Composable functionality**
   ```python
   @log
   @cache
   @timer
   def func(): ...
   ```

### ❌ Don't Use When:

1. **Simple extension** - just use inheritance
2. **Order matters and is complex** - can get confusing
3. **Overhead not justified** - wrapping adds small cost

---

## 10. Interview Tips

### Common Questions

**Q: "Decorator Pattern vs Inheritance?"**
- **Decorator**: Runtime, flexible composition
- **Inheritance**: Compile-time, static structure

**Q: "How does Python @decorator relate to Decorator pattern?"**
- Inspired by it, but functional not object-oriented
- Both wrap and extend behavior

**Q: "Implement a caching decorator"**
```python
def cache(func):
    cache_dict = {}
    def wrapper(*args):
        if args not in cache_dict:
            cache_dict[args] = func(*args)
        return cache_dict[args]
    return wrapper
```

**Q: "Why use @wraps(func)?"**
- Preserves original function's `__name__`, `__doc__`, etc.
- Important for debugging and introspection

### Best Practices

✅ Use `@wraps(func)` in function decorators
✅ Keep decorators focused (single responsibility)
✅ Document decorator behavior clearly
✅ Test decorators independently
✅ Consider decorator order carefully

### Red Flags

❌ Decorators with side effects
❌ Too many stacked decorators (hard to debug)
❌ Not preserving function metadata
❌ Decorators that modify arguments unexpectedly

---

## Quick Reference

### Classic Decorator Pattern

```python
# Component
class Component(ABC):
    @abstractmethod
    def operation(self):
        pass

# Decorator
class Decorator(Component):
    def __init__(self, component: Component):
        self._component = component

    def operation(self):
        return self._component.operation()

# Concrete Decorator
class ConcreteDecorator(Decorator):
    def operation(self):
        return f"Extra({self._component.operation()})"
```

### Python Function Decorator

```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Before
        result = func(*args, **kwargs)
        # After
        return result
    return wrapper

@decorator
def function():
    pass
```

### Decorator with Arguments

```python
def decorator(arg):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use arg here
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator

@decorator(arg="value")
def function():
    pass
```

---

**Related Patterns:**
- [Proxy Pattern](./proxy.md) - Controls access
- [Adapter Pattern](./adapter.md) - Changes interface
- [Strategy Pattern](./strategy.md) - Swappable algorithms

**Back to:** [Design Patterns](./README.md)
