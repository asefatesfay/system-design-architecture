# Multi-Agent Travel System - Step-by-Step Tutorial

Learn by building! Start simple and add one feature at a time.

## 🎯 Learning Path

```
Step 1: Single Agent (Basic Trip Planner)          ← YOU ARE HERE!
   ↓
Step 2: Add Tools (Flight Search)
   ↓
Step 3: Two Agents (Coordinator + Flight Agent)
   ↓
Step 4: Shared Memory (Agents share data)
```

---

## Step 1: Single Agent (Basic Trip Planner)

**Goal**: Run a simple agent that responds to trip requests.

**What you'll learn**: Basic agent setup, entrypoint, testing

### ✅ Code Already Set Up!

The Step 1 code is already in `src/multi_agent_travel_system/main.py`.

Let's look at the key parts:

```python
# Create the agent
travel_agent = Agent(
    model=config.BEDROCK_MODEL,
    system_prompt="You are a helpful travel planning assistant..."
)

# Define an endpoint
@app.entrypoint
def plan_trip(payload):
    user_message = payload.get("message", "I want to plan a trip")
    result = travel_agent(user_message)
    return {"response": result.message}
```

### Run It!

```bash
# Navigate to project
cd ai-corner/aws-agentcore/multi-agent-travel-system

# Set AWS profile
export AWS_PROFILE=admin-user

# Run the application
uv run python -m multi_agent_travel_system.main
```

You should see:
```
🌍 Multi-Agent Travel System
==================================================
✓ AWS Profile: admin-user
✓ AWS Region: us-west-2
✓ Bedrock Model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
✓ Travel Agent created
==================================================
🚀 Server starting on http://localhost:8080
==================================================
```

### Test It!

Open a **new terminal** and run:

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to visit Paris"}' \
  | jq
```

**Expected Output**:
```json
{
  "response": "Great! Paris is a wonderful destination! To help you plan, I need:\n1. When do you want to travel?\n2. How many days?\n3. How many people?\n4. What's your budget?"
}
```

### ✅ Step 1 Complete!

**What you learned**:
- How to run the agent
- How to test with curl
- Agent responds but has no tools yet (can't search flights)

---

## Step 2: Add Tools (Flight Search)

**Goal**: Give your agent the ability to search for flights.

**What you'll learn**: Creating tools, registering them with agents

### Create Flight Tools

Create the file `src/multi_agent_travel_system/tools/flight_tools.py`:

```python
"""Flight search and booking tools"""


def search_flights(origin: str, destination: str, date: str, passengers: int = 1):
    """
    Search for available flights.

    Args:
        origin: Origin city code (e.g., 'NYC', 'LAX')
        destination: Destination city code (e.g., 'CDG', 'LHR')
        date: Departure date (YYYY-MM-DD)
        passengers: Number of passengers

    Returns:
        List of available flights with prices
    """
    # Mock data for learning - you'll add real APIs later
    flights = [
        {
            "id": "FL001",
            "airline": "Delta",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "08:00 AM",
            "arrival": "09:30 PM",
            "duration": "7h 30m",
            "stops": 0,
            "price_per_person": 450,
            "total_price": 450 * passengers,
            "available_seats": 20
        },
        {
            "id": "FL002",
            "airline": "Air France",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "10:30 AM",
            "arrival": "11:45 PM",
            "duration": "7h 15m",
            "stops": 0,
            "price_per_person": 520,
            "total_price": 520 * passengers,
            "available_seats": 15
        },
        {
            "id": "FL003",
            "airline": "United",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "02:00 PM",
            "arrival": "03:30 AM +1",
            "duration": "7h 30m",
            "stops": 1,
            "price_per_person": 380,
            "total_price": 380 * passengers,
            "available_seats": 8
        }
    ]
    return flights


