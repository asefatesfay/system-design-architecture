# The Four Pillars of OOP - Java

The four fundamental principles of Object-Oriented Programming in Java with Java-specific explanations.

## Overview

1. **Encapsulation** - Use access modifiers (private, protected, public)
2. **Abstraction** - Define contracts with abstract classes and interfaces
3. **Inheritance** - Extend classes with `extends` keyword
4. **Polymorphism** - Method overriding and interface implementation

---

## 1. Encapsulation 🔒

### Definition
**Encapsulation** in Java means using explicit access modifiers to control visibility of class members.

### Java Access Modifiers

Java has **four access levels**:
- `private`: Only within the same class
- (default/package-private): Within the same package
- `protected`: Same package + subclasses
- `public`: Everywhere

```java
package com.bank;

import java.util.ArrayList;
import java.util.List;

public class BankAccount {
    // Private fields - cannot access outside class
    private String accountNumber;
    private double balance;
    private List<Transaction> transactionHistory;

    // Constructor
    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
        this.transactionHistory = new ArrayList<>();
    }

    // Public methods - the API
    public boolean deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            addTransaction("deposit", amount);
            return true;
        }
        return false;
    }

    public boolean withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            addTransaction("withdraw", amount);
            return true;
        }
        return false;
    }

    // Public getter - read-only access
    public double getBalance() {
        return balance;
    }

    // Public getter for account number
    public String getAccountNumber() {
        return accountNumber;
    }

    // Protected method - accessible to subclasses
    protected double calculateInterest() {
        return balance * 0.03;
    }

    // Private helper method
    private void addTransaction(String type, double amount) {
        transactionHistory.add(new Transaction(type, amount));
    }

    // Private inner class
    private static class Transaction {
        private String type;
        private double amount;

        public Transaction(String type, double amount) {
            this.type = type;
            this.amount = amount;
        }
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        BankAccount account = new BankAccount("12345", 1000);

        System.out.println(account.getBalance());  // ✓ 1000
        account.deposit(500);                       // ✓ Works
        System.out.println(account.getBalance());  // ✓ 1500

        // account.balance = 5000;  // ❌ Compile error - private field
        // account.addTransaction(...);  // ❌ Compile error - private method
    }
}
```

### Java Thread Safety with synchronized

```java
public class ThreadSafeBankAccount {
    private String accountNumber;
    private double balance;

    public ThreadSafeBankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }

    // Synchronized method - only one thread can execute at a time
    public synchronized boolean deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            return true;
        }
        return false;
    }

    public synchronized boolean withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            return true;
        }
        return false;
    }

    public synchronized double getBalance() {
        return balance;
    }
}
```

### Java Locking with ReentrantLock

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class BankAccountWithLock {
    private double balance;
    private final Lock lock = new ReentrantLock();

    public BankAccountWithLock(double initialBalance) {
        this.balance = initialBalance;
    }

    public boolean deposit(double amount) {
        lock.lock();  // Acquire lock
        try {
            if (amount > 0) {
                balance += amount;
                return true;
            }
            return false;
        } finally {
            lock.unlock();  // Always release lock
        }
    }

    public boolean withdraw(double amount) {
        lock.lock();
        try {
            if (amount > 0 && amount <= balance) {
                balance -= amount;
                return true;
            }
            return false;
        } finally {
            lock.unlock();
        }
    }

    public double getBalance() {
        lock.lock();
        try {
            return balance;
        } finally {
            lock.unlock();
        }
    }
}
```

### Java Concurrency: volatile and AtomicInteger

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public class ConcurrencyExample {
    // volatile - ensures visibility across threads
    private volatile boolean running = true;

    // AtomicInteger - thread-safe without explicit locking
    private AtomicInteger counter = new AtomicInteger(0);
    private AtomicLong balance = new AtomicLong(0);

    public void stop() {
        running = false;  // Visible to all threads immediately
    }

    public boolean isRunning() {
        return running;
    }

    public void increment() {
        counter.incrementAndGet();  // Atomic operation
    }

    public int getCount() {
        return counter.get();
    }

    public void deposit(long amount) {
        balance.addAndGet(amount);  // Atomic addition
    }

    public long getBalance() {
        return balance.get();
    }
}
```

---

## 2. Abstraction 🎭

### Definition
**Abstraction** in Java means using abstract classes and interfaces to define contracts.

### Abstract Classes

