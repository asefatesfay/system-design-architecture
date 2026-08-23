"""
Budget tracking and calculation tools.

TODO: Implement these in Step 6!

These tools don't need external APIs - just calculations.
"""
from typing import Dict, Any, List


def calculate_trip_cost(flights: List[Dict], hotels: List[Dict], activities: List[Dict]) -> Dict[str, Any]:
    """
    Calculate total trip cost from all bookings.

    Args:
        flights: List of flight bookings
        hotels: List of hotel bookings
        activities: List of activity bookings

    Returns:
        Cost breakdown dictionary with 'breakdown' and 'total' keys

    TODO: Implement this!
    Hint:
    - Sum up flight_cost from flights (each has 'total_price')
    - Sum up hotel_cost from hotels (each has 'total_price')
    - Sum up activity_cost from activities
    - Return breakdown dict with categories and total
    """
    # TODO: Your code here
    pass


def check_budget(current_cost: float, budget: float) -> Dict[str, Any]:
    """
    Check if current spending is within budget.

    Args:
        current_cost: Current total spending
        budget: Budget limit

    Returns:
        Budget status dictionary

    TODO: Implement this!
    Hint:
    - Calculate remaining = budget - current_cost
    - Calculate percentage_used
    - Determine status: 'good', 'warning', or 'over_budget'
    - Return dict with budget, spent, remaining, percentage_used, status, message
    """
    # TODO: Your code here
    pass


def suggest_savings(current_bookings: Dict[str, Any], budget: float) -> List[str]:
    """
    Suggest ways to save money.

    Args:
        current_bookings: Dict with flights, hotels, activities
        budget: Budget limit

    Returns:
        List of money-saving suggestions

    TODO: Implement this!
    Hint: Return a list of helpful money-saving tips
    """
    # TODO: Your code here
    pass
