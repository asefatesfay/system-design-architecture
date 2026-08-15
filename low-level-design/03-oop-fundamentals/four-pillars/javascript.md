# The Four Pillars of OOP - JavaScript

The four fundamental principles of Object-Oriented Programming in JavaScript with JavaScript-specific explanations.

## Overview

1. **Encapsulation** - Use closures, WeakMaps, and # private fields (ES2022+)
2. **Abstraction** - Define contracts with classes and throw errors for abstract methods
3. **Inheritance** - Extend classes with `extends` keyword
4. **Polymorphism** - Method overriding and duck typing

---

## 1. Encapsulation 🔒

### Definition
**Encapsulation** in JavaScript means controlling access to object internals using various techniques.

### Modern JavaScript: Private Fields (ES2022+)

```javascript
class BankAccount {
    // Private fields with # prefix
    #accountNumber;
    #balance;
    #transactionHistory;

    constructor(accountNumber, initialBalance) {
        this.#accountNumber = accountNumber;
        this.#balance = initialBalance;
        this.#transactionHistory = [];
    }

    // Public methods
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

    // Public getter
    get balance() {
        return this.#balance;
    }

    // Public setter with validation
    set balance(value) {
        if (value < 0) {
            throw new Error('Balance cannot be negative');
        }
        this.#balance = value;
    }

    // Private method
    #addTransaction(type, amount) {
        this.#transactionHistory.push({ type, amount });
    }

    // Protected-like method (convention with underscore)
    _calculateInterest() {
        return this.#balance * 0.03;
    }
}

// Usage
const account = new BankAccount('12345', 1000);
console.log(account.balance);  // ✓ 1000
account.deposit(500);          // ✓ Works
console.log(account.balance);  // ✓ 1500

// These don't work:
// console.log(account.#balance);  // ❌ SyntaxError
// account.#addTransaction(...);   // ❌ SyntaxError
```

### Closure-Based Encapsulation (Pre-ES2022)

```javascript
function createBankAccount(accountNumber, initialBalance) {
    // Private variables (closure)
    let balance = initialBalance;
    let transactionHistory = [];

    // Private function
    function addTransaction(type, amount) {
        transactionHistory.push({ type, amount });
    }

    // Return public API
    return {
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

// Usage
const account = createBankAccount('12345', 1000);
account.deposit(500);
console.log(account.getBalance());  // 1500
// balance is truly private - no way to access it directly
```

### JavaScript Concurrency: Async/Await and Locks

JavaScript is single-threaded but uses async operations. For coordination:

```javascript
class AsyncBankAccount {
    #balance;
    #mutex = Promise.resolve();  // Simple mutex using promise chain

    constructor(initialBalance) {
        this.#balance = initialBalance;
    }

    async deposit(amount) {
        // Queue operation on mutex
        return this.#mutex = this.#mutex.then(async () => {
            if (amount > 0) {
                await this.#simulateNetworkDelay();
                this.#balance += amount;
                return true;
            }
            return false;
        });
    }

    async withdraw(amount) {
        return this.#mutex = this.#mutex.then(async () => {
            if (amount > 0 && amount <= this.#balance) {
                await this.#simulateNetworkDelay();
                this.#balance -= amount;
                return true;
            }
            return false;
        });
    }

    async getBalance() {
        return this.#mutex.then(() => this.#balance);
    }

    async #simulateNetworkDelay() {
        return new Promise(resolve => setTimeout(resolve, 100));
    }
}

// Usage
const account = new AsyncBankAccount(1000);

// Multiple operations are queued and executed in order
Promise.all([
    account.deposit(100),
    account.withdraw(50),
    account.deposit(200)
]).then(() => {
    account.getBalance().then(balance => {
        console.log('Final balance:', balance);  // 1250
    });
});
```

### Third-Party Lock Library (async-mutex)

