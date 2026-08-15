# Special Methods (Dunder Methods)

Python's **special methods** (also called "dunder methods" for double underscore) allow you to define how objects behave with built-in Python operations.

## What Are Dunder Methods?

Methods with `__double_underscores__` that Python calls automatically in specific situations.

```python
class Book:
    def __init__(self, title):
        self.title = title

    def __str__(self):
        return f"Book: {self.title}"

book = Book("1984")
print(book)  # Python calls __str__() automatically
```

---

## 1. Object Lifecycle

### `__new__` - Object Creation (Before `__init__`)

Called to create a new instance. Rarely needed except for immutable types or metaclasses.

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.value = 42

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True - same instance
```

### `__init__` - Object Initialization

Most common - initialize object after creation.

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        print(f"Initialized {name}")

person = Person("Alice", 30)  # Calls __init__
```

### `__del__` - Object Destruction

Called when object is garbage collected. **Not reliable** - use context managers instead.

```python
class File:
    def __init__(self, filename):
        self.file = open(filename, 'w')

    def __del__(self):
        # Unreliable! Might not be called
        self.file.close()

# Better: Use context manager with __enter__ and __exit__
```

---

## 2. String Representation

### `__str__` - User-Friendly String

For end users. Used by `print()` and `str()`.

```python
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name}: ${self.price:.2f}"

product = Product("Laptop", 999.99)
print(product)  # Laptop: $999.99
```

### `__repr__` - Developer String

For developers. Should be unambiguous, ideally recreate object.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

p = Point(3, 4)
print(p)         # (3, 4) - uses __str__
print(repr(p))   # Point(3, 4) - uses __repr__
print([p])       # [Point(3, 4)] - lists use __repr__
```

**Best Practice:** Always implement `__repr__`. If no `__str__`, Python uses `__repr__`.

---

## 3. Comparison Methods

### `__eq__` - Equality (`==`)

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.age == other.age

p1 = Person("Alice", 30)
p2 = Person("Alice", 30)
p3 = Person("Bob", 25)

print(p1 == p2)  # True
print(p1 == p3)  # False
```

### `__ne__` - Not Equal (`!=`)

Usually auto-generated from `__eq__`, but can override.

### `__lt__`, `__le__`, `__gt__`, `__ge__` - Comparison

```python
from functools import total_ordering

@total_ordering  # Only need __eq__ and one comparison
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def __eq__(self, other):
        return self.grade == other.grade

    def __lt__(self, other):
        return self.grade < other.grade

students = [
    Student("Alice", 85),
    Student("Bob", 92),
    Student("Charlie", 78)
]

sorted_students = sorted(students)  # Uses __lt__
for s in sorted_students:
    print(f"{s.name}: {s.grade}")
# Output:
# Charlie: 78
# Alice: 85
# Bob: 92
```

### `__hash__` - Hashable Objects

Required for using objects in sets or as dict keys.

