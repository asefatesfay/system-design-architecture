# SOLID Principles - Clear & Memorable

SOLID is an acronym for five design principles that make software more maintainable, flexible, and scalable. These principles are **CRITICAL** for LLD interviews!

## 📝 Memory Aid: The SOLID Story

Think of building a house:

- **S**ingle Responsibility: Each room has ONE purpose (bedroom = sleep, kitchen = cook)
- **O**pen/Closed: Add new rooms (extend) without breaking existing walls (modify)
- **L**iskov Substitution: Any chair can be used for sitting (subclass = parent)
- **I**nterface Segregation: Light switches only have power (not water, not gas)
- **D**ependency Inversion: Plug any device into standard outlets (depend on interface, not specific device)

---

## Quick Reference Table

| Letter | Principle | Simple Rule | Real Problem It Solves |
|--------|-----------|-------------|------------------------|
| **S** | Single Responsibility | One class = One job | Code becomes spaghetti when one class does everything |
| **O** | Open/Closed | Add features without changing existing code | Every new feature breaks old code |
| **L** | Liskov Substitution | Subclass must work like parent | Crashes when using subclass where parent expected |
| **I** | Interface Segregation | Don't force unused methods | Classes forced to implement things they don't need |
| **D** | Dependency Inversion | Depend on contracts, not concrete classes | Can't swap implementations (hard to test/change) |

---

## S - Single Responsibility Principle (SRP)

### 💡 In Plain English
**"Do one thing and do it well."** A class should have only ONE reason to change.

### 🎯 Memorable Rule
**One class = One job.** If you describe what your class does and use the word "AND", it's doing too much.

### 🔧 Real Engineering Problems It Solves

**Problem 1: The God Class**
```
Symptom: One 3000-line class that does everything
Result: Every feature change risks breaking unrelated functionality
Example: UserManager that handles validation, database, email, logging, reports
```

**Problem 2: Testing Nightmare**
```
Symptom: Can't test one feature without setting up 10 dependencies
Result: Tests are slow, brittle, hard to maintain
Example: To test email validation, you need a database connection
```

**Problem 3: Merge Conflicts**
```
Symptom: Multiple developers always editing the same file
Result: Constant merge conflicts, blocked work
Example: 5 devs working on User.java, stepping on each other's toes
```

### ❌ Bad Example: Multiple Responsibilities

```python
class UserManager:
    """This class has 5 reasons to change - BAD!"""

    def __init__(self, name, email):
        self.name = name
        self.email = email

    # Reason 1: Email validation logic changes
    def validate_email(self):
        return "@" in self.email

    # Reason 2: Database schema changes
    def save_to_database(self):
        print(f"INSERT INTO users VALUES ('{self.name}', '{self.email}')")

    # Reason 3: Email service provider changes
    def send_welcome_email(self):
        print(f"Sending email to {self.email}")

    # Reason 4: Reporting requirements change
    def generate_report(self):
        return f"User Report: {self.name}"

    # Reason 5: Password rules change
    def validate_password(self, password):
        return len(password) >= 8

# PROBLEM: Changing email validation forces recompilation of database code!
# PROBLEM: Can't test email without database setup!
# PROBLEM: Multiple devs editing same file = merge hell!
```

### ✅ Good Example: Single Responsibility

```python
class User:
    """ONLY represents user data - ONE responsibility"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserValidator:
    """ONLY validates - ONE responsibility"""
    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email

    @staticmethod
    def validate_password(password):
        return len(password) >= 8

class UserRepository:
    """ONLY handles database - ONE responsibility"""
    def save(self, user):
        print(f"Saving {user.name} to database")

    def find_by_email(self, email):
        pass

class EmailService:
    """ONLY sends emails - ONE responsibility"""
    def send_welcome_email(self, user):
        print(f"Email sent to {user.email}")

class UserReportGenerator:
    """ONLY generates reports - ONE responsibility"""
    def generate(self, user):
        return f"Report for {user.name}"

# NOW: Each class has ONE reason to change
# NOW: Can test validation without database
# NOW: Different devs work on different files
```

### 🎓 How to Apply SRP

**Ask yourself:** "What does this class do?"
- If answer has "AND" → Split it!
- If answer is vague → Too much responsibility!
- If answer is simple → Good!

