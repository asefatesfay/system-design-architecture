# Classes and Objects - Java

Complete guide to classes and objects in Java with Java-specific features and best practices.

## What is a Class?

A **class** is a blueprint or template for creating objects. In Java, everything is built around classes.

```java
// Class definition
public class Dog {
    // Class body
}

public class Main {
    public static void main(String[] args) {
        // Creating objects (instances)
        Dog dog1 = new Dog();
        Dog dog2 = new Dog();
        Dog dog3 = new Dog();

        // Each object is unique
        System.out.println(dog1 == dog2);  // false - different references
    }
}
```

---

## Basic Class Structure

```java
public class ClassName {
    // Class variables (static) - shared by all instances
    private static String species = "Homo sapiens";

    // Instance variables - unique per object
    private String attribute;

    // Constructor
    public ClassName(String parameter) {
        this.attribute = parameter;
    }

    // Instance method
    public void methodName() {
        // Do something
    }

    // Getter
    public String getAttribute() {
        return attribute;
    }

    // Setter
    public void setAttribute(String attribute) {
        this.attribute = attribute;
    }
}
```

---

## The Constructor

Constructors initialize new objects. Java requires explicit constructor definitions.

```java
public class Person {
    private String name;
    private int age;

    // Constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
        System.out.println("Created person: " + name);
    }

    // Getters
    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }
}

public class Main {
    public static void main(String[] args) {
        Person person1 = new Person("Alice", 30);  // Output: Created person: Alice
        Person person2 = new Person("Bob", 25);    // Output: Created person: Bob

        System.out.println(person1.getName());  // Alice
        System.out.println(person2.getName());  // Bob
    }
}
```

### Constructor Overloading

```java
public class Person {
    private String name;
    private int age;

    // Constructor 1
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Constructor 2 - default age
    public Person(String name) {
        this(name, 0);  // Call other constructor
    }

    // Constructor 3 - no parameters
    public Person() {
        this("Unknown", 0);
    }
}
```

---

## The `this` Keyword

`this` refers to the current instance of the class.

```java
public class Counter {
    private int count;

    public Counter() {
        this.count = 0;  // this.count refers to instance variable
    }

    public void increment() {
        this.count++;  // Modify this object's count
    }

    public int getCount() {
        return this.count;  // Return this object's count
    }
}

public class Main {
    public static void main(String[] args) {
        // Each object has its own count
        Counter counter1 = new Counter();
        Counter counter2 = new Counter();

        counter1.increment();
        counter1.increment();
        counter2.increment();

        System.out.println(counter1.getCount());  // 2
        System.out.println(counter2.getCount());  // 1
    }
}
```

---

## Instance Variables vs Class Variables

### Instance Variables
- Unique to each object
- Declared without `static`
- Different value for each instance

### Class Variables (static)
- Shared by all instances
- Declared with `static`
- Same value for all instances

```java
public class Employee {
    // Class variable (static) - shared by ALL employees
    private static String company = "TechCorp";
    private static int employeeCount = 0;

    // Instance variables - unique per employee
    private String name;
    private int salary;

    public Employee(String name, int salary) {
        this.name = name;
        this.salary = salary;
        employeeCount++;  // Modify class variable
    }

    public String getName() {
        return name;
    }

    public static String getCompany() {
        return company;
    }

    public static int getEmployeeCount() {
        return employeeCount;
    }

    public static void setCompany(String newCompany) {
        company = newCompany;
    }
}

public class Main {
    public static void main(String[] args) {
        Employee emp1 = new Employee("Alice", 80000);
        Employee emp2 = new Employee("Bob", 90000);

        // Instance variables are different
        System.out.println(emp1.getName());  // Alice
        System.out.println(emp2.getName());  // Bob

        // Class variable is same for all
        System.out.println(Employee.getCompany());      // TechCorp
        System.out.println(Employee.getEmployeeCount()); // 2

        // Changing class variable affects all
        Employee.setCompany("NewCorp");
        System.out.println(Employee.getCompany());  // NewCorp
    }
}
```

---

## Instance Methods

Methods that operate on instance data.

```java
public class BankAccount {
    private String accountNumber;
    private double balance;

    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }

    public boolean deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            return true;
        }
        return false;
    }

    public boolean withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            return true;
        }
        return false;
    }

    public double getBalance() {
        return balance;
    }
}

public class Main {
    public static void main(String[] args) {
        BankAccount account = new BankAccount("123456", 1000);
        account.deposit(500);
        account.withdraw(200);
        System.out.println(account.getBalance());  // 1300.0
    }
}
```

