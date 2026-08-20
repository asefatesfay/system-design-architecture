"""
Without Anti-Corruption Layer Pattern
Problem: Legacy system's data model pollutes the entire application
"""

import requests
from datetime import datetime
from typing import Dict, List, Any


class CustomerService:
    """
    Customer service POLLUTED by legacy system format
    Notice how the ugly legacy format spreads throughout the code
    """

    def __init__(self, legacy_api_url: str):
        self.api_url = legacy_api_url

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Returns customer in LEGACY FORMAT - pollutes entire app"""
        response = requests.get(f"{self.api_url}/customers/{customer_id}")
        # Returning raw legacy format - BAD!
        return response.json()

    def create_customer(self, first_name: str, last_name: str, email: str,
                       street: str, city: str, zip_code: str) -> Dict[str, Any]:
        """Forced to use legacy format"""
        # Business logic has to know legacy format - BAD!
        legacy_customer = {
            "F_NAME": first_name,  # Ugly field names
            "L_NAME": last_name,
            "EMAIL_ADDR": email,
            "ADDR_LN1": street,  # Flat structure
            "ADDR_CITY": city,
            "ADDR_ZIP": zip_code,
            "STATUS_CD": "A",  # Cryptic code
            "CREATE_DT": datetime.now().strftime("%Y%m%d%H%M%S"),  # Weird format
            "CUST_TYP": "R"  # What does "R" mean? Regular? Retail?
        }

        response = requests.post(f"{self.api_url}/customers", json=legacy_customer)
        return response.json()

    def update_customer_status(self, customer_id: str, is_active: bool) -> Dict[str, Any]:
        """Status code logic leaks everywhere"""
        # Business logic knows about status codes - BAD!
        status_code = "A" if is_active else "I"

        response = requests.put(
            f"{self.api_url}/customers/{customer_id}",
            json={"STATUS_CD": status_code}
        )
        return response.json()


class OrderService:
    """
    Order service also POLLUTED by legacy format
    Has to understand legacy customer format
    """

    def __init__(self, customer_service: CustomerService, legacy_api_url: str):
        self.customer_service = customer_service
        self.api_url = legacy_api_url

    def create_order(self, customer_id: str, items: List[Dict]) -> Dict[str, Any]:
        """
        Order creation polluted by legacy customer format
        """
        # Get customer in legacy format
        customer = self.customer_service.get_customer(customer_id)

        # Business logic has to deal with ugly legacy format - BAD!
        customer_name = f"{customer['F_NAME']} {customer['L_NAME']}"
        customer_address = f"{customer['ADDR_LN1']}, {customer['ADDR_CITY']}"

        # Check status using cryptic code - BAD!
        if customer['STATUS_CD'] != 'A':
            raise ValueError(f"Customer is not active (status: {customer['STATUS_CD']})")

        # Parse weird date format - BAD!
        try:
            created_date = datetime.strptime(customer['CREATE_DT'], "%Y%m%d%H%M%S")
            account_age_days = (datetime.now() - created_date).days
        except ValueError:
            account_age_days = 0

        # Create order in legacy format - MORE POLLUTION!
        legacy_order = {
            "CUST_ID": customer_id,
            "ORD_DT": datetime.now().strftime("%Y%m%d"),  # Different date format!
            "ORD_ITM_LST": [
                {
                    "SKU_ID": item['product_id'],
                    "ITM_QTY": item['quantity'],
                    "ITM_PRC": str(item['price'])  # Price as string!
                }
                for item in items
            ],
            "ORD_STATUS": "P",  # What's "P"? Pending? Processing?
            "SHIP_ADDR_LN1": customer['ADDR_LN1'],  # Duplicating address
            "SHIP_ADDR_CITY": customer['ADDR_CITY'],
            "SHIP_ADDR_ZIP": customer['ADDR_ZIP']
        }

        response = requests.post(f"{self.api_url}/orders", json=legacy_order)
        return response.json()

    def get_customer_orders(self, customer_id: str) -> List[Dict[str, Any]]:
        """Returns orders in legacy format - pollutes calling code"""
        response = requests.get(f"{self.api_url}/orders?cust_id={customer_id}")
        # Returning raw legacy format - BAD!
        return response.json()


class ReportService:
    """
    Report service ALSO polluted by legacy format
    Every service has to understand the legacy system!
    """

    def __init__(self, customer_service: CustomerService, order_service: OrderService):
        self.customer_service = customer_service
        self.order_service = order_service

    def generate_customer_report(self, customer_id: str) -> str:
        """Generate report - forced to deal with legacy format"""
        # Get customer in ugly legacy format
        customer = self.customer_service.get_customer(customer_id)

        # Every report has to parse legacy format - CODE DUPLICATION!
        full_name = f"{customer['F_NAME']} {customer['L_NAME']}"
        address = f"{customer['ADDR_LN1']}, {customer['ADDR_CITY']}, {customer['ADDR_ZIP']}"

        # Decode status code - DUPLICATED LOGIC!
        status_map = {"A": "Active", "I": "Inactive", "S": "Suspended"}
        status = status_map.get(customer['STATUS_CD'], "Unknown")

        # Parse weird date - DUPLICATED LOGIC!
        try:
            created_dt = datetime.strptime(customer['CREATE_DT'], "%Y%m%d%H%M%S")
            member_since = created_dt.strftime("%B %d, %Y")
        except ValueError:
            member_since = "Unknown"

        # Get orders in legacy format
        orders = self.order_service.get_customer_orders(customer_id)

        # Parse order dates - MORE DUPLICATION!
        order_summaries = []
        for order in orders:
            try:
                order_date = datetime.strptime(order['ORD_DT'], "%Y%m%d")
                date_str = order_date.strftime("%m/%d/%Y")
            except ValueError:
                date_str = order['ORD_DT']

            # Decode order status - MORE DUPLICATION!
            status_map = {"P": "Pending", "S": "Shipped", "D": "Delivered", "C": "Cancelled"}
            order_status = status_map.get(order['ORD_STATUS'], "Unknown")

            order_summaries.append(f"  - {date_str}: {order_status}")

        # Generate report
        report = f"""