**Bad answers:**
- "Handles users AND sends emails AND generates reports" ❌
- "Does everything related to users" ❌

**Good answers:**
- "Validates user input" ✅
- "Stores users in database" ✅

---

## O - Open/Closed Principle (OCP)

### 💡 In Plain English
**"Add new features without changing existing code."** Extend behavior by adding new code, not editing old code.

### 🎯 Memorable Rule
**Open for extension (add), Closed for modification (don't edit).**

Think of a power strip: you add new devices without rewiring the strip itself.

### 🔧 Real Engineering Problems It Solves

**Problem 1: Every Feature Breaks Old Code**
```
Symptom: Adding new payment method breaks existing checkout flow
Result: Regression bugs, unstable releases
Example: Adding PayPal requires editing CreditCardPayment code
```

**Problem 2: Ripple Effect Changes**
```
Symptom: One small change requires editing 15 files
Result: High risk, slow development
Example: New customer type requires if/else in 10 different places
```

**Problem 3: Fear of Refactoring**
```
Symptom: Team scared to touch old code
Result: Technical debt accumulates, new features slow down
Example: "Don't touch PaymentProcessor - it's fragile!"
```

### ❌ Bad Example: Modification Required

```python
class PaymentProcessor:
    def process_payment(self, payment_type, amount):
        # Problem: Adding new payment type requires modifying this method!
        if payment_type == "credit_card":
            return self.process_credit_card(amount)
        elif payment_type == "paypal":
            return self.process_paypal(amount)
        elif payment_type == "bitcoin":  # New requirement!
            return self.process_bitcoin(amount)  # Had to modify existing code
        elif payment_type == "apple_pay":  # Another new requirement!
            return self.process_apple_pay(amount)  # Modified again!
        # Every new payment type = modify this method = risk breaking others!

# PROBLEM: Adding Bitcoin broke existing PayPal integration
# PROBLEM: Can't add new payment without touching this file
# PROBLEM: if/else grows infinitely
```

### ✅ Good Example: Extension Without Modification

```python
from abc import ABC, abstractmethod

# Define contract - CLOSED for modification
class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

# OPEN for extension - just add new classes
class CreditCardPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via Credit Card"

class PayPalPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via PayPal"

# New payment method? Just add a class - NO modification needed!
class BitcoinPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via Bitcoin"

class ApplePayPayment(PaymentMethod):
    def process(self, amount):
        return f"Processing ${amount} via Apple Pay"

class PaymentProcessor:
    def __init__(self, payment_method: PaymentMethod):
        self.payment_method = payment_method

    def process(self, amount):
        return self.payment_method.process(amount)

# NOW: Add Bitcoin without touching existing code!
# NOW: CreditCard code stays untouched when adding PayPal!
# NOW: No risk of breaking old features!
```

### 🎓 How to Apply OCP

**Use Strategy Pattern or Inheritance:**
1. Identify code that changes frequently (payment methods, discounts, notifications)
2. Extract to abstract interface
3. New features = new classes, not editing old ones

**Red flags:**
- Long if/else chains ❌
- Switch statements on types ❌
- Comments like "// Add new types here" ❌

---

## L - Liskov Substitution Principle (LSP)

### 💡 In Plain English
**"Subclass should work anywhere parent works."** Don't break the promise the parent class made.

### 🎯 Memorable Rule
**If it walks like a duck and quacks like a duck, but needs batteries – it violates LSP.**

Subclass should strengthen, not weaken, parent behavior.

### 🔧 Real Engineering Problems It Solves

**Problem 1: Runtime Crashes**
```
Symptom: Code works with Parent but crashes with Child
Result: Unexpected exceptions in production
Example: Penguin.fly() throws exception but Bird.fly() works
```

**Problem 2: Type Checking Hell**
```
Symptom: Code littered with isinstance() checks
Result: Defeats purpose of polymorphism
Example: if isinstance(bird, Penguin): don't fly
```

**Problem 3: Contract Violations**
```
Symptom: Subclass changes expectations (preconditions/postconditions)
Result: Subtle bugs, broken assumptions
Example: Square.setWidth() also changes height (breaks Rectangle contract)
```

### ❌ Bad Example: Violates LSP

```python
class Bird:
    def fly(self):
        return "Flying high!"

class Sparrow(Bird):
    def fly(self):
        return "Sparrow flying!"  # Works fine

class Penguin(Bird):
    def fly(self):
        # PROBLEM: Penguins can't fly - breaks parent's promise!
        raise Exception("Penguins can't fly!")

def make_bird_fly(bird: Bird):
    """Expects ALL birds to fly"""
    print(bird.fly())

make_bird_fly(Sparrow())  # ✓ Works
make_bird_fly(Penguin())  # ✗ CRASHES! Violates LSP!

# PROBLEM: Can't use Penguin where Bird expected
# PROBLEM: Need to check: if not isinstance(bird, Penguin)
# PROBLEM: Polymorphism broken!
```

### ✅ Good Example: Follows LSP

```python
from abc import ABC, abstractmethod

# Don't promise what you can't deliver!
class Bird(ABC):
    @abstractmethod
    def move(self):
        """All birds move somehow"""
        pass

class FlyingBird(Bird):
    def move(self):
        return self.fly()

    def fly(self):
        return "Flying!"

class Sparrow(FlyingBird):
    def fly(self):
        return "Sparrow flying!"

class FlightlessBird(Bird):
    def move(self):
        return self.walk()

    def walk(self):
        return "Walking!"

class Penguin(FlightlessBird):
    def walk(self):
        return "Penguin waddling!"

def make_bird_move(bird: Bird):
    """Works with ANY bird"""
    print(bird.move())

make_bird_move(Sparrow())  # ✓ Sparrow flying!
make_bird_move(Penguin())  # ✓ Penguin waddling! - No crash!

# NOW: Both work correctly
# NOW: No type checking needed
# NOW: Polymorphism works!
```

### 🎓 How to Apply LSP

**Test with substitution:**
```python
def test_with_parent(obj: Parent):
    obj.method()  # Should work

test_with_parent(Parent())  # Works?
test_with_parent(Child())   # Must also work!
```

**Red flags:**
- Subclass throws new exceptions ❌
- Subclass has weaker behavior ❌
- Need type checks before calling ❌

---

## I - Interface Segregation Principle (ISP)

### 💡 In Plain English
**"Don't force classes to implement methods they don't need."** Many small interfaces > One large interface.

### 🎯 Memorable Rule
**No fat interfaces!** A TV remote shouldn't have microwave buttons.

### 🔧 Real Engineering Problems It Solves

**Problem 1: Bloated Implementations**
```
Symptom: Classes with 50% empty/throw NotImplemented methods
Result: Confusing, error-prone code
Example: SimplePrinter forced to have scan(), fax(), staple() methods
```

**Problem 2: Unnecessary Dependencies**
```
Symptom: Change one method, recompile entire system
Result: Slow builds, tight coupling
Example: Adding fax() forces SimplePrinter to update (even though it doesn't fax)
```

**Problem 3: Interface Pollution**
```
Symptom: Interfaces keep growing with new methods
Result: All implementations must update
Example: IVehicle gains fly() - now Car must implement fly()!
```

### ❌ Bad Example: Fat Interface

```python
from abc import ABC, abstractmethod

class Worker(ABC):
    """Fat interface - forces everyone to implement everything"""

    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass

    @abstractmethod
    def get_salary(self):
        pass

class Human(Worker):
    def work(self): return "Working"
    def eat(self): return "Eating"
    def sleep(self): return "Sleeping"
    def get_salary(self): return 5000

class Robot(Worker):
    def work(self): return "Working"

    # PROBLEM: Forced to implement methods that make no sense!
    def eat(self): pass  # Robots don't eat!
    def sleep(self): pass  # Robots don't sleep!
    def get_salary(self): pass  # Robots don't get paid!

# PROBLEM: Robot has 3 useless methods
# PROBLEM: What should these methods return? raise? None?
# PROBLEM: Fat interface forces inappropriate implementations
```

### ✅ Good Example: Segregated Interfaces

```python
from abc import ABC, abstractmethod

# Small, focused interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Payable(ABC):
    @abstractmethod
    def get_salary(self):
        pass

# Each class picks what it needs
class Human(Workable, Eatable, Sleepable, Payable):
    def work(self): return "Working"
    def eat(self): return "Eating"
    def sleep(self): return "Sleeping"
    def get_salary(self): return 5000

class Robot(Workable):  # Only what it needs!
    def work(self): return "Working 24/7"

class Intern(Workable, Eatable, Sleepable):  # No salary yet!
    def work(self): return "Learning"
    def eat(self): return "Free pizza!"
    def sleep(self): return "Power naps"

# NOW: Each class only implements what makes sense
# NOW: Robot has no dummy methods
# NOW: Easy to add Intern (different combination)
```

### 🎓 How to Apply ISP

**Split large interfaces:**
```python
# Before (BAD)
class IAnimal:
    def walk(), swim(), fly()  # Fat!

# After (GOOD)
class IWalkable: walk()
class ISwimmable: swim()
class IFlyable: fly()

class Duck(IWalkable, ISwimmable, IFlyable)  # Uses all
class Fish(ISwimmable)  # Uses only what it needs
```

**Red flags:**
- Interface with 10+ methods ❌
- Classes with many pass/NotImplemented ❌
- Method names like doEverything() ❌

---

## D - Dependency Inversion Principle (DIP)

### 💡 In Plain English
**"Depend on contracts, not concrete implementations."** High-level code shouldn't know about low-level details.

### 🎯 Memorable Rule
**Plugin architecture.** Your laptop has USB ports (abstraction), not specific device connectors.

**Simple version:** Don't new up concrete classes inside your class - inject them instead!

### 🔧 Real Engineering Problems It Solves

**Problem 1: Hard to Test**
```
Symptom: Can't unit test without real database/API
Result: Slow tests, flaky tests
Example: UserService creates new MySQLDatabase() internally
```

**Problem 2: Tight Coupling**
```
Symptom: Can't swap implementations without rewriting code
Result: Locked into vendor, technology
Example: Code hardcoded to MySQL - can't switch to PostgreSQL
```

**Problem 3: Impossible to Mock**
```
Symptom: Testing requires spinning up entire infrastructure
Result: Tests take 10 minutes to run
Example: Service directly calls external payment API
```

### ❌ Bad Example: High-Level Depends on Low-Level

```python
# Low-level module (detail)
class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL...")

    def query(self, sql):
        print(f"MySQL: {sql}")
        return [{"id": 1, "name": "Alice"}]

# High-level module depends on concrete class
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # PROBLEM: Hard dependency!

    def get_user(self, user_id):
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# PROBLEM: Can't use PostgreSQL without rewriting UserService
# PROBLEM: Can't test without real MySQL database
# PROBLEM: Tightly coupled to MySQL implementation details
# PROBLEM: Can't mock database for tests

# To test, you need:
user_service = UserService()  # Creates real MySQL connection!
# What if MySQL is down? Test fails!
# What if MySQL is slow? Test is slow!
```

### ✅ Good Example: Both Depend on Abstraction

```python
from abc import ABC, abstractmethod

# Abstraction (contract) - HIGH and LOW both depend on this
class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def query(self, sql):
        pass

# Low-level implementations
class MySQLDatabase(Database):
    def connect(self):
        print("MySQL connected")

    def query(self, sql):
        return [{"id": 1, "name": "Alice"}]

class PostgreSQLDatabase(Database):
    def connect(self):
        print("PostgreSQL connected")

    def query(self, sql):
        return [{"id": 1, "name": "Alice"}]

class MockDatabase(Database):
    """For testing - no real database needed!"""
    def connect(self):
        pass  # No real connection

    def query(self, sql):
        return [{"id": 999, "name": "Test User"}]  # Fake data

# High-level module depends on abstraction
class UserService:
    def __init__(self, database: Database):  # Dependency injection!
        self.db = database

    def get_user(self, user_id):
        self.db.connect()
        return self.db.query(f"SELECT * FROM users WHERE id={user_id}")

# NOW: Easy to swap implementations
service1 = UserService(MySQLDatabase())      # Production
service2 = UserService(PostgreSQLDatabase()) # Migrate to Postgres
service3 = UserService(MockDatabase())       # Testing!

# NOW: Tests run instantly with MockDatabase
# NOW: Can switch DB without changing UserService
# NOW: Low coupling, high flexibility
```

### 🎓 How to Apply DIP

**Three-step recipe:**
1. **Define interface** (abstraction)
2. **Implement interface** (low-level details)
3. **Inject dependency** (high-level receives interface)

**Before (Bad):**
```python
class EmailService:
    def __init__(self):
        self.smtp = SMTPClient("smtp.gmail.com")  # Hard-coded!
```

**After (Good):**
```python
class EmailService:
    def __init__(self, email_provider: EmailProvider):  # Injected!
        self.provider = email_provider
```

**Red flags:**
- new SomeClass() inside constructor ❌
- Import concrete classes ❌
- Hard-coded connection strings ❌

---

## 🎯 Interview Cheat Sheet

### Quick Memory Trick: "SOLID House"

```
S - Single room, single purpose (bedroom for sleep ONLY)
O - Open doors (add rooms), closed walls (don't break existing)
L - Light switch works in any room (substitute child for parent)
I - Specific controls (light switch doesn't control AC)
D - Standard outlets (plug any device, not wired for specific one)
```

### What to Say in Interviews

**When designing:**
- "I'll apply Single Responsibility by separating concerns..."
- "This follows Open/Closed - we can add new types without modifying..."
- "To ensure Liskov Substitution, subclasses must honor the contract..."
- "Following Interface Segregation, I'll create small, focused interfaces..."
- "Using Dependency Inversion, I'll depend on abstractions..."

**When asked "What's wrong with this code?":**
1. Check: Does one class do too much? → SRP violation
2. Check: Does adding new feature require editing old code? → OCP violation
3. Check: Does subclass break parent's promise? → LSP violation
4. Check: Are there empty/throw methods? → ISP violation
5. Check: Are there new SomeClass() in constructor? → DIP violation

---

## Common Interview Questions

**Q: "Explain the difference between OCP and DIP?"**
- **OCP**: About adding features (extend without modify)
- **DIP**: About dependencies (depend on abstractions)
- **Together**: Use DIP to achieve OCP (inject strategies to extend behavior)

**Q: "When would you violate SOLID?"**
- Simple scripts - over-engineering wastes time
- Prototypes - premature abstraction is bad
- Performance-critical code - sometimes coupling is faster
- **BUT**: Production code should follow SOLID!

**Q: "How do SOLID principles relate to design patterns?"**
- Strategy Pattern → OCP + DIP
- Factory Pattern → OCP + DIP
- Decorator Pattern → OCP + LSP
- Adapter Pattern → LSP + ISP

---

## Real-World Application

### Example: E-commerce Checkout

```python
from abc import ABC, abstractmethod

# I - Interface Segregation: Small interfaces
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount): pass

class RefundProcessor(ABC):
    @abstractmethod
    def process_refund(self, transaction_id): pass

# S - Single Responsibility: One job per class
class CreditCardPayment(PaymentProcessor, RefundProcessor):
    def process_payment(self, amount):
        return f"Charged ${amount} to credit card"

    def process_refund(self, transaction_id):
        return f"Refunded transaction {transaction_id}"

class GiftCardPayment(PaymentProcessor):  # No refunds!
    def process_payment(self, amount):
        return f"Redeemed ${amount} from gift card"

# D - Dependency Inversion: Depend on abstraction
class CheckoutService:
    def __init__(self, payment: PaymentProcessor):  # DIP
        self.payment = payment

    def checkout(self, cart, amount):
        # Validate cart
        # Calculate total
        result = self.payment.process_payment(amount)
        return result

# O - Open/Closed: Add new payment without modifying CheckoutService
class CryptoPayment(PaymentProcessor):
    def process_payment(self, amount):
        return f"Paid ${amount} with Bitcoin"

# Usage
checkout1 = CheckoutService(CreditCardPayment())
checkout2 = CheckoutService(CryptoPayment())  # Easy to add!
```

---

**Next**: Learn about [Design Patterns →](../06-design-patterns/)

**Related**:
- [OOP Fundamentals](../03-oop-fundamentals/) - Foundation
- [Design Patterns](../06-design-patterns/) - Apply SOLID
- [Practice Problems](../07-practice-problems/) - Use SOLID
