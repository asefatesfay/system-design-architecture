"""
Multi-Agent Travel System - Main Entry Point

Start here for Step 1 of the tutorial!
"""
import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

from .config import config

# Initialize the app
app = BedrockAgentCoreApp()


def setup_environment():
    """Configure AWS environment"""
    config.validate()
    os.environ['AWS_DEFAULT_REGION'] = config.AWS_REGION
    print(f"✓ AWS Profile: {config.AWS_PROFILE}")
    print(f"✓ AWS Region: {config.AWS_REGION}")
    print(f"✓ Bedrock Model: {config.BEDROCK_MODEL}")


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
# STEP 2: Travel Agent with Tools
travel_agent = None


def create_travel_agent():
    """Create the main travel agent with flight search tools (Step 2)"""
    global travel_agent

    travel_agent = Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""You are a travel planning assistant with flight search capabilities.

When users ask about flights:
1. Use search_flights() to find available options
2. Present results clearly showing airline, price, duration, and stops
3. Use get_flight_details() if they want more information about a specific flight
4. Help them choose based on their preferences (price, time, convenience)

For other travel questions, provide helpful advice about destinations, activities, and planning.

Be conversational and helpful!""",
        tools=[search_flights, get_flight_details]  # Include the retrieve tool for additional information
    )
    print("✓ Travel Agent created with flight search tools")


@app.entrypoint
def plan_trip(payload):
    """
    Main endpoint for trip planning

    Now with flight search capability!
    """

    user_message = payload.get("message", "I want to plan a trip")

    # Agent processes the request and can use tools
    result = travel_agent(user_message)

    return {"response": result.message}


def main():
    """Main entry point"""
    print("🌍 Multi-Agent Travel System")
    print("=" * 50)

    # Setup
    setup_environment()
    create_travel_agent()

    print("=" * 50)
    print("🚀 Server starting on http://localhost:8080")
    print("=" * 50)

    # Start the server
    app.run()


if __name__ == "__main__":
    main()
