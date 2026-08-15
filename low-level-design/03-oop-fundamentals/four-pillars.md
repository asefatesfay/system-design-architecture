# The Four Pillars of OOP

The four fundamental principles of Object-Oriented Programming are the foundation of good software design. Mastering these is **critical** for LLD interviews.

## Overview

1. **Encapsulation** - Hide internal details, expose only what's necessary
2. **Abstraction** - Show only essential features, hide complexity
3. **Inheritance** - Reuse and extend existing code
4. **Polymorphism** - Same interface, different implementations

---

## 1. Encapsulation

### Definition
**Encapsulation** means bundling data (attributes) and methods that operate on that data within a single unit (class), and restricting direct access to some of the object's components.

### Why It Matters
- **Data Protection**: Prevent invalid states
- **Maintainability**: Change implementation without affecting users
- **Modularity**: Clear boundaries between components

### Multi-Language Implementation

<details open>
<summary><b>🐍 Python - BankAccount with Encapsulation</b></summary>

Python uses naming conventions for access control:
- `public`: No underscore (accessible everywhere)
- `_protected`: Single underscore (accessible but discouraged)
- `__private`: Double underscore (name mangling, harder to access)

```python
class BankAccount:
    def __init__(self, account_number, initial_balance):
        self.account_number = account_number  # Public
        self._balance = initial_balance        # Protected
        self.__transaction_history = []       # Private

    # Public method - part of the API
    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
            self.__add_transaction("deposit", amount)
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self._balance:
            self._balance -= amount
            self.__add_transaction("withdraw", amount)
            return True
        return False

    # Public getter - controlled access to private data
    def get_balance(self):
        return self._balance

    # Private method - implementation detail
    def __add_transaction(self, type, amount):
        self.__transaction_history.append({
            'type': type,
            'amount': amount
        })

    # Property - pythonic way to encapsulate
    @property
    def balance(self):
        """Read-only access to balance"""
        return self._balance

# Usage
account = BankAccount("123456", 1000)

# Good - using public interface
account.deposit(500)
print(account.get_balance())  # 1500
print(account.balance)         # 1500 (using property)

# Bad - direct access (but Python allows it)
account._balance = 1000000  # NOT RECOMMENDED!

# Very difficult to access
# account.__transaction_history  # AttributeError
```

</details>

<details>
<summary><b>🔷 Go - BankAccount with Encapsulation</b></summary>

Go uses capitalization for access control:
- **Uppercase** = Public (exported from package)
- **lowercase** = Private (package-level only)

```go
package main

import "fmt"

// BankAccount struct
type BankAccount struct {
	AccountNumber string      // Public (Uppercase)
	balance       float64     // Private (lowercase)
	transactionHistory []transaction
}

type transaction struct {
	txType string
	amount float64
}

// Constructor function (Go convention)
func NewBankAccount(accountNumber string, initialBalance float64) *BankAccount {
	return &BankAccount{
		AccountNumber:      accountNumber,
		balance:            initialBalance,
		transactionHistory: make([]transaction, 0),
	}
}

// Public method (Uppercase)
func (ba *BankAccount) Deposit(amount float64) bool {
	if amount > 0 {
		ba.balance += amount
		ba.addTransaction("deposit", amount)
		return true
	}
	return false
}

func (ba *BankAccount) Withdraw(amount float64) bool {
	if amount > 0 && amount <= ba.balance {
		ba.balance -= amount
		ba.addTransaction("withdraw", amount)
		return true
	}
	return false
}

// Public getter
func (ba *BankAccount) GetBalance() float64 {
	return ba.balance
}

// Private method (lowercase)
func (ba *BankAccount) addTransaction(txType string, amount float64) {
	ba.transactionHistory = append(ba.transactionHistory, transaction{
		txType: txType,
		amount: amount,
	})
}

func main() {
	account := NewBankAccount("123456", 1000)
	account.Deposit(500)
	fmt.Printf("Balance: $%.2f\n", account.GetBalance()) // 1500.00
	
	// account.balance = 10000 // ❌ Cannot access - private!
}
```

</details>

<details>
<summary><b>☕ Java - BankAccount with Encapsulation</b></summary>

Java uses explicit access modifiers:

```java
import java.util.ArrayList;
import java.util.List;

public class BankAccount {
    // Private fields - explicit keyword
    private String accountNumber;
    private double balance;
    private List<Transaction> transactionHistory;

    // Inner class
    private static class Transaction {
        String type;
        double amount;
        
        Transaction(String type, double amount) {
            this.type = type;
            this.amount = amount;
        }
    }

    // Constructor
    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
        this.transactionHistory = new ArrayList<>();
    }

    // Public method
    public boolean deposit(double amount) {
        if (amount > 0) {
            this.balance += amount;
            addTransaction("deposit", amount);
            return true;
        }
        return false;
    }

    public boolean withdraw(double amount) {
        if (amount > 0 && amount <= this.balance) {
            this.balance -= amount;
            addTransaction("withdraw", amount);
            return true;
        }
        return false;
    }

    // Public getter
    public double getBalance() {
        return this.balance;
    }

    public String getAccountNumber() {
        return this.accountNumber;
    }

    // Private method
    private void addTransaction(String type, double amount) {
        transactionHistory.add(new Transaction(type, amount));
    }

    public static void main(String[] args) {
        BankAccount account = new BankAccount("123456", 1000);
        account.deposit(500);
        System.out.printf("Balance: $%.2f%n", account.getBalance()); // $1500.00
        
        // account.balance = 10000; // ❌ Compilation error - private!
    }
}
```

</details>

<details>
<summary><b>💛 JavaScript - BankAccount with Encapsulation</b></summary>

JavaScript offers multiple approaches:

**Modern (ES2022+) with `#` private fields:**
```javascript
class BankAccount {
    // Private fields with #
    #balance;
    #transactionHistory;

    constructor(accountNumber, initialBalance) {
        this.accountNumber = accountNumber; // Public
        this.#balance = initialBalance;      // Private
        this.#transactionHistory = [];       // Private
    }

    deposit(amount) {
        if (amount > 0) {
            this.#balance += amount;
            this.#addTransaction('deposit', amount);
            return true;
        }
        return false;
    }

    withdraw(amount) {
        if (amount > 0 && amount <= this.#balance) {
            this.#balance -= amount;
            this.#addTransaction('withdraw', amount);
            return true;
        }
        return false;
    }

    getBalance() {
        return this.#balance;
    }

    // Getter property
    get balance() {
        return this.#balance;
    }

    // Private method
    #addTransaction(type, amount) {
        this.#transactionHistory.push({ type, amount });
    }
}

const account = new BankAccount('123456', 1000);
account.deposit(500);
console.log(account.getBalance()); // 1500
console.log(account.balance);      // 1500

// account.#balance = 10000; // ❌ SyntaxError - truly private!
```

**Alternative (Closure pattern for older JS):**
```javascript
function createBankAccount(accountNumber, initialBalance) {
    // Private variables (closure)
    let balance = initialBalance;
    let transactionHistory = [];

    function addTransaction(type, amount) {
        transactionHistory.push({ type, amount });
    }

    // Public API
    return {
        accountNumber,
        
        deposit(amount) {
            if (amount > 0) {
                balance += amount;
                addTransaction('deposit', amount);
                return true;
            }
            return false;
        },

        withdraw(amount) {
            if (amount > 0 && amount <= balance) {
                balance -= amount;
                addTransaction('withdraw', amount);
                return true;
            }
            return false;
        },

        getBalance() {
            return balance;
        }
    };
}

const account = createBankAccount('123456', 1000);
account.deposit(500);
console.log(account.getBalance()); // 1500
```

</details>

---

### Language Comparison

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Private** | `__field` | `lowercase` | `private field` | `#field` (ES2022+) |
| **Public** | `field` | `Uppercase` | `public field` | `field` |
| **Protected** | `_field` | N/A | `protected field` | Convention only |
| **Enforcement** | Runtime (weak) | Compile-time (package) | Compile-time (strict) | Runtime (`#`) |
| **Best Practice** | Use `@property` | Constructor functions | Getters/setters | Use `#` for truly private |


### Benefits of Encapsulation

```python
# WITHOUT Encapsulation - BAD
class User:
    def __init__(self, email):
        self.email = email  # Anyone can set invalid email!

user = User("john@example.com")
user.email = "invalid-email"  # No validation!


# WITH Encapsulation - GOOD
class User:
    def __init__(self, email):
        self.__email = None
        self.set_email(email)  # Validation in setter

    def set_email(self, email):
        if "@" in email and "." in email:
            self.__email = email
        else:
            raise ValueError("Invalid email format")

    def get_email(self):
        return self.__email

    # Pythonic way using property
    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if "@" in value and "." in value:
            self.__email = value
        else:
            raise ValueError("Invalid email format")

# Usage
user = User("john@example.com")
# user.email = "invalid"  # Raises ValueError
user.email = "new@example.com"  # Validates first
```

---

## 2. Abstraction

### Definition
**Abstraction** means hiding complex implementation details and showing only the essential features of an object.

### Why It Matters
- **Simplicity**: Users don't need to know how it works internally
- **Flexibility**: Implementation can change without affecting users
- **Reduced Complexity**: Focus on what an object does, not how

### Key Difference from Encapsulation
- **Encapsulation**: About data hiding and access control
- **Abstraction**: About hiding complexity and showing only relevant details

### Multi-Language Implementation

