# Cloud Design Patterns Grouped by Popular Apps (System Design View)

This is a vendor-neutral version of cloud design patterns, grouped by how popular apps combine patterns to solve real scaling, reliability, and evolution problems.

---

## 1) Discord / Slack (Real-Time Collaboration)

### Typical architecture pressure
- Millions of concurrent websocket sessions.
- High fan-out messaging with uneven room sizes.
- Presence and notifications must feel instant.

### Pattern bundle you typically use
- Publisher-Subscriber + Competing Consumers + Queue-Based Load Leveling: decouple message ingest from fan-out and absorb bursts.
- Cache-Aside + Materialized View: fast channel history reads and precomputed unread counts.
- Bulkhead + Circuit Breaker + Retry: isolate gateway, message, and notification failures.
- Rate Limiting + Throttling: protect hot channels and abusive clients.
- Sharding + Sequential Convoy: keep per-channel order while scaling horizontally.

### Why this combination works
- Pub/Sub prevents sender-to-receiver tight coupling.
- Queue buffering keeps latency stable during spikes.
- Ordered processing per channel avoids inconsistent chat history.

---

## 2) Netflix / Spotify (Streaming and Personalization)

### Typical architecture pressure
- Global low-latency delivery.
- Heavy recommendation and metadata reads.
- High availability despite regional failures.

### Pattern bundle you typically use
- Geode + Deployment Stamps: active-active multi-region cells with controlled blast radius.
- Static Content Hosting + Valet Key: direct media/object access through scoped tokens.
- Gateway Aggregation + Backends for Frontends: tailor responses for TV, mobile, web clients.
- CQRS + Event Sourcing + Materialized View: write optimized event logs and read optimized recommendation views.
- Health Endpoint Monitoring + Leader Election: robust failover and controlled scheduled tasks.

### Why this combination works
- Regional cells reduce cross-region tail latency and limit outages.
- Event-first data model improves personalization and auditability.
- BFF keeps client contracts stable while backend evolves quickly.

---

## 3) Uber / DoorDash (Dispatch and Marketplace)

### Typical architecture pressure
- Real-time matching under strict latency SLOs.
- Third-party dependency fragility (maps, payments, sms).
- Continuous geo updates and event storms.

### Pattern bundle you typically use
- Saga + Compensating Transaction: orchestrate ride/order/payment consistency without 2PC.
- Circuit Breaker + Retry + Bulkhead: protect dispatch core from external outages.
- Priority Queue + Rate Limiting: prioritize critical flows (active trips) over non-critical jobs.
- Asynchronous Request-Reply + Queue-Based Load Leveling: submit long-running pricing/settlement workflows.
- Gateway Routing: route by region, city, tenant, or experiment cohort.

### Why this combination works
- Sagas keep business invariants across independent services.
- Priority-aware queues protect core business flows during incidents.
- Controlled retries avoid retry storms during partial outages.

---

## 4) Amazon / Shopify (E-commerce and Checkout)

### Typical architecture pressure
- Extreme seasonal burst traffic.
- Inventory/payment consistency across many services.
- Fast browsing with large catalog and filter sets.

### Pattern bundle you typically use
- Cache-Aside + Index Table + Materialized View: speed product listing/filter/search reads.
- Queue-Based Load Leveling + Competing Consumers: smooth order and fulfillment bursts.
- Saga + Compensating Transaction: checkout consistency (authorize payment, reserve stock, create shipment).
- Gateway Offloading + Federated Identity: edge auth, TLS, and policy centralization.
- Deployment Stamps + Sharding: scale tenants/regions while containing incidents.

### Why this combination works
- Read optimization avoids DB bottlenecks during campaigns.
- Async order pipeline prevents synchronous collapse under load.
- Stamp model simplifies compliance and operational isolation.

---

## 5) YouTube / TikTok (Media Upload and Processing)

### Typical architecture pressure
- Large uploads and expensive transcoding.
- Moderation and policy checks before publish.
- Massive fan-out once content goes live.

### Pattern bundle you typically use
- Valet Key + Claim Check: direct upload to object store and small metadata events on bus.
- Pipes and Filters: decode, transcode, thumbnail, moderation, and packaging stages.
- Quarantine: isolate untrusted media until checks pass.
- Asynchronous Request-Reply: upload accepted immediately, processing tracked asynchronously.
- Publisher-Subscriber: notify feeds, recommendations, search indexers, and subscribers.