def get_flight_details(flight_id: str):
    """
    Get detailed information about a specific flight.

    Args:
        flight_id: Flight identifier (e.g., 'FL001')

    Returns:
        Detailed flight information
    """
    flight_db = {
        "FL001": {
            "id": "FL001",
            "airline": "Delta",
            "flight_number": "DL123",
            "aircraft": "Boeing 777",
            "amenities": ["WiFi", "Meals", "Entertainment"],
            "baggage": "1 checked bag included",
            "cancellation_policy": "Free cancellation up to 24h before"
        },
        "FL002": {
            "id": "FL002",
            "airline": "Air France",
            "flight_number": "AF456",
            "aircraft": "Airbus A350",
            "amenities": ["WiFi", "Premium meals", "Entertainment"],
            "baggage": "2 checked bags included",
            "cancellation_policy": "Free cancellation up to 48h before"
        },
        "FL003": {
            "id": "FL003",
            "airline": "United",
            "flight_number": "UA789",
            "aircraft": "Boeing 787",
            "amenities": ["Entertainment", "Snacks"],
            "baggage": "1 checked bag ($35 fee)",
            "cancellation_policy": "Non-refundable"
        }
    }
    return flight_db.get(flight_id, {"error": "Flight not found"})
```

### Update main.py to Use Tools

Edit `src/multi_agent_travel_system/main.py`:

**Find this section (around line 20):**
```python
# STEP 1: Simple Travel Agent
# This will be expanded in later steps
travel_agent = None


def create_travel_agent():
    """Create the main travel agent (Step 1)"""
    global travel_agent
    travel_agent = Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""You are a helpful travel planning assistant.
        Help users plan trips by asking about destination, dates, budget, and interests.
        Be friendly and ask clarifying questions."""
    )
    print("✓ Travel Agent created")
```

**Replace it with:**
```python
# STEP 2: Travel Agent with Flight Tools
from .tools.flight_tools import search_flights, get_flight_details

travel_agent = None


def create_travel_agent():
    """Create the main travel agent with flight tools (Step 2)"""
    global travel_agent
    travel_agent = Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""You are a travel planning assistant with flight search capabilities.

        When users ask about flights:
        1. Use search_flights() to find available options
        2. Present results clearly: airline, price, duration, stops
        3. Use get_flight_details() if they want more information
        4. Help them choose based on their preferences

        Be helpful and conversational!
        """,
        tools=[search_flights, get_flight_details]
    )
    print("✓ Travel Agent created with flight tools")
```

### Test It!

```bash
# Stop the server (Ctrl+C) and restart
uv run python -m multi_agent_travel_system.main
```

```bash
# In another terminal, test flight search
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "Find flights from NYC to Paris on March 15 for 2 people"}' \
  | jq
```

**Expected Output**:
```json
{
  "response": "I found 3 flights from NYC to Paris on March 15 for 2 passengers:\n\n1. **Delta (FL001)** - $900 total\n   - Departs: 8:00 AM, Arrives: 9:30 PM\n   - Non-stop, 7h 30m\n   - 20 seats available\n\n2. **Air France (FL002)** - $1,040 total\n   - Departs: 10:30 AM, Arrives: 11:45 PM\n   - Non-stop, 7h 15m\n   - 15 seats available\n\n3. **United (FL003)** - $760 total\n   - Departs: 2:00 PM, Arrives: 3:30 AM next day\n   - 1 stop, 7h 30m\n   - 8 seats available\n\nThe United flight is cheapest but has a stop. Would you like details on any of these?"
}
```

**🎉 Magic!** The agent automatically called `search_flights()` when you asked!

### ✅ Step 2 Complete!

**What you learned**:
- Create tools (just Python functions!)
- Import and register tools with agents
- Agents automatically use tools when needed

---

## Step 3: Multiple Agents (Coordinator + Specialists)

**Goal**: Create specialized agents that work together.

**What you'll learn**: Agent delegation, specialization, coordination

### Create Flight Agent

Create `src/multi_agent_travel_system/agents/flight_agent.py`:

```python
"""Specialized agent for flight operations"""
from strands import Agent
from ..config import config
from ..tools.flight_tools import search_flights, get_flight_details


