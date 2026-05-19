# Security for System Design

## Definition

Security in system design means reducing risk across identity, data, infrastructure, and operations by applying layered controls and continuous monitoring.

## Key Concepts

### Security Foundations
- Threat modeling (assets, attackers, entry points, trust boundaries)
- Defense in depth (multiple independent controls)
- Least privilege for users, services, and infrastructure

### Data Protection
- Encryption in transit (TLS) and at rest (KMS-managed keys)
- Secrets management and key rotation
- Data classification and retention policies

### Application and API Security
- Input validation and output encoding
- WAF + rate limiting + bot/abuse detection
- Tenant isolation in multi-tenant architectures

## Real-World Examples

### SaaS Multi-Tenant Platform
- Row-level tenant isolation plus scoped tokens
- Per-tenant encryption keys for sensitive data
- Audit trails for admin actions

### Public API Platform
- OAuth2 scopes, DPoP/mTLS for sensitive clients
- Anomaly detection on auth failures and traffic spikes
- Automated secret scanning and dependency vulnerability checks

## When to Use

- Always; security is a baseline requirement
- Especially critical for fintech, healthcare, and enterprise B2B
- Required when handling PII, payment, or regulated data

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| Strict access controls | Lower breach risk | More operational complexity |
| Deep audit logging | Better forensics/compliance | Storage and privacy overhead |
| Strong tenant isolation | Better blast-radius control | Higher implementation effort |

## Implementation Tips

1. Create threat model diagrams during design reviews.
2. Enforce TLS everywhere, including service-to-service traffic.
3. Rotate secrets/keys automatically where possible.
4. Add security observability: auth anomalies, privilege changes, data exfil patterns.
5. Validate third-party dependencies and supply chain integrity.

## Common Pitfalls

- Hardcoded secrets in code or CI configs
- Shared admin credentials across environments
- Incomplete tenant isolation checks in queries
- Security controls without monitoring and alerting

## Related Topics

- [Authentication and Authorization](./53-authentication-and-authorization.md)
- [Rate Limiting](./10-rate-limiting.md)
- [API Gateway](./27-api-gateway.md)
- [Observability and SRE Fundamentals](./54-observability-and-sre-fundamentals.md)

## Interview Tips

- Start with assets and trust boundaries, not tools.
- Explain controls by layer: edge, app, data, ops.
- Mention incident response and forensic readiness.
- Tie decisions to risk reduction and compliance needs.
