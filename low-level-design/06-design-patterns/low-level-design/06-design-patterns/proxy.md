# Proxy Pattern

Provide a surrogate or placeholder for another object to control access to it.

## Why Proxy?

**Problems it solves:**
- Expensive object creation (lazy loading)
- Access control and security
- Remote object access
- Logging and monitoring
- Caching

```python
# WITHOUT Proxy - always loads immediately
large_image = RealImage("huge_file.jpg")  # Loads 100MB immediately!

# WITH Proxy - loads only when needed
image = ImageProxy("huge_file.jpg")  # Doesn't load yet
# ... do other work ...
image.display()  # Only now loads the actual image
```

---

## 1. Types of Proxies

### Virtual Proxy (Lazy Loading)

Delays object creation until needed.

```python
from abc import ABC, abstractmethod


class Image(ABC):
    """Subject interface"""

    @abstractmethod
    def display(self) -> None:
        pass


class RealImage(Image):
    """Real expensive object"""

    def __init__(self, filename: str):
        self.filename = filename
        self.load_from_disk()  # Expensive operation!

    def load_from_disk(self) -> None:
        print(f"Loading image from disk: {self.filename}")
        # Simulate expensive loading
        import time
        time.sleep(1)

    def display(self) -> None:
        print(f"Displaying image: {self.filename}")


class ImageProxy(Image):
    """Virtual proxy - delays loading"""

    def __init__(self, filename: str):
        self.filename = filename
        self._real_image = None  # Not created yet!

    def display(self) -> None:
        """Lazy loading - create real image only when needed"""
        if self._real_image is None:
            print("Proxy: Creating real image...")
            self._real_image = RealImage(self.filename)

        self._real_image.display()


# Usage
print("Creating proxy...")
image = ImageProxy("large_photo.jpg")  # Instant! No loading yet

print("\nDoing other work...")
# ... application continues ...

print("\nNow displaying image...")
image.display()  # Only now loads from disk

print("\nDisplaying again...")
image.display()  # Uses cached real image

# Output:
# Creating proxy...
# Doing other work...
# Now displaying image...
# Proxy: Creating real image...
# Loading image from disk: large_photo.jpg
# Displaying image: large_photo.jpg
# Displaying again...
# Displaying image: large_photo.jpg
```

---

## 2. Protection Proxy (Access Control)

Controls access based on permissions.

```python
from abc import ABC, abstractmethod
from typing import Optional


class Document(ABC):
    """Subject interface"""

    @abstractmethod
    def display(self) -> str:
        pass

    @abstractmethod
    def edit(self, content: str) -> bool:
        pass


class RealDocument(Document):
    """Real document"""

    def __init__(self, content: str):
        self.content = content

    def display(self) -> str:
        return self.content

    def edit(self, content: str) -> bool:
        self.content = content
        return True


class User:
    """User with role"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role


class DocumentProxy(Document):
    """Protection proxy - controls access"""

    def __init__(self, document: RealDocument, user: User):
        self._document = document
        self._user = user

    def display(self) -> str:
        """Anyone can read"""
        print(f"Proxy: {self._user.name} is reading document")
        return self._document.display()

    def edit(self, content: str) -> bool:
        """Only admins and editors can write"""
        if self._user.role in ["admin", "editor"]:
            print(f"Proxy: {self._user.name} ({self._user.role}) allowed to edit")
            return self._document.edit(content)
        else:
            print(f"Proxy: {self._user.name} ({self._user.role}) DENIED edit access")
            return False


# Usage
document = RealDocument("Original content")

# Admin user - full access
admin = User("Alice", "admin")
admin_proxy = DocumentProxy(document, admin)

print(admin_proxy.display())  # ✓ Allowed
# Proxy: Alice is reading document
# Original content

admin_proxy.edit("Admin's new content")  # ✓ Allowed
# Proxy: Alice (admin) allowed to edit

# Viewer user - read-only
viewer = User("Bob", "viewer")
viewer_proxy = DocumentProxy(document, viewer)

print(viewer_proxy.display())  # ✓ Allowed
# Proxy: Bob is reading document
# Admin's new content

viewer_proxy.edit("Trying to edit")  # ❌ Denied
# Proxy: Bob (viewer) DENIED edit access
```

---

## 3. Remote Proxy

Represents object in different address space (e.g., different server).

