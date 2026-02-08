# Consistent Hashing

## Definition

**Consistent Hashing** is a distributed hashing technique that minimizes reorganization when nodes are added or removed, making it ideal for distributed systems, load balancing, and caching.

## Problem with Traditional Hashing

```python
# Traditional: hash(key) % num_servers
server = hash("user_123") % 4  # 4 servers

Problem: Add 1 server (4 → 5)
→ hash("user_123") % 5  # Different server!
→ 80% of keys remapped! ❌
→ Massive cache misses, data migration
```

## Consistent Hashing Solution

```
Hash ring (0° to 360°):
Place servers on ring
Place keys on ring
Key maps to next server clockwise

Add/remove server → Only nearby keys affected (~1/N)
```

## How It Works

```
        S1 (30°)
    K1      K2
S3              S2
(210°)          (150°)
    K4      K3
        S4 (270°)

Key K1 hashed to 45° → Next server clockwise = S2
Key K3 hashed to 200° → Next server clockwise = S3

Add S5 at 100°:
- Only keys between S1 and S5 move to S5
- Other keys unaffected ✅
```

## Real-World Examples

### Amazon DynamoDB
**Consistent hashing for data partitioning**

```
- Data distributed across nodes using consistent hashing
- Each node responsible for range of hash values
- Add node → Only 1/N data moves
- Remove node → Data redistributed to neighbors
- Virtual nodes (tokens) for better balance
```

### Memcached/Redis Clusters
**Client-side consistent hashing**

```python
from hash_ring import HashRing

servers = ['cache1:11211', 'cache2:11211', 'cache3:11211']
ring = HashRing(servers)

# Get server for key
server = ring.get_node('user_123')  # Returns 'cache2:11211'

# Add server → Minimal remapping
ring.add_node('cache4:11211')
```

### Apache Cassandra
**Token ring for data distribution**

```
Each node assigned token range
Data partitioned by hash(partition_key)

Example with 4 nodes:
Node 1: 0-25%
Node 2: 26-50%
Node 3: 51-75%
Node 4: 76-100%

Add node → Redistributes ranges evenly
```

### CDN Load Balancing
**Akamai, Cloudflare**

```
Route users to edge servers using consistent hashing
- User IP hashed to determine server
- Server added/removed → Minimal disruption
- Sticky sessions maintained
```

## Implementation

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node):
        """Add node with virtual nodes for better distribution"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_val = self._hash(virtual_key)
            self.ring[hash_val] = node
            bisect.insort(self.sorted_keys, hash_val)
    
    def remove_node(self, node):
        """Remove node"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_val = self._hash(virtual_key)
            del self.ring[hash_val]
            self.sorted_keys.remove(hash_val)
    
    def get_node(self, key):
        """Get node responsible for key"""
        if not self.ring:
            return None
        
        hash_val = self._hash(key)
        
        # Find next node clockwise
        idx = bisect.bisect_right(self.sorted_keys, hash_val)
        if idx == len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]

# Usage
ch = ConsistentHash(['server1', 'server2', 'server3'])

print(ch.get_node('user_123'))  # server2
print(ch.get_node('user_456'))  # server1

# Add server → minimal remapping
ch.add_node('server4')
print(ch.get_node('user_123'))  # Still server2 (probably)
```

## Virtual Nodes

```
Problem: Uneven distribution with few servers
3 servers = 3 points on ring → Unbalanced ❌

Solution: Virtual nodes
Each physical server = 100-500 virtual nodes
Better distribution ✅

server1 → [server1:0, server1:1, ..., server1:149]
server2 → [server2:0, server2:1, ..., server2:149]
```

## Benefits

✅ **Minimal remapping**
```
Traditional hash: Add 1 server → 80% keys move
Consistent hash: Add 1 server → 1/N keys move (25% with 4 servers)
```

✅ **Scalability**
```
Easy to add/remove nodes
No downtime needed
```

✅ **Load balancing**
```
With virtual nodes, load evenly distributed
```

## Use Cases

✅ **Distributed caching** (Memcached, Redis)
✅ **Load balancers** (distribute connections)  
✅ **Distributed databases** (Cassandra, DynamoDB)
✅ **CDNs** (route users to edges)
✅ **Service discovery** (microservices)

**Key Takeaway:** Consistent hashing minimizes data movement when scaling, making it essential for distributed systems!
