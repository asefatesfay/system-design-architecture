# What is Low-Level Design (LLD)?

## Overview

**Low-Level Design (LLD)** is a form of software design that focuses on the implementation details of a system. It bridges the gap between high-level system architecture and actual code implementation.

## Definition

LLD deals with how individual components of a system should be structured, organized, and implemented. It answers questions like:

- What **classes** should we create?
- What **responsibilities** should each class have?
- How should different **objects interact**?
- Which **interfaces** and **methods** should we define?
- How do we keep the code **readable**, **extensible**, and **maintainable**?

## Key Focus Areas

### 1. Class Design
Identifying the right classes and their responsibilities.

```java
// Example: Designing classes for a Library System
class Book {
    private String isbn;
    private String title;
    private String author;
    private boolean isAvailable;
}

class Member {
    private String memberId;
    private String name;
    private List<Book> borrowedBooks;
}

class Library {
    private List<Book> books;
    private List<Member> members;

    public void borrowBook(Member member, Book book) {
        // Implementation
    }
}
```

### 2. Object Relationships
Defining how objects collaborate and communicate.

```java
// Composition: Library HAS-A collection of Books
class Library {
    private List<Book> books;  // Library owns books
}

// Association: Member borrows Book
class Member {
    private List<Book> borrowedBooks;  // Member references books
}
```

### 3. Interface Design
Creating clean contracts for behavior.

```java
interface Searchable {
    List<Book> searchByTitle(String title);
    List<Book> searchByAuthor(String author);
}

class Library implements Searchable {
    @Override
    public List<Book> searchByTitle(String title) {
        // Implementation
    }
}
```

### 4. Design Principles
Applying SOLID principles and other best practices.

```java
// Single Responsibility: Each class has one job
class BookValidator {
    public boolean isValidISBN(String isbn) {
        // Validation logic
    }
}

class BookRepository {
    public void save(Book book) {
        // Persistence logic
    }
}
```

## Why LLD Matters

### 1. Interview Success
Many top companies (Google, Amazon, Meta, Microsoft) include LLD rounds in their interview process, even for entry-level positions.

### 2. Code Quality
Good LLD leads to:
- **Maintainable** code that's easy to modify
- **Testable** code with clear boundaries
- **Extensible** code that adapts to new requirements
- **Readable** code that others can understand

### 3. Professional Growth
Understanding LLD helps you:
- Write better production code
- Review code more effectively
- Architect scalable features
- Communicate design decisions clearly

## Real-World Example

Let's see the difference between thinking about a problem and designing a solution:

### Problem Statement
"Design a parking lot system"

### Without LLD (Vague)
"We need to track cars, parking spots, and payments."

### With LLD (Clear)
```java
// Core entities identified
class ParkingLot {
    private String id;
    private List<Floor> floors;
    private EntryGate entryGate;
    private ExitGate exitGate;
}

class Floor {
    private int floorNumber;
    private List<ParkingSpot> spots;
}

class ParkingSpot {
    private String spotId;
    private SpotType type;  // COMPACT, LARGE, HANDICAPPED
    private boolean isOccupied;
}

class Vehicle {
    private String licensePlate;
    private VehicleType type;  // CAR, TRUCK, MOTORCYCLE
}

class Ticket {
    private String ticketId;
    private Vehicle vehicle;
    private ParkingSpot assignedSpot;
    private LocalDateTime entryTime;
}

// Behavior defined
interface ParkingStrategy {
    ParkingSpot findSpot(VehicleType type);
}

class NearestSpotStrategy implements ParkingStrategy {
    public ParkingSpot findSpot(VehicleType type) {
        // Find nearest available spot
    }
}
```

## Common Misconceptions

### ❌ "LLD is just writing code"
**Reality**: LLD is about design decisions before writing code. It's about structure, not syntax.

### ❌ "LLD doesn't matter in real projects"
**Reality**: Poor LLD leads to technical debt, bugs, and difficult maintenance.

### ❌ "Only senior engineers need LLD"
**Reality**: LLD skills are valuable at all levels and increasingly tested in interviews.

## LLD vs Implementation

| Aspect | LLD | Implementation |
|--------|-----|----------------|
| Focus | Structure and relationships | Algorithms and logic |
| Question | "What classes do we need?" | "How does this method work?" |
| Abstraction | High-level design | Low-level details |
| Example | Define `PaymentProcessor` interface | Implement credit card validation algorithm |

## When to Apply LLD

- **Before coding**: Design the structure first
- **During refactoring**: Improve existing code structure
- **In code reviews**: Evaluate design decisions
- **In interviews**: Demonstrate design thinking
- **In architecture discussions**: Communicate implementation approach

## Next Steps

Now that you understand what LLD is, let's explore how it differs from High-Level Design (System Design) in [LLD vs HLD](./lld-vs-hld.md).

---

**Key Takeaway**: LLD is about thoughtfully designing the internal structure of a system using classes, objects, interfaces, and relationships while applying sound design principles.
