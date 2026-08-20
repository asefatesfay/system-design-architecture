# Anti-Corruption Layer Pattern

## Overview

The **Anti-Corruption Layer (ACL)** pattern creates an isolation layer between different subsystems that don't share the same semantics. It translates between different domain models, preventing the legacy or external system's data model from "corrupting" your clean, modern domain model.

Think of it as a **translator and adapter** - it speaks the legacy system's language on one side and your modern system's language on the other, keeping them cleanly separated.

## Problem

When integrating with legacy systems or external APIs, you often face:

❌ **Domain model pollution** - Legacy data structures leak into your clean code
❌ **Tight coupling** - Your code depends on external system's quirks
❌ **Hard to test** - Business logic mixed with legacy integration
❌ **Difficult migration** - Can't replace legacy system without rewriting everything
❌ **Breaking changes** - External API changes break your entire application

```python
# Legacy system bleeds into your domain
class OrderService:
    def create_order(self, customer_data):
        # Your clean domain forced to use legacy format
        legacy_customer = {
            "CUST_ID": customer_data.id,  # Ugly naming
            "F_NAME": customer_data.first_name,
            "L_NAME": customer_data.last_name,
            "ADDR_LN1": customer_data.address.street,  # Flat structure
            "ADDR_CITY": customer_data.address.city,
            "STATUS_CD": "A",  # Cryptic codes
            "CREATE_DT": datetime.now().strftime("%Y%m%d%H%M%S")  # Weird formats
        }
        return legacy_api.create_customer(legacy_customer)
```

## Solution

✅ Create an **Anti-Corruption Layer** that translates between systems
✅ **Isolate** your domain model from external concerns
✅ **Encapsulate** all legacy system knowledge in one place
✅ **Protect** your clean architecture from external changes
✅ **Enable** gradual migration from legacy systems

```
┌─────────────────────────────────────────────────────────────┐
│                    Modern Application                        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Order      │  │   Customer   │  │   Product    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  │              │  │              │  │              │      │
│  │  (Clean      │  │  (Clean      │  │  (Clean      │      │
│  │   Domain)    │  │   Domain)    │  │   Domain)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Anti-Corruption Layer (ACL)                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Adapter    │  │  Translator  │  │   Facade     │      │
│  │              │  │              │  │              │      │
│  │ - Converts   │  │ - Maps       │  │ - Simplifies │      │
│  │   protocols  │  │   data       │  │   interface  │      │
│  │ - Handles    │  │   models     │  │ - Validates  │      │
│  │   errors     │  │ - Validates  │  │   data       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Legacy System                             │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  - Cryptic field names (CUST_ID, F_NAME)            │    │
│  │  - Weird date formats (YYYYMMDDHHMMSS)              │    │
│  │  - Status codes (A=Active, I=Inactive)               │    │
│  │  - Flat data structures                              │    │
│  │  - SOAP/XML protocols                                │    │
│  │  - Complex validation rules                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Real-World Use Cases

### 1. **Legacy System Migration**
**Scenario**: Migrating from 20-year-old mainframe to modern microservices.

**Without ACL**: Legacy data structures spread throughout new codebase → migration nightmare

**With ACL**: All legacy integration isolated in ACL → replace piece by piece without touching domain

### 2. **Third-Party Integration**
**Scenario**: Integrating with vendor API that has terrible naming (SKU_ID_VAL, PROD_DESC_TXT).

**Without ACL**: Ugly vendor naming spreads to your entire codebase

**With ACL**: Clean domain model internally, ACL handles vendor quirks

### 3. **Multi-System Integration**
**Scenario**: E-commerce site integrating with 5 different suppliers, each with different APIs.

**Without ACL**: OrderService knows about 5 different data formats → unmaintainable

**With ACL**: OrderService uses clean Product model, ACL adapts each supplier

### 4. **Gradual Modernization**
**Scenario**: Replacing Oracle ERP with modern solution over 2 years.

**Without ACL**: Direct Oracle calls everywhere → can't replace without big bang

**With ACL**: Replace ACL implementation system-by-system → gradual migration

### 5. **SAP/Salesforce Integration**
**Scenario**: Enterprise app needs to sync with SAP and Salesforce.

**Without ACL**: SAP/Salesforce objects pollute your domain model

**With ACL**: Clean internal model, ACL translates to/from SAP and Salesforce

## When to Use

✅ Integrating with **legacy systems** with poor data models
✅ Working with **third-party APIs** you don't control
✅ **Migrating** from old to new systems gradually
✅ Need to **protect** domain model from external changes
✅ Multiple **external systems** with different models for same concepts

## When NOT to Use

❌ Internal service-to-service calls (same team, same standards)
❌ External API is well-designed and aligns with your domain
❌ Simple CRUD operations with no business logic
❌ Over-engineering for systems you fully control
❌ Adding unnecessary translation layers "just in case"

## Related Patterns

- **Adapter Pattern**: ACL often uses adapters internally
- **Facade Pattern**: ACL provides simplified facade to complex legacy systems
- **Gateway Pattern**: ACL acts as gateway to external systems
- **Strangler Fig**: ACL enables gradual legacy replacement

## Implementation Components

### 1. **Domain Model** (Your Clean Model)
```python
@dataclass
class Customer:
    id: UUID
    email: str
    full_name: str
    address: Address
    status: CustomerStatus  # Enum
    created_at: datetime
