# Kafka Deep Dive Tutorial

A comprehensive guide to understanding Apache Kafka from basics to production-ready infrastructure.

## 📚 Learning Path

### Level 1: Fundamentals
Start with [KAFKA_DEEP_DIVE.md](./KAFKA_DEEP_DIVE.md) to understand:
- What is Kafka and why use it?
- **Offsets**: Your bookmark in the message stream
- **Consumer Groups**: Multiple consumers working together
- **Offset Management**: Auto vs manual commits
- Real-world use cases: Event sourcing, analytics, log aggregation

### Level 2: Infrastructure & Architecture
Continue with [KAFKA_INFRASTRUCTURE.md](./KAFKA_INFRASTRUCTURE.md) to learn:
- **Brokers**: Individual Kafka servers and what they do
- **Controllers**: The cluster manager (leader election, failure handling)
- **Partitions**: How data is split for parallelism (ordering, keys, throughput)
- **Replicas**: Data copies for fault tolerance (ISR, durability guarantees)
- Real-world architectures: E-commerce, IoT, banking, microservices

### Level 3: Hands-On (Your Turn!)
Now implement the concepts yourself:
- Experiment with different offset strategies
- Set up multi-broker clusters
- Test failure scenarios
- Tune partition counts and replication factors
- Build real-world pipelines

## 🗂️ What's Included

### Guides
- `KAFKA_DEEP_DIVE.md` - Offsets, consumer groups, and message consumption patterns
- `KAFKA_INFRASTRUCTURE.md` - Brokers, controllers, partitions, and replicas

### Code Examples (Basic)
- `producer.py` - Simple message producer
- `consumer.py` - Simple message consumer
- `main.py` - Entry point

## 🎯 Key Concepts Summary

### Offsets
- Sequential ID for each message in a partition (0, 1, 2, 3...)
- Your "bookmark" for tracking position
- Enables resuming after crashes, replaying data, and parallel consumption

### Consumer Groups
- Multiple consumers working together
- Each partition assigned to one consumer in the group
- Different groups can independently consume the same data

### Brokers
- Individual Kafka servers in a cluster
- Store partitions and serve read/write requests
- Scale horizontally by adding more brokers

### Controller
- Special broker elected as cluster manager
- Handles leader elections when brokers fail
- Manages partition assignments
- Only ONE controller at a time

### Partitions
- Topic is split into partitions for parallelism
- Each partition is an ordered, append-only log
- Messages with same key go to same partition (maintains ordering)
- More partitions = more parallelism = higher throughput

### Replicas
- Copies of partition data on different brokers
- One leader (handles reads/writes) + multiple followers (replicate)
- Replication factor = number of copies
- ISR (In-Sync Replicas) = replicas caught up with leader

## 🏗️ Typical Architecture

```
Producer → Topic (Partitions) → Consumer Groups
              ↓
         Brokers (Replicas)
              ↓
         Controller (Manages)
```

## 🚀 Real-World Patterns

### E-Commerce Orders
- Partition by `order_id`
- Replication factor: 3
- acks: all (durability)
- Multiple consumer groups: payment, inventory, email

### User Activity Feed
- Partition by `user_id` (maintains per-user ordering)
- Replication factor: 2
- acks: 1 (balanced)
- Scale with partitions

### IoT Sensors
- Partition by `sensor_id`
- Replication factor: 2
- acks: 0 (speed)
- High throughput, occasional loss OK

### Banking Transactions
- Partition by `account_id`
- Replication factor: 4 (extra durability)
- min.insync.replicas: 2
- acks: all (zero data loss)

## 🎓 Next Steps

1. **Read** the guides in order
2. **Run** the existing producer/consumer
3. **Experiment** with:
   - Different `auto.offset.reset` values
   - Manual offset commits
   - Multiple consumer groups reading same topic
   - Adding partitions
   - Setting up multi-broker clusters
4. **Build** something real:
   - Log aggregation system
   - Real-time analytics pipeline
   - Event-driven microservices
   - Change data capture (CDC)

## 📖 Additional Resources

- [Official Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Developer Resources](https://developer.confluent.io/)
- [Kafka: The Definitive Guide](https://www.confluent.io/resources/kafka-the-definitive-guide/)

## 💡 Quick Reference

```bash
# Start Kafka (Docker)
docker-compose up -d

# Create topic with 3 partitions, RF=2
kafka-topics --create --topic my-topic --partitions 3 --replication-factor 2

# Describe topic
kafka-topics --describe --topic my-topic

# Check consumer group offsets
kafka-consumer-groups --describe --group my-group

# Run producer
python producer.py

# Run consumer
python consumer.py
```

---

**Ready to dive deep? Start with [KAFKA_DEEP_DIVE.md](./KAFKA_DEEP_DIVE.md)!**
