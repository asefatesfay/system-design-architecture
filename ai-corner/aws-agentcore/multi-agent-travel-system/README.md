# Multi-Agent Travel System

A sophisticated travel planning system using AWS Bedrock AgentCore with multiple specialized agents working together.

## Architecture Overview

```
User Request
     ↓
Coordinator Agent (Main Orchestrator)
     ├─→ Flight Agent (Search & Book Flights)
     ├─→ Hotel Agent (Search & Book Hotels)
     ├─→ Activity Agent (Suggest Activities/Tours)
     ├─→ Budget Agent (Track Spending & Budget)
     └─→ Itinerary Agent (Create Day-by-Day Plan)
```

## Agent Roles

### 1. Coordinator Agent (Orchestrator)
**Responsibility**: Main entry point, understands user intent, delegates to specialized agents

**Example Flow**:
```
User: "Plan a 3-day trip to Paris for 2 people, budget $3000"

Coordinator:
1. Extracts: destination=Paris, days=3, people=2, budget=$3000
2. Delegates to Budget Agent: Track $3000 budget
3. Delegates to Flight Agent: Find flights to Paris for 2
4. Delegates to Hotel Agent: Find hotels for 3 nights, 2 people
5. Delegates to Activity Agent: Suggest 3 days of activities
6. Delegates to Itinerary Agent: Create final day-by-day plan
7. Returns: Complete travel plan
```

### 2. Flight Agent
**Responsibility**: Search flights, compare prices, book tickets

**Tools**:
- `search_flights(origin, destination, date, passengers)` - Search available flights
- `get_flight_details(flight_id)` - Get specific flight info
- `book_flight(flight_id, passengers)` - Book a flight
- `check_flight_status(booking_id)` - Check booking status

**Example**:
```python
User: "Find flights from NYC to Paris on March 15"
Flight Agent:
1. Calls: search_flights("NYC", "Paris", "2024-03-15", 2)
2. Compares: Delta $450, Air France $520, United $480
3. Recommends: Delta (cheapest, non-stop)
4. Reports to Coordinator: "Found Delta flight, $900 for 2 passengers"
```

### 3. Hotel Agent
**Responsibility**: Search hotels, compare rates, make reservations

**Tools**:
- `search_hotels(city, checkin, checkout, guests)` - Search hotels
- `get_hotel_details(hotel_id)` - Get hotel amenities/reviews
- `check_availability(hotel_id, dates)` - Verify availability
- `book_hotel(hotel_id, checkin, checkout, guests)` - Make reservation

**Example**:
```python
User: "Find hotels in Paris for 3 nights"
Hotel Agent:
1. Calls: search_hotels("Paris", "2024-03-15", "2024-03-18", 2)
2. Filters: 4-star, city center, $150-200/night
3. Compares: Hotel A (4.5★, $180), Hotel B (4.2★, $160)
4. Recommends: Hotel A (better reviews, breakfast included)
5. Reports: "Hotel A, $540 for 3 nights"
```

### 4. Activity Agent
**Responsibility**: Suggest attractions, tours, restaurants

**Tools**:
- `search_attractions(city, interests)` - Find attractions
- `get_restaurant_recommendations(city, cuisine, budget)` - Find restaurants
- `search_tours(city, type)` - Find guided tours
- `get_event_calendar(city, dates)` - Check local events

**Example**:
```python
User: "Suggest activities in Paris"
Activity Agent:
1. Day 1: Eiffel Tower ($30), Seine River cruise ($25)
2. Day 2: Louvre Museum ($20), Lunch at Le Marais ($40)
3. Day 3: Versailles Palace tour ($60), Dinner at Montmartre ($50)
4. Reports: "9 activities planned, $225 total"
```

### 5. Budget Agent
**Responsibility**: Track expenses, warn about budget overruns, suggest savings

**Tools**:
- `set_budget(amount)` - Set total budget
- `add_expense(category, amount, description)` - Track spending
- `get_remaining_budget()` - Check remaining funds
- `suggest_alternatives(category)` - Find cheaper options

**Example**:
```python
Budget: $3000
Expenses:
- Flights: $900
- Hotel: $540
- Activities: $225
- Food: $300 (estimated)
Total: $1965
Remaining: $1035

Budget Agent: "You have $1035 left. I recommend:
- Save $200 by booking Hotel B instead
- Airport shuttle ($30) vs Taxi ($50)
"
```

### 6. Itinerary Agent
**Responsibility**: Combine all bookings into a coherent day-by-day plan

**Tools**:
- `create_itinerary(flights, hotels, activities)` - Build timeline
- `optimize_schedule(locations, time_constraints)` - Arrange activities logically
- `add_travel_time(locations)` - Include transit between places
- `export_itinerary(format)` - Export as PDF/JSON

