# Python Must-Knows for Low-Level Design

Essential Python concepts with real-world examples for LLD interviews.

## 📚 Contents

1. [Collections & Data Structures](#1-collections--data-structures)
2. [List & Dictionary Comprehensions](#2-list--dictionary-comprehensions)
3. [Generators & Iterators](#3-generators--iterators)
4. [Decorators & Functools](#4-decorators--functools)
5. [Type Hints & Dataclasses](#5-type-hints--dataclasses)
6. [Context Managers](#6-context-managers)
7. [Error Handling](#7-error-handling)
8. [Advanced Function Features](#8-advanced-function-features)
9. [Functional Programming](#9-functional-programming)
10. [String Operations & Formatting](#10-string-operations--formatting)
11. [Advanced Itertools](#11-advanced-itertools)
12. [File & JSON Operations](#12-file--json-operations)
13. [Modern Python Features](#13-modern-python-features)
14. [Advanced Data Structures](#14-advanced-data-structures)
15. [Common Patterns](#15-common-patterns)

---

## 1. Collections & Data Structures

### defaultdict - Avoid KeyError

**Problem:** Counting items, grouping by key

```python
from collections import defaultdict

# BAD - Check if key exists
word_count = {}
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
for word in words:
    if word not in word_count:
        word_count[word] = 0
    word_count[word] += 1

# GOOD - defaultdict
word_count = defaultdict(int)
for word in words:
    word_count[word] += 1

print(word_count)  # {'apple': 3, 'banana': 2, 'cherry': 1}
```

**Real-World: Group users by role**

```python
from collections import defaultdict

users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "user"},
    {"name": "Charlie", "role": "admin"},
    {"name": "David", "role": "user"},
]

# Group by role
users_by_role = defaultdict(list)
for user in users:
    users_by_role[user["role"]].append(user["name"])

print(users_by_role)
# {'admin': ['Alice', 'Charlie'], 'user': ['Bob', 'David']}
```

### Counter - Count Occurrences

```python
from collections import Counter

# Count frequencies
votes = ["Alice", "Bob", "Alice", "Charlie", "Alice", "Bob"]
vote_count = Counter(votes)

print(vote_count.most_common(2))  # [('Alice', 3), ('Bob', 2)]
print(vote_count["Alice"])  # 3
```

**Real-World: Find most popular products**

```python
from collections import Counter

orders = [
    {"product": "Laptop", "quantity": 2},
    {"product": "Mouse", "quantity": 5},
    {"product": "Laptop", "quantity": 1},
    {"product": "Keyboard", "quantity": 3},
]

# Count total quantity per product
product_sales = Counter()
for order in orders:
    product_sales[order["product"]] += order["quantity"]

top_products = product_sales.most_common(2)
print(top_products)  # [('Mouse', 5), ('Laptop', 3)]
```

### deque - Fast Queue Operations

```python
from collections import deque

# BAD - List as queue (O(n) for pop(0))
queue = [1, 2, 3]
queue.pop(0)  # Slow!

# GOOD - deque (O(1) for both ends)
queue = deque([1, 2, 3])
queue.popleft()  # Fast!
queue.append(4)
queue.appendleft(0)
```

**Real-World: Request queue in web server**

```python
from collections import deque

class RequestQueue:
    def __init__(self, max_size=100):
        self.queue = deque(maxlen=max_size)

    def add_request(self, request):
        """Add request to queue"""
        if len(self.queue) >= self.queue.maxlen:
            dropped = self.queue.popleft()  # Drop oldest
            print(f"Queue full, dropped: {dropped}")
        self.queue.append(request)

    def process_next(self):
        """Process oldest request"""
        if self.queue:
            return self.queue.popleft()
        return None

# Usage
server = RequestQueue(max_size=3)
server.add_request("Request-1")
server.add_request("Request-2")
server.add_request("Request-3")
server.add_request("Request-4")  # Drops Request-1
```

### OrderedDict - Maintain Insertion Order

```python
from collections import OrderedDict

# LRU Cache implementation
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)

# Usage
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))  # 1
cache.put(3, 3)  # Evicts key 2
print(cache.get(2))  # -1 (not found)
```

---

## 2. List & Dictionary Comprehensions

### List Comprehensions

```python
# BAD - Verbose loop
squares = []
for i in range(10):
    squares.append(i ** 2)

# GOOD - List comprehension
squares = [i ** 2 for i in range(10)]

# With condition
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
```

**Real-World: Filter and transform objects**

```python
class User:
    def __init__(self, name, age, active):
        self.name = name
        self.age = age
        self.active = active

users = [
    User("Alice", 25, True),
    User("Bob", 17, False),
    User("Charlie", 30, True),
]

# Get names of active adult users
adult_names = [u.name for u in users if u.active and u.age >= 18]
print(adult_names)  # ['Alice', 'Charlie']
```

### Dictionary Comprehensions

```python
# Create dict from list
users = ["Alice", "Bob", "Charlie"]
user_ids = {name: idx for idx, name in enumerate(users)}
# {'Alice': 0, 'Bob': 1, 'Charlie': 2}

# Invert dictionary
inverted = {v: k for k, v in user_ids.items()}
# {0: 'Alice', 1: 'Bob', 2: 'Charlie'}

# Filter dictionary
prices = {"apple": 1.20, "banana": 0.50, "cherry": 3.00}
expensive = {k: v for k, v in prices.items() if v > 1.0}
# {'apple': 1.20, 'cherry': 3.00}
```

**Real-World: Transform API response**

```python
# API returns list of dicts
api_response = [
    {"id": 1, "name": "Product A", "price": 100},
    {"id": 2, "name": "Product B", "price": 200},
    {"id": 3, "name": "Product C", "price": 150},
]

# Create lookup by ID
products_by_id = {p["id"]: p for p in api_response}

# Create name -> price mapping
price_lookup = {p["name"]: p["price"] for p in api_response}
```

### Set Comprehensions

```python
# Unique values
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = {x for x in numbers}  # {1, 2, 3, 4}

# Filter unique values
unique_evens = {x for x in numbers if x % 2 == 0}  # {2, 4}
```

---

## 3. Generators & Iterators

### Generators - Memory Efficient

```python
# BAD - Loads everything in memory
def get_squares(n):
    result = []
    for i in range(n):
        result.append(i ** 2)
    return result

squares = get_squares(1_000_000)  # Uses lots of memory!

# GOOD - Generator (lazy evaluation)
def get_squares(n):
    for i in range(n):
        yield i ** 2

squares = get_squares(1_000_000)  # Barely uses memory!
for sq in squares:
    print(sq)  # Generated on-demand
```

**Real-World: Read large file line by line**

```python
def read_large_file(file_path):
    """Generator to read file line by line"""
    with open(file_path, 'r') as f:
        for line in f:
            yield line.strip()

# Process huge file without loading into memory
for line in read_large_file("huge_log.txt"):
    if "ERROR" in line:
        print(line)
```

**Real-World: Infinite sequence (event stream)**

```python
def event_stream():
    """Generate events infinitely"""
    event_id = 0
    while True:
        yield f"Event-{event_id}"
        event_id += 1

# Use with itertools.islice to limit
from itertools import islice

events = event_stream()
first_10 = list(islice(events, 10))
print(first_10)  # ['Event-0', 'Event-1', ..., 'Event-9']
```

### Generator Expressions

```python
# Like list comprehension but lazy
squares = (x ** 2 for x in range(1_000_000))  # Generator, not list!

# Use in sum, max, any, all
total = sum(x ** 2 for x in range(1000))  # Memory efficient
```

---

## 4. Decorators & Functools

### Custom Decorators

```python
import time
from functools import wraps

def timer(func):
    """Measure execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def process_data(items):
    return sum(items)

process_data([1, 2, 3, 4, 5])
# process_data took 0.0001s
```

### @lru_cache - Memoization

```python
from functools import lru_cache

# BAD - Recalculates every time
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# GOOD - Caches results
@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(100))  # Fast!
```

**Real-World: Cache expensive computations**

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=128)
def get_user_data(user_id):
    """Cache API calls"""
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

# First call - hits API
data1 = get_user_data(123)

# Second call - returns cached result
data2 = get_user_data(123)  # Instant!
```

### @partial - Partial Function Application

```python
from functools import partial

def send_email(subject, body, from_addr, to_addr):
    print(f"From: {from_addr}")
    print(f"To: {to_addr}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")

# Create specialized function
send_notification = partial(
    send_email,
    from_addr="notifications@example.com"
)

# Now only need 3 arguments
send_notification(
    subject="Welcome!",
    body="Thanks for signing up",
    to_addr="user@example.com"
)
```

---

## 5. Type Hints & Dataclasses

### Type Hints

```python
from typing import List, Dict, Optional, Union, Tuple

def process_users(
    users: List[Dict[str, str]],
    filter_role: Optional[str] = None
) -> List[str]:
    """
    Process user list and return names.

    Args:
        users: List of user dictionaries
        filter_role: Optional role filter

    Returns:
        List of user names
    """
    if filter_role:
        return [u["name"] for u in users if u["role"] == filter_role]
    return [u["name"] for u in users]
```

### Dataclasses - Clean Data Objects

```python
from dataclasses import dataclass, field
from typing import List

# BAD - Manual __init__, __repr__, __eq__
class User:
    def __init__(self, name: str, age: int, tags: List[str] = None):
        self.name = name
        self.age = age
        self.tags = tags or []

    def __repr__(self):
        return f"User(name={self.name}, age={self.age}, tags={self.tags})"

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age

# GOOD - Dataclass (automatic!)
@dataclass
class User:
    name: str
    age: int
    tags: List[str] = field(default_factory=list)

    def is_adult(self) -> bool:
        return self.age >= 18

# Usage
user = User(name="Alice", age=25, tags=["admin", "active"])
print(user)  # User(name='Alice', age=25, tags=['admin', 'active'])
print(user.is_adult())  # True
```

**Real-World: Domain models**

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Order:
    order_id: str
    user_id: str
    total: float
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def mark_completed(self) -> None:
        self.status = "completed"

@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int = 0

    def is_available(self) -> bool:
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        if quantity > self.stock:
            raise ValueError("Insufficient stock")
        self.stock -= quantity

# Usage
product = Product("P001", "Laptop", 999.99, stock=10)
order = Order("O001", "U123", 999.99)

if product.is_available():
    product.reduce_stock(1)
    order.mark_completed()
```

---

## 6. Context Managers

### with Statement - Automatic Cleanup

```python
# BAD - Manual file handling
f = open("data.txt", "r")
try:
    data = f.read()
finally:
    f.close()

# GOOD - Context manager
with open("data.txt", "r") as f:
    data = f.read()
# File automatically closed
```

### Custom Context Manager

```python
from contextlib import contextmanager

@contextmanager
def database_transaction(connection):
    """Context manager for database transactions"""
    try:
        yield connection
        connection.commit()
        print("Transaction committed")
    except Exception as e:
        connection.rollback()
        print(f"Transaction rolled back: {e}")
        raise

# Usage
with database_transaction(conn) as db:
    db.execute("INSERT INTO users VALUES (...)")
    db.execute("UPDATE accounts SET ...")
# Auto-commit or rollback
```

**Real-World: Lock management**

```python
import threading
from contextlib import contextmanager

class ThreadSafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    @contextmanager
    def acquire_lock(self):
        """Context manager for lock"""
        self.lock.acquire()
        try:
            yield
        finally:
            self.lock.release()

    def increment(self):
        with self.acquire_lock():
            self.count += 1

# Usage
counter = ThreadSafeCounter()
counter.increment()  # Thread-safe!
```

---

## 7. Error Handling

### Try-Except Best Practices

```python
# BAD - Catch everything
try:
    result = risky_operation()
except:  # Too broad!
    pass

# GOOD - Specific exceptions
try:
    result = risky_operation()
except ValueError as e:
    print(f"Invalid value: {e}")
except KeyError as e:
    print(f"Missing key: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise  # Re-raise if can't handle
```

**Real-World: API error handling**

```python
import requests
from typing import Optional, Dict

def fetch_user_data(user_id: int) -> Optional[Dict]:
    """Fetch user data with proper error handling"""
    try:
        response = requests.get(
            f"https://api.example.com/users/{user_id}",
            timeout=5
        )
        response.raise_for_status()  # Raise for 4xx/5xx
        return response.json()

    except requests.Timeout:
        print(f"Request timed out for user {user_id}")
        return None

    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print(f"User {user_id} not found")
        else:
            print(f"HTTP error: {e}")
        return None

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    except ValueError:  # JSON decode error
        print("Invalid JSON response")
        return None
```

### Custom Exceptions

```python
class InsufficientFundsError(Exception):
    """Raised when account has insufficient funds"""
    pass

class AccountFrozenError(Exception):
    """Raised when account is frozen"""
    pass

class BankAccount:
    def __init__(self, balance: float):
        self.balance = balance
        self.frozen = False

    def withdraw(self, amount: float) -> None:
        if self.frozen:
            raise AccountFrozenError("Account is frozen")

        if amount > self.balance:
            raise InsufficientFundsError(
                f"Insufficient funds: balance={self.balance}, requested={amount}"
            )

        self.balance -= amount

# Usage
account = BankAccount(100)
try:
    account.withdraw(150)
except InsufficientFundsError as e:
    print(f"Error: {e}")
```

---

## 8. Advanced Function Features

### *args and **kwargs

```python
def flexible_function(*args, **kwargs):
    """Accept any arguments"""
    print(f"Positional args: {args}")
    print(f"Keyword args: {kwargs}")

flexible_function(1, 2, 3, name="Alice", age=25)
# Positional args: (1, 2, 3)
# Keyword args: {'name': 'Alice', 'age': 25}
```

**Real-World: Logger with variable arguments**

```python
from datetime import datetime
from typing import Any

class Logger:
    def log(self, level: str, message: str, **context: Any) -> None:
        """Log message with arbitrary context"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {level}: {message}")

        if context:
            print("Context:")
            for key, value in context.items():
                print(f"  {key}: {value}")

# Usage
logger = Logger()
logger.log("ERROR", "Database connection failed",
           host="localhost",
           port=5432,
           error="Connection timeout")
```

### Lambda Functions

```python
# Sort by custom key
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 20},
]

# Sort by age
sorted_by_age = sorted(users, key=lambda u: u["age"])

# Filter
adults = list(filter(lambda u: u["age"] >= 21, users))

# Map
names = list(map(lambda u: u["name"].upper(), users))
```

---

## 9. Functional Programming

### Lambda Functions

```python
# Sort by custom criteria
users = [
    {"name": "Alice", "age": 25, "score": 95},
    {"name": "Bob", "age": 30, "score": 88},
    {"name": "Charlie", "age": 20, "score": 92},
]

# Multiple sort keys
sorted_users = sorted(users, key=lambda u: (-u["score"], u["age"]))
print(sorted_users)  # Sorted by score desc, then age asc
```

**Real-World: Event filtering and processing**

```python
class Event:
    def __init__(self, event_type, timestamp, user_id):
        self.event_type = event_type
        self.timestamp = timestamp
        self.user_id = user_id

events = [
    Event("login", 100, "user1"),
    Event("purchase", 200, "user2"),
    Event("login", 150, "user1"),
    Event("logout", 300, "user1"),
]

# Filter events by type
logins = list(filter(lambda e: e.event_type == "login", events))

# Get unique user IDs
user_ids = set(map(lambda e: e.user_id, events))

# Sort by timestamp
sorted_events = sorted(events, key=lambda e: e.timestamp)
```


### map(), filter(), reduce()

```python
from functools import reduce

# Map - transform each element
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
# [1, 4, 9, 16, 25]

# Filter - keep only matching elements
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4]

# Reduce - accumulate to single value
total = reduce(lambda acc, x: acc + x, numbers, 0)
# 15

# Product of all numbers
product = reduce(lambda acc, x: acc * x, numbers, 1)
# 120
```

**Real-World: Order processing pipeline**

```python
from functools import reduce
from typing import List, Dict

orders = [
    {"id": 1, "items": 3, "price": 100, "status": "completed"},
    {"id": 2, "items": 1, "price": 50, "status": "pending"},
    {"id": 3, "items": 5, "price": 200, "status": "completed"},
    {"id": 4, "items": 2, "price": 75, "status": "cancelled"},
]

# Filter completed orders
completed = list(filter(lambda o: o["status"] == "completed", orders))

# Calculate total revenue
total_revenue = reduce(
    lambda total, order: total + order["price"],
    completed,
    0
)
print(f"Total revenue: ${total_revenue}")  # $300

# Apply discount (map)
discounted = list(map(
    lambda o: {**o, "price": o["price"] * 0.9},
    completed
))
```

### any() and all()

```python
# any() - at least one True
numbers = [1, 3, 5, 7, 8]
has_even = any(x % 2 == 0 for x in numbers)  # True

# all() - all True
all_positive = all(x > 0 for x in numbers)  # True
```

**Real-World: Validation**

```python
from typing import List, Dict

class Validator:
    @staticmethod
    def validate_user(user: Dict) -> bool:
        """User is valid if has all required fields"""
        required = ["name", "email", "age"]
        return all(field in user for field in required)

    @staticmethod
    def has_permission(user: Dict, required_permissions: List[str]) -> bool:
        """User has at least one required permission"""
        user_permissions = user.get("permissions", [])
        return any(perm in user_permissions for perm in required_permissions)

# Usage
user = {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25,
    "permissions": ["read", "write"]
}

print(Validator.validate_user(user))  # True
print(Validator.has_permission(user, ["admin", "write"]))  # True
```

---

## 10. String Operations & Formatting

### f-strings (Modern & Fast)

```python
name = "Alice"
age = 25
score = 95.567

# f-string - recommended!
message = f"{name} is {age} years old"

# With expressions
result = f"{name.upper()} scored {score:.2f}%"

# Multi-line
report = f"""
Name: {name}
Age: {age}
Score: {score:.1f}%
"""
```

**Real-World: Log formatting**

```python
from datetime import datetime

class Logger:
    def log(self, level: str, message: str, **context):
        timestamp = datetime.now().isoformat()
        base = f"[{timestamp}] {level.upper()}: {message}"

        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            return f"{base} | {context_str}"
        return base

logger = Logger()
print(logger.log("error", "Database connection failed",
                 host="localhost", port=5432, retry=3))
# [2024-01-15T10:30:00] ERROR: Database connection failed | host=localhost | port=5432 | retry=3
```

### String Methods

```python
text = "  Hello World  "

# Cleaning
text.strip()        # "Hello World"
text.lower()        # "  hello world  "
text.upper()        # "  HELLO WORLD  "
text.title()        # "  Hello World  "

# Checking
text.startswith("  Hello")  # True
text.endswith("World  ")    # True
"123".isdigit()             # True
"abc".isalpha()             # True

# Splitting/Joining
words = text.strip().split()  # ["Hello", "World"]
"-".join(words)               # "Hello-World"

# Replacing
text.replace("World", "Python")  # "  Hello Python  "
```

**Real-World: URL parsing and validation**

```python
class URLParser:
    def __init__(self, url: str):
        self.url = url

    def get_domain(self) -> str:
        """Extract domain from URL"""
        # Remove protocol
        without_protocol = self.url.split("://")[-1]
        # Get domain (before /)
        domain = without_protocol.split("/")[0]
        return domain

    def get_path(self) -> str:
        """Extract path from URL"""
        parts = self.url.split("://")[-1].split("/", 1)
        return "/" + parts[1] if len(parts) > 1 else "/"

    def is_secure(self) -> bool:
        """Check if HTTPS"""
        return self.url.startswith("https://")

# Usage
url = URLParser("https://api.example.com/v1/users/123")
print(url.get_domain())   # api.example.com
print(url.get_path())     # /v1/users/123
print(url.is_secure())    # True
```

### Regular Expressions

```python
import re

# Pattern matching
text = "Contact: alice@example.com or bob@test.com"

# Find all emails
emails = re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', text)
# ['alice@example.com', 'bob@test.com']

# Replace pattern
cleaned = re.sub(r'\s+', ' ', "Hello    World")
# "Hello World"

# Validation
phone_pattern = r'^\d{3}-\d{3}-\d{4}$'
is_valid = bool(re.match(phone_pattern, "123-456-7890"))  # True
```

**Real-World: Input validation**

```python
import re
from typing import Optional

class InputValidator:
    EMAIL_PATTERN = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    PHONE_PATTERN = r'^\d{3}-\d{3}-\d{4}$'
    PASSWORD_PATTERN = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        return bool(re.match(cls.EMAIL_PATTERN, email))

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone format"""
        return bool(re.match(cls.PHONE_PATTERN, phone))

    @classmethod
    def validate_password(cls, password: str) -> bool:
        """Password: 8+ chars, uppercase, lowercase, digit"""
        return bool(re.match(cls.PASSWORD_PATTERN, password))

    @classmethod
    def extract_mentions(cls, text: str) -> list:
        """Extract @mentions from text"""
        return re.findall(r'@(\w+)', text)

# Usage
print(InputValidator.validate_email("alice@example.com"))  # True
print(InputValidator.validate_password("Secure123"))       # True
print(InputValidator.extract_mentions("Hello @alice and @bob!"))
# ['alice', 'bob']
```

---

## 11. Advanced Itertools

### itertools - Powerful Iteration Tools

```python
from itertools import (
    chain, combinations, permutations,
    groupby, islice, cycle, repeat
)

# Chain - flatten multiple iterables
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined = list(chain(list1, list2))  # [1, 2, 3, 4, 5, 6]

# Combinations - unique pairs
pairs = list(combinations([1, 2, 3, 4], 2))
# [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]

# Permutations - all orderings
perms = list(permutations([1, 2, 3], 2))
# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

# Groupby - group consecutive items
data = [1, 1, 2, 2, 2, 3, 1, 1]
groups = [(k, list(g)) for k, g in groupby(data)]
# [(1, [1, 1]), (2, [2, 2, 2]), (3, [3]), (1, [1, 1])]

# Islice - slice iterator
numbers = range(100)
first_10 = list(islice(numbers, 10))  # [0, 1, ..., 9]

# Cycle - repeat infinitely
counter = cycle([1, 2, 3])
# next(counter) -> 1, 2, 3, 1, 2, 3, ...
```

**Real-World: Task scheduler with round-robin**

```python
from itertools import cycle, islice
from typing import List

class RoundRobinScheduler:
    def __init__(self, workers: List[str]):
        self.workers = cycle(workers)  # Infinite cycle

    def assign_tasks(self, tasks: List[str]) -> dict:
        """Assign tasks to workers in round-robin"""
        assignments = {}
        for task in tasks:
            worker = next(self.workers)
            if worker not in assignments:
                assignments[worker] = []
            assignments[worker].append(task)
        return assignments

# Usage
scheduler = RoundRobinScheduler(["Worker-1", "Worker-2", "Worker-3"])
tasks = [f"Task-{i}" for i in range(10)]
result = scheduler.assign_tasks(tasks)

for worker, assigned in result.items():
    print(f"{worker}: {assigned}")
# Worker-1: ['Task-0', 'Task-3', 'Task-6', 'Task-9']
# Worker-2: ['Task-1', 'Task-4', 'Task-7']
# Worker-3: ['Task-2', 'Task-5', 'Task-8']
```

---

## 12. Modern Python Features (3.8+)

### Walrus Operator (:=)

```python
# OLD - compute twice
data = get_data()
if len(data) > 10:
    process(data)

# NEW - compute once with walrus
if (n := len(get_data())) > 10:
    print(f"Processing {n} items")
    process(data)

# In while loops
while (line := file.readline()):
    process(line)
```

**Real-World: Validation with computed values**

```python
class OrderValidator:
    def validate_order(self, order: dict) -> tuple[bool, str]:
        """Validate order and return result with message"""

        # Check stock with walrus operator
        if (available := self.check_stock(order["product_id"])) < order["quantity"]:
            return False, f"Insufficient stock: {available} available"

        # Check price
        if (price := self.get_price(order["product_id"])) != order["price"]:
            return False, f"Price mismatch: expected {price}"

        return True, "Order valid"

    def check_stock(self, product_id: str) -> int:
        return 5

    def get_price(self, product_id: str) -> float:
        return 99.99
```

### Unpacking Operators (* and **)

```python
# Unpack lists
numbers = [1, 2, 3]
print(*numbers)  # 1 2 3 (instead of [1, 2, 3])

# Merge lists
list1 = [1, 2]
list2 = [3, 4]
merged = [*list1, *list2]  # [1, 2, 3, 4]

# Unpack dicts
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
merged = {**dict1, **dict2}  # {'a': 1, 'b': 2, 'c': 3, 'd': 4}

# Override values
defaults = {"timeout": 30, "retry": 3}
custom = {"timeout": 60}
config = {**defaults, **custom}  # {'timeout': 60, 'retry': 3}
```

**Real-World: API request builder**

```python
class APIClient:
    def __init__(self, base_url: str, default_headers: dict = None):
        self.base_url = base_url
        self.default_headers = default_headers or {}

    def request(self, endpoint: str, **kwargs):
        """Make request with default + custom headers"""
        # Merge default and custom headers
        headers = {**self.default_headers, **kwargs.get("headers", {})}

        # Build final config
        config = {
            "url": f"{self.base_url}{endpoint}",
            "headers": headers,
            **kwargs  # Include other params (timeout, etc.)
        }

        return config

# Usage
client = APIClient(
    "https://api.example.com",
    default_headers={"Authorization": "Bearer token123"}
)

response = client.request(
    "/users",
    headers={"Content-Type": "application/json"},
    timeout=30
)
```

---

## 13. Quick Reference: When to Use What

### Decision Guide

| Need | Use | Example |
|------|-----|---------|
| Count/Group items | `Counter`, `defaultdict` | Frequency count, group by key |
| Fast queue operations | `deque` | Request queue, sliding window |
| Cache expensive calls | `@lru_cache` | API calls, computations |
| Clean data objects | `@dataclass` | Domain models, DTOs |
| Memory efficient iteration | Generators | Large files, infinite streams |
| Transform collections | Comprehensions | Filter, map lists/dicts |
| Multiple arguments | `*args`, `**kwargs` | Flexible functions |
| Sort/Filter | `sorted()`, `filter()`, `lambda` | Custom sorting, filtering |
| Validate | `any()`, `all()` | Check conditions |
| Pattern matching | `re` (regex) | Email, phone validation |
| Priority ordering | `heapq` | Task scheduling |
| Round-robin | `itertools.cycle` | Load balancing |
| Combinations | `itertools.combinations` | Test cases |

### Common Interview Patterns

```python
# Pattern 1: Frequency count
from collections import Counter
freq = Counter(items)
most_common = freq.most_common(k)

# Pattern 2: Group by key
from collections import defaultdict
groups = defaultdict(list)
for item in items:
    groups[item.key].append(item)

# Pattern 3: Sliding window
from collections import deque
window = deque(maxlen=k)
for item in items:
    window.append(item)

# Pattern 4: LRU Cache
from functools import lru_cache
@lru_cache(maxsize=128)
def expensive_function(n):
    ...

# Pattern 5: Priority queue
import heapq
heap = []
heapq.heappush(heap, (priority, item))
next_item = heapq.heappop(heap)

# Pattern 6: Validation
all(condition(x) for x in items)  # All must pass
any(condition(x) for x in items)  # At least one passes

# Pattern 7: Transform and filter
result = [transform(x) for x in items if condition(x)]

# Pattern 8: Merge dicts
merged = {**defaults, **overrides}

# Pattern 9: Parse structured data
first, *middle, last = items

# Pattern 10: Compute once, use many times
if (result := expensive_computation()) > threshold:
    use(result)
```

---

**📚 Related Topics:**
- [OOP Fundamentals](./03-oop-fundamentals/) - Classes and objects
- [Design Patterns](./06-design-patterns/) - Common patterns
- [Async Patterns](./async-patterns.md) - Concurrency
- [Special Methods](./03-oop-fundamentals/special-methods.md) - Dunder methods

---

**Back to:** [Main README](./README.md) | [Learning Guide](./LEARNING-GUIDE.md)

---

## 14. Common LLD Patterns

### Singleton Pattern (Pythonic Way)

```python
# Module-level singleton
class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connected = False
        return cls._instance

    def connect(self):
        if not self.connected:
            print("Connecting to database...")
            self.connected = True

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # True - same instance
```

### Enum for Constants

```python
from enum import Enum, auto

class OrderStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = OrderStatus.PENDING

    def ship(self):
        if self.status == OrderStatus.PROCESSING:
            self.status = OrderStatus.SHIPPED
        else:
            raise ValueError(f"Cannot ship order in {self.status} state")

# Usage
order = Order("O123")
print(order.status)  # OrderStatus.PENDING
```

### Method Chaining (Fluent Interface)

```python
class QueryBuilder:
    def __init__(self):
        self.filters = []
        self.sort_by = None
        self.limit_value = None

    def where(self, condition: str):
        self.filters.append(condition)
        return self  # Enable chaining!

    def order_by(self, field: str):
        self.sort_by = field
        return self

    def limit(self, n: int):
        self.limit_value = n
        return self

    def build(self) -> str:
        query = "SELECT * FROM table"
        if self.filters:
            query += " WHERE " + " AND ".join(self.filters)
        if self.sort_by:
            query += f" ORDER BY {self.sort_by}"
        if self.limit_value:
            query += f" LIMIT {self.limit_value}"
        return query

# Usage - method chaining
query = (QueryBuilder()
    .where("age > 18")
    .where("status = 'active'")
    .order_by("created_at")
    .limit(10)
    .build())

print(query)
# SELECT * FROM table WHERE age > 18 AND status = 'active' ORDER BY created_at LIMIT 10
```

