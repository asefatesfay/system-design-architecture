"""
Flight search and booking tools.

Currently uses mock data for learning.
To use real APIs: uncomment real API functions and set API keys in .env
"""
from typing import List, Dict, Any
from ..config import config
from .mock_data import get_mock_flights, get_mock_flight_details


# ============================================================================
# PUBLIC API - These functions are called by agents
# ============================================================================

def search_flights(origin: str, destination: str, date: str, passengers: int = 1) -> List[Dict[str, Any]]:
    """
    Search for available flights.

    Args:
        origin: Origin city code (e.g., 'NYC', 'JFK', 'LAX')
        destination: Destination city code (e.g., 'Paris', 'CDG', 'LHR')
        date: Departure date (YYYY-MM-DD format)
        passengers: Number of passengers

    Returns:
        List of available flights with prices and details

    Example:
        >>> search_flights('NYC', 'Paris', '2024-03-15', 2)
        [{'id': 'FL001', 'airline': 'Delta', 'price': 900, ...}, ...]
    """
    # Use mock data for development
    if config.DEBUG or not config.AMADEUS_API_KEY:
        return _search_flights_mock(origin, destination, date, passengers)

    # Use real API when ready
    # return _search_flights_real(origin, destination, date, passengers)

    return _search_flights_mock(origin, destination, date, passengers)


def get_flight_details(flight_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific flight.

    Args:
        flight_id: Flight identifier (e.g., 'FL001', 'FL002')

    Returns:
        Detailed flight information including:
        - Aircraft type
        - Amenities (WiFi, meals, etc.)
        - Baggage policy
        - Cancellation policy
        - Seat information

    Example:
        >>> get_flight_details('FL001')
        {'id': 'FL001', 'airline': 'Delta', 'aircraft': 'Boeing 777', ...}
    """
    if config.DEBUG or not config.AMADEUS_API_KEY:
        return _get_flight_details_mock(flight_id)

    # Use real API when ready
    # return _get_flight_details_real(flight_id)

    return _get_flight_details_mock(flight_id)


def book_flight(flight_id: str, passengers: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Book a flight for passengers.

    Args:
        flight_id: Flight identifier
        passengers: List of passenger details
            [{"first_name": "John", "last_name": "Doe", "email": "john@example.com"}]

    Returns:
        Booking confirmation with reference number

    Example:
        >>> book_flight('FL001', [{'first_name': 'John', 'last_name': 'Doe'}])
        {'booking_ref': 'ABC12345', 'status': 'confirmed', ...}
    """
    if config.DEBUG or not config.AMADEUS_API_KEY:
        return _book_flight_mock(flight_id, passengers)

    # Use real API when ready
    # return _book_flight_real(flight_id, passengers)

    return _book_flight_mock(flight_id, passengers)


# ============================================================================
# MOCK IMPLEMENTATIONS - Used for development/learning
# ============================================================================

def _search_flights_mock(origin: str, destination: str, date: str, passengers: int) -> List[Dict[str, Any]]:
    """Mock implementation using test data"""
    return get_mock_flights(origin, destination, date, passengers)


def _get_flight_details_mock(flight_id: str) -> Dict[str, Any]:
    """Mock implementation using test data"""
    return get_mock_flight_details(flight_id)


def _book_flight_mock(flight_id: str, passengers: List[Dict[str, str]]) -> Dict[str, Any]:
    """Mock flight booking"""
    from .mock_data import generate_booking_reference

    return {
        "booking_reference": generate_booking_reference(),
        "status": "confirmed",
        "flight_id": flight_id,
        "passengers": passengers,
        "booked_at": "2024-03-15T10:30:00Z",
        "message": "Flight booked successfully! (This is a mock booking)"
    }


# ============================================================================
# REAL API IMPLEMENTATIONS - Use when you have API keys
# ============================================================================

# def _search_flights_real(origin: str, destination: str, date: str, passengers: int) -> List[Dict[str, Any]]:
#     """
#     Real implementation using Amadeus Flight API
#
#     Setup:
#     1. Get API key from https://developers.amadeus.com/
#     2. Add to .env: AMADEUS_API_KEY=your_key_here
#     3. Uncomment this function
#     """
#     import requests
#
#     headers = {
#         "Authorization": f"Bearer {config.AMADEUS_API_KEY}"
#     }
#
#     params = {
#         "originLocationCode": origin,
#         "destinationLocationCode": destination,
#         "departureDate": date,
#         "adults": passengers
#     }
#
#     response = requests.get(
#         "https://api.amadeus.com/v2/shopping/flight-offers",
#         headers=headers,
#         params=params
#     )
#
#     if response.status_code == 200:
#         data = response.json()
#         # Transform API response to our format
#         flights = []
#         for offer in data.get("data", [])[:5]:  # Limit to 5 results
#             flight = {
#                 "id": offer["id"],
#                 "airline": offer["validatingAirlineCodes"][0],
#                 "origin": origin,
#                 "destination": destination,
#                 "date": date,
#                 "price_per_person": float(offer["price"]["total"]) / passengers,
#                 "total_price": float(offer["price"]["total"]),
#                 # ... map other fields
#             }
#             flights.append(flight)
#         return flights
#     else:
#         return {"error": f"API error: {response.status_code}"}


# def _get_flight_details_real(flight_id: str) -> Dict[str, Any]:
#     """Real implementation - fetch from API"""
#     # Implement real API call here
#     pass


# def _book_flight_real(flight_id: str, passengers: List[Dict[str, str]]) -> Dict[str, Any]:
#     """Real implementation - book through API"""
#     # Implement real API call here
#     pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_airport_code(location: str) -> str:
    """
    Convert city names to airport codes.

    Examples:
        'New York' or 'NYC' -> 'JFK'
        'Paris' -> 'CDG'
        'London' -> 'LHR'
    """
    city_to_airport = {
        "new york": "JFK",
        "nyc": "JFK",
        "paris": "CDG",
        "london": "LHR",
        "los angeles": "LAX",
        "la": "LAX",
        "tokyo": "NRT",
        "dubai": "DXB",
        "singapore": "SIN",
    }

    location_lower = location.lower().strip()

    # If already an airport code (3 letters), return as-is
    if len(location) == 3:
        return location.upper()

    # Otherwise look up in mapping
    return city_to_airport.get(location_lower, location.upper())