```python
from typing import Dict, Any
import json


class RemoteService(ABC):
    """Interface for remote service"""

    @abstractmethod
    def get_data(self, key: str) -> Any:
        pass

    @abstractmethod
    def set_data(self, key: str, value: Any) -> bool:
        pass


class RealRemoteService(RemoteService):
    """Actual remote service (running on server)"""

    def __init__(self):
        self._storage: Dict[str, Any] = {}

    def get_data(self, key: str) -> Any:
        print(f"[SERVER] Getting {key}")
        return self._storage.get(key)

    def set_data(self, key: str, value: Any) -> bool:
        print(f"[SERVER] Setting {key} = {value}")
        self._storage[key] = value
        return True


class RemoteServiceProxy(RemoteService):
    """Remote proxy - handles network communication"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        # In real implementation, would establish connection

    def get_data(self, key: str) -> Any:
        """Simulate network request"""
        print(f"[PROXY] Sending GET request to {self.host}:{self.port}")
        print(f"[PROXY] Request: GET /data/{key}")

        # Simulate network call
        response = self._make_request("GET", f"/data/{key}")

        print(f"[PROXY] Response received: {response}")
        return response

    def set_data(self, key: str, value: Any) -> bool:
        """Simulate network request"""
        print(f"[PROXY] Sending POST request to {self.host}:{self.port}")
        print(f"[PROXY] Request: POST /data/{key}")
        print(f"[PROXY] Body: {json.dumps({'value': value})}")

        # Simulate network call
        response = self._make_request("POST", f"/data/{key}", {"value": value})

        print(f"[PROXY] Response received: {response}")
        return True

    def _make_request(self, method: str, path: str, data: Dict = None) -> Any:
        """Simulate HTTP request"""
        # In real implementation, would use requests library
        # For demo, directly call server
        server = RealRemoteService()

        if method == "GET":
            key = path.split("/")[-1]
            return server.get_data(key)
        elif method == "POST":
            key = path.split("/")[-1]
            return server.set_data(key, data["value"])


# Usage - client doesn't know it's remote
proxy = RemoteServiceProxy("api.example.com", 8080)

proxy.set_data("user:123", {"name": "Alice", "age": 30})
# [PROXY] Sending POST request to api.example.com:8080
# [PROXY] Request: POST /data/user:123
# [PROXY] Body: {"value": {"name": "Alice", "age": 30}}
# [SERVER] Setting user:123 = {'name': 'Alice', 'age': 30}
# [PROXY] Response received: True

data = proxy.get_data("user:123")
# [PROXY] Sending GET request to api.example.com:8080
# [PROXY] Request: GET /data/user:123
# [SERVER] Getting user:123
# [PROXY] Response received: {'name': 'Alice', 'age': 30}
```

---

## 4. Caching Proxy

Caches results for expensive operations.

```python
from typing import Optional, Dict
import time


class Database(ABC):
    """Database interface"""

    @abstractmethod
    def query(self, sql: str) -> list:
        pass


class RealDatabase(Database):
    """Actual database - expensive queries"""

    def query(self, sql: str) -> list:
        print(f"Database: Executing query: {sql}")
        time.sleep(0.5)  # Simulate slow query

        # Simulate different results
        if "users" in sql:
            return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        elif "products" in sql:
            return [{"id": 1, "product": "Laptop"}]
        return []


class CachingDatabaseProxy(Database):
    """Caching proxy for database"""

    def __init__(self, database: Database):
        self._database = database
        self._cache: Dict[str, list] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def query(self, sql: str) -> list:
        """Check cache before querying database"""
        if sql in self._cache:
            self._cache_hits += 1
            print(f"Proxy: Cache HIT for query (hits: {self._cache_hits})")
            return self._cache[sql]

        self._cache_misses += 1
        print(f"Proxy: Cache MISS (misses: {self._cache_misses})")

        # Query real database
        result = self._database.query(sql)

        # Cache result
        self._cache[sql] = result
        print(f"Proxy: Result cached ({len(self._cache)} entries in cache)")

        return result

    def clear_cache(self) -> None:
        """Clear cache"""
        print("Proxy: Clearing cache")
        self._cache.clear()

    def stats(self) -> Dict:
        """Cache statistics"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "cached_queries": len(self._cache)
        }


# Usage
db = RealDatabase()
proxy = CachingDatabaseProxy(db)

# First query - cache miss
result1 = proxy.query("SELECT * FROM users")
# Proxy: Cache MISS (misses: 1)
# Database: Executing query: SELECT * FROM users
# Proxy: Result cached (1 entries in cache)

# Same query - cache hit!
result2 = proxy.query("SELECT * FROM users")
# Proxy: Cache HIT for query (hits: 1)

# Different query - cache miss
result3 = proxy.query("SELECT * FROM products")
# Proxy: Cache MISS (misses: 2)
# Database: Executing query: SELECT * FROM products
# Proxy: Result cached (2 entries in cache)

# Original query again - cache hit!
result4 = proxy.query("SELECT * FROM users")
# Proxy: Cache HIT for query (hits: 2)

# Statistics
print(f"\nCache Stats: {proxy.stats()}")
# Cache Stats: {'hits': 2, 'misses': 2, 'hit_rate': '50.0%', 'cached_queries': 2}
```

