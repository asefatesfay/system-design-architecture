# The Four Pillars of OOP - Go

The four fundamental principles of Object-Oriented Programming in Go with Go-specific explanations.

## Overview

1. **Encapsulation** - Control visibility with lowercase/Uppercase naming
2. **Abstraction** - Define contracts with interfaces (implicit implementation)
3. **Inheritance** - Achieve reuse through struct embedding and composition
4. **Polymorphism** - Interface-based polymorphism (no inheritance needed)

---

## 1. Encapsulation 🔒

### Definition
**Encapsulation** in Go means controlling access to struct fields and methods using naming conventions and packages.

### Go-Specific Access Control

Go uses **package-based visibility** with simple naming rules:
- `Uppercase`: Exported (public) - visible outside package
- `lowercase`: Unexported (private) - only visible within package

```go
package bank

import (
    "errors"
    "sync"
)

// BankAccount - exported struct
type BankAccount struct {
    AccountNumber string  // Exported field
    balance       float64 // Unexported field (private)
    transactions  []transaction
}

// transaction - unexported struct (private)
type transaction struct {
    txType string
    amount float64
}

// NewBankAccount - constructor function (exported)
func NewBankAccount(accountNumber string, initialBalance float64) *BankAccount {
    return &BankAccount{
        AccountNumber: accountNumber,
        balance:       initialBalance,
        transactions:  make([]transaction, 0),
    }
}

// Deposit - exported method (public API)
func (ba *BankAccount) Deposit(amount float64) error {
    if amount <= 0 {
        return errors.New("amount must be positive")
    }
    ba.balance += amount
    ba.addTransaction("deposit", amount)
    return nil
}

// Withdraw - exported method (public API)
func (ba *BankAccount) Withdraw(amount float64) error {
    if amount <= 0 {
        return errors.New("amount must be positive")
    }
    if amount > ba.balance {
        return errors.New("insufficient funds")
    }
    ba.balance -= amount
    ba.addTransaction("withdraw", amount)
    return nil
}

// Balance - exported getter method
func (ba *BankAccount) Balance() float64 {
    return ba.balance
}

// addTransaction - unexported helper (private)
func (ba *BankAccount) addTransaction(txType string, amount float64) {
    ba.transactions = append(ba.transactions, transaction{
        txType: txType,
        amount: amount,
    })
}

// calculateInterest - unexported method (private)
func (ba *BankAccount) calculateInterest() float64 {
    return ba.balance * 0.03
}
```

### Go Concurrency: Mutexes and Channels

Go provides powerful concurrency primitives built into the language:

```go
package bank

import "sync"

// ThreadSafeBankAccount - safe for concurrent use
type ThreadSafeBankAccount struct {
    accountNumber string
    balance       float64
    mu            sync.Mutex  // Mutual exclusion lock
}

func NewThreadSafeBankAccount(accountNumber string, initialBalance float64) *ThreadSafeBankAccount {
    return &ThreadSafeBankAccount{
        accountNumber: accountNumber,
        balance:       initialBalance,
    }
}

func (ba *ThreadSafeBankAccount) Deposit(amount float64) error {
    ba.mu.Lock()         // Acquire lock
    defer ba.mu.Unlock() // Release lock when function returns

    if amount <= 0 {
        return errors.New("amount must be positive")
    }
    ba.balance += amount
    return nil
}

func (ba *ThreadSafeBankAccount) Withdraw(amount float64) error {
    ba.mu.Lock()
    defer ba.mu.Unlock()

    if amount <= 0 {
        return errors.New("amount must be positive")
    }
    if amount > ba.balance {
        return errors.New("insufficient funds")
    }
    ba.balance -= amount
    return nil
}

func (ba *ThreadSafeBankAccount) Balance() float64 {
    ba.mu.Lock()
    defer ba.mu.Unlock()
    return ba.balance
}
```

### Go Concurrency Patterns

**1. Using Channels for Communication:**
```go
type BankAccountWithChannel struct {
    accountNumber string
    balance       float64
    operations    chan operation
}

type operation struct {
    opType   string
    amount   float64
    response chan error
}

func NewBankAccountWithChannel(accountNumber string, initialBalance float64) *BankAccountWithChannel {
    ba := &BankAccountWithChannel{
        accountNumber: accountNumber,
        balance:       initialBalance,
        operations:    make(chan operation),
    }
    go ba.processOperations()
    return ba
}

// Single goroutine processes all operations - no locks needed!
func (ba *BankAccountWithChannel) processOperations() {
    for op := range ba.operations {
        var err error
        switch op.opType {
        case "deposit":
            if op.amount > 0 {
                ba.balance += op.amount
            } else {
                err = errors.New("amount must be positive")
            }
        case "withdraw":
            if op.amount > 0 && op.amount <= ba.balance {
                ba.balance -= op.amount
            } else {
                err = errors.New("invalid withdrawal")
            }
        }
        op.response <- err
    }
}

func (ba *BankAccountWithChannel) Deposit(amount float64) error {
    response := make(chan error)
    ba.operations <- operation{
        opType:   "deposit",
        amount:   amount,
        response: response,
    }
    return <-response
}
```

