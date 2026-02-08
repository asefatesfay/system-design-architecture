# Data Replication

## Definition

**Data Replication** is the process of creating and maintaining multiple copies of data across different servers or locations to improve availability, reliability, and performance.

## Replication Models

### 1. Primary-Replica (Master-Slave)
```
Primary (Master) → Writes
    ↓ Replicates
Replicas (Slaves) → Reads

Write: To primary only
Read: From replicas (load balanced)
```

**Examples:** MySQL, PostgreSQL, MongoDB

### 2. Multi-Primary (Master-Master)
```
Primary 1 ↔ Primary 2
Both accept writes and sync

Conflict resolution needed
```

### 3. Peer-to-Peer
```
All nodes equal, accept writes
Eventual consistency
```

**Examples:** Cassandra, DynamoDB

## Replication Strategies

### Synchronous Replication
```
Write → Primary → Wait for replica ACK → Confirm ✅

Pros: ✅ Guaranteed consistency
Cons: ❌ Higher latency
```

### Asynchronous Replication
```
Write → Primary → Confirm immediately ✅
       ↓
Replicate in background

Pros: ✅ Low latency
Cons: ❌ Replication lag (eventual consistency)
```

### Semi-Synchronous
```
Write → Primary → Wait for at least 1 replica → Confirm

Balance between consistency and performance
```

## Real-World Examples

### MySQL Replication
**Primary-replica model**

```sql
-- On primary
CREATE USER 'repl'@'replica_host' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'replica_host';

-- On replica
CHANGE MASTER TO
  MASTER_HOST='primary_host',
  MASTER_USER='repl',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=107;

START SLAVE;
```

### Amazon RDS Multi-AZ
**Synchronous replication for high availability**

```
Primary (us-east-1a) ──Sync──> Standby (us-east-1b)

Primary fails? Automatic failover to standby (1-2 minutes)
```

### Cassandra
**Peer-to-peer replication**

```
Replication factor = 3

Write to any node → Replicates to 2 others
Read from any node (configurable consistency)

Tunable consistency:
- ONE: Read from 1 replica (fast, may be stale)
- QUORUM: Read from majority (consistent)
- ALL: Read from all replicas (slow, very consistent)
```

### MongoDB
**Replica sets**

```javascript
rs.initiate({
  _id: "myReplicaSet",
  members: [
    { _id: 0, host: "mongodb0.example.net:27017", priority: 2 },  // Primary
    { _id: 1, host: "mongodb1.example.net:27017" },  // Secondary
    { _id: 2, host: "mongodb2.example.net:27017" }   // Secondary
  ]
})

Primary fails → Automatic election of new primary
```

### Redis Sentinel
**Automatic failover**

```
Sentinel monitors primary + replicas
Primary fails → Sentinel promotes replica to primary
Clients notified of new primary
```

## Benefits

✅ **High Availability**
```
Primary fails → Replica takes over
Minimal downtime
```

✅ **Read Scalability**
```
Distribute reads across replicas
10 replicas = 10x read capacity
```

✅ **Disaster Recovery**
```
Geo-replication (US, EU, Asia)
Region failure? Other regions operational
```

✅ **Data Locality**
```
Replicas in multiple regions
Users read from nearest replica (low latency)
```

## Challenges

❌ **Replication Lag**
```
Write to primary: balance = $100
Read from replica (1s lag): balance = $0 ❌ Stale!

Solutions:
- Read from primary for critical data
- Monitor lag
- Use synchronous replication
```

❌ **Conflict Resolution (Multi-Primary)**
```
User A: Set status = "online" (Primary 1)
User B: Set status = "offline" (Primary 2)
Conflict! Which wins?

Resolution strategies:
- Last-write-wins (timestamp)
- Version vectors
- Application-level resolution
```

❌ **Storage Overhead**
```
3 replicas = 3x storage cost
Trade-off: Availability vs cost
```

## Best Practices

✅ Use at least 3 replicas (quorum)
✅ Monitor replication lag
✅ Test failover procedures
✅ Use geo-replication for DR
✅ Choose appropriate consistency level

**Key Takeaway:** Replication provides high availability and read scalability but introduces consistency challenges. Choose replication strategy based on requirements!