---

## 5. Logging Proxy

Logs all operations for monitoring.

```python
from datetime import datetime
from typing import Any


class API(ABC):
    """API interface"""

    @abstractmethod
    def get(self, endpoint: str) -> Any:
        pass

    @abstractmethod
    def post(self, endpoint: str, data: Any) -> Any:
        pass


class RealAPI(API):
    """Actual API implementation"""

    def get(self, endpoint: str) -> Any:
        return {"data": f"Data from {endpoint}"}

    def post(self, endpoint: str, data: Any) -> Any:
        return {"status": "created", "data": data}


class LoggingAPIProxy(API):
    """Logging proxy - logs all API calls"""

    def __init__(self, api: API):
        self._api = api
        self._log = []

    def get(self, endpoint: str) -> Any:
        """Log GET request"""
        start_time = datetime.now()

        print(f"[LOG] {start_time} GET {endpoint}")

        try:
            result = self._api.get(endpoint)
            elapsed = (datetime.now() - start_time).total_seconds()

            print(f"[LOG] Success in {elapsed:.3f}s")

            self._log.append({
                "method": "GET",
                "endpoint": endpoint,
                "timestamp": start_time,
                "duration": elapsed,
                "status": "success"
            })

            return result

        except Exception as e:
            print(f"[LOG] Error: {e}")

            self._log.append({
                "method": "GET",
                "endpoint": endpoint,
                "timestamp": start_time,
                "status": "error",
                "error": str(e)
            })

            raise

    def post(self, endpoint: str, data: Any) -> Any:
        """Log POST request"""
        start_time = datetime.now()

        print(f"[LOG] {start_time} POST {endpoint}")
        print(f"[LOG] Data: {data}")

        try:
            result = self._api.post(endpoint, data)
            elapsed = (datetime.now() - start_time).total_seconds()

            print(f"[LOG] Success in {elapsed:.3f}s")

            self._log.append({
                "method": "POST",
                "endpoint": endpoint,
                "data": data,
                "timestamp": start_time,
                "duration": elapsed,
                "status": "success"
            })

            return result

        except Exception as e:
            print(f"[LOG] Error: {e}")

            self._log.append({
                "method": "POST",
                "endpoint": endpoint,
                "timestamp": start_time,
                "status": "error",
                "error": str(e)
            })

            raise

    def get_logs(self) -> list:
        """Get all logs"""
        return self._log


# Usage
api = RealAPI()
proxy = LoggingAPIProxy(api)

# All calls are logged
proxy.get("/users/123")
# [LOG] 2024-01-15 10:30:00 GET /users/123
# [LOG] Success in 0.001s

proxy.post("/users", {"name": "Alice"})
# [LOG] 2024-01-15 10:30:01 POST /users
# [LOG] Data: {'name': 'Alice'}
# [LOG] Success in 0.001s

# View logs
logs = proxy.get_logs()
for log in logs:
    print(f"{log['method']} {log['endpoint']} - {log['status']}")
```

---

## 6. Smart Proxy (Reference Counting)

Tracks references and performs cleanup.

```python
class ExpensiveResource:
    """Expensive resource that needs cleanup"""

    def __init__(self, name: str):
        self.name = name
        print(f"Resource: Creating {name}")

    def use(self):
        print(f"Resource: Using {self.name}")

    def cleanup(self):
        print(f"Resource: Cleaning up {self.name}")


class SmartProxy:
    """Smart proxy with reference counting"""

    _instances = {}  # Shared pool of resources

    def __init__(self, name: str):
        self.name = name

        if name not in SmartProxy._instances:
            # Create new resource
            SmartProxy._instances[name] = {
                "resource": ExpensiveResource(name),
                "ref_count": 0
            }
            print(f"Proxy: Created new resource pool for {name}")

        # Increment reference count
        SmartProxy._instances[name]["ref_count"] += 1
        print(f"Proxy: Reference count for {name}: {SmartProxy._instances[name]['ref_count']}")

    def use(self):
        """Use the resource"""
        resource = SmartProxy._instances[self.name]["resource"]
        resource.use()

    def __del__(self):
        """Decrement reference count on deletion"""
        if self.name in SmartProxy._instances:
            SmartProxy._instances[self.name]["ref_count"] -= 1
            ref_count = SmartProxy._instances[self.name]["ref_count"]

            print(f"Proxy: Reference count for {self.name} decreased to {ref_count}")

            # Cleanup if no more references
            if ref_count == 0:
                print(f"Proxy: No more references, cleaning up {self.name}")
                SmartProxy._instances[self.name]["resource"].cleanup()
                del SmartProxy._instances[self.name]


# Usage
print("Creating first proxy...")
proxy1 = SmartProxy("SharedResource")
# Resource: Creating SharedResource
# Proxy: Created new resource pool for SharedResource
# Proxy: Reference count for SharedResource: 1

print("\nCreating second proxy (reuses resource)...")
proxy2 = SmartProxy("SharedResource")
# Proxy: Reference count for SharedResource: 2

print("\nUsing proxies...")
proxy1.use()  # Resource: Using SharedResource
proxy2.use()  # Resource: Using SharedResource

print("\nDeleting first proxy...")
del proxy1
# Proxy: Reference count for SharedResource decreased to 1

print("\nDeleting second proxy...")
del proxy2
# Proxy: Reference count for SharedResource decreased to 0
# Proxy: No more references, cleaning up SharedResource
# Resource: Cleaning up SharedResource
```

