# Bad Example

class DiscountCalculator:
    def calculate_discount(self, customer_type, amount):
        if customer_type == "regular":
            return amount * 0.05
        elif customer_type == "premium":
            return amount * 0.10
        elif customer_type == "vip":
            return amount * 0.20
        # Problem: Adding a new customer type requires modifying this method!
        elif customer_type == "corporate":
            return amount * 0.15
        else:
            return 0.0

# Good design using Open/Closed Principle

from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, amount):
        pass

class RegularCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.05
class PremiumCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.10

class VIPCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.20

class CorporateCustomerDiscount(DiscountStrategy):
    def calculate_discount(self, amount):
        return amount * 0.15

class DiscountCalculator:
    def __init__(self, strategy):
        self.strategy = strategy
    def calculate(self, amount):
        return self.strategy.calculate_discount(amount)

if __name__ == "__main__":
    # Example usage
    amount = 1000.0

    regular_discount = DiscountCalculator(RegularCustomerDiscount())
    print(f"Regular Customer Discount: {regular_discount.calculate(amount)}")

    premium_discount = DiscountCalculator(PremiumCustomerDiscount())
    print(f"Premium Customer Discount: {premium_discount.calculate(amount)}")

    vip_discount = DiscountCalculator(VIPCustomerDiscount())
    print(f"VIP Customer Discount: {vip_discount.calculate(amount)}")

    corporate_discount = DiscountCalculator(CorporateCustomerDiscount())
    print(f"Corporate Customer Discount: {corporate_discount.calculate(amount)}")