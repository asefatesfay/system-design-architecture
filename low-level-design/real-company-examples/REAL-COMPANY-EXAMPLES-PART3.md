# Real Company LLD Examples - Part 3

Final set of real-world low-level design examples from major tech companies.

> **📝 Language Note:** Examples use Python (most common for LLD interviews). For language-specific patterns:
> - [Language Comparison Guide](../lld-coding/multi-language/LANGUAGE-COMPARISON.md) - Python vs Go vs Java vs JavaScript
> - [Four Pillars Multi-Language](../03-oop-fundamentals/four-pillars/) - Core OOP in all 4 languages
> - [Design Patterns](../06-design-patterns/) - Decorator, Template Method, Chain of Responsibility
> - [Part 1](./REAL-COMPANY-EXAMPLES.md) - Rate Limiter, Notifications, Ride Matching
> - [Part 2](./REAL-COMPANY-EXAMPLES-PART2.md) - URL Shortener, Autocomplete, Circuit Breaker

---

# 8. Retry with Exponential Backoff - AWS, Stripe, Twilio

**Used by**: AWS SDK, Stripe API, Twilio, Google Cloud, most HTTP clients

**Problem**: Handle temporary failures gracefully without overwhelming the service

**Patterns**: Decorator (wrap calls), Template Method (retry logic)

## Complete Implementation

