# Idempotency

## Definition

**Idempotency** is a property where an operation can be applied multiple times without changing the result beyond the initial application. In distributed systems, idempotent operations ensure that duplicate requests (retries, network issues) don't cause unintended side effects.

## Key Concept

```
f(f(x)) = f(x)

Applying the function multiple times = Applying it once
```

## Idempotent vs Non-Idempotent

### Idempotent Operations ✅

**HTTP Methods:**
- `GET /users/123` - Read same data multiple times (no state change)
- `PUT /users/123` - Update to same state multiple times = same result
- `DELETE /users/123` - Delete once or 100 times = user deleted

**Examples:**
```python
# Set value (idempotent)
user.email = "alice@example.com"  # Same result always ✅

# Absolute update (idempotent)
UPDATE users SET balance = 1000 WHERE id = 123  # Same end state ✅

# Delete (idempotent)
DELETE FROM users WHERE id = 123  # Delete once or many times ✅
```

### Non-Idempotent Operations ❌

**HTTP Methods:**
- `POST /orders` - Creates new order each time (different IDs)

**Examples:**
```python
# Increment (NOT idempotent)
user.balance += 100  # Different result each time ❌

# Relative update (NOT idempotent)
UPDATE users SET balance = balance + 100 WHERE id = 123  # Changes every time ❌

# Insert (NOT idempotent)
INSERT INTO orders (user_id, amount) VALUES (123, 50)  # Creates new row ❌
```

## Real-World Examples

### Payment Processing (Stripe, PayPal)
**Problem:** Network failure during payment

```python
# WITHOUT idempotency
Client: charge_card(card, $100) → Network timeout ❌
Client: retry charge_card(card, $100) → Success
Result: Customer charged $200! 😱

# WITH idempotency
Client: charge_card(card, $100, idempotency_key="order_123") → Network timeout
Client: retry charge_card(card, $100, idempotency_key="order_123") → Returns original result
Result: Customer charged $100 once ✅
```

**Stripe implementation:**
```python
import stripe

# Idempotent payment
stripe.PaymentIntent.create(
    amount=10000,  # $100.00
    currency="usd",
    payment_method="pm_card_visa",
    confirm=True,
    idempotency_key="unique_key_123"  # Same key = same result
)

# Retry with same key → Returns original charge, doesn't create new one ✅
```

### AWS S3 (PUT Operation)
**PUT is idempotent**

```bash
# Upload file
aws s3 cp file.txt s3://bucket/file.txt

# Upload again with same content
aws s3 cp file.txt s3://bucket/file.txt

# Result: Same file exists once, same content ✅
# Versioning adds complexity but operation is still idempotent
```

### Database Operations

#### Non-Idempotent (Increment)
```sql
-- ❌ Execute twice = wrong result
UPDATE accounts 
SET balance = balance + 100 
WHERE user_id = 123;

-- First execution: balance = 1000 + 100 = 1100
-- Second execution: balance = 1100 + 100 = 1200 ❌ Wrong!
```

#### Idempotent (Absolute Value)
```sql
-- ✅ Execute multiple times = same result
UPDATE accounts 
SET balance = 1100 
WHERE user_id = 123;

-- First execution: balance = 1100
-- Second execution: balance = 1100 ✅ Correct!
```

### Message Queue Processing (Kafka, RabbitMQ)

**Problem:** Message processed multiple times due to retry

```python
# NON-IDEMPOTENT (Bad)
def process_message(message):
    # Charge customer
    charge_card(message.card, message.amount)  # ❌ Duplicate charges!
    
    # Update inventory
    inventory -= message.quantity  # ❌ Wrong inventory count!

# IDEMPOTENT (Good)
def process_message(message):
    # Check if already processed
    if redis.exists(f"processed:{message.id}"):
        return  # Already processed, skip ✅
    
    # Process with idempotency key
    charge_card(message.card, message.amount, idempotency_key=message.id)
    
    # Mark as processed
    redis.setex(f"processed:{message.id}", 86400, "1")  # 24-hour TTL
```

### API Rate Limiting

**Idempotent rate limit check:**
```python
# Same request counted once even if processed multiple times
def rate_limit(user_id, request_id):
    key = f"ratelimit:{user_id}:{request_id}"
    
    # Use SET with NX (only set if not exists)
    if redis.set(key, 1, ex=60, nx=True):
        # First time seeing this request
        increment_counter(user_id)
        return True
    else:
        # Duplicate request, don't count again ✅
        return check_limit(user_id)
```

### E-commerce Order Creation (Amazon, Shopify)

**Problem:** User clicks "Place Order" multiple times (slow response, impatient user)

```python
# WITHOUT idempotency
POST /api/orders
{
    "user_id": 123,
    "items": [{"product_id": 456, "quantity": 1}],
    "amount": 99.99
}
# Click 1 → Order #1 created
# Click 2 → Order #2 created (duplicate!) ❌
# Click 3 → Order #3 created (duplicate!) ❌

# WITH idempotency
POST /api/orders
Headers:
    Idempotency-Key: cart_session_abc123
Body:
{
    "user_id": 123,
    "items": [{"product_id": 456, "quantity": 1}],
    "amount": 99.99
}
# Click 1 → Order #1 created
# Click 2 → Returns existing Order #1 ✅
# Click 3 → Returns existing Order #1 ✅
```

