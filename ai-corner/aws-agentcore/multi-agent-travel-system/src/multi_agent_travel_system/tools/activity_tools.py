"""
Activity and attraction search tools.

TODO: Implement these functions in Step 6 of the tutorial!
"""
from typing import List, Dict, Any
from ..config import config


# ============================================================================
# PUBLIC API - Implement these!
# ============================================================================

def search_activities(city: str, category: str = "all") -> List[Dict[str, Any]]:
    """
    Search for activities and attractions.

    Args:
        city: City name
        category: 'attraction', 'museum', 'tour', 'experience', or 'all'

    Returns:
        List of activities

    TODO: Implement this!
    Hint: Use get_mock_activities() from mock_data.py
    """
    # TODO: Your code here
    pass


def search_restaurants(city: str, cuisine: str = "all") -> List[Dict[str, Any]]:
    """
    Search for restaurants.

    Args:
        city: City name
        cuisine: Cuisine type or 'all'

    Returns:
        List of restaurants

    TODO: Implement this!
    Hint: Use get_mock_restaurants() from mock_data.py
    """
    # TODO: Your code here
    pass


def get_activity_details(activity_id: str) -> Dict[str, Any]:
    """Get detailed activity information - TODO"""
    # TODO: Implement when needed
    return {"id": activity_id, "status": "not_implemented"}


def book_activity(activity_id: str, date: str, participants: int) -> Dict[str, Any]:
    """Book an activity - TODO"""
    # TODO: Implement when needed
    return {"status": "not_implemented"}