<details open>
<summary><b>🐍 Python - PaymentProcessor with Abstraction</b></summary>

```python
from abc import ABC, abstractmethod

# Abstract class - defines WHAT to do, not HOW
class PaymentProcessor(ABC):
    """Abstract class for payment processing"""

    @abstractmethod
    def process_payment(self, amount):
        """Process payment - must be implemented by subclasses"""
        pass

    @abstractmethod
    def refund(self, transaction_id, amount):
        """Refund payment - must be implemented by subclasses"""
        pass

# Concrete implementations - define HOW to do it
class CreditCardProcessor(PaymentProcessor):
    def process_payment(self, amount):
        # Complex credit card processing logic hidden
        print(f"Processing ${amount} via Credit Card")
        # Validate card, contact payment gateway, etc.
        return True

    def refund(self, transaction_id, amount):
        print(f"Refunding ${amount} to credit card")
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount):
        # Complex PayPal API logic hidden
        print(f"Processing ${amount} via PayPal")
        # OAuth, API calls, etc.
        return True

    def refund(self, transaction_id, amount):
        print(f"Refunding ${amount} via PayPal")
        return True

# High-level code doesn't care about implementation details
class OrderService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def checkout(self, amount):
        # Abstraction: We know WHAT it does, not HOW
        return self.payment_processor.process_payment(amount)

# Usage - interchangeable implementations
order1 = OrderService(CreditCardProcessor())
order1.checkout(100)

order2 = OrderService(PayPalProcessor())
order2.checkout(200)
```

</details>

<details>
<summary><b>🔷 Go - PaymentProcessor with Abstraction</b></summary>

Go uses interfaces for abstraction (implicit implementation):

```go
package main

import "fmt"

// Interface defines WHAT (abstraction)
type PaymentProcessor interface {
	ProcessPayment(amount float64) bool
	Refund(transactionID string, amount float64) bool
}

// Concrete implementation - CreditCard
type CreditCardProcessor struct{}

func (cc CreditCardProcessor) ProcessPayment(amount float64) bool {
	fmt.Printf("Processing $%.2f via Credit Card\n", amount)
	// Complex credit card logic hidden
	return true
}

func (cc CreditCardProcessor) Refund(transactionID string, amount float64) bool {
	fmt.Printf("Refunding $%.2f to credit card\n", amount)
	return true
}

// Concrete implementation - PayPal
type PayPalProcessor struct{}

func (pp PayPalProcessor) ProcessPayment(amount float64) bool {
	fmt.Printf("Processing $%.2f via PayPal\n", amount)
	// Complex PayPal API logic hidden
	return true
}

func (pp PayPalProcessor) Refund(transactionID string, amount float64) bool {
	fmt.Printf("Refunding $%.2f via PayPal\n", amount)
	return true
}

// OrderService depends on abstraction
type OrderService struct {
	paymentProcessor PaymentProcessor
}

func NewOrderService(processor PaymentProcessor) *OrderService {
	return &OrderService{paymentProcessor: processor}
}

func (os *OrderService) Checkout(amount float64) bool {
	// Abstraction: We know WHAT, not HOW
	return os.paymentProcessor.ProcessPayment(amount)
}

func main() {
	// Interchangeable implementations
	order1 := NewOrderService(CreditCardProcessor{})
	order1.Checkout(100)

	order2 := NewOrderService(PayPalProcessor{})
	order2.Checkout(200)
}
```

**Key Go concept**: Interfaces are satisfied implicitly - no `implements` keyword needed!

</details>

<details>
<summary><b>☕ Java - PaymentProcessor with Abstraction</b></summary>

```java
// Interface defines WHAT (abstraction)
interface PaymentProcessor {
    boolean processPayment(double amount);
    boolean refund(String transactionId, double amount);
}

// Concrete implementation - CreditCard
class CreditCardProcessor implements PaymentProcessor {
    @Override
    public boolean processPayment(double amount) {
        System.out.printf("Processing $%.2f via Credit Card%n", amount);
        // Complex credit card logic hidden
        return true;
    }

    @Override
    public boolean refund(String transactionId, double amount) {
        System.out.printf("Refunding $%.2f to credit card%n", amount);
        return true;
    }
}

// Concrete implementation - PayPal
class PayPalProcessor implements PaymentProcessor {
    @Override
    public boolean processPayment(double amount) {
        System.out.printf("Processing $%.2f via PayPal%n", amount);
        // Complex PayPal API logic hidden
        return true;
    }

    @Override
    public boolean refund(String transactionId, double amount) {
        System.out.printf("Refunding $%.2f via PayPal%n", amount);
        return true;
    }
}

// OrderService depends on abstraction
class OrderService {
    private PaymentProcessor paymentProcessor;

    public OrderService(PaymentProcessor paymentProcessor) {
        this.paymentProcessor = paymentProcessor;
    }

    public boolean checkout(double amount) {
        // Abstraction: We know WHAT, not HOW
        return paymentProcessor.processPayment(amount);
    }
}

public class AbstractionDemo {
    public static void main(String[] args) {
        // Interchangeable implementations
        OrderService order1 = new OrderService(new CreditCardProcessor());
        order1.checkout(100);

        OrderService order2 = new OrderService(new PayPalProcessor());
        order2.checkout(200);
    }
}
```

