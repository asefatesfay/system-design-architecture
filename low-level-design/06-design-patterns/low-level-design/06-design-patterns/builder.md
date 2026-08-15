# Builder Pattern

Separate the construction of complex objects from their representation. Construct objects step-by-step.

## Why Builder?

**Problems it solves:**
- Too many constructor parameters
- Optional parameters confusion
- Telescoping constructors anti-pattern
- Need different representations of same object

```python
# WITHOUT Builder - messy!
pizza = Pizza("large", True, False, True, False, True, "thin", "tomato")
#              ^size   ^cheese ^olives ^bacon ^peppers ^mushrooms ^crust ^sauce
# What does what? Hard to read!

# WITH Builder - clear!
pizza = (PizzaBuilder()
    .size("large")
    .add_cheese()
    .add_bacon()
    .add_mushrooms()
    .crust_type("thin")
    .sauce("tomato")
    .build())
```

---

## 1. Basic Builder Pattern

```python
class Pizza:
    """Product - the complex object being built"""

    def __init__(self):
        self.size = None
        self.cheese = False
        self.pepperoni = False
        self.bacon = False
        self.olives = False
        self.mushrooms = False
        self.crust_type = "regular"
        self.sauce = "tomato"

    def __str__(self):
        toppings = []
        if self.cheese: toppings.append("cheese")
        if self.pepperoni: toppings.append("pepperoni")
        if self.bacon: toppings.append("bacon")
        if self.olives: toppings.append("olives")
        if self.mushrooms: toppings.append("mushrooms")

        return f"{self.size} pizza with {', '.join(toppings)} on {self.crust_type} crust with {self.sauce} sauce"


class PizzaBuilder:
    """Builder - constructs Pizza step by step"""

    def __init__(self):
        self.pizza = Pizza()

    def size(self, size: str):
        """Set pizza size"""
        self.pizza.size = size
        return self  # Return self for method chaining!

    def add_cheese(self):
        self.pizza.cheese = True
        return self

    def add_pepperoni(self):
        self.pizza.pepperoni = True
        return self

    def add_bacon(self):
        self.pizza.bacon = True
        return self

    def add_olives(self):
        self.pizza.olives = True
        return self

    def add_mushrooms(self):
        self.pizza.mushrooms = True
        return self

    def crust_type(self, crust: str):
        self.pizza.crust_type = crust
        return self

    def sauce(self, sauce: str):
        self.pizza.sauce = sauce
        return self

    def build(self) -> Pizza:
        """Return the built pizza"""
        # Optional: validate before building
        if not self.pizza.size:
            raise ValueError("Pizza size is required")
        return self.pizza


# Usage - fluent interface
pizza = (PizzaBuilder()
    .size("large")
    .add_cheese()
    .add_pepperoni()
    .add_mushrooms()
    .crust_type("thin")
    .build())

print(pizza)
# large pizza with cheese, pepperoni, mushrooms on thin crust with tomato sauce
```

---

## 2. Builder with Director

**Director** knows the steps to build specific configurations.

```python
class Computer:
    """Product"""

    def __init__(self):
        self.cpu = None
        self.ram = None
        self.storage = None
        self.gpu = None
        self.os = None

    def __str__(self):
        parts = [
            f"CPU: {self.cpu}",
            f"RAM: {self.ram}GB",
            f"Storage: {self.storage}",
            f"GPU: {self.gpu or 'Integrated'}",
            f"OS: {self.os}"
        ]
        return "\n".join(parts)


class ComputerBuilder:
    """Builder"""

    def __init__(self):
        self.computer = Computer()

    def set_cpu(self, cpu: str):
        self.computer.cpu = cpu
        return self

    def set_ram(self, ram: int):
        self.computer.ram = ram
        return self

    def set_storage(self, storage: str):
        self.computer.storage = storage
        return self

    def set_gpu(self, gpu: str):
        self.computer.gpu = gpu
        return self

    def set_os(self, os: str):
        self.computer.os = os
        return self

    def build(self) -> Computer:
        return self.computer


class ComputerDirector:
    """Director - knows how to build specific configurations"""

    @staticmethod
    def build_gaming_pc(builder: ComputerBuilder) -> Computer:
        """High-end gaming configuration"""
        return (builder
            .set_cpu("Intel i9-13900K")
            .set_ram(32)
            .set_storage("2TB NVMe SSD")
            .set_gpu("NVIDIA RTX 4090")
            .set_os("Windows 11")
            .build())

    @staticmethod
    def build_office_pc(builder: ComputerBuilder) -> Computer:
        """Budget office configuration"""
        return (builder
            .set_cpu("Intel i5-12400")
            .set_ram(16)
            .set_storage("512GB SSD")
            .set_os("Windows 11 Pro")
            .build())

    @staticmethod
    def build_developer_mac(builder: ComputerBuilder) -> Computer:
        """Developer configuration"""
        return (builder
            .set_cpu("Apple M2 Pro")
            .set_ram(32)
            .set_storage("1TB SSD")
            .set_os("macOS Ventura")
            .build())


# Usage
director = ComputerDirector()

# Predefined configurations
gaming_pc = director.build_gaming_pc(ComputerBuilder())
print("Gaming PC:")
print(gaming_pc)
print()

office_pc = director.build_office_pc(ComputerBuilder())
print("Office PC:")
print(office_pc)
print()

# Custom configuration
custom_pc = (ComputerBuilder()
    .set_cpu("AMD Ryzen 9 7950X")
    .set_ram(64)
    .set_storage("4TB NVMe SSD")
    .set_gpu("AMD Radeon RX 7900 XTX")
    .set_os("Ubuntu 22.04")
    .build())
print("Custom PC:")
print(custom_pc)
```

