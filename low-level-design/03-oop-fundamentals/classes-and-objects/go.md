# Classes and Objects - Go

Complete guide to structs and objects in Go. Go doesn't have classes but uses **structs with methods** to achieve similar functionality.

## What is a Struct?

A **struct** is Go's way of creating custom types that group related data. It's similar to a class but more lightweight.

```go
package main

import "fmt"

// Dog struct (equivalent to class)
type Dog struct {
    Name string
    Age  int
}

func main() {
    // Creating instances (objects)
    dog1 := Dog{Name: "Buddy", Age: 3}
    dog2 := Dog{Name: "Max", Age: 5}
    dog3 := Dog{Name: "Luna", Age: 2}

    // Each instance is unique
    fmt.Println(&dog1 == &dog2)  // false - different memory addresses
}
```

---

## Basic Struct Structure

```go
package main

// Struct definition
type StructName struct {
    // Exported fields (public) - start with Uppercase
    PublicField string

    // Unexported fields (private) - start with lowercase
    privateField int
}

// Constructor function (by convention, starts with "New")
func NewStructName(param string) *StructName {
    return &StructName{
        PublicField:  param,
        privateField: 42,
    }
}

// Method - function with receiver
func (s *StructName) MethodName() {
    // Access fields via receiver
    fmt.Println(s.PublicField)
}
```

---

## Constructor Functions

Go doesn't have constructors. Instead, use **constructor functions** (by convention, named `NewTypeName`).

```go
type Person struct {
    Name string
    Age  int
}

// Constructor function
func NewPerson(name string, age int) *Person {
    fmt.Printf("Created person: %s\n", name)
    return &Person{
        Name: name,
        Age:  age,
    }
}

func main() {
    // Creating objects calls constructor function
    person1 := NewPerson("Alice", 30)  // Output: Created person: Alice
    person2 := NewPerson("Bob", 25)    // Output: Created person: Bob

    fmt.Println(person1.Name)  // Alice
    fmt.Println(person2.Name)  // Bob
}
```

**Note:** Returns pointer (`*Person`) for efficiency and to allow modifications.

---

## Methods and Receivers

Go uses **methods with receivers** instead of class methods.

```go
type Counter struct {
    count int  // lowercase = unexported (private)
}

// Method with pointer receiver (can modify struct)
func (c *Counter) Increment() {
    c.count++
}

// Method with value receiver (read-only)
func (c Counter) GetCount() int {
    return c.count
}

func main() {
    // Each object has its own count
    counter1 := &Counter{}
    counter2 := &Counter{}

    counter1.Increment()
    counter1.Increment()
    counter2.Increment()

    fmt.Println(counter1.GetCount())  // 2
    fmt.Println(counter2.GetCount())  // 1
}
```

**Pointer Receiver vs Value Receiver:**
- `func (c *Counter)` - **Pointer receiver**: Can modify the struct, efficient for large structs
- `func (c Counter)` - **Value receiver**: Cannot modify (gets a copy), use for read-only operations

---

## "Instance" Variables vs Package Variables

### Struct Fields (Instance Variables)
- Unique to each struct instance
- Defined inside the struct

### Package-Level Variables (Class Variables Equivalent)
- Shared across the package
- Defined outside structs

```go
package main

import "fmt"

// Package-level variable (shared - like class variable)
var companyName = "TechCorp"
var employeeCount = 0

type Employee struct {
    // Struct fields (unique per instance)
    Name   string
    Salary int
}

func NewEmployee(name string, salary int) *Employee {
    employeeCount++  // Modify package-level variable
    return &Employee{
        Name:   name,
        Salary: salary,
    }
}

func main() {
    emp1 := NewEmployee("Alice", 80000)
    emp2 := NewEmployee("Bob", 90000)

    // Struct fields are different
    fmt.Println(emp1.Name)  // Alice
    fmt.Println(emp2.Name)  // Bob

    // Package variable is same for all
    fmt.Println(companyName)    // TechCorp
    fmt.Println(employeeCount)  // 2

    // Changing package variable affects all
    companyName = "NewCorp"
    fmt.Println(companyName)  // NewCorp
}
```

---

## Methods (Functions with Receivers)

