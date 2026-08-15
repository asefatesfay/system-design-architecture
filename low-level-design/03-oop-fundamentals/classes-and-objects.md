# Classes and Objects

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

## The `self` Parameter

`self` refers to the current instance of the class. It's how objects access their own attributes and methods.

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

## Instance Variables vs Class Variables

### Instance Variables
- Unique to each object
- Defined inside `__init__` with `self.`
- Different value for each instance

### Class Variables
- Shared by all instances
- Defined outside methods
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

## Instance Methods

Methods that operate on instance data.

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

## Class Methods

Methods that operate on class data, not instance data.

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

# Usage
emp1 = Employee("Alice")
emp2 = Employee("Bob")

print(Employee.get_employee_count())  # 2 - called on class
Employee.change_company_name("NewCorp")
print(Employee.company_name)  # NewCorp
```

## Static Methods

Methods that don't use instance or class data. They belong to the class namespace but act like regular functions.

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        """Static method - doesn't need self or cls"""
        return a + b

    @staticmethod
    def is_even(number):
        return number % 2 == 0

# Usage - no need to create object
print(MathUtils.add(5, 3))      # 8
print(MathUtils.is_even(10))    # True
```

## String Representation

### `__str__`: Human-readable string

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

## Real-World Example: Movie Class


### Multi-Language Implementation

<details open>
<summary><b>🐍 Python - Movie Class</b></summary>

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

</details>

<details>
<summary><b>🔷 Go - Movie Struct</b></summary>

```go
package main

import (
	"fmt"
	"time"
)

// Class variable equivalent (package-level)
var totalMovies int

// Movie struct (equivalent to class)
type Movie struct {
	MovieID     int
	Title       string
	Genre       string
	Duration    int // minutes
	ReleaseDate time.Time
	Ratings     []int
}

// Constructor function
func NewMovie(movieID int, title, genre string, duration int, releaseDate time.Time) *Movie {
	totalMovies++ // Update package-level "class" variable
	return &Movie{
		MovieID:     movieID,
		Title:       title,
		Genre:       genre,
		Duration:    duration,
		ReleaseDate: releaseDate,
		Ratings:     make([]int, 0),
	}
}

// Instance method - Add rating
func (m *Movie) AddRating(rating int) bool {
	if rating >= 1 && rating <= 5 {
		m.Ratings = append(m.Ratings, rating)
		return true
	}
	return false
}

// Instance method - Get average rating
func (m *Movie) GetAverageRating() float64 {
	if len(m.Ratings) == 0 {
		return 0.0
	}
	sum := 0
	for _, rating := range m.Ratings {
		sum += rating
	}
	return float64(sum) / float64(len(m.Ratings))
}

// Instance method - Check if recently released
func (m *Movie) IsRecentlyReleased(days int) bool {
	today := time.Now()
	daysSinceRelease := int(today.Sub(m.ReleaseDate).Hours() / 24)
	return daysSinceRelease <= days
}

// String method (equivalent to __str__)
func (m *Movie) String() string {
	avgRating := m.GetAverageRating()
	return fmt.Sprintf("%s (%s) - %.1f★", m.Title, m.Genre, avgRating)
}

// GoString method (equivalent to __repr__)
func (m *Movie) GoString() string {
	return fmt.Sprintf("Movie{id=%d, title='%s'}", m.MovieID, m.Title)
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

	fmt.Println(inception) // Inception (Sci-Fi) - 4.7★
	fmt.Printf("Average rating: %.2f\n", inception.GetAverageRating())
	fmt.Printf("Recently released: %v\n", inception.IsRecentlyReleased(30))
	fmt.Printf("Total movies in system: %d\n", totalMovies)
}
```

**Key Go Concepts:**
- Use `NewMovie()` constructor function
- `totalMovies` at package level (shared state)
- `String()` method for formatting
- Methods have receiver `(m *Movie)`

</details>

