# Class Relationships

Understanding how objects interact is crucial for good design. There are four main types of relationships in OOP.

## Overview of Relationships

| Relationship | Description | Lifetime | Example |
|--------------|-------------|----------|---------|
| **Association** | Objects work together | Independent | Teacher teaches Student |
| **Aggregation** | "Has-a" (loose) | Independent | Team has Players |
| **Composition** | "Part-of" (strong) | Dependent | Car has Engine |
| **Dependency** | Uses temporarily | Temporary | Method uses Calculator |

---

## 1. Association

**Definition:** Two objects are associated but remain independent. One object uses another but doesn't own it.

**Lifetime:** Objects can exist independently.

### Example: Teacher and Student

```python
class Student:
    def __init__(self, name):
        self.name = name

    def attend_class(self):
        print(f"{self.name} is attending class")

class Teacher:
    def __init__(self, name):
        self.name = name
        self.students = []  # Association: Teacher knows Students

    def add_student(self, student):
        self.students.append(student)

    def teach(self):
        print(f"{self.name} is teaching {len(self.students)} students")
        for student in self.students:
            student.attend_class()

# Students exist independently
alice = Student("Alice")
bob = Student("Bob")

# Teacher associates with students
teacher = Teacher("Prof. Smith")
teacher.add_student(alice)
teacher.add_student(bob)
teacher.teach()

# Students still exist if teacher is deleted
del teacher
print(alice.name)  # ✓ Alice still exists
```

### Bidirectional Association

```python
class Author:
    def __init__(self, name):
        self.name = name
        self.books = []

    def write_book(self, book):
        self.books.append(book)
        book.author = self  # Bidirectional

class Book:
    def __init__(self, title):
        self.title = title
        self.author = None

author = Author("J.K. Rowling")
book = Book("Harry Potter")
author.write_book(book)

print(f"{book.title} written by {book.author.name}")
print(f"{author.name} wrote {author.books[0].title}")
```

---

## 2. Aggregation (Shared Ownership)

**Definition:** "Has-a" relationship where the contained object can exist independently. **Weaker** than composition.

**Lifetime:** Parts can exist without the whole.

**Visual:** ◇─────> (hollow diamond)

### Example: Team and Players

```python
class Player:
    def __init__(self, name):
        self.name = name

    def play(self):
        print(f"{self.name} is playing")

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []  # Aggregation: Team HAS Players

    def add_player(self, player):
        self.players.append(player)

    def play_match(self):
        print(f"Team {self.name} is playing")
        for player in self.players:
            player.play()

# Players exist independently
player1 = Player("Alice")
player2 = Player("Bob")

# Team aggregates players
team = Team("Champions")
team.add_player(player1)
team.add_player(player2)
team.play_match()

# Players still exist if team is disbanded
del team
player1.play()  # ✓ Alice can still play
```

### Another Example: Library and Books

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

class Library:
    def __init__(self, name):
        self.name = name
        self.books = []  # Aggregation

    def add_book(self, book):
        self.books.append(book)

    def list_books(self):
        for book in self.books:
            print(f"- {book.title} by {book.author}")

# Books exist independently
book1 = Book("1984", "George Orwell")
book2 = Book("Brave New World", "Aldous Huxley")

# Library has books
library = Library("City Library")
library.add_book(book1)
library.add_book(book2)

# Books survive library closure
del library
print(book1.title)  # ✓ Book still exists
```

---

## 3. Composition (Exclusive Ownership)

**Definition:** "Part-of" relationship where the contained object cannot exist without the container. **Stronger** than aggregation.

**Lifetime:** Parts die with the whole.

**Visual:** ♦─────> (filled diamond)

### Example: Car and Engine

```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def start(self):
        print(f"Engine with {self.horsepower}hp started")

class Car:
    def __init__(self, brand, horsepower):
        self.brand = brand
        # Composition: Car OWNS Engine
        self.engine = Engine(horsepower)  # Created here!

    def start(self):
        print(f"{self.brand} car starting...")
        self.engine.start()

# Engine is created with Car
car = Car("Toyota", 200)
car.start()

# Engine doesn't exist separately
# You can't do: engine = Engine(200); car = Car("Toyota", engine)
# Engine dies when car is destroyed
del car
# engine no longer exists!
```

### Example: House and Rooms

```python
class Room:
    def __init__(self, name, area):
        self.name = name
        self.area = area