def create_flight_agent():
    """Create a specialized flight search agent"""
    return Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""You are a flight search specialist.

        Your ONLY job is to help with flights:
        - Search for flights using search_flights()
        - Provide flight details using get_flight_details()
        - Compare options and recommend the best choice
        - Consider: price, duration, stops, departure times

        Do NOT handle hotels, activities, or other travel aspects.
        Stay focused on flights!
        """,
        tools=[search_flights, get_flight_details]
    )
```

### Create Coordinator Agent

Create `src/multi_agent_travel_system/agents/coordinator.py`:

```python
"""Coordinator agent that delegates to specialists"""
from strands import Agent
from ..config import config


def create_coordinator(flight_agent):
    """
    Create coordinator agent that manages specialists.

    Args:
        flight_agent: The flight specialist agent

    Returns:
        Coordinator agent that can delegate to specialists
    """

    def ask_flight_agent(query: str):
        """
        Delegate flight-related questions to the flight specialist.

        Args:
            query: The flight-related question or request

        Returns:
            Response from flight agent
        """
        result = flight_agent(query)
        return result.message

    coordinator = Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""You are a travel planning coordinator.

        Your job: understand requests and delegate to specialists.

        FOR FLIGHTS → use ask_flight_agent(query)
        Examples:
        - "Find flights to Paris"
        - "Search flights from NYC on March 15"
        - "What are the cheapest flights?"

        FOR GENERAL PLANNING → handle yourself
        - "What should I see in Paris?"
        - "Tell me about Paris"

        COMPLEX REQUESTS → delegate + add your own suggestions
        User: "Plan a 3-day trip to Paris"
        You:
        1. ask_flight_agent("Find flights to Paris")
        2. Then YOU suggest hotels and activities

        Coordinate specialists to create complete travel plans!
        """,
        tools=[ask_flight_agent]
    )

    return coordinator
```

### Update Main to Use Multiple Agents

Edit `src/multi_agent_travel_system/main.py`:

**Find the import section and replace:**
```python
from .tools.flight_tools import search_flights, get_flight_details
```

**With:**
```python
from .agents.coordinator import create_coordinator
from .agents.flight_agent import create_flight_agent
```

**Find the agent creation section and replace:**
```python
# STEP 2: Travel Agent with Flight Tools
from .tools.flight_tools import search_flights, get_flight_details

travel_agent = None


