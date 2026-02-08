"""
Example: Using the Proximity Service API with a generated Python client

Prerequisites:
    pip install requests pyyaml

Generate client:
    openapi-generator-cli generate -i openapi.yaml -g python -o ./client
    cd client && pip install -e .
"""

import requests
from typing import List, Dict, Optional
import json


class ProximityServiceClient:
    """Simple client for Proximity Service API (without code generation)"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius: int = 5000,
        place_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        open_now: Optional[bool] = None,
        min_rating: Optional[float] = None
    ) -> Dict:
        """
        Search for places near a location
        
        Args:
            latitude: Latitude of search center
            longitude: Longitude of search center
            radius: Search radius in meters (default: 5000)
            place_type: Filter by type (e.g., 'restaurant', 'cafe')
            limit: Max results to return (default: 20)
            offset: Pagination offset (default: 0)
            open_now: Filter to only open places
            min_rating: Minimum rating (0-5)
            
        Returns:
            Dict with keys: places (list), total (int), has_more (bool)
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius,
            'limit': limit,
            'offset': offset
        }
        
        if place_type:
            params['type'] = place_type
        if open_now is not None:
            params['open_now'] = str(open_now).lower()
        if min_rating is not None:
            params['min_rating'] = min_rating
        
        response = self.session.get(
            f'{self.base_url}/places/nearby',
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_place(self, place_id: str) -> Dict:
        """
        Get detailed information about a place
        
        Args:
            place_id: Unique place identifier
            
        Returns:
            Dict with place details
        """
        response = self.session.get(
            f'{self.base_url}/places/{place_id}'
        )
        response.raise_for_status()
        return response.json()
    
    def create_place(self, place_data: Dict) -> Dict:
        """
        Create a new place (requires authentication)
        
        Args:
            place_data: Dict with place information
                Required: name, address, location, type
                Optional: phone, website, hours
                
        Returns:
            Dict with place_id, message, created_at
        """
        response = self.session.post(
            f'{self.base_url}/places',
            json=place_data
        )
        response.raise_for_status()
        return response.json()
    
    def update_place(self, place_id: str, updates: Dict) -> Dict:
        """
        Update an existing place (requires authentication)
        
        Args:
            place_id: Place to update
            updates: Dict with fields to update
            
        Returns:
            Dict with place_id, message, updated_at
        """
        response = self.session.put(
            f'{self.base_url}/places/{place_id}',
            json=updates
        )
        response.raise_for_status()
        return response.json()
    
    def delete_place(self, place_id: str) -> None:
        """
        Delete a place (requires authentication)
        
        Args:
            place_id: Place to delete
        """
        response = self.session.delete(
            f'{self.base_url}/places/{place_id}'
        )
        response.raise_for_status()
    
    def search_area(
        self,
        polygon: List[Dict[str, float]],
        place_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict:
        """
        Search places within a polygon area
        
        Args:
            polygon: List of {"latitude": float, "longitude": float}
            place_type: Filter by type
            limit: Max results
            
        Returns:
            Dict with places, total, has_more
        """
        payload = {
            'polygon': polygon,
            'limit': limit
        }
        if place_type:
            payload['type'] = place_type
        
        response = self.session.post(
            f'{self.base_url}/places/search-area',
            json=payload
        )
        response.raise_for_status()
        return response.json()


# ========================================
# Example Usage
# ========================================

def main():
    # Initialize client
    client = ProximityServiceClient(
        base_url='https://api.proximity.example.com/v1',
        api_key='your-jwt-token-here'  # Only needed for write operations
    )
    
    # Example 1: Search for restaurants near San Francisco
    print("Example 1: Search nearby restaurants")
    print("=" * 50)
    
    results = client.search_nearby(
        latitude=37.7749,
        longitude=-122.4194,
        radius=5000,  # 5km
        place_type='restaurant',
        limit=10,
        open_now=True,
        min_rating=4.0
    )
    
    print(f"Found {results['total']} restaurants")
    print(f"\nTop {len(results['places'])} results:")
    
    for place in results['places']:
        print(f"\n  🍽️  {place['name']}")
        print(f"      {place['address']}")
        print(f"      ⭐ {place['rating']} - 📍 {place['distance']}m away")
        print(f"      {'🟢 Open' if place['is_open'] else '🔴 Closed'}")
    
    # Example 2: Get place details
    if results['places']:
        print("\n\nExample 2: Get place details")
        print("=" * 50)
        
        first_place = results['places'][0]
        details = client.get_place(first_place['place_id'])
        
        print(f"\n{details['name']}")
        print(f"📞 {details.get('phone', 'N/A')}")
        print(f"🌐 {details.get('website', 'N/A')}")
        print(f"\n⏰ Business hours:")
        for day, hours in details.get('hours', {}).items():
            print(f"   {day.capitalize()}: {hours}")
    
    # Example 3: Search within polygon
    print("\n\nExample 3: Search within area")
    print("=" * 50)
    
    # Define a triangle area in SF
    polygon = [
        {"latitude": 37.7749, "longitude": -122.4194},
        {"latitude": 37.7849, "longitude": -122.4094},
        {"latitude": 37.7649, "longitude": -122.4094}
    ]
    
    area_results = client.search_area(
        polygon=polygon,
        place_type='cafe',
        limit=20
    )
    
    print(f"Found {area_results['total']} cafes in the area")
    
    # Example 4: Create a new place (requires authentication)
    print("\n\nExample 4: Create new place")
    print("=" * 50)
    
    try:
        new_place = client.create_place({
            "name": "My New Cafe",
            "address": "123 Main St, San Francisco, CA 94102",
            "location": {
                "latitude": 37.7850,
                "longitude": -122.4100
            },
            "phone": "+14155550123",
            "website": "https://mynewcafe.com",
            "type": "cafe",
            "hours": {
                "monday": "08:00-20:00",
                "tuesday": "08:00-20:00",
                "wednesday": "08:00-20:00",
                "thursday": "08:00-20:00",
                "friday": "08:00-20:00",
                "saturday": "09:00-21:00",
                "sunday": "09:00-21:00"
            }
        })
        
        print(f"✅ Created place: {new_place['place_id']}")
        print(f"   Created at: {new_place['created_at']}")
        
        # Example 5: Update the place
        print("\n\nExample 5: Update place")
        print("=" * 50)
        
        update_response = client.update_place(
            new_place['place_id'],
            {
                "name": "My New Cafe - Updated",
                "hours": {
                    "monday": "07:00-21:00"
                }
            }
        )
        
        print(f"✅ Updated place: {update_response['place_id']}")
        print(f"   Updated at: {update_response['updated_at']}")
        
        # Example 6: Delete the place
        print("\n\nExample 6: Delete place")
        print("=" * 50)
        
        client.delete_place(new_place['place_id'])
        print(f"✅ Deleted place: {new_place['place_id']}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Authentication required for write operations")
            print("   Set api_key when initializing the client")
        else:
            print(f"❌ Error: {e.response.json()}")
    
    # Example 7: Error handling
    print("\n\nExample 7: Error handling")
    print("=" * 50)
    
    try:
        client.search_nearby(
            latitude=200,  # Invalid latitude
            longitude=-122.4194
        )
    except requests.exceptions.HTTPError as e:
        error = e.response.json()
        print(f"❌ {error['error']}: {error['message']}")


# ========================================
# Using Generated Client
# ========================================

def example_with_generated_client():
    """
    Example using auto-generated client from OpenAPI spec
    
    First, generate the client:
        openapi-generator-cli generate -i openapi.yaml -g python -o ./client
        cd client && pip install -e .
    """
    
    # Uncomment when you have the generated client
    """
    from proximity_client import ApiClient, Configuration, SearchApi, PlacesApi
    from proximity_client.models import CreatePlaceRequest, Location
    
    # Configure API client
    config = Configuration(
        host="https://api.proximity.example.com/v1"
    )
    
    # For authenticated requests
    config.access_token = "your-jwt-token"
    
    client = ApiClient(configuration=config)
    search_api = SearchApi(client)
    places_api = PlacesApi(client)
    
    # Search nearby places (with type hints and auto-completion!)
    response = search_api.search_nearby_places(
        latitude=37.7749,
        longitude=-122.4194,
        radius=5000,
        type="restaurant",
        limit=20
    )
    
    # Type-safe response
    for place in response.places:
        print(f"{place.name} - {place.distance}m")
    
    # Create place with type-safe request
    new_place_request = CreatePlaceRequest(
        name="New Cafe",
        address="123 Main St, San Francisco, CA",
        location=Location(latitude=37.7850, longitude=-122.4100),
        type="cafe"
    )
    
    created = places_api.create_place(new_place_request)
    print(f"Created: {created.place_id}")
    """
    pass


if __name__ == '__main__':
    # Run manual client examples
    # main()
    
    # For generated client examples, uncomment:
    # example_with_generated_client()
    
    print("\n📝 Note: Set base_url and api_key before running examples")
    print("   Or use mock server: prism mock openapi.yaml -p 8080")
