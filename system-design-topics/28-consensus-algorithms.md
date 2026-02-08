# Consensus Algorithms

## Definition

**Consensus Algorithms** enable multiple distributed nodes to agree on a single value or state, even in the presence of failures. Critical for building reliable distributed systems.

## The Problem

```
Distributed database with 3 nodes:
User updates balance: $100 → $200

Node 1: $200 ✓
Node 2: $200 ✓
Node 3: $100 ❌ (network partition)

How to ensure all nodes agree? → Consensus
```

## Key Challenges

1. **Network Partitions:** Nodes can't communicate
2. **Node Failures:** Nodes crash
3. **Message Loss:** Network unreliable
4. **Timing:** Can't rely on clocks being synchronized

**Goal:** All non-faulty nodes agree on same value

## CAP Theorem Reminder

```
Distributed systems can have at most 2 of 3:
- Consistency
- Availability  
- Partition Tolerance

Consensus helps choose the right tradeoff
```

## Paxos

**The classic consensus algorithm (1989)**

### How It Works

```
Roles:
- Proposer: Proposes values
- Acceptor: Votes on proposals  
- Learner: Learns chosen value

Phases:
1. Prepare: Proposer sends prepare(n) to acceptors
2. Promise: Acceptors promise not to accept proposals < n
3. Accept: If majority promise, proposer sends accept(n, value)
4. Accepted: If majority accept, value chosen

Guarantees:
- Safety: Only one value chosen
- Progress: Eventually value chosen (if majority alive)
```

### Example

```
Proposer wants to set value = 42

Phase 1:
Proposer → prepare(5) → [Acceptor1, Acceptor2, Acceptor3]
← promise(5) ← [Acceptor1, Acceptor2] (majority!)

Phase 2:
Proposer → accept(5, 42) → [Acceptor1, Acceptor2, Acceptor3]
← accepted(5, 42) ← [Acceptor1, Acceptor2] (majority!)

Value 42 chosen ✓
```

**Used by:** Google Chubby (lock service), Apache ZooKeeper (early versions)

**Challenge:** Paxos is notoriously difficult to understand and implement correctly.

## Raft

**Consensus made understandable (2014)**

### How It Works

```
Roles:
- Leader: Handles all client requests
- Follower: Replicate leader's log
- Candidate: During leader election

States:
Normal: 1 Leader + N Followers
Leader fails → Election → New leader
```

### Leader Election

```
1. Leader sends heartbeats to followers
2. If follower doesn't hear from leader (timeout) → becomes candidate
3. Candidate requests votes from other nodes
4. If receives majority → becomes leader
5. New leader replicates log to followers
```

### Log Replication

```
Client → Leader: Set x = 42

Leader log: [set x = 42] (uncommitted)
Leader → Followers: Append entry [set x = 42]

Follower1: Appended ✓
Follower2: Appended ✓
Follower3: Network partition ❌

Leader has majority (2/3) → Commit entry
Leader → Followers: Entry committed
All apply to state machine

Result: x = 42 on all nodes ✓
```

### Example

```
3-node cluster: [A, B, C]
Leader: A

1. Client writes: SET key1 = "hello"
2. A appends to log (uncommitted)
3. A replicates to B, C
4. B, C acknowledge
5. A commits (majority achieved)
6. A applies to state machine
7. A tells B, C to commit
8. All nodes: key1 = "hello" ✓
```

**Used by:** etcd, Consul, TiKV, CockroachDB

**Why Raft > Paxos:** Easier to understand and implement while providing same guarantees.

## Real-World Examples

### etcd (Kubernetes)
**Uses Raft for consensus**

```
Kubernetes stores cluster state in etcd
3-5 etcd nodes in Raft cluster

Write: Update pod definition
1. Leader receives write
2. Replicates to followers
3. Commits when majority acknowledge
4. Returns success

Even if 1 node fails, cluster continues (2/3 alive)
```

### Consul (Service Discovery)
**Uses Raft for service registry**

```
3 Consul servers in datacenter
Service registers: "payment-service @ 10.0.0.5:8080"

1. Leader receives registration
2. Replicates to followers
3. Commits when majority acknowledge

All servers have consistent view of services
```

### CockroachDB
**Uses Raft for distributed SQL**

```
Data partitioned into ranges
Each range has Raft group (3 replicas)

Write to range:
1. Leader of range receives write
2. Replicates to followers
3. Commits when majority acknowledge

Guarantees:
- Strong consistency
- Survives node failures
```