**Example Output**:
```
Day 1 (March 15):
├─ 8:00 AM: Delta Flight DL123 departs JFK
├─ 9:30 PM: Arrive Paris CDG (local time)
├─ 11:00 PM: Check-in Hotel A (123 Rue de Rivoli)

Day 2 (March 16):
├─ 9:00 AM: Breakfast at hotel
├─ 10:30 AM: Eiffel Tower visit ($30)
├─ 1:00 PM: Lunch at Le Jules Verne ($60)
├─ 3:00 PM: Seine River Cruise ($25)
├─ 7:00 PM: Dinner at Le Marais ($40)

Day 3 (March 17):
├─ 9:00 AM: Louvre Museum ($20)
├─ 2:00 PM: Explore Montmartre
├─ 7:00 PM: Dinner at Le Consulat ($50)

Day 4 (March 18):
├─ 8:00 AM: Hotel checkout
├─ 10:00 AM: Versailles Palace tour ($60)
├─ 5:00 PM: Return to Paris
├─ 8:00 PM: Delta Flight DL124 departs CDG
├─ 11:00 PM: Arrive JFK
```

## System Features

### 1. Agent Communication
Agents communicate through the Coordinator using a structured message format:

```python
{
    "from_agent": "coordinator",
    "to_agent": "flight_agent",
    "action": "search_flights",
    "parameters": {
        "origin": "NYC",
        "destination": "Paris",
        "date": "2024-03-15",
        "passengers": 2
    },
    "context": {
        "budget_remaining": 3000,
        "trip_duration": 3
    }
}
```

### 2. Shared Memory
All agents access a shared trip context:

```python
trip_context = {
    "trip_id": "trip-123",
    "user_id": "user-456",
    "destination": "Paris",
    "dates": {"start": "2024-03-15", "end": "2024-03-18"},
    "passengers": 2,
    "budget": {
        "total": 3000,
        "spent": 1965,
        "remaining": 1035
    },
    "bookings": {
        "flights": [{"id": "FL123", "cost": 900}],
        "hotels": [{"id": "HT456", "cost": 540}],
        "activities": [{"id": "ACT789", "cost": 225}]
    },
    "preferences": {
        "interests": ["art", "food", "history"],
        "budget_level": "moderate",
        "pace": "relaxed"
    }
}
```

### 3. Error Handling & Fallbacks

When an agent fails:
```python
# Example: Flight search returns no results

Flight Agent → Coordinator: "No flights available on March 15"
Coordinator → Flight Agent: "Try March 16-17 instead"
Flight Agent → Coordinator: "Found flights on March 16, $950"
Coordinator → Hotel Agent: "Adjust hotel dates to March 16-19"
```

### 4. Real-time Updates

As agents work, users see progress:
```
✓ Searching flights... Found 5 options
✓ Comparing prices... Best price: $900
✓ Checking hotel availability... 12 hotels found
✓ Filtering by location and rating... 3 recommendations
✓ Calculating total cost... $1965 of $3000 used
✓ Creating itinerary... Day-by-day plan ready
✓ Trip planned! Ready to book.
```

## Project Structure

```
multi-agent-travel-system/
├── src/
│   └── multi_agent_travel_system/
│       ├── __init__.py
│       ├── main.py                    # Entry point
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── coordinator.py         # Main orchestrator
│       │   ├── flight_agent.py        # Flight specialist
│       │   ├── hotel_agent.py         # Hotel specialist
│       │   ├── activity_agent.py      # Activities specialist
│       │   ├── budget_agent.py        # Budget tracker
│       │   └── itinerary_agent.py     # Itinerary builder
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── flight_tools.py        # Flight API wrappers
│       │   ├── hotel_tools.py         # Hotel API wrappers
│       │   ├── activity_tools.py      # Activity API wrappers
│       │   └── budget_tools.py        # Budget calculations
│       ├── models/
│       │   ├── __init__.py
│       │   ├── trip.py                # Trip data models
│       │   ├── booking.py             # Booking data models
│       │   └── message.py             # Agent message format
│       └── utils/
│           ├── __init__.py
│           ├── memory.py              # Shared memory/context
│           └── config.py              # Configuration
├── tests/
├── README.md
└── pyproject.toml
```

## Implementation Phases

### Phase 1: Basic Setup (Week 1)
- [ ] Create main.py with BedrockAgentCoreApp
- [ ] Implement Coordinator Agent
- [ ] Set up shared memory structure
- [ ] Test with simple "Plan a trip" request

### Phase 2: Flight Agent (Week 1-2)
- [ ] Implement Flight Agent
- [ ] Create mock flight search tool (for testing)
- [ ] Integrate real flight API (optional)
- [ ] Test: "Find flights to Paris"

### Phase 3: Hotel Agent (Week 2)
- [ ] Implement Hotel Agent
- [ ] Create hotel search tools
- [ ] Test: "Find hotels in Paris for 3 nights"

### Phase 4: Activity & Budget Agents (Week 3)
- [ ] Implement Activity Agent with attractions/restaurants
- [ ] Implement Budget Agent with expense tracking
- [ ] Test: Full trip with budget constraints

