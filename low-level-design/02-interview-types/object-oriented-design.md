# Object-Oriented Design (OOD) Interviews

## Overview

Object-Oriented Design is the **most common** type of LLD interview at major tech companies like Google, Amazon, Meta, Microsoft, Apple, and Netflix.

## Format

- **Duration**: 45-60 minutes
- **Expectation**: Design classes, interfaces, and relationships
- **Output**: Class diagrams, pseudocode, or skeleton code
- **Focus**: Design thinking, not complete implementation

## What Interviewers Evaluate

### 1. Requirements Clarification (10-15 min)
- Do you ask the right questions?
- Can you identify ambiguities?
- Do you understand the problem scope?

### 2. Core Design (20-30 min)
- Can you identify the right entities/classes?
- Are responsibilities clearly separated?
- Do relationships make sense?
- Are you applying OOP principles correctly?

### 3. Design Patterns & Principles (10-15 min)
- Can you justify your design decisions?
- Do you know when to apply design patterns?
- Are you following SOLID principles?

### 4. Extensions & Trade-offs (5-10 min)
- How does your design handle new requirements?
- Can you discuss alternative approaches?
- Do you understand the trade-offs?

## Common Problem Types

### 1. Management Systems
- Parking Lot
- Library Management
- Hotel Management
- Restaurant Reservation

### 2. Games
- Chess
- Tic-Tac-Toe
- Snake and Ladders
- Card Games (Poker, Blackjack)

### 3. Services
- Vending Machine
- ATM
- Elevator System
- Traffic Light System

### 4. Applications
- Movie Ticket Booking
- Online Shopping Cart
- Splitwise
- Logging Framework

## Step-by-Step Approach

### Step 1: Clarify Requirements (CRITICAL!)

Never start designing immediately. Ask questions:

```python
# Example: "Design a Parking Lot"

# Questions to ask:
"""
1. What types of vehicles? (Car, Truck, Motorcycle, Bus)
2. What types of parking spots? (Compact, Large, Handicapped, Electric)
3. Multiple floors or single level?
4. How is pricing calculated? (Hourly, flat rate, vehicle type based)
5. What about entry/exit gates?
6. Do we need to track which vehicle is in which spot?
7. Should we support reservations?
8. What happens if parking lot is full?
9. Payment methods? (Cash, Card, UPI)
10. Any special rules? (First hour free, member discounts)
"""
```

### Step 2: Identify Core Entities

List the main "nouns" in the problem:

```python
# Parking Lot System

# Core Entities:
# - ParkingLot
# - Floor
# - ParkingSpot
# - Vehicle
# - Ticket
# - Payment
# - Gate (Entry/Exit)
```

### Step 3: Define Classes

Start with basic class structure:

```python
from enum import Enum
from datetime import datetime
from typing import List, Optional

class VehicleType(Enum):
    CAR = "CAR"
    TRUCK = "TRUCK"
    MOTORCYCLE = "MOTORCYCLE"
    BUS = "BUS"

class SpotType(Enum):
    COMPACT = "COMPACT"
    LARGE = "LARGE"
    HANDICAPPED = "HANDICAPPED"
    ELECTRIC = "ELECTRIC"

class Vehicle:
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

class ParkingSpot:
    def __init__(self, spot_id: str, spot_type: SpotType, floor_number: int):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.floor_number = floor_number
        self.is_available = True
        self.vehicle: Optional[Vehicle] = None

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.is_available:
            return False
        self.vehicle = vehicle
        self.is_available = False
        return True

    def remove_vehicle(self) -> Optional[Vehicle]:
        vehicle = self.vehicle
        self.vehicle = None
        self.is_available = True
        return vehicle

class Floor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: List[ParkingSpot] = []

    def add_spot(self, spot: ParkingSpot):
        self.spots.append(spot)

    def get_available_spots(self, spot_type: SpotType) -> List[ParkingSpot]:
        return [
            spot for spot in self.spots
            if spot.is_available and spot.spot_type == spot_type
        ]

class Ticket:
    def __init__(self, ticket_id: str, vehicle: Vehicle, spot: ParkingSpot):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time: Optional[datetime] = None

    def mark_exit(self):
        self.exit_time = datetime.now()

class ParkingLot:
    def __init__(self, name: str):
        self.name = name
        self.floors: List[Floor] = []
        self.active_tickets: dict[str, Ticket] = {}

    def add_floor(self, floor: Floor):
        self.floors.append(floor)

    def find_available_spot(self, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        spot_type = self._get_spot_type_for_vehicle(vehicle_type)
        for floor in self.floors:
            available_spots = floor.get_available_spots(spot_type)
            if available_spots:
                return available_spots[0]
        return None

    def _get_spot_type_for_vehicle(self, vehicle_type: VehicleType) -> SpotType:
        # Simple mapping
        if vehicle_type == VehicleType.MOTORCYCLE:
            return SpotType.COMPACT
        elif vehicle_type == VehicleType.CAR:
            return SpotType.COMPACT
        elif vehicle_type in [VehicleType.TRUCK, VehicleType.BUS]:
            return SpotType.LARGE
        return SpotType.COMPACT
```

### Step 4: Add Behavior & Relationships

Implement key operations:

```python
class ParkingService:
    """Service to handle parking operations"""

    def __init__(self, parking_lot: ParkingLot):
        self.parking_lot = parking_lot

    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        # Find available spot
        spot = self.parking_lot.find_available_spot(vehicle.vehicle_type)
        if not spot:
            print("No available spots")
            return None

        # Park the vehicle
        if spot.park_vehicle(vehicle):
            # Generate ticket
            ticket = Ticket(
                ticket_id=self._generate_ticket_id(),
                vehicle=vehicle,
                spot=spot
            )
            self.parking_lot.active_tickets[ticket.ticket_id] = ticket
            return ticket

        return None

    def exit_vehicle(self, ticket_id: str) -> float:
        ticket = self.parking_lot.active_tickets.get(ticket_id)
        if not ticket:
            raise ValueError("Invalid ticket")

        # Mark exit
        ticket.mark_exit()

        # Calculate fee
        fee = self._calculate_fee(ticket)

        # Free up spot
        ticket.spot.remove_vehicle()

        # Remove from active tickets
        del self.parking_lot.active_tickets[ticket_id]

        return fee

    def _calculate_fee(self, ticket: Ticket) -> float:
        duration = (ticket.exit_time - ticket.entry_time).total_seconds() / 3600
        hourly_rate = 10.0
        return duration * hourly_rate

    def _generate_ticket_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
```

### Step 5: Apply Design Patterns

Identify where patterns can improve your design:

```python
# Strategy Pattern for Parking Spot Selection
from abc import ABC, abstractmethod

class ParkingStrategy(ABC):
    @abstractmethod
    def find_spot(self, floors: List[Floor], vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        pass

class NearestSpotStrategy(ParkingStrategy):
    """Find the nearest available spot"""
    def find_spot(self, floors: List[Floor], vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        for floor in floors:
            spot_type = self._map_vehicle_to_spot(vehicle_type)
            available = floor.get_available_spots(spot_type)
            if available:
                return available[0]
        return None

    def _map_vehicle_to_spot(self, vehicle_type: VehicleType) -> SpotType:
        # Mapping logic
        pass

class MinimumDistanceStrategy(ParkingStrategy):
    """Find spot with minimum walking distance from entrance"""
    def find_spot(self, floors: List[Floor], vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        # Implementation with distance calculation
        pass

# Factory Pattern for Ticket Generation
class TicketFactory:
    @staticmethod
    def create_ticket(ticket_type: str, vehicle: Vehicle, spot: ParkingSpot) -> Ticket:
        if ticket_type == "HOURLY":
            return HourlyTicket(vehicle, spot)
        elif ticket_type == "DAILY":
            return DailyTicket(vehicle, spot)
        else:
            return Ticket(str(uuid.uuid4()), vehicle, spot)
```

### Step 6: Discuss SOLID Principles

Be ready to explain how your design follows SOLID:

```python
# Single Responsibility Principle (SRP)
# Each class has ONE reason to change

class ParkingSpot:
    """Responsible ONLY for managing a single parking spot"""
    pass

class PaymentProcessor:
    """Responsible ONLY for processing payments"""
    pass

class TicketGenerator:
    """Responsible ONLY for generating tickets"""
    pass

# Open/Closed Principle (OCP)
# Open for extension, closed for modification

class PaymentMethod(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool:
        pass

# Can add new payment methods without modifying existing code
class CreditCardPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # Credit card logic
        pass

class CashPayment(PaymentMethod):
    def process(self, amount: float) -> bool:
        # Cash logic
        pass

# Liskov Substitution Principle (LSP)
# Subclasses should be substitutable for their base classes

def process_payment(payment_method: PaymentMethod, amount: float):
    # Works with ANY PaymentMethod subclass
    return payment_method.process(amount)

# Interface Segregation Principle (ISP)
# Clients shouldn't depend on interfaces they don't use

class Parkable(ABC):
    @abstractmethod
    def park(self, vehicle: Vehicle) -> bool:
        pass

class Reservable(ABC):
    @abstractmethod
    def reserve(self, vehicle: Vehicle, time: datetime) -> bool:
        pass

# Regular spot only implements Parkable
# Premium spot implements both Parkable and Reservable

# Dependency Inversion Principle (DIP)
# Depend on abstractions, not concretions

class ParkingService:
    def __init__(self, parking_strategy: ParkingStrategy):
        # Depends on abstraction (ParkingStrategy)
        # Not on concrete implementation
        self.strategy = parking_strategy
```

## Common Mistakes to Avoid

### ❌ Starting to code immediately
**✅ Do**: Clarify requirements first, then design, then code

### ❌ Creating god classes
```python
# BAD: ParkingLot does everything
class ParkingLot:
    def park_vehicle(self): pass
    def process_payment(self): pass
    def send_notification(self): pass
    def generate_report(self): pass
```

**✅ Do**: Separate responsibilities
```python
# GOOD: Each class has one job
class ParkingLot: pass
class PaymentService: pass
class NotificationService: pass
class ReportGenerator: pass
```

### ❌ Ignoring edge cases
**✅ Do**: Ask about edge cases
- What if parking lot is full?
- What if vehicle is already parked?
- What if ticket is lost?
- What if payment fails?

### ❌ Over-engineering
**✅ Do**: Start simple, then extend

### ❌ Not communicating
**✅ Do**: Think out loud, explain your decisions

## Interview Tips

1. **Clarify first**: Spend 10-15 minutes on requirements
2. **Start simple**: Core classes first, then extend
3. **Draw diagrams**: Visual representation helps
4. **Think out loud**: Explain your reasoning
5. **Be open to feedback**: Interviewers may guide you
6. **Know SOLID**: Reference principles when explaining
7. **Discuss trade-offs**: Every design has pros/cons
8. **Handle extensions**: Show your design is flexible

## Practice Problem

**Try this now**: Design an **Elevator System**

Spend 45 minutes designing it, then check the solution in the practice problems section.

---

**Next**: Learn about [Machine Coding Interviews](./machine-coding.md)
