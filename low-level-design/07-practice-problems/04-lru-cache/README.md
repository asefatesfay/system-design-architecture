# Design an LRU Cache

> **🌍 Multi-Language Note:** This solution is in Python. For implementations in other languages:
> - [Language Comparison Guide](../../lld-coding/multi-language/LANGUAGE-COMPARISON.md)
> - [Core OOP Multi-Language Examples](../../03-oop-fundamentals/four-pillars/)

## Problem Statement

Design and implement a data structure for a **Least Recently Used (LRU) cache**. The cache should:
1. Support `get(key)` and `put(key, value)` operations
2. Both operations should be **O(1)** time complexity
3. When capacity is reached, evict the least recently used item
4. Consider thread-safety (bonus)

## Difficulty Level
**Medium** - 45 minutes for basic, 60 minutes with thread-safety

## Requirements Clarification

### Functional Requirements
1. `get(key)`: Return value if key exists, else -1
2. `put(key, value)`: Insert or update key-value pair
3. Capacity limit: When full, remove LRU item
4. "Used" means: accessed via get() or added/updated via put()

### Non-Functional Requirements
1. **O(1)** time for get and put
2. **O(n)** space where n is capacity
3. Thread-safe operations (bonus)

### Constraints
1. Fixed capacity (set at initialization)
2. Keys are integers
3. Values are integers (can be generalized)

## Solution Approach

### Data Structure Choice

To achieve O(1) for both operations:
- **HashMap**: O(1) lookup by key
- **Doubly Linked List**: O(1) insertion/deletion and maintains order

```
Why Doubly Linked List?

Head → [LRU Item] ⟷ [Item] ⟷ [Item] ⟷ [MRU Item] ← Tail
       (Remove)                              (Add new)

- Most recently used at tail
- Least recently used at head
- O(1) to move any node to tail
- O(1) to remove head node
```

### Visual Example

```
Capacity = 3

1. put(1, 10)
   Cache: [1:10]

2. put(2, 20)
   Cache: [1:10] → [2:20]

3. put(3, 30)
   Cache: [1:10] → [2:20] → [3:30]

4. get(1)       // Access key 1, move to end
   Cache: [2:20] → [3:30] → [1:10]
   Return: 10

5. put(4, 40)   // Capacity full, evict LRU (key 2)
   Cache: [3:30] → [1:10] → [4:40]

6. get(2)       // Key 2 was evicted
   Return: -1
```

## Complete Implementation

### Basic LRU Cache (Without Thread Safety)

```python
class Node:
    """Doubly linked list node"""
    def __init__(self, key: int, value: int):
        self.key = key
        self.value = value
        self.prev: Node = None
        self.next: Node = None

class LRUCache:
    """
    LRU Cache with O(1) get and put operations

    Uses:
    - HashMap for O(1) lookup
    - Doubly Linked List for O(1) reordering
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Dummy head and tail for easier list operations
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_tail(self, node: Node):
        """Add node right before tail (most recent position)"""
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def _remove_node(self, node: Node):
        """Remove node from list"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_tail(self, node: Node):
        """Move existing node to tail (mark as recently used)"""
        self._remove_node(node)
        self._add_to_tail(node)

    def _remove_from_head(self) -> Node:
        """Remove least recently used node (right after head)"""
        lru_node = self.head.next
        self._remove_node(lru_node)
        return lru_node

    def get(self, key: int) -> int:
        """
        Get value by key
        Time: O(1)
        """
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._move_to_tail(node)  # Mark as recently used
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Put key-value pair into cache
        Time: O(1)
        """
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_tail(node)
        else:
            # Add new key
            new_node = Node(key, value)
            self.cache[key] = new_node
            self._add_to_tail(new_node)

            # Check capacity
            if len(self.cache) > self.capacity:
                # Remove LRU
                lru_node = self._remove_from_head()
                del self.cache[lru_node.key]

    def display(self):
        """Display cache state (for debugging)"""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append(f"{current.key}:{current.value}")
            current = current.next
        print(f"Cache (LRU→MRU): {' → '.join(items)}")

# Test
def test_lru_cache():
    print("Testing LRU Cache\n" + "="*50)

    cache = LRUCache(3)

    print("1. put(1, 10)")
    cache.put(1, 10)
    cache.display()

    print("\n2. put(2, 20)")
    cache.put(2, 20)
    cache.display()

    print("\n3. put(3, 30)")
    cache.put(3, 30)
    cache.display()

    print("\n4. get(1) - move to end")
    result = cache.get(1)
    print(f"   Result: {result}")
    cache.display()

    print("\n5. put(4, 40) - evict LRU (key 2)")
    cache.put(4, 40)
    cache.display()

    print("\n6. get(2) - should return -1")
    result = cache.get(2)
    print(f"   Result: {result}")

    print("\n7. put(5, 50) - evict LRU (key 3)")
    cache.put(5, 50)
    cache.display()

    print("\n8. Update existing key (1, 100)")
    cache.put(1, 100)
    cache.display()

test_lru_cache()
```

