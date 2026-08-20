# Pattern Selection Guide

A comprehensive guide to choosing the right pattern - when to use what, and understanding the differences between similar patterns.

---

## 🚀 Quick Start: What's Your Problem?

```
What's your main problem?
│
├─ External API calls need to be more RELIABLE
│  └─ → AMBASSADOR pattern
│     (Retry logic, circuit breakers, consistent logging)
│
├─ External system has UGLY/DIFFERENT data format
│  └─ → ANTI-CORRUPTION LAYER pattern
│     (Legacy codes, weird dates, cryptic names)
│
├─ Need to call MULTIPLE APIs for one operation
│  └─ → GATEWAY AGGREGATION pattern
│     (Mobile app needs user+orders+profile in one call)
│
├─ Need to CACHE frequently accessed data
│  └─ → CACHE-ASIDE pattern
│     (Product catalog, user profiles)
│
├─ Prevent failures from CASCADING
│  └─ → CIRCUIT BREAKER pattern
│     (Payment down shouldn't kill entire app)
│
└─ Handle BURST traffic smoothly
   └─ → QUEUE-BASED LOAD LEVELING pattern
      (Black Friday sales, viral content)
```

---

## 🤔 Ambassador vs Anti-Corruption Layer

### The Confusion

Both patterns sit between your app and external systems. **But they solve different problems!**

### The Key Distinction

| Aspect | Ambassador | Anti-Corruption Layer |
|--------|-----------|----------------------|
| **Focus** | **HOW** you communicate | **WHAT** you communicate |
| **Purpose** | Connectivity (retry, logging) | Translation (format conversion) |
| **Data Model** | Same on both sides | Different on each side |
| **Analogy** | Smart HTTP client | Translator between languages |

### Visual Comparison

**Ambassador (no data change):**
```
Your App (Customer) → Ambassador [retry/log] → API (Customer)
                      ↑ Same model
```

**Anti-Corruption Layer (translates data):**
```
Your App (Customer) → ACL [translate] → Legacy ({"F_NAME", "STATUS_CD"})
                      ↑ Different models
```

### When to Use What

**Use Ambassador when:**
- ✅ API is well-designed (good naming, structure)
- ✅ Need retry, circuit breaker, logging
- ✅ Problem: **HOW** to call reliably
- Example: Stripe API (clean, but needs retry)

**Use Anti-Corruption Layer when:**
- ✅ API has bad format (cryptic codes, weird dates)
- ✅ Want to protect your domain from external changes
- ✅ Problem: **WHAT** format to use
- Example: Mainframe with STATUS_CD="A", YYYYMMDDHHMMSS dates

**Use BOTH when:**
- ✅ System is unreliable AND has ugly format
- Example: Legacy mainframe (bad format + times out)

```
Your App → ACL (translate) → Ambassador (retry) → Legacy System
```

### Decision Tree

```
Is external API well-designed?
│
├─ YES → Need reliability features?
│        ├─ YES → AMBASSADOR (Stripe with retry)
│        └─ NO  → Direct HTTP (simple API)
│
└─ NO  → Has ugly/legacy format?
         ├─ YES → Also unreliable?
         │        ├─ YES → BOTH (mainframe)
         │        └─ NO  → ACL only (bad vendor API)
         └─ NO  → AMBASSADOR (bad reliability only)
```

### Code Examples

**Scenario 1: Stripe API (Ambassador only)**
```python
# Clean API, just needs reliability
class PaymentService:
    def __init__(self, ambassador: StripeAmbassador):
        self.ambassador = ambassador

    def charge(self, amount):
        # Same model, reliable connectivity
        return self.ambassador.post("/charges", {"amount": amount})
```

**Scenario 2: Legacy Mainframe (Both ACL + Ambassador)**
```python
# Bad format AND unreliable

# 1. ACL: Translates data
class CustomerTranslator:
    def to_domain(self, legacy):
        return Customer(
            full_name=f"{legacy['F_NAME']} {legacy['L_NAME']}",
            status=self._map_status(legacy['STATUS_CD'])
        )

# 2. Ambassador: Handles connectivity
class MainframeAmbassador:
    def request(self, endpoint, data):
        # Retry, circuit breaker, logging
        ...

# 3. Adapter: Combines both
class LegacyAdapter:
    def get_customer(self, id):
        legacy_data = self.ambassador.get(f"/cust/{id}")  # HOW
        return self.translator.to_domain(legacy_data)     # WHAT
```