### Apache ZooKeeper
**Uses ZAB (similar to Paxos/Raft)**

```
Coordination service for distributed systems
Stores configuration, locks, leader election

Used by: Kafka, HBase, Hadoop
Ensures all nodes see consistent configuration
```

## Quorum

**Core concept in consensus**

```
Quorum = Majority of nodes must agree

3 nodes: Quorum = 2
5 nodes: Quorum = 3
7 nodes: Quorum = 4

Formula: N/2 + 1

Why majority?
- Prevents split-brain
- Two majorities always overlap → Consistency
```

### Read/Write Quorum

```
N = 3 replicas

Write Quorum (W) = 2
Read Quorum (R) = 2

W + R > N → Guaranteed to read latest write

Example:
Write to 2 nodes → Read from 2 nodes → At least 1 overlap
```

**Used by:** Cassandra, DynamoDB (tunable quorum)

```python
# Cassandra: Tunable consistency
session.execute(query, consistency_level=ConsistencyLevel.QUORUM)
# Waits for majority of replicas
```

## Two-Phase Commit (2PC)

**Not consensus, but related: Distributed transactions**

```
Distributed transaction across multiple databases

Phase 1 (Prepare):
Coordinator → Can you commit? → [DB1, DB2, DB3]
               ← Yes/No ←

Phase 2 (Commit):
If all Yes:
  Coordinator → Commit → [DB1, DB2, DB3]
Else:
  Coordinator → Abort → [DB1, DB2, DB3]
```

**Problem:** Coordinator failure = Blocking

**Used by:** XA transactions, distributed databases

## Comparing Algorithms

| Algorithm | Complexity | Performance | Fault Tolerance |
|-----------|------------|-------------|-----------------|
| **Paxos** | High | Good | N/2 + 1 |
| **Raft** | Medium | Good | N/2 + 1 |
| **2PC** | Low | Good | None (blocking) |
| **Quorum** | Low | Excellent | Tunable |

## Byzantine Fault Tolerance

**Additional challenge: Malicious nodes**

```
Not just crash failures, but:
- Nodes lie
- Corrupt messages
- Collude with other nodes
```

**PBFT (Practical Byzantine Fault Tolerance):**
```
Can tolerate (N-1)/3 Byzantine nodes
4 nodes: Tolerate 1 Byzantine
7 nodes: Tolerate 2 Byzantine
```

**Used by:** Blockchain (Bitcoin, Ethereum use variants)

## Best Practices

✅ **Use odd number of nodes**
```
3, 5, 7 nodes (not 4, 6)
Better failure tolerance for same cost
```

✅ **Deploy across availability zones**
```
3 nodes: One per AZ
Survives entire datacenter failure
```

✅ **Monitor leader health**
```
Alert on frequent leader elections
Indicates network instability
```

✅ **Tune timeouts carefully**
```
Too short: Unnecessary elections
Too long: Slow failover
```

## Interview Tips

**Q: "What is consensus?"**

**A:** Agreement among distributed nodes on a single value despite failures. Example: 3 database replicas must agree on account balance. Algorithms like Raft ensure all non-faulty nodes agree. Used by Kubernetes (etcd), Consul, CockroachDB for consistency.

**Q: "Raft vs Paxos?"**

**A:** Both achieve consensus, same guarantees (safety, liveness). Raft designed to be easier to understand/implement than Paxos. Raft has explicit leader, clear leader election, log replication phases. Paxos more flexible but complex. Most modern systems use Raft (etcd, Consul).

**Q: "How does distributed database maintain consistency?"**

**A:** Use consensus algorithm like Raft. Leader receives writes, replicates to followers, commits when majority acknowledge. Example: Write to 3-node cluster, leader waits for 2 nodes (quorum) before committing. Guarantees all nodes eventually have same data. Trade-off: Latency (wait for quorum) vs consistency.

**Q: "What is quorum?"**

**A:** Majority of nodes (N/2 + 1). For 5 nodes, quorum = 3. Used to ensure consistency: if write succeeds on quorum, subsequent read from quorum guaranteed to see write (quorums always overlap). Cassandra/DynamoDB use tunable quorum for consistency levels.

**Key Takeaway:** Consensus enables distributed systems to stay consistent despite failures. Raft most understandable!