**Alternative: Abstract class** (when you need some default implementation):
```java
abstract class AbstractPaymentProcessor {
    // Concrete method with default behavior
    public void logTransaction(double amount) {
        System.out.println("Transaction logged: $" + amount);
    }

    // Abstract method - must be implemented
    public abstract boolean processPayment(double amount);
}
```

</details>

<details>
<summary><b>💛 JavaScript - PaymentProcessor with Abstraction</b></summary>

**Modern approach (ES6 classes):**
```javascript
// Abstract class (by convention)
class PaymentProcessor {
    processPayment(amount) {
        throw new Error('processPayment must be implemented');
    }

    refund(transactionId, amount) {
        throw new Error('refund must be implemented');
    }
}

// Concrete implementation - CreditCard
class CreditCardProcessor extends PaymentProcessor {
    processPayment(amount) {
        console.log(`Processing $${amount} via Credit Card`);
        // Complex credit card logic hidden
        return true;
    }

    refund(transactionId, amount) {
        console.log(`Refunding $${amount} to credit card`);
        return true;
    }
}

// Concrete implementation - PayPal
class PayPalProcessor extends PaymentProcessor {
    processPayment(amount) {
        console.log(`Processing $${amount} via PayPal`);
        // Complex PayPal API logic hidden
        return true;
    }

    refund(transactionId, amount) {
        console.log(`Refunding $${amount} via PayPal`);
        return true;
    }
}

// OrderService depends on abstraction
class OrderService {
    constructor(paymentProcessor) {
        this.paymentProcessor = paymentProcessor;
    }

    checkout(amount) {
        // Abstraction: We know WHAT, not HOW
        return this.paymentProcessor.processPayment(amount);
    }
}

// Usage - interchangeable implementations
const order1 = new OrderService(new CreditCardProcessor());
order1.checkout(100);

const order2 = new OrderService(new PayPalProcessor());
order2.checkout(200);
```

**TypeScript alternative** (true interfaces):
```typescript
// Interface (TypeScript)
interface PaymentProcessor {
    processPayment(amount: number): boolean;
    refund(transactionId: string, amount: number): boolean;
}

class CreditCardProcessor implements PaymentProcessor {
    processPayment(amount: number): boolean {
        console.log(`Processing $${amount} via Credit Card`);
        return true;
    }

    refund(transactionId: string, amount: number): boolean {
        console.log(`Refunding $${amount} to credit card`);
        return true;
    }
}
```

</details>

---

### Language Comparison - Abstraction

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Abstraction** | `ABC` + `@abstractmethod` | Interfaces (implicit) | `interface` or `abstract class` | Convention or TypeScript |
| **Enforcement** | Runtime error if not implemented | Compile-time (implicit) | Compile-time (explicit) | Runtime or TS compile-time |
| **Multiple** | Multiple inheritance from ABC | Multiple interfaces (implicit) | Multiple interfaces | Multiple base classes |
| **When to use** | Define contract for subclasses | Define behavior contracts | Formal contracts | TypeScript for type safety |

---

## 3. Inheritance

### Definition
**Inheritance** allows a class to inherit attributes and methods from another class, promoting code reuse and establishing relationships.

### Why It Matters
- **Code Reuse**: Don't repeat yourself
- **Extensibility**: Add new features without modifying existing code
- **Hierarchy**: Model real-world relationships

### Multi-Language Implementation

<details open>
<summary><b>🐍 Python - Animal Hierarchy with Inheritance</b></summary>

```python
# Base class (Parent/Superclass)
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        print(f"{self.name} is eating")

    def sleep(self):
        print(f"{self.name} is sleeping")

    def make_sound(self):
        print("Some generic sound")

# Derived class (Child/Subclass)
class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # Call parent constructor
        self.breed = breed

    # Override parent method
    def make_sound(self):
        print(f"{self.name} says: Woof!")

    # Add new method
    def fetch(self):
        print(f"{self.name} is fetching the ball")

class Cat(Animal):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color

    # Override parent method
    def make_sound(self):
        print(f"{self.name} says: Meow!")

    # Add new method
    def scratch(self):
        print(f"{self.name} is scratching the furniture")

# Usage
dog = Dog("Buddy", 3, "Golden Retriever")
cat = Cat("Whiskers", 2, "Black")

# Inherited methods
dog.eat()    # Buddy is eating
cat.sleep()  # Whiskers is sleeping

# Overridden methods
dog.make_sound()  # Buddy says: Woof!
cat.make_sound()  # Whiskers says: Meow!

# New methods
dog.fetch()      # Buddy is fetching the ball
cat.scratch()    # Whiskers is scratching the furniture
```

