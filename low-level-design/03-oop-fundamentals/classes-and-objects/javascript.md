# Classes and Objects - JavaScript

Complete guide to classes and objects in JavaScript, covering both modern ES6 classes and prototype-based approaches.

## What is a Class?

In JavaScript, a **class** is syntactic sugar over the prototype-based inheritance system. ES6 introduced the `class` keyword.

```javascript
// ES6 Class
class Dog {
    constructor() {
        // Constructor code
    }
}

// Creating objects (instances)
const dog1 = new Dog();
const dog2 = new Dog();
const dog3 = new Dog();

// Each object is unique
console.log(dog1 === dog2);  // false - different objects
```

---

## Basic Class Structure

```javascript
class ClassName {
    // Static property (class variable)
    static species = 'Homo sapiens';

    constructor(parameter) {
        // Instance variables
        this.attribute = parameter;
    }

    // Instance method
    methodName() {
        // Do something
    }

    // Static method
    static staticMethod() {
        // Belongs to class, not instance
    }
}
```

---

## The Constructor

The `constructor` method initializes new objects.

```javascript
class Person {
    constructor(name, age) {
        this.name = name;  // Instance variable
        this.age = age;    // Instance variable
        console.log(`Created person: ${name}`);
    }

    getName() {
        return this.name;
    }
}

// Creating objects calls constructor
const person1 = new Person('Alice', 30);  // Output: Created person: Alice
const person2 = new Person('Bob', 25);    // Output: Created person: Bob

console.log(person1.getName());  // Alice
console.log(person2.getName());  // Bob
```

---

## The `this` Keyword

`this` refers to the current instance. Be careful with arrow functions!

```javascript
class Counter {
    constructor() {
        this.count = 0;  // this.count belongs to this object
    }

    increment() {
        this.count++;  // Access this object's count
    }

    getCount() {
        return this.count;
    }

    // Arrow function preserves 'this' context
    incrementAsync() {
        setTimeout(() => {
            this.count++;  // 'this' still refers to Counter instance
        }, 1000);
    }
}

// Each object has its own count
const counter1 = new Counter();
const counter2 = new Counter();

counter1.increment();
counter1.increment();
counter2.increment();

console.log(counter1.getCount());  // 2
console.log(counter2.getCount());  // 1
```

---

## Instance Properties vs Static Properties

### Instance Properties
- Unique to each object
- Defined in constructor or as class fields

### Static Properties
- Shared by class, not instances
- Defined with `static` keyword

```javascript
class Employee {
    // Static properties (class level)
    static company = 'TechCorp';
    static employeeCount = 0;

    constructor(name, salary) {
        // Instance properties (unique per object)
        this.name = name;
        this.salary = salary;

        // Modify static property
        Employee.employeeCount++;
    }
}

// Creating objects
const emp1 = new Employee('Alice', 80000);
const emp2 = new Employee('Bob', 90000);

// Instance properties are different
console.log(emp1.name);  // Alice
console.log(emp2.name);  // Bob

// Static property is same for all (accessed via class)
console.log(Employee.company);      // TechCorp
console.log(Employee.employeeCount); // 2

// Changing static property affects all
Employee.company = 'NewCorp';
console.log(Employee.company);  // NewCorp
```

---

## Instance Methods

Methods that operate on instance data.

```javascript
class BankAccount {
    constructor(accountNumber, initialBalance = 0) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }

    deposit(amount) {
        if (amount > 0) {
            this.balance += amount;
            return true;
        }
        return false;
    }

    withdraw(amount) {
        if (amount > 0 && amount <= this.balance) {
            this.balance -= amount;
            return true;
        }
        return false;
    }

    getBalance() {
        return this.balance;
    }
}

// Usage
const account = new BankAccount('123456', 1000);
account.deposit(500);
account.withdraw(200);
console.log(account.getBalance());  // 1300
```

---

## Static Methods

Methods that belong to the class, not instances.

```javascript
class MathUtils {
    static add(a, b) {
        return a + b;
    }

    static isEven(number) {
        return number % 2 === 0;
    }

    static fahrenheitToCelsius(f) {
        return (f - 32) * 5 / 9;
    }
}

// Usage - no need to create object
console.log(MathUtils.add(5, 3));                   // 8
console.log(MathUtils.isEven(10));                   // true
console.log(MathUtils.fahrenheitToCelsius(98.6));    // 37
```

---

## String Representation

### toString() Method

```javascript
class Book {
    constructor(title, author) {
        this.title = title;
        this.author = author;
    }

    toString() {
        return `"${this.title}" by ${this.author}`;
    }
}

const book = new Book('1984', 'George Orwell');
console.log(book.toString());  // "1984" by George Orwell
console.log(`Book: ${book}`);  // Implicitly calls toString()
```

