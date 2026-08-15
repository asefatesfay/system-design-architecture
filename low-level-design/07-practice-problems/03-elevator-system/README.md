# Design an Elevator System

> **🌍 Multi-Language Note:** This solution is in Python. For implementations in other languages:
> - [Language Comparison Guide](../../lld-coding/multi-language/LANGUAGE-COMPARISON.md)
> - [Core OOP Multi-Language Examples](../../03-oop-fundamentals/four-pillars/)

## Problem Statement

Design an elevator control system for a building that can:
1. Handle multiple elevators
2. Process floor requests (both inside and outside elevator)
3. Optimize elevator assignment
4. Handle emergency situations
5. Maintain door operations
6. Track elevator state and position

## Difficulty Level
**Medium-Hard** - 60-90 minutes

## Requirements Clarification

### Functional Requirements
1. Multiple elevators in a building
2. Each elevator has capacity limit
3. Handle up and down button requests from floors
4. Handle floor selection from inside elevator
5. Doors open/close automatically
6. Emergency button
7. Display current floor
8. Optimize which elevator responds to request

### Non-Functional Requirements
1. Minimize wait time
2. Energy efficient (don't send empty elevators)
3. Thread-safe operations
4. Handle edge cases (power failure, stuck elevator)

### Constraints
1. Building has N floors (0 to N-1)
2. Each elevator has weight limit
3. Doors stay open for fixed duration
4. Cannot exceed maximum speed

## Core Design Decisions

### Design Patterns Used
1. **State Pattern** - Elevator states (Idle, Moving Up, Moving Down, Maintenance)
2. **Strategy Pattern** - Different scheduling algorithms
3. **Singleton Pattern** - Elevator controller
4. **Observer Pattern** - Notify displays of elevator position

### Algorithms
1. **SCAN (Elevator Algorithm)** - Continue in same direction
2. **LOOK** - Reverse when no more requests
3. **Shortest Seek Time First (SSTF)** - Closest request first

## Complete Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Set, Optional
from dataclasses import dataclass
import threading
import time
from queue import PriorityQueue

# ============= ENUMS =============

class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class ElevatorState(Enum):
    IDLE = "IDLE"
    MOVING_UP = "MOVING_UP"
    MOVING_DOWN = "MOVING_DOWN"
    DOOR_OPEN = "DOOR_OPEN"
    DOOR_CLOSED = "DOOR_CLOSED"
    MAINTENANCE = "MAINTENANCE"
    EMERGENCY = "EMERGENCY"

class RequestType(Enum):
    INTERNAL = "INTERNAL"  # From inside elevator
    EXTERNAL = "EXTERNAL"  # From floor buttons

# ============= REQUEST =============

@dataclass
class ElevatorRequest:
    floor: int
    direction: Direction
    request_type: RequestType
    timestamp: float

    def __lt__(self, other):
        return self.timestamp < other.timestamp

# ============= ELEVATOR =============

class Elevator:
    """Represents a single elevator"""

    def __init__(self, elevator_id: int, total_floors: int, capacity: int = 10):
        self.elevator_id = elevator_id
        self.total_floors = total_floors
        self.capacity = capacity

        self.current_floor = 0
        self.current_direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self.current_load = 0

        # Requests to service
        self.up_requests: Set[int] = set()
        self.down_requests: Set[int] = set()

        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_request(self, floor: int, direction: Direction):
        """Add a floor request"""
        with self._lock:
            if direction == Direction.UP or direction == Direction.IDLE:
                self.up_requests.add(floor)
            if direction == Direction.DOWN or direction == Direction.IDLE:
                self.down_requests.add(floor)

    def has_requests(self) -> bool:
        """Check if elevator has pending requests"""
        with self._lock:
            return len(self.up_requests) > 0 or len(self.down_requests) > 0

    def move_to_floor(self, target_floor: int):
        """Move elevator to target floor"""
        if target_floor == self.current_floor:
            self._open_doors()
            return

        # Determine direction
        if target_floor > self.current_floor:
            self.current_direction = Direction.UP
            self.state = ElevatorState.MOVING_UP
        else:
            self.current_direction = Direction.DOWN
            self.state = ElevatorState.MOVING_DOWN

        print(f"🔼 Elevator {self.elevator_id}: Moving {self.current_direction.name} from floor {self.current_floor}")

        # Simulate movement
        while self.current_floor != target_floor:
            time.sleep(0.5)  # Simulate time to move one floor
            self.current_floor += self.current_direction.value
            print(f"   Elevator {self.elevator_id} at floor {self.current_floor}")

            # Check if any request at this floor in current direction
            self._check_stops()

        self._open_doors()

    def _check_stops(self):
        """Check if should stop at current floor"""
        with self._lock:
            if self.current_direction == Direction.UP:
                if self.current_floor in self.up_requests:
                    self._open_doors()
                    self.up_requests.remove(self.current_floor)
            elif self.current_direction == Direction.DOWN:
                if self.current_floor in self.down_requests:
                    self._open_doors()
                    self.down_requests.remove(self.current_floor)

    def _open_doors(self):
        """Open elevator doors"""
        with self._lock:
            print(f"🚪 Elevator {self.elevator_id}: Doors opening at floor {self.current_floor}")
            self.state = ElevatorState.DOOR_OPEN
            time.sleep(1)  # Doors stay open
            self._close_doors()

    def _close_doors(self):
        """Close elevator doors"""
        print(f"🚪 Elevator {self.elevator_id}: Doors closing at floor {self.current_floor}")
        self.state = ElevatorState.DOOR_CLOSED

    def get_next_floor(self) -> Optional[int]:
        """Get next floor to service using SCAN algorithm"""
        with self._lock:
            if self.current_direction == Direction.UP or self.current_direction == Direction.IDLE:
                # Check floors above
                above = [f for f in self.up_requests if f > self.current_floor]
                if above:
                    return min(above)

                # No more up requests, check down requests
                below = [f for f in self.down_requests if f < self.current_floor]
                if below:
                    self.current_direction = Direction.DOWN
                    return max(below)

            elif self.current_direction == Direction.DOWN:
                # Check floors below
                below = [f for f in self.down_requests if f < self.current_floor]
                if below:
                    return max(below)

                # No more down requests, check up requests
                above = [f for f in self.up_requests if f > self.current_floor]
                if above:
                    self.current_direction = Direction.UP
                    return min(above)

            # No more requests
            self.current_direction = Direction.IDLE
            self.state = ElevatorState.IDLE
            return None

    def run(self):
        """Main elevator loop"""
        self._running = True
        while self._running:
            next_floor = self.get_next_floor()
            if next_floor is not None:
                self.move_to_floor(next_floor)
            else:
                print(f"😴 Elevator {self.elevator_id}: Idle at floor {self.current_floor}")
                time.sleep(1)

    def start(self):
        """Start elevator operation"""
        if not self._thread:
            self._thread = threading.Thread(target=self.run, daemon=True)
            self._thread.start()

    def stop(self):
        """Stop elevator operation"""
        self._running = False
        if self._thread:
            self._thread.join()

    def emergency_stop(self):
        """Emergency stop"""
        with self._lock:
            self.state = ElevatorState.EMERGENCY
            self._running = False
            print(f"🚨 Elevator {self.elevator_id}: EMERGENCY STOP at floor {self.current_floor}")

    def __str__(self):
        return (f"Elevator {self.elevator_id}: Floor {self.current_floor}, "
                f"State: {self.state.name}, Direction: {self.current_direction.name}")

# ============= SCHEDULING STRATEGIES =============

class ElevatorScheduler(ABC):
    """Abstract scheduler for elevator assignment"""

    @abstractmethod
    def select_elevator(self, elevators: List[Elevator], request_floor: int,
                       direction: Direction) -> Optional[Elevator]:
        pass

class NearestElevatorScheduler(ElevatorScheduler):
    """Assign request to nearest elevator"""

    def select_elevator(self, elevators: List[Elevator], request_floor: int,
                       direction: Direction) -> Optional[Elevator]:
        nearest = None
        min_distance = float('inf')

        for elevator in elevators:
            if elevator.state == ElevatorState.MAINTENANCE:
                continue

            distance = abs(elevator.current_floor - request_floor)

            # Prefer elevator already moving in same direction
            if elevator.current_direction == direction:
                distance *= 0.5

            if distance < min_distance:
                min_distance = distance
                nearest = elevator

        return nearest

class LeastLoadedScheduler(ElevatorScheduler):
    """Assign request to elevator with least requests"""

    def select_elevator(self, elevators: List[Elevator], request_floor: int,
                       direction: Direction) -> Optional[Elevator]:
        least_loaded = None
        min_requests = float('inf')

        for elevator in elevators:
            if elevator.state == ElevatorState.MAINTENANCE:
                continue

            request_count = len(elevator.up_requests) + len(elevator.down_requests)

            if request_count < min_requests:
                min_requests = request_count
                least_loaded = elevator

        return least_loaded

class ZoneBasedScheduler(ElevatorScheduler):
    """Assign elevators to specific floor zones"""

    def __init__(self, total_floors: int, num_elevators: int):
        self.total_floors = total_floors
        self.zone_size = total_floors // num_elevators

    def select_elevator(self, elevators: List[Elevator], request_floor: int,
                       direction: Direction) -> Optional[Elevator]:
        # Determine zone
        zone = request_floor // self.zone_size
        zone = min(zone, len(elevators) - 1)

        # Try to assign to zone elevator
        zone_elevator = elevators[zone]
        if zone_elevator.state != ElevatorState.MAINTENANCE:
            return zone_elevator

        # Fallback to nearest
        return NearestElevatorScheduler().select_elevator(elevators, request_floor, direction)

# ============= ELEVATOR CONTROLLER =============

class ElevatorController:
    """Controls multiple elevators (Singleton)"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, num_elevators: int = 3, total_floors: int = 10):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, num_elevators: int = 3, total_floors: int = 10):
        if not hasattr(self, 'initialized'):
            self.total_floors = total_floors
            self.elevators = [
                Elevator(i, total_floors)
                for i in range(num_elevators)
            ]
            self.scheduler: ElevatorScheduler = NearestElevatorScheduler()
            self.pending_requests: PriorityQueue = PriorityQueue()
            self.initialized = True

    def set_scheduler(self, scheduler: ElevatorScheduler):
        """Set scheduling strategy"""
        self.scheduler = scheduler

    def request_elevator(self, floor: int, direction: Direction):
        """Request an elevator from a floor"""
        print(f"\n📞 Floor {floor} requesting elevator going {direction.name}")

        elevator = self.scheduler.select_elevator(self.elevators, floor, direction)

        if elevator:
            print(f"   → Assigned Elevator {elevator.elevator_id}")
            elevator.add_request(floor, direction)
        else:
            print(f"   ⚠️  No elevator available")

    def press_floor_button(self, elevator_id: int, floor: int):
        """Press floor button inside elevator"""
        if 0 <= elevator_id < len(self.elevators):
            elevator = self.elevators[elevator_id]
            print(f"\n🔘 Button pressed: Floor {floor} in Elevator {elevator_id}")

            # Determine direction
            if floor > elevator.current_floor:
                direction = Direction.UP
            elif floor < elevator.current_floor:
                direction = Direction.DOWN
            else:
                direction = Direction.IDLE

            elevator.add_request(floor, direction)

    def start_all(self):
        """Start all elevators"""
        print("🚀 Starting all elevators...\n")
        for elevator in self.elevators:
            elevator.start()

    def stop_all(self):
        """Stop all elevators"""
        print("\n🛑 Stopping all elevators...")
        for elevator in self.elevators:
            elevator.stop()

    def display_status(self):
        """Display status of all elevators"""
        print("\n" + "="*70)
        print("ELEVATOR SYSTEM STATUS")
        print("="*70)
        for elevator in self.elevators:
            print(elevator)
        print("="*70 + "\n")

    def emergency_stop_all(self):
        """Emergency stop all elevators"""
        print("\n🚨 EMERGENCY: Stopping all elevators!")
        for elevator in self.elevators:
            elevator.emergency_stop()

# ============= DEMO USAGE =============

def main():
    print("🏢 ELEVATOR CONTROL SYSTEM 🏢\n")

    # Create controller with 3 elevators, 10 floors
    controller = ElevatorController(num_elevators=3, total_floors=10)
    controller.start_all()

    time.sleep(1)
    controller.display_status()

    # Scenario 1: Multiple floor requests
    print("\n" + "="*70)
    print("SCENARIO 1: Multiple people requesting elevators")
    print("="*70)

    controller.request_elevator(floor=5, direction=Direction.UP)
    controller.request_elevator(floor=7, direction=Direction.DOWN)
    controller.request_elevator(floor=2, direction=Direction.UP)

    time.sleep(5)
    controller.display_status()

    # Scenario 2: Internal button presses
    print("\n" + "="*70)
    print("SCENARIO 2: Passengers pressing floor buttons")
    print("="*70)

    controller.press_floor_button(elevator_id=0, floor=8)
    controller.press_floor_button(elevator_id=1, floor=3)
    controller.press_floor_button(elevator_id=2, floor=9)

    time.sleep(5)
    controller.display_status()

    # Scenario 3: Heavy traffic
    print("\n" + "="*70)
    print("SCENARIO 3: Heavy traffic simulation")
    print("="*70)

    for floor in [1, 3, 5, 7, 9]:
        controller.request_elevator(floor, Direction.UP)

    time.sleep(10)

    # Scenario 4: Change scheduling strategy
    print("\n" + "="*70)
    print("SCENARIO 4: Switching to Zone-Based Scheduler")
    print("="*70)

    controller.set_scheduler(ZoneBasedScheduler(total_floors=10, num_elevators=3))
    controller.request_elevator(floor=2, direction=Direction.UP)
    controller.request_elevator(floor=5, direction=Direction.UP)
    controller.request_elevator(floor=8, direction=Direction.DOWN)

    time.sleep(10)

    # Display final status
    controller.display_status()

    # Stop all elevators
    controller.stop_all()
    print("\n✅ System shutdown complete")

if __name__ == "__main__":
    main()
```

## Key Design Decisions

### 1. SCAN Algorithm
- Elevator continues in current direction
- Services all requests in that direction
- Reverses when no more requests

### 2. Scheduling Strategies
- **Nearest**: Minimize wait time
- **Least Loaded**: Balance load across elevators
- **Zone-Based**: Divide building into zones

### 3. Thread Safety
- Locks for shared state
- Thread-safe request handling
- Concurrent elevator operations

### 4. SOLID Principles

**Single Responsibility**:
- `Elevator`: Manages single elevator
- `ElevatorController`: Coordinates all elevators
- `ElevatorScheduler`: Handles assignment logic

**Open/Closed**:
- Easy to add new scheduling strategies
- Extend elevator features without modifying core

**Strategy Pattern**:
- Different schedulers interchangeable

## Testing Scenarios

1. ✅ Single elevator, single request
2. ✅ Multiple elevators, multiple requests
3. ✅ Elevator already moving in direction
4. ✅ Heavy traffic handling
5. ✅ Emergency stop
6. ✅ Change scheduling strategy
7. ✅ Edge cases (top floor, bottom floor)

## Extensions

1. **Priority requests**: VIP/Emergency priority
2. **Energy optimization**: Sleep mode for idle elevators
3. **Predictive algorithms**: ML-based request prediction
4. **Maintenance mode**: Schedule maintenance windows
5. **Load sensors**: Prevent overloading
6. **Door obstruction**: Sensor-based door reopening
7. **Fire mode**: All elevators to ground floor
8. **Statistics**: Track average wait time, usage patterns

## Time Complexity

- Request assignment: O(n) where n = number of elevators
- Find next floor: O(m) where m = pending requests
- Move to floor: O(k) where k = floors to travel

## Interview Discussion Points

1. **Why SCAN algorithm?**
   - Efficient for multiple requests
   - Minimizes direction changes
   - Fair to all requests

2. **How to optimize?**
   - Predictive scheduling
   - Group nearby requests
   - Zone-based assignment

3. **Handling edge cases?**
   - Emergency situations
   - Power failures
   - Stuck doors
   - Overload situations

4. **Scalability?**
   - Support 50+ floors
   - 10+ elevators
   - Distributed control system

---

**Complete!** This demonstrates State Pattern, Strategy Pattern, threading, and real elevator algorithms.
