# Heartbeat Mechanism

## Definition

A **Heartbeat** is a periodic signal sent between systems to indicate that they are alive and functioning properly. It's used for health monitoring, failure detection, and maintaining connection state in distributed systems.

## Real-World Examples

### Kubernetes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10  # Heartbeat every 10s
```

### Kafka
- Brokers send heartbeats to ZooKeeper
- Consumers send heartbeats to group coordinator
- If heartbeat missed → Node considered dead

### Redis Sentinel
- Sentinel nodes ping master every second
- If 3 pings missed → Master marked as down
- Automatic failover initiated

### Database Replication (MySQL, PostgreSQL)
- Primary sends heartbeat to replicas
- Replica lag detected through missing heartbeats

## Implementation

```python
import time
import threading

class HeartbeatMonitor:
    def __init__(self, interval=5, timeout=15):
        self.interval = interval  # Send heartbeat every 5s
        self.timeout = timeout    # Consider dead after 15s
        self.last_heartbeat = {}
        self.running = True
    
    def send_heartbeat(self, node_id):
        """Record heartbeat from node"""
        self.last_heartbeat[node_id] = time.time()
    
    def check_health(self, node_id):
        """Check if node is alive"""
        if node_id not in self.last_heartbeat:
            return False
        
        elapsed = time.time() - self.last_heartbeat[node_id]
        return elapsed < self.timeout
    
    def monitor(self):
        """Background thread to check node health"""
        while self.running:
            current_time = time.time()
            for node_id, last_hb in self.last_heartbeat.items():
                if current_time - last_hb > self.timeout:
                    self.on_node_failure(node_id)
            time.sleep(self.interval)
    
    def on_node_failure(self, node_id):
        """Handle node failure"""
        print(f"Node {node_id} failed!")
        # Trigger failover, alerts, etc.
```

**Key Takeaway:** Heartbeats enable automatic failure detection and recovery in distributed systems!
