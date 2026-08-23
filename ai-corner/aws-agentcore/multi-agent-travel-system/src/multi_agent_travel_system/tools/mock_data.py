"""
Mock data for development and testing.

Use this while learning. Later, swap with real API calls.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta


# ============================================================================
# FLIGHTS MOCK DATA
# ============================================================================

def get_mock_flights(origin: str, destination: str, date: str, passengers: int) -> List[Dict[str, Any]]:
    """Generate mock flight data"""

    # Sample airlines and their characteristics
    airlines = [
        {"name": "Delta", "base_price": 450, "quality": "good", "bags": 1},
        {"name": "Air France", "base_price": 520, "quality": "premium", "bags": 2},
        {"name": "United", "base_price": 380, "quality": "budget", "bags": 0},
        {"name": "American", "base_price": 470, "quality": "good", "bags": 1},
        {"name": "British Airways", "base_price": 540, "quality": "premium", "bags": 2},
    ]

    flights = []
    for i, airline in enumerate(airlines[:3], 1):  # Limit to 3 options
        flight = {
            "id": f"FL{i:03d}",
            "airline": airline["name"],
            "origin": origin,
            "destination": destination,
            "date": date,
            "departure": ["08:00 AM", "10:30 AM", "02:00 PM", "06:30 PM"][i % 4],
            "arrival": ["09:30 PM", "11:45 PM", "03:30 AM +1", "07:45 AM +1"][i % 4],
            "duration": ["7h 30m", "7h 15m", "7h 30m", "8h 15m"][i % 4],
            "stops": 0 if i <= 2 else 1,
            "price_per_person": airline["base_price"],
            "total_price": airline["base_price"] * passengers,
            "available_seats": [20, 15, 8, 12][i % 4],
            "aircraft": ["Boeing 777", "Airbus A350", "Boeing 787"][i % 3],
            "amenities": get_flight_amenities(airline["quality"]),
            "baggage_allowance": f"{airline['bags']} checked bag(s) included" if airline['bags'] > 0 else "Baggage fee applies"
        }
        flights.append(flight)

    return flights


def get_flight_amenities(quality: str) -> List[str]:
    """Get amenities based on flight quality"""
    if quality == "premium":
        return ["WiFi", "Premium meals", "Entertainment", "Power outlets", "Extra legroom"]
    elif quality == "good":
        return ["WiFi", "Meals included", "Entertainment", "Power outlets"]
    else:
        return ["Entertainment", "Snacks available for purchase"]


def get_mock_flight_details(flight_id: str) -> Dict[str, Any]:
    """Get detailed mock flight information"""

    flight_details = {
        "FL001": {
            "id": "FL001",
            "airline": "Delta",
            "flight_number": "DL123",
            "aircraft": "Boeing 777",
            "amenities": ["WiFi", "Meals included", "In-flight entertainment", "Power outlets"],
            "baggage": "1 checked bag (50 lbs) included, 1 carry-on",
            "seat_pitch": "32 inches",
            "cancellation_policy": "Free cancellation up to 24h before departure",
            "change_fee": "$200 per person",
            "booking_class": "Economy"
        },
        "FL002": {
            "id": "FL002",
            "airline": "Air France",
            "flight_number": "AF456",
            "aircraft": "Airbus A350",
            "amenities": ["WiFi", "Premium meals", "Entertainment", "USB ports", "Amenity kit"],
            "baggage": "2 checked bags (50 lbs each) included, 1 carry-on",
            "seat_pitch": "34 inches",
            "cancellation_policy": "Free cancellation up to 48h before departure",
            "change_fee": "$150 per person",
            "booking_class": "Economy Premium"
        },
        "FL003": {
            "id": "FL003",
            "airline": "United",
            "flight_number": "UA789",
            "aircraft": "Boeing 787",
            "amenities": ["In-flight entertainment", "Snacks for purchase"],
            "baggage": "1 checked bag ($35 fee), 1 carry-on",
            "seat_pitch": "30 inches",
            "cancellation_policy": "Non-refundable",
            "change_fee": "$300 per person",
            "booking_class": "Basic Economy"
        }
    }

    return flight_details.get(flight_id, {"error": "Flight not found"})


# ============================================================================
# HOTELS MOCK DATA
# ============================================================================

def get_mock_hotels(city: str, checkin: str, checkout: str, guests: int) -> List[Dict[str, Any]]:
    """Generate mock hotel data"""

    hotels = [
        {
            "id": "HTL001",
            "name": "Le Grand Hotel Paris",
            "city": city,
            "address": "123 Rue de Rivoli, 75001 Paris",
            "stars": 5,
            "rating": 4.8,
            "reviews": 1250,
            "checkin": checkin,
            "checkout": checkout,
            "guests": guests,
            "price_per_night": 280,
            "total_price": calculate_nights(checkin, checkout) * 280,
            "room_type": "Deluxe King Room",
            "amenities": ["Free WiFi", "Breakfast included", "Pool", "Spa", "Gym", "Restaurant"],
            "cancellation": "Free cancellation until 3 days before",
            "distance_to_center": "0.5 km"
        },
        {
            "id": "HTL002",
            "name": "Hotel Moderne",
            "city": city,
            "address": "45 Boulevard Saint-Germain, 75005 Paris",
            "stars": 4,
            "rating": 4.5,
            "reviews": 890,
            "checkin": checkin,
            "checkout": checkout,
            "guests": guests,
            "price_per_night": 180,
            "total_price": calculate_nights(checkin, checkout) * 180,
            "room_type": "Standard Double Room",
            "amenities": ["Free WiFi", "Breakfast included", "Restaurant", "24h reception"],
            "cancellation": "Free cancellation until 2 days before",
            "distance_to_center": "1.2 km"
        },
        {
            "id": "HTL003",
            "name": "Budget Inn Paris",
            "city": city,
            "address": "78 Rue de la Republique, 75011 Paris",
            "stars": 3,
            "rating": 4.0,
            "reviews": 456,
            "checkin": checkin,
            "checkout": checkout,
            "guests": guests,
            "price_per_night": 120,
            "total_price": calculate_nights(checkin, checkout) * 120,
            "room_type": "Standard Twin Room",
            "amenities": ["Free WiFi", "24h reception"],
            "cancellation": "Non-refundable",
            "distance_to_center": "2.5 km"
        }
    ]

    return hotels


def calculate_nights(checkin: str, checkout: str) -> int:
    """Calculate number of nights between dates"""
    try:
        checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
        checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
        nights = (checkout_date - checkin_date).days
        return max(1, nights)  # At least 1 night
    except:
        return 3  # Default to 3 nights


def get_mock_hotel_details(hotel_id: str) -> Dict[str, Any]:
    """Get detailed mock hotel information"""

    hotel_details = {
        "HTL001": {
            "id": "HTL001",
            "name": "Le Grand Hotel Paris",
            "description": "Luxury 5-star hotel in the heart of Paris with stunning city views",
            "photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg"],
            "room_details": {
                "size": "35 sqm",
                "bed": "King size",
                "max_guests": 2,
                "view": "City view"
            },
            "facilities": [
                "Indoor pool", "Spa & wellness center", "Fitness center",
                "Restaurant", "Bar", "Room service", "Concierge",
                "Valet parking", "Business center"
            ],
            "policies": {
                "checkin_time": "3:00 PM",
                "checkout_time": "12:00 PM",
                "children": "All ages welcome",
                "pets": "Not allowed"
            }
        },
        "HTL002": {
            "id": "HTL002",
            "name": "Hotel Moderne",
            "description": "Comfortable 4-star hotel with modern amenities",
            "photos": ["photo1.jpg", "photo2.jpg"],
            "room_details": {
                "size": "25 sqm",
                "bed": "Double",
                "max_guests": 2,
                "view": "Street view"
            },
            "facilities": [
                "Restaurant", "Bar", "24h reception",
                "Luggage storage", "Tour desk"
            ],
            "policies": {
                "checkin_time": "2:00 PM",
                "checkout_time": "11:00 AM",
                "children": "All ages welcome",
                "pets": "Allowed with fee"
            }
        },
        "HTL003": {
            "id": "HTL003",
            "name": "Budget Inn Paris",
            "description": "Affordable accommodation with basic amenities",
            "photos": ["photo1.jpg"],
            "room_details": {
                "size": "18 sqm",
                "bed": "2 Twin beds",
                "max_guests": 2,
                "view": "Interior view"
            },
            "facilities": [
                "24h reception", "Luggage storage"
            ],
            "policies": {
                "checkin_time": "2:00 PM",
                "checkout_time": "11:00 AM",
                "children": "All ages welcome",
                "pets": "Not allowed"
            }
        }
    }

    return hotel_details.get(hotel_id, {"error": "Hotel not found"})


# ============================================================================
# ACTIVITIES MOCK DATA
# ============================================================================

def get_mock_activities(city: str, category: str = "all") -> List[Dict[str, Any]]:
    """Generate mock activity/attraction data"""

    activities = [
        {
            "id": "ACT001",
            "name": "Eiffel Tower Tour",
            "city": city,
            "category": "attraction",
            "description": "Skip-the-line access to all floors of the iconic Eiffel Tower",
            "duration": "2 hours",
            "price_per_person": 35,
            "rating": 4.8,
            "reviews": 12450,
            "included": ["Skip-the-line ticket", "Elevator access", "Guide"],
            "location": "Champ de Mars, 5 Avenue Anatole France"
        },
        {
            "id": "ACT002",
            "name": "Louvre Museum Skip-the-Line",
            "city": city,
            "category": "museum",
            "description": "Priority access to the world's largest art museum",
            "duration": "3 hours",
            "price_per_person": 25,
            "rating": 4.7,
            "reviews": 8920,
            "included": ["Skip-the-line ticket", "Audio guide"],
            "location": "Rue de Rivoli, 75001 Paris"
        },
        {
            "id": "ACT003",
            "name": "Seine River Cruise",
            "city": city,
            "category": "experience",
            "description": "1-hour scenic cruise along the Seine with commentary",
            "duration": "1 hour",
            "price_per_person": 18,
            "rating": 4.5,
            "reviews": 5670,
            "included": ["Boat ride", "Audio commentary", "Complimentary drink"],
            "location": "Port de la Bourdonnais"
        },
        {
            "id": "ACT004",
            "name": "Versailles Palace Day Trip",
            "city": city,
            "category": "day-trip",
            "description": "Full-day guided tour of Versailles Palace and Gardens",
            "duration": "8 hours",
            "price_per_person": 75,
            "rating": 4.9,
            "reviews": 3240,
            "included": ["Round-trip transport", "Skip-the-line ticket", "Guide", "Lunch"],
            "location": "Pickup from Paris hotel"
        },
        {
            "id": "ACT005",
            "name": "Montmartre Walking Tour",
            "city": city,
            "category": "tour",
            "description": "2-hour walking tour of artistic Montmartre neighborhood",
            "duration": "2 hours",
            "price_per_person": 20,
            "rating": 4.6,
            "reviews": 1890,
            "included": ["Local guide", "Small group"],
            "location": "Meet at Sacré-Cœur"
        }
    ]

    # Filter by category if specified
    if category != "all":
        activities = [a for a in activities if a["category"] == category]

    return activities


def get_mock_restaurants(city: str, cuisine: str = "all") -> List[Dict[str, Any]]:
    """Generate mock restaurant data"""

    restaurants = [
        {
            "id": "REST001",
            "name": "Le Jules Verne",
            "city": city,
            "cuisine": "French",
            "price_level": "$$$",
            "rating": 4.7,
            "reviews": 2340,
            "location": "Eiffel Tower, 2nd floor",
            "specialties": ["Duck confit", "Soufflé", "Fine wines"],
            "avg_cost_per_person": 120,
            "reservation_required": True
        },
        {
            "id": "REST002",
            "name": "L'As du Fallafel",
            "city": city,
            "cuisine": "Middle Eastern",
            "price_level": "$",
            "rating": 4.5,
            "reviews": 5670,
            "location": "Le Marais",
            "specialties": ["Falafel sandwich", "Shawarma", "Hummus"],
            "avg_cost_per_person": 15,
            "reservation_required": False
        },
        {
            "id": "REST003",
            "name": "Le Comptoir du Relais",
            "city": city,
            "cuisine": "Bistro",
            "price_level": "$$",
            "rating": 4.6,
            "reviews": 1890,
            "location": "Saint-Germain-des-Prés",
            "specialties": ["Steak tartare", "French onion soup", "Crème brûlée"],
            "avg_cost_per_person": 45,
            "reservation_required": True
        },
        {
            "id": "REST004",
            "name": "Pink Mamma",
            "city": city,
            "cuisine": "Italian",
            "price_level": "$$",
            "rating": 4.4,
            "reviews": 3120,
            "location": "Pigalle",
            "specialties": ["Pizza", "Pasta", "Tiramisu"],
            "avg_cost_per_person": 35,
            "reservation_required": True
        }
    ]

    # Filter by cuisine if specified
    if cuisine != "all":
        restaurants = [r for r in restaurants if r["cuisine"].lower() == cuisine.lower()]

    return restaurants


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def add_price_variation(base_price: float, variation_percent: float = 10) -> float:
    """Add random price variation to make data more realistic"""
    import random
    variation = base_price * (variation_percent / 100)
    return round(base_price + random.uniform(-variation, variation), 2)


def generate_booking_reference() -> str:
    """Generate a mock booking reference"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