### Phase 5: Itinerary Agent (Week 3-4)
- [ ] Implement Itinerary Agent
- [ ] Create day-by-day scheduling logic
- [ ] Test: Generate complete travel itinerary

### Phase 6: Polish & Deploy (Week 4)
- [ ] Add error handling
- [ ] Implement observability (logging/tracing)
- [ ] Deploy to AWS Lambda
- [ ] Create API Gateway integration

## API Endpoints

### POST /plan-trip
Plan a complete trip

```bash
curl -X POST http://localhost:8080/plan-trip \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "origin": "New York",
    "dates": {
      "start": "2024-03-15",
      "end": "2024-03-18"
    },
    "passengers": 2,
    "budget": 3000,
    "interests": ["art", "food", "history"]
  }'
```

### POST /search-flights
Search flights only

```bash
curl -X POST http://localhost:8080/search-flights \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "NYC",
    "destination": "Paris",
    "date": "2024-03-15",
    "passengers": 2
  }'
```

### POST /search-hotels
Search hotels only

```bash
curl -X POST http://localhost:8080/search-hotels \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Paris",
    "checkin": "2024-03-15",
    "checkout": "2024-03-18",
    "guests": 2
  }'
```

### GET /trip/{trip_id}
Get trip details

```bash
curl http://localhost:8080/trip/trip-123
```

## Mock vs Real APIs

For learning, start with **mock data**:

```python
# tools/flight_tools.py
def search_flights(origin, destination, date, passengers):
    # Mock data for testing
    return [
        {
            "id": "FL123",
            "airline": "Delta",
            "price": 450,
            "duration": "7h 30m",
            "stops": 0
        },
        {
            "id": "FL456",
            "airline": "Air France",
            "price": 520,
            "duration": "7h 45m",
            "stops": 0
        }
    ]
```

Later, integrate real APIs:
- **Flights**: Amadeus API, Skyscanner API
- **Hotels**: Booking.com API, Hotels.com API
- **Activities**: GetYourGuide API, Viator API

## Configuration

Create a `.env` file:

```bash
# AWS Configuration
AWS_PROFILE=admin-user
AWS_DEFAULT_REGION=us-west-2

# Bedrock Model
BEDROCK_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# API Keys (optional, for real integrations)
AMADEUS_API_KEY=your_key_here
BOOKING_API_KEY=your_key_here
GETYOURGUIDE_API_KEY=your_key_here

# Database (for storing trip data)
DYNAMODB_TABLE=travel-trips
```

## Advanced Features (Optional)

### 1. User Preferences Learning
```python
# Agent learns user preferences over time
user_profile = {
    "always_prefers": "window_seat",
    "favorite_airlines": ["Delta", "United"],
    "dietary": "vegetarian",
    "past_trips": ["Paris", "London", "Tokyo"]
}
```

### 2. Real-time Price Monitoring
```python
# Monitor prices and alert when they drop
budget_agent.watch_price("FL123")
# Alert: "Flight price dropped from $450 to $399!"
```

### 3. Multi-destination Trips
```python
# Plan trips with multiple stops
trip = {
    "destinations": ["Paris", "Rome", "Barcelona"],
    "duration": 10,
    "budget": 5000
}
```

### 4. Group Travel
```python
# Coordinate travel for groups
trip = {
    "passengers": 5,
    "rooms": 2,  # 2 rooms, 5 people
    "activities": "all ages"  # Kid-friendly
}
```

## Testing Strategy

### Unit Tests
Test individual agents:
```python
def test_flight_agent():
    agent = FlightAgent()
    results = agent.search("NYC", "Paris", "2024-03-15", 2)
    assert len(results) > 0
    assert results[0]["price"] > 0
```

### Integration Tests
Test agent coordination:
```python
def test_coordinator():
    coordinator = CoordinatorAgent()
    trip = coordinator.plan_trip({
        "destination": "Paris",
        "budget": 3000
    })
    assert "flights" in trip
    assert "hotels" in trip
    assert trip["total_cost"] <= 3000
```

### End-to-End Tests
Test full API:
```bash
pytest tests/e2e/test_trip_planning.py -v
```

## Resources

- [AWS Bedrock AgentCore Docs](https://github.com/awslabs/bedrock-agentcore)
- [Strands Agents Guide](https://strandsagents.com/docs/)
- [Multi-Agent Systems Patterns](https://www.anthropic.com/research/building-effective-agents)
- [Travel APIs Overview](https://rapidapi.com/hub/travel)

## Next Steps

1. **Start Simple**: Implement Coordinator + Flight Agent first
2. **Use Mock Data**: Don't worry about real APIs initially
3. **Test Frequently**: Test each agent before adding the next
4. **Add Complexity**: Add more agents once core works
5. **Deploy**: Move to Lambda when ready

Ready to start building? Let's begin with Phase 1! 🚀