```

### 2. **Legacy Model** (External System)
```python
# Legacy system format
{
    "CUST_ID": "12345",
    "EMAIL_ADDR": "john@example.com",
    "F_NAME": "John",
    "L_NAME": "Doe",
    "ADDR_LN1": "123 Main St",
    "STATUS_CD": "A",
    "CREATE_DT": "20240101120000"
}
```

### 3. **Translator** (ACL Core)
```python
class CustomerTranslator:
    def to_domain(self, legacy_data: dict) -> Customer:
        """Convert legacy → domain"""

    def to_legacy(self, customer: Customer) -> dict:
        """Convert domain → legacy"""
```

### 4. **Adapter** (Integration)
```python
class LegacyCustomerAdapter:
    def __init__(self, translator: CustomerTranslator):
        self.translator = translator

    def get_customer(self, customer_id: UUID) -> Customer:
        legacy_data = legacy_api.get_customer(str(customer_id))
        return self.translator.to_domain(legacy_data)
```

## Key Benefits

### 1. **Domain Model Protection**
Your clean domain model stays pure, unaffected by external quirks.

### 2. **Single Point of Change**
When legacy system changes, update ACL only → domain unchanged.

### 3. **Testability**
Mock ACL in tests → test business logic without legacy system.

### 4. **Gradual Migration**
Replace legacy system piece by piece behind ACL.

### 5. **Team Independence**
Domain team works with clean model, integration team handles ACL.

## Common Translation Tasks

| Legacy Format | Domain Format | Translation |
|---------------|---------------|-------------|
| `YYYYMMDDHHMMSS` | `datetime` | Parse string → datetime object |
| Status codes (`A`, `I`) | Enum (`ACTIVE`, `INACTIVE`) | Map codes → enum values |
| Flat structure | Nested objects | Group fields → objects |
| `CUST_ID` (string) | `id` (UUID) | Parse string → UUID |
| Null as `"N/A"` | `None` | Convert sentinel → None |
| Multiple fields | Single field | Combine `F_NAME` + `L_NAME` → `full_name` |

## Example

```python
# WITHOUT ACL - Legacy pollution
class OrderService:
    def create_order(self, items):
        # Forced to use legacy format
        order_data = {
            "ORD_ITM_LST": [{"SKU": i.sku, "QTY": i.qty} for i in items],
            "ORD_DT": datetime.now().strftime("%Y%m%d"),
            "STATUS": "P"  # What does "P" mean?
        }
        return legacy_api.create_order(order_data)

# WITH ACL - Clean domain
class OrderService:
    def __init__(self, order_adapter: OrderAdapter):
        self.adapter = order_adapter

    def create_order(self, items: List[OrderItem]) -> Order:
        # Use clean domain model!
        return self.adapter.create_order(items)
```

## Files

- [without_pattern/main.py](./without_pattern/main.py) - Legacy system polluting domain
- [with_pattern/main.py](./with_pattern/main.py) - Clean domain with ACL
- [demo/run_demo.py](./demo/run_demo.py) - Interactive demonstration
- [benchmarks/benchmark.py](./benchmarks/benchmark.py) - Performance comparison

## Running the Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start mock legacy system
python demo/mock_legacy_system.py

# Terminal 2: Run demo
python demo/run_demo.py

# Run benchmarks
python benchmarks/benchmark.py
```

## Performance Considerations

**Overhead**: Translation adds 0.1-1ms per operation
**Memory**: Temporary objects during translation
**Tradeoff**: Small overhead worth it for clean architecture

## Testing Strategy

1. **Unit test translators** - Test each translation in isolation
2. **Contract tests** - Verify ACL handles legacy format changes
3. **Integration tests** - Test full flow with real legacy system
4. **Mock ACL** - Test domain logic without legacy system

## Migration Strategy

### Phase 1: Add ACL
1. Create ACL layer
2. Route existing code through ACL
3. No functionality changes

### Phase 2: Clean Domain
1. Refactor domain model
2. Update ACL translators
3. Domain code improves

### Phase 3: Replace Legacy
1. Build new system behind ACL
2. Update ACL to call new system
3. Remove legacy system

## Further Reading

- [Microsoft Azure Anti-Corruption Layer](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) - Eric Evans
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