**2. RWMutex for Read-Heavy Workloads:**
```go
import "sync"

type ReadHeavyAccount struct {
    accountNumber string
    balance       float64
    mu            sync.RWMutex  // Read-Write mutex
}

func (ba *ReadHeavyAccount) Balance() float64 {
    ba.mu.RLock()         // Multiple readers can acquire this
    defer ba.mu.RUnlock()
    return ba.balance
}

func (ba *ReadHeavyAccount) Deposit(amount float64) error {
    ba.mu.Lock()          // Exclusive write lock
    defer ba.mu.Unlock()
    ba.balance += amount
    return nil
}
```

---

## 2. Abstraction 🎭

### Definition
**Abstraction** in Go means defining interfaces that specify behavior contracts. Go uses **implicit interface implementation**.

### Go's Implicit Interfaces

```go
package payment

import "fmt"

// PaymentProcessor - interface definition
type PaymentProcessor interface {
    ProcessPayment(amount float64) (string, error)
    Refund(transactionID string) error
}

// CreditCardProcessor - implements interface implicitly
type CreditCardProcessor struct {
    CardNumber string
    CVV        string
}

// ProcessPayment - no "implements" keyword needed!
func (cc *CreditCardProcessor) ProcessPayment(amount float64) (string, error) {
    if amount <= 0 {
        return "", fmt.Errorf("invalid amount")
    }
    fmt.Printf("Processing $%.2f via credit card\n", amount)
    return fmt.Sprintf("CC-%d", time.Now().Unix()), nil
}

func (cc *CreditCardProcessor) Refund(transactionID string) error {
    fmt.Printf("Refunding transaction %s\n", transactionID)
    return nil
}

// PayPalProcessor - also implements interface implicitly
type PayPalProcessor struct {
    Email string
}

func (pp *PayPalProcessor) ProcessPayment(amount float64) (string, error) {
    if amount <= 0 {
        return "", fmt.Errorf("invalid amount")
    }
    fmt.Printf("Processing $%.2f via PayPal\n", amount)
    return fmt.Sprintf("PP-%d", time.Now().Unix()), nil
}

func (pp *PayPalProcessor) Refund(transactionID string) error {
    fmt.Printf("Refunding PayPal transaction %s\n", transactionID)
    return nil
}

// Checkout - works with ANY PaymentProcessor
func Checkout(processor PaymentProcessor, amount float64) (string, error) {
    return processor.ProcessPayment(amount)
}

// Usage
func main() {
    cc := &CreditCardProcessor{CardNumber: "1234-5678", CVV: "123"}
    paypal := &PayPalProcessor{Email: "user@example.com"}

    Checkout(cc, 100.0)     // Credit card
    Checkout(paypal, 200.0) // PayPal
}
```

### Interface Composition

Go allows composing interfaces from smaller interfaces:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// ReadWriter - composed of Reader and Writer
type ReadWriter interface {
    Reader
    Writer
}

// ReadWriteCloser - composed of all three
type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

---

## 3. Inheritance (Composition) 👨‍👩‍👧

### Definition
Go doesn't have traditional inheritance. Instead, it uses **struct embedding** and **composition**.

### Struct Embedding

```go
package animals

import "fmt"

// Animal - base struct
type Animal struct {
    Name string
    Age  int
}

func (a *Animal) Eat() {
    fmt.Printf("%s is eating\n", a.Name)
}

func (a *Animal) Sleep() {
    fmt.Printf("%s is sleeping\n", a.Name)
}

// Dog - embeds Animal (composition, not inheritance)
type Dog struct {
    Animal        // Embedded struct - gets all Animal fields/methods
    Breed  string
}

func (d *Dog) Bark() {
    fmt.Printf("%s says: Woof!\n", d.Name)  // Can access Animal.Name directly
}

// Override - define method with same name to "override"
func (d *Dog) Eat() {
    fmt.Printf("%s the %s is eating dog food\n", d.Name, d.Breed)
}

// Cat - also embeds Animal
type Cat struct {
    Animal
    Indoor bool
}

func (c *Cat) Meow() {
    fmt.Printf("%s says: Meow!\n", c.Name)
}

// Usage
func main() {
    dog := Dog{
        Animal: Animal{Name: "Buddy", Age: 3},
        Breed:  "Golden Retriever",
    }

    cat := Cat{
        Animal: Animal{Name: "Whiskers", Age: 2},
        Indoor: true,
    }

    dog.Eat()    // Uses Dog's version (overridden)
    cat.Eat()    // Uses Animal's version (inherited)
    dog.Sleep()  // Uses Animal's version (inherited)
    dog.Bark()   // Dog-specific
    cat.Meow()   // Cat-specific
}
```

### Composition Over Inheritance