def create_travel_agent():
    """Create the main travel agent with flight tools (Step 2)"""
    global travel_agent
    travel_agent = Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""...""",
        tools=[search_flights, get_flight_details]
    )
    print("✓ Travel Agent created with flight tools")
```

**With:**
```python
# STEP 3: Multiple Agents (Coordinator + Specialists)
coordinator_agent = None
flight_agent = None


def create_agents():
    """Create coordinator and specialized agents (Step 3)"""
    global coordinator_agent, flight_agent

    # Create specialists first
    flight_agent = create_flight_agent()
    print("✓ Flight Agent created")

    # Create coordinator that manages specialists
    coordinator_agent = create_coordinator(flight_agent)
    print("✓ Coordinator Agent created")
```

**Update the entrypoint:**
```python
@app.entrypoint
def plan_trip(payload):
    """
    Main endpoint for trip planning

    Now uses coordinator + specialists! (Step 3)
    """
    user_message = payload.get("message", "I want to plan a trip")

    # Coordinator handles request and delegates as needed
    result = coordinator_agent(user_message)

    return {"response": result.message}
```

**Update the main() function:**

**Find:**
```python
def main():
    """Main entry point"""
    print("🌍 Multi-Agent Travel System")
    print("=" * 50)

    # Setup
    setup_environment()
    create_travel_agent()
```

**Change to:**
```python
def main():
    """Main entry point"""
    print("🌍 Multi-Agent Travel System")
    print("=" * 50)

    # Setup
    setup_environment()
    create_agents()  # Changed from create_travel_agent()
```

### Test It!

```bash
# Restart the server
uv run python -m multi_agent_travel_system.main
```

You should see:
```
✓ Flight Agent created
✓ Coordinator Agent created
```

```bash
# Test delegation
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to go to Paris for 3 days. Find me flights from NYC on March 15 for 2 people."}' \
  | jq
```

**What happens behind the scenes**:
1. Coordinator receives request
2. Coordinator identifies flight part
3. Coordinator calls: `ask_flight_agent("Find flights from NYC to Paris...")`
4. Flight Agent calls: `search_flights(...)`
5. Flight Agent returns results
6. Coordinator adds hotel/activity suggestions

### ✅ Step 3 Complete!

**What you learned**:
- Create specialized agents (single responsibility)
- Agents can delegate to other agents
- Coordinator pattern for multi-agent systems

---

## Step 4: Shared Memory (Agents Remember)

**Goal**: Agents remember context and share trip information.

**What you'll learn**: State management, persistent context

### Create Trip Model

Create `src/multi_agent_travel_system/models/trip.py`:

```python
"""Trip data model"""
from typing import Dict, Any, Optional
from datetime import datetime


class Trip:
    """Represents a travel trip with all bookings and details"""

    def __init__(self, trip_id: str, user_message: str):
        self.trip_id = trip_id
        self.created_at = datetime.now().isoformat()
        self.original_request = user_message

        # Trip details
        self.destination: Optional[str] = None
        self.origin: Optional[str] = None
        self.dates = {"start": None, "end": None}
        self.passengers: int = 1
        self.budget: Optional[float] = None

        # Bookings
        self.bookings = {
            "flights": [],
            "hotels": [],
            "activities": []
        }

        # Tracking
        self.total_cost: float = 0.0
        self.status: str = "planning"

    def add_flight(self, flight: Dict[str, Any]):
        """Add a flight booking"""
        self.bookings["flights"].append(flight)
        self.total_cost += flight.get("total_price", 0)

    def add_hotel(self, hotel: Dict[str, Any]):
        """Add a hotel booking"""
        self.bookings["hotels"].append(hotel)
        self.total_cost += hotel.get("total_price", 0)

    def get_summary(self) -> str:
        """Get human-readable trip summary"""
        return f"""
Trip to {self.destination or 'TBD'}
Dates: {self.dates['start'] or 'TBD'} to {self.dates['end'] or 'TBD'}
Passengers: {self.passengers}
Total Cost: ${self.total_cost:.2f}
Budget: ${self.budget or 'Not set'}

Bookings:
- Flights: {len(self.bookings['flights'])}
- Hotels: {len(self.bookings['hotels'])}
- Activities: {len(self.bookings['activities'])}

Status: {self.status}
        """.strip()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "trip_id": self.trip_id,
            "created_at": self.created_at,
            "destination": self.destination,
            "origin": self.origin,
            "dates": self.dates,
            "passengers": self.passengers,
            "budget": self.budget,
            "bookings": self.bookings,
            "total_cost": self.total_cost,
            "status": self.status
        }
```

### Create Memory Manager

Create `src/multi_agent_travel_system/utils/memory.py`:

```python
"""Shared memory for multi-agent system"""
from typing import Dict, Optional
from ..models.trip import Trip


class TripMemory:
    """Shared memory that all agents can access"""

    def __init__(self):
        self.trips: Dict[str, Trip] = {}

    def create_trip(self, trip_id: str, user_message: str) -> Trip:
        """Create a new trip"""
        trip = Trip(trip_id, user_message)
        self.trips[trip_id] = trip
        return trip

    def get_trip(self, trip_id: str) -> Optional[Trip]:
        """Get trip by ID"""
        return self.trips.get(trip_id)

    def update_trip(self, trip_id: str, **kwargs):
        """Update trip details"""
        trip = self.get_trip(trip_id)
        if trip:
            for key, value in kwargs.items():
                if hasattr(trip, key):
                    setattr(trip, key, value)

    def list_trips(self) -> list:
        """List all trips"""
        return [trip.to_dict() for trip in self.trips.values()]


# Global memory instance that persists across requests
trip_memory = TripMemory()
```

### Update Main to Use Memory

Edit `src/multi_agent_travel_system/main.py`:

**Add these imports at the top:**
```python
import uuid
from .utils.memory import trip_memory
```

**Replace the entrypoint:**
```python
@app.entrypoint
def plan_trip(payload):
    """
    Main endpoint for trip planning

    Now with memory! Agents remember context (Step 4)
    """
    user_message = payload.get("message", "I want to plan a trip")
    trip_id = payload.get("trip_id")  # Allow continuing existing trips

    # Create or get trip context
    if not trip_id:
        trip_id = f"trip-{uuid.uuid4().hex[:8]}"
        trip = trip_memory.create_trip(trip_id, user_message)
        print(f"📝 Created new trip: {trip_id}")
    else:
        trip = trip_memory.get_trip(trip_id)
        print(f"📝 Continuing trip: {trip_id}")

    # Add trip context to the message
    context_message = f"""