Customer Report
===============
Name: {full_name}
Email: {customer['EMAIL_ADDR']}
Address: {address}
Status: {status}
Member Since: {member_since}
Customer Type: {customer.get('CUST_TYP', 'Unknown')}

Orders ({len(orders)}):
{chr(10).join(order_summaries) if order_summaries else '  No orders'}
        """

        return report.strip()


def main():
    """Demonstrate problems without Anti-Corruption Layer"""

    print("=" * 70)
    print(" " * 15 + "WITHOUT ANTI-CORRUPTION LAYER")
    print("=" * 70)
    print("\n❌ Problems:")
    print("1. Legacy data format pollutes entire application")
    print("2. Cryptic codes (A, I, P, R) spread everywhere")
    print("3. Weird date formats duplicated in every service")
    print("4. Status/code translation logic duplicated")
    print("5. Every service must understand legacy system")
    print("6. Hard to test (business logic mixed with legacy format)")
    print("7. Can't replace legacy without rewriting everything")
    print("\n")

    # Initialize services
    api_url = "http://localhost:8081"
    customer_service = CustomerService(api_url)
    order_service = OrderService(customer_service, api_url)
    report_service = ReportService(customer_service, order_service)

    try:
        # Create customer - notice ugly parameter names
        print("1. Creating customer...")
        print("   (Service forced to use first_name, last_name, street, city separately)")
        customer = customer_service.create_customer(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            street="123 Main St",
            city="New York",
            zip_code="10001"
        )
        customer_id = customer['CUST_ID']
        print(f"   ✅ Created customer: {customer_id}")
        print(f"   Raw legacy format leaked to application:")
        print(f"   F_NAME: {customer['F_NAME']}, STATUS_CD: {customer['STATUS_CD']}")

        # Create order - business logic polluted
        print("\n2. Creating order...")
        print("   (Business logic has to deal with legacy customer format)")
        order = order_service.create_order(
            customer_id=customer_id,
            items=[
                {"product_id": "PROD-001", "quantity": 2, "price": 29.99},
                {"product_id": "PROD-002", "quantity": 1, "price": 49.99}
            ]
        )
        print(f"   ✅ Created order: {order['ORD_ID']}")
        print(f"   Raw legacy format: ORD_STATUS={order['ORD_STATUS']}")

        # Generate report - everything knows about legacy
        print("\n3. Generating customer report...")
        print("   (Every service must parse legacy format)")
        report = report_service.generate_customer_report(customer_id)
        print(report)

        print("\n" + "=" * 70)
        print("Issues demonstrated:")
        print("=" * 70)
        print("❌ CustomerService returns raw legacy format (F_NAME, STATUS_CD)")
        print("❌ OrderService has to parse legacy customer data")
        print("❌ ReportService duplicates date/status parsing logic")
        print("❌ Business rules mixed with legacy format knowledge")
        print("❌ Every developer must learn legacy system quirks")
        print("❌ Can't replace legacy without big bang rewrite")
        print("❌ Testing requires understanding legacy format")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("(Make sure legacy system is running: python demo/mock_legacy_system.py)")


if __name__ == "__main__":
    main()