### Custom Inspect (Node.js)

```javascript
class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    toString() {
        return `(${this.x}, ${this.y})`;
    }

    // For console.log() in Node.js
    [Symbol.for('nodejs.util.inspect.custom')]() {
        return `Point { x: ${this.x}, y: ${this.y} }`;
    }
}

const point = new Point(3, 4);
console.log(point.toString());  // (3, 4)
console.log(point);             // Point { x: 3, y: 4 } (in Node.js)
```

---

## Real-World Example: Movie Class

```javascript
class Movie {
    // Static property
    static totalMovies = 0;

    constructor(movieId, title, genre, duration, releaseDate) {
        // Instance properties
        this.movieId = movieId;
        this.title = title;
        this.genre = genre;
        this.duration = duration; // minutes
        this.releaseDate = releaseDate;
        this.ratings = [];

        // Update static property
        Movie.totalMovies++;
    }

    // Instance method - Add rating
    addRating(rating) {
        if (rating >= 1 && rating <= 5) {
            this.ratings.push(rating);
            return true;
        }
        return false;
    }

    // Instance method - Get average rating
    getAverageRating() {
        if (this.ratings.length === 0) {
            return 0.0;
        }
        const sum = this.ratings.reduce((acc, r) => acc + r, 0);
        return sum / this.ratings.length;
    }

    // Instance method - Check if recently released
    isRecentlyReleased(days = 30) {
        const today = new Date();
        const daysSinceRelease = Math.floor(
            (today - this.releaseDate) / (1000 * 60 * 60 * 24)
        );
        return daysSinceRelease <= days;
    }

    // toString method
    toString() {
        const avgRating = this.getAverageRating();
        return `${this.title} (${this.genre}) - ${avgRating.toFixed(1)}★`;
    }

    // Custom inspect for Node.js
    [Symbol.for('nodejs.util.inspect.custom')]() {
        return `Movie(id=${this.movieId}, title='${this.title}')`;
    }

    // Static method
    static getTotalMovies() {
        return Movie.totalMovies;
    }
}

// Usage
const inception = new Movie(
    1,
    'Inception',
    'Sci-Fi',
    148,
    new Date(2010, 6, 16)  // Note: month is 0-indexed
);

inception.addRating(5);
inception.addRating(4);
inception.addRating(5);

console.log(inception.toString());  // Inception (Sci-Fi) - 4.7★
console.log(`Average: ${inception.getAverageRating().toFixed(2)}`);
console.log(`Recent: ${inception.isRecentlyReleased()}`);
console.log(`Total movies: ${Movie.getTotalMovies()}`);
```

---

## Private Fields (ES2022+)

Use `#` prefix for truly private fields.

```javascript
class BankAccount {
    // Private fields with #
    #accountNumber;
    #balance;

    constructor(accountNumber, initialBalance) {
        this.#accountNumber = accountNumber;
        this.#balance = initialBalance;
    }

    deposit(amount) {
        if (amount > 0) {
            this.#balance += amount;
            return true;
        }
        return false;
    }

    // Getter for balance
    get balance() {
        return this.#balance;
    }

    // Private method
    #logTransaction(type, amount) {
        console.log(`${type}: ${amount}`);
    }
}

const account = new BankAccount('123', 1000);
console.log(account.balance);  // 1000 (via getter)
// console.log(account.#balance);  // SyntaxError - private field
```

---

## Getters and Setters

```javascript
class Temperature {
    #celsius;

    constructor(celsius) {
        this.#celsius = celsius;
    }

    // Getter
    get celsius() {
        return this.#celsius;
    }

    // Setter with validation
    set celsius(value) {
        if (value < -273.15) {
            throw new Error('Below absolute zero!');
        }
        this.#celsius = value;
    }

    // Computed property
    get fahrenheit() {
        return this.#celsius * 9/5 + 32;
    }

    set fahrenheit(value) {
        this.celsius = (value - 32) * 5/9;
    }
}

const temp = new Temperature(25);
console.log(temp.celsius);      // 25
console.log(temp.fahrenheit);   // 77
temp.celsius = 30;              // Uses setter
console.log(temp.fahrenheit);   // 86
```

---

## Common Patterns

### 1. Builder Pattern with Method Chaining

