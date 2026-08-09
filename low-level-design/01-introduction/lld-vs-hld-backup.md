# Low-Level Design vs High-Level Design

## Overview

Understanding the difference between Low-Level Design (LLD) and High-Level Design (HLD/System Design) is crucial for interviews and real-world software development.

## Quick Comparison

| Aspect | High-Level Design (HLD) | Low-Level Design (LLD) |
|--------|------------------------|------------------------|
| **Focus** | System architecture | Code structure |
| **Scope** | Entire system | Individual components |
| **Abstraction** | Very high | Moderate |
| **Concerns** | Scalability, availability, distribution | Maintainability, extensibility, readability |
| **Output** | Architecture diagrams, component diagrams | Class diagrams, code structure |
| **Time Scale** | Days to weeks of planning | Hours to days of design |

## High-Level Design (System Design)

### What It Covers

HLD focuses on the **bigger picture** of how a system works:

```
┌─────────────────────────────────────────────────────────┐
│                    System Design                        │
│                                                         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐   │
│  │   CDN    │      │  Load    │      │  Cache   │   │
│  │          │──────│ Balancer │──────│  Redis   │   │
│  └──────────┘      └──────────┘      └──────────┘   │
│                           │                           │
│                    ┌──────┴──────┐                   │
│              ┌─────▼─────┐  ┌────▼─────┐            │
│              │ Service A │  │ Service B │            │
│              └─────┬─────┘  └────┬─────┘            │
│                    │             │                    │
│              ┌─────▼─────────────▼─────┐            │
│              │    PostgreSQL DB        │            │
│              └─────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Key Questions in HLD

1. **Scalability**: How do we handle millions of users?
2. **Data Storage**: Which database should we use? SQL or NoSQL?
3. **Communication**: Should services use REST, gRPC, or message queues?
4. **Caching**: What should we cache and where?
5. **Load Balancing**: How do we distribute traffic?
6. **Failure Handling**: What happens if a service goes down?

### Example: Design Twitter

**HLD concerns:**
```
- How to handle 500M daily active users?
- How to store billions of tweets?
- How to implement the news feed efficiently?
- How to handle read-heavy vs write-heavy traffic?
- Which databases for tweets, users, relationships?
- How to implement notifications at scale?
- CDN strategy for images/videos
- Rate limiting approach
```

## Low-Level Design (LLD)

### What It Covers

LLD focuses on **implementation details** within a component:

```python
# LLD focuses on class structure and relationships

class Tweet:
    """Represents a single tweet"""
    def __init__(self, tweet_id, user_id, content, timestamp):
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.content = content
        self.timestamp = timestamp
        self.likes = []
        self.retweets = []

class User:
    """Represents a Twitter user"""
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.followers = []
        self.following = []
        self.tweets = []

    def post_tweet(self, content):
        tweet = Tweet(
            tweet_id=generate_id(),
            user_id=self.user_id,
            content=content,
            timestamp=datetime.now()
        )
        self.tweets.append(tweet)
        return tweet

class NewsFeedGenerator:
    """Generates personalized news feed"""
    def __init__(self, strategy):
        self.strategy = strategy

    def generate_feed(self, user):
        return self.strategy.create_feed(user)

class ChronologicalFeedStrategy:
    """Strategy for chronological feed"""
    def create_feed(self, user):
        # Implementation
        pass
```

### Key Questions in LLD

1. **Classes**: What classes should we create?
2. **Responsibilities**: What should each class do?
3. **Relationships**: How do objects interact?
4. **Interfaces**: What contracts should we define?
5. **Patterns**: Which design pattern fits best?
6. **Principles**: Are we following SOLID principles?

### Example: Design Twitter (LLD View)

**LLD concerns:**
```python
# What classes do we need?
- Tweet, User, Follow, Like, Retweet

# How should they interact?
- User posts Tweet
- User can follow/unfollow other Users
- Tweet can be liked and retweeted

# What interfaces?
- FeedGenerator interface
- NotificationService interface

# Which patterns?
- Strategy pattern for feed generation
- Observer pattern for notifications
- Factory pattern for creating different tweet types
```

## Side-by-Side Example

Let's design a **Movie Ticket Booking System**:

### HLD Perspective

```
┌────────────────────────────────────────────────────┐
│           Movie Booking System (HLD)               │
├────────────────────────────────────────────────────┤
│                                                    │
│  Client Apps ──► [API Gateway]                   │
│                        │                           │
│          ┌─────────────┼─────────────┐           │
│          ▼             ▼             ▼            │
│    [User Service] [Booking Service] [Payment]    │
│          │             │             │            │
│          ▼             ▼             ▼            │
│    [User DB]    [Booking DB]   [Payment DB]      │
│                                                    │
│  Cache: Redis for seat availability               │
│  Queue: RabbitMQ for booking confirmation         │
│  CDN: For movie posters and trailers              │
│                                                    │
└────────────────────────────────────────────────────┘