### Why this combination works
- Removes heavy payloads from message bus.
- Pipeline stages scale independently by bottleneck.
- Safety gates prevent unsafe content from early exposure.

---

## 6) Airbnb / Booking (Travel Booking Platforms)

### Typical architecture pressure
- Multi-step reservations across payments, calendars, and notifications.
- Strong user trust requirements for correctness and transparency.
- Mixed consistency needs across different services.

### Pattern bundle you typically use
- Saga + Compensating Transaction: reserve listing, charge, confirm, and rollback safely.
- CQRS + Materialized View: fast availability search while keeping robust write workflows.
- External Configuration Store: dynamic feature flags for policy and pricing experiments.
- Priority Queue: prioritize in-progress booking actions over background jobs.

### Why this combination works
- Handles distributed consistency with clear business rollback.
- Keeps search fast while booking workflow stays reliable.

---

## 7) Figma / Notion (Collaborative SaaS)

### Typical architecture pressure
- Low-latency collaborative state sync.
- Frequent schema and feature evolution.
- Enterprise SSO and tenant policy controls.

### Pattern bundle you typically use
- Publisher-Subscriber + Backends for Frontends: real-time updates with client-specific shaping.
- Event Sourcing + Materialized View: document history and fast current-state reads.
- Federated Identity + Gateway Offloading: secure enterprise authentication and edge policies.
- External Configuration Store: tenant-specific feature gates and rollout controls.
- Bulkhead: isolate collaboration core from secondary integrations.

### Why this combination works
- Maintains collaboration responsiveness as product surface grows.
- Enables history/replay while keeping hot path read latency low.

---

## 8) GitHub / Stripe / Public API Platforms

### Typical architecture pressure
- Noisy neighbors and unpredictable client behavior.
- Strict API reliability and backward compatibility.
- High operational burden from many integrations.

### Pattern bundle you typically use
- Rate Limiting + Throttling + Priority Queue: protect core APIs and reserve capacity for premium/internal flows.
- Gateway Routing + Gateway Aggregation: versioned API routing and unified entrypoints.
- Retry + Circuit Breaker: resilient calls to internal and external dependencies.
- Health Endpoint Monitoring + Scheduler Agent Supervisor: stable background sync/reconciliation jobs.
- Messaging Bridge: migrate between queue systems without client disruption.

### Why this combination works
- Enforces fairness while preserving reliability SLOs.
- Decouples client contracts from internal service topology changes.

---

## Cross-App Pattern Shortcuts

- If traffic is bursty: Queue-Based Load Leveling + Competing Consumers + Priority Queue.
- If dependencies are flaky: Retry + Circuit Breaker + Bulkhead.
- If reads dominate: Cache-Aside + Materialized View + Index Table.
- If microservice writes must stay consistent: Saga + Compensating Transaction (+ CQRS when read/write shapes differ).
- If global scale is mandatory: Geode + Deployment Stamps + Gateway Routing.
- If modernization is ongoing: Strangler Fig + Anti-Corruption Layer + Messaging Bridge.

---

## Common Implementation Mistakes

- Retrying everywhere without budgets, causing retry storms.
- Using Saga without explicit idempotency keys.
- Sharding too early without clear rebalancing strategy.
- BFF duplication without shared schema contracts and governance.
- Event sourcing without retention and projection rebuild strategy.

---

## Distributed Systems Fallacies (With Real-World Use Cases)

These assumptions often look true in dev or early scale, then fail in production.

### Plain-English Terms (So the fallacies are easier to read)

- Topology: how services are connected at runtime (who calls whom, through which gateway, in which region).
Example: checkout API -> payment service -> fraud service -> ledger DB. If payment service moves to a new cluster/IP, topology changed.
- Service discovery: finding the current healthy address of a service dynamically instead of hardcoding IPs.
Example: `payment.internal` resolves to whichever payment pods are healthy right now.
- Health-based routing: send traffic only to instances that pass health checks.
Example: load balancer stops routing to a pod failing `/healthz`.
- Graceful drain: stop sending new requests to an instance, but let in-flight requests finish before shutdown.
Example: during deploy, an old API pod completes existing checkout requests before termination.
- Idempotency key: a client-generated unique key so repeating the same request does not create duplicate side effects.
Example: pressing "Pay" twice still creates one charge.
- Dead-letter queue (DLQ): failed messages are moved to a separate queue for inspection and replay.
Example: malformed "order shipped" events go to DLQ instead of blocking normal processing.
- SLO: target service level objective, such as p95 latency < 200 ms or monthly availability 99.9%.
Example: if error budget burns too fast, you pause feature rollouts to improve reliability.
- MTTR: mean time to recovery after incidents.
Example: better tracing reduces MTTR from 2 hours to 20 minutes.

