# Mock APIs for Learning

## Why Use Mock Data?

When building the multi-agent travel system, you have **two options**:

### Option 1: Mock Data (Recommended for Learning) ✅
- **No API keys needed** - Start immediately
- **Free** - No costs while learning
- **Fast** - Instant responses
- **Predictable** - Same data every time for testing
- **No rate limits** - Test as much as you want

### Option 2: Real APIs
- **Requires API keys** - Need to sign up
- **Costs money** - Pay per request
- **Slower** - Network latency
- **Variable** - Data changes
- **Rate limits** - Limited requests

**👉 Start with mock data, switch to real APIs when ready!**

## Project Structure with Mocks

```
src/multi_agent_travel_system/tools/
├── __init__.py              # Exports all tools
├── mock_data.py             # ✨ All mock data in one place
├── flight_tools.py          # Flight search (uses mock_data)
├── hotel_tools.py           # Hotel search (uses mock_data)
├── activity_tools.py        # Activity search (uses mock_data)
└── budget_tools.py          # Budget calculations (no API needed)
```

## How It Works

Each tool file follows this pattern:

```python
# tools/flight_tools.py

from .mock_data import get_mock_flights  # Import mock data

def search_flights(origin, destination, date, passengers):
    """Public function that agents call"""

    # Use mock data for development
    if config.DEBUG or not config.AMADEUS_API_KEY:
        return _search_flights_mock(...)

    # Use real API when ready
    # return _search_flights_real(...)

def _search_flights_mock(...):
    """Mock implementation - uses test data"""
    return get_mock_flights(...)

# def _search_flights_real(...):
#     """Real implementation - calls actual API"""
#     # Uncomment when you have API keys
#     pass
```

## Available Mock Data

### ✈️ Flights (mock_data.py)
```python
get_mock_flights(origin, destination, date, passengers)
# Returns: [
#     {"id": "FL001", "airline": "Delta", "price": 900, ...},
#     {"id": "FL002", "airline": "Air France", "price": 1040, ...},
#     {"id": "FL003", "airline": "United", "price": 760, ...}
# ]

get_mock_flight_details(flight_id)
# Returns: {
#     "aircraft": "Boeing 777",
#     "amenities": ["WiFi", "Meals", "Entertainment"],
#     "baggage": "1 checked bag included",
#     ...
# }
```

### 🏨 Hotels (mock_data.py)
```python
get_mock_hotels(city, checkin, checkout, guests)
# Returns: [
#     {"id": "HTL001", "name": "Le Grand Hotel", "stars": 5, ...},
#     {"id": "HTL002", "name": "Hotel Moderne", "stars": 4, ...},
#     {"id": "HTL003", "name": "Budget Inn", "stars": 3, ...}
# ]
```

### 🎭 Activities (mock_data.py)
```python
get_mock_activities(city, category)
# Returns: [
#     {"id": "ACT001", "name": "Eiffel Tower Tour", "price": 35, ...},
#     {"id": "ACT002", "name": "Louvre Museum", "price": 25, ...},
#     ...
# ]

get_mock_restaurants(city, cuisine)
# Returns: [
#     {"id": "REST001", "name": "Le Jules Verne", "cuisine": "French", ...}
# ]
```

## Testing the Mocks

The mocks return realistic data that works with all agents:

```bash
# Test flight search
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "Find flights from NYC to Paris on March 15 for 2 people"}' \
  | jq

# Response uses mock data - but agents don't know the difference!
```

## Switching to Real APIs

When you're ready to use real APIs:

### 1. Get API Keys