---

## Static Methods

Methods that belong to the class, not instances. Cannot access instance variables.

```java
public class MathUtils {
    // Static methods - no need to create object
    public static int add(int a, int b) {
        return a + b;
    }

    public static boolean isEven(int number) {
        return number % 2 == 0;
    }

    public static double fahrenheitToCelsius(double f) {
        return (f - 32) * 5 / 9;
    }
}

public class Main {
    public static void main(String[] args) {
        // Call without creating object
        System.out.println(MathUtils.add(5, 3));                   // 8
        System.out.println(MathUtils.isEven(10));                   // true
        System.out.println(MathUtils.fahrenheitToCelsius(98.6));    // 37.0
    }
}
```

---

## String Representation: toString()

Override `toString()` to provide human-readable representation.

```java
public class Book {
    private String title;
    private String author;

    public Book(String title, String author) {
        this.title = title;
        this.author = author;
    }

    @Override
    public String toString() {
        return String.format("\"%s\" by %s", title, author);
    }
}

public class Main {
    public static void main(String[] args) {
        Book book = new Book("1984", "George Orwell");
        System.out.println(book);  // "1984" by George Orwell
    }
}
```

---

## Real-World Example: Movie Class

```java
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

public class Movie {
    // Class variable (static)
    private static int totalMovies = 0;

    // Instance variables
    private int movieId;
    private String title;
    private String genre;
    private int duration; // minutes
    private LocalDate releaseDate;
    private List<Integer> ratings;

    // Constructor
    public Movie(int movieId, String title, String genre, int duration, LocalDate releaseDate) {
        this.movieId = movieId;
        this.title = title;
        this.genre = genre;
        this.duration = duration;
        this.releaseDate = releaseDate;
        this.ratings = new ArrayList<>();
        totalMovies++;
    }

    // Instance method - Add rating
    public boolean addRating(int rating) {
        if (rating >= 1 && rating <= 5) {
            ratings.add(rating);
            return true;
        }
        return false;
    }

    // Instance method - Get average rating
    public double getAverageRating() {
        if (ratings.isEmpty()) {
            return 0.0;
        }
        int sum = 0;
        for (int rating : ratings) {
            sum += rating;
        }
        return (double) sum / ratings.size();
    }

    // Instance method - Check if recently released
    public boolean isRecentlyReleased(int days) {
        LocalDate today = LocalDate.now();
        long daysSinceRelease = ChronoUnit.DAYS.between(releaseDate, today);
        return daysSinceRelease <= days;
    }

    // Getters
    public int getMovieId() {
        return movieId;
    }

    public String getTitle() {
        return title;
    }

    public static int getTotalMovies() {
        return totalMovies;
    }

    // toString (human-readable)
    @Override
    public String toString() {
        double avgRating = getAverageRating();
        return String.format("%s (%s) - %.1f★", title, genre, avgRating);
    }

    // Usage example
    public static void main(String[] args) {
        Movie inception = new Movie(
            1,
            "Inception",
            "Sci-Fi",
            148,
            LocalDate.of(2010, 7, 16)
        );

        inception.addRating(5);
        inception.addRating(4);
        inception.addRating(5);

        System.out.println(inception);  // Inception (Sci-Fi) - 4.7★
        System.out.printf("Average rating: %.2f%n", inception.getAverageRating());
        System.out.printf("Recently released: %b%n", inception.isRecentlyReleased(30));
        System.out.printf("Total movies: %d%n", Movie.getTotalMovies());
    }
}
```

---

## Common Patterns

### 1. Builder Pattern

```java
public class Person {
    private String name;
    private int age;
    private String email;
    private String phone;

    // Private constructor
    private Person(Builder builder) {
        this.name = builder.name;
        this.age = builder.age;
        this.email = builder.email;
        this.phone = builder.phone;
    }

    // Static nested Builder class
    public static class Builder {
        private String name;
        private int age;
        private String email;
        private String phone;

        public Builder name(String name) {
            this.name = name;
            return this;
        }

        public Builder age(int age) {
            this.age = age;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }

        public Person build() {
            return new Person(this);
        }
    }

    @Override
    public String toString() {
        return String.format("Person{name='%s', age=%d, email='%s', phone='%s'}",
                             name, age, email, phone);
    }
}

public class Main {
    public static void main(String[] args) {
        // Fluent interface with method chaining
        Person person = new Person.Builder()
            .name("Alice")
            .age(30)
            .email("alice@example.com")
            .phone("555-1234")
            .build();

        System.out.println(person);
    }
}
```