### Quick Reference

| Problem | Use | Why |
|---------|-----|-----|
| Clean API, needs retry | Ambassador | Adds connectivity |
| Ugly format, reliable | ACL | Translates data |
| Ugly + unreliable | BOTH | Need translation + reliability |

---

## 🔄 Other Pattern Comparisons

### Circuit Breaker vs Bulkhead

**Circuit Breaker:**
- Stops calling failing service (temporal isolation)
- "Stop trying, it's broken"
- Example: Payment API down → fail fast

**Bulkhead:**
- Isolates resources (spatial isolation)
- "Keep failures contained"
- Example: Payment has own thread pool

**Often used together!**

### Retry vs Circuit Breaker

**Retry:**
- Transient failures (optimistic)
- "Try again, might work"
- Example: 503 error → retry after 1s

**Circuit Breaker:**
- Sustained failures (protective)
- "Stop trying, won't recover soon"
- Example: API down 5 min → fail fast

**Used together in Ambassador!**

### Gateway Aggregation vs CQRS

**Gateway Aggregation:**
- External-facing (reduces client round trips)
- Example: Mobile app → one call for user+orders+notifications

**CQRS:**
- Internal architecture (separate read/write models)
- Example: Write to SQL, read from Elasticsearch

**Key difference:** Aggregation = UI optimization, CQRS = architecture

---

## 📋 Detailed Decision Trees

### External System Integration

```
Integrating with external system?
│
├─ Is API well-designed?
│  ├─ YES, could fail → AMBASSADOR
│  └─ NO, ugly format
│     ├─ Reliable → ANTI-CORRUPTION LAYER
│     └─ Unreliable → BOTH (ACL + Ambassador)
│
└─ Internal service? → Direct calls or SERVICE MESH
```

### Performance Problems

```
What's slow?
│
├─ Database
│  ├─ Same data fetched repeatedly → CACHE-ASIDE
│  ├─ Too many small queries (N+1) → Optimize or CQRS
│  └─ DB doing too much → Move logic to app
│
├─ API calls
│  ├─ Many sequential calls → Concurrency or GATEWAY AGGREGATION
│  └─ API slow/unreliable → AMBASSADOR
│
└─ Traffic spikes → QUEUE-BASED LOAD LEVELING
```

### Reliability Problems

```
What keeps failing?
│
├─ External API fails
│  ├─ Transient (network blips) → RETRY
│  └─ Sustained (service down) → CIRCUIT BREAKER
│
├─ One failure kills all → BULKHEAD
│
└─ System overloaded
   ├─ Too many requests → THROTTLING
   └─ Traffic bursts → QUEUE-BASED LOAD LEVELING
```

---

## 💼 Common Scenarios

### Scenario 1: E-commerce Checkout

**Problem:** Calls payment, shipping, notification APIs

**Solution:**
```
Ambassador
├─ Payment API (retry, circuit breaker)
├─ Shipping API (retry, logging)
└─ Notification API (retry, timeout)

+ Gateway Aggregation
  └─ Mobile: one call for checkout status

+ Cache-Aside
  └─ Product details
```

### Scenario 2: Legacy Migration

**Problem:** Replace 20-year-old mainframe

**Solution:**
```
Anti-Corruption Layer
└─ Translate: CUST_ID → Customer.id, STATUS_CD → enum

+ Ambassador
  └─ Handle unreliability (retry, circuit breaker)

+ Strangler Fig
  └─ Gradually replace behind ACL
```

### Scenario 3: High-Traffic Social Media

**Problem:** Millions of users, read-heavy

**Solution:**
```
CQRS
└─ Writes: SQL, Reads: Elasticsearch

+ Cache-Aside
  └─ Popular posts, profiles

+ Queue-Based Load Leveling
  └─ Handle viral posts

+ Circuit Breaker
  └─ Protect from cascades
```

---

## 🎯 Pattern Combinations

### Common Combos

1. **ACL + Ambassador** → Legacy system (ugly + unreliable)
2. **Gateway + Cache** → Mobile app (aggregate + cache)
3. **CQRS + Event Sourcing** → Audit trail + read scalability
4. **Circuit Breaker + Bulkhead** → Fail fast + resource isolation

---

## ⚠️ Anti-Patterns to Avoid

### Over-Engineering

**DON'T:**
```
Internal call → Ambassador → ACL → Gateway → Circuit Breaker
```

**DO:**
```
Internal call → Direct HTTP with basic retry
```