**Implementation:**
```python
@app.route('/api/orders', methods=['POST'])
def create_order():
    idempotency_key = request.headers.get('Idempotency-Key')
    
    if not idempotency_key:
        return {"error": "Idempotency-Key header required"}, 400
    
    # Check if order already exists
    existing_order = redis.get(f"order:{idempotency_key}")
    if existing_order:
        return json.loads(existing_order), 200  # Return existing ✅
    
    # Create new order
    order = create_new_order(request.json)
    
    # Store with TTL (24 hours)
    redis.setex(f"order:{idempotency_key}", 86400, json.dumps(order))
    
    return order, 201
```

## Implementation Patterns

### 1. Idempotency Key (Most Common)

**Client generates unique key:**
```python
import uuid

# Client side
idempotency_key = str(uuid.uuid4())  # or use order_id, cart_id, etc.

response = requests.post(
    'https://api.example.com/orders',
    headers={'Idempotency-Key': idempotency_key},
    json=order_data
)
```

**Server side:**
```python
from functools import wraps
import redis

redis_client = redis.Redis()

def idempotent(ttl=86400):  # 24 hours default
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get idempotency key from request headers
            idempotency_key = request.headers.get('Idempotency-Key')
            
            if not idempotency_key:
                return {"error": "Idempotency-Key required"}, 400
            
            cache_key = f"idempotent:{func.__name__}:{idempotency_key}"
            
            # Check cache
            cached_response = redis_client.get(cache_key)
            if cached_response:
                return json.loads(cached_response)  # Return cached ✅
            
            # Execute function
            response = func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(response))
            
            return response
        return wrapper
    return decorator

# Usage
@app.route('/api/orders', methods=['POST'])
@idempotent(ttl=86400)
def create_order():
    # Order creation logic
    order = {
        "id": generate_order_id(),
        "user_id": request.json['user_id'],
        "amount": request.json['amount']
    }
    db.save(order)
    return order
```

### 2. Database Constraints (Unique Constraint)

```sql
-- Ensure uniqueness at database level
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    user_id INT NOT NULL,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,  -- Prevents duplicates
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Try to insert
INSERT INTO orders (id, user_id, idempotency_key, amount)
VALUES (uuid_generate_v4(), 123, 'key_abc', 99.99)
ON CONFLICT (idempotency_key) DO NOTHING;  -- PostgreSQL

-- Or return existing
INSERT INTO orders (id, user_id, idempotency_key, amount)
VALUES (uuid_generate_v4(), 123, 'key_abc', 99.99)
ON CONFLICT (idempotency_key) 
DO UPDATE SET id = orders.id  -- No-op, just to return existing
RETURNING *;
```

### 3. Versioning (Optimistic Locking)

```python
# Ensure update only happens if version matches
def update_user(user_id, new_email, expected_version):
    result = db.execute(
        """
        UPDATE users 
        SET email = ?, version = version + 1
        WHERE id = ? AND version = ?
        """,
        [new_email, user_id, expected_version]
    )
    
    if result.rowcount == 0:
        # Version mismatch or user not found
        raise ConflictError("User was modified by another request")
    
    return {"status": "updated"}

# Client includes version
PUT /users/123
{
    "email": "newemail@example.com",
    "version": 5  # Current version
}
```

### 4. Distributed Locks

```python
import redis
import time

def with_distributed_lock(key, ttl=30):
    def decorator(func):
        def wrapper(*args, **kwargs):
            lock_key = f"lock:{key}"
            lock_id = str(uuid.uuid4())
            
            # Acquire lock
            if not redis_client.set(lock_key, lock_id, nx=True, ex=ttl):
                return {"error": "Request already processing"}, 409
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Release lock (only if we still own it)
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                redis_client.eval(lua_script, 1, lock_key, lock_id)
        return wrapper
    return decorator

@with_distributed_lock("order:user_123")
def create_order(user_id):
    # Only one request can execute at a time
    pass
```

## HTTP Method Idempotency

```
Method    Idempotent?    Safe?
GET       ✅ Yes         ✅ Yes (read-only)
PUT       ✅ Yes         ❌ No (modifies)
DELETE    ✅ Yes         ❌ No (modifies)
POST      ❌ No          ❌ No (creates new)
PATCH     ⚠️  Maybe      ❌ No (depends on implementation)
```

### Making POST Idempotent

```python
# Traditional POST (not idempotent)
POST /api/orders
→ Creates new order each time ❌

# Idempotent POST (with key)
POST /api/orders
Headers:
    Idempotency-Key: unique_key_123
→ Same key = same order ✅
```

## TTL Considerations

**How long to cache idempotency keys?**