```java
package com.payment;

public abstract class PaymentProcessor {
    // Abstract methods - must be implemented by subclasses
    public abstract String processPayment(double amount);
    public abstract boolean refund(String transactionId);

    // Concrete method - shared by all subclasses
    public boolean validateAmount(double amount) {
        return amount > 0;
    }

    // Protected method - accessible to subclasses
    protected void logTransaction(String message) {
        System.out.println("Transaction: " + message);
    }
}

public class CreditCardProcessor extends PaymentProcessor {
    private String cardNumber;

    public CreditCardProcessor(String cardNumber) {
        this.cardNumber = cardNumber;
    }

    @Override
    public String processPayment(double amount) {
        if (!validateAmount(amount)) {
            throw new IllegalArgumentException("Invalid amount");
        }
        logTransaction("Processing $" + amount + " via credit card");
        return "CC-" + System.currentTimeMillis();
    }

    @Override
    public boolean refund(String transactionId) {
        logTransaction("Refunding transaction: " + transactionId);
        return true;
    }
}

public class PayPalProcessor extends PaymentProcessor {
    private String email;

    public PayPalProcessor(String email) {
        this.email = email;
    }

    @Override
    public String processPayment(double amount) {
        if (!validateAmount(amount)) {
            throw new IllegalArgumentException("Invalid amount");
        }
        logTransaction("Processing $" + amount + " via PayPal");
        return "PP-" + System.currentTimeMillis();
    }

    @Override
    public boolean refund(String transactionId) {
        logTransaction("Refunding PayPal transaction: " + transactionId);
        return true;
    }
}
```

### Interfaces

```java
public interface PaymentMethod {
    String processPayment(double amount);
    boolean refund(String transactionId);
}

// Can implement multiple interfaces
public class StripeProcessor implements PaymentMethod {
    @Override
    public String processPayment(double amount) {
        System.out.println("Processing via Stripe: $" + amount);
        return "STRIPE-" + System.currentTimeMillis();
    }

    @Override
    public boolean refund(String transactionId) {
        System.out.println("Refunding: " + transactionId);
        return true;
    }
}

// Usage - polymorphism
public class Checkout {
    public static String checkout(PaymentMethod processor, double amount) {
        return processor.processPayment(amount);
    }

    public static void main(String[] args) {
        PaymentMethod stripe = new StripeProcessor();
        String txId = checkout(stripe, 100.0);
    }
}
```

### Java 8+ Default Methods in Interfaces

```java
public interface Vehicle {
    // Abstract method
    void start();

    // Default method - has implementation
    default void stop() {
        System.out.println("Vehicle stopped");
    }

    // Static method
    static void honk() {
        System.out.println("Beep beep!");
    }
}

public class Car implements Vehicle {
    @Override
    public void start() {
        System.out.println("Car engine started");
    }

    // Can override default method if needed
    @Override
    public void stop() {
        System.out.println("Car engine stopped");
    }
}
```

---

## 3. Inheritance 👨‍👩‍👧

### Definition
**Inheritance** in Java allows classes to inherit fields and methods from parent classes using `extends`.

### Basic Inheritance

```java
public class Animal {
    private String name;
    private int age;

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

    // Getters
    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }
}

public class Dog extends Animal {
    private String breed;

    public Dog(String name, int age, String breed) {
        super(name, age);  // Call parent constructor
        this.breed = breed;
    }

    public void bark() {
        System.out.println(getName() + " says: Woof!");
    }

    // Override parent method
    @Override
    public void eat() {
        System.out.println(getName() + " the " + breed + " is eating dog food");
    }
}

public class Cat extends Animal {
    private boolean indoor;

    public Cat(String name, int age, boolean indoor) {
        super(name, age);
        this.indoor = indoor;
    }

    public void meow() {
        System.out.println(getName() + " says: Meow!");
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        Dog dog = new Dog("Buddy", 3, "Golden Retriever");
        Cat cat = new Cat("Whiskers", 2, true);

        dog.eat();    // Overridden: "Buddy the Golden Retriever is eating dog food"
        cat.eat();    // Inherited: "Whiskers is eating"
        dog.sleep();  // Inherited: "Buddy is sleeping"
        dog.bark();   // Dog-specific: "Buddy says: Woof!"
        cat.meow();   // Cat-specific: "Whiskers says: Meow!"
    }
}
```

### Protected Members and Inheritance

```java
public class Vehicle {
    private String vin;       // Only in Vehicle
    protected int speed;      // Accessible to subclasses
    public String model;      // Accessible everywhere

    protected void accelerate() {
        speed += 10;
    }
}

public class Car extends Vehicle {
    public void goFaster() {
        // Can access protected members
        accelerate();
        speed += 5;

        // Cannot access private members
        // vin = "123";  // ❌ Compile error
    }
}
```

### super Keyword

```java
public class ElectricCar extends Car {
    private int batteryLevel;

    public ElectricCar(String name, int age, String breed, int batteryLevel) {
        super(name, age, breed);  // Call parent constructor
        this.batteryLevel = batteryLevel;
    }

    @Override
    public void eat() {
        super.eat();  // Call parent's eat() method
        System.out.println("Also charging battery...");
    }
}
```

---

## 4. Polymorphism 🦎

### Definition
**Polymorphism** in Java allows objects of different types to be treated through a common interface.

### Method Overriding (Runtime Polymorphism)

