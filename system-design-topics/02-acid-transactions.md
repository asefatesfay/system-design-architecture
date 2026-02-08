# ACID Transactions

## Definition

ACID is a set of properties that guarantee database transactions are processed reliably. ACID stands for **Atomicity**, **Consistency**, **Isolation**, and **Durability**.

## Key Concepts

### A - Atomicity
**"All or nothing"**

A transaction is treated as a single unit that either:
- Completes entirely (COMMIT), or
- Fails entirely (ROLLBACK)

No partial execution is allowed.

**Example:**
```sql
BEGIN TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- Debit
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- Credit
COMMIT;
```
If the second UPDATE fails, the first one is rolled back automatically.

### C - Consistency
**"Data integrity is maintained"**

Transactions move the database from one valid state to another valid state, respecting all defined rules (constraints, triggers, cascades).

**Example:**
```sql
-- Constraint: balance >= 0
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
-- Transaction fails if balance would go negative
```

Database constraints ensure consistency:
- Primary keys
- Foreign keys
- Check constraints
- Unique constraints

### I - Isolation
**"Concurrent transactions don't interfere"**

Multiple transactions executing simultaneously should produce the same result as if they executed sequentially.

**Isolation Levels (weakest to strongest):**

1. **Read Uncommitted** (Dirty reads allowed)
2. **Read Committed** (PostgreSQL default)
3. **Repeatable Read** (MySQL InnoDB default)
4. **Serializable** (Strictest)

### D - Durability
**"Committed data survives crashes"**

Once a transaction is committed, it remains committed even if:
- System crashes
- Power fails
- Disk fails (with proper replication)

Achieved through:
- Write-Ahead Logging (WAL)
- Transaction logs
- Disk fsync operations
- Replication

## Real-World Examples

### Banking (Wells Fargo, Chase)
**Scenario:** Money transfer between accounts

```sql
BEGIN TRANSACTION;
  -- Debit sender
  UPDATE accounts SET balance = balance - 500 WHERE user_id = 'alice';
  
  -- Credit receiver
  UPDATE accounts SET balance = balance + 500 WHERE user_id = 'bob';
  
  -- Log transaction
  INSERT INTO transactions (from, to, amount) VALUES ('alice', 'bob', 500);
COMMIT;
```

**ACID Guarantees:**
- ✅ **Atomicity**: Can't have money deducted without crediting
- ✅ **Consistency**: Total money in system remains same
- ✅ **Isolation**: Concurrent transfers don't corrupt balances
- ✅ **Durability**: Transfer survives server crash

### E-commerce (Amazon, Shopify)
**Scenario:** Order placement

```sql
BEGIN TRANSACTION;
  -- Reduce inventory
  UPDATE products SET stock = stock - 1 WHERE id = 123;
  
  -- Create order
  INSERT INTO orders (user_id, product_id, amount) VALUES (456, 123, 99.99);
  
  -- Charge payment (external API call)
  -- If payment fails, entire transaction rolls back
COMMIT;
```

**Why ACID matters:**
- Prevents overselling (consistency)
- Ensures payment matches order (atomicity)
- Stock updates don't conflict (isolation)

### Booking Systems (Airbnb, Ticketmaster)
**Scenario:** Preventing double booking

```sql
BEGIN TRANSACTION;
  -- Check availability
  SELECT * FROM bookings WHERE room_id = 42 AND date = '2026-02-15' FOR UPDATE;
  
  -- If available, book it
  INSERT INTO bookings (room_id, user_id, date) VALUES (42, 789, '2026-02-15');
COMMIT;
```

**ACID prevents:**
- Two users booking the same room (isolation with row locking)
- Partial bookings (atomicity)

### Uber/Lyft - Trip Management

```sql
BEGIN TRANSACTION;
  -- Update driver status
  UPDATE drivers SET status = 'busy' WHERE id = 'driver_123';
  
  -- Create trip
  INSERT INTO trips (driver_id, rider_id, status) VALUES ('driver_123', 'rider_456', 'active');
  
  -- Update rider status
  UPDATE riders SET current_trip_id = LAST_INSERT_ID() WHERE id = 'rider_456';
COMMIT;
```

## Isolation Levels in Detail

### Read Uncommitted
```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
```
**Problems:**
- ❌ Dirty reads (read uncommitted data)
- ❌ Non-repeatable reads
- ❌ Phantom reads

**Use case:** Rarely used; maybe for approximate counts