---

## 3. Immutable Builder (Pythonic)

Use `dataclass` with builder for immutable objects.

```python
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)  # Immutable
class Request:
    """Immutable HTTP request"""

    method: str
    url: str
    headers: dict
    params: dict
    body: Optional[str] = None
    timeout: int = 30


class RequestBuilder:
    """Builder for immutable Request"""

    def __init__(self, method: str, url: str):
        self._method = method
        self._url = url
        self._headers = {}
        self._params = {}
        self._body = None
        self._timeout = 30

    def header(self, key: str, value: str):
        """Add header"""
        self._headers[key] = value
        return self

    def headers(self, headers: dict):
        """Add multiple headers"""
        self._headers.update(headers)
        return self

    def param(self, key: str, value: str):
        """Add query parameter"""
        self._params[key] = value
        return self

    def body(self, body: str):
        """Set request body"""
        self._body = body
        return self

    def timeout(self, seconds: int):
        """Set timeout"""
        self._timeout = seconds
        return self

    def build(self) -> Request:
        """Build immutable Request"""
        return Request(
            method=self._method,
            url=self._url,
            headers=self._headers.copy(),
            params=self._params.copy(),
            body=self._body,
            timeout=self._timeout
        )


# Usage
request = (RequestBuilder("POST", "https://api.example.com/users")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .param("filter", "active")
    .body('{"name": "Alice", "age": 30}')
    .timeout(60)
    .build())

print(f"Method: {request.method}")
print(f"URL: {request.url}")
print(f"Headers: {request.headers}")
print(f"Body: {request.body}")

# request.method = "GET"  # ❌ FrozenInstanceError - immutable!
```

---

## 4. Real-World Example: SQL Query Builder

```python
from typing import List, Optional


class SQLQuery:
    """Product - SQL query"""

    def __init__(self):
        self.select_fields: List[str] = []
        self.from_table: Optional[str] = None
        self.where_clauses: List[str] = []
        self.order_by: Optional[str] = None
        self.limit_value: Optional[int] = None
        self.join_clauses: List[str] = []

    def to_sql(self) -> str:
        """Generate SQL string"""
        if not self.from_table:
            raise ValueError("FROM clause is required")

        # SELECT
        fields = ", ".join(self.select_fields) if self.select_fields else "*"
        sql = f"SELECT {fields}"

        # FROM
        sql += f" FROM {self.from_table}"

        # JOIN
        for join in self.join_clauses:
            sql += f" {join}"

        # WHERE
        if self.where_clauses:
            sql += " WHERE " + " AND ".join(self.where_clauses)

        # ORDER BY
        if self.order_by:
            sql += f" ORDER BY {self.order_by}"

        # LIMIT
        if self.limit_value:
            sql += f" LIMIT {self.limit_value}"

        return sql


class QueryBuilder:
    """Builder for SQL queries"""

    def __init__(self):
        self.query = SQLQuery()

    def select(self, *fields: str):
        """SELECT fields"""
        self.query.select_fields.extend(fields)
        return self

    def from_table(self, table: str):
        """FROM table"""
        self.query.from_table = table
        return self

    def where(self, condition: str):
        """WHERE condition"""
        self.query.where_clauses.append(condition)
        return self

    def join(self, table: str, condition: str):
        """INNER JOIN"""
        self.query.join_clauses.append(f"INNER JOIN {table} ON {condition}")
        return self

    def left_join(self, table: str, condition: str):
        """LEFT JOIN"""
        self.query.join_clauses.append(f"LEFT JOIN {table} ON {condition}")
        return self

    def order_by(self, field: str, direction: str = "ASC"):
        """ORDER BY"""
        self.query.order_by = f"{field} {direction}"
        return self

    def limit(self, count: int):
        """LIMIT"""
        self.query.limit_value = count
        return self

    def build(self) -> str:
        """Build SQL string"""
        return self.query.to_sql()


# Usage
query = (QueryBuilder()
    .select("users.name", "users.email", "COUNT(orders.id) as order_count")
    .from_table("users")
    .left_join("orders", "users.id = orders.user_id")
    .where("users.active = 1")
    .where("users.created_at > '2023-01-01'")
    .order_by("order_count", "DESC")
    .limit(10)
    .build())

print(query)
# SELECT users.name, users.email, COUNT(orders.id) as order_count
# FROM users
# LEFT JOIN orders ON users.id = orders.user_id
# WHERE users.active = 1 AND users.created_at > '2023-01-01'
# ORDER BY order_count DESC
# LIMIT 10
```