</details>

<details>
<summary><b>🔷 Go - Animal Hierarchy with Embedding</b></summary>

Go doesn't have traditional inheritance, but uses **composition via embedding**:

```go
package main

import "fmt"

// Base "class" - Animal
type Animal struct {
	Name string
	Age  int
}

// Methods on Animal
func (a Animal) Eat() {
	fmt.Printf("%s is eating\n", a.Name)
}

func (a Animal) Sleep() {
	fmt.Printf("%s is sleeping\n", a.Name)
}

func (a Animal) MakeSound() {
	fmt.Println("Some generic sound")
}

// Dog "inherits" from Animal via embedding
type Dog struct {
	Animal // Embedded struct (composition)
	Breed  string
}

// Override MakeSound for Dog
func (d Dog) MakeSound() {
	fmt.Printf("%s says: Woof!\n", d.Name)
}

// New method specific to Dog
func (d Dog) Fetch() {
	fmt.Printf("%s is fetching the ball\n", d.Name)
}

// Cat "inherits" from Animal via embedding
type Cat struct {
	Animal // Embedded struct
	Color  string
}

// Override MakeSound for Cat
func (c Cat) MakeSound() {
	fmt.Printf("%s says: Meow!\n", c.Name)
}

// New method specific to Cat
func (c Cat) Scratch() {
	fmt.Printf("%s is scratching the furniture\n", c.Name)
}

func main() {
	// Create instances
	dog := Dog{
		Animal: Animal{Name: "Buddy", Age: 3},
		Breed:  "Golden Retriever",
	}

	cat := Cat{
		Animal: Animal{Name: "Whiskers", Age: 2},
		Color:  "Black",
	}

	// Inherited methods (promoted from embedded Animal)
	dog.Eat()   // Buddy is eating
	cat.Sleep() // Whiskers is sleeping

	// Overridden methods
	dog.MakeSound() // Buddy says: Woof!
	cat.MakeSound() // Whiskers says: Meow!

	// New methods
	dog.Fetch()   // Buddy is fetching the ball
	cat.Scratch() // Whiskers is scratching the furniture
}
```

**Key Go Concept:**
- Go uses **composition over inheritance**
- Embedded structs promote their fields/methods automatically
- No `super()` - access embedded struct directly: `d.Animal.MakeSound()`

</details>

<details>
<summary><b>☕ Java - Animal Hierarchy with Inheritance</b></summary>

```java
// Base class (Parent/Superclass)
class Animal {
    protected String name;
    protected int age;

    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public void eat() {
        System.out.println(name + " is eating");
    }

    public void sleep() {
        System.out.println(name + " is sleeping");
    }

    public void makeSound() {
        System.out.println("Some generic sound");
    }
}

// Derived class (Child/Subclass)
class Dog extends Animal {
    private String breed;

    public Dog(String name, int age, String breed) {
        super(name, age);  // Call parent constructor
        this.breed = breed;
    }

    // Override parent method
    @Override
    public void makeSound() {
        System.out.println(name + " says: Woof!");
    }

    // Add new method
    public void fetch() {
        System.out.println(name + " is fetching the ball");
    }

    public String getBreed() {
        return breed;
    }
}

class Cat extends Animal {
    private String color;

    public Cat(String name, int age, String color) {
        super(name, age);
        this.color = color;
    }

    // Override parent method
    @Override
    public void makeSound() {
        System.out.println(name + " says: Meow!");
    }

    // Add new method
    public void scratch() {
        System.out.println(name + " is scratching the furniture");
    }

    public String getColor() {
        return color;
    }
}

public class InheritanceDemo {
    public static void main(String[] args) {
        Dog dog = new Dog("Buddy", 3, "Golden Retriever");
        Cat cat = new Cat("Whiskers", 2, "Black");

        // Inherited methods
        dog.eat();    // Buddy is eating
        cat.sleep();  // Whiskers is sleeping

        // Overridden methods
        dog.makeSound();  // Buddy says: Woof!
        cat.makeSound();  // Whiskers says: Meow!

        // New methods
        dog.fetch();      // Buddy is fetching the ball
        cat.scratch();    // Whiskers is scratching the furniture
    }
}
```

**Key Java Concepts:**
- `extends` keyword for inheritance
- `super()` to call parent constructor (must be first line)
- `@Override` annotation (optional but recommended)
- `protected` allows access in subclasses
- Java only supports **single inheritance** (one parent class)

</details>

<details>
<summary><b>💛 JavaScript - Animal Hierarchy with Inheritance</b></summary>

