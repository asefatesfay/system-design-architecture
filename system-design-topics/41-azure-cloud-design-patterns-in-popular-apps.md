# Azure Cloud Design Patterns in Popular Apps (System Design View)

This guide maps the Azure Architecture Center cloud design patterns to concrete places you would use them in real products. The focus is system design decisions, not only definitions.

Source catalog: Azure Architecture Center cloud design patterns page.

---

## How to Read This

- Pattern: The Azure pattern name.
- Where it fits in popular apps: A realistic place this appears in products like Netflix, Uber, Amazon, Discord, Slack, Spotify, YouTube, Airbnb, Shopify, and Figma.
- System design trigger: The architecture signal that tells you to apply the pattern.

---

## Pattern-to-Use Mapping

| Pattern | Where it fits in popular apps | System design trigger |
|---|---|---|
| Ambassador | Service-to-service egress helper in multi-cluster microservices (for example, Shopify checkout services calling payment providers through a local proxy). | You need shared outbound concerns (mTLS, retries, auth, telemetry) without modifying every service. |
| Anti-Corruption Layer | Modern order service translating between legacy ERP schemas and new domain models (common in Amazon-scale retail modernization). | You are integrating with legacy systems but want a clean new domain model. |
| Asynchronous Request-Reply | Video transcoding submit-and-poll flow (YouTube upload pipeline) or report generation (Shopify analytics export). | Processing is long-running, but clients need immediate acknowledgement and later result retrieval. |
| Backends for Frontends | Separate mobile, web, and partner APIs (Uber rider app vs driver app backend). | Different clients have distinct latency, payload, or feature needs and a single backend is becoming bloated. |
| Bulkhead | Isolating feed generation from notifications so failures do not cascade (Instagram or X-like systems). | One subsystem spike/failure must not consume all shared resources. |
| Cache-Aside | Product detail and pricing read optimization (Amazon/Shopify), or channel message history hot cache (Discord/Slack). | Read-heavy workload with repeated access to hot keys. |
| Choreography | Order lifecycle with events across payment, inventory, and shipping services (e-commerce marketplaces). | You want decentralized workflow coordination and independent service evolution. |
| Circuit Breaker | API clients calling third-party maps/payments (Uber, DoorDash) with failure isolation. | Repeated remote failures are causing thread exhaustion or latency amplification. |
| Claim Check | Large media metadata events: put blob in storage, send pointer through bus (YouTube/Netflix media pipelines). | Message broker payload limits or high queue cost for large messages. |
| Compensating Transaction | Travel booking rollback across flight, hotel, and payment steps (Airbnb Experiences-like multi-step booking). | Distributed write flow needs business-level undo instead of ACID transaction. |
| Competing Consumers | Background workers processing jobs from shared queue (email delivery, image processing, invoice generation). | Queue backlog grows and you need horizontal throughput scaling. |
| Compute Resource Consolidation | Consolidating low-utilization internal microservices onto fewer nodes for cost/perf balance (early-stage SaaS scaling). | Many services are underutilized and operational overhead is high. |
| CQRS | Separate write model for orders and read model for dashboards/search (Amazon order systems, Stripe-like ledgers). | Read and write paths have different scale/query shapes or consistency requirements. |
| Deployment Stamps | Multi-tenant SaaS replicated by region/stamp (Microsoft 365-like or Shopify pods). | You need repeatable isolation units for scale, compliance, and blast-radius control. |
| Event Sourcing | Immutable account/activity timeline (financial wallets, ride lifecycle history in Uber-like systems). | Auditability, temporal debugging, and replay are first-class requirements. |
| External Configuration Store | Feature flags and runtime config for gradual rollout (Netflix-style experimentation, mobile backend toggles). | You need dynamic config changes without redeploying services. |
| Federated Identity | Social login and enterprise SSO for collaboration apps (Figma, Slack, Notion). | You need trusted identity delegation to external IdPs (OIDC/SAML). |
| Gateway Aggregation | Mobile home screen assembled from profile, recommendations, and notifications APIs (Spotify/Netflix app shell). | Chatty client-to-microservice calls are inflating latency. |
| Gateway Offloading | TLS termination, WAF, auth token validation, and response compression at edge/API gateway (any hyperscale app). | Cross-cutting concerns are duplicated across services and costly to maintain. |
| Gateway Routing | Version- or tenant-aware routing to different backend clusters (canary and blue/green deploys). | You need smart request steering with a stable public endpoint. |
| Geode | Active-active global deployment where any region can serve users (Netflix/Spotify global streaming control planes). | Low-latency global access and regional fault tolerance are mandatory. |
| Health Endpoint Monitoring | Liveness/readiness and synthetic checks for service health (Kubernetes-based microservices everywhere). | You need fast fault detection and automated remediation triggers. |
| Index Table | Secondary lookup structures (user-by-email, order-by-customer) in NoSQL stores. | Primary key access is not enough for required query patterns. |
| Leader Election | Single scheduler/lease holder for periodic jobs (cron coordinator in distributed worker fleets). | Exactly one active coordinator is needed to avoid duplicate work. |
| Materialized View | Precomputed dashboards and feed projections (creator analytics in YouTube/Spotify for Artists). | Complex joins/aggregations are too expensive on request path. |
| Messaging Bridge | Bridging Kafka and cloud-native queue systems during migration/acquisition integration. | You must integrate heterogeneous messaging ecosystems without big-bang replacement. |
| Pipes and Filters | Multi-stage content moderation or ETL pipeline (TikTok/YouTube upload processing). | Processing can be decomposed into independent ordered stages. |
| Priority Queue | Premium customer support tickets and urgent fraud checks processed first (fintech/e-commerce ops). | Work items have strict urgency classes and shared workers. |
| Publisher-Subscriber | Event fan-out for order placed, ride completed, or content published events (Uber, Amazon, Discord). | Multiple downstream consumers need the same event, asynchronously. |
| Quarantine | Isolate untrusted user uploads before malware/content policy checks (Google Drive, Discord attachments). | External artifacts must be validated before becoming accessible. |
| Queue-Based Load Leveling | Absorb checkout spikes (Black Friday) between API and downstream fulfillment services (Amazon/Shopify). | Producers burst faster than consumers can process. |
| Rate Limiting | Per-user/API-key quotas in public APIs (GitHub, Stripe, OpenAI-style APIs). | You must protect shared capacity and enforce fair usage. |
| Retry | Transient network/database retry policy in client SDKs and service calls. | Failures are short-lived and often succeed on subsequent attempt. |
| Saga | Cross-service order transaction: payment, reserve inventory, create shipment (marketplaces/food delivery). | You need consistency across services without 2PC distributed transactions. |
| Scheduler Agent Supervisor | Orchestrated batch workflow with checkpoints/retry supervision (billing close process). | A long multi-step process requires explicit coordination, recovery, and observability. |
| Sequential Convoy | Preserve per-entity ordering (all events for one account in order) while parallelizing across accounts. | Some streams require in-order handling but global serialization is too slow. |
| Sharding | Partition user/messages/orders across database shards (Discord message stores, large social graphs). | Single database node no longer meets data volume or throughput needs. |
| Sidecar | Co-located proxy for telemetry, policy, secret rotation, or service mesh dataplane (Kubernetes workloads). | You need per-service platform capabilities without embedding SDK logic everywhere. |
| Static Content Hosting | Web assets and images served from CDN-backed object storage (Netflix artwork, Shopify storefront assets). | Content is mostly static and should be served cheaply at edge. |
| Strangler Fig | Gradual replacement of monolith modules with microservices (legacy e-commerce or banking modernization). | You need incremental migration with low risk and continuous delivery. |
| Throttling | Adaptive request shaping during overload or downstream constraints (search/autocomplete under traffic surges). | You need controlled degradation to preserve core user journeys. |
| Valet Key | Time-limited direct upload/download URL for media (Slack file uploads, Dropbox-like sharing). | Clients should access storage directly with scoped, temporary permission. |

---

## Quick Pattern Selection by Problem

- Latency from too many service hops: Gateway Aggregation, BFF, Cache-Aside.
- Resilience under partial failure: Circuit Breaker, Retry, Bulkhead, Health Endpoint Monitoring.
- Async scale and burst handling: Queue-Based Load Leveling, Competing Consumers, Pub/Sub, Priority Queue.
- Data consistency in microservices: Saga, Compensating Transaction, CQRS, Event Sourcing.
- Global scale and tenant isolation: Geode, Deployment Stamps, Sharding.
- Secure edge and content handling: Gateway Offloading, Federated Identity, Quarantine, Valet Key.
- Legacy modernization: Anti-Corruption Layer, Strangler Fig, Messaging Bridge.

---

## Design Notes for Interviews and Real Systems

- Patterns are composable. Real systems use bundles, for example: Retry + Circuit Breaker + Bulkhead.
- Pick patterns from workload bottlenecks, not fashion. Start from SLOs, failure modes, and scaling hotspots.
- Validate with production signals: p95 latency, saturation, queue depth, error budget burn, and recovery time.

For a dedicated estimation drill-down, see [42-back-of-the-envelope-estimation-framework.md](42-back-of-the-envelope-estimation-framework.md).