```javascript
// npm install async-mutex
import { Mutex } from 'async-mutex';

class ThreadSafeBankAccount {
    #balance;
    #mutex = new Mutex();

    constructor(initialBalance) {
        this.#balance = initialBalance;
    }

    async deposit(amount) {
        const release = await this.#mutex.acquire();
        try {
            if (amount > 0) {
                this.#balance += amount;
                return true;
            }
            return false;
        } finally {
            release();
        }
    }

    async withdraw(amount) {
        const release = await this.#mutex.acquire();
        try {
            if (amount > 0 && amount <= this.#balance) {
                this.#balance -= amount;
                return true;
            }
            return false;
        } finally {
            release();
        }
    }

    async getBalance() {
        const release = await this.#mutex.acquire();
        try {
            return this.#balance;
        } finally {
            release();
        }
    }
}
```

---

## 2. Abstraction 🎭

### Definition
**Abstraction** in JavaScript means defining base classes with methods that must be overridden.

### Abstract Class Pattern

```javascript
class PaymentProcessor {
    // Constructor checks that this is not instantiated directly
    constructor() {
        if (new.target === PaymentProcessor) {
            throw new Error('Cannot instantiate abstract class PaymentProcessor');
        }
    }

    // Abstract method - must be overridden
    processPayment(amount) {
        throw new Error('Method processPayment() must be implemented');
    }

    // Abstract method
    refund(transactionId) {
        throw new Error('Method refund() must be implemented');
    }

    // Concrete method - shared by all subclasses
    validateAmount(amount) {
        return amount > 0;
    }
}

class CreditCardProcessor extends PaymentProcessor {
    constructor(cardNumber) {
        super();
        this.cardNumber = cardNumber;
    }

    processPayment(amount) {
        if (!this.validateAmount(amount)) {
            throw new Error('Invalid amount');
        }
        console.log(`Processing $${amount} via credit card`);
        return `CC-${Date.now()}`;
    }

    refund(transactionId) {
        console.log(`Refunding transaction ${transactionId}`);
        return true;
    }
}

class PayPalProcessor extends PaymentProcessor {
    constructor(email) {
        super();
        this.email = email;
    }

    processPayment(amount) {
        if (!this.validateAmount(amount)) {
            throw new Error('Invalid amount');
        }
        console.log(`Processing $${amount} via PayPal`);
        return `PP-${Date.now()}`;
    }

    refund(transactionId) {
        console.log(`Refunding PayPal transaction ${transactionId}`);
        return true;
    }
}

// Usage
function checkout(processor, amount) {
    return processor.processPayment(amount);
}

const cc = new CreditCardProcessor('1234-5678');
const paypal = new PayPalProcessor('user@example.com');

checkout(cc, 100);      // Credit card
checkout(paypal, 200);  // PayPal

// Cannot instantiate abstract class
// const processor = new PaymentProcessor();  // ❌ Error
```

### Interface Pattern with Duck Typing

```javascript
// JavaScript uses duck typing - no formal interface needed
// But we can document expected interface

/**
 * @interface Vehicle
 * @method start()
 * @method stop()
 * @property {number} maxSpeed
 */

class Car {
    constructor() {
        this._maxSpeed = 120;
    }

    start() {
        console.log('Car engine started');
    }

    stop() {
        console.log('Car stopped');
    }

    get maxSpeed() {
        return this._maxSpeed;
    }
}

class Boat {
    constructor() {
        this._maxSpeed = 50;
    }

    start() {
        console.log('Boat engine started');
    }

    stop() {
        console.log('Boat stopped');
    }

    get maxSpeed() {
        return this._maxSpeed;
    }
}

// Function works with any object that has these methods
function startVehicle(vehicle) {
    vehicle.start();
    console.log(`Max speed: ${vehicle.maxSpeed}`);
}

startVehicle(new Car());   // Works
startVehicle(new Boat());  // Works
```

---

## 3. Inheritance 👨‍👩‍👧

### Definition
**Inheritance** in JavaScript allows classes to inherit from parent classes using `extends`.

### ES6 Class Inheritance