### 2. Singleton Pattern

```java
public class Database {
    // Static instance
    private static Database instance;

    // Private constructor prevents instantiation
    private Database() {
        System.out.println("Database connection initialized");
    }

    // Static method to get instance
    public static Database getInstance() {
        if (instance == null) {
            instance = new Database();
        }
        return instance;
    }

    public void query(String sql) {
        System.out.println("Executing: " + sql);
    }
}

public class Main {
    public static void main(String[] args) {
        Database db1 = Database.getInstance();
        Database db2 = Database.getInstance();

        System.out.println(db1 == db2);  // true - same instance
    }
}
```

---

## Java-Specific Features

### 1. Access Modifiers

```java
public class Example {
    public int publicField;        // Accessible everywhere
    protected int protectedField;  // Package + subclasses
    int packageField;              // Package only (default)
    private int privateField;      // Only within this class

    public void publicMethod() { }
    protected void protectedMethod() { }
    void packageMethod() { }
    private void privateMethod() { }
}
```

### 2. Final Keyword

```java
public class Constants {
    // Final variable - cannot change
    public static final double PI = 3.14159;

    // Final instance variable - must initialize in constructor
    private final String id;

    public Constants(String id) {
        this.id = id;
        // this.id = "other";  // Error - can only assign once
    }
}

// Final class - cannot extend
public final class ImmutableClass {
    // ...
}

// Final method - cannot override
public class Parent {
    public final void criticalMethod() {
        // Cannot be overridden
    }
}
```

### 3. Nested Classes

```java
public class OuterClass {
    private int outerField = 10;

    // Inner class - has access to outer class members
    public class InnerClass {
        public void display() {
            System.out.println("Outer field: " + outerField);
        }
    }

    // Static nested class - no access to instance members
    public static class StaticNestedClass {
        public void display() {
            System.out.println("Static nested class");
            // Cannot access outerField
        }
    }
}

public class Main {
    public static void main(String[] args) {
        // Inner class requires instance of outer class
        OuterClass outer = new OuterClass();
        OuterClass.InnerClass inner = outer.new InnerClass();
        inner.display();

        // Static nested class doesn't require outer instance
        OuterClass.StaticNestedClass nested = new OuterClass.StaticNestedClass();
        nested.display();
    }
}
```

### 4. Immutable Classes

```java
public final class Point {
    private final double x;
    private final double y;

    public Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    // Only getters, no setters
    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    // Return new object for modifications
    public Point move(double dx, double dy) {
        return new Point(x + dx, y + dy);
    }
}
```

### 5. Records (Java 14+)

```java
// Compact syntax for immutable data classes
public record Point(double x, double y) {
    // Automatically gets constructor, getters, equals, hashCode, toString

    // Can add custom methods
    public double distanceFromOrigin() {
        return Math.sqrt(x * x + y * y);
    }
}

public class Main {
    public static void main(String[] args) {
        Point p = new Point(3, 4);
        System.out.println(p);  // Point[x=3.0, y=4.0]
        System.out.println(p.x());  // 3.0 (getter)
        System.out.println(p.distanceFromOrigin());  // 5.0
    }
}
```

---

## Key Takeaways

1. **Class** = Blueprint, **Object** = Instance
2. Constructors initialize objects (can be overloaded)
3. `this` refers to current instance
4. **Instance variables** are unique per object
5. **static variables/methods** belong to the class
6. Use `private` for encapsulation, provide getters/setters
7. Override `toString()` for readable output
8. Use `final` for immutability
9. Java 14+ **records** for simple data classes
10. Access modifiers: `private` < package < `protected` < `public`

---

## Practice Exercises

1. Create a `Student` class with name, ID, and grades list
2. Add methods to add grade, calculate average, check if passing
3. Implement `toString()` method
4. Add a static variable to track total students
5. Add a static method to get student count
6. Create multiple student objects and test them
7. Try creating the class as a **record** (Java 14+)

---

**Related Files:**
- [Python Implementation](./python.md)
- [Go Implementation](./go.md)
- [JavaScript Implementation](./javascript.md)
- [Back to OOP Fundamentals](../README.md)
- [The Four Pillars of OOP](../four-pillars/)