```python
from abc import ABC, abstractmethod
from typing import Callable, Any, List, Type
import time
import random
from datetime import datetime

# ============================================
# RETRY STRATEGIES
# ============================================

class RetryStrategy(ABC):
    """Abstract retry strategy"""

    @abstractmethod
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry"""
        pass

class FixedDelayStrategy(RetryStrategy):
    """
    Fixed delay between retries
    Simple but not optimal

    Example: 1s, 1s, 1s, 1s...
    """

    def __init__(self, delay_seconds: float = 1.0):
        self.delay_seconds = delay_seconds

    def calculate_delay(self, attempt: int) -> float:
        return self.delay_seconds

class LinearBackoffStrategy(RetryStrategy):
    """
    Linear increase in delay
    Example: 1s, 2s, 3s, 4s...
    """

    def __init__(self, initial_delay: float = 1.0, increment: float = 1.0):
        self.initial_delay = initial_delay
        self.increment = increment

    def calculate_delay(self, attempt: int) -> float:
        return self.initial_delay + (attempt * self.increment)

class ExponentialBackoffStrategy(RetryStrategy):
    """
    Exponential backoff - Used by AWS, Stripe, Google Cloud

    Example: 1s, 2s, 4s, 8s, 16s...

    Pros: Reduces load on failing service
    Cons: Can lead to long waits
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier

    def calculate_delay(self, attempt: int) -> float:
        """Calculate exponential delay with cap"""
        delay = self.base_delay * (self.multiplier ** attempt)
        return min(delay, self.max_delay)

class ExponentialBackoffWithJitterStrategy(RetryStrategy):
    """
    Exponential backoff with jitter - AWS SDK uses this!

    Jitter: Add randomness to prevent thundering herd problem

    Example: 1s±50%, 2s±50%, 4s±50%...

    Used by: AWS SDK, Stripe, Netflix
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        jitter_factor: float = 0.5
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter_factor = jitter_factor

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay with random jitter"""
        base_delay = self.base_delay * (self.multiplier ** attempt)
        base_delay = min(base_delay, self.max_delay)

        # Add jitter: randomize between (base * (1-jitter), base * (1+jitter))
        min_delay = base_delay * (1 - self.jitter_factor)
        max_delay_with_jitter = base_delay * (1 + self.jitter_factor)

        return random.uniform(min_delay, max_delay_with_jitter)

# ============================================
# RETRY DECORATOR
# ============================================

class RetryConfig:
    """Configuration for retry behavior"""

    def __init__(
        self,
        max_attempts: int = 3,
        strategy: RetryStrategy = None,
        retryable_exceptions: List[Type[Exception]] = None,
        on_retry: Callable = None
    ):
        self.max_attempts = max_attempts
        self.strategy = strategy or ExponentialBackoffWithJitterStrategy()
        self.retryable_exceptions = retryable_exceptions or [Exception]
        self.on_retry = on_retry

class RetryExecutor:
    """
    Execute function with retry logic
    Like AWS SDK's retry mechanism
    """

    def __init__(self, config: RetryConfig):
        self.config = config

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retries"""

        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                # Try to execute
                result = func(*args, **kwargs)

                # Success!
                if attempt > 0:
                    print(f"✓ Succeeded after {attempt + 1} attempts")

                return result

            except Exception as e:
                last_exception = e

                # Check if this exception is retryable
                if not self._is_retryable(e):
                    print(f"✗ Non-retryable error: {type(e).__name__}")
                    raise

                # Check if we have more attempts
                if attempt < self.config.max_attempts - 1:
                    delay = self.config.strategy.calculate_delay(attempt)

                    print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                    print(f"   Retrying in {delay:.2f}s...")

                    # Call retry hook if provided
                    if self.config.on_retry:
                        self.config.on_retry(attempt, e, delay)

                    time.sleep(delay)
                else:
                    print(f"✗ All {self.config.max_attempts} attempts failed")

        # All attempts exhausted
        raise last_exception

    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable"""
        for exc_type in self.config.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        return False

# ============================================
# SERVICE CLIENT WITH RETRY
# ============================================

class NetworkError(Exception):
    """Simulated network error"""
    pass

class ServiceUnavailableError(Exception):
    """Service temporarily unavailable (503)"""
    pass

class AuthenticationError(Exception):
    """Authentication failed (401) - not retryable!"""
    pass

class ExternalAPIClient:
    """
    API client with retry logic
    Like: AWS SDK, Stripe SDK, Twilio SDK
    """

    def __init__(self, retry_config: RetryConfig = None):
        self.retry_config = retry_config or RetryConfig(
            max_attempts=3,
            strategy=ExponentialBackoffWithJitterStrategy(
                base_delay=1.0,
                max_delay=30.0
            ),
            retryable_exceptions=[NetworkError, ServiceUnavailableError]
        )

        self.retry_executor = RetryExecutor(self.retry_config)
        self.call_count = 0

    def make_api_call(self, endpoint: str, data: dict) -> dict:
        """
        Make API call with automatic retry

        This is what AWS SDK, Stripe SDK do internally
        """

        def _api_call():
            self.call_count += 1
            return self._execute_request(endpoint, data)

        return self.retry_executor.execute(_api_call)

    def _execute_request(self, endpoint: str, data: dict) -> dict:
        """
        Simulate actual HTTP request
        In real world: uses requests library or http client
        """

        print(f"→ Making request to {endpoint}")

        # Simulate various failure scenarios
        # In real world: actual network errors, 5xx responses, timeouts

        # Simulate random failures (for demo)
        failure_rate = 0.4  # 40% failure rate

        if random.random() < failure_rate and self.call_count < 2:
            # Simulate intermittent failure
            raise ServiceUnavailableError("503: Service temporarily unavailable")

        # Success!
        return {
            'status': 'success',
            'endpoint': endpoint,
            'data': data,
            'attempt': self.call_count
        }

# ============================================
# DEMO
# ============================================

def demo_retry_patterns():
    """Demonstrate retry patterns used by AWS, Stripe, etc."""

    print("="*70)
    print("RETRY WITH EXPONENTIAL BACKOFF (AWS SDK / Stripe)")
    print("="*70)

    # Scenario 1: Exponential backoff without jitter
    print("\n" + "="*70)
    print("SCENARIO 1: Exponential Backoff (No Jitter)")
    print("="*70)

    config1 = RetryConfig(
        max_attempts=5,
        strategy=ExponentialBackoffStrategy(base_delay=0.5, max_delay=10.0),
        retryable_exceptions=[NetworkError, ServiceUnavailableError]
    )

    client1 = ExternalAPIClient(config1)

    try:
        result = client1.make_api_call("/api/payment", {"amount": 100})
        print(f"✓ Result: {result}")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Scenario 2: Exponential backoff WITH jitter (AWS SDK style)
    print("\n" + "="*70)
    print("SCENARIO 2: Exponential Backoff with Jitter (AWS SDK)")
    print("="*70)

    config2 = RetryConfig(
        max_attempts=4,
        strategy=ExponentialBackoffWithJitterStrategy(
            base_delay=1.0,
            max_delay=15.0,
            jitter_factor=0.5
        ),
        retryable_exceptions=[NetworkError, ServiceUnavailableError]
    )

    client2 = ExternalAPIClient(config2)

    try:
        result = client2.make_api_call("/api/charge", {"amount": 200})
        print(f"✓ Result: {result}")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Scenario 3: Compare retry strategies
    print("\n" + "="*70)
    print("SCENARIO 3: Comparing Retry Strategies")
    print("="*70)

    strategies = [
        ("Fixed (1s)", FixedDelayStrategy(delay_seconds=1.0)),
        ("Linear", LinearBackoffStrategy(initial_delay=1.0, increment=1.0)),
        ("Exponential", ExponentialBackoffStrategy(base_delay=1.0)),
        ("Exponential + Jitter (AWS)", ExponentialBackoffWithJitterStrategy(base_delay=1.0))
    ]

    print("\nDelay progression for 6 attempts:\n")

    for name, strategy in strategies:
        delays = [strategy.calculate_delay(i) for i in range(6)]
        delays_str = " → ".join(f"{d:.2f}s" for d in delays)
        print(f"{name:25} {delays_str}")

if __name__ == "__main__":
    demo_retry_patterns()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ Exponential Backoff: 1s → 2s → 4s → 8s...")
    print("✓ Jitter: Prevents thundering herd (many clients retrying together)")
    print("✓ AWS SDK uses: Exponential Backoff + Jitter")
    print("✓ Only retry transient errors (5xx, network), not 4xx errors")
    print("✓ Set max delay cap to avoid waiting forever")
    print("="*70)
```