---

## 5. Builder with Validation

```python
from typing import List, Optional
from datetime import datetime


class EmailValidationError(Exception):
    pass


class Email:
    """Product - validated email"""

    def __init__(
        self,
        to: List[str],
        subject: str,
        body: str,
        from_addr: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ):
        self.to = to
        self.subject = subject
        self.body = body
        self.from_addr = from_addr
        self.cc = cc or []
        self.bcc = bcc or []
        self.attachments = attachments or []
        self.sent_at = None

    def __str__(self):
        return f"Email from {self.from_addr} to {', '.join(self.to)}: {self.subject}"


class EmailBuilder:
    """Builder with validation"""

    def __init__(self):
        self._to: List[str] = []
        self._subject: Optional[str] = None
        self._body: Optional[str] = None
        self._from: Optional[str] = None
        self._cc: List[str] = []
        self._bcc: List[str] = []
        self._attachments: List[str] = []

    def _validate_email(self, email: str) -> bool:
        """Simple email validation"""
        return "@" in email and "." in email.split("@")[1]

    def from_address(self, email: str):
        """Set sender (with validation)"""
        if not self._validate_email(email):
            raise EmailValidationError(f"Invalid email: {email}")
        self._from = email
        return self

    def to(self, *emails: str):
        """Add recipients"""
        for email in emails:
            if not self._validate_email(email):
                raise EmailValidationError(f"Invalid email: {email}")
            self._to.append(email)
        return self

    def cc(self, *emails: str):
        """Add CC recipients"""
        for email in emails:
            if not self._validate_email(email):
                raise EmailValidationError(f"Invalid email: {email}")
            self._cc.append(email)
        return self

    def bcc(self, *emails: str):
        """Add BCC recipients"""
        for email in emails:
            if not self._validate_email(email):
                raise EmailValidationError(f"Invalid email: {email}")
            self._bcc.append(email)
        return self

    def subject(self, subject: str):
        """Set subject"""
        if not subject or len(subject) > 200:
            raise EmailValidationError("Subject must be 1-200 characters")
        self._subject = subject
        return self

    def body(self, body: str):
        """Set body"""
        if not body:
            raise EmailValidationError("Body cannot be empty")
        self._body = body
        return self

    def attach(self, *files: str):
        """Add attachments"""
        self._attachments.extend(files)
        return self

    def build(self) -> Email:
        """Build with validation"""
        # Validate required fields
        if not self._from:
            raise EmailValidationError("From address is required")
        if not self._to:
            raise EmailValidationError("At least one recipient is required")
        if not self._subject:
            raise EmailValidationError("Subject is required")
        if not self._body:
            raise EmailValidationError("Body is required")

        return Email(
            to=self._to.copy(),
            subject=self._subject,
            body=self._body,
            from_addr=self._from,
            cc=self._cc.copy(),
            bcc=self._bcc.copy(),
            attachments=self._attachments.copy()
        )


# Usage
try:
    email = (EmailBuilder()
        .from_address("sender@example.com")
        .to("recipient1@example.com", "recipient2@example.com")
        .cc("manager@example.com")
        .subject("Project Update")
        .body("Here's the latest update on the project...")
        .attach("report.pdf", "data.xlsx")
        .build())

    print(email)
    print(f"CC: {', '.join(email.cc)}")
    print(f"Attachments: {', '.join(email.attachments)}")

except EmailValidationError as e:
    print(f"Validation error: {e}")
```