**Rule:** Only add patterns when you have the specific problem.

### Wrong Pattern

| Problem | WRONG | RIGHT |
|---------|-------|-------|
| Ugly format | Ambassador | ACL |
| Needs retry | ACL | Ambassador |
| Both issues | Just ACL or Ambassador | BOTH |

---

## 🧠 Practice Exercises

### Exercise 1: Twilio SMS API
**Scenario:** Twilio API occasionally returns 429 (rate limit) or 503.

**Question:** Which pattern?

<details>
<summary>Answer</summary>

**Ambassador Pattern**
- Retry on 503
- Back off on 429
- Circuit breaker for sustained failures
- Twilio has clean API, no ACL needed
</details>

### Exercise 2: Old HR System
**Scenario:** Returns `{"EMP_ID":"123", "F_NM":"John", "ST_CD":"A"}`. Reliable but ugly.

**Question:** Which pattern?

<details>
<summary>Answer</summary>

**Anti-Corruption Layer**
- Translate EMP_ID → id, F_NM → name, ST_CD → enum
- No Ambassador (system is reliable)
</details>

### Exercise 3: Legacy Mainframe
**Scenario:** Ugly format AND timeouts/failures.

**Question:** Which pattern?

<details>
<summary>Answer</summary>

**Both: ACL + Ambassador**
- ACL: Legacy format → domain model
- Ambassador: Retry, circuit breaker
- Flow: App → ACL → Ambassador → Mainframe
</details>

### Exercise 4: Mobile Dashboard
**Scenario:** Dashboard needs user profile + orders + notifications + wallet. Currently 4 API calls.

**Question:** Which pattern?

<details>
<summary>Answer</summary>

**Gateway Aggregation**
- Create `/dashboard` endpoint
- Backend calls all 4 services
- Returns combined response
- Optionally add Cache-Aside + Circuit Breaker
</details>

---

## 📚 Quick Reference

### Problem → Pattern Matrix

| Problem | Pattern | Why |
|---------|---------|-----|
| API needs retry | Ambassador | Adds connectivity |
| Ugly data format | Anti-Corruption Layer | Translates models |
| Multiple API calls | Gateway Aggregation | Combines into one |
| Frequently accessed | Cache-Aside | Reduces DB load |
| Service keeps failing | Circuit Breaker | Fail fast |
| Transient failures | Retry | Try again |
| Traffic spikes | Queue-Based Load Leveling | Smooth load |
| One failure affects all | Bulkhead | Isolate failures |
| Too many requests | Throttling | Rate limit |
| Read/write different | CQRS | Separate models |
| Need audit trail | Event Sourcing | Store events |

### Pattern Properties

| Pattern | Changes Data? | Adds Reliability? | Use Case |
|---------|---------------|-------------------|----------|
| Ambassador | ❌ | ✅ | Stripe, modern APIs |
| ACL | ✅ | ❌ | Legacy, bad APIs |
| BOTH | ✅ | ✅ | Unreliable legacy |

---

## ✅ Decision Checklist

Before adding a pattern:

1. **Do I have the specific problem this solves?**
   - ❌ No → Don't use it
   - ✅ Yes → Continue

2. **Is there a simpler solution?**
   - ✅ Yes → Use simpler solution
   - ❌ No → Continue

3. **Benefits outweigh complexity?**
   - ❌ No → Don't use it
   - ✅ Yes → Use the pattern

**Remember:** Patterns are tools, not rules. Use when needed, not because they're cool.

---

## 🔍 Building Intuition

Ask yourself:

1. **Is the problem the DATA FORMAT?** → ACL
2. **Is the problem CONNECTIVITY/RELIABILITY?** → Ambassador
3. **Need to TRANSLATE between models?** → ACL
4. **Need RETRY/CIRCUIT BREAKER/LOGGING?** → Ambassador
5. **BOTH ugly format AND unreliable?** → Use BOTH!

### Mental Models

- **Ambassador** = Smart HTTP client (connectivity)
- **ACL** = Translator (data model)
- **Gateway** = Combiner (multiple calls → one)
- **Circuit Breaker** = Stop switch (fail fast)
- **Cache** = Memory (avoid repeated work)
- **Queue** = Buffer (smooth traffic)

---

## 📖 See Also

- [Pattern Catalog](./README.md) - All available patterns
- [Learning Path](./README.md#learning-path) - Recommended order
- [Microsoft Azure Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