```go
type BankAccount struct {
    accountNumber string
    balance       float64
}

func NewBankAccount(accountNumber string, initialBalance float64) *BankAccount {
    return &BankAccount{
        accountNumber: accountNumber,
        balance:       initialBalance,
    }
}

// Method - deposit money
func (ba *BankAccount) Deposit(amount float64) bool {
    if amount > 0 {
        ba.balance += amount
        return true
    }
    return false
}

// Method - withdraw money
func (ba *BankAccount) Withdraw(amount float64) bool {
    if amount > 0 && amount <= ba.balance {
        ba.balance -= amount
        return true
    }
    return false
}

// Getter method (value receiver since read-only)
func (ba BankAccount) GetBalance() float64 {
    return ba.balance
}

func main() {
    account := NewBankAccount("123456", 1000)
    account.Deposit(500)
    account.Withdraw(200)
    fmt.Println(account.GetBalance())  // 1300
}
```

---

## Package-Level Functions (Static Methods Equivalent)

Go doesn't have static methods. Use package-level functions instead.

```go
package mathutils

// Package-level functions (like static methods)
func Add(a, b int) int {
    return a + b
}

func IsEven(number int) bool {
    return number%2 == 0
}

func FahrenheitToCelsius(f float64) float64 {
    return (f - 32) * 5 / 9
}

// Usage from another package
package main

import (
    "fmt"
    "yourmodule/mathutils"
)

func main() {
    fmt.Println(mathutils.Add(5, 3))                   // 8
    fmt.Println(mathutils.IsEven(10))                   // true
    fmt.Println(mathutils.FahrenheitToCelsius(98.6))    // 37.0
}
```

---

## String Representation

Go uses the `String()` method (implements `fmt.Stringer` interface).

```go
type Book struct {
    Title  string
    Author string
}

// String method (like Python's __str__)
func (b Book) String() string {
    return fmt.Sprintf("\"%s\" by %s", b.Title, b.Author)
}

func main() {
    book := Book{Title: "1984", Author: "George Orwell"}
    fmt.Println(book)  // "1984" by George Orwell
}
```

### GoString for Developer Representation

```go
type Point struct {
    X, Y float64
}

// String for users
func (p Point) String() string {
    return fmt.Sprintf("(%.1f, %.1f)", p.X, p.Y)
}

// GoString for developers (used by %#v)
func (p Point) GoString() string {
    return fmt.Sprintf("Point{X: %.1f, Y: %.1f}", p.X, p.Y)
}

func main() {
    point := Point{X: 3.0, Y: 4.0}
    fmt.Println(point)       // (3.0, 4.0) - uses String()
    fmt.Printf("%#v\n", point)  // Point{X: 3.0, Y: 4.0} - uses GoString()
}
```

---

## Real-World Example: Movie Struct

```go
package main

import (
    "fmt"
    "time"
)

// Package-level variable (like class variable)
var totalMovies int

// Movie struct
type Movie struct {
    MovieID     int
    Title       string
    Genre       string
    Duration    int // minutes
    ReleaseDate time.Time
    ratings     []int  // unexported (private)
}

// Constructor function
func NewMovie(movieID int, title, genre string, duration int, releaseDate time.Time) *Movie {
    totalMovies++  // Update package variable
    return &Movie{
        MovieID:     movieID,
        Title:       title,
        Genre:       genre,
        Duration:    duration,
        ReleaseDate: releaseDate,
        ratings:     make([]int, 0),
    }
}

// Method - Add rating
func (m *Movie) AddRating(rating int) bool {
    if rating >= 1 && rating <= 5 {
        m.ratings = append(m.ratings, rating)
        return true
    }
    return false
}

// Method - Get average rating
func (m *Movie) GetAverageRating() float64 {
    if len(m.ratings) == 0 {
        return 0.0
    }
    sum := 0
    for _, rating := range m.ratings {
        sum += rating
    }
    return float64(sum) / float64(len(m.ratings))
}

// Method - Check if recently released
func (m *Movie) IsRecentlyReleased(days int) bool {
    today := time.Now()
    daysSinceRelease := int(today.Sub(m.ReleaseDate).Hours() / 24)
    return daysSinceRelease <= days
}

// String method
func (m *Movie) String() string {
    avgRating := m.GetAverageRating()
    return fmt.Sprintf("%s (%s) - %.1f★", m.Title, m.Genre, avgRating)
}

// GoString method (developer representation)
func (m *Movie) GoString() string {
    return fmt.Sprintf("Movie{ID: %d, Title: '%s'}", m.MovieID, m.Title)
}

func main() {
    // Usage
    inception := NewMovie(
        1,
        "Inception",
        "Sci-Fi",
        148,
        time.Date(2010, 7, 16, 0, 0, 0, 0, time.UTC),
    )

    inception.AddRating(5)
    inception.AddRating(4)
    inception.AddRating(5)

    fmt.Println(inception)  // Inception (Sci-Fi) - 4.7★
    fmt.Printf("Average rating: %.2f\n", inception.GetAverageRating())
    fmt.Printf("Recently released: %v\n", inception.IsRecentlyReleased(30))
    fmt.Printf("Total movies in system: %d\n", totalMovies)
}
```

