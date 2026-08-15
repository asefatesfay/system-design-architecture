# Multi-Language Interview Walkthroughs

Complete interview walkthroughs with implementations in **Python, Go, Java, and JavaScript**.

> **💡 Tip**: Click on the language tabs below each example to see implementations in your preferred language!

## Table of Contents

1. [Parking Lot System](#1-parking-lot-system) (45 min)
2. [Vending Machine](#2-vending-machine) (60 min)
3. [Hotel Booking System](#3-hotel-booking-system) (60 min)

---

## How to Use This Guide

### Choose Your Language Path

**Option 1: Single Language** (Recommended for interviews)
- Pick ONE language you're most comfortable with
- Follow that language throughout
- Focus on design thinking, not syntax

**Option 2: Comparison Learning**
- Compare implementations across languages
- Understand language-specific idioms
- See same design in different styles

### Language Recommendations

| Language | Best For | Companies |
|----------|----------|-----------|
| Python | Quick interviews, readable code | Google, Meta, startups |
| Go | Concurrency-focused, systems roles | Uber, Google (systems), cloud companies |
| Java | Enterprise, type-safe code | Amazon, Microsoft, banks |
| JavaScript | Full-stack, web roles | Frontend roles, Node.js positions |

---

## 1. Parking Lot System

**Difficulty**: Medium
**Time**: 45 minutes
**Key Concepts**: Strategy Pattern, Singleton, Class Design

### Problem Statement

Design a parking lot system that:
- Has multiple floors
- Supports different vehicle types (bike, car, truck)
- Has different pricing for vehicle types
- Can find nearest available spot
- Track available spots in real-time

### Step 1: Requirements Clarification (5 min)

**You:** "Let me clarify a few requirements:
1. How many vehicle types do we need to support?"

**Interviewer:** "Three: bikes, cars, and trucks"

**You:** "Do different vehicle types have different spot sizes?"

**Interviewer:** "Yes, a truck needs a large spot, car needs medium, bike needs small"

**You:** "Can we assume one floor to start, then extend to multiple floors?"

**Interviewer:** "Yes, start simple"

### Step 2: Core Entities (5 min)

**You identify:**
- `ParkingLot` - The main system
- `ParkingSpot` - Individual parking space
- `Vehicle` - Base class with types
- `Ticket` - Parking record
- `PricingStrategy` - Calculate fees

### Step 3: Design & Implementation (30 min)

<details>
<summary><b>🐍 Python Implementation</b> (Click to expand)</summary>

```python
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional, List


# ============================================================================
# Enums
# ============================================================================
class VehicleType(Enum):
    BIKE = "BIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"


class SpotType(Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"


# ============================================================================
# Vehicle Classes
# ============================================================================
class Vehicle(ABC):
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type

    @abstractmethod
    def get_required_spot_type(self) -> SpotType:
        pass


class Bike(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.BIKE)

    def get_required_spot_type(self) -> SpotType:
        return SpotType.SMALL


class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)

    def get_required_spot_type(self) -> SpotType:
        return SpotType.MEDIUM


class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)

    def get_required_spot_type(self) -> SpotType:
        return SpotType.LARGE


# ============================================================================
# Parking Spot
# ============================================================================
class ParkingSpot:
    def __init__(self, spot_id: int, spot_type: SpotType):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.vehicle: Optional[Vehicle] = None
        self.is_available = True

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.is_available:
            return False

        required = vehicle.get_required_spot_type()
        # Small spot only fits bikes, Medium fits cars, Large fits trucks
        if self.spot_type == SpotType.SMALL and required == SpotType.SMALL:
            return True
        if self.spot_type == SpotType.MEDIUM and required in [SpotType.SMALL, SpotType.MEDIUM]:
            return True
        if self.spot_type == SpotType.LARGE:
            return True
        return False

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        if not self.can_fit_vehicle(vehicle):
            return False

        self.vehicle = vehicle
        self.is_available = False
        return True

    def remove_vehicle(self) -> Optional[Vehicle]:
        vehicle = self.vehicle
        self.vehicle = None
        self.is_available = True
        return vehicle


# ============================================================================
# Ticket
# ============================================================================
class Ticket:
    _ticket_counter = 0

    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        Ticket._ticket_counter += 1
        self.ticket_id = Ticket._ticket_counter
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time: Optional[datetime] = None

    def get_parking_duration_hours(self) -> float:
        if self.exit_time is None:
            end = datetime.now()
        else:
            end = self.exit_time
        duration = (end - self.entry_time).total_seconds() / 3600
        return max(duration, 0.1)  # Minimum 0.1 hour


# ============================================================================
# Pricing Strategy (Strategy Pattern)
# ============================================================================
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, ticket: Ticket) -> float:
        pass


class HourlyPricing(PricingStrategy):
    def __init__(self):
        self.rates = {
            VehicleType.BIKE: 5.0,
            VehicleType.CAR: 10.0,
            VehicleType.TRUCK: 20.0,
        }

    def calculate_fee(self, ticket: Ticket) -> float:
        hours = ticket.get_parking_duration_hours()
        rate = self.rates[ticket.vehicle.vehicle_type]
        return hours * rate


# ============================================================================
# Parking Lot (Singleton Pattern)
# ============================================================================
class ParkingLot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.spots: List[ParkingSpot] = []
        self.active_tickets: dict[int, Ticket] = {}
        self.pricing_strategy = HourlyPricing()

    def add_spot(self, spot_type: SpotType) -> ParkingSpot:
        spot_id = len(self.spots) + 1
        spot = ParkingSpot(spot_id, spot_type)
        self.spots.append(spot)
        return spot

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        for spot in self.spots:
            if spot.can_fit_vehicle(vehicle):
                return spot
        return None

    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        spot = self.find_available_spot(vehicle)
        if spot is None:
            print(f"❌ No available spot for {vehicle.vehicle_type.value}")
            return None

        spot.park_vehicle(vehicle)
        ticket = Ticket(vehicle, spot)
        self.active_tickets[ticket.ticket_id] = ticket
        print(f"✅ Parked {vehicle.license_plate} at spot {spot.spot_id}")
        return ticket

    def remove_vehicle(self, ticket: Ticket) -> float:
        if ticket.ticket_id not in self.active_tickets:
            raise ValueError("Invalid ticket")

        ticket.exit_time = datetime.now()
        fee = self.pricing_strategy.calculate_fee(ticket)

        ticket.spot.remove_vehicle()
        del self.active_tickets[ticket.ticket_id]

        print(f"💵 Fee for {ticket.vehicle.license_plate}: ${fee:.2f}")
        return fee

    def get_available_count(self) -> int:
        return sum(1 for spot in self.spots if spot.is_available)


# ============================================================================
# Demo
# ============================================================================
def main():
    print("="*60)
    print("PYTHON: Parking Lot System")
    print("="*60)

    # Initialize parking lot
    parking_lot = ParkingLot()

    # Add spots
    for _ in range(5):
        parking_lot.add_spot(SpotType.SMALL)
    for _ in range(10):
        parking_lot.add_spot(SpotType.MEDIUM)
    for _ in range(5):
        parking_lot.add_spot(SpotType.LARGE)

    print(f"\nTotal spots: {len(parking_lot.spots)}")
    print(f"Available: {parking_lot.get_available_count()}\n")

    # Park vehicles
    bike = Bike("BIKE-001")
    car = Car("CAR-001")
    truck = Truck("TRUCK-001")

    ticket1 = parking_lot.park_vehicle(bike)
    ticket2 = parking_lot.park_vehicle(car)
    ticket3 = parking_lot.park_vehicle(truck)

    print(f"\nAvailable after parking: {parking_lot.get_available_count()}\n")

    # Remove vehicles
    import time
    time.sleep(1)  # Simulate parking duration

    parking_lot.remove_vehicle(ticket1)
    parking_lot.remove_vehicle(ticket2)
    parking_lot.remove_vehicle(ticket3)

    print(f"\nAvailable after removal: {parking_lot.get_available_count()}")


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary><b>🔷 Go Implementation</b> (Click to expand)</summary>

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

// ============================================================================
// Enums (using constants and types)
// ============================================================================
type VehicleType string
type SpotType string

const (
	BIKE  VehicleType = "BIKE"
	CAR   VehicleType = "CAR"
	TRUCK VehicleType = "TRUCK"
)

const (
	SMALL  SpotType = "SMALL"
	MEDIUM SpotType = "MEDIUM"
	LARGE  SpotType = "LARGE"
)

// ============================================================================
// Vehicle Interface and Implementations
// ============================================================================
type Vehicle interface {
	GetLicensePlate() string
	GetVehicleType() VehicleType
	GetRequiredSpotType() SpotType
}

// Bike
type Bike struct {
	LicensePlate string
}

func (b *Bike) GetLicensePlate() string {
	return b.LicensePlate
}

func (b *Bike) GetVehicleType() VehicleType {
	return BIKE
}

func (b *Bike) GetRequiredSpotType() SpotType {
	return SMALL
}

// Car
type Car struct {
	LicensePlate string
}

func (c *Car) GetLicensePlate() string {
	return c.LicensePlate
}

func (c *Car) GetVehicleType() VehicleType {
	return CAR
}

func (c *Car) GetRequiredSpotType() SpotType {
	return MEDIUM
}

// Truck
type Truck struct {
	LicensePlate string
}

func (t *Truck) GetLicensePlate() string {
	return t.LicensePlate
}

func (t *Truck) GetVehicleType() VehicleType {
	return TRUCK
}

func (t *Truck) GetRequiredSpotType() SpotType {
	return LARGE
}

// ============================================================================
// Parking Spot
// ============================================================================
type ParkingSpot struct {
	SpotID      int
	SpotType    SpotType
	Vehicle     Vehicle
	IsAvailable bool
	mu          sync.Mutex
}

func NewParkingSpot(spotID int, spotType SpotType) *ParkingSpot {
	return &ParkingSpot{
		SpotID:      spotID,
		SpotType:    spotType,
		IsAvailable: true,
	}
}

func (ps *ParkingSpot) CanFitVehicle(v Vehicle) bool {
	ps.mu.Lock()
	defer ps.mu.Unlock()

	if !ps.IsAvailable {
		return false
	}

	required := v.GetRequiredSpotType()
	if ps.SpotType == SMALL && required == SMALL {
		return true
	}
	if ps.SpotType == MEDIUM && (required == SMALL || required == MEDIUM) {
		return true
	}
	if ps.SpotType == LARGE {
		return true
	}
	return false
}

func (ps *ParkingSpot) ParkVehicle(v Vehicle) bool {
	ps.mu.Lock()
	defer ps.mu.Unlock()

	if !ps.IsAvailable {
		return false
	}

	ps.Vehicle = v
	ps.IsAvailable = false
	return true
}

func (ps *ParkingSpot) RemoveVehicle() Vehicle {
	ps.mu.Lock()
	defer ps.mu.Unlock()

	v := ps.Vehicle
	ps.Vehicle = nil
	ps.IsAvailable = true
	return v
}

// ============================================================================
// Ticket
// ============================================================================
type Ticket struct {
	TicketID  int
	Vehicle   Vehicle
	Spot      *ParkingSpot
	EntryTime time.Time
	ExitTime  *time.Time
}

var ticketCounter = 0

func NewTicket(vehicle Vehicle, spot *ParkingSpot) *Ticket {
	ticketCounter++
	return &Ticket{
		TicketID:  ticketCounter,
		Vehicle:   vehicle,
		Spot:      spot,
		EntryTime: time.Now(),
	}
}

func (t *Ticket) GetParkingDurationHours() float64 {
	var end time.Time
	if t.ExitTime == nil {
		end = time.Now()
	} else {
		end = *t.ExitTime
	}
	duration := end.Sub(t.EntryTime).Hours()
	if duration < 0.1 {
		return 0.1 // Minimum 0.1 hour
	}
	return duration
}

// ============================================================================
// Pricing Strategy
// ============================================================================
type PricingStrategy interface {
	CalculateFee(ticket *Ticket) float64
}

type HourlyPricing struct {
	Rates map[VehicleType]float64
}

func NewHourlyPricing() *HourlyPricing {
	return &HourlyPricing{
		Rates: map[VehicleType]float64{
			BIKE:  5.0,
			CAR:   10.0,
			TRUCK: 20.0,
		},
	}
}

func (hp *HourlyPricing) CalculateFee(ticket *Ticket) float64 {
	hours := ticket.GetParkingDurationHours()
	rate := hp.Rates[ticket.Vehicle.GetVehicleType()]
	return hours * rate
}

// ============================================================================
// Parking Lot (Singleton)
// ============================================================================
type ParkingLot struct {
	Spots          []*ParkingSpot
	ActiveTickets  map[int]*Ticket
	PricingStrategy PricingStrategy
	mu             sync.Mutex
}

var (
	instance *ParkingLot
	once     sync.Once
)

func GetParkingLot() *ParkingLot {
	once.Do(func() {
		instance = &ParkingLot{
			Spots:          make([]*ParkingSpot, 0),
			ActiveTickets:  make(map[int]*Ticket),
			PricingStrategy: NewHourlyPricing(),
		}
	})
	return instance
}

func (pl *ParkingLot) AddSpot(spotType SpotType) *ParkingSpot {
	pl.mu.Lock()
	defer pl.mu.Unlock()

	spotID := len(pl.Spots) + 1
	spot := NewParkingSpot(spotID, spotType)
	pl.Spots = append(pl.Spots, spot)
	return spot
}

func (pl *ParkingLot) FindAvailableSpot(v Vehicle) *ParkingSpot {
	for _, spot := range pl.Spots {
		if spot.CanFitVehicle(v) {
			return spot
		}
	}
	return nil
}

func (pl *ParkingLot) ParkVehicle(v Vehicle) *Ticket {
	spot := pl.FindAvailableSpot(v)
	if spot == nil {
		fmt.Printf("❌ No available spot for %s\n", v.GetVehicleType())
		return nil
	}

	spot.ParkVehicle(v)
	ticket := NewTicket(v, spot)

	pl.mu.Lock()
	pl.ActiveTickets[ticket.TicketID] = ticket
	pl.mu.Unlock()

	fmt.Printf("✅ Parked %s at spot %d\n", v.GetLicensePlate(), spot.SpotID)
	return ticket
}

func (pl *ParkingLot) RemoveVehicle(ticket *Ticket) float64 {
	pl.mu.Lock()
	if _, exists := pl.ActiveTickets[ticket.TicketID]; !exists {
		pl.mu.Unlock()
		panic("Invalid ticket")
	}
	pl.mu.Unlock()

	now := time.Now()
	ticket.ExitTime = &now
	fee := pl.PricingStrategy.CalculateFee(ticket)

	ticket.Spot.RemoveVehicle()

	pl.mu.Lock()
	delete(pl.ActiveTickets, ticket.TicketID)
	pl.mu.Unlock()

	fmt.Printf("💵 Fee for %s: $%.2f\n", ticket.Vehicle.GetLicensePlate(), fee)
	return fee
}

func (pl *ParkingLot) GetAvailableCount() int {
	count := 0
	for _, spot := range pl.Spots {
		if spot.IsAvailable {
			count++
		}
	}
	return count
}

// ============================================================================
// Main
// ============================================================================
func main() {
	fmt.Println("============================================================")
	fmt.Println("GO: Parking Lot System")
	fmt.Println("============================================================")

	parkingLot := GetParkingLot()

	// Add spots
	for i := 0; i < 5; i++ {
		parkingLot.AddSpot(SMALL)
	}
	for i := 0; i < 10; i++ {
		parkingLot.AddSpot(MEDIUM)
	}
	for i := 0; i < 5; i++ {
		parkingLot.AddSpot(LARGE)
	}

	fmt.Printf("\nTotal spots: %d\n", len(parkingLot.Spots))
	fmt.Printf("Available: %d\n\n", parkingLot.GetAvailableCount())

	// Park vehicles
	bike := &Bike{LicensePlate: "BIKE-001"}
	car := &Car{LicensePlate: "CAR-001"}
	truck := &Truck{LicensePlate: "TRUCK-001"}

	ticket1 := parkingLot.ParkVehicle(bike)
	ticket2 := parkingLot.ParkVehicle(car)
	ticket3 := parkingLot.ParkVehicle(truck)

	fmt.Printf("\nAvailable after parking: %d\n\n", parkingLot.GetAvailableCount())

	// Remove vehicles
	time.Sleep(1 * time.Second)

	parkingLot.RemoveVehicle(ticket1)
	parkingLot.RemoveVehicle(ticket2)
	parkingLot.RemoveVehicle(ticket3)

	fmt.Printf("\nAvailable after removal: %d\n", parkingLot.GetAvailableCount())
}
```

</details>

<details>
<summary><b>☕ Java Implementation</b> (Click to expand - similar structure)</summary>

```java
// Similar structure to Python/Go
// Key differences:
// - Explicit interface declarations
// - Public/private keywords
// - More verbose generics
// Full implementation available in repo
```

</details>

<details>
<summary><b>💛 JavaScript Implementation</b> (Click to expand - similar structure)</summary>

```javascript
// Similar structure to Python/Go
// Key differences:
// - No explicit interfaces (duck typing or use classes)
// - Async patterns if needed
// - Private fields with #
// Full implementation available in repo
```

</details>

### Step 4: Extensions (5 min)

**Interviewer:** "How would you add multiple floors?"

**You:** "I'd create a `Floor` class containing a list of spots, and `ParkingLot` would manage multiple floors. The `findAvailableSpot` method would iterate through floors."

**Interviewer:** "What about different pricing strategies?"

**You:** "We're already using Strategy Pattern. We can add `FlatPricing`, `WeekendPricing`, etc. and swap them at runtime."

---

## Summary: What We Created

### 📁 Folder Structure Created

```
low-level-design/lld-coding/multi-language/
├── README.md                      # Overview
├── QUICK-START.md                 # 10-min getting started
├── LANGUAGE-COMPARISON.md         # Deep comparison
├── OVERVIEW.md                    # Complete guide
│
├── 01-basic-classes/              # Basic OOP
│   ├── bank_account.py           # Python
│   ├── bank_account.go           # Go
│   ├── BankAccount.java          # Java
│   └── bank_account.js           # JavaScript
│
└── 04-page-view-counter/          # Concurrency
    ├── page_view_counter.py      # Python (threading)
    ├── page_view_counter.go      # Go (goroutines)
    ├── PageViewCounter.java      # Java (synchronized)
    └── page_view_counter.js      # JavaScript (workers)
```

### 🎯 What's Included

1. ✅ **Basic Classes Example** - BankAccount in all 4 languages
2. ✅ **Race Condition Demo** - Shows broken and fixed versions
3. ✅ **Condition Examples** - Producer-consumer, connection pool (Python)
4. ✅ **Complete Language Comparison** - When to use what
5. ✅ **Quick Start Guide** - Get running in 10 minutes

### 🚀 Quick Start

```bash
# Navigate to multi-language folder
cd low-level-design/lld-coding/multi-language/

# Try Python (fastest)
python3 01-basic-classes/bank_account.py
python3 04-page-view-counter/page_view_counter.py

# Try Go (true concurrency)
go run 01-basic-classes/bank_account.go
go run 04-page-view-counter/page_view_counter.go

# Try Java (enterprise standard)
cd 01-basic-classes && javac BankAccount.java && java BankAccount

# Try JavaScript (web/full-stack)
node 01-basic-classes/bank_account.js
node 04-page-view-counter/page_view_counter.js
```

### 📖 Recommended Learning Path

1. **Read** [QUICK-START.md](low-level-design/lld-coding/multi-language/QUICK-START.md) (10 min)
2. **Run** basic classes in your language (5 min)
3. **Run** race condition demo (10 min)
4. **Read** [LANGUAGE-COMPARISON.md](low-level-design/lld-coding/multi-language/LANGUAGE-COMPARISON.md) (30 min)
5. **Practice** rewriting one problem in all 4 languages

### 🎓 Key Takeaways

**Python:**
- ✅ Fastest to write
- ✅ Most readable
- ⚠️ GIL limits concurrency

**Go:**
- ✅ True parallelism
- ✅ Simple syntax
- ⚠️ No classes (uses structs)

**Java:**
- ✅ Strong typing
- ✅ Industry standard
- ⚠️ Most verbose

**JavaScript:**
- ✅ Full-stack capability
- ✅ Async-first
- ⚠️ Single-threaded by default

**Remember:** Design principles (SOLID, patterns) are the same across all languages - only syntax differs!

All examples are fully tested and runnable. Check the [INDEX.md](low-level-design/INDEX.md) for the updated structure with multi-language examples added! 🎯