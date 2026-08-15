# Classes and Objects - Python

Complete guide to classes and objects in Python with Python-specific features.

## What is a Class?

A **class** is a blueprint or template for creating objects. It defines:
- **Attributes** (data/properties)
- **Methods** (behavior/functions)

Think of a class as a cookie cutter, and objects as the cookies made from it.

## What is an Object?

An **object** is an instance of a class. It's a concrete entity created from the class blueprint.

```python
# Class = Blueprint
class Dog:
    pass

# Objects = Instances
dog1 = Dog()  # First dog object
dog2 = Dog()  # Second dog object
dog3 = Dog()  # Third dog object

# Each object is unique
print(dog1 is dog2)  # False - different objects
```

---

## Basic Class Structure

```python
class ClassName:
    """Class docstring - describes what the class does"""

    # Class variables (shared by all instances)
    species = "Homo sapiens"

    def __init__(self, parameters):
        """Constructor - initializes new objects"""
        # Instance variables (unique per object)
        self.attribute = parameters

    def method_name(self):
        """Instance method - behavior"""
        # Do something
        pass
```

---

## The Constructor: `__init__`

The constructor is a special method called when creating a new object.

```python
class Person:
    def __init__(self, name, age):
        """Initialize a new Person object"""
        self.name = name  # Instance variable
        self.age = age    # Instance variable
        print(f"Created person: {name}")

# Creating objects calls __init__
person1 = Person("Alice", 30)  # Output: Created person: Alice
person2 = Person("Bob", 25)    # Output: Created person: Bob

print(person1.name)  # Alice
print(person2.name)  # Bob
```

---

## The `self` Parameter

`self` refers to the current instance of the class. It's how objects access their own attributes and methods.

**Why `self`?**
- Python needs explicit reference to instance
- Other languages use implicit `this`
- Must be first parameter of instance methods

```python
class Counter:
    def __init__(self):
        self.count = 0  # self.count belongs to THIS object

    def increment(self):
        self.count += 1  # Access THIS object's count

    def get_count(self):
        return self.count  # Return THIS object's count

# Each object has its own count
counter1 = Counter()
counter2 = Counter()

counter1.increment()
counter1.increment()
counter2.increment()

print(counter1.get_count())  # 2
print(counter2.get_count())  # 1 - separate object, separate count
```

---

## Instance Variables vs Class Variables

### Instance Variables
- Unique to each object
- Defined inside `__init__` with `self.`
- Different value for each instance

### Class Variables
- Shared by all instances
- Defined outside methods (at class level)
- Same value for all instances (unless overridden)

```python
class Employee:
    # Class variable - shared by ALL employees
    company = "TechCorp"
    employee_count = 0

    def __init__(self, name, salary):
        # Instance variables - unique per employee
        self.name = name
        self.salary = salary

        # Modify class variable
        Employee.employee_count += 1

# Creating objects
emp1 = Employee("Alice", 80000)
emp2 = Employee("Bob", 90000)

# Instance variables are different
print(emp1.name)    # Alice
print(emp2.name)    # Bob

# Class variable is same for all
print(emp1.company)  # TechCorp
print(emp2.company)  # TechCorp
print(Employee.employee_count)  # 2

# Changing class variable affects all
Employee.company = "NewCorp"
print(emp1.company)  # NewCorp
print(emp2.company)  # NewCorp
```

**Important:** If you assign to instance (`emp1.company = "X"`), it creates instance variable that shadows class variable!

```python
emp1.company = "OtherCorp"  # Creates instance variable
print(emp1.company)         # OtherCorp (instance variable)
print(emp2.company)         # NewCorp (class variable)
print(Employee.company)     # NewCorp (class variable)
```

---

## Instance Methods

Methods that operate on instance data. Must have `self` as first parameter.

```python
class BankAccount:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        """Add money to account"""
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        """Remove money from account"""
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def get_balance(self):
        """Return current balance"""
        return self.balance

# Usage
account = BankAccount("123456", 1000)
account.deposit(500)
account.withdraw(200)
print(account.get_balance())  # 1300
```

---

## Class Methods

