"""
With Ambassador Pattern
Solution: Centralized connectivity logic in Ambassador service
"""

import requests
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class APIAmbassador:
    """
    Ambassador service that handles all connectivity concerns:
    - Retry logic with exponential backoff
    - Circuit breaker pattern
    - Request/response logging
    - Metrics collection
    - Rate limiting
    - Timeout handling
    """

    def __init__(
        self,
        base_url: str,
        retry_count: int = 3,
        timeout: int = 5,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
        rate_limit: int = 100,  # requests per second
    ):
        self.base_url = base_url
        self.retry_count = retry_count
        self.timeout = timeout

        # Circuit breaker
        self.circuit_state = CircuitState.CLOSED
        self.failure_count = 0
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.circuit_opened_at = None

        # Rate limiting (token bucket)
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.last_refill = time.time()

        # Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        self.retry_count_total = 0

    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows request"""
        if self.circuit_state == CircuitState.CLOSED:
            return True

        if self.circuit_state == CircuitState.OPEN:
            # Check if timeout has passed
            if time.time() - self.circuit_opened_at > self.circuit_breaker_timeout:
                logger.info("Circuit breaker: OPEN → HALF_OPEN (testing recovery)")
                self.circuit_state = CircuitState.HALF_OPEN
                return True
            else:
                logger.warning("Circuit breaker: Request rejected (circuit OPEN)")
                return False

        if self.circuit_state == CircuitState.HALF_OPEN:
            return True

        return False

    def _handle_success(self):
        """Handle successful request for circuit breaker"""
        if self.circuit_state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker: HALF_OPEN → CLOSED (service recovered)")
            self.circuit_state = CircuitState.CLOSED
            self.failure_count = 0
        elif self.circuit_state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)

    def _handle_failure(self):
        """Handle failed request for circuit breaker"""
        self.failure_count += 1

        if self.failure_count >= self.circuit_breaker_threshold:
            if self.circuit_state != CircuitState.OPEN:
                logger.error(
                    f"Circuit breaker: {self.circuit_state.value} → OPEN "
                    f"(threshold {self.circuit_breaker_threshold} reached)"
                )
                self.circuit_state = CircuitState.OPEN
                self.circuit_opened_at = time.time()

    def _rate_limit_check(self) -> bool:
        """Token bucket rate limiting"""
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens
        self.tokens = min(
            self.rate_limit,
            self.tokens + elapsed * self.rate_limit
        )
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        else:
            logger.warning("Rate limit exceeded, request delayed")
            return False

    def _execute_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> requests.Response:
        """Execute HTTP request with timeout"""
        url = f"{self.base_url}{endpoint}"

        if method.upper() == "GET":
            return requests.get(url, headers=headers, timeout=self.timeout)
        elif method.upper() == "POST":
            return requests.post(url, json=data, headers=headers, timeout=self.timeout)
        elif method.upper() == "PUT":
            return requests.put(url, json=data, headers=headers, timeout=self.timeout)
        elif method.upper() == "DELETE":
            return requests.delete(url, headers=headers, timeout=self.timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request through Ambassador with:
        - Circuit breaker protection
        - Rate limiting
        - Automatic retries
        - Logging and metrics
        """
        self.total_requests += 1
        start_time = time.time()

        # Check circuit breaker
        if not self._check_circuit_breaker():
            self.failed_requests += 1
            return {
                "success": False,
                "error": "Circuit breaker open - service unavailable"
            }

        # Rate limiting
        while not self._rate_limit_check():
            time.sleep(0.01)  # Wait for tokens

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.retry_count):
            try:
                logger.info(
                    f"Ambassador: {method.upper()} {endpoint} "
                    f"(attempt {attempt + 1}/{self.retry_count})"
                )

                response = self._execute_request(method, endpoint, data, headers)

                # Calculate latency
                latency = time.time() - start_time
                self.total_latency += latency

                # Log response
                logger.info(
                    f"Ambassador: Response {response.status_code} "
                    f"({latency:.3f}s)"
                )

                # Handle response
                if response.status_code == 200:
                    self._handle_success()
                    self.successful_requests += 1
                    return {
                        "success": True,
                        "data": response.json() if response.text else {},
                        "status_code": response.status_code,
                        "latency": latency,
                    }
                elif response.status_code >= 500:
                    # Server error - retry
                    self._handle_failure()
                    if attempt < self.retry_count - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(
                            f"Ambassador: Server error, retrying in {wait_time}s..."
                        )
                        self.retry_count_total += 1
                        time.sleep(wait_time)
                        continue
                    else:
                        self.failed_requests += 1
                        return {
                            "success": False,
                            "error": f"Server error: {response.status_code}",
                            "status_code": response.status_code,
                        }
                else:
                    # Client error (4xx) - don't retry
                    self.failed_requests += 1
                    return {
                        "success": False,
                        "error": f"Client error: {response.text}",
                        "status_code": response.status_code,
                    }

            except requests.exceptions.Timeout:
                logger.error(f"Ambassador: Timeout on attempt {attempt + 1}")
                self._handle_failure()
                last_error = "Request timeout"
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    self.retry_count_total += 1
                    continue

            except requests.exceptions.ConnectionError:
                logger.error(f"Ambassador: Connection error on attempt {attempt + 1}")
                self._handle_failure()
                last_error = "Connection failed"
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    self.retry_count_total += 1
                    continue

            except Exception as e:
                logger.error(f"Ambassador: Unexpected error: {e}")
                self._handle_failure()
                last_error = str(e)
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
                    self.retry_count_total += 1
                    continue

        # All retries exhausted
        self.failed_requests += 1
        return {
            "success": False,
            "error": last_error or "Max retries exceeded",
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        avg_latency = (
            self.total_latency / self.successful_requests
            if self.successful_requests > 0
            else 0
        )

        success_rate = (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0
            else 0
        )

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{success_rate:.1f}%",
            "average_latency": f"{avg_latency:.3f}s",
            "total_retries": self.retry_count_total,
            "circuit_breaker_state": self.circuit_state.value,
            "failure_count": self.failure_count,
        }