<details>
<summary><b>☕ Java - Movie Class</b></summary>

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

        // Update class variable
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

    // toString (equivalent to __str__)
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

        System.out.println(inception); // Inception (Sci-Fi) - 4.7★
        System.out.printf("Average rating: %.2f%n", inception.getAverageRating());
        System.out.printf("Recently released: %b%n", inception.isRecentlyReleased(30));
        System.out.printf("Total movies in system: %d%n", Movie.getTotalMovies());
    }
}
```

**Key Java Concepts:**
- `static` keyword for class variables
- Explicit getters/setters
- `@Override` for toString()
- `LocalDate` for date handling
- `List<Integer>` for typed collections

</details>

<details>
<summary><b>💛 JavaScript - Movie Class</b></summary>

**Modern ES6 Classes:**
```javascript
class Movie {
    // Class variable (static)
    static totalMovies = 0;

    constructor(movieId, title, genre, duration, releaseDate) {
        // Instance variables
        this.movieId = movieId;
        this.title = title;
        this.genre = genre;
        this.duration = duration; // minutes
        this.releaseDate = releaseDate;
        this.ratings = [];

        // Update class variable
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
        const sum = this.ratings.reduce((acc, rating) => acc + rating, 0);
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

    // toString (equivalent to __str__)
    toString() {
        const avgRating = this.getAverageRating();
        return `${this.title} (${this.genre}) - ${avgRating.toFixed(1)}★`;
    }

    // Custom inspect (Node.js equivalent to __repr__)
    [Symbol.for('nodejs.util.inspect.custom')]() {
        return `Movie(id=${this.movieId}, title='${this.title}')`;
    }

    // Static method to get total
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
    new Date(2010, 6, 16) // Note: month is 0-indexed in JS
);

inception.addRating(5);
inception.addRating(4);
inception.addRating(5);

console.log(inception.toString()); // Inception (Sci-Fi) - 4.7★
console.log(`Average rating: ${inception.getAverageRating().toFixed(2)}`);
console.log(`Recently released: ${inception.isRecentlyReleased()}`);
console.log(`Total movies in system: ${Movie.getTotalMovies()}`);
```

**TypeScript Version (with types):**
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

    isRecentlyReleased(days: number = 30): boolean {
        const today = new Date();
        const daysSinceRelease = Math.floor(
            (today.getTime() - this.releaseDate.getTime()) / (1000 * 60 * 60 * 24)
        );
        return daysSinceRelease <= days;
    }

    toString(): string {
        const avgRating = this.getAverageRating();
        return `${this.title} (${this.genre}) - ${avgRating.toFixed(1)}★`;
    }
}
```

**Key JavaScript Concepts:**
- `static` keyword for class variables
- `Date` object for date handling
- `reduce()` for array operations
- ES6 class syntax
- TypeScript adds type safety

</details>

---

### Language Comparison - Class Structure

| Feature | Python | Go | Java | JavaScript |
|---------|--------|-----|------|------------|
| **Class Definition** | `class Movie:` | `type Movie struct` | `public class Movie` | `class Movie` |
| **Constructor** | `__init__(self, ...)` | `NewMovie(...)` function | `public Movie(...)` | `constructor(...)` |
| **Instance Variables** | `self.title` | `m.Title` | `this.title` | `this.title` |
| **Class Variables** | `Movie.total_movies` | `totalMovies` (package-level) | `static totalMovies` | `static totalMovies` |
| **Methods** | `def method(self):` | `func (m *Movie) Method()` | `public returnType method()` | `method() { }` |
| **String Representation** | `__str__` | `String()` | `toString()` | `toString()` |
| **Date Handling** | `datetime` | `time.Time` | `LocalDate` | `Date` |


## Object Lifecycle

```python
class Resource:
    def __init__(self, name):
        self.name = name
        print(f"Resource {name} created")

    def __del__(self):
        """Destructor - called when object is destroyed"""
        print(f"Resource {name} destroyed")

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

## Key Takeaways

1. **Class** = Blueprint, **Object** = Instance
2. `__init__` initializes objects
3. `self` refers to current object
4. **Instance variables** are unique per object
5. **Class variables** are shared by all objects
6. Use `__str__` for human-readable output
7. Use `__repr__` for debugging
8. Methods define object behavior

## Practice Exercises

1. Create a `Student` class with name, ID, and grades list
2. Add methods to add grade, calculate average, and check if passing
3. Implement `__str__` and `__repr__`
4. Create multiple student objects and test them

---

**Next**: Learn about [The Four Pillars of OOP →](./four-pillars.md)