---

## 7. Combined Proxy Example

Proxy with multiple responsibilities.

```python
class CombinedProxy:
    """Proxy with lazy loading, caching, logging, and access control"""

    def __init__(self, filename: str, user_role: str):
        self.filename = filename
        self.user_role = user_role
        self._real_object = None
        self._cache = {}
        self._log = []

    def read(self) -> str:
        """Read with all proxy features"""
        # 1. Access control
        if self.user_role not in ["admin", "user"]:
            print("Proxy: Access DENIED")
            return None

        # 2. Logging
        self._log.append(f"READ {self.filename}")
        print(f"Proxy: Logged read operation")

        # 3. Caching
        if "content" in self._cache:
            print("Proxy: Cache HIT")
            return self._cache["content"]

        # 4. Lazy loading
        if self._real_object is None:
            print("Proxy: Lazy loading real object...")
            self._real_object = RealFile(self.filename)

        # Read and cache
        content = self._real_object.read()
        self._cache["content"] = content

        return content
```

---

## 8. When to Use Proxy Pattern

### ✅ Use When:

1. **Lazy initialization** - delay expensive object creation
2. **Access control** - restrict access based on permissions
3. **Remote proxy** - represent object in different location
4. **Caching** - cache expensive operation results
5. **Logging** - track object usage
6. **Reference counting** - manage resource lifecycle

### ❌ Don't Use When:

- Simple delegation - no added value
- Proxy adds unnecessary complexity
- Direct access is always required

---

## 9. Proxy vs Other Patterns

| Pattern | Purpose | Key Difference |
|---------|---------|----------------|
| **Proxy** | Control access | Same interface as real object |
| **Decorator** | Add behavior | Stacks multiple wrappers |
| **Adapter** | Change interface | Different interface |
| **Facade** | Simplify interface | Hides multiple objects |

---

## 10. Interview Tips

### Common Questions

**Q: "What's the difference between Proxy and Decorator?"**
- **Proxy**: Controls access (lazy load, security, caching)
- **Decorator**: Adds responsibilities (new behavior)

**Q: "Explain Virtual Proxy"**
- Delays object creation until actually needed
- Example: Image proxy that loads only when displayed

**Q: "What is Protection Proxy?"**
- Controls access based on permissions
- Example: Document proxy that checks user role

**Q: "Implement a caching proxy"**
```python
class CachingProxy:
    def __init__(self, real_object):
        self._real = real_object
        self._cache = {}

    def operation(self, key):
        if key not in self._cache:
            self._cache[key] = self._real.operation(key)
        return self._cache[key]
```

### Best Practices

✅ Proxy implements same interface as real object
✅ Keep proxy transparent to client
✅ Use for cross-cutting concerns (logging, caching, security)
✅ Document proxy's additional responsibilities
✅ Consider combining multiple proxy types

### Red Flags

❌ Proxy changes object's interface (use Adapter)
❌ Proxy with business logic (keep it thin)
❌ Too many proxy layers (complexity)
❌ Proxy that doesn't delegate to real object

---

## Quick Reference

```python
# Subject interface
class Subject(ABC):
    @abstractmethod
    def request(self):
        pass

# Real subject
class RealSubject(Subject):
    def request(self):
        return "Real operation"

# Proxy
class Proxy(Subject):
    def __init__(self):
        self._real_subject = None

    def request(self):
        # Additional logic (lazy load, check access, log, cache, etc.)
        if self._real_subject is None:
            self._real_subject = RealSubject()

        return self._real_subject.request()
```

---

**Related Patterns:**
- [Decorator Pattern](./decorator.md) - Adds behavior dynamically
- [Adapter Pattern](./adapter.md) - Changes interface
- [Facade Pattern](./facade.md) - Simplifies interface
- [Flyweight Pattern](./flyweight.md) - Shares objects

**Back to:** [Design Patterns](./README.md)
