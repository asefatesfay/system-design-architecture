"""
Interactive demo comparing code without and with Ambassador pattern

Requirements:
1. Start mock API server: python demo/mock_api.py
2. Run this demo: python demo/run_demo.py
"""

import sys
import os
import time

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'without_pattern'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'with_pattern'))

import requests


def check_api_server():
    """Check if mock API server is running"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def run_without_ambassador():
    """Run demo without Ambassador pattern"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "WITHOUT AMBASSADOR PATTERN" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Import here to avoid conflicts
    from main import PaymentService, ShippingService, NotificationService

    payment = PaymentService("http://localhost:8080")
    shipping = ShippingService("http://localhost:8080")
    notification = NotificationService("http://localhost:8080")

    print("📦 Processing order without Ambassador...")
    print("-" * 60)

    start_time = time.time()

    # Payment
    print("\n💳 Step 1: Processing payment")
    payment_result = payment.process_payment(amount=99.99, currency="USD")
    print(f"   → {payment_result['success'] and '✅ Success' or '❌ Failed'}: {payment_result}")

    # Shipping
    print("\n📮 Step 2: Creating shipment")
    shipping_result = shipping.create_shipment(address="123 Main St, New York, NY")
    print(f"   → {shipping_result['success'] and '✅ Success' or '❌ Failed'}: {shipping_result}")

    # Notification
    print("\n📧 Step 3: Sending confirmation email")
    email_result = notification.send_email(
        recipient="customer@example.com",
        subject="Your Order #12345 Confirmation"
    )
    print(f"   → {email_result['success'] and '✅ Success' or '❌ Failed'}: {email_result}")

    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"⏱️  Total time: {total_time:.2f}s")
    print("=" * 60)

    print("\n❌ Problems observed:")
    print("   • Retry logic duplicated in each service")
    print("   • Inconsistent error handling")
    print("   • Scattered logging")
    print("   • No centralized metrics")
    print("   • Hard to enforce policies")

    return total_time


def run_with_ambassador():
    """Run demo with Ambassador pattern"""
    print("\n\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 17 + "WITH AMBASSADOR PATTERN" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Import here to avoid conflicts
    from main import APIAmbassador, PaymentService, ShippingService, NotificationService

    # Single Ambassador for all services
    ambassador = APIAmbassador(
        base_url="http://localhost:8080",
        retry_count=3,
        timeout=5,
        circuit_breaker_threshold=5,
        rate_limit=100,
    )

    payment = PaymentService(ambassador)
    shipping = ShippingService(ambassador)
    notification = NotificationService(ambassador)

    print("📦 Processing order WITH Ambassador...")
    print("-" * 60)

    start_time = time.time()

    # Payment
    print("\n💳 Step 1: Processing payment")
    payment_result = payment.process_payment(amount=99.99, currency="USD")
    print(f"   → {payment_result['success'] and '✅ Success' or '❌ Failed'}")
    if payment_result['success']:
        print(f"      Latency: {payment_result['latency']:.3f}s")

    # Shipping
    print("\n📮 Step 2: Creating shipment")
    shipping_result = shipping.create_shipment(address="123 Main St, New York, NY")
    print(f"   → {shipping_result['success'] and '✅ Success' or '❌ Failed'}")
    if shipping_result['success']:
        print(f"      Latency: {shipping_result['latency']:.3f}s")

    # Notification
    print("\n📧 Step 3: Sending confirmation email")
    email_result = notification.send_email(
        recipient="customer@example.com",
        subject="Your Order #12345 Confirmation"
    )
    print(f"   → {email_result['success'] and '✅ Success' or '❌ Failed'}")
    if email_result['success']:
        print(f"      Latency: {email_result['latency']:.3f}s")

    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"⏱️  Total time: {total_time:.2f}s")
    print("=" * 60)

    # Show centralized metrics
    print("\n📊 CENTRALIZED METRICS (from Ambassador)")
    print("-" * 60)
    metrics = ambassador.get_metrics()
    print(f"   Total Requests:      {metrics['total_requests']}")
    print(f"   Successful:          {metrics['successful_requests']}")
    print(f"   Failed:              {metrics['failed_requests']}")
    print(f"   Success Rate:        {metrics['success_rate']}")
    print(f"   Average Latency:     {metrics['average_latency']}")
    print(f"   Total Retries:       {metrics['total_retries']}")
    print(f"   Circuit State:       {metrics['circuit_breaker_state']}")
    print(f"   Failure Count:       {metrics['failure_count']}")

    print("\n✅ Benefits demonstrated:")
    print("   • Centralized retry logic (no duplication)")
    print("   • Consistent error handling")
    print("   • Unified logging and monitoring")
    print("   • Single source for metrics")
    print("   • Circuit breaker protection")
    print("   • Rate limiting built-in")
    print("   • Easy to test and maintain")

    return total_time


def run_comparison():
    """Run side-by-side comparison"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "AMBASSADOR PATTERN - COMPARISON DEMO" + " " * 16 + "║")
    print("╚" + "=" * 68 + "╝")

    # Check API server
    print("\n🔍 Checking mock API server...")
    if not check_api_server():
        print("❌ ERROR: Mock API server not running!")
        print("\nPlease start it first:")
        print("   python demo/mock_api.py")
        print("\nThen run this demo again.")
        return

    print("✅ Mock API server is running")

    # Run both demos
    time_without = run_without_ambassador()
    time_with = run_with_ambassador()

    # Final comparison
    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 25 + "FINAL COMPARISON" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    print("┌─────────────────────────────────┬──────────────┬──────────────┐")
    print("│ Metric                          │ Without      │ With         │")
    print("├─────────────────────────────────┼──────────────┼──────────────┤")
    print(f"│ Code Duplication                │ ❌ High      │ ✅ None      │")
    print(f"│ Consistency                     │ ❌ Low       │ ✅ High      │")
    print(f"│ Maintainability                 │ ❌ Hard      │ ✅ Easy      │")
    print(f"│ Testability                     │ ❌ Hard      │ ✅ Easy      │")
    print(f"│ Monitoring                      │ ❌ Scattered │ ✅ Unified   │")
    print(f"│ Circuit Breaker                 │ ❌ No        │ ✅ Yes       │")
    print(f"│ Rate Limiting                   │ ❌ No        │ ✅ Yes       │")
    print(f"│ Execution Time                  │ {time_without:.2f}s       │ {time_with:.2f}s      │")
    print("└─────────────────────────────────┴──────────────┴──────────────┘")

    print("\n🎯 Key Takeaway:")
    print("   The Ambassador pattern centralizes connectivity concerns,")
    print("   making code cleaner, more consistent, and easier to maintain.")
    print("   The small latency overhead is worth the operational benefits!")

    print("\n💡 When to use Ambassador:")
    print("   ✓ Multiple services calling external APIs")
    print("   ✓ Need consistent retry/timeout behavior")
    print("   ✓ Want centralized monitoring")
    print("   ✓ Polyglot microservices")
    print("   ✓ Need to enforce policies (rate limits, circuit breakers)")

    print("\n📚 Learn more:")
    print("   • Microsoft: https://learn.microsoft.com/azure/architecture/patterns/ambassador")
    print("   • Pattern README: ../README.md")
    print("\n")


if __name__ == "__main__":
    run_comparison()
