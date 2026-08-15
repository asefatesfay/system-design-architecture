# LLD Interview Tips & Strategies

Complete guide to acing Low-Level Design interviews at top tech companies.

> **🌍 Language Preparation:** Choose your interview language wisely:
> - **Most recommended**: Python 🐍 (fastest to write, most interviewers know it)
> - **Systems roles**: Go 🔷 (clean concurrency)
> - **Enterprise/Amazon**: Java ☕ (what they expect)
> - **Full-stack/Web**: JavaScript 💛 (for web-focused roles)
>
> Resources:
> - [Choose Your Language](./lld-coding/multi-language/LANGUAGE-COMPARISON.md) - Detailed comparison
> - [Practice in All Languages](./COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md) - Side-by-side examples
> - [Four Pillars - Multi-Language](./03-oop-fundamentals/four-pillars/) - Core concepts in all 4

## Table of Contents

1. [Before the Interview](#before-the-interview)
2. [Interview Structure](#interview-structure)
3. [Step-by-Step Approach](#step-by-step-approach)
4. [Communication Tips](#communication-tips)
5. [Common Mistakes](#common-mistakes)
6. [Red Flags to Avoid](#red-flags-to-avoid)
7. [Company-Specific Tips](#company-specific-tips)
8. [Practice Schedule](#practice-schedule)

---

## Before the Interview

### Week Before

**Technical Preparation**:
- [ ] Review all SOLID principles with examples
- [ ] Practice 3-5 LLD problems end-to-end
- [ ] Review 10 essential design patterns
- [ ] Practice drawing class diagrams quickly
- [ ] Review your previous projects for design examples

**Mental Preparation**:
- [ ] Research the company's tech stack
- [ ] Prepare questions to ask interviewer
- [ ] Plan your setup (if remote)
- [ ] Get good sleep

### Day Before

- [ ] Review SOLID principles (30 min)
- [ ] Quick review of Strategy and Observer patterns
- [ ] Solve one problem with timer (45 min)
- [ ] Relax and rest

### Morning Of

- [ ] Light review of notes (15 min)
- [ ] Test your setup (camera, mic, screen share)
- [ ] Have water nearby
- [ ] Arrive/login 10 minutes early

---

## Interview Structure

### Typical 45-60 Minute Interview

```
00-05 min: Introductions and problem statement
05-15 min: Requirements clarification
15-35 min: Core design and implementation
35-45 min: Extensions and discussion
45-60 min: Your questions to interviewer
```

### What Interviewers Evaluate

| Aspect | Weight | What They Look For |
|--------|--------|-------------------|
| **Problem Understanding** | 20% | Did you ask clarifying questions? |
| **Design Quality** | 30% | Clear classes, SOLID principles, patterns |
| **Code Quality** | 20% | Clean, readable, organized |
| **Communication** | 15% | Think out loud, explain decisions |
| **Extensibility** | 10% | Can design handle changes? |
| **Trade-offs** | 5% | Discuss alternatives and reasons |

---

## Step-by-Step Approach

### Phase 1: Clarify Requirements (10-15 minutes)

**Critical! Don't skip this!**

#### What to Ask

```
1. SCOPE
   - What are the core features?
   - What can we skip for now?
   - Any specific constraints?

2. SCALE
   - How many users?
   - How many transactions?
   - Performance requirements?

3. ENTITIES
   - What are the main objects?
   - What types/variations exist?
   - Any special rules?

4. BEHAVIOR
   - What operations are needed?
   - What workflows exist?
   - Any edge cases?

5. TECHNICAL
   - Thread safety needed?
   - Persistence required?
   - External integrations?
```

#### Example: Parking Lot

```
❌ BAD: "Okay, I'll design a parking lot"

✅ GOOD:
"Let me clarify a few things:

1. Vehicle Types:
   - What types of vehicles? (Cars, trucks, motorcycles?)
   - Any special vehicles like electric cars?

2. Parking Spots:
   - Different spot sizes?
   - Any reserved spots? (Handicapped, VIP?)
   - How many floors?

3. Pricing:
   - Hourly or flat rate?
   - Different rates for vehicle types?
   - Payment methods?

4. Behavior:
   - How do vehicles enter/exit?
   - What if parking is full?
   - Can spots be reserved?

5. Technical:
   - Should it be thread-safe?
   - Need to persist data?
   - Any admin functions?"
```

### Phase 2: Identify Core Entities (5 minutes)

List the main "nouns" in the problem.

```python
# Example: Movie Ticket Booking

# Core Entities:
# - Movie
# - Theater / Cinema
# - Screen
# - Seat
# - Show / Showtime
# - Booking / Ticket
# - Customer / User
# - Payment

# Write this list in comments first!
```

### Phase 3: Define Classes (15-20 minutes)

Start with basic structure, then add details.

**Order of Implementation**:
1. Enums and simple data classes
2. Core entity classes
3. Relationships between classes
4. Behavior/methods
5. Patterns and strategies

```python
# Step 1: Enums
class SeatType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    VIP = "VIP"

# Step 2: Simple classes
class Seat:
    def __init__(self, seat_id, seat_type):
        self.seat_id = seat_id
        self.seat_type = seat_type
        self.is_available = True

# Step 3: Add relationships
class Screen:
    def __init__(self):
        self.seats = []  # Screen HAS-A Seats

# Step 4: Add behavior
    def book_seat(self, seat_id):
        # Implementation
        pass

# Step 5: Add patterns (Strategy, etc.)
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, seat_type):
        pass
```

### Phase 4: Apply Design Principles (Throughout)

**As you design, call out SOLID principles**:

```python
# "I'm following Single Responsibility here"
class BookingService:  # Only handles bookings
    pass

class PaymentService:  # Only handles payments
    pass

# "This follows Open/Closed Principle"
class PaymentMethod(ABC):  # Easy to add new payment types
    pass

# "Using Strategy pattern for flexibility"
class PricingStrategy(ABC):
    pass
```

### Phase 5: Handle Extensions (5-10 minutes)

Common extension questions:
- "How would you add X feature?"
- "What if we need to support Y?"
- "How does this scale?"

```
Example Extensions:

Parking Lot:
- Multiple entry/exit gates
- Reserved parking
- Electric charging stations
- Mobile app integration

Vending Machine:
- Credit card payments
- Touch screen interface
- Remote monitoring
- Promotions/discounts
```

---

## Communication Tips

### Think Out Loud

```
❌ BAD: (Silent for 5 minutes, then starts coding)

✅ GOOD:
"Let me think about the entities... we'll need:
- A Vehicle class - this will be abstract since we have different types
- A ParkingSpot class - also abstract for different sizes
- A ParkingLot class to manage everything
- A Ticket class to track parking sessions

For the relationships, ParkingLot HAS-A Floors, and Floor HAS-A Spots.
This is composition because spots don't exist without the parking lot.

Let me start with..."
```

### Explain Decisions

```
❌ BAD: "I'll use the Strategy pattern"

✅ GOOD:
"I'll use the Strategy pattern here for payment methods because:
1. We have multiple payment types (card, cash, UPI)
2. The client needs to choose at runtime
3. It follows Open/Closed - we can add new payment methods easily
4. Each payment method has different validation logic"
```

### Ask for Feedback

```
"Does this approach make sense so far?"
"Would you like me to focus on any particular aspect?"
"Should I implement this method in detail or move forward?"
```

### Handle Uncertainty

```
❌ BAD: "I don't know"

✅ GOOD:
"I'm thinking between two approaches:
1. Using a queue for requests
2. Using a priority queue based on distance

I'd go with priority queue because it's more efficient for nearest-car dispatch.
What do you think?"
```

---

## Common Mistakes

### Mistake 1: Starting to Code Immediately

```
❌ Problem given → Immediately start writing classes

✅ Problem given → Clarify → List entities → Design → Code
```

### Mistake 2: Creating God Classes

```python
❌ BAD:
class ParkingLot:
    def park_vehicle(self): pass
    def process_payment(self): pass
    def send_notification(self): pass
    def generate_report(self): pass
    def manage_employees(self): pass
    # Does EVERYTHING!

✅ GOOD:
class ParkingLot:
    def park_vehicle(self): pass

class PaymentService:
    def process_payment(self): pass

class NotificationService:
    def send_notification(self): pass
```

### Mistake 3: Ignoring Edge Cases

```
❌ Only handles happy path

✅ Considers:
- What if parking is full?
- What if payment fails?
- What if ticket is lost?
- What if vehicle already parked?
```

### Mistake 4: Over-Engineering

```python
❌ BAD: Creating complex pattern hierarchies for simple problems

✅ GOOD: Start simple, add patterns only when needed
```

### Mistake 5: Not Using SOLID

```
❌ Never mentions design principles

✅ "I'm applying Single Responsibility here..."
   "This follows Open/Closed Principle..."
```

### Mistake 6: Poor Variable Names

```python
❌ BAD:
def calc(x, y):
    return x + y

✅ GOOD:
def calculate_total_price(base_price: float, tax: float) -> float:
    return base_price + tax
```

---

## Red Flags to Avoid

### 🚩 Silent Coding
**Problem**: Coding in silence for long periods
**Fix**: Narrate your thought process

### 🚩 Arguing with Interviewer
**Problem**: Defending a clearly flawed design
**Fix**: Be open to feedback, adapt

### 🚩 Jumping to Code
**Problem**: No clarification or design phase
**Fix**: Follow the structured approach

### 🚩 Memorized Solutions
**Problem**: Regurgitating exact solution without understanding
**Fix**: Adapt to specific requirements

### 🚩 Ignoring Feedback
**Problem**: Interviewer hints at issue, you ignore
**Fix**: Listen carefully to hints

### 🚩 No Trade-offs Discussion
**Problem**: "This is the only way"
**Fix**: "We could also... but I chose this because..."

---

## Company-Specific Tips

### Google
- **Focus**: Clean design, scalability, SOLID principles
- **Typical Problems**: Parking lot, library system, file system
- **Duration**: 45-60 minutes
- **Tip**: Be ready to discuss alternatives

### Amazon
- **Focus**: Working code, handling edge cases, SOLID
- **Typical Problems**: Vending machine, elevator, parking
- **Duration**: 45-60 minutes
- **Tip**: Show bias for action, work backwards from customer

### Meta (Facebook)
- **Focus**: Clean code, design patterns, extensibility
- **Typical Problems**: News feed, notification system, chat
- **Duration**: 45 minutes
- **Tip**: Think about scale from the start

### Microsoft
- **Focus**: Design patterns, OOP principles, completeness
- **Typical Problems**: Parking lot, ATM, calendar
- **Duration**: 45-60 minutes
- **Tip**: Be thorough, discuss testing

### Indian Startups (Flipkart, Swiggy, CRED, etc.)
- **Focus**: Working code, machine coding, speed
- **Typical Problems**: Splitwise, cab booking, food delivery
- **Duration**: 90-120 minutes (machine coding)
- **Tip**: Actually implement, not just pseudocode

---

## Practice Schedule

### 4 Weeks Before Interview

**Week 1: Foundations**
- Day 1-2: Review OOP pillars
- Day 3-5: Master SOLID principles
- Day 6-7: Practice 2 problems

**Week 2: Patterns**
- Day 1-3: Learn 10 essential patterns
- Day 4-5: Identify patterns in existing code
- Day 6-7: Practice 2 problems using patterns

**Week 3: Practice**
- Day 1: Parking Lot (45 min)
- Day 2: Vending Machine (45 min)
- Day 3: Elevator System (60 min)
- Day 4: LRU Cache (45 min)
- Day 5: Library System (45 min)
- Day 6-7: Review and refactor solutions

**Week 4: Mock Interviews**
- Day 1: Mock interview #1
- Day 2: Review and improve
- Day 3: Mock interview #2
- Day 4: Review weak areas
- Day 5: Quick problem (30 min)
- Day 6: Review SOLID, patterns
- Day 7: Rest!

### Daily Practice Routine

```
30-Minute Session:
- 5 min: Review one SOLID principle
- 20 min: Code a small problem
- 5 min: Reflect and note learnings

60-Minute Session:
- 10 min: Clarify problem
- 35 min: Design and code
- 10 min: Review and refactor
- 5 min: Write learnings
```

---

## Interview Day Checklist

### 1 Hour Before

- [ ] Review SOLID principles (5 min each)
- [ ] Practice explaining one design pattern
- [ ] Sketch parking lot class diagram (10 min)
- [ ] Deep breathing exercises
- [ ] Bathroom break!

### Setup Check (Remote)

- [ ] Camera working and positioned well
- [ ] Microphone tested
- [ ] Screen sharing tested
- [ ] Stable internet connection
- [ ] Phone on silent
- [ ] Water bottle nearby
- [ ] Notes and pen ready
- [ ] IDE/editor open and configured

### During Interview

**First 5 Minutes**:
- [ ] Listen carefully to problem
- [ ] Take notes on requirements
- [ ] Ask for time to think

**Clarification Phase (10 min)**:
- [ ] Ask about entities and types
- [ ] Clarify constraints
- [ ] Confirm assumptions
- [ ] Write down key points

**Design Phase (30 min)**:
- [ ] List core entities
- [ ] Think out loud
- [ ] Start simple
- [ ] Apply SOLID principles
- [ ] Use design patterns when appropriate
- [ ] Handle edge cases

**Extension Phase (10 min)**:
- [ ] Show how design is extensible
- [ ] Discuss trade-offs
- [ ] Mention alternatives

**Closing (5 min)**:
- [ ] Summarize your design
- [ ] Ask questions about team/role
- [ ] Thank the interviewer

---

## Sample Self-Introduction

```
"Hi, I'm [Name]. I have [X years] of experience in [domain].
I've worked extensively with [languages/technologies] and
have designed several systems including [brief example].

I'm particularly interested in clean code and design patterns.
Recently, I've been focusing on [relevant tech/concept].

I'm excited to work through this design problem today!"
```

Keep it under 1 minute!

---

## Questions to Ask Interviewer

**About the Problem**:
- "Are there any constraints I should be aware of?"
- "What's the priority - correctness or completeness?"
- "Should I focus on any particular aspect?"

**About the Role**:
- "What does a typical day look like?"
- "What's the team working on currently?"
- "How does the team approach design decisions?"
- "What's the tech stack?"

**About Growth**:
- "What learning opportunities exist?"
- "How does the team stay updated with new technologies?"
- "What's the code review process like?"

---

## Final Tips

### The Night Before
- ✅ Review your notes
- ✅ Get 8 hours of sleep
- ✅ Prepare your setup
- ❌ Don't cram new topics

### Mental Preparation
- **Confidence**: You've practiced, you're ready
- **Curiosity**: Think of it as a design discussion
- **Flexibility**: Be ready to adapt your approach
- **Positivity**: Believe in yourself!

### During the Interview
- **Breathe**: Take a moment to think
- **Clarify**: Never assume
- **Communicate**: Think out loud
- **Adapt**: Listen to hints
- **Learn**: Even if stuck, show learning ability

### Remember
1. **Perfect solutions don't exist** - Show trade-offs
2. **Communication matters** - Think out loud
3. **SOLID is key** - Reference it often
4. **Simplicity wins** - Start simple, extend later
5. **You got this!** 💪

---

## Emergency Recovery

### If You're Stuck

```
1. Pause and breathe (5 seconds)
2. Summarize what you know
3. Break problem into smaller parts
4. Ask for a hint
5. Try a simpler version first
```

### If You Made a Mistake

```
"Actually, I realize there's an issue with this approach.
The problem is [explain]. Instead, I should [better approach]."
```

Interviewers appreciate self-correction!

### If Running Out of Time

```
"I have 10 minutes left. Should I:
A) Finish implementing this class
B) Sketch out the remaining classes
C) Discuss extensions

What would be most valuable?"
```

---

**Good luck with your interviews! 🚀**

Remember: Every interview is a learning opportunity. Even if it doesn't go perfectly, you'll gain valuable experience.

You've got this! 💪