Current Trip Context:
{trip.get_summary()}

User Message: {user_message}
"""

    # Coordinator processes with full context
    result = coordinator_agent(context_message)

    return {
        "trip_id": trip_id,
        "response": result.message,
        "trip_summary": trip.get_summary(),
        "trip_details": trip.to_dict()
    }
```

### Test It!

```bash
# Restart server
uv run python -m multi_agent_travel_system.main
```

```bash
# First request - creates new trip
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a trip to Paris from NYC for 2 people, budget $3000"}' \
  | jq '.trip_id, .trip_summary'

# You'll see:
# "trip-abc12345"
# "Trip to TBD\nDates: TBD to TBD\n..."

# Save that trip_id! Now continue the conversation:
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"trip_id": "trip-abc12345", "message": "Find flights for March 15"}' \
  | jq '.trip_summary'
```

**What's new**: The agent remembers your destination, budget, and passengers!

### ✅ Step 4 Complete!

**What you learned**:
- Create data models (Trip class)
- Implement shared memory (TripMemory)
- Persist context across requests
- Continue conversations with trip_id

---

## 🎉 You Did It!

### ✅ What You've Built:

- ✅ **Step 1**: Basic agent with conversational skills
- ✅ **Step 2**: Agent with flight search tools
- ✅ **Step 3**: Multiple specialized agents working together
- ✅ **Step 4**: Persistent memory across requests

### 📁 Your Project Structure:

```
src/multi_agent_travel_system/
├── __init__.py
├── main.py                 # Main entry point ✓
├── config.py               # Configuration ✓
├── agents/
│   ├── __init__.py
│   ├── coordinator.py      # Delegates to specialists ✓
│   └── flight_agent.py     # Flight specialist ✓
├── tools/
│   ├── __init__.py
│   └── flight_tools.py     # Flight search tools ✓
├── models/
│   ├── __init__.py
│   └── trip.py             # Trip data model ✓
└── utils/
    ├── __init__.py
    └── memory.py           # Shared memory ✓
```

### 🚀 What's Next?

You can now:
1. **Experiment**: Try different prompts, change agent behaviors
2. **Extend**: Add hotel agent, budget agent (follow same patterns!)
3. **Deploy**: Move to AWS Lambda (see README.md)
4. **Real APIs**: Replace mock data with real flight APIs

### 💡 Key Patterns You Learned:

1. **Tools Pattern**: Python functions become agent capabilities
2. **Delegation Pattern**: Coordinator delegates to specialists
3. **Memory Pattern**: Shared state across agent calls
4. **Package Structure**: Clean organization as you scale

## 📚 Reference

- **QUICKSTART.md** - Quick setup guide
- **PROJECT-STRUCTURE.md** - File organization details
- **README.md** - Complete system overview

## Need Help?

Common issues:
- **Import errors**: Check you're in the project root
- **AWS errors**: Ensure `AWS_PROFILE` is set
- **Module not found**: Run `uv sync` to install dependencies

Take your time, experiment, and build on what you've learned! 🎉