```go
// Explicit composition - more flexible
type DogV2 struct {
    animal Animal  // Named field, not embedding
    Breed  string
}

// Must explicitly forward calls
func (d *DogV2) Eat() {
    d.animal.Eat()
}

func (d *DogV2) GetName() string {
    return d.animal.Name  // Access through field
}
```

---

## 4. Polymorphism 🦎

### Definition
**Polymorphism** in Go is achieved through interfaces - any type implementing the interface can be used.

### Interface-Based Polymorphism

```go
package shapes

import (
    "fmt"
    "math"
)

// Shape - interface
type Shape interface {
    Area() float64
    Perimeter() float64
}

// Circle
type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * math.Pi * c.Radius
}

// Rectangle
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

// Triangle
type Triangle struct {
    A, B, C float64
}

func (t Triangle) Area() float64 {
    s := (t.A + t.B + t.C) / 2
    return math.Sqrt(s * (s - t.A) * (s - t.B) * (s - t.C))
}

func (t Triangle) Perimeter() float64 {
    return t.A + t.B + t.C
}

// PrintShapeInfo - works with ANY Shape
func PrintShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f\n", s.Area())
    fmt.Printf("Perimeter: %.2f\n", s.Perimeter())
}

// Usage
func main() {
    shapes := []Shape{
        Circle{Radius: 5},
        Rectangle{Width: 4, Height: 6},
        Triangle{A: 3, B: 4, C: 5},
    }

    for _, shape := range shapes {
        PrintShapeInfo(shape)
    }
}
```

### Empty Interface and Type Assertions

```go
// interface{} (or 'any' in Go 1.18+) - accepts anything
func PrintAnything(v interface{}) {
    fmt.Println(v)
}

// Type assertion to get concrete type
func ProcessValue(v interface{}) {
    // Type switch
    switch val := v.(type) {
    case int:
        fmt.Printf("Integer: %d\n", val)
    case string:
        fmt.Printf("String: %s\n", val)
    case Shape:
        fmt.Printf("Shape with area: %.2f\n", val.Area())
    default:
        fmt.Printf("Unknown type: %T\n", val)
    }
}

// Type assertion with check
func GetCircleRadius(s Shape) (float64, bool) {
    if circle, ok := s.(Circle); ok {
        return circle.Radius, true
    }
    return 0, false
}
```

---

## Go-Specific Concepts Summary

### 1. Visibility Rules
```go
type PublicStruct struct {      // Visible outside package
    PublicField  string          // Visible outside package
    privateField string          // Only visible in package
}

func PublicFunction() {}         // Exported
func privateFunction() {}        // Not exported
```

### 2. Interface Implementation
```go
// No explicit "implements" keyword
// Any type with matching methods automatically implements interface

type Speaker interface {
    Speak() string
}

type Dog struct{}
func (d Dog) Speak() string { return "Woof" }

// Dog now implements Speaker automatically!
```

### 3. Concurrency Primitives

**Mutex:**
```go
var mu sync.Mutex
mu.Lock()
// critical section
mu.Unlock()

// Better: use defer
mu.Lock()
defer mu.Unlock()
// critical section
```

**RWMutex:**
```go
var mu sync.RWMutex

// Multiple readers
mu.RLock()
defer mu.RUnlock()
// read operations

// Single writer
mu.Lock()
defer mu.Unlock()
// write operations
```

**Channels:**
```go
// Unbuffered channel
ch := make(chan int)

// Buffered channel
ch := make(chan int, 10)

// Send
ch <- 42

// Receive
value := <-ch

// Close
close(ch)

// Range over channel
for value := range ch {
    fmt.Println(value)
}
```

**Select Statement:**
```go
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case msg := <-ch2:
    fmt.Println("Received from ch2:", msg)
case <-time.After(1 * time.Second):
    fmt.Println("Timeout!")
default:
    fmt.Println("No message received")
}
```

**Goroutines:**
```go
// Start goroutine
go func() {
    fmt.Println("Running in goroutine")
}()

// Wait for goroutines
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    // do work
}()
wg.Wait()
```

**sync.Once:**
```go
var once sync.Once
var instance *Singleton

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{}
    })
    return instance
}
```

---

## Key Takeaways for Go

✅ **Encapsulation**: Use lowercase/Uppercase for visibility control
✅ **Abstraction**: Interfaces with implicit implementation (no "implements" keyword)
✅ **Inheritance**: Use struct embedding, not traditional inheritance
✅ **Polymorphism**: Interface-based, any type can implement any interface

✅ **Concurrency**: `sync.Mutex`, `sync.RWMutex`, channels, goroutines
✅ **No Classes**: Use structs with methods
✅ **Composition**: Preferred over inheritance
✅ **Simple**: Fewer features, more explicit code

---

**Related Files:**
- [Python Implementation](./python.md)
- [Java Implementation](./java.md)
- [JavaScript Implementation](./javascript.md)
- [Back to OOP Fundamentals](../README.md)
