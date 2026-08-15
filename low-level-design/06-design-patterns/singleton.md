# Singleton Pattern

Ensure a class has only **one instance** and provide a global point of access to it.

## Problem

You need exactly one instance of a class throughout your application:
- Database connection pool
- Configuration manager
- Logger
- Cache
- Thread pool

## Solution

Control instance creation so only one instance exists.

---

## 1. Classic Singleton (Not Thread-Safe!)

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.value = 42

# Test
s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True - same instance

s1.value = 100
print(s2.value)  # 100 - shared state
```

**Problem:** Not thread-safe! Multiple threads can create multiple instances.

---

## 2. Thread-Safe Singleton (Double-Checked Locking)

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.value = 42

# Test with threads
def create_singleton():
    singleton = ThreadSafeSingleton()
    print(f"Singleton ID: {id(singleton)}")

threads = [threading.Thread(target=create_singleton) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# All print same ID - only one instance created!
```

---

## 3. Metaclass Singleton (Pythonic Way)

```python
class SingletonMeta(type):
    """Metaclass that creates a Singleton base class"""
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected to database"

    def query(self, sql):
        return f"Executing: {sql}"

# Test
db1 = Database()
db2 = Database()
print(db1 is db2)  # True

print(db1.query("SELECT * FROM users"))
```

**Advantages:**
- Thread-safe by default
- Clean syntax
- Reusable metaclass
- Works with inheritance

---

## 4. Decorator Singleton

```python
def singleton(cls):
    """Decorator to make a class a singleton"""
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class Logger:
    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(f"[LOG] {message}")

# Test
logger1 = Logger()
logger2 = Logger()
print(logger1 is logger2)  # True

logger1.log("First message")
print(len(logger2.logs))  # 1 - shared state
```

---

## 5. Module-Level Singleton (Simplest!)

Python modules are singletons by default!

```python
# config.py
class Config:
    def __init__(self):
        self.settings = {}

    def set(self, key, value):
        self.settings[key] = value

    def get(self, key):
        return self.settings.get(key)

# Create single instance at module level
config = Config()

# ================================

# main.py
from config import config  # Same instance everywhere!

config.set("debug", True)
print(config.get("debug"))

# other_module.py
from config import config  # Same instance!
print(config.get("debug"))  # True
```

**This is the Pythonic way!** Use modules as singletons.

---

## 6. Real-World Example: Database Connection Pool

```python
import threading
from typing import Optional

class DatabasePool:
    """Thread-safe singleton connection pool"""
    _instance: Optional['DatabasePool'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._connections = []
            self._max_connections = 10
            print("Initializing database pool...")

    def get_connection(self):
        """Get a connection from the pool"""
        if len(self._connections) < self._max_connections:
            connection = f"Connection-{len(self._connections) + 1}"
            self._connections.append(connection)
            print(f"Created {connection}")
            return connection
        return self._connections[0]  # Reuse existing

    def get_stats(self):
        return {
            'total_connections': len(self._connections),
            'max_connections': self._max_connections
        }

# Usage
pool1 = DatabasePool()
pool2 = DatabasePool()
print(pool1 is pool2)  # True

conn1 = pool1.get_connection()
conn2 = pool2.get_connection()
print(pool1.get_stats())  # Same pool!
```

---

## 7. Real-World Example: Application Logger

```python
from datetime import datetime
import threading

class ApplicationLogger:
    """Singleton logger with thread-safe operations"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._logs = []
            self._log_lock = threading.Lock()

    def log(self, level: str, message: str):
        """Thread-safe logging"""
        with self._log_lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}"
            self._logs.append(log_entry)
            print(log_entry)

    def get_logs(self):
        with self._log_lock:
            return self._logs.copy()

    def clear_logs(self):
        with self._log_lock:
            self._logs.clear()

# Usage
logger = ApplicationLogger()
logger.log("INFO", "Application started")
logger.log("ERROR", "Something went wrong")

# From another module - same logger
another_logger = ApplicationLogger()
print(len(another_logger.get_logs()))  # 2 - same logs!
```

---

## 8. Lazy Initialization Singleton

```python
class LazyConnection:
    """Singleton that only initializes when first accessed"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Don't initialize expensive resources here!
        pass

    @property
    def connection(self):
        """Lazy initialization of expensive resource"""
        if not hasattr(self, '_connection'):
            print("Initializing expensive connection...")
            self._connection = "Expensive database connection"
        return self._connection

# Creating instance is cheap
db = LazyConnection()
print("Instance created")

# Connection only created when accessed
print(db.connection)  # "Initializing expensive connection..."
print(db.connection)  # No re-initialization
```

---

## 9. Singleton with Parameters (Registry Pattern)

