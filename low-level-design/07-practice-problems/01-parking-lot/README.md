# Design a Parking Lot System

> **🌍 Multi-Language Note:** This solution is in Python. For complete implementations in **Go, Java, and JavaScript**:
> - [Complete Interview Walkthrough - Multi-Language](../../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md#walkthrough-1-parking-lot-system)
> - [Language Comparison Guide](../../lld-coding/multi-language/LANGUAGE-COMPARISON.md)

## Problem Statement

Design a parking lot system that can:
1. Park different types of vehicles (Car, Truck, Motorcycle, Bus)
2. Have multiple floors with different types of parking spots
3. Track which vehicle is parked in which spot
4. Calculate parking fees based on time
5. Handle entry and exit of vehicles
6. Display availability of spots

## Requirements Clarification

### Functional Requirements
1. Multiple vehicle types: Car, Truck, Motorcycle, Bus
2. Multiple spot types: Compact, Large, Handicapped, Electric
3. Multiple floors in the parking lot
4. Entry and exit gates
5. Ticket generation on entry
6. Fee calculation on exit
7. Payment processing
8. Display board showing availability

### Non-Functional Requirements
1. System should be extensible (easy to add new vehicle/spot types)
2. Should follow SOLID principles
3. Should be thread-safe (for concurrent operations)

### Constraints
1. Motorcycle → Compact spot
2. Car → Compact or Regular spot
3. Truck/Bus → Large spot
4. Each vehicle needs exactly one spot
5. First come, first served for spot allocation

## Step-by-Step Design

### Step 1: Identify Core Entities

- ParkingLot
- Floor
- ParkingSpot (different types)
- Vehicle (different types)
- Ticket
- Gate (Entry/Exit)
- Payment
- Display Board

### Step 2: Class Diagram

```
ParkingLot
    ├── has multiple Floors
    ├── has Entry/Exit Gates
    └── manages Tickets

Floor
    └── has multiple ParkingSpots

ParkingSpot (abstract)
    ├── CompactSpot
    ├── LargeSpot
    ├── HandicappedSpot
    └── ElectricSpot

Vehicle (abstract)
    ├── Car
    ├── Truck
    ├── Motorcycle
    └── Bus

Ticket
    └── links Vehicle to ParkingSpot
```

### Step 3: Apply Design Patterns

1. **Singleton**: ParkingLot (only one instance)
2. **Strategy**: Parking spot selection strategy
3. **Factory**: Create different types of vehicles/spots
4. **Observer**: Notify display boards when spots change

### Step 4: Apply SOLID Principles

- **SRP**: Each class has one responsibility
- **OCP**: Easy to add new vehicle/spot types
- **LSP**: All spot types can substitute ParkingSpot
- **ISP**: Separate interfaces for different capabilities
- **DIP**: Depend on abstractions (interfaces)

## Complete Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict
import threading
from dataclasses import dataclass

# ============= ENUMS =============

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

class PaymentStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PaymentMethod(Enum):
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    UPI = "UPI"

# ============= VEHICLE CLASSES =============

class Vehicle(ABC):
    """Abstract base class for all vehicles"""

    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

    def __str__(self):
        return f"{self.vehicle_type.value} ({self.license_plate})"

class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)

class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)

class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)

class Bus(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.BUS)

# ============= PARKING SPOT CLASSES =============

class ParkingSpot(ABC):
    """Abstract base class for parking spots"""

    def __init__(self, spot_id: str, floor_number: int, spot_type: SpotType):
        self.spot_id = spot_id
        self.floor_number = floor_number
        self.spot_type = spot_type
        self.is_available = True
        self.vehicle: Optional[Vehicle] = None
        self._lock = threading.Lock()

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """Thread-safe vehicle parking"""
        with self._lock:
            if not self.is_available:
                return False
            self.vehicle = vehicle
            self.is_available = False
            return True

    def remove_vehicle(self) -> Optional[Vehicle]:
        """Thread-safe vehicle removal"""
        with self._lock:
            if self.is_available:
                return None
            vehicle = self.vehicle
            self.vehicle = None
            self.is_available = True
            return vehicle

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        """Check if spot can accommodate vehicle"""
        return self.is_available and self._is_compatible(vehicle)

    @abstractmethod
    def _is_compatible(self, vehicle: Vehicle) -> bool:
        """Check if vehicle type is compatible with spot type"""
        pass

    def __str__(self):
        status = "Available" if self.is_available else f"Occupied by {self.vehicle}"
        return f"Spot {self.spot_id} ({self.spot_type.value}): {status}"