**Output**:
```
Testing LRU Cache
==================================================
1. put(1, 10)
Cache (LRU→MRU): 1:10

2. put(2, 20)
Cache (LRU→MRU): 1:10 → 2:20

3. put(3, 30)
Cache (LRU→MRU): 1:10 → 2:20 → 3:30

4. get(1) - move to end
   Result: 10
Cache (LRU→MRU): 2:20 → 3:30 → 1:10

5. put(4, 40) - evict LRU (key 2)
Cache (LRU→MRU): 3:30 → 1:10 → 4:40

6. get(2) - should return -1
   Result: -1

7. put(5, 50) - evict LRU (key 3)
Cache (LRU→MRU): 1:10 → 4:40 → 5:50

8. Update existing key (1, 100)
Cache (LRU→MRU): 4:40 → 5:50 → 1:100
```

### Thread-Safe LRU Cache

```python
import threading
from typing import Optional

class ThreadSafeLRUCache:
    """Thread-safe LRU Cache using locks"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        self._lock = threading.Lock()

    def _add_to_tail(self, node: Node):
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def _remove_node(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_tail(self, node: Node):
        self._remove_node(node)
        self._add_to_tail(node)

    def _remove_from_head(self) -> Node:
        lru_node = self.head.next
        self._remove_node(lru_node)
        return lru_node

    def get(self, key: int) -> int:
        """Thread-safe get operation"""
        with self._lock:
            if key not in self.cache:
                return -1

            node = self.cache[key]
            self._move_to_tail(node)
            return node.value

    def put(self, key: int, value: int) -> None:
        """Thread-safe put operation"""
        with self._lock:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                self._move_to_tail(node)
            else:
                new_node = Node(key, value)
                self.cache[key] = new_node
                self._add_to_tail(new_node)

                if len(self.cache) > self.capacity:
                    lru_node = self._remove_from_head()
                    del self.cache[lru_node.key]

# Test thread safety
def test_thread_safety():
    cache = ThreadSafeLRUCache(100)

    def worker(thread_id):
        for i in range(1000):
            key = (thread_id * 1000) + i
            cache.put(key, key * 10)
            _ = cache.get(key)

    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Thread safety test completed!")

test_thread_safety()
```

### Generic LRU Cache (Type-Safe)

```python
from typing import TypeVar, Generic, Optional

K = TypeVar('K')
V = TypeVar('V')

class GenericNode(Generic[K, V]):
    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value
        self.prev: Optional['GenericNode[K, V]'] = None
        self.next: Optional['GenericNode[K, V]'] = None

class GenericLRUCache(Generic[K, V]):
    """Generic LRU Cache supporting any hashable key type"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[K, GenericNode[K, V]] = {}
        self.head = GenericNode(None, None)
        self.tail = GenericNode(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_tail(self, node: GenericNode[K, V]):
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def _remove_node(self, node: GenericNode[K, V]):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_tail(self, node: GenericNode[K, V]):
        self._remove_node(node)
        self._add_to_tail(node)

    def _remove_from_head(self) -> GenericNode[K, V]:
        lru_node = self.head.next
        self._remove_node(lru_node)
        return lru_node

    def get(self, key: K) -> Optional[V]:
        if key not in self.cache:
            return None

        node = self.cache[key]
        self._move_to_tail(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_tail(node)
        else:
            new_node = GenericNode(key, value)
            self.cache[key] = new_node
            self._add_to_tail(new_node)

            if len(self.cache) > self.capacity:
                lru_node = self._remove_from_head()
                del self.cache[lru_node.key]

# Usage with different types
def test_generic():
    # String keys, Integer values
    string_cache = GenericLRUCache[str, int](3)
    string_cache.put("apple", 5)
    string_cache.put("banana", 3)
    print(string_cache.get("apple"))  # 5

    # Tuple keys, String values
    tuple_cache = GenericLRUCache[tuple, str](2)
    tuple_cache.put((1, 2), "point1")
    tuple_cache.put((3, 4), "point2")
    print(tuple_cache.get((1, 2)))  # "point1"

test_generic()
```