Questions:
- How to prevent double booking? (Use distributed locks)
- How to handle concurrent bookings? (Use Redis + optimistic locking)
- How to ensure payment consistency? (2-phase commit or saga pattern)
- How to scale for ticket releases? (Use queue system)
```

### LLD Perspective

```python
# Movie Booking System (LLD)

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

class SeatType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    VIP = "VIP"

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

# Core Entities
class Movie:
    def __init__(self, movie_id, title, duration, genre):
        self.movie_id = movie_id
        self.title = title
        self.duration = duration
        self.genre = genre

class Theater:
    def __init__(self, theater_id, name, location):
        self.theater_id = theater_id
        self.name = name
        self.location = location
        self.screens = []

class Screen:
    def __init__(self, screen_id, theater, total_seats):
        self.screen_id = screen_id
        self.theater = theater
        self.seats = self._initialize_seats(total_seats)

    def _initialize_seats(self, total_seats):
        # Create seat objects
        pass

class Seat:
    def __init__(self, seat_id, row, number, seat_type):
        self.seat_id = seat_id
        self.row = row
        self.number = number
        self.seat_type = seat_type
        self.is_available = True

class Show:
    def __init__(self, show_id, movie, screen, start_time):
        self.show_id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time

class Booking:
    def __init__(self, booking_id, user, show, seats):
        self.booking_id = booking_id
        self.user = user
        self.show = show
        self.seats = seats
        self.status = BookingStatus.PENDING
        self.created_at = datetime.now()

class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.bookings = []

# Payment Strategy Pattern
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount):
        # Process credit card payment
        print(f"Processing ${amount} via Credit Card")
        return True

class UPIPayment(PaymentStrategy):
    def process_payment(self, amount):
        # Process UPI payment
        print(f"Processing ${amount} via UPI")
        return True

# Service Layer
class BookingService:
    def __init__(self):
        self.bookings = {}

    def create_booking(self, user, show, seats, payment_strategy):
        # Check seat availability
        if not self._are_seats_available(show, seats):
            raise Exception("Seats not available")

        # Create booking
        booking = Booking(
            booking_id=self._generate_booking_id(),
            user=user,
            show=show,
            seats=seats
        )

        # Process payment
        total_amount = self._calculate_total(seats)
        if payment_strategy.process_payment(total_amount):
            booking.status = BookingStatus.CONFIRMED
            self._mark_seats_booked(seats)
            self.bookings[booking.booking_id] = booking
            return booking
        else:
            raise Exception("Payment failed")

    def _are_seats_available(self, show, seats):
        return all(seat.is_available for seat in seats)

    def _calculate_total(self, seats):
        # Calculate based on seat types
        pass

    def _mark_seats_booked(self, seats):
        for seat in seats:
            seat.is_available = False

    def _generate_booking_id(self):
        import uuid
        return str(uuid.uuid4())

# Usage
movie = Movie("m1", "Inception", 148, "Sci-Fi")
theater = Theater("t1", "PVR Cinemas", "Mumbai")
screen = Screen("s1", theater, 100)
show = Show("sh1", movie, screen, datetime.now())
user = User("u1", "John Doe", "john@example.com")

service = BookingService()
seats = [screen.seats[0], screen.seats[1]]  # Select seats
payment = CreditCardPayment()

booking = service.create_booking(user, show, seats, payment)
```

## When to Use Each

### Use HLD When:
- Designing a new system from scratch
- Deciding on technology stack
- Planning for scalability
- Architecting microservices
- System design interviews

### Use LLD When:
- Implementing a specific feature
- Refactoring existing code
- Designing class structure
- Applying design patterns
- Low-level design interviews

## Both Work Together

In real projects, you need both:

1. **Start with HLD**: Design the overall system architecture
2. **Then LLD**: Design each component's internal structure
3. **Iterate**: Refine both as you learn more

```
System Design (HLD)
        │
        ├── Component 1 ──► LLD Design ──► Classes, Interfaces
        ├── Component 2 ──► LLD Design ──► Classes, Interfaces
        └── Component 3 ──► LLD Design ──► Classes, Interfaces
```

## Interview Context

### System Design Interview (45-60 min)
- Draw architecture diagrams
- Discuss scalability, databases, caching
- Focus on trade-offs at system level
- Common for Senior+ roles

### LLD Interview (45-60 min for OOD, 90-120 min for machine coding)
- Write class definitions
- Discuss design patterns and SOLID principles
- Focus on code structure and maintainability
- Common for all levels, including entry-level

## Key Takeaways

1. **HLD** = System architecture and scalability
2. **LLD** = Class design and code structure
3. Both are essential for building great software
4. Different interview types test different skills
5. LLD is increasingly important even for junior roles

---

**Next**: Learn about the different [types of LLD interviews](../02-interview-types/object-oriented-design.md) you might encounter.