class CompactSpot(ParkingSpot):
    def __init__(self, spot_id: str, floor_number: int):
        super().__init__(spot_id, floor_number, SpotType.COMPACT)

    def _is_compatible(self, vehicle: Vehicle) -> bool:
        return vehicle.vehicle_type in [VehicleType.MOTORCYCLE, VehicleType.CAR]

class LargeSpot(ParkingSpot):
    def __init__(self, spot_id: str, floor_number: int):
        super().__init__(spot_id, floor_number, SpotType.LARGE)

    def _is_compatible(self, vehicle: Vehicle) -> bool:
        return vehicle.vehicle_type in [VehicleType.TRUCK, VehicleType.BUS, VehicleType.CAR]

class HandicappedSpot(ParkingSpot):
    def __init__(self, spot_id: str, floor_number: int):
        super().__init__(spot_id, floor_number, SpotType.HANDICAPPED)

    def _is_compatible(self, vehicle: Vehicle) -> bool:
        return vehicle.vehicle_type in [VehicleType.CAR, VehicleType.MOTORCYCLE]

class ElectricSpot(ParkingSpot):
    def __init__(self, spot_id: str, floor_number: int):
        super().__init__(spot_id, floor_number, SpotType.ELECTRIC)

    def _is_compatible(self, vehicle: Vehicle) -> bool:
        return vehicle.vehicle_type == VehicleType.CAR

# ============= PARKING STRATEGY =============

class ParkingStrategy(ABC):
    """Strategy pattern for spot selection"""

    @abstractmethod
    def find_spot(self, floors: List['Floor'], vehicle: Vehicle) -> Optional[ParkingSpot]:
        pass

class NearestSpotStrategy(ParkingStrategy):
    """Find nearest available spot"""

    def find_spot(self, floors: List['Floor'], vehicle: Vehicle) -> Optional[ParkingSpot]:
        for floor in floors:
            spot = floor.find_available_spot(vehicle)
            if spot:
                return spot
        return None

class LargestSpotStrategy(ParkingStrategy):
    """Prefer larger spots first"""

    def find_spot(self, floors: List['Floor'], vehicle: Vehicle) -> Optional[ParkingSpot]:
        spot_priority = [SpotType.LARGE, SpotType.COMPACT, SpotType.HANDICAPPED, SpotType.ELECTRIC]
        for spot_type in spot_priority:
            for floor in floors:
                spot = floor.find_spot_by_type(vehicle, spot_type)
                if spot:
                    return spot
        return None

# ============= FLOOR CLASS =============