### Read Committed (PostgreSQL default)
```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```
**Prevents:**
- ✅ Dirty reads

**Problems:**
- ❌ Non-repeatable reads
- ❌ Phantom reads

**Use case:** Most applications

### Repeatable Read (MySQL default)
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```
**Prevents:**
- ✅ Dirty reads
- ✅ Non-repeatable reads

**Problems:**
- ❌ Phantom reads (in some databases)

**Use case:** Financial applications

### Serializable (Strictest)
```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```
**Prevents:**
- ✅ All anomalies

**Trade-off:**
- ❌ Lowest concurrency
- ❌ Highest overhead
- ❌ More deadlocks

**Use case:** Critical operations (e.g., accounting, inventory)

## Trade-offs

### ACID vs Performance

**Costs of ACID:**
- ❌ Slower writes (WAL, fsync)
- ❌ Lock contention (with higher isolation)
- ❌ Limited horizontal scalability
- ❌ Higher resource usage

**Benefits:**
- ✅ Data correctness guaranteed
- ✅ Simpler application logic
- ✅ No partial failures
- ✅ Predictable behavior

### ACID vs Availability (CAP Theorem)

In distributed systems, you can't have all three:
- **Consistency** (ACID)
- **Availability**
- **Partition tolerance**

ACID databases typically choose CP (Consistency + Partition tolerance).

## NoSQL and BASE

Many NoSQL databases sacrifice ACID for scale:

**BASE:**
- **B**asically **A**vailable
- **S**oft state
- **E**ventual consistency

**Examples:**
- Cassandra: Eventually consistent
- DynamoDB: Configurable consistency
- MongoDB: ACID within a document, eventual across nodes

## When to Use ACID

✅ **Financial systems**
- Banking, payments, billing
- Accounting systems

✅ **Inventory management**
- E-commerce stock
- Ticket/seat reservations

✅ **Data integrity is critical**
- Healthcare records
- Legal documents
- Regulatory compliance

✅ **Complex transactions**
- Multi-step workflows
- Cross-table operations

## When NOT to Use ACID

❌ **High-volume, low-value data**
- Logging, analytics
- Social media posts
- IoT sensor data

❌ **Eventually consistent is acceptable**
- View counts, likes
- Recommendations
- Search indexes

❌ **Need extreme scalability**
- Global-scale applications
- Millions of writes/second

## ACID in Distributed Systems

### Distributed Databases with ACID
- **Google Spanner**: ACID globally with TrueTime
- **CockroachDB**: ACID with Raft consensus
- **YugabyteDB**: PostgreSQL-compatible, ACID distributed

### Challenges
- Network partitions
- Increased latency
- Complex coordination (2PC, Paxos, Raft)

## Implementation Best Practices

### 1. Keep transactions short
```sql
-- BAD: Long-running transaction
BEGIN;
  SELECT * FROM huge_table;  -- Takes minutes
  UPDATE accounts SET balance = 0 WHERE id = 1;
COMMIT;

-- GOOD: Short, focused transaction
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

### 2. Avoid user interaction in transactions
```sql
-- BAD
BEGIN;
  UPDATE inventory SET reserved = true WHERE id = 123;
  -- Wait for user to confirm (deadlock risk!)
COMMIT;

-- GOOD
-- Reserve with timestamp, release after timeout
UPDATE inventory SET reserved = true, reserved_until = NOW() + INTERVAL '5 minutes' WHERE id = 123;
```

### 3. Use appropriate isolation level
```sql
-- Don't always use SERIALIZABLE
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;  -- Usually sufficient
```

### 4. Handle deadlocks
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        with db.transaction():
            # Transaction code
            pass
        break
    except DeadlockError:
        if attempt == max_retries - 1:
            raise
        time.sleep(random.uniform(0.1, 0.5))  # Exponential backoff
```

## Interview Tips

**Common questions:**

1. **"What does ACID mean?"**
   - Explain each letter with concrete examples

2. **"Why might you choose NoSQL over ACID database?"**
   - Scale, speed, flexibility
   - When eventual consistency is acceptable

3. **"How do you handle transactions in microservices?"**
   - Saga pattern
   - Event sourcing
   - 2PC (rarely)

4. **"Difference between isolation levels?"**
   - Know the anomalies each prevents
   - Performance trade-offs

**Key Takeaway:** ACID guarantees correctness but sacrifices some performance and scalability. Choose based on your requirements!
