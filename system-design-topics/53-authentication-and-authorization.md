# Authentication and Authorization

## Definition

**Authentication (AuthN)** verifies who a user/service is.
**Authorization (AuthZ)** decides what that identity can do.

## Key Concepts

### Identity and Session
- Identity providers (IdP): Okta, Auth0, Azure AD, Cognito
- Session models: server-side sessions vs stateless tokens
- Access token lifetime: short (minutes), refresh token lifetime: longer (days)

### Token Types
- JWT: self-contained, easy to validate locally, harder to revoke immediately
- Opaque token: requires introspection, easier centralized revocation

### Auth Protocols
- OAuth2 for delegated access
- OpenID Connect (OIDC) for login and identity claims
- mTLS/service identity (SPIFFE/SPIRE) for service-to-service trust

### Authorization Models
- RBAC: role-based, simple and common
- ABAC: attribute-based, more flexible and complex
- ReBAC: relationship-based ("viewer of document")

## Real-World Examples

### Google Login with OIDC
- User authenticates with Google
- App receives ID token (identity) + access token (API access)
- Backend validates token signature, issuer, audience, expiration

### Internal Microservices
- API Gateway validates user token
- Gateway passes service token to downstream services
- Services enforce resource-level permissions (not only gateway-level checks)

## When to Use

- Use **OIDC + OAuth2** for consumer login and API access
- Use **short-lived access tokens + refresh flow** for mobile/web apps
- Use **service identity + mTLS** for zero-trust service meshes

## Trade-offs

| Decision | Benefit | Cost |
|----------|---------|------|
| JWT access token | Fast local validation | Hard immediate revocation |
| Opaque token | Central control/revocation | Introspection latency |
| Fine-grained ABAC | Better least privilege | Higher policy complexity |

## Implementation Tips

1. Validate tokens strictly: `iss`, `aud`, `exp`, `nbf`, signature algorithm.
2. Rotate signing keys with JWKS and key IDs (`kid`).
3. Enforce least privilege scopes (e.g., `read:profile`, `write:invoice`).
4. Log authorization decisions for audit trails.
5. Add step-up auth (MFA) for high-risk operations.

## Common Pitfalls

- Mixing up authentication and authorization logic
- Long-lived tokens without rotation
- Trusting token claims without signature validation
- Authorization checks only at gateway, not at resource owners
- Missing tenant isolation checks in multi-tenant systems

## Related Topics

- [Idempotency](./11-idempotency.md)
- [Microservices Architecture](./26-microservices-architecture.md)
- [API Gateway](./27-api-gateway.md)
- [Security for System Design](./62-security-for-system-design.md)

## Interview Tips

- Start with threat model: token theft, replay, privilege escalation.
- Explain token lifecycle (issue, validate, rotate, revoke).
- Mention where policy is enforced (gateway + service + data layer).
- Call out tenant boundary and audit requirements explicitly.