**Rule:** If `__eq__` is defined, must also define `__hash__` (or objects can't be in sets/dicts).

```python
class Book:
    def __init__(self, isbn, title):
        self.isbn = isbn
        self.title = title

    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return self.isbn == other.isbn

    def __hash__(self):
        # Hash should be based on immutable attributes
        return hash(self.isbn)

book1 = Book("978-0-13-468599-1", "Clean Code")
book2 = Book("978-0-13-468599-1", "Clean Code")

# Can use in set/dict
books = {book1, book2}  # Only one entry (they're equal)
print(len(books))  # 1

# Can use as dict key
book_info = {book1: "Great book"}
```

**Important:** If objects are mutable, don't make them hashable!

---

## 4. Container Methods

### `__len__` - Length

```python
class Playlist:
    def __init__(self):
        self.songs = []

    def add(self, song):
        self.songs.append(song)

    def __len__(self):
        return len(self.songs)

playlist = Playlist()
playlist.add("Song 1")
playlist.add("Song 2")
print(len(playlist))  # 2 - calls __len__
```

### `__getitem__` - Index Access (`obj[key]`)

```python
class Playlist:
    def __init__(self):
        self.songs = []

    def add(self, song):
        self.songs.append(song)

    def __getitem__(self, index):
        return self.songs[index]

    def __len__(self):
        return len(self.songs)

playlist = Playlist()
playlist.add("Song 1")
playlist.add("Song 2")

print(playlist[0])  # Song 1 - calls __getitem__
print(playlist[-1]) # Song 2

# Also enables slicing
print(playlist[0:1])  # ['Song 1']

# And iteration!
for song in playlist:
    print(song)
```

### `__setitem__` - Index Assignment

```python
class Playlist:
    def __init__(self):
        self.songs = []

    def __getitem__(self, index):
        return self.songs[index]

    def __setitem__(self, index, value):
        self.songs[index] = value

playlist = Playlist()
playlist.songs = ["Song 1", "Song 2"]
playlist[0] = "New Song"  # Calls __setitem__
print(playlist[0])  # New Song
```

### `__contains__` - Membership (`in`)

```python
class Playlist:
    def __init__(self):
        self.songs = []

    def add(self, song):
        self.songs.append(song)

    def __contains__(self, song):
        return song in self.songs

playlist = Playlist()
playlist.add("Song 1")

print("Song 1" in playlist)  # True - calls __contains__
print("Song 2" in playlist)  # False
```

---

## 5. Numeric Methods

### Arithmetic Operators

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Addition: v1 + v2"""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Subtraction: v1 - v2"""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """Multiplication: v * 3"""
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        """Division: v / 2"""
        return Vector(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1 + v2)  # Vector(4, 6)
print(v1 - v2)  # Vector(-2, -2)
print(v1 * 3)   # Vector(3, 6)
print(v2 / 2)   # Vector(1.5, 2.0)
```

### In-Place Operations

```python
class Counter:
    def __init__(self, value=0):
        self.value = value

    def __iadd__(self, other):
        """In-place addition: counter += 5"""
        self.value += other
        return self  # Must return self!

    def __isub__(self, other):
        """In-place subtraction: counter -= 3"""
        self.value -= other
        return self

counter = Counter(10)
counter += 5  # Calls __iadd__
print(counter.value)  # 15
```

---

## 6. Context Managers

### `__enter__` and `__exit__` - `with` Statement

```python
class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        """Called when entering 'with' block"""
        print(f"Opening connection to {self.db_name}")
        self.connection = f"Connection to {self.db_name}"
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block"""
        print(f"Closing connection to {self.db_name}")
        self.connection = None
        # Return False to propagate exceptions
        # Return True to suppress exceptions
        return False

# Usage
with DatabaseConnection("mydb") as conn:
    print(f"Using {conn}")
    # Connection automatically closed after block
# Output:
# Opening connection to mydb
# Using Connection to mydb
# Closing connection to mydb
```

**Real-World Example: File Handler**

```python
class FileHandler:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False

# Usage - file automatically closed
with FileHandler('data.txt', 'w') as f:
    f.write('Hello, World!')
```

---

## 7. Iterator Protocol

### `__iter__` and `__next__` - Make Objects Iterable

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        """Return iterator object (self)"""
        return self

    def __next__(self):
        """Return next item or raise StopIteration"""
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

# Usage
for num in Countdown(5):
    print(num)
# Output: 5, 4, 3, 2, 1
```

**Better Pattern: Separate Iterator**

```python
class Playlist:
    def __init__(self):
        self.songs = []

    def add(self, song):
        self.songs.append(song)

    def __iter__(self):
        """Return separate iterator object"""
        return PlaylistIterator(self.songs)

class PlaylistIterator:
    def __init__(self, songs):
        self.songs = songs
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.songs):
            raise StopIteration
        song = self.songs[self.index]
        self.index += 1
        return song

playlist = Playlist()
playlist.add("Song 1")
playlist.add("Song 2")

for song in playlist:
    print(song)
```

**Simplest: Use Generator**

```python
class Playlist:
    def __init__(self):
        self.songs = []

    def __iter__(self):
        """Return generator"""
        for song in self.songs:
            yield song

# Or even simpler - just delegate
class Playlist:
    def __init__(self):
        self.songs = []

    def __iter__(self):
        return iter(self.songs)
```

---

## 8. Callable Objects

### `__call__` - Make Object Callable

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, x):
        """Called when object is used like a function"""
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10 - calls __call__
print(triple(5))  # 15
```

**Use Case: Stateful Functions**

```python
class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __call__(self):
        """Check if call is allowed"""
        import time
        now = time.time()

        # Remove old calls
        self.calls = [t for t in self.calls if now - t < self.period]

        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

limiter = RateLimiter(max_calls=5, period=60)  # 5 calls per minute

if limiter():  # Calls __call__
    print("Request allowed")
else:
    print("Rate limited")
```

---

## 9. Attribute Access

### `__getattr__` - Missing Attribute

Called when attribute is not found.

```python
class DynamicObject:
    def __init__(self):
        self.data = {'name': 'Alice', 'age': 30}

    def __getattr__(self, key):
        """Called when attribute not found normally"""
        if key in self.data:
            return self.data[key]
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

obj = DynamicObject()
print(obj.name)  # Alice - calls __getattr__
print(obj.age)   # 30
# print(obj.invalid)  # AttributeError
```

### `__setattr__` - Attribute Assignment

Called on ALL attribute assignments.

```python
class ValidatedPerson:
    def __setattr__(self, key, value):
        """Called on EVERY attribute assignment"""
        if key == 'age' and value < 0:
            raise ValueError("Age cannot be negative")
        # Must use super().__setattr__ to avoid infinite recursion
        super().__setattr__(key, value)

person = ValidatedPerson()
person.name = "Alice"  # OK
person.age = 30        # OK
# person.age = -5      # ValueError
```

### `__delattr__` - Attribute Deletion

```python
class ProtectedObject:
    def __init__(self):
        self.data = "important"

    def __delattr__(self, key):
        if key == 'data':
            raise AttributeError("Cannot delete 'data'")
        super().__delattr__(key)

obj = ProtectedObject()
# del obj.data  # AttributeError
```

---

## 10. Complete Example: Custom List

```python
class MyList:
    """Custom list with all special methods"""

    def __init__(self, items=None):
        self._items = list(items) if items else []

    # String representation
    def __repr__(self):
        return f"MyList({self._items})"

    def __str__(self):
        return str(self._items)

    # Container methods
    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __setitem__(self, index, value):
        self._items[index] = value

    def __contains__(self, item):
        return item in self._items

    # Iterator
    def __iter__(self):
        return iter(self._items)

    # Comparison
    def __eq__(self, other):
        if isinstance(other, MyList):
            return self._items == other._items
        return False

    # Arithmetic
    def __add__(self, other):
        if isinstance(other, MyList):
            return MyList(self._items + other._items)
        raise TypeError("Can only add MyList to MyList")

    # Boolean
    def __bool__(self):
        return bool(self._items)

# Usage
lst = MyList([1, 2, 3])
print(lst)              # [1, 2, 3]
print(len(lst))         # 3
print(lst[0])           # 1
print(2 in lst)         # True
print(lst + MyList([4, 5]))  # MyList([1, 2, 3, 4, 5])

for item in lst:
    print(item)         # 1, 2, 3
```

---

## 11. Interview Tips

### Common Questions
1. **"Explain the difference between `__str__` and `__repr__`"**
   - `__str__`: Human-readable for users
   - `__repr__`: Unambiguous for developers

2. **"Why do you need `__hash__` if you define `__eq__`?"**
   - Objects need to be hashable for sets/dicts
   - Equal objects must have same hash

3. **"What's a context manager and when to use it?"**
   - `__enter__` and `__exit__`
   - For resource management (files, connections, locks)

### Best Practices
- ✅ Always implement `__repr__`
- ✅ If `__eq__`, also implement `__hash__` (or set to None)
- ✅ Use `@total_ordering` for comparison methods
- ✅ Prefer context managers over `__del__`
- ✅ Use generators for `__iter__` when possible

### Red Flags
- ❌ Implementing `__getattr__` without understanding recursion
- ❌ Modifying objects in `__hash__`
- ❌ Relying on `__del__` for cleanup
- ❌ Not returning `self` in in-place operators (`__iadd__`, etc.)

---

## Quick Reference

| Method | Operator/Function | Purpose |
|--------|-------------------|---------|
| `__init__` | - | Initialize object |
| `__str__` | `str()`, `print()` | User-friendly string |
| `__repr__` | `repr()` | Developer string |
| `__eq__` | `==` | Equality |
| `__lt__` | `<` | Less than |
| `__hash__` | `hash()`, `set()`, `dict` | Hashable |
| `__len__` | `len()` | Length |
| `__getitem__` | `obj[key]` | Index access |
| `__setitem__` | `obj[key] = val` | Index assignment |
| `__contains__` | `in` | Membership test |
| `__iter__` | `for x in obj` | Iterator |
| `__next__` | `next()` | Next item |
| `__enter__`/`__exit__` | `with` | Context manager |
| `__call__` | `obj()` | Callable |
| `__add__` | `+` | Addition |

---

**Next:** [Interfaces and Abstract Classes →](./interfaces-abstract-classes.md)
