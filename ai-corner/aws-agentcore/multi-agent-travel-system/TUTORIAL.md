# Multi-Agent Travel System - Step-by-Step Tutorial

Learn by building! We'll start with a simple single agent, then gradually add more agents and features.

## 🎯 Learning Path

```
Step 1: Single Agent (Basic Trip Planner)          ← Start here!
   ↓
Step 2: Add Tools (Flight Search)
   ↓
Step 3: Two Agents (Coordinator + Flight Agent)
   ↓
Step 4: Shared Memory (Agents share data)
   ↓
Step 5: Add Hotel Agent
   ↓
Step 6: Add Budget Tracking
   ↓
Step 7: Complete Trip Planner
```

---

## Step 1: Single Agent (Basic Trip Planner)

**Goal**: Create a simple agent that responds to trip requests.

**What you'll learn**: Basic agent setup, entrypoint, simple responses

### Create `main.py`:

```python
import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

# Initialize the app
app = BedrockAgentCoreApp()

# AWS Configuration
if 'AWS_PROFILE' not in os.environ:
    print("Error: Set AWS_PROFILE environment variable")
    exit(1)
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Create a simple travel agent
travel_agent = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    system_prompt="""You are a helpful travel planning assistant.
    Help users plan trips by asking about destination, dates, budget, and interests.
    Be friendly and ask clarifying questions."""
)

@app.entrypoint
def plan_trip(payload):
    """Main endpoint for trip planning"""
    user_message = payload.get("message", "I want to plan a trip")

    # Agent processes the request
    result = travel_agent(user_message)

    return {"response": result.message}

if __name__ == "__main__":
    print("🌍 Travel Agent starting...")
    app.run()
```

### Test it:

```bash
# Terminal 1: Start the agent
AWS_PROFILE=admin-user uv run main.py

# Terminal 2: Test requests
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to visit Paris"}'

curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "For 3 days in March"}'
```

**What happens**: Agent responds conversationally but has no memory or tools yet.

**Expected Output**:
```json
{
  "response": "Great! Paris is wonderful in March. How many people are traveling? What's your budget?"
}
```

---

## Step 2: Add Tools (Flight Search)

**Goal**: Give your agent the ability to search for flights.

**What you'll learn**: Tool definition, tool calling, returning structured data

### Create `tools.py`:

```python
"""Tools for travel agents"""

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
    # Mock data for now - later you can integrate real APIs
    flights = [
        {
            "id": "FL001",
            "airline": "Delta",
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": "08:00",
            "arrival": "21:30",
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
            "departure": "10:30",
            "arrival": "23:45",
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
            "departure": "14:00",
            "arrival": "03:30",
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
    # Mock data
    flight_db = {
        "FL001": {
            "id": "FL001",
            "airline": "Delta",
            "flight_number": "DL123",
            "aircraft": "Boeing 777",
            "amenities": ["wifi", "meals", "entertainment"],
            "baggage": "1 checked bag included",
            "cancellation_policy": "Free cancellation up to 24h before"
        },
        "FL002": {
            "id": "FL002",
            "airline": "Air France",
            "flight_number": "AF456",
            "aircraft": "Airbus A350",
            "amenities": ["wifi", "premium meals", "entertainment"],
            "baggage": "2 checked bags included",
            "cancellation_policy": "Free cancellation up to 48h before"
        },
        "FL003": {
            "id": "FL003",
            "airline": "United",
            "flight_number": "UA789",
            "aircraft": "Boeing 787",
            "amenities": ["entertainment"],
            "baggage": "1 checked bag ($35 fee)",
            "cancellation_policy": "Non-refundable"
        }
    }
    return flight_db.get(flight_id, {"error": "Flight not found"})
```

### Update `main.py`:

```python
import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from tools import search_flights, get_flight_details  # Import tools

app = BedrockAgentCoreApp()

if 'AWS_PROFILE' not in os.environ:
    print("Error: Set AWS_PROFILE environment variable")
    exit(1)
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Create agent with tools
travel_agent = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    system_prompt="""You are a travel planning assistant with access to flight search tools.

    When users ask about flights:
    1. Use search_flights() to find available options
    2. Present the results clearly (airline, price, duration, stops)
    3. Use get_flight_details() if they want more info about a specific flight
    4. Help them choose the best option based on their preferences
    """,
    tools=[search_flights, get_flight_details]  # Register tools
)

@app.entrypoint
def plan_trip(payload):
    user_message = payload.get("message", "I want to plan a trip")
    result = travel_agent(user_message)
    return {"response": result.message}

if __name__ == "__main__":
    print("🌍 Travel Agent with Flight Search starting...")
    app.run()
```

