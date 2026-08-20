"""
With Anti-Corruption Layer Pattern
Solution: Clean domain model isolated from legacy system
"""

import requests
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from decimal import Decimal


# ============================================================================
# CLEAN DOMAIN MODEL (No legacy pollution!)
# ============================================================================

class CustomerStatus(Enum):
    """Clean enum instead of cryptic codes"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CustomerType(Enum):
    """Clean enum for customer types"""
    REGULAR = "regular"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class OrderStatus(Enum):
    """Clean enum for order status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Address:
    """Clean nested address object"""
    street: str
    city: str
    zip_code: str

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.zip_code}"


@dataclass
class Customer:
    """Clean domain model for Customer"""
    id: str
    email: str
    full_name: str  # Combined, not split
    address: Address  # Nested object, not flat
    status: CustomerStatus  # Enum, not code
    customer_type: CustomerType  # Enum, not code
    created_at: datetime  # Proper datetime, not string

    def is_active(self) -> bool:
        """Business logic in domain model"""
        return self.status == CustomerStatus.ACTIVE


@dataclass
class OrderItem:
    """Clean order item model"""
    product_id: str
    quantity: int
    unit_price: Decimal  # Proper decimal, not string


@dataclass
class Order:
    """Clean domain model for Order"""
    id: str
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus  # Enum, not code
    shipping_address: Address  # Nested object
    order_date: datetime  # Proper datetime

    @property
    def total_amount(self) -> Decimal:
        """Business logic in domain"""
        return sum(item.quantity * item.unit_price for item in self.items)


# ============================================================================
# ANTI-CORRUPTION LAYER - Translators
# ============================================================================

class CustomerTranslator:
    """Translates between legacy format and domain model"""

    @staticmethod
    def to_domain(legacy_data: dict) -> Customer:
        """Convert legacy format → clean domain model"""
        # Map status codes to enum
        status_map = {
            "A": CustomerStatus.ACTIVE,
            "I": CustomerStatus.INACTIVE,
            "S": CustomerStatus.SUSPENDED
        }

        # Map customer type codes to enum
        type_map = {
            "R": CustomerType.REGULAR,
            "P": CustomerType.PREMIUM,
            "E": CustomerType.ENTERPRISE
        }

        # Parse weird date format
        created_at = datetime.strptime(
            legacy_data['CREATE_DT'],
            "%Y%m%d%H%M%S"
        )

        # Create nested address object
        address = Address(
            street=legacy_data['ADDR_LN1'],
            city=legacy_data['ADDR_CITY'],
            zip_code=legacy_data['ADDR_ZIP']
        )

        # Combine split name
        full_name = f"{legacy_data['F_NAME']} {legacy_data['L_NAME']}"

        return Customer(
            id=legacy_data['CUST_ID'],
            email=legacy_data['EMAIL_ADDR'],
            full_name=full_name,
            address=address,
            status=status_map.get(legacy_data['STATUS_CD'], CustomerStatus.INACTIVE),
            customer_type=type_map.get(legacy_data.get('CUST_TYP', 'R'), CustomerType.REGULAR),
            created_at=created_at
        )

    @staticmethod
    def to_legacy(customer: Customer) -> dict:
        """Convert clean domain model → legacy format"""
        # Reverse mapping
        status_map = {
            CustomerStatus.ACTIVE: "A",
            CustomerStatus.INACTIVE: "I",
            CustomerStatus.SUSPENDED: "S"
        }

        type_map = {
            CustomerType.REGULAR: "R",
            CustomerType.PREMIUM: "P",
            CustomerType.ENTERPRISE: "E"
        }

        # Split full name (simple split, could be more sophisticated)
        name_parts = customer.full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        return {
            "CUST_ID": customer.id,
            "F_NAME": first_name,
            "L_NAME": last_name,
            "EMAIL_ADDR": customer.email,
            "ADDR_LN1": customer.address.street,
            "ADDR_CITY": customer.address.city,
            "ADDR_ZIP": customer.address.zip_code,
            "STATUS_CD": status_map[customer.status],
            "CUST_TYP": type_map[customer.customer_type],
            "CREATE_DT": customer.created_at.strftime("%Y%m%d%H%M%S")
        }