**Modern ES6 Classes:**
```javascript
// Base class (Parent/Superclass)
class Animal {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    eat() {
        console.log(`${this.name} is eating`);
    }

    sleep() {
        console.log(`${this.name} is sleeping`);
    }

    makeSound() {
        console.log("Some generic sound");
    }
}

// Derived class (Child/Subclass)
class Dog extends Animal {
    constructor(name, age, breed) {
        super(name, age);  // Call parent constructor
        this.breed = breed;
    }

    // Override parent method
    makeSound() {
        console.log(`${this.name} says: Woof!`);
    }

    // Add new method
    fetch() {
        console.log(`${this.name} is fetching the ball`);
    }
}

class Cat extends Animal {
    constructor(name, age, color) {
        super(name, age);
        this.color = color;
    }

    // Override parent method
    makeSound() {
        console.log(`${this.name} says: Meow!`);
    }

    // Add new method
    scratch() {
        console.log(`${this.name} is scratching the furniture`);
    }
}

// Usage
const dog = new Dog("Buddy", 3, "Golden Retriever");
const cat = new Cat("Whiskers", 2, "Black");

// Inherited methods
dog.eat();    // Buddy is eating
cat.sleep();  // Whiskers is sleeping

// Overridden methods
dog.makeSound();  // Buddy says: Woof!
cat.makeSound();  // Whiskers says: Meow!

// New methods
dog.fetch();      // Buddy is fetching the ball
cat.scratch();    // Whiskers is scratching the furniture
```

**Prototype-based Inheritance (Pre-ES6):**
```javascript
// Constructor function
function Animal(name, age) {
    this.name = name;
    this.age = age;
}

Animal.prototype.eat = function() {
    console.log(this.name + " is eating");
};

Animal.prototype.makeSound = function() {
    console.log("Some generic sound");
};

// Inheritance via prototype chain
function Dog(name, age, breed) {
    Animal.call(this, name, age);  // Call parent constructor
    this.breed = breed;
}

Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

Dog.prototype.makeSound = function() {
    console.log(this.name + " says: Woof!");
};

Dog.prototype.fetch = function() {
    console.log(this.name + " is fetching the ball");
};
```

</details>

---

### Language Comparison - Inheritance

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Syntax** | `class Dog(Animal)` | Embedding: `Animal` inside struct | `class Dog extends Animal` | `class Dog extends Animal` |
| **Constructor** | `super().__init__()` | Initialize embedded struct | `super(name, age)` | `super(name, age)` |
| **Multiple Inheritance** | ✅ Yes (can inherit from multiple classes) | ❌ No (use multiple interfaces) | ❌ No (single parent, multiple interfaces) | ❌ No (single parent) |
| **Method Override** | Just redefine method | Redefine method (shadows embedded) | `@Override` annotation | Just redefine method |
| **Access Parent** | `super().method()` | `d.Animal.Method()` | `super.method()` | `super.method()` |
| **Philosophy** | Inheritance is common | Composition over inheritance | Inheritance is fundamental | Prototypal (classes are sugar) |

---

---

## 4. Polymorphism

### Definition
**Polymorphism** means "many forms." It allows objects of different classes to be treated as objects of a common base class, with each implementing behavior in their own way.

### Why It Matters
- **Flexibility**: Write code that works with multiple types
- **Extensibility**: Add new types without changing existing code
- **Clean Code**: Same interface, different implementations

### Types of Polymorphism


### Multi-Language Implementation

#### Method Overriding (Runtime Polymorphism)

<details open>
<summary><b>🐍 Python - Shape Polymorphism</b></summary>

```python
class Shape:
    def area(self):
        pass

    def perimeter(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def area(self):
        # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5

    def perimeter(self):
        return self.a + self.b + self.c

# Polymorphism in action
def print_shape_info(shape: Shape):
    """Works with ANY shape - polymorphism!"""
    print(f"Area: {shape.area()}")
    print(f"Perimeter: {shape.perimeter()}")

# All shapes can be used interchangeably
shapes = [
    Rectangle(5, 10),
    Circle(7),
    Triangle(3, 4, 5)
]

for shape in shapes:
    print_shape_info(shape)  # Same code, different behavior!
```

**Duck Typing (Python-specific):**
```python
# No inheritance needed in Python!
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

class Robot:
    def speak(self):
        return "Beep boop!"

# Works with any object that has speak() method
def make_it_speak(thing):
    print(thing.speak())

# All work even though they're unrelated
make_it_speak(Dog())    # Woof!
make_it_speak(Cat())    # Meow!
make_it_speak(Robot())  # Beep boop!
```

</details>

<details>
<summary><b>🔷 Go - Shape Polymorphism with Interfaces</b></summary>