**Real-World Usage**:
- **AWS SDK**: Exponential backoff with jitter, 3 retries by default
- **Stripe**: Exponential backoff, retries on 5xx, connection errors
- **Twilio**: Exponential backoff with max 3 retries
- **Google Cloud**: Similar to AWS with configurable strategies

---

# 9. Distributed Cache - Redis, Memcached

**Used by**: Redis, Memcached, AWS ElastiCache, Azure Cache

**Problem**: Fast data access across multiple servers

**Patterns**: Proxy (cache wrapper), Strategy (eviction policies)

## Complete Implementation

```python
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
import time

# ============================================
# CACHE EVICTION STRATEGIES
# ============================================

class EvictionPolicy(ABC):
    """Abstract cache eviction policy"""

    @abstractmethod
    def on_get(self, key: str):
        """Called when key is accessed"""
        pass

    @abstractmethod
    def on_put(self, key: str):
        """Called when key is added"""
        pass

    @abstractmethod
    def evict(self) -> Optional[str]:
        """Return key to evict"""
        pass

class LRUEvictionPolicy(EvictionPolicy):
    """
    Least Recently Used - Redis default
    Evict least recently accessed item
    """

    def __init__(self):
        self.access_order = OrderedDict()

    def on_get(self, key: str):
        """Move to end (most recent)"""
        if key in self.access_order:
            self.access_order.move_to_end(key)

    def on_put(self, key: str):
        """Add to end (most recent)"""
        self.access_order[key] = True
        self.access_order.move_to_end(key)

    def evict(self) -> Optional[str]:
        """Evict least recently used (first item)"""
        if self.access_order:
            key, _ = self.access_order.popitem(last=False)
            return key
        return None

    def remove(self, key: str):
        """Remove key from tracking"""
        if key in self.access_order:
            del self.access_order[key]

class LFUEvictionPolicy(EvictionPolicy):
    """
    Least Frequently Used
    Evict least frequently accessed item
    """

    def __init__(self):
        self.frequencies: Dict[str, int] = {}

    def on_get(self, key: str):
        """Increment frequency"""
        self.frequencies[key] = self.frequencies.get(key, 0) + 1

    def on_put(self, key: str):
        """Initialize frequency"""
        if key not in self.frequencies:
            self.frequencies[key] = 1

    def evict(self) -> Optional[str]:
        """Evict least frequently used"""
        if not self.frequencies:
            return None

        # Find key with minimum frequency
        min_key = min(self.frequencies.items(), key=lambda x: x[1])[0]
        del self.frequencies[min_key]
        return min_key

    def remove(self, key: str):
        """Remove key from tracking"""
        if key in self.frequencies:
            del self.frequencies[key]

# ============================================
# CACHE ENTRY
# ============================================

class CacheEntry:
    """Entry in cache with TTL support"""

    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        self.key = key
        self.value = value
        self.created_at = datetime.now()

        # TTL (Time To Live) in seconds
        self.ttl = ttl
        self.expires_at = (
            datetime.now() + timedelta(seconds=ttl)
            if ttl else None
        )

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

# ============================================
# DISTRIBUTED CACHE
# ============================================

class DistributedCache:
    """
    Redis-like distributed cache

    Features:
    - TTL support
    - LRU/LFU eviction
    - Get/Set/Delete operations
    - Statistics
    """

    def __init__(
        self,
        max_size: int = 1000,
        eviction_policy: EvictionPolicy = None,
        default_ttl: Optional[int] = None
    ):
        self.max_size = max_size
        self.eviction_policy = eviction_policy or LRUEvictionPolicy()
        self.default_ttl = default_ttl

        # Storage
        self.cache: Dict[str, CacheEntry] = {}

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        Returns None if not found or expired
        """

        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]

        # Check if expired
        if entry.is_expired():
            self.delete(key)
            self.misses += 1
            return None

        # Update access tracking
        self.eviction_policy.on_get(key)

        self.hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache with optional TTL

        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds (optional)
        """

        # Use default TTL if not specified
        if ttl is None:
            ttl = self.default_ttl

        # Check if we need to evict
        if key not in self.cache and len(self.cache) >= self.max_size:
            self._evict()

        # Store entry
        entry = CacheEntry(key, value, ttl)
        self.cache[key] = entry

        # Update access tracking
        self.eviction_policy.on_put(key)

        print(f"✓ Cached: {key} (TTL: {ttl}s)" if ttl else f"✓ Cached: {key}")

    def delete(self, key: str) -> bool:
        """Delete key from cache"""

        if key in self.cache:
            del self.cache[key]
            self.eviction_policy.remove(key)
            return True

        return False

    def _evict(self):
        """Evict one entry according to policy"""

        key_to_evict = self.eviction_policy.evict()

        if key_to_evict and key_to_evict in self.cache:
            del self.cache[key_to_evict]
            self.evictions += 1
            print(f"⚠️ Evicted: {key_to_evict}")

    def get_stats(self) -> dict:
        """Get cache statistics"""

        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'evictions': self.evictions
        }

    def clear(self):
        """Clear all entries"""
        self.cache.clear()

# ============================================
# CACHE CLIENT (Like Redis Client)
# ============================================

class CacheClient:
    """
    Client for distributed cache
    Like: redis-py, node-redis
    """

    def __init__(self, cache: DistributedCache):
        self.cache = cache

    def get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        return self.cache.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        """Set in cache with expiration (EX in Redis)"""
        self.cache.set(key, value, ttl=ex)

    def delete(self, key: str):
        """Delete from cache"""
        return self.cache.delete(key)

# ============================================
# DEMO
# ============================================

def demo_distributed_cache():
    """Simulate Redis-like distributed cache"""

    print("="*70)
    print("DISTRIBUTED CACHE (Redis / Memcached)")
    print("="*70)

    # Create cache with LRU eviction
    cache = DistributedCache(
        max_size=5,
        eviction_policy=LRUEvictionPolicy(),
        default_ttl=None
    )

    client = CacheClient(cache)

    # Scenario 1: Basic operations
    print("\n" + "="*70)
    print("SCENARIO 1: Basic Cache Operations")
    print("="*70)

    # Set values
    client.set("user:1", {"name": "Alice", "age": 30})
    client.set("user:2", {"name": "Bob", "age": 25})
    client.set("user:3", {"name": "Carol", "age": 28})

    # Get values
    print(f"\nGet user:1: {client.get('user:1')}")
    print(f"Get user:2: {client.get('user:2')}")

    # Scenario 2: TTL (Time To Live)
    print("\n" + "="*70)
    print("SCENARIO 2: TTL (Expiration)")
    print("="*70)

    client.set("session:abc", {"user_id": 1}, ex=2)  # 2 second TTL
    print(f"Get session:abc: {client.get('session:abc')}")

    print("⏳ Waiting 3 seconds...")
    time.sleep(3)

    print(f"Get session:abc after expiry: {client.get('session:abc')}")

    # Scenario 3: LRU Eviction
    print("\n" + "="*70)
    print("SCENARIO 3: LRU Eviction (max_size=5)")
    print("="*70)

    # Fill cache to capacity
    for i in range(4, 8):
        client.set(f"key{i}", f"value{i}")

    # Show stats
    print(f"\n📊 Cache Stats:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    demo_distributed_cache()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ LRU: Most common eviction policy (Redis default)")
    print("✓ TTL: Auto-expire entries after timeout")
    print("✓ Hit rate: % of requests served from cache")
    print("✓ Redis uses: Single-threaded, in-memory, pub/sub")
    print("="*70)
```