class OrderTranslator:
    """Translates order between legacy format and domain model"""

    @staticmethod
    def to_domain(legacy_data: dict) -> Order:
        """Convert legacy format → clean domain model"""
        status_map = {
            "P": OrderStatus.PENDING,
            "R": OrderStatus.PROCESSING,
            "S": OrderStatus.SHIPPED,
            "D": OrderStatus.DELIVERED,
            "C": OrderStatus.CANCELLED
        }

        # Parse order date
        order_date = datetime.strptime(legacy_data['ORD_DT'], "%Y%m%d")

        # Convert items
        items = [
            OrderItem(
                product_id=item['SKU_ID'],
                quantity=item['ITM_QTY'],
                unit_price=Decimal(item['ITM_PRC'])
            )
            for item in legacy_data['ORD_ITM_LST']
        ]

        # Create address from flat structure
        address = Address(
            street=legacy_data['SHIP_ADDR_LN1'],
            city=legacy_data['SHIP_ADDR_CITY'],
            zip_code=legacy_data['SHIP_ADDR_ZIP']
        )

        return Order(
            id=legacy_data['ORD_ID'],
            customer_id=legacy_data['CUST_ID'],
            items=items,
            status=status_map.get(legacy_data['ORD_STATUS'], OrderStatus.PENDING),
            shipping_address=address,
            order_date=order_date
        )

    @staticmethod
    def to_legacy(order: Order) -> dict:
        """Convert clean domain model → legacy format"""
        status_map = {
            OrderStatus.PENDING: "P",
            OrderStatus.PROCESSING: "R",
            OrderStatus.SHIPPED: "S",
            OrderStatus.DELIVERED: "D",
            OrderStatus.CANCELLED: "C"
        }

        return {
            "ORD_ID": order.id,
            "CUST_ID": order.customer_id,
            "ORD_DT": order.order_date.strftime("%Y%m%d"),
            "ORD_ITM_LST": [
                {
                    "SKU_ID": item.product_id,
                    "ITM_QTY": item.quantity,
                    "ITM_PRC": str(item.unit_price)
                }
                for item in order.items
            ],
            "ORD_STATUS": status_map[order.status],
            "SHIP_ADDR_LN1": order.shipping_address.street,
            "SHIP_ADDR_CITY": order.shipping_address.city,
            "SHIP_ADDR_ZIP": order.shipping_address.zip_code
        }


# ============================================================================
# ANTI-CORRUPTION LAYER - Adapters
# ============================================================================

class LegacyCustomerAdapter:
    """Adapter that talks to legacy system and returns domain objects"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.translator = CustomerTranslator()

    def get_customer(self, customer_id: str) -> Customer:
        """Get customer - returns CLEAN domain object"""
        response = requests.get(f"{self.api_url}/customers/{customer_id}")
        legacy_data = response.json()
        # Translation happens in ACL - domain stays clean!
        return self.translator.to_domain(legacy_data)

    def create_customer(self, email: str, full_name: str, address: Address) -> Customer:
        """Create customer - accepts CLEAN domain objects"""
        # Business logic works with clean objects
        customer = Customer(
            id="",  # Will be assigned by legacy system
            email=email,
            full_name=full_name,
            address=address,
            status=CustomerStatus.ACTIVE,
            customer_type=CustomerType.REGULAR,
            created_at=datetime.now()
        )

        # ACL handles translation to legacy format
        legacy_data = self.translator.to_legacy(customer)
        response = requests.post(f"{self.api_url}/customers", json=legacy_data)

        # Return clean domain object
        return self.translator.to_domain(response.json())

    def update_customer_status(self, customer_id: str, status: CustomerStatus) -> Customer:
        """Update status - uses clean enum, not cryptic codes"""
        # Get current customer
        customer = self.get_customer(customer_id)
        customer.status = status

        # ACL translates to legacy format
        legacy_data = self.translator.to_legacy(customer)
        response = requests.put(
            f"{self.api_url}/customers/{customer_id}",
            json={"STATUS_CD": legacy_data['STATUS_CD']}
        )

        return self.translator.to_domain(response.json())


class LegacyOrderAdapter:
    """Adapter for order operations"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.translator = OrderTranslator()

    def create_order(self, customer: Customer, items: List[OrderItem]) -> Order:
        """Create order - accepts CLEAN domain objects"""
        order = Order(
            id="",  # Assigned by legacy system
            customer_id=customer.id,
            items=items,
            status=OrderStatus.PENDING,
            shipping_address=customer.address,  # Use customer's address
            order_date=datetime.now()
        )

        # ACL handles translation
        legacy_data = self.translator.to_legacy(order)
        response = requests.post(f"{self.api_url}/orders", json=legacy_data)

        return self.translator.to_domain(response.json())

    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get orders - returns CLEAN domain objects"""
        response = requests.get(f"{self.api_url}/orders?cust_id={customer_id}")
        legacy_orders = response.json()

        # ACL translates all orders
        return [self.translator.to_domain(order) for order in legacy_orders]


# ============================================================================
# APPLICATION SERVICES (Clean! No legacy pollution!)
# ============================================================================

class CustomerService:
    """Clean customer service - knows nothing about legacy format"""

    def __init__(self, customer_adapter: LegacyCustomerAdapter):
        self.adapter = customer_adapter

    def get_customer(self, customer_id: str) -> Customer:
        """Returns CLEAN domain object"""
        return self.adapter.get_customer(customer_id)

    def create_customer(self, email: str, full_name: str, address: Address) -> Customer:
        """Accepts CLEAN domain objects"""
        return self.adapter.create_customer(email, full_name, address)

    def deactivate_customer(self, customer_id: str) -> Customer:
        """Business logic with clean enums"""
        return self.adapter.update_customer_status(customer_id, CustomerStatus.INACTIVE)


class OrderService:
    """Clean order service - no legacy knowledge"""

    def __init__(self, order_adapter: LegacyOrderAdapter, customer_adapter: LegacyCustomerAdapter):
        self.order_adapter = order_adapter
        self.customer_adapter = customer_adapter

    def create_order(self, customer_id: str, items: List[OrderItem]) -> Order:
        """Clean business logic - no legacy format parsing!"""
        # Get customer as clean domain object
        customer = self.customer_adapter.get_customer(customer_id)

        # Business rules with clean objects
        if not customer.is_active():
            raise ValueError(f"Customer {customer.full_name} is not active")

        # Check account age
        account_age = (datetime.now() - customer.created_at).days
        if account_age < 1:
            print(f"   ⚠️  New customer (account age: {account_age} days)")

        # Create order with clean objects
        return self.order_adapter.create_order(customer, items)

    def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Returns clean domain objects"""
        return self.order_adapter.get_customer_orders(customer_id)