class Floor:
    """Represents a floor in the parking lot"""

    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: Dict[str, ParkingSpot] = {}

    def add_spot(self, spot: ParkingSpot):
        self.spots[spot.spot_id] = spot

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find first available compatible spot"""
        for spot in self.spots.values():
            if spot.can_fit_vehicle(vehicle):
                return spot
        return None

    def find_spot_by_type(self, vehicle: Vehicle, spot_type: SpotType) -> Optional[ParkingSpot]:
        """Find spot of specific type"""
        for spot in self.spots.values():
            if spot.spot_type == spot_type and spot.can_fit_vehicle(vehicle):
                return spot
        return None

    def get_available_count(self) -> Dict[SpotType, int]:
        """Get count of available spots by type"""
        counts = {spot_type: 0 for spot_type in SpotType}
        for spot in self.spots.values():
            if spot.is_available:
                counts[spot.spot_type] += 1
        return counts

    def __str__(self):
        return f"Floor {self.floor_number}: {len(self.spots)} spots"

# ============= TICKET CLASS =============

@dataclass
class Ticket:
    """Parking ticket"""
    ticket_id: str
    vehicle: Vehicle
    spot: ParkingSpot
    entry_time: datetime
    exit_time: Optional[datetime] = None

    def mark_exit(self):
        self.exit_time = datetime.now()

    def get_duration_hours(self) -> float:
        """Calculate parking duration in hours"""
        if not self.exit_time:
            return 0
        duration = (self.exit_time - self.entry_time).total_seconds()
        return duration / 3600

# ============= PAYMENT CLASSES =============

class PaymentProcessor(ABC):
    """Abstract payment processor"""

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CashPayment(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        print(f"Processing cash payment of ${amount:.2f}")
        return True

class CreditCardPayment(PaymentProcessor):
    def __init__(self, card_number: str):
        self.card_number = card_number

    def process_payment(self, amount: float) -> bool:
        print(f"Processing credit card payment of ${amount:.2f}")
        # Simulate payment processing
        return True

class UPIPayment(PaymentProcessor):
    def __init__(self, upi_id: str):
        self.upi_id = upi_id

    def process_payment(self, amount: float) -> bool:
        print(f"Processing UPI payment of ${amount:.2f}")
        return True

# ============= PRICING STRATEGY =============

class PricingStrategy(ABC):
    """Strategy for calculating parking fees"""

    @abstractmethod
    def calculate_fee(self, ticket: Ticket) -> float:
        pass

class HourlyPricing(PricingStrategy):
    def __init__(self, hourly_rate: float):
        self.hourly_rate = hourly_rate

    def calculate_fee(self, ticket: Ticket) -> float:
        hours = ticket.get_duration_hours()
        return hours * self.hourly_rate

class FlatRatePricing(PricingStrategy):
    def __init__(self, flat_rate: float):
        self.flat_rate = flat_rate

    def calculate_fee(self, ticket: Ticket) -> float:
        return self.flat_rate

# ============= PARKING LOT (Singleton) =============

class ParkingLot:
    """Main parking lot class (Singleton pattern)"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.name = "Grand Parking Lot"
            self.floors: List[Floor] = []
            self.active_tickets: Dict[str, Ticket] = {}
            self.parking_strategy: ParkingStrategy = NearestSpotStrategy()
            self.pricing_strategy: PricingStrategy = HourlyPricing(10.0)
            self._ticket_counter = 0
            self._lock = threading.Lock()
            self.initialized = True

    def add_floor(self, floor: Floor):
        self.floors.append(floor)

    def set_parking_strategy(self, strategy: ParkingStrategy):
        self.parking_strategy = strategy

    def set_pricing_strategy(self, strategy: PricingStrategy):
        self.pricing_strategy = strategy

    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        """Park a vehicle and return ticket"""
        with self._lock:
            # Find available spot
            spot = self.parking_strategy.find_spot(self.floors, vehicle)
            if not spot:
                print(f"No available spot for {vehicle}")
                return None

            # Park the vehicle
            if spot.park_vehicle(vehicle):
                # Generate ticket
                ticket = Ticket(
                    ticket_id=self._generate_ticket_id(),
                    vehicle=vehicle,
                    spot=spot,
                    entry_time=datetime.now()
                )
                self.active_tickets[ticket.ticket_id] = ticket
                print(f"✓ Parked {vehicle} at {spot.spot_id}")
                return ticket

            return None

    def exit_vehicle(self, ticket_id: str, payment_processor: PaymentProcessor) -> bool:
        """Process vehicle exit"""
        with self._lock:
            ticket = self.active_tickets.get(ticket_id)
            if not ticket:
                print("Invalid ticket")
                return False

            # Mark exit time
            ticket.mark_exit()

            # Calculate fee
            fee = self.pricing_strategy.calculate_fee(ticket)
            print(f"Parking fee: ${fee:.2f}")

            # Process payment
            if payment_processor.process_payment(fee):
                # Remove vehicle from spot
                ticket.spot.remove_vehicle()

                # Remove from active tickets
                del self.active_tickets[ticket_id]

                print(f"✓ {ticket.vehicle} exited successfully")
                return True
            else:
                print("Payment failed")
                return False

    def display_availability(self):
        """Display availability across all floors"""
        print("\n" + "="*60)
        print(f"{self.name} - Parking Availability")
        print("="*60)
        for floor in self.floors:
            counts = floor.get_available_count()
            print(f"Floor {floor.floor_number}:")
            for spot_type, count in counts.items():
                print(f"  {spot_type.value}: {count} available")
        print("="*60 + "\n")

    def _generate_ticket_id(self) -> str:
        self._ticket_counter += 1
        return f"TICKET-{self._ticket_counter:06d}"