# Now services are SIMPLE - just business logic!
class PaymentService:
    """Clean payment service - no retry/logging clutter"""

    def __init__(self, ambassador: APIAmbassador):
        self.ambassador = ambassador

    def process_payment(self, amount: float, currency: str) -> Dict[str, Any]:
        """Process payment through Ambassador - clean and simple!"""
        return self.ambassador.request(
            method="POST",
            endpoint="/charge",
            data={"amount": amount, "currency": currency},
        )


class ShippingService:
    """Clean shipping service - Ambassador handles connectivity"""

    def __init__(self, ambassador: APIAmbassador):
        self.ambassador = ambassador

    def create_shipment(self, address: str) -> Dict[str, Any]:
        """Create shipment through Ambassador"""
        return self.ambassador.request(
            method="POST",
            endpoint="/shipment",
            data={"address": address},
        )


class NotificationService:
    """Clean notification service - consistent with others!"""

    def __init__(self, ambassador: APIAmbassador):
        self.ambassador = ambassador

    def send_email(self, recipient: str, subject: str) -> Dict[str, Any]:
        """Send email through Ambassador"""
        return self.ambassador.request(
            method="POST",
            endpoint="/email",
            data={"to": recipient, "subject": subject},
        )


def main():
    """Demonstrate Ambassador pattern benefits"""

    print("=" * 60)
    print("WITH AMBASSADOR PATTERN")
    print("=" * 60)
    print("\n✅ Benefits:")
    print("1. Centralized retry logic (DRY principle)")
    print("2. Consistent behavior across all services")
    print("3. Easy to test (mock ambassador)")
    print("4. Centralized monitoring (single metrics source)")
    print("5. Easy to change (update ambassador only)")
    print("6. Circuit breaker prevents cascading failures")
    print("7. Rate limiting prevents API bans")
    print("\n")

    # Single Ambassador instance for all services!
    ambassador = APIAmbassador(
        base_url="http://localhost:8080",
        retry_count=3,
        timeout=5,
        circuit_breaker_threshold=5,
        rate_limit=100,
    )

    # Initialize services with shared Ambassador
    payment = PaymentService(ambassador)
    shipping = ShippingService(ambassador)
    notification = NotificationService(ambassador)

    # Process order
    print("Processing order...")
    print("-" * 60)

    # Payment - notice how clean the service code is!
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

    # Show centralized metrics
    print("\n" + "=" * 60)
    print("CENTRALIZED METRICS (from Ambassador)")
    print("=" * 60)
    metrics = ambassador.get_metrics()
    for key, value in metrics.items():
        print(f"{key:.<30} {value}")

    print("\n" + "=" * 60)
    print("Improvements demonstrated:")
    print("- All retry logic handled by Ambassador")
    print("- Consistent behavior across services")
    print("- Single source for metrics and monitoring")
    print("- Services contain only business logic")
    print("=" * 60)


if __name__ == "__main__":
    main()