### With Expiration Time (TTL)

```python
import time

class NodeWithTTL:
    def __init__(self, key: int, value: int, ttl: float):
        self.key = key
        self.value = value
        self.expiry_time = time.time() + ttl
        self.prev = None
        self.next = None

    def is_expired(self) -> bool:
        return time.time() > self.expiry_time

class LRUCacheWithTTL:
    """LRU Cache with Time-To-Live for entries"""

    def __init__(self, capacity: int, default_ttl: float = 60.0):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self.cache = {}
        self.head = NodeWithTTL(0, 0, float('inf'))
        self.tail = NodeWithTTL(0, 0, float('inf'))
        self.head.next = self.tail
        self.tail.prev = self.head

    def _cleanup_expired(self):
        """Remove all expired entries"""
        current = self.head.next
        while current != self.tail:
            next_node = current.next
            if current.is_expired():
                self._remove_node(current)
                del self.cache[current.key]
            current = next_node

    def get(self, key: int) -> int:
        self._cleanup_expired()

        if key not in self.cache:
            return -1

        node = self.cache[key]
        if node.is_expired():
            self._remove_node(node)
            del self.cache[key]
            return -1

        self._move_to_tail(node)
        return node.value

    # ... rest of implementation similar to basic LRU
```

## Time & Space Complexity

| Operation | Time | Space |
|-----------|------|-------|
| get(key) | O(1) | - |
| put(key, value) | O(1) | - |
| Overall | O(1) | O(capacity) |

## Key Design Decisions

### 1. Why Doubly Linked List?

```
Singly Linked List:    Doubly Linked List:
A → B → C             A ⟷ B ⟷ C

To remove B:          To remove B:
- Need to find A      - Direct access to A
- O(n) traversal      - O(1) operation
```

### 2. Why Dummy Head/Tail?

```
Without Dummy Nodes:          With Dummy Nodes:
- Check if list empty          - No null checks needed
- Handle edge cases            - Simplified logic
- Complex insertion            - Uniform operations

if head is None:              head.next.prev = node
    # special case            (always valid)
```

### 3. HashMap + Linked List

```
HashMap alone:
✓ O(1) lookup
✗ Can't track order

Linked List alone:
✓ Maintains order
✗ O(n) lookup

Combined:
✓ O(1) lookup
✓ O(1) reordering
✓ O(1) eviction
```

## Interview Discussion Points

### Q: Why not use OrderedDict?

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

**Answer**: OrderedDict is valid! But:
- Interview tests DS knowledge
- Custom implementation shows understanding
- Might not be available in production language

### Q: How to make it distributed?

**Answer**:
- Use Redis with TTL
- Consistent hashing for sharding
- Separate cache per server
- Central cache service

### Q: How to handle cache stampede?

**Answer**:
- Probabilistic early expiration
- Request coalescing
- Stale-while-revalidate pattern

## Extensions

1. **LFU Cache**: Track frequency instead of recency
2. **2Q Cache**: Combine LRU with FIFO
3. **ARC Cache**: Adaptive replacement
4. **Write-through/Write-back**: Handle updates
5. **Distributed cache**: Multi-server support

## Testing

```python
def comprehensive_test():
    cache = LRUCache(2)

    # Test 1: Basic put and get
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1

    # Test 2: Eviction
    cache.put(3, 3)  # Evicts key 2
    assert cache.get(2) == -1

    # Test 3: Update existing
    cache.put(1, 10)
    assert cache.get(1) == 10

    # Test 4: Get non-existent
    assert cache.get(5) == -1

    print("All tests passed!")

comprehensive_test()
```

---

**Complete!** This LRU Cache demonstrates optimal O(1) performance using HashMap + Doubly Linked List.