class House:
    def __init__(self, address):
        self.address = address
        # Composition: Rooms are part of the house
        self.rooms = [
            Room("Living Room", 200),
            Room("Bedroom", 150),
            Room("Kitchen", 100)
        ]

    def get_total_area(self):
        return sum(room.area for room in self.rooms)

house = House("123 Main St")
print(f"Total area: {house.get_total_area()} sq ft")

# Rooms don't exist without the house
del house
# All rooms are destroyed too!
```

### Example: Document and Paragraphs

```python
class Paragraph:
    def __init__(self, text):
        self.text = text

    def word_count(self):
        return len(self.text.split())

class Document:
    def __init__(self, title):
        self.title = title
        self.paragraphs = []  # Composition

    def add_paragraph(self, text):
        # Document creates and owns paragraphs
        paragraph = Paragraph(text)
        self.paragraphs.append(paragraph)

    def word_count(self):
        return sum(p.word_count() for p in self.paragraphs)

doc = Document("My Essay")
doc.add_paragraph("This is the first paragraph.")
doc.add_paragraph("This is the second paragraph.")
print(f"Total words: {doc.word_count()}")

# Paragraphs are destroyed with document
del doc
```

---

## 4. Dependency

**Definition:** One class temporarily uses another class. Weakest relationship.

**Lifetime:** Temporary usage, typically as method parameter.

**Visual:** -------> (dashed arrow)

### Example: Calculator as Parameter

```python
class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

class Report:
    def __init__(self, data):
        self.data = data

    def generate(self, calculator):
        """Dependency: Uses Calculator temporarily"""
        total = calculator.add(self.data[0], self.data[1])
        product = calculator.multiply(self.data[0], self.data[1])
        return f"Total: {total}, Product: {product}"

# Calculator used temporarily
calc = Calculator()
report = Report([10, 20])
result = report.generate(calc)  # Dependency here
print(result)
```

### Example: Email Sender

```python
class Email:
    def __init__(self, to, subject, body):
        self.to = to
        self.subject = subject
        self.body = body

class EmailSender:
    def send(self, email):
        print(f"Sending email to {email.to}")
        print(f"Subject: {email.subject}")
        print(f"Body: {email.body}")

class NotificationService:
    def notify_user(self, user_email, message):
        """Dependency: Temporarily uses EmailSender"""
        email = Email(user_email, "Notification", message)
        sender = EmailSender()  # Created temporarily
        sender.send(email)      # Used and discarded

service = NotificationService()
service.notify_user("alice@example.com", "Your order shipped!")
```

---

## 5. Aggregation vs Composition - Key Differences

| Feature | Aggregation | Composition |
|---------|-------------|-------------|
| **Relationship** | Has-a (weak) | Part-of (strong) |
| **Lifetime** | Independent | Dependent |
| **Creation** | Outside | Inside |
| **Deletion** | Survives | Dies together |
| **Example** | Team-Player | Car-Engine |

### Side-by-Side Example

```python
# AGGREGATION - Players exist independently
class Player:
    def __init__(self, name):
        self.name = name

class Team:
    def __init__(self):
        self.players = []

    def add_player(self, player):  # Player created outside
        self.players.append(player)

player = Player("Alice")  # Exists independently
team = Team()
team.add_player(player)   # Team uses existing player
del team
print(player.name)        # ✓ Player still exists


# COMPOSITION - Engine created with Car
class Engine:
    def __init__(self, hp):
        self.hp = hp

class Car:
    def __init__(self, hp):
        self.engine = Engine(hp)  # Created here!

car = Car(200)            # Engine created inside
del car                   # Engine destroyed too
```

---

## 6. Real-World Example: University System

```python
class Student:
    """Independent entity"""
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id

class Address:
    """Exists only as part of Building"""
    def __init__(self, street, city):
        self.street = street
        self.city = city

class Room:
    """Exists only as part of Building"""
    def __init__(self, room_number, capacity):
        self.room_number = room_number
        self.capacity = capacity

class Building:
    """Composition with Address and Rooms"""
    def __init__(self, name, street, city):
        self.name = name
        # Composition: Building owns Address
        self.address = Address(street, city)
        # Composition: Building owns Rooms
        self.rooms = []

    def add_room(self, room_number, capacity):
        room = Room(room_number, capacity)
        self.rooms.append(room)