```python
# Too short (1 minute)
- User retries after 2 minutes → Duplicate created ❌

# Too long (forever)
- Wastes storage
- Never allows same operation again (even if intended)

# Recommended: 24 hours to 7 days
- Most retries happen within minutes
- Balances storage and safety
- Can be adjusted per use case
```

**Example:**
```python
# Payment: 24 hours (users won't retry after a day)
redis.setex(f"payment:{key}", 86400, result)

# Order creation: 7 days (may need to reference)
redis.setex(f"order:{key}", 604800, result)

# API calls: 1 hour (short-lived)
redis.setex(f"api:{key}", 3600, result)
```

## Best Practices

✅ **Use idempotency keys for critical operations**
```python
# Financial transactions
# Order creation
# Account modifications
# Anything with side effects
```

✅ **Generate keys on client side**
```python
# Not server-generated (defeats purpose)
❌ key = str(uuid.uuid4())  # Server generates

# Client generates (can retry with same key)
✅ key = f"{user_id}:{cart_id}:{timestamp}"
✅ key = str(uuid.uuid4())  # Client-side UUID
```

✅ **Return same response for duplicate requests**
```python
# Don't just prevent duplicate - return original result
if cache.exists(key):
    return cache.get(key)  # Same status code, same body ✅
```

✅ **Use database constraints as backup**
```sql
-- Idempotency key + DB constraint = defense in depth
ALTER TABLE orders ADD CONSTRAINT unique_idempotency_key UNIQUE (idempotency_key);
```

✅ **Make GET/PUT/DELETE naturally idempotent**
```python
# PUT: Use absolute values (not relative)
PUT /users/123
{"name": "Alice", "age": 30}  # Same state every time ✅

# DELETE: HTTP 204 or 404
DELETE /users/123
First call: 204 No Content
Subsequent calls: 404 Not Found (but operation succeeded) ✅
```

✅ **Document idempotency requirements**
```
API Documentation:
POST /api/orders
Headers:
  Idempotency-Key: string (required, max 255 chars)
  
The same Idempotency-Key will return the same order, even if
called multiple times. Keys should be unique per order.
Keys are cached for 24 hours.
```

## Common Pitfalls

❌ **Forgetting side effects**
```python
# Bad: Email sent multiple times
def create_order(order_data, idempotency_key):
    if cache.exists(idempotency_key):
        return cache.get(idempotency_key)
    
    order = db.create(order_data)
    send_email(order)  # ❌ Sent even on cache hit path!
    cache.set(idempotency_key, order)
    return order

# Good: Email only sent once
def create_order(order_data, idempotency_key):
    if cache.exists(idempotency_key):
        return cache.get(idempotency_key)  # Early return ✅
    
    order = db.create(order_data)
    send_email(order)  # ✅ Only sent for new orders
    cache.set(idempotency_key, order)
    return order
```

❌ **Not handling races**
```python
# Bad: Two simultaneous requests create duplicates
if not cache.exists(key):  # Both check simultaneously
    result = create_order()  # Both create! ❌
    cache.set(key, result)

# Good: Atomic check-and-set
lua_script = """
if redis.call("exists", KEYS[1]) == 1 then
    return redis.call("get", KEYS[1])
else
    return nil
end
"""
cached = redis.eval(lua_script, 1, key)
if not cached:
    # Use distributed lock or database constraint
    with lock(key):
        result = create_order()
        cache.set(key, result)
```

❌ **Weak idempotency keys**
```python
# Bad: Predictable or not unique
❌ key = str(time.time())  # Can collide
❌ key = f"{user_id}"  # Not unique per operation

# Good: Truly unique
✅ key = str(uuid.uuid4())
✅ key = f"{user_id}:{operation}:{uuid.uuid4()}"
✅ key = f"cart_{cart_id}"  # If cart_id is unique
```

## Interview Tips

**Q: "What is idempotency and why is it important?"**

**A:**
```
Idempotency means an operation can be applied multiple times
without changing the result beyond the first application.

Important because:
- Network failures cause retries
- Users click buttons multiple times
- Message queues may deliver duplicates
- Prevents duplicate charges, orders, etc.

Examples: PUT, DELETE are idempotent. POST is not (creates new each time).
```

**Q: "How would you make a payment API idempotent?"**

**A:**
```
1. Require Idempotency-Key header from client
2. Store payment result in Redis/database with key
3. On retry with same key, return cached result
4. TTL: 24 hours (balance storage vs safety)
5. Database unique constraint as backup
6. Handle race conditions (distributed locks)
```

**Q: "PUT vs PATCH for idempotency?"**

**A:**
```
PUT: Idempotent (replaces entire resource with same state)
  PUT /users/123 {"name": "Alice", "age": 30}
  → Same result every time ✅

PATCH: Depends on implementation
  PATCH /users/123 {"age": 30}  → Idempotent (absolute value) ✅
  PATCH /users/123 {"age": "+1"}  → Not idempotent (relative) ❌

Recommendation: Use absolute values in PATCH for idempotency
```

**Key Takeaway:** Idempotency prevents duplicate operations in distributed systems. Use idempotency keys for critical operations, cache results, and handle retries gracefully!