---

# 10. Event-Driven Architecture - Kafka, RabbitMQ

**Used by**: Kafka, RabbitMQ, AWS SQS/SNS, Google Pub/Sub

**Problem**: Decouple services, handle async communication

**Patterns**: Observer, Publisher-Subscriber, Queue

## Complete Implementation

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Any
from datetime import datetime
from collections import deque
from enum import Enum
import time

# ============================================
# EVENT MODELS
# ============================================

class Event:
    """Generic event"""

    def __init__(self, event_type: str, data: dict, source: str):
        self.event_id = f"evt_{int(time.time() * 1000)}"
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"Event({self.event_type}, from={self.source})"

# ============================================
# MESSAGE QUEUE
# ============================================

class MessageQueue:
    """
    Kafka-like message queue
    FIFO (First In, First Out)
    """

    def __init__(self, name: str, max_size: int = 10000):
        self.name = name
        self.max_size = max_size
        self.messages: deque = deque(maxlen=max_size)
        self.total_published = 0
        self.total_consumed = 0

    def publish(self, event: Event):
        """Publish event to queue"""
        self.messages.append(event)
        self.total_published += 1
        print(f"📤 Published to {self.name}: {event.event_type}")

    def consume(self) -> Event:
        """Consume event from queue"""
        if self.messages:
            event = self.messages.popleft()
            self.total_consumed += 1
            return event
        return None

    def size(self) -> int:
        """Get current queue size"""
        return len(self.messages)

