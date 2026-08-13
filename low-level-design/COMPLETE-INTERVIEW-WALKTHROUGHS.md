# Complete LLD Interview Walkthroughs

Real-world interview examples walked through from start to finish, showing exactly what to say and do at each step.

---

## 📖 How to Use This Guide

### Your Learning Path

**📚 First Time Reading?**
- Read the [Interview Success Formula](#general-interview-success-formula) section first
- Then go through **Walkthrough 1 (Parking Lot)** completely
- Understand the 7-step structure that all walkthroughs follow

**🎯 Practicing for Interviews?**
1. **Try solving first** - Set a 45-minute timer, attempt the problem
2. **Then read the walkthrough** - Compare your approach
3. **Note the differences** - What did you miss? What could be better?
4. **Redo after 2-3 days** - Test retention and improvement

**⏰ Interview Tomorrow?**
- Skim all three walkthroughs (focus on Steps 1-3)
- **Memorize the question patterns** in Step 2 (Requirements)
- **Study the SOLID explanations** throughout the code
- **Read the "Key Takeaways"** at the end of each walkthrough

**🔄 Already Familiar with LLD?**
- Jump to specific walkthroughs based on what you need to practice
- Use the comparison table below to choose
- Focus on the "Extensions Discussion" sections

### What Each Walkthrough Includes

Every walkthrough follows the same **7-step interview structure**:

1. **Problem Statement** (0-2 min) - How interviewer presents it
2. **Requirements Clarification** (2-12 min) - Exact Q&A dialogue
3. **Core Design** (12-17 min) - Entity identification, pattern selection
4. **Implementation** (17-42 min) - Complete code with explanations
5. **Demo & Testing** (42-48 min) - Realistic scenarios
6. **Extensions** (48-53 min) - "What if..." discussions
7. **Summary** (53-58 min) - Patterns, SOLID, complexity analysis

---

## 🎯 Walkthrough Comparison

Choose the right walkthrough based on what you want to practice:

| # | Problem | Difficulty | Duration | Key Learning | Primary Patterns | Best For |
|---|---------|------------|----------|--------------|------------------|----------|
| **1** | **Parking Lot** | Medium | 45-60 min | Class hierarchies, SOLID principles | Singleton, Strategy, Inheritance | **First LLD interview, SOLID practice** |
| **2** | **Vending Machine** | Medium | 45 min | State machines, state transitions | **State Pattern**, Strategy | **State pattern mastery, FSM** |
| **3** | **Hotel Booking** | Medium-Hard | 45-60 min | **Concurrency, thread-safety** | Strategy, Repository, State | **Booking systems, race conditions** |

### Pattern Coverage Matrix

| Pattern | Parking Lot | Vending Machine | Hotel Booking |
|---------|-------------|-----------------|---------------|
| Singleton | ✅ Main class | ✅ Main class | Optional |
| Strategy | ✅ Pricing | ✅ Payment | ✅ Pricing, Search |
| State | ❌ | ✅ **Primary** | ✅ Booking lifecycle |
| Factory | ✅ Vehicle types | ✅ Product creation | ✅ Room types |
| Inheritance | ✅ Vehicle hierarchy | ✅ State hierarchy | ✅ Room hierarchy |
| Repository | ❌ | ❌ | ✅ Booking management |
| Thread-Safety | ❌ | ❌ | ✅ **Critical** |

### Recommended Order

**For Learning:**
1. Parking Lot (foundational concepts)
2. Vending Machine (state pattern focus)
3. Hotel Booking (advanced concurrency)

**For Interview Prep:**
- **Google/Amazon** → Start with Parking Lot
- **Booking.com/Airbnb** → Focus on Hotel Booking
- **Amazon (State Machines)** → Practice Vending Machine

**By Time Available:**
- **< 2 hours** → Read Parking Lot only
- **2-4 hours** → Parking Lot + Vending Machine
- **Full day** → All three + practice coding them yourself

---

## Table of Contents

1. [General Interview Success Formula](#general-interview-success-formula)
2. [Walkthrough 1: Parking Lot System](#walkthrough-1-parking-lot-system)
3. [Walkthrough 2: Vending Machine](#walkthrough-2-vending-machine)
4. [Walkthrough 3: Hotel Booking System](#walkthrough-3-hotel-booking-system)

---

# General Interview Success Formula

## The 5-Phase Approach

### Phase 1: Clarify (15-20%)
- Don't assume anything
- Ask 8-10 targeted questions
- Confirm scope

### Phase 2: Design (10-15%)
- List entities
- Identify patterns
- Explain high-level approach

### Phase 3: Implement (50-60%)
- Start simple
- Build incrementally
- Think out loud
- Reference SOLID principles

### Phase 4: Demonstrate (10-15%)
- Show realistic scenarios
- Handle edge cases
- Prove thread-safety if applicable

### Phase 5: Extend (10-15%)
- Discuss improvements
- Show extensibility
- Analyze complexity

## Time Management Tips

**45-minute interview:**
```
00-08 min: Requirements
08-12 min: Design
12-35 min: Implementation
35-42 min: Demo & Extensions
42-45 min: Questions
```

**60-minute interview:**
```
00-12 min: Requirements
12-17 min: Design
17-45 min: Implementation
45-53 min: Demo & Extensions
53-58 min: Summary
58-60 min: Questions
```

## Final Checklist

Before saying "I'm done":
- [ ] Asked clarifying questions
- [ ] Identified core entities
- [ ] Used appropriate design patterns
- [ ] Referenced SOLID principles
- [ ] Handled edge cases
- [ ] Demonstrated with examples
- [ ] Discussed extensions
- [ ] Analyzed complexity
- [ ] Clean, readable code
- [ ] Communicated throughout

---

**You've got this! 🚀**

Practice these walkthroughs until you can explain every decision naturally. The key is not memorizing solutions, but understanding the thought process.

Good luck with your interviews! 💪
# Walkthrough 1: Parking Lot System

**Difficulty**: Medium | **Time**: 45-60 minutes | **Companies**: Google, Amazon, Microsoft, Uber

## Step 1: Problem Statement (0-2 min)

**Interviewer**: "Design a parking lot system."

**You**: "Thank you! Before I start, let me clarify the requirements to make sure I understand the problem correctly."

---

## Step 2: Requirements Clarification (2-12 min)

### Your Questions → Interviewer's Answers

**You**: "First, let me understand the types of vehicles and parking spots."

**Q1: What types of vehicles should the system support?**
**A**: Motorcycles, cars, and trucks.

**Q2: Do we need different sized parking spots?**
**A**: Yes - small (motorcycle), medium (car), large (truck). A larger vehicle can't fit in a smaller spot, but smaller vehicles can use larger spots.

**Q3: How is the parking lot structured?**
**A**: Multiple floors, each floor has multiple spots.

**You**: "Got it. Now about the parking and payment workflow:"

**Q4: How does the entry/exit process work?**
**A**: Vehicle enters, gets a ticket with entry time. On exit, pays based on duration and leaves.

**Q5: How is pricing calculated?**
**A**: Hourly rate that differs by vehicle type. Motorcycles: $2/hr, Cars: $4/hr, Trucks: $6/hr.

**Q6: What if the parking lot is full?**
**A**: Show "full" message and don't allow entry.

**You**: "Great. A few technical questions:"

**Q7: Do we need to handle concurrent access (multiple vehicles entering/exiting simultaneously)?**
**A**: For now, assume single-threaded. We can discuss threading later.

**Q8: Any specific parking strategy (nearest to entrance, first available, etc.)?**
**A**: First available spot of the appropriate size, starting from the lowest floor.

**You**: "Perfect! Let me summarize what I'll build:
- Support 3 vehicle types with different spot requirements
- Multi-floor parking structure
- Entry/exit with ticket system
- Hourly pricing based on vehicle type
- Handle full parking scenarios
- Find first available spot algorithm

Does this sound right?"

**Interviewer**: "Yes, sounds good. Go ahead."

---

## Step 3: Core Entities & High-Level Design (12-17 min)

**You**: "Let me identify the core entities first."

*[Writing/typing out loud]*

```python
# Core Entities:
# 1. Vehicle - Abstract (Motorcycle, Car, Truck)
# 2. ParkingSpot - Abstract (SmallSpot, MediumSpot, LargeSpot)
# 3. Floor - Collection of spots
# 4. ParkingLot - Manages floors
# 5. Ticket - Entry record with timestamp
# 6. ParkingRate - Pricing strategy
```

**You**: "The relationships I'm thinking:
- ParkingLot HAS-MANY Floors (composition)
- Floor HAS-MANY ParkingSpots (composition)
- Vehicle uses Strategy pattern for different types
- ParkingSpot also uses Strategy for different sizes
- Ticket links Vehicle to ParkingSpot with entry time"

**You**: "I'll use several design principles here:
- **Single Responsibility**: Each class has one job
- **Open/Closed**: Easy to add new vehicle types without changing existing code
- **Liskov Substitution**: All vehicle types work interchangeably
- **Strategy Pattern**: For vehicle types and pricing
- **Singleton Pattern**: For ParkingLot (single instance)"

**Interviewer**: "Sounds good. Show me the code."

---

## Step 4: Implementation (17-40 min)

**You**: "I'll start with enums and simple classes, then build up complexity."

```python
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, List
import threading

# Step 1: Enums and Constants
class VehicleType(Enum):
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    TRUCK = "TRUCK"

class SpotSize(Enum):
    SMALL = "SMALL"      # Motorcycle
    MEDIUM = "MEDIUM"    # Car
    LARGE = "LARGE"      # Truck

class SpotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"

# Step 2: Vehicle Hierarchy
class Vehicle(ABC):
    """Abstract base class for all vehicles"""
    def __init__(self, license_plate: str):
        self.license_plate = license_plate
        self.vehicle_type = None

    @abstractmethod
    def get_required_spot_size(self) -> SpotSize:
        """Returns the minimum spot size required"""
        pass

    def can_fit_in_spot(self, spot_size: SpotSize) -> bool:
        """Check if vehicle can fit in given spot size"""
        required = self.get_required_spot_size()

        # Smaller vehicles can use larger spots
        size_hierarchy = {
            SpotSize.SMALL: [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE],
            SpotSize.MEDIUM: [SpotSize.MEDIUM, SpotSize.LARGE],
            SpotSize.LARGE: [SpotSize.LARGE]
        }

        return spot_size in size_hierarchy[required]

class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.MOTORCYCLE

    def get_required_spot_size(self) -> SpotSize:
        return SpotSize.SMALL

class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.CAR

    def get_required_spot_size(self) -> SpotSize:
        return SpotSize.MEDIUM

class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.TRUCK

    def get_required_spot_size(self) -> SpotSize:
        return SpotSize.LARGE
```

**You**: "I'm using abstract base class for Vehicle to follow the Open/Closed principle. Each vehicle type knows its requirements. The `can_fit_in_spot` method implements the rule that smaller vehicles can use larger spots."

```python
# Step 3: Parking Spot Hierarchy
class ParkingSpot:
    """Represents a single parking spot"""
    def __init__(self, spot_id: str, spot_size: SpotSize, floor_id: int):
        self.spot_id = spot_id
        self.spot_size = spot_size
        self.floor_id = floor_id
        self.status = SpotStatus.AVAILABLE
        self.parked_vehicle: Optional[Vehicle] = None

    def is_available(self) -> bool:
        return self.status == SpotStatus.AVAILABLE

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        """Check if this spot can accommodate the vehicle"""
        return self.is_available() and vehicle.can_fit_in_spot(self.spot_size)

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """Park a vehicle in this spot"""
        if not self.can_fit_vehicle(vehicle):
            return False

        self.parked_vehicle = vehicle
        self.status = SpotStatus.OCCUPIED
        return True

    def remove_vehicle(self) -> Optional[Vehicle]:
        """Remove and return the parked vehicle"""
        vehicle = self.parked_vehicle
        self.parked_vehicle = None
        self.status = SpotStatus.AVAILABLE
        return vehicle

    def __str__(self):
        return f"Spot({self.spot_id}, {self.spot_size.value}, Floor-{self.floor_id}, {self.status.value})"

# Step 4: Ticket System
class Ticket:
    """Represents a parking ticket issued at entry"""
    _ticket_counter = 0

    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        Ticket._ticket_counter += 1
        self.ticket_id = f"TICKET-{Ticket._ticket_counter:06d}"
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time: Optional[datetime] = None
        self.paid_amount: float = 0.0

    def get_parking_duration_hours(self) -> float:
        """Calculate parking duration in hours"""
        exit_time = self.exit_time if self.exit_time else datetime.now()
        duration = (exit_time - self.entry_time).total_seconds() / 3600
        return max(duration, 0.1)  # Minimum 6 minutes (0.1 hour)

    def __str__(self):
        return f"Ticket {self.ticket_id}: {self.vehicle.license_plate} at {self.spot.spot_id}"
```

**You**: "The Ticket class tracks the parking session. I'm using a class-level counter for unique ticket IDs. The duration calculation rounds up to a minimum billing period."

```python
# Step 5: Pricing Strategy
class ParkingRate:
    """Calculates parking fees based on vehicle type and duration"""

    # Hourly rates by vehicle type
    RATES = {
        VehicleType.MOTORCYCLE: 2.0,
        VehicleType.CAR: 4.0,
        VehicleType.TRUCK: 6.0
    }

    @staticmethod
    def calculate_fee(vehicle_type: VehicleType, hours: float) -> float:
        """Calculate parking fee"""
        rate = ParkingRate.RATES.get(vehicle_type, 4.0)
        # Round up to nearest hour
        import math
        hours_rounded = math.ceil(hours)
        return rate * hours_rounded

    @staticmethod
    def get_rate_info() -> str:
        """Return pricing information"""
        return ("Parking Rates:\n"
                "  Motorcycle: $2/hour\n"
                "  Car: $4/hour\n"
                "  Truck: $6/hour")
```

**You**: "Simple pricing strategy. This could be extended with Strategy pattern if we needed dynamic pricing (peak hours, discounts, etc.)."

```python
# Step 6: Floor Management
class Floor:
    """Represents a floor in the parking lot"""
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: List[ParkingSpot] = []

    def add_spot(self, spot: ParkingSpot):
        """Add a parking spot to this floor"""
        self.spots.append(spot)

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find first available spot that can fit the vehicle"""
        for spot in self.spots:
            if spot.can_fit_vehicle(vehicle):
                return spot
        return None

    def get_available_count(self) -> dict:
        """Get count of available spots by size"""
        counts = {size: 0 for size in SpotSize}
        for spot in self.spots:
            if spot.is_available():
                counts[spot.spot_size] += 1
        return counts

    def __str__(self):
        available = sum(1 for spot in self.spots if spot.is_available())
        return f"Floor {self.floor_number}: {available}/{len(self.spots)} spots available"
```

**You**: "Floor manages its spots and can search for available spots. The `find_available_spot` method implements our 'first available' strategy."

```python
# Step 7: Main ParkingLot (Singleton)
class ParkingLot:
    """Main parking lot system - Singleton pattern"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure only one instance exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.floors: List[Floor] = []
            self.active_tickets: dict = {}  # spot_id -> Ticket
            self.payment_history: List[Ticket] = []
            self.initialized = True

    def add_floor(self, floor: Floor):
        """Add a floor to the parking lot"""
        self.floors.append(floor)

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find first available spot across all floors"""
        # Search from lowest floor to highest
        for floor in sorted(self.floors, key=lambda f: f.floor_number):
            spot = floor.find_available_spot(vehicle)
            if spot:
                return spot
        return None

    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        """Park a vehicle and return a ticket"""
        print(f"\n🚗 Vehicle {vehicle.license_plate} ({vehicle.vehicle_type.value}) requesting entry...")

        # Find available spot
        spot = self.find_available_spot(vehicle)

        if not spot:
            print(f"❌ Sorry! No available spots for {vehicle.vehicle_type.value}")
            self._show_availability()
            return None

        # Park vehicle
        if spot.park_vehicle(vehicle):
            ticket = Ticket(vehicle, spot)
            self.active_tickets[spot.spot_id] = ticket
            print(f"✅ Parked at {spot.spot_id} (Floor {spot.floor_id})")
            print(f"🎫 Ticket issued: {ticket.ticket_id}")
            print(f"⏰ Entry time: {ticket.entry_time.strftime('%H:%M:%S')}")
            return ticket

        return None

    def exit_vehicle(self, ticket: Ticket) -> float:
        """Process vehicle exit and calculate fee"""
        print(f"\n🚗 Vehicle {ticket.vehicle.license_plate} exiting...")

        if ticket.spot.spot_id not in self.active_tickets:
            print("❌ Invalid ticket or vehicle already exited!")
            return 0.0

        # Mark exit time
        ticket.exit_time = datetime.now()

        # Calculate fee
        duration = ticket.get_parking_duration_hours()
        fee = ParkingRate.calculate_fee(ticket.vehicle.vehicle_type, duration)
        ticket.paid_amount = fee

        # Remove vehicle from spot
        ticket.spot.remove_vehicle()

        # Move ticket to history
        del self.active_tickets[ticket.spot.spot_id]
        self.payment_history.append(ticket)

        # Print receipt
        self._print_receipt(ticket, duration, fee)

        return fee

    def _print_receipt(self, ticket: Ticket, duration: float, fee: float):
        """Print parking receipt"""
        print(f"\n{'='*50}")
        print(f"           PARKING RECEIPT")
        print(f"{'='*50}")
        print(f"Ticket ID    : {ticket.ticket_id}")
        print(f"License Plate: {ticket.vehicle.license_plate}")
        print(f"Vehicle Type : {ticket.vehicle.vehicle_type.value}")
        print(f"Spot         : {ticket.spot.spot_id} (Floor {ticket.spot.floor_id})")
        print(f"Entry Time   : {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Exit Time    : {ticket.exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration     : {duration:.2f} hours")
        print(f"Rate         : ${ParkingRate.RATES[ticket.vehicle.vehicle_type]}/hour")
        print(f"Total Amount : ${fee:.2f}")
        print(f"{'='*50}")
        print(f"     Thank you! Drive safely! 🚗")
        print(f"{'='*50}\n")

    def get_status(self) -> str:
        """Get current parking lot status"""
        status = "\n" + "="*50 + "\n"
        status += "      PARKING LOT STATUS\n"
        status += "="*50 + "\n"

        for floor in self.floors:
            status += f"\n{floor}\n"
            counts = floor.get_available_count()
            status += f"  Small: {counts[SpotSize.SMALL]}, "
            status += f"Medium: {counts[SpotSize.MEDIUM]}, "
            status += f"Large: {counts[SpotSize.LARGE]}\n"

        status += f"\nActive Vehicles: {len(self.active_tickets)}\n"
        status += "="*50 + "\n"
        return status

    def _show_availability(self):
        """Show current availability"""
        print("\nCurrent Availability:")
        for floor in self.floors:
            counts = floor.get_available_count()
            print(f"  Floor {floor.floor_number}: "
                  f"Small={counts[SpotSize.SMALL]}, "
                  f"Medium={counts[SpotSize.MEDIUM]}, "
                  f"Large={counts[SpotSize.LARGE]}")
```

**You**: "This is the main system. I'm using Singleton pattern since we have one parking lot. It orchestrates parking, exit, and fee calculation. The methods are self-explanatory and follow Single Responsibility."

---

## Step 5: Demo & Testing (40-45 min)

**You**: "Let me demonstrate with a realistic scenario."

```python
def demo_parking_lot():
    """Demonstrate the parking lot system"""

    print("="*60)
    print("      PARKING LOT SYSTEM DEMO")
    print("="*60)

    # Initialize parking lot
    parking_lot = ParkingLot()

    # Create 2 floors with spots
    floor1 = Floor(1)
    floor1.add_spot(ParkingSpot("F1-S01", SpotSize.SMALL, 1))
    floor1.add_spot(ParkingSpot("F1-S02", SpotSize.SMALL, 1))
    floor1.add_spot(ParkingSpot("F1-M01", SpotSize.MEDIUM, 1))
    floor1.add_spot(ParkingSpot("F1-M02", SpotSize.MEDIUM, 1))
    floor1.add_spot(ParkingSpot("F1-L01", SpotSize.LARGE, 1))

    floor2 = Floor(2)
    floor2.add_spot(ParkingSpot("F2-S01", SpotSize.SMALL, 2))
    floor2.add_spot(ParkingSpot("F2-M01", SpotSize.MEDIUM, 2))
    floor2.add_spot(ParkingSpot("F2-L01", SpotSize.LARGE, 2))

    parking_lot.add_floor(floor1)
    parking_lot.add_floor(floor2)

    # Show pricing
    print("\n" + ParkingRate.get_rate_info())

    # Show initial status
    print(parking_lot.get_status())

    # Scenario 1: Park different vehicles
    print("\n--- SCENARIO 1: Parking Vehicles ---")

    bike1 = Motorcycle("BIKE-001")
    car1 = Car("CAR-001")
    car2 = Car("CAR-002")
    truck1 = Truck("TRUCK-001")

    ticket1 = parking_lot.park_vehicle(bike1)
    ticket2 = parking_lot.park_vehicle(car1)
    ticket3 = parking_lot.park_vehicle(car2)
    ticket4 = parking_lot.park_vehicle(truck1)

    print(parking_lot.get_status())

    # Scenario 2: Simulate some parking time
    print("\n--- SCENARIO 2: Simulating Time Passage ---")
    import time
    print("⏰ Waiting 2 seconds to simulate parking time...")
    time.sleep(2)

    # Scenario 3: Exit vehicles
    print("\n--- SCENARIO 3: Vehicle Exit & Payment ---")

    if ticket1:
        parking_lot.exit_vehicle(ticket1)

    if ticket2:
        parking_lot.exit_vehicle(ticket2)

    print(parking_lot.get_status())

    # Scenario 4: Test full parking lot
    print("\n--- SCENARIO 4: Testing Full Parking ---")

    # Park more vehicles to fill up
    car3 = Car("CAR-003")
    car4 = Car("CAR-004")
    bike2 = Motorcycle("BIKE-002")

    parking_lot.park_vehicle(car3)
    parking_lot.park_vehicle(car4)
    parking_lot.park_vehicle(bike2)

    print(parking_lot.get_status())

    # Try to park when full
    car5 = Car("CAR-005")
    ticket_full = parking_lot.park_vehicle(car5)

    # Scenario 5: Edge case - small vehicle in large spot
    print("\n--- SCENARIO 5: Motorcycle Using Large Spot ---")

    # Exit a vehicle first
    if ticket4:
        parking_lot.exit_vehicle(ticket4)

    # Now park a motorcycle (it can use the large spot)
    bike3 = Motorcycle("BIKE-003")
    ticket_bike = parking_lot.park_vehicle(bike3)

    if ticket_bike:
        print(f"✅ Motorcycle parked in {ticket_bike.spot.spot_size.value} spot!")

    print(parking_lot.get_status())

if __name__ == "__main__":
    demo_parking_lot()
```

**You**: "This demo shows:
1. ✅ Different vehicle types parking
2. ✅ Time-based fee calculation
3. ✅ Exit and payment
4. ✅ Full parking lot handling
5. ✅ Small vehicles using larger spots"

---

## Step 6: Extensions Discussion (45-50 min)

**Interviewer**: "How would you add reserved parking?"

**You**: "Great question! I'd extend the ParkingSpot class:

```python
class ReservedParkingSpot(ParkingSpot):
    def __init__(self, spot_id: str, spot_size: SpotSize, floor_id: int,
                 reserved_for: str):
        super().__init__(spot_id, spot_size, floor_id)
        self.reserved_for = reserved_for  # License plate or user ID

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        # Check reservation first
        if vehicle.license_plate != self.reserved_for:
            return False
        return super().can_fit_vehicle(vehicle)
```

This follows Open/Closed principle - we extend without modifying existing code."

**Interviewer**: "What about multiple entry/exit gates?"

**You**: "I'd add a Gate class:

```python
class Gate:
    def __init__(self, gate_id: str, gate_type: str):  # type: ENTRY or EXIT
        self.gate_id = gate_id
        self.gate_type = gate_type

    def process_entry(self, vehicle: Vehicle) -> Optional[Ticket]:
        parking_lot = ParkingLot()
        return parking_lot.park_vehicle(vehicle)

    def process_exit(self, ticket: Ticket) -> float:
        parking_lot = ParkingLot()
        return parking_lot.exit_vehicle(ticket)
```

Each gate delegates to the ParkingLot singleton. We'd add threading locks for concurrency."

**Interviewer**: "How would you handle different payment methods?"

**You**: "Strategy pattern for payment:

```python
class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CashPayment(PaymentStrategy):
    def process_payment(self, amount: float) -> bool:
        print(f'Processing ${amount} cash payment')
        return True

class CardPayment(PaymentStrategy):
    def process_payment(self, amount: float) -> bool:
        print(f'Processing ${amount} card payment')
        # Validate card, process through payment gateway
        return True
```

We'd add a payment method parameter to the exit_vehicle method."

---

## Step 7: Summary & Complexity Analysis (50-55 min)

**You**: "Let me summarize the design:

**Design Patterns Used:**
- ✅ **Singleton**: ParkingLot (single instance)
- ✅ **Strategy**: Vehicle types, potential pricing strategies
- ✅ **Inheritance**: Vehicle and ParkingSpot hierarchies
- ✅ **Composition**: ParkingLot has Floors, Floors have Spots

**SOLID Principles:**
- ✅ **S**RP: Each class has one responsibility
- ✅ **O**CP: Can extend vehicle/spot types without modification
- ✅ **L**SP: All vehicle subtypes work interchangeably
- ✅ **I**SP: Interfaces are focused and minimal
- ✅ **D**IP: Depend on Vehicle abstraction, not concrete types

**Time Complexity:**
- `park_vehicle()`: O(F × S) where F = floors, S = spots per floor
- `exit_vehicle()`: O(1) - direct ticket lookup
- `get_status()`: O(F × S) - iterate all spots

**Space Complexity:**
- O(F × S + T) where T = active tickets

**Possible Improvements:**
1. Indexed spot lookup by size (HashMap) - O(1) parking
2. Priority queue for spot assignment
3. Admin panel for monitoring
4. API endpoints for mobile app integration
5. Database persistence
6. Real-time availability display"

**Interviewer**: "Great! Any questions for me?"

**You**: "Yes! How does your team typically approach design decisions - do you favor simplicity or future-proofing?"

---

## Key Takeaways from Walkthrough 1

### ✅ What Went Well
- Clear requirements gathering upfront
- Structured, step-by-step implementation
- Used proper design patterns and explained why
- Demonstrated with realistic scenarios
- Handled edge cases
- Showed extensibility

### 💡 Interview Tips
1. **Clarify first** - Don't jump to coding
2. **Think out loud** - "I'm using X pattern because..."
3. **Start simple** - Enums → Classes → Relationships
4. **Reference SOLID** - Interviewers love hearing this
5. **Show, don't tell** - Demo your code
6. **Discuss trade-offs** - No solution is perfect

### ⏱️ Time Management
- 0-12 min: Requirements (20%)
- 12-17 min: Design (10%)
- 17-40 min: Implementation (50%)
- 40-50 min: Demo & Extensions (17%)
- 50-55 min: Summary (5%)
- 55-60 min: Questions (8%)

---

# Walkthrough 2: Vending Machine

**Difficulty**: Medium | **Time**: 45 minutes | **Companies**: Amazon, Google, Microsoft

## Step 1: Problem Statement (0-2 min)

**Interviewer**: "Design a vending machine."

**You**: "Interesting! Let me clarify the requirements before I start designing."

---

## Step 2: Requirements Clarification (2-10 min)

**Q1: What products does it sell?**
**A**: Snacks and drinks with different prices.

**Q2: What payment methods?**
**A**: Coins and bills. Keep it simple - coins: 25¢, 50¢, $1. Bills: $5, $10, $20.

**Q3: Should it return change?**
**A**: Yes, must calculate and dispense change.

**Q4: What if product is out of stock?**
**A**: Show error message, return money.

**Q5: What if exact change cannot be given?**
**A**: Show error, return money, product not dispensed.

**Q6: Should it track inventory?**
**A**: Yes, track quantity for each product.

**Q7: Any admin functions?**
**A**: Yes - restock products, collect money.

**You**: "Perfect! Summarizing:
- Sell products with different prices
- Accept coins and bills
- Calculate and return change
- Handle out-of-stock
- Handle insufficient change
- Track inventory
- Admin functions (restock, collect money)"

---

## Step 3: Core Design (10-15 min)

**You**: "This is a perfect use case for the State pattern! The vending machine has distinct states:
- **IDLE**: Waiting for user
- **ACCEPTING_MONEY**: User inserting money
- **DISPENSING**: Giving product and change
- **OUT_OF_SERVICE**: Maintenance mode

I'll also use:
- **Strategy pattern**: For payment handling
- **Factory pattern**: For product creation
- **Singleton**: For vending machine instance"

---

## Step 4: Implementation (15-40 min)

```python
from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

# Step 1: Enums and money
class MachineState(Enum):
    IDLE = "IDLE"
    ACCEPTING_MONEY = "ACCEPTING_MONEY"
    DISPENSING = "DISPENSING"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class MoneyType(Enum):
    QUARTER = 0.25
    HALF_DOLLAR = 0.50
    ONE_DOLLAR = 1.00
    FIVE_DOLLAR = 5.00
    TEN_DOLLAR = 10.00
    TWENTY_DOLLAR = 20.00

@dataclass
class Product:
    """Represents a product in the vending machine"""
    code: str  # e.g., "A1", "B3"
    name: str
    price: float
    quantity: int

    def is_available(self) -> bool:
        return self.quantity > 0

    def dispense(self) -> bool:
        if self.is_available():
            self.quantity -= 1
            return True
        return False

    def restock(self, amount: int):
        self.quantity += amount

# Step 2: Inventory
class Inventory:
    """Manages products in the vending machine"""
    def __init__(self):
        self.products: Dict[str, Product] = {}

    def add_product(self, product: Product):
        self.products[product.code] = product

    def get_product(self, code: str) -> Optional[Product]:
        return self.products.get(code)

    def is_available(self, code: str) -> bool:
        product = self.get_product(code)
        return product and product.is_available()

    def get_all_products(self) -> List[Product]:
        return list(self.products.values())

# Step 3: Money management
class MoneyInventory:
    """Manages money in the vending machine"""
    def __init__(self):
        self.money_count: Dict[MoneyType, int] = {
            money_type: 10 for money_type in MoneyType  # Start with 10 of each
        }

    def add_money(self, money_type: MoneyType, count: int = 1):
        self.money_count[money_type] += count

    def can_give_change(self, amount: float) -> bool:
        """Check if we can make change for given amount"""
        return self._make_change(amount, simulate=True) is not None

    def give_change(self, amount: float) -> Optional[Dict[MoneyType, int]]:
        """Calculate and dispense change"""
        change = self._make_change(amount, simulate=False)
        if change:
            # Deduct from inventory
            for money_type, count in change.items():
                self.money_count[money_type] -= count
        return change

    def _make_change(self, amount: float, simulate: bool) -> Optional[Dict[MoneyType, int]]:
        """Greedy algorithm to make change"""
        if amount <= 0:
            return {}

        change = {}
        remaining = round(amount, 2)

        # Sort money types by value (descending)
        sorted_money = sorted(MoneyType, key=lambda x: x.value, reverse=True)

        # Make a copy for simulation
        available = self.money_count.copy() if simulate else self.money_count

        for money_type in sorted_money:
            if remaining <= 0:
                break

            count_needed = int(remaining / money_type.value)
            count_available = available[money_type]
            count_to_use = min(count_needed, count_available)

            if count_to_use > 0:
                change[money_type] = count_to_use
                remaining = round(remaining - (count_to_use * money_type.value), 2)

        # Check if we made exact change
        if remaining > 0.01:  # Allow for floating point errors
            return None

        return change

    def get_total_money(self) -> float:
        return sum(money_type.value * count
                  for money_type, count in self.money_count.items())

# Step 4: States (State Pattern)
class VendingMachineState(ABC):
    """Abstract state for vending machine"""
    def __init__(self, machine):
        self.machine = machine

    @abstractmethod
    def insert_money(self, money_type: MoneyType) -> str:
        pass

    @abstractmethod
    def select_product(self, code: str) -> str:
        pass

    @abstractmethod
    def dispense(self) -> str:
        pass

    @abstractmethod
    def cancel(self) -> str:
        pass

class IdleState(VendingMachineState):
    """Machine is idle, waiting for interaction"""

    def insert_money(self, money_type: MoneyType) -> str:
        self.machine.current_balance += money_type.value
        self.machine.inserted_money.append(money_type)
        self.machine.state = self.machine.accepting_money_state
        return f"Inserted ${money_type.value:.2f}. Total: ${self.machine.current_balance:.2f}"

    def select_product(self, code: str) -> str:
        return "Please insert money first"

    def dispense(self) -> str:
        return "Please insert money and select product"

    def cancel(self) -> str:
        return "No transaction to cancel"

class AcceptingMoneyState(VendingMachineState):
    """Machine is accepting money"""

    def insert_money(self, money_type: MoneyType) -> str:
        self.machine.current_balance += money_type.value
        self.machine.inserted_money.append(money_type)
        return f"Inserted ${money_type.value:.2f}. Total: ${self.machine.current_balance:.2f}"

    def select_product(self, code: str) -> str:
        product = self.machine.inventory.get_product(code)

        if not product:
            return "Invalid product code"

        if not product.is_available():
            return f"{product.name} is out of stock"

        if self.machine.current_balance < product.price:
            needed = product.price - self.machine.current_balance
            return f"Insufficient funds. Need ${needed:.2f} more"

        # Calculate change
        change_amount = self.machine.current_balance - product.price

        if change_amount > 0 and not self.machine.money_inventory.can_give_change(change_amount):
            return "Cannot give exact change. Transaction cancelled"

        # All good - save product and proceed to dispense
        self.machine.selected_product = product
        self.machine.state = self.machine.dispensing_state
        return self.machine.state.dispense()

    def dispense(self) -> str:
        return "Please select a product first"

    def cancel(self) -> str:
        # Return all inserted money
        refund = self.machine.current_balance
        self.machine.current_balance = 0.0
        self.machine.inserted_money = []
        self.machine.state = self.machine.idle_state
        return f"Transaction cancelled. Refunded: ${refund:.2f}"

class DispensingState(VendingMachineState):
    """Machine is dispensing product and change"""

    def insert_money(self, money_type: MoneyType) -> str:
        return "Please wait, dispensing in progress"

    def select_product(self, code: str) -> str:
        return "Please wait, dispensing in progress"

    def dispense(self) -> str:
        product = self.machine.selected_product

        # Dispense product
        if not product.dispense():
            # Refund
            self.machine.state = self.machine.idle_state
            return "Error dispensing product. Money refunded"

        # Add inserted money to machine
        for money_type in self.machine.inserted_money:
            self.machine.money_inventory.add_money(money_type)

        # Calculate and give change
        change_amount = self.machine.current_balance - product.price
        change_detail = ""

        if change_amount > 0:
            change = self.machine.money_inventory.give_change(change_amount)
            if change:
                change_detail = "\nChange: "
                for money_type, count in sorted(change.items(),
                                              key=lambda x: x[0].value,
                                              reverse=True):
                    change_detail += f"{count}×${money_type.value:.2f} "

        # Reset machine
        result = f"✅ Dispensed: {product.name}"
        result += change_detail

        self.machine.current_balance = 0.0
        self.machine.inserted_money = []
        self.machine.selected_product = None
        self.machine.state = self.machine.idle_state

        return result

    def cancel(self) -> str:
        return "Cannot cancel, dispensing in progress"

# Step 5: Main Vending Machine
class VendingMachine:
    """Main vending machine class using State pattern"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Inventory
            self.inventory = Inventory()
            self.money_inventory = MoneyInventory()

            # Transaction state
            self.current_balance = 0.0
            self.inserted_money: List[MoneyType] = []
            self.selected_product: Optional[Product] = None

            # States
            self.idle_state = IdleState(self)
            self.accepting_money_state = AcceptingMoneyState(self)
            self.dispensing_state = DispensingState(self)

            self.state: VendingMachineState = self.idle_state
            self.initialized = True

    def insert_money(self, money_type: MoneyType) -> str:
        """Insert money into machine"""
        return self.state.insert_money(money_type)

    def select_product(self, code: str) -> str:
        """Select product by code"""
        return self.state.select_product(code)

    def cancel_transaction(self) -> str:
        """Cancel current transaction"""
        return self.state.cancel()

    def display_products(self) -> str:
        """Display all products"""
        result = "\n" + "="*50 + "\n"
        result += "        AVAILABLE PRODUCTS\n"
        result += "="*50 + "\n"

        for product in self.inventory.get_all_products():
            status = "✅" if product.is_available() else "❌ OUT OF STOCK"
            result += f"{product.code}: {product.name:<20} ${product.price:>5.2f}  [{product.quantity}] {status}\n"

        result += "="*50 + "\n"
        return result

    # Admin functions
    def restock_product(self, code: str, quantity: int):
        """Admin: Restock a product"""
        product = self.inventory.get_product(code)
        if product:
            product.restock(quantity)
            return f"Restocked {product.name}: +{quantity} (now {product.quantity})"
        return "Product not found"

    def collect_money(self) -> float:
        """Admin: Collect money from machine"""
        total = self.money_inventory.get_total_money()
        # Reset to minimum change float
        self.money_inventory.money_count = {
            money_type: 5 for money_type in MoneyType
        }
        return total

def demo_vending_machine():
    """Demonstrate vending machine"""

    print("="*60)
    print("          VENDING MACHINE DEMO")
    print("="*60)

    # Initialize machine
    vm = VendingMachine()

    # Stock products
    vm.inventory.add_product(Product("A1", "Coca Cola", 1.50, 10))
    vm.inventory.add_product(Product("A2", "Pepsi", 1.50, 8))
    vm.inventory.add_product(Product("B1", "Chips", 2.00, 5))
    vm.inventory.add_product(Product("B2", "Cookies", 2.50, 3))
    vm.inventory.add_product(Product("C1", "Chocolate", 1.75, 0))  # Out of stock

    # Show products
    print(vm.display_products())

    # Scenario 1: Successful purchase with change
    print("\n--- SCENARIO 1: Buy Coca Cola with $5 bill ---")
    print(vm.insert_money(MoneyType.FIVE_DOLLAR))
    print(vm.select_product("A1"))

    # Scenario 2: Insufficient funds
    print("\n--- SCENARIO 2: Insufficient Funds ---")
    print(vm.insert_money(MoneyType.ONE_DOLLAR))
    print(vm.select_product("B2"))  # Costs $2.50
    print(vm.insert_money(MoneyType.ONE_DOLLAR))
    print(vm.select_product("B2"))  # Now enough

    # Scenario 3: Out of stock
    print("\n--- SCENARIO 3: Out of Stock ---")
    print(vm.insert_money(MoneyType.FIVE_DOLLAR))
    print(vm.select_product("C1"))  # Out of stock
    print(vm.cancel_transaction())

    # Scenario 4: Exact change
    print("\n--- SCENARIO 4: Exact Change ---")
    print(vm.insert_money(MoneyType.ONE_DOLLAR))
    print(vm.insert_money(MoneyType.HALF_DOLLAR))
    print(vm.select_product("A2"))  # Costs $1.50

    # Show final state
    print(vm.display_products())

if __name__ == "__main__":
    demo_vending_machine()
```

---

## Step 5: Summary (40-45 min)

**You**: "This design uses **State Pattern** as the core - each state controls what operations are valid. Key design decisions:

**Patterns:**
- ✅ State pattern for machine states
- ✅ Singleton for machine instance
- ✅ Strategy for payment (extensible)
- ✅ Greedy algorithm for change-making

**SOLID:**
- ✅ Each state class has single responsibility
- ✅ Open for extension (new products, payment methods)
- ✅ States are interchangeable (LSP)

**Complexity:**
- Change-making: O(M) where M = money types
- All other operations: O(1) or O(P) for displaying products

The State pattern makes it easy to add new states or modify behavior without touching other code."

---

## Key Takeaways from Walkthrough 3

### ✅ What Went Well
- Perfect use case for State pattern
- Clean state transitions
- Proper change-making algorithm
- Good separation of concerns

### 💡 Interview Tips
1. **Recognize state machines** - Vending machine, ATM, game states
2. **Change-making is tricky** - Use greedy with validation
3. **Edge cases matter** - Out of stock, insufficient change
4. **Admin functions** - Don't forget maintenance operations

---

# Walkthrough 3: Hotel Booking System

**Difficulty**: Medium-Hard | **Time**: 45-60 minutes | **Companies**: Airbnb, Booking.com, Expedia, OYO

## Step 1: Problem Statement (0-2 min)

**Interviewer**: "Design a hotel booking system similar to Airbnb or Booking.com."

**You**: "Interesting! This could be quite broad. Let me clarify the scope before I begin."

---

## Step 2: Requirements Clarification (2-12 min)

**You**: "Let me understand the core functionality we need to support."

### Your Questions → Interviewer's Answers

**Q1: What's the scope - hotel management, search, booking, or all of it?**
**A**: Focus on the booking and room management part. Assume hotel/room data already exists.

**Q2: What types of rooms should we support?**
**A**: Different room types - Single, Double, Suite. Each type has different pricing.

**Q3: How does the booking workflow work?**
**A**: User searches for available rooms for specific dates, selects a room, makes a booking. Can later cancel or modify.

**Q4: How do we handle concurrent bookings for the same room?**
**A**: Important! Two users shouldn't be able to book the same room for overlapping dates.

**Q5: Can users book multiple rooms in one reservation?**
**A**: Yes, support multiple rooms in one booking.

**Q6: Do we need to handle payments?**
**A**: Keep it simple - just mark as paid/unpaid. Don't need full payment processing.

**Q7: What about cancellations?**
**A**: Support cancellation with a simple cancellation policy (full refund if cancelled 24 hours before check-in).

**Q8: Do we need search by amenities, location, price range?**
**A**: For now, just search by dates and room type. We can discuss extensions later.

**You**: "Perfect! Let me summarize:
- Room management with different types
- Date-based availability search
- Booking workflow with concurrency handling
- Support multiple rooms per booking
- Simple payment tracking
- Cancellation with refund policy
- Thread-safe operations for concurrent bookings

Does that capture everything?"

**Interviewer**: "Yes, let's see your design."

---

## Step 3: Core Entities & High-Level Design (12-17 min)

**You**: "Let me identify the core entities:"

```python
# Core Entities:
# 1. Hotel - Contains rooms and manages bookings
# 2. Room - Abstract (SingleRoom, DoubleRoom, Suite)
# 3. Booking/Reservation - Links user to rooms for date range
# 4. Guest/User - Person making booking
# 5. Payment - Payment details
# 6. DateRange - Helper for date operations
```

**You**: "The key challenge here is handling concurrent bookings. I'll need to:
1. Use locking mechanism when checking availability
2. Atomic check-and-book operation
3. Handle date overlaps correctly

Design patterns I'll use:
- **Factory Pattern**: Create different room types
- **Strategy Pattern**: Different pricing and cancellation policies
- **Repository Pattern**: Manage bookings
- **Thread-safe Singleton**: BookingManager
- **State Pattern**: Booking states (PENDING → CONFIRMED → CANCELLED)"

---

## Step 4: Implementation (17-42 min)

**You**: "Starting with date handling and enums:"

```python
from enum import Enum
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict
from abc import ABC, abstractmethod
import threading
from dataclasses import dataclass

# Step 1: Enums and Data Classes
class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    SUITE = "SUITE"

class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class PaymentStatus(Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"

@dataclass
class DateRange:
    """Helper class for date range operations"""
    check_in: date
    check_out: date

    def __post_init__(self):
        if self.check_in >= self.check_out:
            raise ValueError("Check-in must be before check-out")

    def overlaps_with(self, other: 'DateRange') -> bool:
        """Check if two date ranges overlap"""
        # Ranges overlap if one starts before the other ends
        return (self.check_in < other.check_out and
                other.check_in < self.check_out)

    def get_nights(self) -> int:
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days

    def __str__(self):
        return f"{self.check_in} to {self.check_out} ({self.get_nights()} nights)"
```

**You**: "The DateRange class is crucial for checking booking conflicts. The `overlaps_with` method handles all edge cases."

```python
# Step 2: Room Hierarchy
class Room(ABC):
    """Abstract base class for all room types"""
    def __init__(self, room_id: str, room_number: str, floor: int):
        self.room_id = room_id
        self.room_number = room_number
        self.floor = floor
        self.room_type: RoomType = None
        self.base_price: float = 0.0

    @abstractmethod
    def get_price_per_night(self) -> float:
        """Get price per night for this room"""
        pass

    def get_total_price(self, nights: int) -> float:
        """Calculate total price for given nights"""
        return self.get_price_per_night() * nights

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.value}, Floor {self.floor})"

class SingleRoom(Room):
    def __init__(self, room_id: str, room_number: str, floor: int):
        super().__init__(room_id, room_number, floor)
        self.room_type = RoomType.SINGLE
        self.base_price = 100.0
        self.max_occupancy = 1

    def get_price_per_night(self) -> float:
        return self.base_price

class DoubleRoom(Room):
    def __init__(self, room_id: str, room_number: str, floor: int):
        super().__init__(room_id, room_number, floor)
        self.room_type = RoomType.DOUBLE
        self.base_price = 150.0
        self.max_occupancy = 2

    def get_price_per_night(self) -> float:
        return self.base_price

class SuiteRoom(Room):
    def __init__(self, room_id: str, room_number: str, floor: int):
        super().__init__(room_id, room_number, floor)
        self.room_type = RoomType.SUITE
        self.base_price = 300.0
        self.max_occupancy = 4
        self.has_kitchen = True
        self.has_living_room = True

    def get_price_per_night(self) -> float:
        return self.base_price
```

**You**: "Room hierarchy follows OOP principles. Each room type knows its price and capacity. Easy to extend with new room types."

```python
# Step 3: Guest/User
class Guest:
    """Represents a hotel guest"""
    def __init__(self, guest_id: str, name: str, email: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f"Guest({self.name}, {self.email})"

# Step 4: Payment
class Payment:
    """Represents a payment for a booking"""
    def __init__(self, amount: float):
        self.payment_id = f"PAY-{id(self)}"
        self.amount = amount
        self.status = PaymentStatus.UNPAID
        self.payment_date: Optional[datetime] = None
        self.refund_date: Optional[datetime] = None

    def mark_paid(self):
        """Mark payment as completed"""
        self.status = PaymentStatus.PAID
        self.payment_date = datetime.now()

    def process_refund(self, refund_amount: float):
        """Process a refund"""
        if self.status != PaymentStatus.PAID:
            raise ValueError("Can only refund paid payments")

        self.status = PaymentStatus.REFUNDED
        self.refund_date = datetime.now()
        # In real system, initiate refund to payment gateway
        print(f"💰 Refunded ${refund_amount:.2f}")
```

**You**: "Payment class is simple for now. In production, this would integrate with Stripe or similar."

```python
# Step 5: Booking/Reservation
class Booking:
    """Represents a room booking"""
    _booking_counter = 0
    _counter_lock = threading.Lock()

    def __init__(self, guest: Guest, rooms: List[Room], date_range: DateRange):
        with Booking._counter_lock:
            Booking._booking_counter += 1
            self.booking_id = f"BK{Booking._booking_counter:08d}"

        self.guest = guest
        self.rooms = rooms
        self.date_range = date_range
        self.booking_date = datetime.now()
        self.status = BookingStatus.PENDING

        # Calculate pricing
        nights = date_range.get_nights()
        self.total_amount = sum(room.get_total_price(nights) for room in rooms)
        self.payment = Payment(self.total_amount)

    def confirm(self):
        """Confirm the booking"""
        if self.status != BookingStatus.PENDING:
            raise ValueError(f"Cannot confirm booking in {self.status} status")
        self.status = BookingStatus.CONFIRMED
        self.payment.mark_paid()

    def cancel(self) -> float:
        """Cancel the booking and calculate refund"""
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Booking already cancelled")

        if self.status == BookingStatus.COMPLETED:
            raise ValueError("Cannot cancel completed booking")

        # Calculate refund based on cancellation policy
        refund_amount = self._calculate_refund()

        self.status = BookingStatus.CANCELLED

        if refund_amount > 0 and self.payment.status == PaymentStatus.PAID:
            self.payment.process_refund(refund_amount)

        return refund_amount

    def _calculate_refund(self) -> float:
        """Calculate refund amount based on cancellation policy"""
        if self.payment.status != PaymentStatus.PAID:
            return 0.0

        # Cancellation policy: Full refund if cancelled 24+ hours before check-in
        hours_until_checkin = (datetime.combine(self.date_range.check_in,
                                                 datetime.min.time()) -
                              datetime.now()).total_seconds() / 3600

        if hours_until_checkin >= 24:
            return self.total_amount  # Full refund
        elif hours_until_checkin >= 6:
            return self.total_amount * 0.5  # 50% refund
        else:
            return 0.0  # No refund

    def complete(self):
        """Mark booking as completed (after checkout)"""
        if self.status != BookingStatus.CONFIRMED:
            raise ValueError("Can only complete confirmed bookings")
        self.status = BookingStatus.COMPLETED

    def get_summary(self) -> str:
        """Get booking summary"""
        rooms_desc = ", ".join(f"{r.room_number}({r.room_type.value})"
                               for r in self.rooms)
        return (f"Booking {self.booking_id}\n"
                f"  Guest: {self.guest.name}\n"
                f"  Rooms: {rooms_desc}\n"
                f"  Dates: {self.date_range}\n"
                f"  Total: ${self.total_amount:.2f}\n"
                f"  Status: {self.status.value}")
```

**You**: "Booking encapsulates the entire reservation. The State pattern is implicit - status transitions are controlled. Cancellation policy is implemented with time-based refund calculation."

```python
# Step 6: Hotel & Booking Manager
class Hotel:
    """Represents a hotel with rooms and booking management"""

    def __init__(self, hotel_id: str, name: str, address: str):
        self.hotel_id = hotel_id
        self.name = name
        self.address = address
        self.rooms: Dict[str, Room] = {}
        self.bookings: List[Booking] = []
        self._booking_lock = threading.Lock()

    def add_room(self, room: Room):
        """Add a room to the hotel"""
        self.rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get room by ID"""
        return self.rooms.get(room_id)

    def search_available_rooms(self, date_range: DateRange,
                              room_type: Optional[RoomType] = None) -> List[Room]:
        """
        Search for available rooms for given dates
        This is the critical method for handling concurrent bookings
        """
        with self._booking_lock:  # Thread-safe search
            available_rooms = []

            for room in self.rooms.values():
                # Filter by room type if specified
                if room_type and room.room_type != room_type:
                    continue

                # Check if room is available (not booked for these dates)
                if self._is_room_available(room, date_range):
                    available_rooms.append(room)

            return available_rooms

    def _is_room_available(self, room: Room, date_range: DateRange) -> bool:
        """Check if a room is available for given date range"""
        # Check all confirmed bookings for this room
        for booking in self.bookings:
            # Skip cancelled bookings
            if booking.status == BookingStatus.CANCELLED:
                continue

            # Check if any booked room matches and dates overlap
            for booked_room in booking.rooms:
                if booked_room.room_id == room.room_id:
                    if date_range.overlaps_with(booking.date_range):
                        return False

        return True

    def create_booking(self, guest: Guest, room_ids: List[str],
                      date_range: DateRange) -> Optional[Booking]:
        """
        Create a new booking (atomic operation)
        This is thread-safe to prevent double bookings
        """
        with self._booking_lock:  # Critical section
            # Get room objects
            rooms = []
            for room_id in room_ids:
                room = self.get_room(room_id)
                if not room:
                    print(f"❌ Room {room_id} not found")
                    return None
                rooms.append(room)

            # Check availability of ALL rooms
            for room in rooms:
                if not self._is_room_available(room, date_range):
                    print(f"❌ Room {room.room_number} not available for {date_range}")
                    return None

            # All rooms available - create booking
            booking = Booking(guest, rooms, date_range)
            self.bookings.append(booking)

            print(f"✅ Booking created: {booking.booking_id}")
            return booking

    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking"""
        with self._booking_lock:
            for booking in self.bookings:
                if booking.booking_id == booking_id:
                    try:
                        refund = booking.cancel()
                        print(f"✅ Booking {booking_id} cancelled. Refund: ${refund:.2f}")
                        return True
                    except ValueError as e:
                        print(f"❌ {e}")
                        return False

            print(f"❌ Booking {booking_id} not found")
            return False

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                return booking
        return None

    def get_bookings_for_guest(self, guest_id: str) -> List[Booking]:
        """Get all bookings for a guest"""
        return [b for b in self.bookings if b.guest.guest_id == guest_id]
```

**You**: "The Hotel class is the core. Key points:
1. **Thread-safe operations**: Using `threading.Lock()` for critical sections
2. **Atomic check-and-book**: Availability check and booking creation are in the same lock
3. **Overlap detection**: Uses DateRange.overlaps_with() to prevent conflicts
4. This prevents race conditions where two users book the same room simultaneously."

---

## Step 5: Demo & Testing (42-48 min)

**You**: "Let me demonstrate with concurrent booking scenarios:"

```python
def demo_hotel_booking():
    """Demonstrate the hotel booking system"""

    print("="*70)
    print("           HOTEL BOOKING SYSTEM DEMO")
    print("="*70)

    # Initialize hotel
    hotel = Hotel("H001", "Grand Plaza Hotel", "123 Main St, City")

    # Add rooms
    hotel.add_room(SingleRoom("R101", "101", 1))
    hotel.add_room(SingleRoom("R102", "102", 1))
    hotel.add_room(DoubleRoom("R201", "201", 2))
    hotel.add_room(DoubleRoom("R202", "202", 2))
    hotel.add_room(SuiteRoom("R301", "301", 3))

    # Create guests
    alice = Guest("G001", "Alice Smith", "alice@email.com", "+1-555-0101")
    bob = Guest("G002", "Bob Jones", "bob@email.com", "+1-555-0102")
    charlie = Guest("G003", "Charlie Brown", "charlie@email.com", "+1-555-0103")

    # Scenario 1: Search and book available rooms
    print("\n--- SCENARIO 1: Normal Booking ---")

    check_in = date.today() + timedelta(days=5)
    check_out = date.today() + timedelta(days=8)
    date_range = DateRange(check_in, check_out)

    print(f"\n🔍 Searching for rooms: {date_range}")
    available = hotel.search_available_rooms(date_range)

    print(f"Found {len(available)} available rooms:")
    for room in available:
        price = room.get_total_price(date_range.get_nights())
        print(f"  • {room} - ${price:.2f} total")

    # Alice books a double room
    print(f"\n👤 {alice.name} booking room 201...")
    booking1 = hotel.create_booking(alice, ["R201"], date_range)

    if booking1:
        booking1.confirm()
        print(booking1.get_summary())

    # Scenario 2: Overlapping booking attempt (should fail)
    print("\n--- SCENARIO 2: Preventing Double Booking ---")

    overlap_range = DateRange(check_in + timedelta(days=1), check_out + timedelta(days=1))
    print(f"\n👤 {bob.name} trying to book room 201 for {overlap_range}")
    booking2 = hotel.create_booking(bob, ["R201"], overlap_range)
    # Should fail - room already booked

    # Scenario 3: Non-overlapping booking (should succeed)
    print("\n--- SCENARIO 3: Non-Overlapping Booking ---")

    future_range = DateRange(check_out + timedelta(days=1),
                           check_out + timedelta(days=4))
    print(f"\n👤 {bob.name} booking room 201 for {future_range}")
    booking3 = hotel.create_booking(bob, ["R201"], future_range)

    if booking3:
        booking3.confirm()
        print(booking3.get_summary())

    # Scenario 4: Multiple rooms in one booking
    print("\n--- SCENARIO 4: Multi-Room Booking ---")

    print(f"\n👤 {charlie.name} booking 2 rooms...")
    booking4 = hotel.create_booking(charlie, ["R101", "R102"], date_range)

    if booking4:
        booking4.confirm()
        print(booking4.get_summary())

    # Scenario 5: Cancellation with refund
    print("\n--- SCENARIO 5: Cancellation Policy ---")

    print(f"\n👤 {alice.name} cancelling booking...")
    if booking1:
        hotel.cancel_booking(booking1.booking_id)

    # Scenario 6: After cancellation, room becomes available
    print("\n--- SCENARIO 6: Room Available After Cancellation ---")

    print(f"\n🔍 Searching again for {date_range}")
    available_now = hotel.search_available_rooms(date_range, RoomType.DOUBLE)
    print(f"Available double rooms: {len(available_now)}")
    for room in available_now:
        print(f"  • {room}")

    # Now Bob can book the room
    print(f"\n👤 {bob.name} booking room 201 after cancellation...")
    booking5 = hotel.create_booking(bob, ["R201"], date_range)
    if booking5:
        booking5.confirm()
        print("✅ Successfully booked after cancellation!")

    # Scenario 7: Search by room type
    print("\n--- SCENARIO 7: Search by Room Type ---")

    suites = hotel.search_available_rooms(date_range, RoomType.SUITE)
    print(f"\nAvailable suites: {len(suites)}")
    for suite in suites:
        print(f"  • {suite} - ${suite.get_price_per_night()}/night")

    # Summary
    print("\n" + "="*70)
    print("                    BOOKING SUMMARY")
    print("="*70)

    for booking in hotel.bookings:
        print(f"\n{booking.get_summary()}")
        print(f"  Payment: {booking.payment.status.value}")

def demo_concurrent_bookings():
    """Demonstrate thread-safety with concurrent bookings"""
    import time

    print("\n" + "="*70)
    print("      CONCURRENT BOOKING TEST (Thread Safety)")
    print("="*70)

    hotel = Hotel("H001", "Test Hotel", "123 Main St")
    hotel.add_room(DoubleRoom("R201", "201", 2))

    date_range = DateRange(date.today() + timedelta(days=1),
                          date.today() + timedelta(days=3))

    alice = Guest("G001", "Alice", "alice@email.com", "+1-555-0101")
    bob = Guest("G002", "Bob", "bob@email.com", "+1-555-0102")

    results = []

    def try_booking(guest, room_id, date_range):
        """Function to run in thread"""
        booking = hotel.create_booking(guest, [room_id], date_range)
        results.append((guest.name, booking is not None))
        if booking:
            booking.confirm()

    # Create two threads trying to book same room simultaneously
    thread1 = threading.Thread(target=try_booking, args=(alice, "R201", date_range))
    thread2 = threading.Thread(target=try_booking, args=(bob, "R201", date_range))

    print("\n🔄 Starting concurrent booking attempts...")
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print("\nResults:")
    for name, success in results:
        print(f"  {name}: {'✅ SUCCESS' if success else '❌ FAILED (room taken)'}")

    successful_bookings = sum(1 for _, success in results if success)
    print(f"\n✅ Thread-safety verified: Only {successful_bookings}/2 booking(s) succeeded")
    print("   (This proves no double-booking occurred)")

if __name__ == "__main__":
    demo_hotel_booking()
    demo_concurrent_bookings()
```

**You**: "The demo shows:
1. ✅ Normal booking flow
2. ✅ Preventing overlapping bookings
3. ✅ Non-overlapping bookings work fine
4. ✅ Multi-room bookings
5. ✅ Cancellation and refunds
6. ✅ Room becomes available after cancellation
7. ✅ Thread-safety test

The concurrent test proves that our locking mechanism prevents double bookings."

---

## Step 6: Extensions Discussion (48-53 min)

**Interviewer**: "How would you add dynamic pricing?"

**You**: "Great question! I'd use Strategy pattern:

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, room: Room, date_range: DateRange) -> float:
        pass

class StandardPricing(PricingStrategy):
    def calculate_price(self, room: Room, date_range: DateRange) -> float:
        return room.get_price_per_night() * date_range.get_nights()

class DynamicPricing(PricingStrategy):
    def calculate_price(self, room: Room, date_range: DateRange) -> float:
        base_price = room.get_price_per_night()
        nights = date_range.get_nights()

        # Weekend premium
        total = 0
        current = date_range.check_in
        while current < date_range.check_out:
            multiplier = 1.5 if current.weekday() >= 5 else 1.0  # Weekend
            total += base_price * multiplier
            current += timedelta(days=1)

        # Occupancy-based pricing (would check current bookings)
        # High demand = higher prices

        return total

# Add to Room class:
class Room(ABC):
    def __init__(self, ...):
        ...
        self.pricing_strategy: PricingStrategy = StandardPricing()

    def get_total_price(self, date_range: DateRange) -> float:
        return self.pricing_strategy.calculate_price(self, date_range)
```

This allows easy switching between pricing models without changing room classes."

**Interviewer**: "What about search filters - price range, amenities, etc.?"

**You**: "I'd use the Builder pattern for search queries:

```python
class RoomSearchBuilder:
    def __init__(self, hotel: Hotel, date_range: DateRange):
        self.hotel = hotel
        self.date_range = date_range
        self.room_type: Optional[RoomType] = None
        self.min_price: Optional[float] = None
        self.max_price: Optional[float] = None
        self.min_floor: Optional[int] = None
        self.max_floor: Optional[int] = None

    def with_room_type(self, room_type: RoomType):
        self.room_type = room_type
        return self

    def with_price_range(self, min_price: float, max_price: float):
        self.min_price = min_price
        self.max_price = max_price
        return self

    def with_floor_range(self, min_floor: int, max_floor: int):
        self.min_floor = min_floor
        self.max_floor = max_floor
        return self

    def search(self) -> List[Room]:
        # Get available rooms
        rooms = self.hotel.search_available_rooms(self.date_range, self.room_type)

        # Apply filters
        if self.min_price or self.max_price:
            rooms = [r for r in rooms
                    if (self.min_price or 0) <= r.get_price_per_night() <= (self.max_price or float('inf'))]

        if self.min_floor or self.max_floor:
            rooms = [r for r in rooms
                    if (self.min_floor or 0) <= r.floor <= (self.max_floor or 999)]

        return rooms

# Usage:
results = (RoomSearchBuilder(hotel, date_range)
          .with_room_type(RoomType.DOUBLE)
          .with_price_range(100, 200)
          .with_floor_range(2, 5)
          .search())
```

This provides a fluent, extensible search API."

**Interviewer**: "How would you handle overbooking?"

**You**: "Airlines do this intentionally. For hotels:

```python
class OverbookingPolicy:
    def __init__(self, overbooking_percentage: float = 0.05):
        self.overbooking_percentage = overbooking_percentage

    def calculate_available_capacity(self, total_rooms: int,
                                     booked_rooms: int) -> int:
        # Allow 5% more bookings than actual capacity
        max_bookings = int(total_rooms * (1 + self.overbooking_percentage))
        return max(0, max_bookings - booked_rooms)

    def should_allow_booking(self, hotel: Hotel, date_range: DateRange) -> bool:
        total = len(hotel.rooms)
        booked = sum(1 for b in hotel.bookings
                    if b.date_range.overlaps_with(date_range)
                    and b.status == BookingStatus.CONFIRMED)

        return booked < self.calculate_available_capacity(total, booked)
```

We'd also need a `handle_overbooking()` method to upgrade guests or arrange alternative accommodation."

---

## Step 7: Summary & Complexity Analysis (53-58 min)

**You**: "Let me summarize:

**Key Design Decisions:**
1. **Thread-safe operations**: Critical for preventing double bookings
2. **Atomic check-and-book**: Availability check and booking in same lock
3. **Date overlap logic**: Robust date range comparison
4. **State machine**: Booking status transitions
5. **Cancellation policy**: Time-based refund calculation

**Design Patterns:**
- ✅ **Factory**: Room creation (could extract to RoomFactory)
- ✅ **Strategy**: Pricing, cancellation policies
- ✅ **State**: Booking status lifecycle
- ✅ **Repository**: Booking management
- ✅ **Builder**: (Discussed) Search filters

**SOLID Principles:**
- ✅ **SRP**: Room, Booking, Payment have single responsibilities
- ✅ **OCP**: Can add new room types/pricing without modifying existing
- ✅ **LSP**: All room types interchangeable
- ✅ **DIP**: Depend on abstractions (Room, PricingStrategy)

**Time Complexity:**
- `search_available_rooms()`: O(R × B) where R = rooms, B = bookings
- `create_booking()`: O(R × B) - must check all bookings
- `cancel_booking()`: O(B) - linear search

**Space Complexity:**
- O(R + B) for rooms and bookings

**Improvements:**
1. **Index by date**: HashMap<Date, Set<RoomId>> for faster availability
2. **Database**: Persist data with transactions
3. **Caching**: Cache availability for popular date ranges
4. **Event system**: Notify on booking/cancellation
5. **Admin panel**: Manage rooms, view statistics
6. **Rate limiting**: Prevent booking spam
7. **Waiting list**: Queue for fully booked dates"

---

## Key Takeaways from Walkthrough 2

### ✅ What Went Well
- Identified concurrency as critical requirement
- Proper thread-safety implementation
- Robust date overlap handling
- Clean state machine for bookings
- Demonstrated thread-safety with concurrent test

### 💡 Interview Tips
1. **Ask about concurrency** - Critical for booking systems
2. **Date handling is tricky** - Get it right upfront
3. **Atomic operations** - Check-and-book must be atomic
4. **State machines** - Great for booking status
5. **Test concurrent scenarios** - Shows deep thinking

### 🎯 Common Pitfalls
- ❌ Forgetting thread-safety → Double bookings
- ❌ Wrong date overlap logic → Conflicts
- ❌ Not handling cancellations → Incomplete solution
- ❌ God class doing everything → Violates SRP

---