class ReportService:
    """Clean report service - works with domain objects"""

    def __init__(self, customer_service: CustomerService, order_service: OrderService):
        self.customer_service = customer_service
        self.order_service = order_service

    def generate_customer_report(self, customer_id: str) -> str:
        """Generate report with CLEAN domain objects - no parsing!"""
        # Get clean domain objects
        customer = self.customer_service.get_customer(customer_id)
        orders = self.order_service.get_customer_orders(customer_id)

        # Work with clean enums and objects - no translation needed!
        order_summaries = [
            f"  - {order.order_date.strftime('%m/%d/%Y')}: "
            f"{order.status.value.title()} (${order.total_amount:.2f})"
            for order in orders
        ]

        report = f"""
Customer Report
===============
Name: {customer.full_name}
Email: {customer.email}
Address: {customer.address}
Status: {customer.status.value.title()}
Type: {customer.customer_type.value.title()}
Member Since: {customer.created_at.strftime('%B %d, %Y')}

Orders ({len(orders)}):
{chr(10).join(order_summaries) if order_summaries else '  No orders'}

Total Revenue: ${sum(order.total_amount for order in orders):.2f}
        """

        return report.strip()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Demonstrate Anti-Corruption Layer benefits"""

    print("=" * 70)
    print(" " * 17 + "WITH ANTI-CORRUPTION LAYER")
    print("=" * 70)
    print("\n✅ Benefits:")
    print("1. Clean domain model (no legacy pollution)")
    print("2. Enums instead of cryptic codes")
    print("3. Proper types (datetime, Decimal, not strings)")
    print("4. Nested objects (Address) not flat structures")
    print("5. Business logic separate from legacy integration")
    print("6. Easy to test (mock adapters)")
    print("7. Can replace legacy system by updating ACL only")
    print("\n")

    # Initialize ACL adapters
    api_url = "http://localhost:8081"
    customer_adapter = LegacyCustomerAdapter(api_url)
    order_adapter = LegacyOrderAdapter(api_url)

    # Initialize clean services
    customer_service = CustomerService(customer_adapter)
    order_service = OrderService(order_adapter, customer_adapter)
    report_service = ReportService(customer_service, order_service)

    try:
        # Create customer with clean API
        print("1. Creating customer (clean domain model)...")
        address = Address(
            street="123 Main St",
            city="New York",
            zip_code="10001"
        )
        customer = customer_service.create_customer(
            email="john.doe@example.com",
            full_name="John Doe",
            address=address
        )
        print(f"   ✅ Created: {customer.full_name}")
        print(f"   Status: {customer.status.value} (clean enum!)")
        print(f"   Address: {customer.address} (nested object!)")

        # Create order with clean objects
        print("\n2. Creating order (clean business logic)...")
        items = [
            OrderItem(product_id="PROD-001", quantity=2, unit_price=Decimal("29.99")),
            OrderItem(product_id="PROD-002", quantity=1, unit_price=Decimal("49.99"))
        ]
        order = order_service.create_order(customer.id, items)
        print(f"   ✅ Created order: {order.id}")
        print(f"   Status: {order.status.value} (clean enum!)")
        print(f"   Total: ${order.total_amount:.2f} (calculated property!)")

        # Generate report with clean objects
        print("\n3. Generating report (clean domain objects)...")
        report = report_service.generate_customer_report(customer.id)
        print(report)

        print("\n" + "=" * 70)
        print("Benefits demonstrated:")
        print("=" * 70)
        print("✅ Services work with clean Customer/Order objects")
        print("✅ No status code translation in business logic")
        print("✅ No date parsing scattered everywhere")
        print("✅ Business rules use is_active() not 'STATUS_CD == A'")
        print("✅ Reports work with enums, not cryptic codes")
        print("✅ ACL isolates all legacy system knowledge")
        print("✅ Easy to test (mock adapters, not legacy system)")
        print("✅ Can replace legacy system behind ACL")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("(Make sure legacy system is running: python demo/mock_legacy_system.py)")


if __name__ == "__main__":
    main()