```java
public abstract class Shape {
    public abstract double area();
    public abstract double perimeter();
}

public class Circle extends Shape {
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

public class Rectangle extends Shape {
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

public class Triangle extends Shape {
    private double a, b, c;

    public Triangle(double a, double b, double c) {
        this.a = a;
        this.b = b;
        this.c = c;
    }

    @Override
    public double area() {
        double s = (a + b + c) / 2;
        return Math.sqrt(s * (s - a) * (s - b) * (s - c));
    }

    @Override
    public double perimeter() {
        return a + b + c;
    }
}

// Usage - Polymorphism in action
public class ShapeDemo {
    public static void printShapeInfo(Shape shape) {
        System.out.printf("Area: %.2f\n", shape.area());
        System.out.printf("Perimeter: %.2f\n", shape.perimeter());
    }

    public static void main(String[] args) {
        Shape[] shapes = {
            new Circle(5),
            new Rectangle(4, 6),
            new Triangle(3, 4, 5)
        };

        for (Shape shape : shapes) {
            printShapeInfo(shape);  // Works with any Shape!
        }
    }
}
```

### Interface-Based Polymorphism

```java
public interface Animal {
    void makeSound();
}

public class Dog implements Animal {
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}

public class Cat implements Animal {
    @Override
    public void makeSound() {
        System.out.println("Meow!");
    }
}

public class Duck implements Animal {
    @Override
    public void makeSound() {
        System.out.println("Quack!");
    }
}

// Polymorphism - same interface, different implementations
public class AnimalSounds {
    public static void makeItSpeak(Animal animal) {
        animal.makeSound();
    }

    public static void main(String[] args) {
        makeItSpeak(new Dog());   // Woof!
        makeItSpeak(new Cat());   // Meow!
        makeItSpeak(new Duck());  // Quack!
    }
}
```

### Method Overloading (Compile-Time Polymorphism)

```java
public class Calculator {
    // Same method name, different parameters
    public int add(int a, int b) {
        return a + b;
    }

    public double add(double a, double b) {
        return a + b;
    }

    public int add(int a, int b, int c) {
        return a + b + c;
    }

    public String add(String a, String b) {
        return a + b;
    }
}

// Usage
Calculator calc = new Calculator();
calc.add(2, 3);           // Calls int version
calc.add(2.5, 3.7);       // Calls double version
calc.add(1, 2, 3);        // Calls 3-parameter version
calc.add("Hello", " World");  // Calls String version
```

---

## Java-Specific Concepts Summary

### 1. Access Modifiers
```java
public class Example {
    private int onlyInThisClass;
    int packagePrivate;              // default
    protected int packageAndSubclass;
    public int everywhere;
}
```

### 2. Final Keyword
```java
// Final variable - cannot change value
final int MAX_SIZE = 100;

// Final method - cannot override
public final void criticalMethod() { }

// Final class - cannot extend
public final class ImmutableClass { }
```

### 3. Thread Synchronization

**synchronized keyword:**
```java
public class Counter {
    private int count = 0;

    // Synchronized method
    public synchronized void increment() {
        count++;
    }

    // Synchronized block
    public void decrement() {
        synchronized(this) {
            count--;
        }
    }
}
```

**ReentrantLock:**
```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Counter {
    private int count = 0;
    private Lock lock = new ReentrantLock();

    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();
        }
    }
}
```

**ReadWriteLock:**
```java
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class SharedResource {
    private String data;
    private ReadWriteLock lock = new ReentrantReadWriteLock();

    public String read() {
        lock.readLock().lock();
        try {
            return data;
        } finally {
            lock.readLock().unlock();
        }
    }

    public void write(String newData) {
        lock.writeLock().lock();
        try {
            data = newData;
        } finally {
            lock.writeLock().unlock();
        }
    }
}
```

**volatile:**
```java
public class Flag {
    // volatile ensures visibility across threads
    private volatile boolean running = true;

    public void stop() {
        running = false;
    }

    public boolean isRunning() {
        return running;
    }
}
```

**Atomic classes:**
```java
import java.util.concurrent.atomic.*;

public class AtomicExample {
    private AtomicInteger counter = new AtomicInteger(0);
    private AtomicLong balance = new AtomicLong(0);
    private AtomicBoolean flag = new AtomicBoolean(false);

    public void increment() {
        counter.incrementAndGet();
    }

    public void deposit(long amount) {
        balance.addAndGet(amount);
    }

    public boolean compareAndSet(int expected, int update) {
        return counter.compareAndSet(expected, update);
    }
}
```

---

## Key Takeaways for Java

✅ **Encapsulation**: Use private/protected/public access modifiers
✅ **Abstraction**: Use abstract classes and interfaces
✅ **Inheritance**: Use `extends` for classes, `implements` for interfaces
✅ **Polymorphism**: Method overriding (runtime) and overloading (compile-time)

✅ **Concurrency**: `synchronized`, `ReentrantLock`, `volatile`, atomic classes
✅ **Type Safety**: Strong static typing, explicit casting
✅ **Single Inheritance**: Can extend only one class, but implement multiple interfaces
✅ **Explicit**: Everything must be declared (types, access modifiers, etc.)

---

**Related Files:**
- [Python Implementation](./python.md)
- [Go Implementation](./go.md)
- [JavaScript Implementation](./javascript.md)
- [Back to OOP Fundamentals](../README.md)