class Department:
    """Association with Students, Composition with Building"""
    def __init__(self, name):
        self.name = name
        # Association: Students exist independently
        self.students = []
        # Composition: Department owns Building
        self.building = None

    def set_building(self, street, city):
        self.building = Building(f"{self.name} Building", street, city)

    def enroll_student(self, student):
        self.students.append(student)

# Students exist independently (Association)
alice = Student("Alice", "S001")
bob = Student("Bob", "S002")

# Department associates with students
cs_dept = Department("Computer Science")
cs_dept.enroll_student(alice)
cs_dept.enroll_student(bob)

# Building is composed in department
cs_dept.set_building("123 University Ave", "Tech City")
cs_dept.building.add_room("101", 30)
cs_dept.building.add_room("102", 40)

# Students survive department deletion
del cs_dept
print(alice.name)  # ✓ Alice still exists
# But building and rooms are destroyed!
```

---

## 7. Design Principles

### Favor Composition Over Inheritance

**Problem with Inheritance:**

```python
# BAD: Deep inheritance hierarchy
class Animal:
    def breathe(self): pass

class Mammal(Animal):
    def give_birth(self): pass

class Dog(Mammal):
    def bark(self): pass

class PoliceDog(Dog):
    def track(self): pass

# What if you need a RobotDog? Can't inherit from Dog!
```

**Better with Composition:**

```python
# GOOD: Composition for flexibility
class BreathingBehavior:
    def breathe(self):
        print("Breathing...")

class BarkingBehavior:
    def bark(self):
        print("Woof!")

class TrackingBehavior:
    def track(self):
        print("Tracking scent...")

class Dog:
    def __init__(self):
        self.breathing = BreathingBehavior()
        self.barking = BarkingBehavior()

class PoliceDog:
    def __init__(self):
        self.breathing = BreathingBehavior()
        self.barking = BarkingBehavior()
        self.tracking = TrackingBehavior()  # Additional behavior

class RobotDog:
    def __init__(self):
        # No breathing! Composition allows this
        self.barking = BarkingBehavior()

robot = RobotDog()
robot.barking.bark()  # Works without breathing!
```

---

## 8. Interview Tips

### Common Questions

**Q: "What's the difference between Aggregation and Composition?"**
- **Aggregation:** Parts can exist independently (Team-Player)
- **Composition:** Parts die with the whole (Car-Engine)

**Q: "When to use Composition vs Inheritance?"**
- **Composition:** When you need flexibility, mix behaviors
- **Inheritance:** When clear "is-a" relationship, shared interface

**Q: "How do you represent these in code?"**
- **Association:** References between independent objects
- **Aggregation:** Container holds references to existing objects
- **Composition:** Container creates and owns objects
- **Dependency:** Method parameter or local variable

### Best Practices

✅ **Prefer composition over inheritance** for flexibility
✅ **Use association** for independent objects that collaborate
✅ **Use composition** for parts that don't make sense alone
✅ **Use dependency** for temporary usage
✅ **Keep relationships simple** - avoid over-engineering

### Red Flags

❌ Deep inheritance hierarchies (>3 levels)
❌ Composition when aggregation would suffice
❌ Circular dependencies
❌ Tight coupling between unrelated classes

---

## Quick Reference

### Choosing the Right Relationship

```python
# Association: Independent collaboration
teacher.students.append(student)  # Student exists separately

# Aggregation: Has-a (weak)
team.add_player(player)  # Player created outside

# Composition: Part-of (strong)
car.engine = Engine(200)  # Engine created inside

# Dependency: Temporary use
def process(calculator):  # Calculator passed as parameter
    result = calculator.add(1, 2)
```

### Memory Diagram

```
Association:
Teacher ─────→ Student
  |              |
  exists      exists
  alone       alone

Aggregation:
Team ◇─────→ Player
  |            |
deleted    still
           exists

Composition:
Car ♦─────→ Engine
  |            |
deleted    deleted
           too!

Dependency:
Report ----→ Calculator
         (temporary)
```

---

**Previous:** [Access Modifiers ←](./access-modifiers.md)
**Back to:** [OOP Fundamentals](./README.md)