Methods that operate on class data, not instance data. Use `@classmethod` decorator.

```python
class Employee:
    company_name = "TechCorp"
    employee_list = []

    def __init__(self, name):
        self.name = name
        Employee.employee_list.append(name)

    @classmethod
    def get_employee_count(cls):
        """Class method - operates on class data"""
        return len(cls.employee_list)

    @classmethod
    def change_company_name(cls, new_name):
        """Class method - modifies class variable"""
        cls.company_name = new_name

    @classmethod
    def create_intern(cls, name):
        """Alternative constructor pattern"""
        print(f"Creating intern: {name}")
        return cls(name)

# Usage
emp1 = Employee("Alice")
emp2 = Employee("Bob")

print(Employee.get_employee_count())  # 2 - called on class
Employee.change_company_name("NewCorp")
print(Employee.company_name)  # NewCorp

# Alternative constructor
intern = Employee.create_intern("Charlie")
```

**When to use:**
- Working with class-level data
- Alternative constructors
- Factory methods

---

## Static Methods

Methods that don't use instance or class data. Use `@staticmethod` decorator.

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        """Static method - doesn't need self or cls"""
        return a + b

    @staticmethod
    def is_even(number):
        return number % 2 == 0

    @staticmethod
    def fahrenheit_to_celsius(f):
        return (f - 32) * 5/9

# Usage - no need to create object
print(MathUtils.add(5, 3))      # 8
print(MathUtils.is_even(10))    # True
print(MathUtils.fahrenheit_to_celsius(98.6))  # 37.0
```

**When to use:**
- Utility functions logically related to class
- No need to access instance or class data
- Could be standalone function but belongs to class namespace

---

## String Representation

### `__str__`: Human-readable string

Used by `print()` and `str()`.

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        """Return human-readable string"""
        return f'"{self.title}" by {self.author}'

book = Book("1984", "George Orwell")
print(book)  # "1984" by George Orwell
print(str(book))  # "1984" by George Orwell
```

### `__repr__`: Developer-friendly representation

Used by `repr()` and in interactive shell.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        """Return unambiguous representation"""
        return f"Point(x={self.x}, y={self.y})"

    def __str__(self):
        """Return human-readable string"""
        return f"({self.x}, {self.y})"

point = Point(3, 4)
print(point)        # (3, 4) - uses __str__
print(repr(point))  # Point(x=3, y=4) - uses __repr__
print([point])      # [Point(x=3, y=4)] - lists use __repr__
```

**Rule of thumb:**
- `__str__`: For end users ("pretty")
- `__repr__`: For developers ("precise")
- If only one, implement `__repr__`

---

## Real-World Example: Movie Class

```python
from datetime import datetime

class Movie:
    """Represents a movie in a ticket booking system"""

    # Class variable
    total_movies = 0

    def __init__(self, movie_id, title, genre, duration, release_date):
        """Initialize a new movie"""
        # Instance variables
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.duration = duration  # in minutes
        self.release_date = release_date
        self.ratings = []

        # Update class variable
        Movie.total_movies += 1

    def add_rating(self, rating):
        """Add a user rating (1-5)"""
        if 1 <= rating <= 5:
            self.ratings.append(rating)
            return True
        return False

    def get_average_rating(self):
        """Calculate average rating"""
        if not self.ratings:
            return 0.0
        return sum(self.ratings) / len(self.ratings)

    def is_recently_released(self, days=30):
        """Check if movie was released in last N days"""
        today = datetime.now()
        days_since_release = (today - self.release_date).days
        return days_since_release <= days

    def __str__(self):
        """Human-readable representation"""
        avg_rating = self.get_average_rating()
        return f"{self.title} ({self.genre}) - {avg_rating:.1f}★"

    def __repr__(self):
        """Developer representation"""
        return f"Movie(id={self.movie_id}, title='{self.title}')"

# Usage
inception = Movie(
    movie_id=1,
    title="Inception",
    genre="Sci-Fi",
    duration=148,
    release_date=datetime(2010, 7, 16)
)

inception.add_rating(5)
inception.add_rating(4)
inception.add_rating(5)

