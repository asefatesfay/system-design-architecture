# Noisy Neighbor Antipattern

## 🔴 The Problem

In multi-tenant systems or shared infrastructure, one tenant/process consumes excessive resources (CPU, memory, I/O, network), negatively impacting other tenants sharing the same resources. This leads to:
- Unpredictable performance for well-behaved tenants
- Unfair resource distribution
- SLA violations
- Customer churn

## Common Scenarios

### 1. **Multi-Tenant SaaS Applications**
- One customer runs expensive queries
- All customers share the same database
- Everyone else experiences slowdowns

### 2. **Shared Compute Resources**
- One pod/container uses 100% CPU
- Other pods on same node are starved
- Kubernetes node becomes unstable

### 3. **Database Connection Pool**
- One service holds connections too long
- Other services can't get connections
- Connection pool exhausted

### 4. **API Rate Limiting**
- One client makes too many requests
- API servers overloaded
- All clients experience high latency

## 📊 Impact

- **Performance**: 2-10x slowdown for affected tenants
- **Reliability**: SLA violations, timeouts
- **Customer satisfaction**: Users complain about inconsistency
- **Cost**: Need to over-provision to handle noisy neighbors

## ✅ Solutions

### 1. **Resource Quotas & Limits**

**Kubernetes Resource Limits:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

**Database Query Timeouts:**
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

rows, err := db.QueryContext(ctx, "SELECT * FROM large_table")
// Query will be cancelled after 5 seconds
```

### 2. **Rate Limiting (Per-Tenant)**

```go
// Token bucket rate limiter per tenant
type RateLimiter struct {
    limiters map[string]*rate.Limiter
    mu       sync.RWMutex
}

func (rl *RateLimiter) Allow(tenantID string) bool {
    rl.mu.RLock()
    limiter, exists := rl.limiters[tenantID]
    rl.mu.RUnlock()

    if !exists {
        rl.mu.Lock()
        // 100 requests per second per tenant
        limiter = rate.NewLimiter(100, 200)
        rl.limiters[tenantID] = limiter
        rl.mu.Unlock()
    }

    return limiter.Allow()
}

func handler(w http.ResponseWriter, r *http.Request) {
    tenantID := getTenantID(r)
    
    if !rateLimiter.Allow(tenantID) {
        http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
        return
    }
    
    // Handle request...
}
```

### 3. **Resource Isolation**

**Database: Separate Schemas or Databases per Tenant**
```go
// Route tenant to their own database
func getTenantDB(tenantID string) *sql.DB {
    return connectionPool[tenantID]
}

// Each tenant has isolated resources
db := getTenantDB(tenant.ID)
rows, err := db.Query("SELECT * FROM orders")
```

**Compute: Separate Node Pools**
```yaml
# High-value customers get dedicated node pool
apiVersion: v1
kind: Pod
metadata:
  name: premium-tenant-pod
spec:
  nodeSelector:
    tier: premium
  containers:
  - name: app
    image: myapp:latest
```

### 4. **Queue-Based Processing with Priority**

```go
type Task struct {
    TenantID string
    Priority int
    Work     func() error
}

type WorkerPool struct {
    queues map[string]chan Task  // Per-tenant queue
}

func (wp *WorkerPool) Submit(task Task) {
    queue := wp.queues[task.TenantID]
    
    select {
    case queue <- task:
        // Task queued
    default:
        // Queue full - tenant hitting limit
        log.Printf("Tenant %s queue full", task.TenantID)
    }
}
```

### 5. **Circuit Breakers per Tenant**

```go
type TenantCircuitBreaker struct {
    breakers map[string]*CircuitBreaker
    mu       sync.RWMutex
}

func (tcb *TenantCircuitBreaker) Execute(tenantID string, fn func() error) error {
    breaker := tcb.getBreaker(tenantID)
    
    if breaker.IsOpen() {
        return fmt.Errorf("circuit breaker open for tenant %s", tenantID)
    }
    
    err := fn()
    if err != nil {
        breaker.RecordFailure()
    } else {
        breaker.RecordSuccess()
    }
    
    return err
}
```

### 6. **Monitoring & Alerting**

```go
// Track resource usage per tenant
func recordTenantMetrics(tenantID string, duration time.Duration, cpuUsage float64) {
    prometheus.Histogram.
        WithLabelValues(tenantID).
        Observe(duration.Seconds())
    
    prometheus.Gauge.
        WithLabelValues(tenantID).
        Set(cpuUsage)
}

// Alert when tenant exceeds threshold
if cpuUsage > 80.0 {
    alerting.Send(fmt.Sprintf("Tenant %s high CPU: %.2f%%", tenantID, cpuUsage))
}
```

## 🎯 Best Practices

### 1. **Fair Share Scheduling**
- Use weighted fair queuing
- Ensure minimum resources for each tenant
- Allow burst capacity for idle tenants

### 2. **Tiered Service Levels**
```go
type ServiceTier int

const (
    TierFree ServiceTier = iota
    TierBasic
    TierPremium
)

func getResourceLimits(tier ServiceTier) ResourceLimits {
    switch tier {
    case TierFree:
        return ResourceLimits{QPS: 10, CPU: "100m", Memory: "128Mi"}
    case TierBasic:
        return ResourceLimits{QPS: 100, CPU: "500m", Memory: "512Mi"}
    case TierPremium:
        return ResourceLimits{QPS: 1000, CPU: "2000m", Memory: "2Gi"}
    }
}
```

### 3. **Bulkhead Pattern**
- Isolate different workload types
- Prevent cascade failures
```go
var (
    readPool  *WorkerPool  // For read operations
    writePool *WorkerPool  // For write operations
    queryPool *WorkerPool  // For analytics queries
)
```

### 4. **Graceful Degradation**
```go
func handleRequest(tenantID string) Response {
    limits := getTenantLimits(tenantID)
    
    if isOverLimit(tenantID, limits) {
        // Degrade service instead of rejecting
        return generateSimpleResponse()  // Cache, reduced data, etc.
    }
    
    return generateFullResponse()
}
```

## 📊 Detection Metrics

Monitor these metrics per tenant:
- **CPU usage** (percentage, cores)
- **Memory usage** (MB, percentage)
- **Query execution time** (p50, p95, p99)
- **Request rate** (QPS)
- **Database connections** (active, idle)
- **I/O operations** (reads/sec, writes/sec)
- **Network bandwidth** (MB/s)

## 🛠️ Tools

- **Kubernetes**: Resource quotas, LimitRanges, PodDisruptionBudgets
- **Rate limiting**: `golang.org/x/time/rate`, Redis-based rate limiters
- **Monitoring**: Prometheus, Grafana, DataDog
- **APM**: New Relic, Datadog APM, OpenTelemetry
- **Database**: Connection pooling (pgBouncer), query governors

## 🎯 Key Takeaways

1. **Isolate tenants**: Use quotas, limits, and separate resources
2. **Monitor per-tenant**: Track resource usage by tenant
3. **Rate limit**: Prevent any tenant from overwhelming system
4. **Fair share**: Ensure minimum resources for all tenants
5. **Tiered pricing**: Higher tiers get more resources
6. **Graceful degradation**: Slow down heavy users rather than failing

## 📚 Related Patterns

- Bulkhead Pattern
- Throttling Pattern
- Rate Limiting
- Priority Queue
- Multi-Tenancy Patterns
