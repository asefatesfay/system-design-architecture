"""
Hotel search and booking tools.

TODO: Implement these functions in Step 5 of the tutorial!

Hints:
- Use mock_data.get_mock_hotels() for mock implementation
- Follow the same pattern as flight_tools.py
- Remember: public function → check config → call mock or real
"""
from typing import List, Dict, Any
from ..config import config


# ============================================================================
# PUBLIC API - Agents will call these functions
# ============================================================================

def search_hotels(city: str, checkin: str, checkout: str, guests: int = 2) -> List[Dict[str, Any]]:
    """
    Search for available hotels.

    Args:
        city: City name (e.g., 'Paris', 'London')
        checkin: Check-in date (YYYY-MM-DD)
        checkout: Check-out date (YYYY-MM-DD)
        guests: Number of guests

    Returns:
        List of available hotels with prices

    TODO: Implement this in Step 5!
    Hint: Check if DEBUG mode, then call _search_hotels_mock()
    """
    # TODO: Your code here
    pass


def get_hotel_details(hotel_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific hotel.

    Args:
        hotel_id: Hotel identifier (e.g., 'HTL001')

    Returns:
        Detailed hotel information

    TODO: Implement this!
    """
    # TODO: Your code here
    pass


def book_hotel(hotel_id: str, checkin: str, checkout: str, guests: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Book a hotel room.

    Args:
        hotel_id: Hotel identifier
        checkin: Check-in date
        checkout: Check-out date
        guests: Guest details [{"first_name": "...", "last_name": "..."}]

    Returns:
        Booking confirmation

    TODO: Implement this!
    """
    # TODO: Your code here
    pass


# ============================================================================
# MOCK IMPLEMENTATIONS - You'll implement these!
# ============================================================================

def _search_hotels_mock(city: str, checkin: str, checkout: str, guests: int) -> List[Dict[str, Any]]:
    """
    Mock implementation using test data.

    TODO: Import and use get_mock_hotels() from mock_data.py
    """
    # TODO: Your code here
    pass


def _get_hotel_details_mock(hotel_id: str) -> Dict[str, Any]:
    """
    Mock implementation for hotel details.

    TODO: Import and use get_mock_hotel_details() from mock_data.py
    """
    # TODO: Your code here
    pass


def _book_hotel_mock(hotel_id: str, checkin: str, checkout: str, guests: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Mock hotel booking.

    TODO: Return a booking confirmation dictionary
    Include: booking_reference, status, hotel_id, checkin, checkout, guests
    """
    # TODO: Your code here
    pass
