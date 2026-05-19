# Service Discovery, Config, and Feature Flags

## Definition

**Service discovery** lets services find each other dynamically.
**Configuration management** distributes runtime settings safely.
**Feature flags** control behavior without redeploying code.

## Key Concepts

### Discovery Patterns
- Client-side discovery (client picks instance)
- Server-side discovery (load balancer picks instance)
- Health checks and instance TTL/heartbeats

### Config Management
- Centralized config store with versioning
- Dynamic reload vs restart-based config changes
- Secret management and rotation (never hardcoded)

### Feature Flags
- Kill switch for rapid mitigation
- Gradual rollout (1%, 5%, 25%, 100%)
- Targeting by user cohort, tenant, or region

## Real-World Examples

### Canary Rollout
- New pricing engine behind flag
- Enable for internal users then 5% traffic
- Monitor errors/latency before wider rollout

### Service Discovery in Kubernetes
- Service DNS resolves pod endpoints
- Readiness probe removes unhealthy pods from traffic
- ConfigMap/Secret updates rollout safely

## When to Use

- Dynamic microservice environments
- Frequent configuration changes
- Safe experimentation and rollback needs

## Trade-offs

| Pattern | Benefit | Cost |
|--------|---------|------|
| Dynamic config reload | Faster response | Runtime state complexity |
| Heavy feature flag usage | Safer releases | Flag debt and logic sprawl |
| Client-side discovery | Better routing control | More client complexity |

## Implementation Tips

1. Version and audit every config change.
2. Validate config schema before applying.
3. Separate flags for release, ops, and experiments.
4. Add automatic expiry/cleanup for stale flags.
5. Keep fallback defaults when config service is unavailable.

## Common Pitfalls

- Long-lived stale feature flags
- Config changes without blast-radius controls
- Missing readiness checks causing traffic to unhealthy nodes
- Secrets copied into app logs by mistake

## Related Topics

- [Heartbeat Mechanism](./13-heartbeat-mechanism.md)
- [Load Balancing](./09-load-balancing.md)
- [Microservices Architecture](./26-microservices-architecture.md)
- [API Gateway](./27-api-gateway.md)

## Interview Tips

- Explain how discovery, config, and flags reduce deployment risk.
- Mention kill switches for incident mitigation.
- Include governance: ownership, audits, and cleanup cadence.
- Show failure behavior when config/discovery plane is down.
