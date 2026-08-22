# Testing Distributed Systems

> **"In God we trust, all others must bring data." - W. Edwards Deming**
>
> Production systems need comprehensive testing. This guide covers testing strategies from unit tests to chaos engineering.

---

## Table of Contents

1. [Testing Pyramid for Distributed Systems](#testing-pyramid-for-distributed-systems)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [Contract Testing](#contract-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [Load Testing](#load-testing)
7. [Chaos Engineering](#chaos-engineering)
8. [Testing Eventual Consistency](#testing-eventual-consistency)
9. [Testing Data Consistency](#testing-data-consistency)
10. [Testing Strategies by System Type](#testing-strategies-by-system-type)

---

## Testing Pyramid for Distributed Systems

```
         /\
        /E2E\          ← 5% (Slow, expensive, brittle)
       /------\
      /Contract\       ← 15% (API contracts)
     /----------\
    /Integration\      ← 30% (Service + DB)
   /--------------\
  /   Unit Tests   \   ← 50% (Fast, cheap, stable)
 /------------------\
```

### Why This Ratio?

**Unit Tests (50%):**
- Fast (<100ms each)
- Cheap (no infrastructure)
- Stable (isolated)
- Easy to debug

**Integration Tests (30%):**
- Medium speed (1-10s each)
- Need database/cache
- Test real interactions
- Catch integration bugs

**Contract Tests (15%):**
- Medium speed
- Test API compatibility
- Prevent breaking changes
- Independent of implementation

**E2E Tests (5%):**
- Slow (minutes)
- Expensive (full stack)
- Brittle (many failure points)
- Test critical user journeys only

---

## Unit Testing

### Principles

**Test in isolation:**
- Mock external dependencies
- Test one component at a time
- Fast execution (<100ms)

### Example: Testing URL Shortener Logic

```python
import pytest
from unittest.mock import Mock, patch
from url_shortener import URLShortener

class TestURLShortener:

    @pytest.fixture
    def shortener(self):
        # Mock database
        mock_db = Mock()
        return URLShortener(database=mock_db)

    def test_generate_short_code_length(self, shortener):
        """Short code should be 6 characters"""
        code = shortener.generate_short_code()
        assert len(code) == 6

    def test_generate_short_code_uniqueness(self, shortener):
        """Generate 1000 codes, all should be unique"""
        codes = {shortener.generate_short_code() for _ in range(1000)}
        assert len(codes) == 1000

    def test_generate_short_code_only_alphanumeric(self, shortener):
        """Code should only contain a-z, A-Z, 0-9"""
        code = shortener.generate_short_code()
        assert code.isalnum()

    @patch('url_shortener.database')
    def test_shorten_url_success(self, mock_db, shortener):
        """Successfully shorten a URL"""
        mock_db.insert.return_value = True

        result = shortener.shorten('https://example.com')

        assert 'short_code' in result
        assert len(result['short_code']) == 6
        mock_db.insert.assert_called_once()

    def test_shorten_url_invalid(self, shortener):
        """Reject invalid URLs"""
        with pytest.raises(ValueError):
            shortener.shorten('not-a-url')

    def test_shorten_url_duplicate_retry(self, shortener):
        """Retry on collision"""
        shortener.database.insert.side_effect = [
            DuplicateKeyError(),  # First attempt fails
            True                   # Second attempt succeeds
        ]

        result = shortener.shorten('https://example.com')
        assert result is not None
        assert shortener.database.insert.call_count == 2
```

### Testing Async Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_cache_get():
    """Test async cache operations"""
    cache = AsyncCache()

    # Set value
    await cache.set('key', 'value', ttl=60)

    # Get value
    result = await cache.get('key')
    assert result == 'value'

    # Wait for expiration
    await asyncio.sleep(61)
    result = await cache.get('key')
    assert result is None
```

### Testing Concurrency

```python
import threading
import pytest

def test_concurrent_withdrawals():
    """Test thread-safe bank account"""
    account = BankAccount(balance=100)

    def withdraw_50():
        account.withdraw(50)

    # Two threads try to withdraw $50 simultaneously
    t1 = threading.Thread(target=withdraw_50)
    t2 = threading.Thread(target=withdraw_50)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Only one withdrawal should succeed
    # Balance should be $50, not $0 or $100
    assert account.balance == 50
```

---

## Integration Testing

### Test with Real Dependencies

**Use TestContainers for integration tests:**

```python
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope='module')
def postgres():
    """Start PostgreSQL container for tests"""
    with PostgresContainer('postgres:15') as postgres:
        yield postgres

@pytest.fixture(scope='module')
def redis():
    """Start Redis container for tests"""
    with RedisContainer('redis:7') as redis:
        yield redis

def test_url_shortener_with_real_db(postgres, redis):
    """Test with real PostgreSQL and Redis"""
    # Initialize service with real databases
    shortener = URLShortener(
        db_url=postgres.get_connection_url(),
        redis_url=redis.get_connection_url()
    )

    # Test flow
    result = shortener.shorten('https://example.com')
    short_code = result['short_code']

    # Verify in database
    original_url = shortener.get_original(short_code)
    assert original_url == 'https://example.com'

    # Verify cache hit
    cached_url = shortener.get_original(short_code)  # Should hit cache
    assert cached_url == 'https://example.com'
```

### Testing Database Transactions

```python
def test_withdraw_rollback_on_insufficient_funds(postgres):
    """Test transaction rollback"""
    account = BankAccount(db=postgres, balance=50)

    # Try to withdraw $100 (should fail)
    with pytest.raises(InsufficientFundsError):
        account.withdraw(100)

    # Balance should remain unchanged
    assert account.get_balance() == 50
```

### Testing Cache Invalidation

```python
def test_cache_invalidation_on_update(postgres, redis):
    """Update should invalidate cache"""
    shortener = URLShortener(db=postgres, cache=redis)

    # Create URL
    result = shortener.shorten('https://example.com')
    short_code = result['short_code']

    # First access (cache miss)
    url1 = shortener.get_original(short_code)
    assert redis.get(f'url:{short_code}') is not None  # Now cached

    # Update URL (should invalidate cache)
    shortener.update(short_code, 'https://updated.com')

    # Cache should be invalidated
    assert redis.get(f'url:{short_code}') is None

    # Next access should fetch from DB
    url2 = shortener.get_original(short_code)
    assert url2 == 'https://updated.com'
```

---

## Contract Testing

### What is Contract Testing?

**Problem:** Microservices break when APIs change
**Solution:** Test API contracts independently

### Pact - Consumer-Driven Contracts

```python
# Consumer test (URL Shortener Service)
from pact import Consumer, Provider

pact = Consumer('URLShortener').has_pact_with(Provider('AnalyticsService'))

def test_get_analytics_contract():
    """Define contract: What URLShortener expects from Analytics"""
    expected = {
        'short_code': 'abc123',
        'clicks': 100,
        'unique_visitors': 75,
        'top_referrers': ['google.com', 'twitter.com']
    }

    (pact
     .given('analytics exist for abc123')
     .upon_receiving('a request for analytics')
     .with_request('GET', '/analytics/abc123')
     .will_respond_with(200, body=expected))

    with pact:
        analytics = analytics_client.get_analytics('abc123')
        assert analytics['clicks'] == 100
```

```python
# Provider test (Analytics Service)
from pact import Verifier

def test_verify_analytics_contract():
    """Verify Analytics Service satisfies contract"""
    verifier = Verifier(provider='AnalyticsService')

    # Run provider against consumer's contract
    output, logs = verifier.verify_pacts(
        './pacts/urlshortener-analyticsservice.json',
        provider_base_url='http://localhost:8000',
        provider_states_setup_url='http://localhost:8000/_pact/provider_states'
    )

    assert output == 0  # All contract tests passed
```

### Benefits of Contract Testing

✅ **Catch breaking changes early** (before deploy)
✅ **Independent testing** (no need for full E2E)
✅ **Fast feedback** (seconds, not minutes)
✅ **Living documentation** (contracts = API docs)

---

## End-to-End Testing

### When to Use E2E Tests

**Only for critical user journeys:**
- User signup → create URL → share → track clicks
- Payment flow end-to-end
- Critical security flows (authentication)

### Example: E2E Test with Playwright

```python
from playwright.sync_api import sync_playwright

def test_url_shortener_e2e():
    """Test complete user journey"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Go to homepage
        page.goto('http://localhost:3000')

        # 2. Enter long URL
        page.fill('#url-input', 'https://example.com/very/long/url')
        page.click('#shorten-button')

        # 3. Wait for short URL
        page.wait_for_selector('#short-url')
        short_url = page.inner_text('#short-url')

        # 4. Verify short URL format
        assert 'http://short.ly/' in short_url

        # 5. Click short URL (new tab)
        with page.expect_popup() as popup_info:
            page.click('#short-url')

        popup = popup_info.value
        popup.wait_for_load_state()

        # 6. Verify redirect to original URL
        assert popup.url == 'https://example.com/very/long/url'

        # 7. Go back and check analytics
        page.click('#view-analytics')
        page.wait_for_selector('#click-count')
        clicks = page.inner_text('#click-count')

        # 8. Verify click was counted
        assert clicks == '1'

        browser.close()
```

### E2E Test Best Practices

**1. Use Page Object Model:**
```python
class URLShortenerPage:
    def __init__(self, page):
        self.page = page

    def shorten_url(self, url):
        self.page.fill('#url-input', url)
        self.page.click('#shorten-button')
        return self.page.inner_text('#short-url')

    def get_analytics(self, short_code):
        self.page.goto(f'/analytics/{short_code}')
        return {
            'clicks': int(self.page.inner_text('#click-count')),
            'unique_visitors': int(self.page.inner_text('#unique-visitors'))
        }

# Test becomes cleaner
def test_url_shortener_e2e():
    shortener_page = URLShortenerPage(page)
    short_url = shortener_page.shorten_url('https://example.com')
    analytics = shortener_page.get_analytics(extract_code(short_url))
    assert analytics['clicks'] == 1
```

**2. Minimize E2E Tests:**
- Only test critical paths
- Keep under 20 E2E tests
- Run in CI but not on every commit

**3. Make Tests Resilient:**
```python
# ❌ Brittle: Hardcoded wait
time.sleep(5)

# ✅ Resilient: Wait for condition
page.wait_for_selector('#short-url', timeout=10000)

# ✅ Retry on flake
@retry(tries=3, delay=2)
def test_flaky_operation():
    pass
```

---

## Load Testing

### Why Load Test?

- Find bottlenecks before production
- Validate performance requirements
- Determine breaking points
- Plan capacity

### Tools

- **k6** - Modern, script-able (JavaScript)
- **Apache Bench** - Simple, quick tests
- **Gatling** - Scala-based, detailed reports
- **Locust** - Python-based, easy to learn

### Example: k6 Load Test

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
  },
};

export default function () {
  // Shorten URL
  let shortenRes = http.post('http://localhost:8000/shorten', JSON.stringify({
    url: `https://example.com/${__VU}-${__ITER}`  // Unique URL per request
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(shortenRes, {
    'shorten status is 201': (r) => r.status === 201,
    'shorten response time < 500ms': (r) => r.timings.duration < 500,
  });

  let shortCode = JSON.parse(shortenRes.body).short_code;

  sleep(1);  // Think time

  // Redirect
  let redirectRes = http.get(`http://localhost:8000/${shortCode}`, {
    redirects: 0  // Don't follow redirect
  });

  check(redirectRes, {
    'redirect status is 301': (r) => r.status === 301,
    'redirect response time < 100ms': (r) => r.timings.duration < 100,
  });
}
```

**Run test:**
```bash
k6 run load-test.js

# Output:
# ✓ shorten status is 201
# ✓ shorten response time < 500ms
# ✓ redirect status is 301
# ✓ redirect response time < 100ms
#
# http_req_duration.............avg=85ms p(95)=234ms p(99)=412ms
# http_reqs.....................20000
# http_req_failed...............0.15%
```

### Load Test Patterns

**1. Smoke Test** - Minimal load
```javascript
export let options = {
  vus: 1,  // 1 virtual user
  duration: '1m',
};
```

**2. Load Test** - Expected load
```javascript
export let options = {
  vus: 100,
  duration: '10m',
};
```

**3. Stress Test** - Find breaking point
```javascript
export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 500 },  // Keep ramping up
    { duration: '5m', target: 500 },
    { duration: '2m', target: 1000 }, // Until it breaks
  ],
};
```

**4. Soak Test** - Extended duration
```javascript
export let options = {
  vus: 100,
  duration: '24h',  // Run overnight
};
```

---

## Chaos Engineering

### Principles

1. **Assume failure will happen**
2. **Test in production** (with safeguards)
3. **Minimize blast radius**
4. **Automate experiments**

### Netflix's Chaos Monkey

**What it does:**
- Randomly terminates EC2 instances
- Forces system to handle failures
- Runs continuously in production

### DIY Chaos Engineering

```python
# chaos.py
import random
import docker
import time

client = docker.from_env()

def chaos_kill_random_container():
    """Kill a random container"""
    containers = client.containers.list()
    if not containers:
        return

    victim = random.choice(containers)
    print(f"🔥 Chaos: Killing container {victim.name}")
    victim.kill()

def chaos_network_latency(container_name, latency_ms=1000):
    """Add network latency to container"""
    container = client.containers.get(container_name)
    container.exec_run(f"tc qdisc add dev eth0 root netem delay {latency_ms}ms")
    print(f"🐌 Chaos: Added {latency_ms}ms latency to {container_name}")

def chaos_disk_fill(container_name, size_mb=1000):
    """Fill disk space"""
    container = client.containers.get(container_name)
    container.exec_run(f"dd if=/dev/zero of=/tmp/fill bs=1M count={size_mb}")
    print(f"💾 Chaos: Filled {size_mb}MB on {container_name}")

# Run chaos experiments
if __name__ == '__main__':
    while True:
        time.sleep(random.randint(60, 300))  # Every 1-5 minutes

        experiment = random.choice([
            chaos_kill_random_container,
            lambda: chaos_network_latency('api-server', 1000),
            lambda: chaos_disk_fill('database', 500)
        ])

        experiment()
```

### Chaos Experiment Example

```python
# Test: System survives database failure

def test_chaos_database_failure():
    """System should gracefully handle DB failure"""

    # 1. System is healthy
    response = requests.get('http://localhost:8000/health')
    assert response.status_code == 200

    # 2. Kill database
    db_container = docker.from_env().containers.get('postgres')
    db_container.kill()

    # 3. System should return 503 (not crash)
    response = requests.get('http://localhost:8000/shorten', json={'url': 'https://example.com'})
    assert response.status_code == 503
    assert 'database unavailable' in response.json()['error']

    # 4. Cached reads should still work
    response = requests.get('http://localhost:8000/abc123')
    assert response.status_code == 301  # Served from cache

    # 5. Restart database
    db_container.start()
    time.sleep(5)  # Wait for recovery

    # 6. System should recover
    response = requests.get('http://localhost:8000/health')
    assert response.status_code == 200
```

### Chaos Experiments to Run

**1. Instance Termination**
- Kill random API server
- System should continue serving

**2. Network Partition**
- Isolate database from API servers
- Test timeout handling, circuit breakers

**3. Resource Exhaustion**
- Fill disk to 100%
- Max out CPU
- Exhaust memory

**4. Clock Skew**
- Change system time
- Test time-dependent logic

**5. Dependency Failure**
- External API returns 500
- Test fallback behavior

---

## Testing Eventual Consistency

### The Problem

Distributed systems have eventual consistency. How do you test it?

### Strategy 1: Poll Until Consistent

```python
import time
import pytest

def test_cache_invalidation_eventual():
    """Test eventually consistent cache invalidation"""
    cache = DistributedCache()
    db = Database()

    # Update database
    db.update('user:123', {'name': 'Alice Updated'})

    # Cache might be stale immediately after
    # Poll until consistent (max 5 seconds)
    max_wait = 5
    start = time.time()

    while time.time() - start < max_wait:
        cached_user = cache.get('user:123')
        if cached_user and cached_user['name'] == 'Alice Updated':
            return  # ✅ Eventually consistent

        time.sleep(0.1)

    pytest.fail("Cache not consistent within 5 seconds")
```

### Strategy 2: Inject Consistency Checks

```python
class EventuallyConsistentTest:
    def assert_eventually(self, condition, timeout=5, interval=0.1):
        """Helper to test eventual consistency"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                if condition():
                    return  # ✅ Success
            except:
                pass
            time.sleep(interval)

        raise AssertionError(f"Condition not met within {timeout}s")

def test_distributed_counter():
    """Test eventually consistent counter"""
    counter = DistributedCounter()
    test = EventuallyConsistentTest()

    # Increment from 3 different nodes
    counter.increment(node=1)
    counter.increment(node=2)
    counter.increment(node=3)

    # Assert eventual consistency
    test.assert_eventually(
        lambda: counter.read() == 3,
        timeout=10
    )
```

### Strategy 3: Test Idempotency

```python
def test_idempotent_message_processing():
    """Process same message multiple times = same result"""
    processor = MessageProcessor()
    message = {'id': '123', 'amount': 100}

    # Process message 3 times
    result1 = processor.process(message)
    result2 = processor.process(message)
    result3 = processor.process(message)

    # All results should be identical (idempotent)
    assert result1 == result2 == result3

    # Balance should be incremented only once
    assert get_balance() == 100  # Not 300!
```

---

## Testing Data Consistency

### Race Condition Tests

```python
import concurrent.futures

def test_concurrent_seat_booking():
    """Two users try to book same seat simultaneously"""
    booking_system = BookingSystem()

    def book_seat(user_id):
        try:
            return booking_system.book_seat('A1', user_id)
        except SeatAlreadyBooked:
            return None

    # Two users book simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(book_seat, user_id='user1')
        future2 = executor.submit(book_seat, user_id='user2')

        result1 = future1.result()
        result2 = future2.result()

    # Exactly one should succeed
    assert (result1 is None) != (result2 is None)

    # Verify only one booking exists
    bookings = booking_system.get_bookings_for_seat('A1')
    assert len(bookings) == 1
```

### Lost Update Tests

```python
def test_no_lost_updates():
    """Test optimistic locking prevents lost updates"""
    account = BankAccount(balance=100)

    # Two transactions read balance=100
    tx1_balance = account.get_balance()
    tx2_balance = account.get_balance()

    # TX1: Deposit $50 (balance = 150)
    account.deposit(50, expected_version=tx1_balance.version)

    # TX2: Withdraw $30 (should fail - stale version)
    with pytest.raises(OptimisticLockError):
        account.withdraw(30, expected_version=tx2_balance.version)

    # Final balance should be $150, not $120
    assert account.get_balance() == 150
```

---

## Testing Strategies by System Type

### E-commerce System

**Critical tests:**
- ✅ Payment processing (idempotency)
- ✅ Inventory consistency (no overselling)
- ✅ Order state machine (valid transitions only)
- ✅ Cart abandonment (cleanup old carts)

### Social Media Feed

**Critical tests:**
- ✅ Feed generation (correct posts, correct order)
- ✅ Fan-out on write (all followers notified)
- ✅ Hot user handling (celebrity with 100M followers)
- ✅ Real-time updates (new posts appear quickly)

### Chat System

**Critical tests:**
- ✅ Message delivery (at-least-once)
- ✅ Message ordering (correct sequence)
- ✅ Read receipts (eventual consistency OK)
- ✅ Offline message queue (deliver when online)

### Payment System

**Critical tests:**
- ✅ Double-charge prevention (idempotency)
- ✅ Balance consistency (never negative)
- ✅ Transaction rollback (on failure)
- ✅ Reconciliation (payments match invoices)

---

## Testing Checklist

### Before Production ✅

**Unit Tests:**
- [ ] >80% code coverage
- [ ] All critical paths tested
- [ ] Edge cases covered
- [ ] Tests run in <5 minutes

**Integration Tests:**
- [ ] Database operations tested
- [ ] Cache invalidation tested
- [ ] External APIs mocked
- [ ] Tests use TestContainers

**Contract Tests:**
- [ ] Consumer contracts defined
- [ ] Provider verification passing
- [ ] Breaking changes caught

**Load Tests:**
- [ ] Tested at 2x expected load
- [ ] Stress test to find breaking point
- [ ] Soak test for 24 hours
- [ ] Latency p99 < 500ms

**Chaos Tests:**
- [ ] Survives instance termination
- [ ] Handles database failure gracefully
- [ ] Recovers from network partition
- [ ] Circuit breakers work

---

## Tools Summary

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **pytest** | Unit/Integration tests | Python projects |
| **JUnit** | Unit/Integration tests | Java projects |
| **Testcontainers** | Integration tests | Need real databases |
| **Pact** | Contract tests | Microservices |
| **Playwright/Cypress** | E2E tests | Web applications |
| **k6** | Load tests | Performance testing |
| **Locust** | Load tests | Python, custom scenarios |
| **Chaos Monkey** | Chaos engineering | Production resilience |
| **Toxiproxy** | Network chaos | Network failure testing |

---

## Key Takeaways

1. **Test Pyramid** - More unit tests, fewer E2E tests
2. **Test in Production** - Chaos engineering catches real issues
3. **Eventual Consistency** - Poll until consistent, test idempotency
4. **Load Test** - Find bottlenecks before users do
5. **Contract Tests** - Prevent breaking API changes
6. **Automate Everything** - Manual testing doesn't scale

---

## Next Steps

1. **Add tests to your project** - Start with unit tests
2. **Set up CI/CD** - Run tests on every commit
3. **Add load tests** - Find your breaking point
4. **Run chaos experiments** - Test failure handling
5. **Monitor in production** - Tests + monitoring = reliability

---

**Related Guides:**
- [Observability Guide](./system-design-topics/54-observability-and-sre-fundamentals.md)
- [Deployment Guide](./DEPLOYMENT-GUIDE.md) ← To be created
- [Hands-On Labs](./hands-on-labs/)

Good luck testing! 🧪