---

## Common Patterns

### 1. Builder Pattern with Method Chaining

```go
type QueryBuilder struct {
    query string
}

func NewQueryBuilder() *QueryBuilder {
    return &QueryBuilder{query: ""}
}

func (qb *QueryBuilder) Select(fields string) *QueryBuilder {
    qb.query += "SELECT " + fields + " "
    return qb  // Return self for chaining
}

func (qb *QueryBuilder) From(table string) *QueryBuilder {
    qb.query += "FROM " + table + " "
    return qb
}

func (qb *QueryBuilder) Where(condition string) *QueryBuilder {
    qb.query += "WHERE " + condition + " "
    return qb
}

func (qb *QueryBuilder) Build() string {
    return qb.query
}

func main() {
    // Method chaining
    query := NewQueryBuilder().
        Select("name, age").
        From("users").
        Where("age > 18").
        Build()

    fmt.Println(query)  // SELECT name, age FROM users WHERE age > 18
}
```

### 2. Options Pattern for Constructors

```go
type Config struct {
    host    string
    port    int
    timeout int
}

// Option function type
type ConfigOption func(*Config)

// Option functions
func WithHost(host string) ConfigOption {
    return func(c *Config) {
        c.host = host
    }
}

func WithPort(port int) ConfigOption {
    return func(c *Config) {
        c.port = port
    }
}

func WithTimeout(timeout int) ConfigOption {
    return func(c *Config) {
        c.timeout = timeout
    }
}

// Constructor with options
func NewConfig(opts ...ConfigOption) *Config {
    // Defaults
    c := &Config{
        host:    "localhost",
        port:    8080,
        timeout: 30,
    }

    // Apply options
    for _, opt := range opts {
        opt(c)
    }

    return c
}

func main() {
    // Flexible construction
    config1 := NewConfig()  // All defaults
    config2 := NewConfig(WithHost("example.com"), WithPort(9000))
    config3 := NewConfig(WithTimeout(60))
}
```

---

## Go-Specific Features

### 1. Embedded Structs (Composition)

```go
type Address struct {
    Street string
    City   string
}

type Person struct {
    Name string
    Address  // Embedded - can access Address fields directly
}

func main() {
    p := Person{
        Name: "Alice",
        Address: Address{
            Street: "123 Main St",
            City:   "NYC",
        },
    }

    // Can access embedded fields directly
    fmt.Println(p.Name)    // Alice
    fmt.Println(p.Street)  // 123 Main St (from embedded Address)
    fmt.Println(p.City)    // NYC
}
```

### 2. Zero Values

Go initializes all fields to zero values automatically:

```go
type User struct {
    ID       int     // 0
    Name     string  // ""
    Active   bool    // false
    Score    float64 // 0.0
    Tags     []string // nil
}

func main() {
    u := User{}  // All fields have zero values
    fmt.Printf("%+v\n", u)  // {ID:0 Name: Active:false Score:0 Tags:[]}
}
```

### 3. Tags for Metadata

```go
type User struct {
    ID    int    `json:"id" db:"user_id"`
    Name  string `json:"name" db:"user_name"`
    Email string `json:"email" db:"email_address"`
}

// Tags are used by json.Marshal, database libraries, etc.
```

---

## Key Takeaways

1. **Struct** = Blueprint (no class keyword)
2. **Constructor functions** replace constructors (`NewTypeName`)
3. **Methods** have receivers (`func (s *Struct) Method()`)
4. **Pointer receivers** for modification, **value receivers** for read-only
5. **Uppercase** = exported (public), **lowercase** = unexported (private)
6. **Package-level variables** act like class variables
7. **Package-level functions** act like static methods
8. Implement `String()` for user output
9. Implement `GoString()` for developer debugging
10. Use **embedded structs** for composition

---

## Practice Exercises

1. Create a `Student` struct with name, ID, and grades slice
2. Add methods to add grade, calculate average, and check if passing
3. Implement `String()` and `GoString()` methods
4. Add a package-level variable to track total number of students
5. Create a constructor function that increments the counter
6. Create multiple student instances and test them

---

**Related Files:**
- [Python Implementation](./python.md)
- [Java Implementation](./java.md)
- [JavaScript Implementation](./javascript.md)
- [Back to OOP Fundamentals](../README.md)
- [The Four Pillars of OOP](../four-pillars/)