**Flights:**
- [Amadeus Flight API](https://developers.amadeus.com/) - Free tier available
- Alternative: [Skyscanner API](https://developers.skyscanner.net/)

**Hotels:**
- [Booking.com API](https://www.booking.com/affiliate-program)
- Alternative: [Hotels.com API](https://www.hotels.com/affiliates/)

**Activities:**
- [GetYourGuide API](https://api.getyourguide.com/)
- Alternative: [Viator API](https://www.viator.com/partners/)

### 2. Add Keys to .env

```bash
# .env
AMADEUS_API_KEY=your_amadeus_key_here
BOOKING_API_KEY=your_booking_key_here
GETYOURGUIDE_API_KEY=your_getyourguide_key_here

# Set DEBUG=false to use real APIs
DEBUG=false
```

### 3. Implement Real API Functions

Uncomment and implement the `_*_real()` functions in tool files:

```python
# tools/flight_tools.py

def _search_flights_real(origin, destination, date, passengers):
    """Real implementation using Amadeus API"""
    import requests

    headers = {
        "Authorization": f"Bearer {config.AMADEUS_API_KEY}"
    }

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": passengers
    }

    response = requests.get(
        "https://api.amadeus.com/v2/shopping/flight-offers",
        headers=headers,
        params=params
    )

    if response.status_code == 200:
        data = response.json()
        # Transform API response to our format
        return transform_amadeus_response(data)
    else:
        return {"error": f"API error: {response.status_code}"}
```

### 4. The Switch is Automatic!

The tool automatically switches based on config:

```python
def search_flights(...):
    # Checks config automatically
    if config.DEBUG or not config.AMADEUS_API_KEY:
        return _search_flights_mock(...)  # Mock

    return _search_flights_real(...)      # Real API
```

## File Structure Overview

```
tools/
├── mock_data.py              ← All mock data lives here
│   ├── get_mock_flights()
│   ├── get_mock_hotels()
│   ├── get_mock_activities()
│   └── get_mock_restaurants()
│
├── flight_tools.py           ← Flight operations
│   ├── search_flights()           [public]
│   ├── _search_flights_mock()     [uses mock_data]
│   └── _search_flights_real()     [TODO: implement]
│
├── hotel_tools.py            ← Hotel operations
│   ├── search_hotels()            [public]
│   ├── _search_hotels_mock()      [uses mock_data]
│   └── _search_hotels_real()      [TODO: implement]
│
├── activity_tools.py         ← Activity operations
│   ├── search_activities()        [public]
│   ├── _search_activities_mock()  [uses mock_data]
│   └── _search_activities_real()  [TODO: implement]
│
└── budget_tools.py           ← Budget tracking (no API needed)
    ├── calculate_trip_cost()
    ├── check_budget()
    └── suggest_savings()
```

## Benefits of This Pattern

### 1. **Clean Separation**
- Mock logic separate from tool logic
- Easy to maintain and test

### 2. **Easy Testing**
- Test agents without API calls
- Consistent, predictable responses

### 3. **Gradual Migration**
- Switch one tool at a time
- Mix mock and real APIs
- No breaking changes

### 4. **Development Speed**
- No API setup required
- Instant feedback
- Focus on learning agent patterns

## Current Status

| Tool | Mock Data | Real API |
|------|-----------|----------|
| ✈️ **Flights** | ✅ Complete | ⏳ TODO (Amadeus) |
| 🏨 **Hotels** | ✅ Complete | ⏳ TODO (Booking.com) |
| 🎭 **Activities** | ✅ Complete | ⏳ TODO (GetYourGuide) |
| 🍽️ **Restaurants** | ✅ Complete | ⏳ TODO (Google Places) |
| 💰 **Budget** | ✅ Complete | N/A (calculations only) |

## Next Steps

1. **Complete the Tutorial** - Use mock data throughout
2. **Build All Agents** - Flight, Hotel, Activity, Budget agents
3. **Test End-to-End** - Plan a complete trip with mocks
4. **Add Real APIs** - One at a time, when ready

## Example: Complete Mock Trip

```bash
# This entire interaction uses ONLY mock data!

curl -X POST http://localhost:8080/invocations \
  -d '{"message": "Plan a 3-day trip to Paris for 2 people, budget $3000"}'

# Agent uses:
# - Mock flights ($900)
# - Mock hotels ($540)
# - Mock activities ($225)
# - Budget tools (calculations)
#
# Total: $1665 (mock prices)
# Result: Complete travel itinerary!
```

**All this without a single API key or spending a penny!** 🎉

## Summary

- ✅ **Use mock data for learning** - It's free, fast, and perfect for development
- 📁 **All mocks in mock_data.py** - One file to rule them all
- 🔄 **Easy to switch** - Just add API keys and set DEBUG=false
- 🚀 **Focus on learning** - Build agents without API complexity

**Start with mocks → Learn the patterns → Add real APIs when ready!**