### Test it:

```bash
# Restart the agent
AWS_PROFILE=admin-user uv run main.py

# Test flight search
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "Find flights from NYC to Paris on March 15 for 2 people"}'
```

**Expected Output**:
```json
{
  "response": "I found 3 flights from NYC to Paris on March 15 for 2 passengers:

  1. **Delta (FL001)** - $900 total
     - Departs: 8:00 AM, Arrives: 9:30 PM
     - Non-stop, 7h 30m
     - 20 seats available

  2. **Air France (FL002)** - $1,040 total
     - Departs: 10:30 AM, Arrives: 11:45 PM
     - Non-stop, 7h 15m
     - 15 seats available

  3. **United (FL003)** - $760 total
     - Departs: 2:00 PM, Arrives: 3:30 AM next day
     - 1 stop, 7h 30m
     - 8 seats available

  The United flight is cheapest but has a stop. The Delta flight is a good balance of price and convenience. Would you like details on any of these?"
}
```

**What happened**: The agent automatically called `search_flights()` when you asked about flights!

---

## Step 3: Two Agents (Coordinator + Flight Agent)

**Goal**: Create specialized agents that work together.

**What you'll learn**: Agent communication, delegation, specialization

### Create `agents/flight_agent.py`:

```python
"""Specialized agent for flight operations"""
from strands import Agent
from tools import search_flights, get_flight_details

def create_flight_agent():
    """Create a specialized flight search agent"""
    return Agent(
        model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        system_prompt="""You are a flight search specialist.

        Your ONLY job is to help with flights:
        - Search for flights using search_flights()
        - Provide flight details using get_flight_details()
        - Compare options and recommend the best choice
        - Consider: price, duration, stops, departure times

        Do NOT handle hotels, activities, or other travel aspects.
        """,
        tools=[search_flights, get_flight_details]
    )
```

### Create `agents/coordinator.py`:

```python
"""Coordinator agent that delegates to specialists"""
from strands import Agent

def create_coordinator(flight_agent):
    """Create coordinator agent that manages specialists"""

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
        model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        system_prompt="""You are a travel planning coordinator.

        Your job is to understand what the user wants and delegate to specialists:
        - For FLIGHT questions → use ask_flight_agent()
        - For general trip planning → handle it yourself

        Examples:
        - "Find flights to Paris" → ask_flight_agent("Find flights to Paris")
        - "Plan a trip to Paris" → ask_flight_agent() for flights, then suggest hotels/activities yourself
        - "What should I see in Paris?" → answer directly (no delegation needed)

        Always be helpful and coordinate the specialists to create a complete plan.
        """,
        tools=[ask_flight_agent]
    )

    return coordinator
```

### Update `main.py`:

```python
import os
from bedrock_agentcore import BedrockAgentCoreApp
from agents.coordinator import create_coordinator
from agents.flight_agent import create_flight_agent

app = BedrockAgentCoreApp()

if 'AWS_PROFILE' not in os.environ:
    print("Error: Set AWS_PROFILE environment variable")
    exit(1)
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Create specialized agents
flight_agent = create_flight_agent()
coordinator = create_coordinator(flight_agent)

@app.entrypoint
def plan_trip(payload):
    user_message = payload.get("message", "I want to plan a trip")

    # Coordinator handles the request and delegates as needed
    result = coordinator(user_message)

    return {"response": result.message}

if __name__ == "__main__":
    print("🌍 Multi-Agent Travel System starting...")
    print("   - Coordinator Agent ✓")
    print("   - Flight Agent ✓")
    app.run()
```

### Test it:

```bash
AWS_PROFILE=admin-user uv run main.py

# Test delegation
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to go to Paris for 3 days. Find me flights from NYC on March 15 for 2 people."}'
```

**What happens**:
1. Coordinator receives request
2. Coordinator identifies flight-related part
3. Coordinator calls `ask_flight_agent("Find flights from NYC to Paris on March 15 for 2 people")`
4. Flight Agent calls `search_flights()`
5. Flight Agent returns results
6. Coordinator combines flight info with trip suggestions

---

## Step 4: Shared Memory (Agents Share Data)

**Goal**: Agents remember context and share information about the trip.

**What you'll learn**: State management, context sharing between agents

### Create `memory.py`:

```python
"""Shared memory for multi-agent system"""
from typing import Dict, Any, Optional
from datetime import datetime

class TripMemory:
    """Shared memory that all agents can access"""

    def __init__(self):
        self.trips: Dict[str, Dict[str, Any]] = {}

    def create_trip(self, trip_id: str, user_message: str) -> Dict[str, Any]:
        """Create a new trip context"""
        self.trips[trip_id] = {
            "trip_id": trip_id,
            "created_at": datetime.now().isoformat(),
            "original_request": user_message,
            "destination": None,
            "origin": None,
            "dates": {"start": None, "end": None},
            "passengers": 1,
            "budget": None,
            "bookings": {
                "flights": [],
                "hotels": [],
                "activities": []
            },
            "total_cost": 0,
            "status": "planning"
        }
        return self.trips[trip_id]

    def get_trip(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """Get trip context"""
        return self.trips.get(trip_id)

    def update_trip(self, trip_id: str, updates: Dict[str, Any]):
        """Update trip context"""
        if trip_id in self.trips:
            self.trips[trip_id].update(updates)

    def add_flight(self, trip_id: str, flight: Dict[str, Any]):
        """Add a flight booking"""
        if trip_id in self.trips:
            self.trips[trip_id]["bookings"]["flights"].append(flight)
            self.trips[trip_id]["total_cost"] += flight.get("total_price", 0)

    def add_hotel(self, trip_id: str, hotel: Dict[str, Any]):
        """Add a hotel booking"""
        if trip_id in self.trips:
            self.trips[trip_id]["bookings"]["hotels"].append(hotel)
            self.trips[trip_id]["total_cost"] += hotel.get("total_price", 0)

    def get_summary(self, trip_id: str) -> str:
        """Get human-readable trip summary"""
        trip = self.get_trip(trip_id)
        if not trip:
            return "Trip not found"

        summary = f"""
Trip to {trip['destination'] or 'TBD'}
Dates: {trip['dates']['start'] or 'TBD'} to {trip['dates']['end'] or 'TBD'}
Passengers: {trip['passengers']}
Total Cost: ${trip['total_cost']}
Budget: ${trip['budget'] or 'Not set'}

Bookings:
- Flights: {len(trip['bookings']['flights'])}
- Hotels: {len(trip['bookings']['hotels'])}
- Activities: {len(trip['bookings']['activities'])}

Status: {trip['status']}
        """.strip()
        return summary

# Global memory instance
trip_memory = TripMemory()
```

### Update `main.py` to use memory:

```python
import os
import uuid
from bedrock_agentcore import BedrockAgentCoreApp
from agents.coordinator import create_coordinator
from agents.flight_agent import create_flight_agent
from memory import trip_memory

app = BedrockAgentCoreApp()

if 'AWS_PROFILE' not in os.environ:
    print("Error: Set AWS_PROFILE environment variable")
    exit(1)
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Create agents
flight_agent = create_flight_agent()
coordinator = create_coordinator(flight_agent)

@app.entrypoint
def plan_trip(payload):
    user_message = payload.get("message", "I want to plan a trip")
    trip_id = payload.get("trip_id")  # Allow continuing existing trips

    # Create or get trip context
    if not trip_id:
        trip_id = f"trip-{uuid.uuid4().hex[:8]}"
        trip_memory.create_trip(trip_id, user_message)

    # Get current trip state
    trip = trip_memory.get_trip(trip_id)

    # Add trip context to coordinator's prompt
    context_prompt = f"""
Current trip context:
{trip_memory.get_summary(trip_id)}

User message: {user_message}
"""

    # Coordinator processes with context
    result = coordinator(context_prompt)

    return {
        "trip_id": trip_id,
        "response": result.message,
        "trip_summary": trip_memory.get_summary(trip_id)
    }

if __name__ == "__main__":
    print("🌍 Multi-Agent Travel System with Memory starting...")
    app.run()
```

### Test it:

```bash
# First request - creates new trip
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a trip to Paris from NYC for 2 people, budget $3000"}' \
  | jq

# Save the trip_id from response, then continue
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"trip_id": "trip-abc123", "message": "Find flights for March 15"}' \
  | jq
```

**What's new**: Agents now remember your destination, budget, and passengers across multiple requests!

---

## ✅ Checkpoint

You've learned:
- ✅ Create a basic agent
- ✅ Add tools to agents
- ✅ Create specialized agents
- ✅ Agent delegation and communication
- ✅ Shared memory between agents

## Next Steps

Would you like me to create:
- **Step 5**: Add Hotel Agent (searches and books hotels)
- **Step 6**: Add Budget Tracking (warns when over budget)
- **Step 7**: Complete System (all agents working together)

Or would you like to practice these 4 steps first? Let me know what pace works for you! 🚀