---

## 6. Method Chaining vs Separate Steps

```python
class ReportBuilder:
    def __init__(self):
        self.title = None
        self.data = []
        self.format = "pdf"

    def set_title(self, title: str):
        self.title = title
        return self

    def add_data(self, data):
        self.data.append(data)
        return self

    def set_format(self, format: str):
        self.format = format
        return self

    def build(self):
        return {
            'title': self.title,
            'data': self.data,
            'format': self.format
        }


# STYLE 1: Method chaining (fluent interface)
report = (ReportBuilder()
    .set_title("Sales Report")
    .add_data({'month': 'Jan', 'sales': 1000})
    .add_data({'month': 'Feb', 'sales': 1200})
    .set_format("excel")
    .build())

# STYLE 2: Separate steps (when conditional logic needed)
builder = ReportBuilder()
builder.set_title("Sales Report")

# Conditional data
if include_january:
    builder.add_data({'month': 'Jan', 'sales': 1000})
if include_february:
    builder.add_data({'month': 'Feb', 'sales': 1200})

builder.set_format("excel")
report = builder.build()
```

---

## 7. When to Use Builder Pattern

### ✅ Use When:

1. **Many constructor parameters** (>5)
   ```python
   # BAD - telescoping constructor
   User(name, email, phone, address, city, state, zip, country, age, gender)

   # GOOD - builder
   UserBuilder().name("Alice").email("alice@example.com").build()
   ```

2. **Optional parameters**
   ```python
   # Builder makes optional parameters clear
   pizza = PizzaBuilder().size("large").add_cheese().build()
   ```

3. **Immutable objects**
   ```python
   # Set all properties before building
   request = RequestBuilder("GET", url).header("Auth", token).build()
   # request is now immutable
   ```

4. **Complex construction steps**
   ```python
   # Multi-step validation and configuration
   db = DatabaseBuilder().host("localhost").port(5432).validate().build()
   ```

### ❌ Don't Use When:

1. **Few parameters** - just use constructor
2. **Simple objects** - over-engineering
3. **No optional parameters** - unnecessary complexity

---

## 8. Builder vs Factory

| Feature | Builder | Factory |
|---------|---------|---------|
| **Purpose** | Configure complex object | Create object type |
| **Steps** | Multiple steps | Single call |
| **Flexibility** | High - many options | Low - predefined types |
| **Usage** | `builder.step1().step2().build()` | `factory.create(type)` |

```python
# Factory - creates different types
animal = AnimalFactory.create('dog')  # Returns Dog

# Builder - configures single type
pizza = PizzaBuilder().size("large").add_cheese().build()  # Returns Pizza
```

---

## 9. Interview Tips

### Common Questions

**Q: "What problem does Builder solve?"**
- Avoids telescoping constructors
- Makes optional parameters clear
- Separates construction from representation

**Q: "Builder vs Constructor?"**
- Builder: Many optional parameters, step-by-step
- Constructor: Few required parameters, simple

**Q: "Implement a builder with validation"**
```python
def build(self):
    if not self._required_field:
        raise ValueError("Required field missing")
    return Product(self._required_field, self._optional_field)
```

### Best Practices

✅ Return `self` for method chaining
✅ Validate in `build()` method
✅ Make built object immutable
✅ Use descriptive method names
✅ Consider Director for common configurations

### Red Flags

❌ Builder for simple objects
❌ Not returning `self` in builder methods
❌ Mutable built objects (without reason)
❌ No validation before building

---

## Quick Reference

```python
# Basic pattern
class ProductBuilder:
    def __init__(self):
        self._product = Product()

    def set_property(self, value):
        self._product.property = value
        return self  # Enable chaining!

    def build(self) -> Product:
        # Validate
        if not self._product.required_field:
            raise ValueError("Missing required field")
        return self._product

# Usage
product = (ProductBuilder()
    .set_property("value")
    .build())
```

---

**Related Patterns:**
- [Factory Pattern](./factory.md) - Object creation
- [Prototype Pattern](./prototype.md) - Clone objects
- [Abstract Factory](./factory.md) - Create families

**Back to:** [Design Patterns](./README.md)