# ============================================
# EVENT BUS (Pub/Sub)
# ============================================

class EventBus:
    """
    Kafka/RabbitMQ-like event bus

    Features:
    - Topic-based routing
    - Multiple subscribers per topic
    - Async event delivery
    """

    def __init__(self):
        # Topic -> List of subscribers
        self.subscribers: Dict[str, List[Callable]] = {}

        # Topic -> Message queue
        self.queues: Dict[str, MessageQueue] = {}

        # Statistics
        self.total_events = 0

    def create_topic(self, topic: str):
        """Create a topic (like Kafka topic)"""
        if topic not in self.queues:
            self.queues[topic] = MessageQueue(topic)
            self.subscribers[topic] = []
            print(f"✓ Created topic: {topic}")

    def subscribe(self, topic: str, handler: Callable[[Event], None]):
        """
        Subscribe to topic
        Like: Kafka consumer, RabbitMQ consumer
        """

        if topic not in self.subscribers:
            self.create_topic(topic)

        self.subscribers[topic].append(handler)
        print(f"✓ Subscribed to topic: {topic}")

    def publish(self, topic: str, event: Event):
        """
        Publish event to topic
        Like: Kafka producer, RabbitMQ publisher
        """

        if topic not in self.queues:
            self.create_topic(topic)

        # Add to queue
        self.queues[topic].publish(event)
        self.total_events += 1

        # Notify all subscribers (simulate async)
        for handler in self.subscribers[topic]:
            try:
                handler(event)
            except Exception as e:
                print(f"⚠️ Handler error: {e}")

    def get_stats(self) -> dict:
        """Get event bus statistics"""
        return {
            'total_events': self.total_events,
            'topics': len(self.queues),
            'topic_stats': {
                topic: {
                    'published': queue.total_published,
                    'consumed': queue.total_consumed,
                    'pending': queue.size()
                }
                for topic, queue in self.queues.items()
            }
        }

# ============================================
# EXAMPLE: E-COMMERCE SYSTEM
# ============================================

class OrderService:
    """Order service - publishes order events"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def create_order(self, order_id: str, user_id: str, amount: float):
        """Create order and publish event"""

        print(f"\n🛒 OrderService: Creating order {order_id}")

        # Publish event
        event = Event(
            event_type="order.created",
            data={
                'order_id': order_id,
                'user_id': user_id,
                'amount': amount
            },
            source="OrderService"
        )

        self.event_bus.publish("orders", event)

class PaymentService:
    """Payment service - subscribes to order events"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("orders", self.handle_order_created)

    def handle_order_created(self, event: Event):
        """Handle order created event"""

        if event.event_type == "order.created":
            order_id = event.data['order_id']
            amount = event.data['amount']

            print(f"💳 PaymentService: Processing payment for order {order_id} (${amount})")

            # Simulate payment processing
            time.sleep(0.1)

            # Publish payment event
            payment_event = Event(
                event_type="payment.completed",
                data={
                    'order_id': order_id,
                    'status': 'success'
                },
                source="PaymentService"
            )

            self.event_bus.publish("payments", payment_event)