```go
package main

import (
	"fmt"
	"math"
)

// Interface defines the contract (polymorphism)
type Shape interface {
	Area() float64
	Perimeter() float64
}

// Rectangle implementation
type Rectangle struct {
	Width  float64
	Height float64
}

func (r Rectangle) Area() float64 {
	return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
	return 2 * (r.Width + r.Height)
}

// Circle implementation
type Circle struct {
	Radius float64
}

func (c Circle) Area() float64 {
	return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
	return 2 * math.Pi * c.Radius
}

// Triangle implementation
type Triangle struct {
	A, B, C float64
}

func (t Triangle) Area() float64 {
	// Heron's formula
	s := (t.A + t.B + t.C) / 2
	return math.Sqrt(s * (s - t.A) * (s - t.B) * (s - t.C))
}

func (t Triangle) Perimeter() float64 {
	return t.A + t.B + t.C
}

// Polymorphic function - works with ANY shape
func PrintShapeInfo(shape Shape) {
	fmt.Printf("Area: %.2f\n", shape.Area())
	fmt.Printf("Perimeter: %.2f\n", shape.Perimeter())
}

func main() {
	// All shapes can be used interchangeably
	shapes := []Shape{
		Rectangle{Width: 5, Height: 10},
		Circle{Radius: 7},
		Triangle{A: 3, B: 4, C: 5},
	}

	for _, shape := range shapes {
		PrintShapeInfo(shape) // Same code, different behavior!
	}
}
```

**Key Go Concept:**
- Interfaces are satisfied **implicitly** - no `implements` keyword
- Any type with matching methods automatically satisfies the interface
- This is Go's primary mechanism for polymorphism

</details>

<details>
<summary><b>☕ Java - Shape Polymorphism with Interfaces</b></summary>

```java
// Interface defines the contract
interface Shape {
    double area();
    double perimeter();
}

// Rectangle implementation
class Rectangle implements Shape {
    private double width;
    private double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public double area() {
        return width * height;
    }

    @Override
    public double perimeter() {
        return 2 * (width + height);
    }
}

// Circle implementation
class Circle implements Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double area() {
        return Math.PI * radius * radius;
    }

    @Override
    public double perimeter() {
        return 2 * Math.PI * radius;
    }
}

// Triangle implementation
class Triangle implements Shape {
    private double a, b, c;

    public Triangle(double a, double b, double c) {
        this.a = a;
        this.b = b;
        this.c = c;
    }

    @Override
    public double area() {
        // Heron's formula
        double s = (a + b + c) / 2;
        return Math.sqrt(s * (s - a) * (s - b) * (s - c));
    }

    @Override
    public double perimeter() {
        return a + b + c;
    }
}

// Polymorphic function - works with ANY shape
class ShapeDemo {
    public static void printShapeInfo(Shape shape) {
        System.out.printf("Area: %.2f%n", shape.area());
        System.out.printf("Perimeter: %.2f%n", shape.perimeter());
    }

    public static void main(String[] args) {
        // All shapes can be used interchangeably
        Shape[] shapes = {
            new Rectangle(5, 10),
            new Circle(7),
            new Triangle(3, 4, 5)
        };

        for (Shape shape : shapes) {
            printShapeInfo(shape); // Same code, different behavior!
        }
    }
}
```

**Alternative: Using Abstract Class**
```java
abstract class AbstractShape {
    // Concrete method
    public void display() {
        System.out.println("This is a shape");
    }

    // Abstract methods
    public abstract double area();
    public abstract double perimeter();
}

class Rectangle extends AbstractShape {
    private double width, height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public double area() {
        return width * height;
    }

    @Override
    public double perimeter() {
        return 2 * (width + height);
    }
}
```

</details>

<details>
<summary><b>💛 JavaScript - Shape Polymorphism</b></summary>

**Modern ES6 Classes:**
```javascript
// Base "interface" (by convention)
class Shape {
    area() {
        throw new Error('area() must be implemented');
    }

    perimeter() {
        throw new Error('perimeter() must be implemented');
    }
}

// Rectangle implementation
class Rectangle extends Shape {
    constructor(width, height) {
        super();
        this.width = width;
        this.height = height;
    }

    area() {
        return this.width * this.height;
    }

    perimeter() {
        return 2 * (this.width + this.height);
    }
}

// Circle implementation
class Circle extends Shape {
    constructor(radius) {
        super();
        this.radius = radius;
    }

    area() {
        return Math.PI * this.radius ** 2;
    }

    perimeter() {
        return 2 * Math.PI * this.radius;
    }
}

// Triangle implementation
class Triangle extends Shape {
    constructor(a, b, c) {
        super();
        this.a = a;
        this.b = b;
        this.c = c;
    }

    area() {
        // Heron's formula
        const s = (this.a + this.b + this.c) / 2;
        return Math.sqrt(s * (s - this.a) * (s - this.b) * (s - this.c));
    }

    perimeter() {
        return this.a + this.b + this.c;
    }
}

// Polymorphic function - works with ANY shape
function printShapeInfo(shape) {
    console.log(`Area: ${shape.area().toFixed(2)}`);
    console.log(`Perimeter: ${shape.perimeter().toFixed(2)}`);
}

// All shapes can be used interchangeably
const shapes = [
    new Rectangle(5, 10),
    new Circle(7),
    new Triangle(3, 4, 5)
];

shapes.forEach(shape => {
    printShapeInfo(shape); // Same code, different behavior!
});
```