### 1) "The network is reliable"
- Real-world use case: A ride dispatch service sends "driver accepted" events, but an intermittent network partition drops acknowledgements. Rider app times out and re-requests, creating duplicate assignment attempts.
- Design implication: Never assume delivery success. Use idempotency keys, retries with backoff, dead-letter queues, and reconciliation jobs.

### 2) "Latency is zero"
- Real-world use case: A global collaboration app writes document state in one region and reads in another. Even 120-200 ms RTT makes cursor sync feel laggy.
- Design implication: Keep write/read locality, use edge routing, cache hot reads, and prefer async workflows where user journey allows.

### 3) "Bandwidth is infinite"
- Real-world use case: A media app sends full state snapshots to mobile clients every few seconds. Users on constrained networks hit timeouts and battery drain.
- Design implication: Use deltas, compression, pagination, claim-check style payload indirection, and adaptive quality.

### 4) "The network is secure"
- Real-world use case: An internal service mesh trusts east-west traffic by default; a compromised service account laterally moves and reads sensitive APIs.
- Design implication: Apply zero-trust principles: mTLS, short-lived credentials, least privilege, workload identity, and continuous secret rotation.

### 5) "Topology doesn't change"
- Real-world use case: Hardcoded service endpoints break when autoscaling, failover, or blue/green deployment rotates instances and IPs.
- Design implication: Use service discovery, health-based routing, graceful drain, and resilient clients that re-resolve endpoints.

### 6) "There's one administrator"
- Real-world use case: Marketplace platform has separate teams for payments, catalog, and fulfillment, each with different deploy windows and incident runbooks.
- Design implication: Expect federated ownership. Define clear contracts, API version policies, SLOs, and platform guardrails.

### 7) "Component versioning is simple"
- Real-world use case: Mobile clients lag 2-6 months behind; backend removes a field used by older app versions, breaking checkout for a cohort.
- Design implication: Design backward/forward compatible schemas, additive API evolution, consumer-driven contract testing, and sunset timelines.

### 8) "Observability implementation can be delayed"
- Real-world use case: During a payment incident, teams lack trace correlation IDs across gateway, order, and payment services; MTTR expands from minutes to hours.
- Design implication: Ship observability on day one: structured logs, traces, metrics, SLO-based alerts, and dashboard/runbook links.

### Practical takeaway
- Treat each fallacy as a non-functional requirement risk register item.
- For every new critical workflow, explicitly decide: failure handling, timeout budget, retry policy, security boundary, discovery strategy, compatibility plan, and observability minimums.

### Quick Reference Checklist

| Fallacy | Symptom in prod | First 3 mitigations |
|---|---|---|
| The network is reliable | Silent data loss, duplicate events, partial writes | Idempotency keys · Retry with backoff · Dead-letter queue |
| Latency is zero | UI feels slow across regions, sync state lag | Edge routing · Local read replicas · Async where possible |
| Bandwidth is infinite | Mobile timeouts, high egress cost, slow payloads | Delta updates · Payload compression · Claim-Check pattern |
| The network is secure | Lateral movement after compromise, data exfiltration | mTLS · Workload identity · Least-privilege secret scoping |
| Topology doesn't change | Stale endpoints after autoscale, failed requests post-deploy | Service discovery · Health-based routing · Graceful drain |
| There is one administrator | Conflicting deploys, no clear incident owner, SLO gaps | Team contracts · API versioning policy · Federated runbooks |
| Component versioning is simple | Old mobile clients break on field removal, silent deserialization errors | Additive schema evolution · Consumer-contract tests · Sunset timelines |
| Observability can be delayed | Hours to root-cause incidents, no trace correlation across services | Structured logs · Distributed traces from day one · SLO-based alerts |

---

## Practical Design Rule

Choose patterns as bundles around one bottleneck at a time:
- Start from the failing SLO (latency, error rate, throughput, recovery time).
- Apply the smallest pattern set that moves that SLO.
- Validate with production metrics before adding more complexity.