print(inception)  # Inception (Sci-Fi) - 4.7★
print(f"Average rating: {inception.get_average_rating():.2f}")
print(f"Recently released: {inception.is_recently_released()}")
print(f"Total movies in system: {Movie.total_movies}")
```

---

## Object Lifecycle

```python
class Resource:
    def __init__(self, name):
        self.name = name
        print(f"Resource {name} created")

    def __del__(self):
        """Destructor - called when object is destroyed"""
        print(f"Resource {self.name} destroyed")

# Object creation
resource = Resource("Database Connection")

# Object usage
print(f"Using {resource.name}")

# Object destruction
del resource  # Explicitly delete

# Or let it go out of scope
def create_temp_resource():
    temp = Resource("Temporary")
    # temp is destroyed when function ends

create_temp_resource()
```

**Note:** `__del__` is unreliable for cleanup. Use context managers instead (`with` statement).

---

## Common Patterns

### 1. Builder Pattern with Method Chaining

```python
class QueryBuilder:
    def __init__(self):
        self.query = ""

    def select(self, fields):
        self.query += f"SELECT {fields} "
        return self  # Return self for chaining

    def from_table(self, table):
        self.query += f"FROM {table} "
        return self

    def where(self, condition):
        self.query += f"WHERE {condition} "
        return self

    def build(self):
        return self.query

# Usage with method chaining
query = (QueryBuilder()
         .select("name, age")
         .from_table("users")
         .where("age > 18")
         .build())

print(query)  # SELECT name, age FROM users WHERE age > 18
```

### 2. Object as Dictionary

```python
class Configuration:
    def __init__(self):
        self._config = {}

    def __getitem__(self, key):
        return self._config.get(key)

    def __setitem__(self, key, value):
        self._config[key] = value

    def __contains__(self, key):
        return key in self._config

# Usage like a dictionary
config = Configuration()
config["database"] = "PostgreSQL"
config["port"] = 5432

print(config["database"])  # PostgreSQL
print("port" in config)    # True
```

---

## Python-Specific Features

### 1. Properties with @property

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        """Getter for celsius"""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """Setter with validation"""
        if value < -273.15:
            raise ValueError("Below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self):
        """Computed property"""
        return self._celsius * 9/5 + 32

temp = Temperature(25)
print(temp.celsius)      # 25
print(temp.fahrenheit)   # 77.0
temp.celsius = 30        # Uses setter
```

### 2. Slots for Memory Optimization

```python
class Point:
    __slots__ = ['x', 'y']  # Only allow these attributes

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
# p.z = 3  # ❌ AttributeError - z not in __slots__
```

**Benefits:** Reduces memory usage, faster attribute access

### 3. Dataclasses (Python 3.7+)

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    def distance_from_origin(self):
        return (self.x**2 + self.y**2)**0.5

# Automatically gets __init__, __repr__, __eq__
p = Point(3, 4)
print(p)  # Point(x=3, y=4)
print(p.distance_from_origin())  # 5.0
```

---

## Key Takeaways

1. **Class** = Blueprint, **Object** = Instance
2. `__init__` initializes objects
3. `self` refers to current object (explicit in Python)
4. **Instance variables** are unique per object (`self.var`)
5. **Class variables** are shared by all objects
6. Use `@classmethod` for class-level operations
7. Use `@staticmethod` for utility functions
8. Implement `__str__` for users, `__repr__` for developers
9. Use `@property` for controlled attribute access
10. Consider `@dataclass` for data-holding classes

---

## Practice Exercises

1. Create a `Student` class with name, ID, and grades list
2. Add methods to add grade, calculate average, and check if passing
3. Implement `__str__` and `__repr__`
4. Add a class variable to track total number of students
5. Add a `@classmethod` to get student by ID
6. Create multiple student objects and test them

---

**Related Files:**
- [Go Implementation](./go.md)
- [Java Implementation](./java.md)
- [JavaScript Implementation](./javascript.md)
- [Back to OOP Fundamentals](../README.md)
- [The Four Pillars of OOP](../four-pillars/)
