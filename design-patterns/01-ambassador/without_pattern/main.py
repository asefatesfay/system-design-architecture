"""
Without Ambassador Pattern
Problem: Every service has duplicate retry, logging, and error handling logic
"""

import requests
import time
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaymentService:
    """Direct API calls with manual retry logic"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.retry_count = 3
        self.timeout = 5

    def process_payment(self, amount: float, currency: str) -> Dict[str, Any]:
        """Process payment with manual retry logic"""
        start_time = time.time()

        for attempt in range(self.retry_count):
            try:
                logger.info(f"Payment API call attempt {attempt + 1}/{self.retry_count}")

                response = requests.post(
                    f"{self.api_url}/charge",
                    json={"amount": amount, "currency": currency},
                    timeout=self.timeout
                )

                # Manual logging
                duration = time.time() - start_time
                logger.info(f"Payment API response: {response.status_code} ({duration:.2f}s)")

                # Manual error handling
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                elif response.status_code >= 500:
                    # Server error - retry
                    if attempt < self.retry_count - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Server error, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {"success": False, "error": "Server error after retries"}
                else:
                    # Client error - don't retry
                    return {"success": False, "error": response.text}

            except requests.exceptions.Timeout:
                logger.error(f"Timeout on attempt {attempt + 1}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Timeout"}

            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error on attempt {attempt + 1}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Connection failed"}

        return {"success": False, "error": "Max retries exceeded"}


class ShippingService:
    """Another service with DUPLICATE retry logic"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.retry_count = 3  # Duplicated!
        self.timeout = 5  # Duplicated!

    def create_shipment(self, address: str) -> Dict[str, Any]:
        """Create shipment with DUPLICATE retry logic"""
        start_time = time.time()

        # Same retry logic as PaymentService - CODE DUPLICATION!
        for attempt in range(self.retry_count):
            try:
                logger.info(f"Shipping API call attempt {attempt + 1}/{self.retry_count}")

                response = requests.post(
                    f"{self.api_url}/shipment",
                    json={"address": address},
                    timeout=self.timeout
                )

                duration = time.time() - start_time
                logger.info(f"Shipping API response: {response.status_code} ({duration:.2f}s)")

                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                elif response.status_code >= 500:
                    if attempt < self.retry_count - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Server error, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return {"success": False, "error": "Server error after retries"}
                else:
                    return {"success": False, "error": response.text}

            except requests.exceptions.Timeout:
                logger.error(f"Timeout on attempt {attempt + 1}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Timeout"}

            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error on attempt {attempt + 1}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Connection failed"}

        return {"success": False, "error": "Max retries exceeded"}


class NotificationService:
    """Yet another service with DUPLICATE retry logic"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.retry_count = 2  # Different config - INCONSISTENT!
        self.timeout = 3  # Different timeout - INCONSISTENT!

    def send_email(self, recipient: str, subject: str) -> Dict[str, Any]:
        """Send email with YET ANOTHER duplicate retry implementation"""
        # Yet another copy of retry logic - THIRD TIME!
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    f"{self.api_url}/email",
                    json={"to": recipient, "subject": subject},
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return {"success": True}
                elif response.status_code >= 500 and attempt < self.retry_count - 1:
                    time.sleep(1)  # Simple sleep - INCONSISTENT with others!
                    continue

            except Exception as e:
                logger.error(f"Email error: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)
                    continue

        return {"success": False, "error": "Failed to send email"}


def main():
    """Demonstrate the problems without Ambassador pattern"""

    print("=" * 60)
    print("WITHOUT AMBASSADOR PATTERN")
    print("=" * 60)
    print("\n❌ Problems:")
    print("1. Code duplication across services (retry logic repeated 3 times)")
    print("2. Inconsistent behavior (different retry counts, timeouts)")
    print("3. Hard to test (network logic mixed with business logic)")
    print("4. Difficult to monitor (logging scattered everywhere)")
    print("5. Hard to change (need to update multiple services)")
    print("\n")

    # Initialize services
    payment = PaymentService("http://localhost:8080")
    shipping = ShippingService("http://localhost:8080")
    notification = NotificationService("http://localhost:8080")

    # Process order
    print("Processing order...")
    print("-" * 60)

    # Payment
    print("\n1. Processing payment...")
    payment_result = payment.process_payment(amount=99.99, currency="USD")
    print(f"   Result: {payment_result}")

    # Shipping
    print("\n2. Creating shipment...")
    shipping_result = shipping.create_shipment(address="123 Main St")
    print(f"   Result: {shipping_result}")

    # Notification
    print("\n3. Sending confirmation email...")
    email_result = notification.send_email(
        recipient="customer@example.com",
        subject="Order Confirmation"
    )
    print(f"   Result: {email_result}")

    print("\n" + "=" * 60)
    print("Issues demonstrated:")
    print("- Notice the duplicate retry logic in the logs")
    print("- Each service implements the same pattern differently")
    print("- Hard to ensure consistent behavior across services")
    print("=" * 60)


if __name__ == "__main__":
    main()
