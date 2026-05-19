# Multi-Region and Disaster Recovery

## Definition

**Multi-region design** deploys services across geographic regions for latency and resilience.
**Disaster recovery (DR)** ensures business continuity when major failures occur.

## Key Concepts

### Topologies
- Active-passive: primary handles traffic, secondary is standby
- Active-active: multiple regions serve traffic concurrently

### Recovery Targets
- RPO (Recovery Point Objective): maximum acceptable data loss window
- RTO (Recovery Time Objective): maximum acceptable recovery time

### Traffic and Data
- Global traffic routing via DNS/Anycast/load-balancing
- Cross-region replication (sync or async)
- Regional isolation and blast-radius control

## Real-World Examples

### Payment Service (Low RPO)
- Primary region writes + synchronous quorum in 2 zones
- Async replica in backup region
- Automated failover playbook tested weekly

### Media Streaming (Low Latency)
- Active-active reads from nearest region
- Session metadata replicated globally
- CDN edge absorbs most traffic during regional degradation

## When to Use

- Business cannot tolerate regional outages
- Global users need low-latency access
- Compliance requires regional data controls

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Active-passive | Simpler control plane | Higher failover latency |
| Active-active | Better availability/latency | Conflict resolution complexity |
| Synchronous cross-region writes | Stronger consistency | Higher write latency |

## Implementation Tips

1. Explicitly define regional failover criteria and owner.
2. Separate control plane and data plane failure handling.
3. Run game days and failover drills with production-like traffic.
4. Keep infrastructure as code identical across regions.
5. Track replication lag and failover readiness on dashboards.

## Common Pitfalls

- DR plan exists but is never tested
- Shared dependency (single identity service) across all regions
- Unclear write authority in active-active mode
- Secrets/config not replicated to recovery region

## Related Topics

- [Strong vs Eventual Consistency](./06-strong-vs-eventual-consistency.md)
- [Domain Name System (DNS)](./15-dns.md)
- [Content Delivery Network (CDN)](./16-cdn.md)
- [Data Replication](./18-data-replication.md)

## Interview Tips

- Start from required RPO/RTO to pick architecture.
- State whether consistency or availability wins during region loss.
- Mention readiness checks and regular failover exercises.
- Include data residency and compliance constraints.