```python
class DatabaseConnection:
    """Singleton per database (registry pattern)"""
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, db_name: str):
        if db_name not in cls._instances:
            with cls._lock:
                if db_name not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[db_name] = instance
        return cls._instances[db_name]

    def __init__(self, db_name: str):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.db_name = db_name
            self.connection = f"Connected to {db_name}"
            print(f"Initialized connection to {db_name}")

# Different singletons for different databases
db1_conn1 = DatabaseConnection("users_db")
db1_conn2 = DatabaseConnection("users_db")
print(db1_conn1 is db1_conn2)  # True - same instance

db2_conn1 = DatabaseConnection("orders_db")
print(db1_conn1 is db2_conn1)  # False - different database
```

---

## 10. Breaking Singleton (For Testing)

```python
class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.settings = {}

    @classmethod
    def reset_instance(cls):
        """Reset singleton for testing"""
        with cls._lock:
            cls._instance = None

# Test 1
config1 = ConfigManager()
config1.settings['debug'] = True

# Test 2 - reset between tests
ConfigManager.reset_instance()
config2 = ConfigManager()
print(config2.settings)  # {} - clean state
```

---

## 11. When to Use Singleton

### ✅ Good Use Cases

1. **Configuration Management**
   ```python
   config = AppConfig()  # One config for entire app
   ```

2. **Logging**
   ```python
   logger = Logger()  # One logger instance
   ```

3. **Database Connection Pool**
   ```python
   pool = ConnectionPool()  # Manage limited connections
   ```

4. **Cache**
   ```python
   cache = MemoryCache()  # Shared cache
   ```

5. **Thread Pool**
   ```python
   executor = ThreadPoolExecutor()  # Reuse threads
   ```

### ❌ When NOT to Use

1. **Testing is Important**
   - Hard to mock/replace
   - Shared state between tests

2. **Multiple Instances Needed**
   - Different configs for different parts
   - Use dependency injection instead

3. **Just for Global Access**
   - Singleton is not for global variables!
   - Use modules or dependency injection

4. **Stateless Utility Classes**
   - Just use a module with functions

---

## 12. Alternatives to Singleton

### Dependency Injection

```python
# Instead of Singleton
class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

class UserService:
    def __init__(self, db: DatabaseConnection):
        self.db = db  # Injected dependency

# Create once, inject everywhere
db = DatabaseConnection("localhost", 5432)
user_service = UserService(db)
order_service = OrderService(db)
```

### Module-Level Instance (Pythonic!)

```python
# database.py
class _Database:
    def __init__(self):
        self.connection = "Connected"

# Create at module level
database = _Database()

# ================================

# main.py
from database import database  # Import instance directly
database.query("SELECT * FROM users")
```

---

## 13. Interview Tips

### Common Questions

**Q: "Implement a thread-safe singleton"**
```python
# Show double-checked locking
class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Q: "What's wrong with singletons?"**
- Global state (hard to test)
- Hidden dependencies
- Violates Single Responsibility Principle
- Tight coupling

**Q: "How would you test a singleton?"**
- Add `reset()` method
- Use dependency injection instead
- Mock at module level

**Q: "Singleton vs Static class?"**
- Python doesn't have static classes
- Singleton can implement interfaces
- Singleton is lazy-initialized

### Best Practices

✅ Use **module-level instances** (most Pythonic)
✅ Make it **thread-safe** if needed
✅ Use **`__new__`** not `__init__` for instance control
✅ Consider **dependency injection** as alternative
✅ Add **reset method** for testing

### Red Flags

❌ Using singleton for global variables
❌ Not thread-safe in multi-threaded environment
❌ Overusing when dependency injection is better
❌ Making everything a singleton
❌ Ignoring testability issues

---

## Quick Comparison

| Method | Pros | Cons | Use When |
|--------|------|------|----------|
| **Module-level** | Simple, Pythonic | Not lazy | Simple cases |
| **`__new__`** | Explicit control | More code | Need control |
| **Metaclass** | Reusable, clean | Advanced | Multiple singletons |
| **Decorator** | Reusable, clear | Function wrapper | Flexibility |

---

## Complete Example: Application Cache

```python
import threading
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheSingleton:
    """Thread-safe singleton cache with TTL support"""
    _instance: Optional['CacheSingleton'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._cache = {}
            self._cache_lock = threading.Lock()

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set cache value with TTL"""
        with self._cache_lock:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = {'value': value, 'expiry': expiry}

    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        with self._cache_lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.now() < entry['expiry']:
                    return entry['value']
                else:
                    del self._cache[key]  # Expired
        return None

    def clear(self):
        """Clear all cache"""
        with self._cache_lock:
            self._cache.clear()

    def size(self) -> int:
        """Get cache size"""
        with self._cache_lock:
            return len(self._cache)

# Usage
cache = CacheSingleton()
cache.set("user:1", {"name": "Alice", "age": 30}, ttl_seconds=60)

# From another part of application
cache2 = CacheSingleton()
print(cache2.get("user:1"))  # Same cache!
print(cache is cache2)  # True
```

---

**Related Patterns:**
- [Factory Pattern](./factory.md) - Create instances
- [Builder Pattern](./builder.md) - Complex construction

**Back to:** [Design Patterns](./README.md)
