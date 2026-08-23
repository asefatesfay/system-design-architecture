# Kafka Deep Dive: From Basics to Real-World Use Cases

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Understanding Offsets](#understanding-offsets)
3. [Consumer Groups](#consumer-groups)
4. [Offset Management Strategies](#offset-management-strategies)
5. [Real-World Use Cases](#real-world-use-cases)
6. [Best Practices](#best-practices)

---

## Core Concepts

### What is Kafka?
Kafka is a distributed streaming platform that allows you to:
- **Publish and subscribe** to streams of records (like a message queue)
- **Store** streams of records in a fault-tolerant, durable way
- **Process** streams of records as they occur

### Key Components

```
Producer → [Topic: Partition 0] → Consumer Group 1
           [Topic: Partition 1] → Consumer Group 2
           [Topic: Partition 2]
```

- **Producer**: Publishes messages to topics
- **Topic**: A category/feed name where records are published
- **Partition**: Topics are split into partitions for parallelism
- **Consumer**: Reads messages from topics
- **Consumer Group**: Multiple consumers working together
- **Broker**: Kafka server that stores data

---

## Understanding Offsets

### What is an Offset?

An **offset** is a unique sequential ID (number) assigned to each message within a partition. Think of it as a bookmark that tells you where you are in reading a book.

```
Partition 0:
┌─────────────────────────────────────────────────────┐
│ Offset: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 │
│ Msg:   A | B | C | D | E | F | G | H | I | J | K  │
└─────────────────────────────────────────────────────┘
         ↑                           ↑
    First message              Consumer is here
```

### Why Offsets Matter

1. **Resumability**: If your consumer crashes, it can resume from where it left off
2. **Replay**: You can rewind to any offset to reprocess data
3. **Tracking**: Kafka tracks which messages have been consumed
4. **Parallel Processing**: Each partition maintains its own offset sequence

### Offset Storage

Kafka stores consumer offsets in a special internal topic called `__consumer_offsets`. When you commit an offset, you're essentially saying:
> "I've successfully processed all messages up to offset X in partition Y"

---

## Consumer Groups

### What is a Consumer Group?

A consumer group is a set of consumers that work together to consume a topic. Each partition is consumed by exactly **one consumer** within the group.

### Example Scenario

```
Topic: orders (3 partitions)

Consumer Group: "order-processors"
┌──────────────────────────────────────────────┐
│                                              │
│  Consumer 1 → Partition 0 (offsets 0-100)  │
│  Consumer 2 → Partition 1 (offsets 0-150)  │
│  Consumer 3 → Partition 2 (offsets 0-80)   │
│                                              │
└──────────────────────────────────────────────┘

Consumer Group: "analytics"  (Different group, same topic!)
┌──────────────────────────────────────────────┐
│                                              │
│  Consumer A → Partition 0 (offsets 0-100)  │
│  Consumer B → Partition 1 (offsets 0-150)  │
│  Consumer C → Partition 2 (offsets 0-80)   │
│                                              │
└──────────────────────────────────────────────┘
```

**Key Point**: Different consumer groups can read the same data independently!

### Consumer Group Benefits

1. **Load Balancing**: Work is distributed among consumers
2. **Fault Tolerance**: If a consumer dies, its partitions are reassigned
3. **Independent Processing**: Multiple applications can consume the same data
4. **Scalability**: Add more consumers to process data faster

---

## Offset Management Strategies

### 1. Auto Commit (Default)

```python
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,  # Default
    'auto.commit.interval.ms': 5000  # Commit every 5 seconds
})
```

**Pros**: Simple, automatic
**Cons**: Risk of message loss or duplicate processing if consumer crashes

### 2. Manual Commit - Synchronous

```python
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my_group',
    'enable.auto.commit': False
})

while True:
    msg = consumer.poll(1.0)
    if msg:
        process_message(msg)
        consumer.commit()  # Commit after processing
```

**Pros**: Guaranteed at-least-once delivery
**Cons**: Slower due to synchronous commits

### 3. Manual Commit - Asynchronous

```python
consumer.commit(asynchronous=True)
```

**Pros**: Better performance
**Cons**: Slight risk if callback fails

### 4. Manual Offset Control

```python
from confluent_kafka import TopicPartition

# Store specific offset
tp = TopicPartition('my_topic', 0, 42)
consumer.commit(offsets=[tp])

# Seek to specific offset
consumer.seek(TopicPartition('my_topic', 0, 100))
```

### auto.offset.reset Options

```python
'auto.offset.reset': 'earliest'  # Start from beginning (offset 0)
'auto.offset.reset': 'latest'    # Start from end (only new messages)
'auto.offset.reset': 'none'      # Throw error if no offset found
```

**When does this matter?**
- First time a consumer group reads a topic
- When committed offset no longer exists (data was deleted)

---

## Real-World Use Cases

### 1. **Event Sourcing / Audit Logs**

**Scenario**: Banking transaction system

```python
# Producer: Bank transactions
producer.produce('bank-transactions', {
    'account_id': '12345',
    'amount': 500,
    'type': 'withdrawal',
    'timestamp': '2026-08-23T10:30:00Z'
})

# Consumer: Build account balance by replaying all transactions
# Uses 'earliest' to process from the beginning
consumer_config = {
    'group.id': 'balance-calculator',
    'auto.offset.reset': 'earliest'  # Process ALL historical data
}
```

**Why Offsets Matter**: You can rebuild the entire state by replaying from offset 0

---

### 2. **Real-Time Analytics**

**Scenario**: Website click tracking

```python
# Producer: User clicks
producer.produce('user-clicks', {
    'user_id': 'user123',
    'page': '/products',
    'timestamp': now()
})

# Consumer Group 1: Real-time dashboard (only care about recent data)
config = {
    'group.id': 'realtime-dashboard',
    'auto.offset.reset': 'latest'  # Only new clicks
}

# Consumer Group 2: ML training (needs all historical data)
config = {
    'group.id': 'ml-training',
    'auto.offset.reset': 'earliest'  # All historical clicks
}
```

**Why Consumer Groups Matter**: Same data, different processing needs!

---

### 3. **Order Processing Pipeline**

**Scenario**: E-commerce order fulfillment

```python
# Topic: orders
# Partition key: order_id (ensures order events stay in order)

# Consumer Group: "payment-processor"
# - Must process exactly once
# - Manual commit after payment succeeds

# Consumer Group: "inventory-service"
# - Can process in parallel
# - Different offset from payment-processor

# Consumer Group: "email-service"
# - Sends confirmation emails
# - Can retry from any offset if emails fail
```

---

### 4. **Change Data Capture (CDC)**

**Scenario**: Sync database changes to search index

```python
# Producer: Database writes
# Every INSERT/UPDATE/DELETE → Kafka

# Consumer: Elasticsearch indexer
config = {
    'group.id': 'elasticsearch-sync',
    'enable.auto.commit': False  # Manual commit after ES confirms write
}

while True:
    msg = consumer.poll()
    if msg:
        # Write to Elasticsearch
        es.index(data=msg.value())
        # Only commit after ES confirms
        consumer.commit()
```

**Why Manual Commit**: Ensures ES index stays in sync with database

---

### 5. **Log Aggregation**

**Scenario**: Collect logs from 1000s of services

```python
# Producers: Every microservice sends logs
service_a.send_log('errors', log_data)
service_b.send_log('errors', log_data)

# Consumer Group: "log-storage" (writes to S3)
# Consumer Group: "alerting" (monitors for critical errors)
# Consumer Group: "metrics" (extracts metrics)

# Each group independently tracks its offset
```

---

### 6. **Replay Scenario - Data Correction**

**Scenario**: Bug in processing logic, need to reprocess

```python
# Original processing had a bug
# Messages 0-1000 were processed incorrectly

# Solution: Reset offset and reprocess
from confluent_kafka import TopicPartition

consumer.assign([TopicPartition('my_topic', 0)])
consumer.seek(TopicPartition('my_topic', 0, 0))  # Go back to offset 0

# Now reprocess with fixed logic
while True:
    msg = consumer.poll()
    if msg.offset() <= 1000:
        process_with_fixed_logic(msg)
```

---

## Best Practices

### 1. **Choose the Right Offset Reset Strategy**

- `earliest`: Data warehousing, analytics, rebuilding state
- `latest`: Real-time monitoring, alerting, dashboards
- `none`: Strict applications that should fail if offset is lost

### 2. **Use Manual Commits for Critical Operations**

```python
# ❌ BAD: Auto-commit with external state
while True:
    msg = consumer.poll()
    database.write(msg)  # What if this fails after auto-commit?

# ✅ GOOD: Manual commit after successful write
consumer_config['enable.auto.commit'] = False
while True:
    msg = consumer.poll()
    database.write(msg)
    consumer.commit()  # Only commit after successful write
```

### 3. **Partition Keys for Ordering**

```python
# Ensure all events for same user go to same partition (maintains order)
producer.produce('events',
    key=str(user_id),  # Partition key
    value=event_data
)
```

### 4. **Monitor Consumer Lag**

```python
# Consumer lag = Latest offset - Consumer's committed offset
# High lag means consumer is falling behind
```

### 5. **Handle Rebalancing**

```python
def on_assign(consumer, partitions):
    print(f"Partitions assigned: {partitions}")

def on_revoke(consumer, partitions):
    print(f"Partitions revoked: {partitions}")
    consumer.commit()  # Commit before losing partitions

consumer.subscribe(['my_topic'],
    on_assign=on_assign,
    on_revoke=on_revoke
)
```

---

## Offset Scenarios Summary

| Scenario | auto.offset.reset | enable.auto.commit | Why |
|----------|-------------------|-------------------|-----|
| Real-time dashboard | `latest` | `True` | Only care about new data, speed matters |
| Historical analytics | `earliest` | `True` | Need all data, can tolerate some duplicates |
| Payment processing | `earliest` | `False` | Need all data, must ensure exactly-once |
| Log monitoring | `latest` | `True` | Only care about current logs |
| Data warehouse ETL | `earliest` | `False` | Need all data, must track what's loaded |

---

## Common Pitfalls

### 1. **Lost Messages with Auto-Commit**

```
1. Consumer polls message (offset 100)
2. Auto-commit commits offset 100
3. Consumer crashes before processing
4. Message 100 is lost!
```

**Solution**: Use manual commit after processing

### 2. **Duplicate Processing**

```
1. Consumer processes message (offset 100)
2. Consumer crashes before committing
3. Consumer restarts, processes offset 100 again
```

**Solution**: Make processing idempotent (safe to process twice)

### 3. **Consumer Lag**

```
Producer: 1000 messages/sec
Consumer: 500 messages/sec
→ Lag keeps growing!
```

**Solution**: Add more consumers to the group (up to # of partitions)

---

## Testing Offset Behavior

```bash
# Create topic with 3 partitions
kafka-topics --create --topic test-offsets \
  --partitions 3 --replication-factor 1

# Produce 100 messages
for i in {1..100}; do
  echo "Message $i" | kafka-console-producer --topic test-offsets
done

# Consumer 1: Read from beginning
kafka-console-consumer --topic test-offsets \
  --from-beginning --group test-group

# Consumer 2: Same group, will not see messages (already committed)
kafka-console-consumer --topic test-offsets \
  --from-beginning --group test-group

# Consumer 3: Different group, will see all messages
kafka-console-consumer --topic test-offsets \
  --from-beginning --group different-group
```

---

## Next Steps

1. **Run the examples** in this directory to see offsets in action
2. **Monitor offsets** using `kafka-consumer-groups --describe`
3. **Experiment** with different `auto.offset.reset` values
4. **Build** a real pipeline with multiple consumer groups
5. **Practice** reprocessing by manually seeking to offsets

---

## Further Reading

- [Kafka Documentation - Consumers](https://kafka.apache.org/documentation/#consumerapi)
- [Confluent - Offset Management](https://docs.confluent.io/platform/current/clients/consumer.html#offset-management)
- [Understanding Kafka Consumer Groups](https://www.confluent.io/blog/tutorial-getting-started-with-the-new-apache-kafka-0-9-consumer-client/)