```javascript
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
}

class Dog extends Animal {
    constructor(name, age, breed) {
        super(name, age);  // Call parent constructor
        this.breed = breed;
    }

    bark() {
        console.log(`${this.name} says: Woof!`);
    }

    // Override parent method
    eat() {
        console.log(`${this.name} the ${this.breed} is eating dog food`);
    }
}

class Cat extends Animal {
    constructor(name, age, indoor) {
        super(name, age);
        this.indoor = indoor;
    }

    meow() {
        console.log(`${this.name} says: Meow!`);
    }
}

// Usage
const dog = new Dog('Buddy', 3, 'Golden Retriever');
const cat = new Cat('Whiskers', 2, true);

dog.eat();    // Overridden: "Buddy the Golden Retriever is eating dog food"
cat.eat();    // Inherited: "Whiskers is eating"
dog.sleep();  // Inherited: "Buddy is sleeping"
dog.bark();   // Dog-specific: "Buddy says: Woof!"
cat.meow();   // Cat-specific: "Whiskers says: Meow!"
```

### Prototype Chain (Pre-ES6 Way)

```javascript
// Constructor function
function Animal(name, age) {
    this.name = name;
    this.age = age;
}

Animal.prototype.eat = function() {
    console.log(this.name + ' is eating');
};

// Inheritance
function Dog(name, age, breed) {
    Animal.call(this, name, age);  // Call parent constructor
    this.breed = breed;
}

// Set up prototype chain
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

Dog.prototype.bark = function() {
    console.log(this.name + ' says: Woof!');
};

const dog = new Dog('Buddy', 3, 'Golden Retriever');
dog.eat();   // Inherited
dog.bark();  // Dog-specific
```

### Super Keyword

```javascript
class ElectricCar extends Car {
    constructor(name, age, breed, batteryLevel) {
        super(name, age, breed);  // Call parent constructor
        this.batteryLevel = batteryLevel;
    }

    eat() {
        super.eat();  // Call parent's eat() method
        console.log('Also charging battery...');
    }
}
```

---

## 4. Polymorphism 🦎

### Definition
**Polymorphism** in JavaScript is achieved through method overriding and duck typing.

### Duck Typing Polymorphism

```javascript
class Dog {
    speak() {
        return 'Woof!';
    }
}

class Cat {
    speak() {
        return 'Meow!';
    }
}

class Duck {
    speak() {
        return 'Quack!';
    }
}

// Works with ANY object that has speak() method
function makeItSpeak(animal) {
    console.log(animal.speak());
}

makeItSpeak(new Dog());   // Woof!
makeItSpeak(new Cat());   // Meow!
makeItSpeak(new Duck());  // Quack!
```

### Class-Based Polymorphism

```javascript
class Shape {
    constructor() {
        if (new.target === Shape) {
            throw new Error('Cannot instantiate abstract class Shape');
        }
    }

    area() {
        throw new Error('Method area() must be implemented');
    }

    perimeter() {
        throw new Error('Method perimeter() must be implemented');
    }
}

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

class Triangle extends Shape {
    constructor(a, b, c) {
        super();
        this.a = a;
        this.b = b;
        this.c = c;
    }

    area() {
        const s = (this.a + this.b + this.c) / 2;
        return Math.sqrt(s * (s - this.a) * (s - this.b) * (s - this.c));
    }

    perimeter() {
        return this.a + this.b + this.c;
    }
}

// Polymorphism - works with any Shape
function printShapeInfo(shape) {
    console.log(`Area: ${shape.area().toFixed(2)}`);
    console.log(`Perimeter: ${shape.perimeter().toFixed(2)}`);
}

// All work through same interface
const shapes = [
    new Circle(5),
    new Rectangle(4, 6),
    new Triangle(3, 4, 5)
];

shapes.forEach(shape => printShapeInfo(shape));
```

### Method Overriding

```javascript
class Vehicle {
    start() {
        console.log('Vehicle starting...');
    }
}

class Car extends Vehicle {
    start() {
        console.log('Car engine starting with key...');
    }
}

class ElectricCar extends Car {
    start() {
        console.log('Electric car silently powering on...');
        // Can still call parent method if needed:
        // super.start();
    }
}

// Same method name, different behavior
const vehicles = [new Vehicle(), new Car(), new ElectricCar()];

vehicles.forEach(v => v.start());
// Output:
// Vehicle starting...
// Car engine starting with key...
// Electric car silently powering on...
```

