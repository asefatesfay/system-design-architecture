# Anti-Corruption Layer Pattern - Quick Start

## Overview

The Anti-Corruption Layer (ACL) protects your clean domain model from external system ugliness. It translates between your beautiful modern code and that awful legacy system you're stuck with.

## Installation

```bash
cd design-patterns/02-anti-corruption-layer
pip install -r requirements.txt
```

## Running the Demo

### Step 1: Start Mock Legacy System

```bash
# Terminal 1
python demo/mock_legacy_system.py
```

This starts a mock legacy API on `http://localhost:8081` with:
- Cryptic field names (`F_NAME`, `CUST_ID`, `STATUS_CD`)
- Weird date formats (`YYYYMMDDHHMMSS`)
- Status codes instead of readable values (`A`, `I`, `P`)
- Flat data structures (no nesting)

### Step 2: Run the Comparison Demo

```bash
# Terminal 2
python demo/run_demo.py
```

This shows:
1. ❌ **Without ACL**: Legacy format pollutes entire application
2. ✅ **With ACL**: Clean domain model isolated from legacy

## What You'll See

### Without ACL (Bad)
```python
# Legacy pollution everywhere!
customer = get_customer("CUST000001")
name = f"{customer['F_NAME']} {customer['L_NAME']}"  # Ugly!
if customer['STATUS_CD'] == 'A':  # Cryptic code!
    # Parse weird date format
    date = datetime.strptime(customer['CREATE_DT'], "%Y%m%d%H%M%S")
```

### With ACL (Good)
```python
# Clean domain model!
customer: Customer = get_customer("CUST000001")
name = customer.full_name  # Clean!
if customer.is_active():  # Readable!
    # Proper datetime object
    date = customer.created_at
```

## Key Concepts

### 1. Domain Model (Your Clean Model)
```python
@dataclass
class Customer:
    id: str
    email: str
    full_name: str  # Combined, not split
    address: Address  # Nested object
    status: CustomerStatus  # Enum, not code
    created_at: datetime  # Proper type
```

### 2. Legacy Format (External System)
```python
{
    "CUST_ID": "CUST000001",
    "F_NAME": "John",
    "L_NAME": "Doe",
    "EMAIL_ADDR": "john@example.com",
    "ADDR_LN1": "123 Main St",
    "ADDR_CITY": "New York",
    "ADDR_ZIP": "10001",
    "STATUS_CD": "A",
    "CREATE_DT": "20240101120000"
}
```

### 3. Translator (ACL Core)
```python
class CustomerTranslator:
    def to_domain(self, legacy_data: dict) -> Customer:
        """Legacy → Clean"""
        # Map codes to enums
        status = {"A": CustomerStatus.ACTIVE}[legacy_data['STATUS_CD']]
        # Parse weird dates
        created = datetime.strptime(legacy_data['CREATE_DT'], "%Y%m%d%H%M%S")
        # Combine names
        full_name = f"{legacy_data['F_NAME']} {legacy_data['L_NAME']}"
        # Return clean object
        return Customer(...)
```

## File Structure

```
02-anti-corruption-layer/
├── README.md                   # Full documentation
├── QUICKSTART.md              # This file
├── requirements.txt           # Dependencies
│
├── without_pattern/           # ❌ Legacy pollution
│   └── main.py               # Legacy format everywhere
│
├── with_pattern/             # ✅ Clean with ACL
│   └── main.py               # Clean domain + translators
│
└── demo/                     # Interactive demo
    ├── mock_legacy_system.py # Mock legacy API
    └── run_demo.py           # Comparison demo
```

## Common Translations

| From (Legacy) | To (Domain) | How |
|---------------|-------------|-----|
| `F_NAME` + `L_NAME` | `full_name` | Combine strings |
| `STATUS_CD` = "A" | `status` = `ACTIVE` | Map to enum |
| `CREATE_DT` = "20240101120000" | `created_at` = `datetime` | Parse string |
| Flat fields | Nested objects | Group related fields |
| String numbers | Proper types | Convert & validate |

## Benefits Demonstrated

### 1. **Clean Domain Model**
Your code works with nice objects, not ugly dictionaries.

### 2. **No Code Duplication**
Translation logic in ONE place (ACL), not scattered everywhere.

### 3. **Easy to Test**
Mock the adapter, test business logic with clean objects.

### 4. **Gradual Migration**
Replace legacy system behind ACL without touching business logic.

### 5. **Team Independence**
Domain team works with clean model, integration team handles ACL.

## Real-World Use Cases

### Legacy Migration
```
Old Mainframe → ACL → Modern Microservices
```
Replace piece by piece without big bang rewrite.

### Third-Party Integration
```
Vendor API (ugly) → ACL → Your Clean Domain
```
Vendor changes don't break your entire app.

### Multi-System Integration
```
SAP     ↘
         → ACL → Clean Domain
Salesforce ↗
```
Different external models, one internal model.

## Next Steps

1. **Explore the code**: Check [without_pattern/main.py](./without_pattern/main.py) vs [with_pattern/main.py](./with_pattern/main.py)
2. **Read full docs**: [README.md](./README.md)
3. **Try modifying**: Add new fields, change translations
4. **Build your own**: Apply ACL to your legacy integration

## Common Issues

### Legacy System Not Running
```
❌ Connection refused
```
**Solution**: Start legacy system first: `python demo/mock_legacy_system.py`

### Port Already in Use
```
Address already in use (port 8081)
```
**Solution**: Kill process using port 8081 or change port

### Import Errors
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: `pip install -r requirements.txt`

## Learn More

- [Microsoft Azure ACL Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) - Eric Evans
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html) - Martin Fowler