**TypeScript with Interfaces (type-safe):**
```typescript
// Real interface (TypeScript)
interface Shape {
    area(): number;
    perimeter(): number;
}

class Rectangle implements Shape {
    constructor(
        private width: number,
        private height: number
    ) {}

    area(): number {
        return this.width * this.height;
    }

    perimeter(): number {
        return 2 * (this.width + this.height);
    }
}

class Circle implements Shape {
    constructor(private radius: number) {}

    area(): number {
        return Math.PI * this.radius ** 2;
    }

    perimeter(): number {
        return 2 * Math.PI * this.radius;
    }
}

// Type-safe polymorphism
function printShapeInfo(shape: Shape): void {
    console.log(`Area: ${shape.area().toFixed(2)}`);
    console.log(`Perimeter: ${shape.perimeter().toFixed(2)}`);
}
```

**Duck Typing (JavaScript style):**
```javascript
// No inheritance needed - just matching methods
const dog = {
    speak() { return "Woof!"; }
};

const cat = {
    speak() { return "Meow!"; }
};

const robot = {
    speak() { return "Beep boop!"; }
};

// Works with any object that has speak()
function makeItSpeak(thing) {
    console.log(thing.speak());
}

makeItSpeak(dog);    // Woof!
makeItSpeak(cat);    // Meow!
makeItSpeak(robot);  // Beep boop!
```

</details>

---

### Language Comparison - Polymorphism

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Mechanism** | Inheritance + Duck Typing | Interfaces (implicit) | Interfaces + Inheritance | Inheritance + Duck Typing |
| **Type Checking** | Runtime (duck typing) | Compile-time (interfaces) | Compile-time (explicit) | Runtime (or TS compile-time) |
| **Flexibility** | Very flexible (duck typing) | Explicit interfaces | Strict interfaces | Very flexible (dynamic) |
| **Operator Overload** | ✅ Yes (`__add__`, etc.) | ❌ No | ❌ No (limited) | ❌ No |
| **Best for** | Rapid prototyping | Clear contracts | Type safety | Quick prototyping |

---


---

## How They Work Together

All four pillars work together in real applications:

```python
from abc import ABC, abstractmethod

# ABSTRACTION: Define interface
class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount):
        pass

# ENCAPSULATION: Hide implementation details
class CreditCard(PaymentMethod):
    def __init__(self, card_number, cvv):
        self.__card_number = card_number  # Private
        self.__cvv = cvv                  # Private

    def process(self, amount):
        # Complex processing hidden
        if self.__validate_card():
            print(f"Charged ${amount} to card ****{self.__card_number[-4:]}")
            return True
        return False

    def __validate_card(self):  # Private method
        # Validation logic
        return True

# INHERITANCE: Reuse and extend
class DebitCard(CreditCard):
    def __init__(self, card_number, cvv, bank_account):
        super().__init__(card_number, cvv)
        self.bank_account = bank_account

    def process(self, amount):
        if self.__check_balance(amount):
            return super().process(amount)
        print("Insufficient funds")
        return False

    def __check_balance(self, amount):
        # Check account balance
        return True

# POLYMORPHISM: Same interface, different implementations
def process_payment(payment_method: PaymentMethod, amount):
    """Works with ANY payment method"""
    return payment_method.process(amount)

# Works with any PaymentMethod!
process_payment(CreditCard("1234567890123456", "123"), 100)
process_payment(DebitCard("9876543210987654", "456", "ACC001"), 50)
```

## Interview Tips

1. **Know the definitions**: Be able to explain each pillar clearly
2. **Use examples**: Always provide code examples when explaining
3. **Relate to SOLID**: These pillars connect to SOLID principles
4. **Identify in problems**: Point out where you're using each pillar
5. **Trade-offs**: Discuss when NOT to use inheritance (favor composition)

## Key Takeaways

1. **Encapsulation** = Data hiding + controlled access
2. **Abstraction** = Hide complexity, show essentials
3. **Inheritance** = "IS-A" relationship, code reuse
4. **Polymorphism** = Same interface, different implementations

---

**Next**: Learn about [Interfaces and Abstract Classes →](./interfaces-abstract-classes.md)