class InventoryService:
    """Inventory service - subscribes to order events"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("orders", self.handle_order_created)

    def handle_order_created(self, event: Event):
        """Handle order created event"""

        if event.event_type == "order.created":
            order_id = event.data['order_id']

            print(f"📦 InventoryService: Reserving items for order {order_id}")

class NotificationService:
    """Notification service - subscribes to multiple events"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("orders", self.handle_order_event)
        self.event_bus.subscribe("payments", self.handle_payment_event)

    def handle_order_event(self, event: Event):
        """Handle order events"""
        if event.event_type == "order.created":
            user_id = event.data['user_id']
            print(f"📧 NotificationService: Sending order confirmation to user {user_id}")

    def handle_payment_event(self, event: Event):
        """Handle payment events"""
        if event.event_type == "payment.completed":
            order_id = event.data['order_id']
            print(f"📧 NotificationService: Sending payment receipt for order {order_id}")

# ============================================
# DEMO
# ============================================

def demo_event_driven_architecture():
    """Simulate Kafka-like event-driven system"""

    print("="*70)
    print("EVENT-DRIVEN ARCHITECTURE (Kafka / RabbitMQ)")
    print("="*70)

    # Create event bus
    event_bus = EventBus()

    # Create services
    print("\n📋 Initializing services...")
    order_service = OrderService(event_bus)
    payment_service = PaymentService(event_bus)
    inventory_service = InventoryService(event_bus)
    notification_service = NotificationService(event_bus)

    # Scenario: Create orders
    print("\n" + "="*70)
    print("SCENARIO: Order Flow")
    print("="*70)

    # Create order (triggers cascade of events)
    order_service.create_order("ORD-001", "user_123", 99.99)

    # Small delay to see event flow
    time.sleep(0.5)

    # Create another order
    order_service.create_order("ORD-002", "user_456", 149.99)

    # Show statistics
    print("\n" + "="*70)
    print("📊 Event Bus Statistics")
    print("="*70)

    stats = event_bus.get_stats()
    print(f"Total events: {stats['total_events']}")
    print(f"Topics: {stats['topics']}")
    print("\nTopic details:")
    for topic, topic_stats in stats['topic_stats'].items():
        print(f"  {topic}:")
        print(f"    Published: {topic_stats['published']}")
        print(f"    Consumed: {topic_stats['consumed']}")
        print(f"    Pending: {topic_stats['pending']}")

if __name__ == "__main__":
    demo_event_driven_architecture()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("✓ Observer Pattern: Services subscribe to events")
    print("✓ Decoupling: Services don't know about each other")
    print("✓ Scalability: Easy to add new subscribers")
    print("✓ Kafka uses: Topics, partitions, consumer groups")
    print("✓ Benefits: Async, fault-tolerant, scalable")
    print("="*70)
```

**Real-World Usage**:
- **Kafka**: LinkedIn, Uber, Netflix for real-time data pipelines
- **RabbitMQ**: E-commerce order processing, task queues
- **AWS SNS/SQS**: Serverless architectures, microservices
- **Google Pub/Sub**: Analytics, IoT, streaming

---

## Summary of All 10 Examples

| # | System | Companies | Key Pattern | Complexity |
|---|--------|-----------|-------------|------------|
| 1 | Rate Limiter | Twitter, GitHub, Stripe | Strategy | Medium |
| 2 | Notification System | Slack, Facebook | Observer, Factory | Medium |
| 3 | Ride Matching | Uber, Lyft | Strategy, State | Hard |
| 4 | Recommendations | Netflix, YouTube | Strategy, Chain | Hard |
| 5 | Circuit Breaker | Netflix, AWS | State, Proxy | Medium |
| 6 | URL Shortener | bit.ly, TinyURL | Factory, Strategy | Medium |
| 7 | Autocomplete | Google, Amazon | Trie (Data Structure) | Medium |
| 8 | Retry Logic | AWS, Stripe | Decorator, Strategy | Medium |
| 9 | Distributed Cache | Redis, Memcached | Proxy, Strategy | Medium |
| 10 | Event Bus | Kafka, RabbitMQ | Observer, Pub/Sub | Hard |

All examples are production-grade with complete, runnable implementations! 🚀