# ============= DEMO USAGE =============

def main():
    # Create parking lot (Singleton)
    parking_lot = ParkingLot()

    # Create floors
    for floor_num in range(1, 4):
        floor = Floor(floor_num)

        # Add different types of spots
        for i in range(10):
            spot_id = f"F{floor_num}-C{i+1}"
            floor.add_spot(CompactSpot(spot_id, floor_num))

        for i in range(5):
            spot_id = f"F{floor_num}-L{i+1}"
            floor.add_spot(LargeSpot(spot_id, floor_num))

        for i in range(2):
            spot_id = f"F{floor_num}-H{i+1}"
            floor.add_spot(HandicappedSpot(spot_id, floor_num))

        for i in range(3):
            spot_id = f"F{floor_num}-E{i+1}"
            floor.add_spot(ElectricSpot(spot_id, floor_num))

        parking_lot.add_floor(floor)

    print("🚗 Parking Lot Management System 🚗\n")

    # Display initial availability
    parking_lot.display_availability()

    # Park some vehicles
    car1 = Car("ABC-123")
    car2 = Car("XYZ-789")
    truck1 = Truck("TRUCK-001")
    motorcycle1 = Motorcycle("MOTO-001")

    ticket1 = parking_lot.park_vehicle(car1)
    ticket2 = parking_lot.park_vehicle(car2)
    ticket3 = parking_lot.park_vehicle(truck1)
    ticket4 = parking_lot.park_vehicle(motorcycle1)

    # Display updated availability
    parking_lot.display_availability()

    # Simulate some time passing
    print("\n⏰ Simulating 2 hours of parking...\n")

    # Exit a vehicle
    if ticket1:
        parking_lot.exit_vehicle(ticket1.ticket_id, CreditCardPayment("1234-5678-9012-3456"))

    # Display final availability
    parking_lot.display_availability()

if __name__ == "__main__":
    main()
```

## Key Design Decisions

### 1. Singleton Pattern for ParkingLot
- Only one parking lot instance needed
- Centralized management

### 2. Strategy Pattern
- `ParkingStrategy`: Different spot selection algorithms
- `PricingStrategy`: Different fee calculation methods

### 3. Thread Safety
- Used `threading.Lock()` for concurrent access
- Protected critical sections

### 4. SOLID Compliance
- **SRP**: Each class has single responsibility
- **OCP**: Easy to add new vehicle/spot types
- **LSP**: All subclasses work correctly
- **ISP**: No unnecessary interface methods
- **DIP**: Depend on abstractions (ParkingStrategy, PaymentProcessor)

### 5. Extensibility
- Add new vehicle type: Create new Vehicle subclass
- Add new spot type: Create new ParkingSpot subclass
- Add new payment method: Implement PaymentProcessor
- Add new pricing: Implement PricingStrategy

## Testing the Design

### Test Cases

1. ✅ Park different vehicle types
2. ✅ Handle parking lot full scenario
3. ✅ Calculate fees correctly
4. ✅ Process different payment methods
5. ✅ Display availability accurately
6. ✅ Thread-safe operations
7. ✅ Invalid ticket handling

## Time Complexity

- Park vehicle: O(F × S) where F = floors, S = spots per floor
- Exit vehicle: O(1) with dictionary lookup
- Display availability: O(F × S)

## Space Complexity

- O(F × S) for storing all spots
- O(T) for active tickets

## Extensions

1. **Reservations**: Add booking system
2. **Multiple entry/exit gates**: Track queue at gates
3. **VIP parking**: Priority parking spots
4. **Electric charging**: Track charging status
5. **Mobile app integration**: QR code for tickets
6. **Analytics**: Track occupancy patterns

---

**Complete!** This solution demonstrates all key LLD concepts: OOP pillars, SOLID principles, design patterns, and real-world considerations.
