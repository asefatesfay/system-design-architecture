"""
Quick test script to demonstrate all caching patterns.
Run after starting docker-compose and installing dependencies.
"""

import asyncio
import httpx
import time

BASE_URLS = {
    "cache_aside": "http://localhost:8001",
    "read_through": "http://localhost:8002",
    "write_through": "http://localhost:8003",
    "write_behind": "http://localhost:8004",
    "refresh_ahead": "http://localhost:8005",
}

async def test_pattern(pattern_name: str, base_url: str):
    """Test a specific caching pattern."""
    print(f"\n{'='*60}")
    print(f"Testing: {pattern_name.upper().replace('_', '-')}")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Read user (cache miss)
            print("\n1. Reading user 1 (cache miss expected)...")
            start = time.time()
            response = await client.get(f"{base_url}/users/1")
            elapsed = time.time() - start
            if response.status_code == 200:
                print(f"   ✓ User retrieved in {elapsed*1000:.2f}ms")
                print(f"   Data: {response.json()}")
            
            # Test 2: Read same user (cache hit)
            print("\n2. Reading user 1 again (cache hit expected)...")
            start = time.time()
            response = await client.get(f"{base_url}/users/1")
            elapsed = time.time() - start
            if response.status_code == 200:
                print(f"   ✓ User retrieved in {elapsed*1000:.2f}ms (faster!)")
            
            # Test 3: Create new user
            print("\n3. Creating new user...")
            new_user = {
                "name": "Test User",
                "email": f"test_{pattern_name}@example.com",
                "age": 30
            }
            start = time.time()
            response = await client.post(f"{base_url}/users", json=new_user)
            elapsed = time.time() - start
            if response.status_code == 201:
                created = response.json()
                user_id = created["id"]
                print(f"   ✓ User created with ID {user_id} in {elapsed*1000:.2f}ms")
                
                # Test 4: Update user
                print("\n4. Updating user...")
                update_data = {
                    "name": "Updated User",
                    "email": created["email"],
                    "age": 31
                }
                start = time.time()
                response = await client.put(f"{base_url}/users/{user_id}", json=update_data)
                elapsed = time.time() - start
                if response.status_code == 200:
                    print(f"   ✓ User updated in {elapsed*1000:.2f}ms")
                
                # Test 5: Read updated user
                print("\n5. Reading updated user...")
                response = await client.get(f"{base_url}/users/{user_id}")
                if response.status_code == 200:
                    print(f"   ✓ User: {response.json()}")
                
                # Test 6: Delete user
                print("\n6. Deleting user...")
                response = await client.delete(f"{base_url}/users/{user_id}")
                if response.status_code == 204:
                    print(f"   ✓ User deleted")
            
            # Test 7: Get stats
            print("\n7. Cache Statistics:")
            response = await client.get(f"{base_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                for key, value in stats.items():
                    print(f"   {key}: {value}")
            
            print(f"\n✓ {pattern_name.upper().replace('_', '-')} tests completed successfully!")
            
        except httpx.ConnectError:
            print(f"   ✗ Could not connect to {base_url}")
            print(f"   Make sure the service is running:")
            print(f"   poetry run uvicorn {pattern_name}.main:app --port {base_url.split(':')[-1]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          CACHING PATTERNS DEMONSTRATION                      ║
╚══════════════════════════════════════════════════════════════╝

This script tests all 5 caching patterns:
1. Cache-Aside (Lazy Loading)
2. Read-Through
3. Write-Through
4. Write-Behind (Write-Back)
5. Refresh-Ahead

Prerequisites:
- Docker services running (docker-compose up -d)
- All FastAPI apps running on ports 8001-8005

Starting services:
  poetry run uvicorn cache_aside.main:app --port 8001 &
  poetry run uvicorn read_through.main:app --port 8002 &
  poetry run uvicorn write_through.main:app --port 8003 &
  poetry run uvicorn write_behind.main:app --port 8004 &
  poetry run uvicorn refresh_ahead.main:app --port 8005 &
""")
    
    input("Press Enter to start tests...")
    
    for pattern_name, base_url in BASE_URLS.items():
        await test_pattern(pattern_name, base_url)
        await asyncio.sleep(1)
    
    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETED!")
    print(f"{'='*60}")
    print("\nPattern Comparison:")
    print("  Cache-Aside:   Simple, lazy loading, app manages cache")
    print("  Read-Through:  Cache manages DB reads transparently")
    print("  Write-Through: Synchronous writes to cache + DB")
    print("  Write-Behind:  Async writes, batched to DB")
    print("  Refresh-Ahead: Proactive refresh of hot items")

if __name__ == "__main__":
    asyncio.run(main())