```javascript
class QueryBuilder {
    constructor() {
        this.query = '';
    }

    select(fields) {
        this.query += `SELECT ${fields} `;
        return this;  // Return self for chaining
    }

    from(table) {
        this.query += `FROM ${table} `;
        return this;
    }

    where(condition) {
        this.query += `WHERE ${condition} `;
        return this;
    }

    build() {
        return this.query;
    }
}

// Method chaining
const query = new QueryBuilder()
    .select('name, age')
    .from('users')
    .where('age > 18')
    .build();

console.log(query);  // SELECT name, age FROM users WHERE age > 18
```

### 2. Singleton Pattern

```javascript
class Database {
    static #instance = null;

    constructor() {
        if (Database.#instance) {
            return Database.#instance;
        }
        console.log('Database connection initialized');
        Database.#instance = this;
    }

    static getInstance() {
        if (!Database.#instance) {
            Database.#instance = new Database();
        }
        return Database.#instance;
    }

    query(sql) {
        console.log(`Executing: ${sql}`);
    }
}

const db1 = Database.getInstance();
const db2 = Database.getInstance();
console.log(db1 === db2);  // true - same instance
```

---

## Prototype-Based Approach (Pre-ES6)

Before ES6, JavaScript used prototypes directly:

```javascript
// Constructor function
function Person(name, age) {
    this.name = name;
    this.age = age;
}

// Methods on prototype
Person.prototype.greet = function() {
    return `Hello, I'm ${this.name}`;
};

// Static property
Person.species = 'Homo sapiens';

// Creating instances
const person1 = new Person('Alice', 30);
const person2 = new Person('Bob', 25);

console.log(person1.greet());  // Hello, I'm Alice
console.log(Person.species);   // Homo sapiens
```

**Note:** ES6 classes are preferred for cleaner syntax.

---

## JavaScript-Specific Features

### 1. Class Expressions

```javascript
// Named class expression
const Person = class PersonClass {
    constructor(name) {
        this.name = name;
    }
};

// Anonymous class expression
const Animal = class {
    constructor(type) {
        this.type = type;
    }
};
```

### 2. Factory Functions (Alternative to Classes)

```javascript
function createPerson(name, age) {
    // Private variables (closure)
    let secret = 'private';

    // Return object with public interface
    return {
        name,
        age,
        greet() {
            return `Hello, I'm ${name}`;
        },
        getSecret() {
            return secret;  // Closure access
        }
    };
}

const person = createPerson('Alice', 30);
console.log(person.greet());  // Hello, I'm Alice
// person.secret is undefined - truly private
```

### 3. Object.create() Pattern

```javascript
const personPrototype = {
    greet() {
        return `Hello, I'm ${this.name}`;
    }
};

function createPerson(name, age) {
    const person = Object.create(personPrototype);
    person.name = name;
    person.age = age;
    return person;
}

const p = createPerson('Alice', 30);
console.log(p.greet());  // Hello, I'm Alice
```

---

## TypeScript Version (Typed)

TypeScript adds static typing to JavaScript classes:

```typescript
class Movie {
    static totalMovies: number = 0;

    private ratings: number[] = [];

    constructor(
        public movieId: number,
        public title: string,
        public genre: string,
        public duration: number,
        public releaseDate: Date
    ) {
        Movie.totalMovies++;
    }

    addRating(rating: number): boolean {
        if (rating >= 1 && rating <= 5) {
            this.ratings.push(rating);
            return true;
        }
        return false;
    }

    getAverageRating(): number {
        if (this.ratings.length === 0) {
            return 0.0;
        }
        const sum = this.ratings.reduce((acc, r) => acc + r, 0);
        return sum / this.ratings.length;
    }

    toString(): string {
        const avgRating = this.getAverageRating();
        return `${this.title} (${this.genre}) - ${avgRating.toFixed(1)}★`;
    }
}
```

---

## Key Takeaways

1. **Class** = Blueprint (syntactic sugar over prototypes)
2. `constructor()` initializes objects
3. `this` refers to current instance
4. **Instance properties** unique per object
5. **static properties/methods** belong to class
6. Use `#` for private fields (ES2022+)
7. Use getters/setters for controlled access
8. Implement `toString()` for readable output
9. Arrow functions preserve `this` context
10. Can mix classes with prototypes and closures

---

## Practice Exercises

1. Create a `Student` class with name, ID, and grades array
2. Add methods to add grade, calculate average, check if passing
3. Implement `toString()` method
4. Add static property to track total students
5. Add static method to get student count
6. Create version with private fields using `#`
7. Try implementing with factory function pattern

---

**Related Files:**
- [Python Implementation](./python.md)
- [Go Implementation](./go.md)
- [Java Implementation](./java.md)
- [Back to OOP Fundamentals](../README.md)
- [The Four Pillars of OOP](../four-pillars/)
