# Bad example with multiple responsibilities
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    # Responsibility 1: Validate user data
    def validate_email(self):
        return "@" in self.email and "." in self.email
    
    # Responsibility 2: Save to database
    def save_to_database(self):
        print(f"Saving {self.name} to database")
    
    # Responsibility 3: Send email
    def send_email(self):
        print(f"Sending email to {self.email}")
    
    # Responsibility 4: Generate report
    def generate_report(self):
        print(f"Generating report for {self.name}")
    
    # Problem: User class has 4 reasons to change
    # - Email format changes
    # - Database structure changes
    # - Email service changes
    # - Report format changes

# Good example with single reponsibility

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserValidator:
    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email
    
    @staticmethod
    def validate_name(name):
        return len(name) > 0

class UserRepository:
    def save(self, user):
        print(f"Saving {user.name} to database")
    def find_by_email(self, email):
        # Database query logic here
        print(f"Finding user by email: {email}")

class EmailService:
    def send_email(self, user):
        print(f"Sending email to {user.email}")

class ReportGenerator:
    def generate_report(self, user):
        print(f"Generating report for {user.name}")

#Bad OrderProcessor does everything

from datetime import datetime
class BadOrderProcessor:
    def process_order(self, order):
        # Validate order
        if not order.items:
            return False
        
        # Calculate total
        total = sum(item.price * item.quantity for item in order.items)
        
        # Process payment
        print(f"Processing payment of {total} for order {order.id}")
        
        # Update inventory
        for item in order.items:
            print(f"Reducing inventory for {item.name} by {item.quantity}")
        
        # Send confirmation email
        print(f"Sending confirmation email for order {order.id}")
        
        # Log to database
        print(f"Logging order {order.id} to database")
        
        return True

# Good: Separate responsibilities
class Order:
    def __init__(self, order_id, customer, items):
        self.id = order_id
        self.customer = customer
        self.items = items
class Item:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class OrderValidator:
    def validate(self, order):
        if not order.items:
            raise ValueError("Order must have at least one item")
        return True
class PriceCalculator:
    def calculate_total(self, order):
        return sum(item.price * item.quantity for item in order.items)

class PaymentProcessor:
    def process(self, amount):
        print(f"Processing payment of {amount}")

class InventoryService:
    def update_inventory(self, order):
        for item in order.items:
            print(f"Reducing inventory for {item.name} by {item.quantity}")

class NotificationService:
    def send_confirmation_email(self, order):
        print(f"Sending confirmation email for order {order.id}")

class OrderLogger:
    def log(self, order):
        print(f"Logging order {order.id} to database")

# Usage - coordinated by service

class OrderService:
    def __init__(self):
        self.validator = OrderValidator()
        self.calculator = PriceCalculator()
        self.payment_processor = PaymentProcessor()
        self.inventory_service = InventoryService()
        self.notification_service = NotificationService()
        self.logger = OrderLogger()

    def process_order(self, order):
        # Validate order
        self.validator.validate(order)
        
        # Calculate total
        total = self.calculator.calculate_total(order)
        
        # Process payment
        self.payment_processor.process(total)
        
        # Update inventory
        self.inventory_service.update_inventory(order)
        
        # Send confirmation email
        self.notification_service.send_confirmation_email(order)
        
        # Log to database
        self.logger.log(order)

if __name__ == "__main__":
    # Example usage
    items = [Item("Widget", 10.0, 2), Item("Gadget", 15.0, 1)]
    customer = Customer(name="John Doe", email="john.doe@example.com")
    order = Order(order_id=123, customer=customer, items=items)
    
    order_service = OrderService()
    order_service.process_order(order)