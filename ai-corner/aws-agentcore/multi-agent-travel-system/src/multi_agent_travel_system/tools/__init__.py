"""
Tool implementations for agents.

STATUS:
✅ flight_tools.py    - Fully implemented (Step 2)
⏳ hotel_tools.py     - TODO: Implement in Step 5
⏳ activity_tools.py  - TODO: Implement in Step 6
⏳ budget_tools.py    - TODO: Implement in Step 6

You'll implement the missing tools as you progress through the tutorial!
"""

# Flight tools - IMPLEMENTED
from .flight_tools import (
    search_flights,
    get_flight_details,
    book_flight
)

# Hotel tools - TODO: You'll implement these!
from .hotel_tools import (
    search_hotels,
    get_hotel_details,
    book_hotel
)

# Activity tools - TODO: You'll implement these!
from .activity_tools import (
    search_activities,
    search_restaurants,
    get_activity_details,
    book_activity
)

# Budget tools - TODO: You'll implement these!
from .budget_tools import (
    calculate_trip_cost,
    check_budget,
    suggest_savings
)

__all__ = [
    # Flights (Step 2) ✅
    "search_flights",
    "get_flight_details",
    "book_flight",
    # Hotels (Step 5) ⏳
    "search_hotels",
    "get_hotel_details",
    "book_hotel",
    # Activities (Step 6) ⏳
    "search_activities",
    "search_restaurants",
    "get_activity_details",
    "book_activity",
    # Budget (Step 6) ⏳
    "calculate_trip_cost",
    "check_budget",
    "suggest_savings",
]