---

## JavaScript-Specific Concepts Summary

### 1. Private Fields (ES2022+)
```javascript
class Example {
    #privateField = 'hidden';  // Truly private with #
    _protectedField = 'convention';  // Convention only

    getPrivate() {
        return this.#privateField;
    }
}

const ex = new Example();
// ex.#privateField;  // ❌ SyntaxError
ex.getPrivate();      // ✓ Works
```

### 2. Getters and Setters
```javascript
class Temperature {
    #celsius;

    constructor(celsius) {
        this.#celsius = celsius;
    }

    get celsius() {
        return this.#celsius;
    }

    set celsius(value) {
        if (value < -273.15) {
            throw new Error('Below absolute zero!');
        }
        this.#celsius = value;
    }

    get fahrenheit() {
        return this.#celsius * 9/5 + 32;
    }
}

const temp = new Temperature(25);
console.log(temp.celsius);      // 25
console.log(temp.fahrenheit);   // 77
temp.celsius = 30;              // Uses setter
```

### 3. Async/Await and Promises

```javascript
class DataService {
    async fetchData(id) {
        try {
            const response = await fetch(`/api/data/${id}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }

    // Promise-based version
    fetchDataPromise(id) {
        return fetch(`/api/data/${id}`)
            .then(response => response.json())
            .catch(error => {
                console.error('Error:', error);
                throw error;
            });
    }
}
```

### 4. Web Workers for True Parallelism

```javascript
// main.js
class WorkerPool {
    constructor(workerScript, poolSize) {
        this.workers = [];
        for (let i = 0; i < poolSize; i++) {
            this.workers.push(new Worker(workerScript));
        }
        this.currentWorker = 0;
    }

    execute(task) {
        return new Promise((resolve, reject) => {
            const worker = this.workers[this.currentWorker];
            this.currentWorker = (this.currentWorker + 1) % this.workers.length;

            worker.onmessage = (e) => resolve(e.data);
            worker.onerror = (e) => reject(e);
            worker.postMessage(task);
        });
    }

    terminate() {
        this.workers.forEach(w => w.terminate());
    }
}

// worker.js
self.onmessage = function(e) {
    const result = processTask(e.data);
    self.postMessage(result);
};

function processTask(data) {
    // Heavy computation here
    return data * 2;
}
```

### 5. Event Emitters (Node.js)

```javascript
const EventEmitter = require('events');

class BankAccount extends EventEmitter {
    #balance;

    constructor(initialBalance) {
        super();
        this.#balance = initialBalance;
    }

    deposit(amount) {
        this.#balance += amount;
        this.emit('deposit', { amount, balance: this.#balance });
    }

    withdraw(amount) {
        if (amount <= this.#balance) {
            this.#balance -= amount;
            this.emit('withdraw', { amount, balance: this.#balance });
        }
    }
}

// Usage
const account = new BankAccount(1000);

account.on('deposit', (data) => {
    console.log(`Deposited ${data.amount}, balance: ${data.balance}`);
});

account.on('withdraw', (data) => {
    console.log(`Withdrew ${data.amount}, balance: ${data.balance}`);
});

account.deposit(500);
account.withdraw(200);
```

---

## Key Takeaways for JavaScript

✅ **Encapsulation**: Use # private fields (ES2022+) or closures
✅ **Abstraction**: Throw errors in base class methods that must be overridden
✅ **Inheritance**: Use `extends` keyword with `super()` for parent access
✅ **Polymorphism**: Duck typing + method overriding

✅ **Async**: Native Promises and async/await for asynchronous operations
✅ **Concurrency**: Single-threaded event loop, use Web Workers for parallelism
✅ **Flexible**: Dynamic typing, duck typing, prototype-based
✅ **Modern**: ES6+ classes, private fields, getters/setters

---

**Related Files:**
- [Python Implementation](./python.md)
- [Go Implementation](./go.md)
- [Java Implementation](./java.md)
- [Back to OOP Fundamentals](../README.md)
