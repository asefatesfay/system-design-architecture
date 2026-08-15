"""
Python Implementation: BankAccount Class
========================================
Features:
- Class-based OOP
- __init__ constructor
- Instance variables with self
- Private variables by convention (_balance)
- String formatting with f-strings
"""


class BankAccount:
    """Represents a bank account with basic operations"""

    def __init__(self, account_number, initial_balance=0):
        """
        Initialize a new bank account

        Args:
            account_number: Unique account identifier
            initial_balance: Starting balance (default: 0)
        """
        self.account_number = account_number
        self._balance = initial_balance  # _ prefix = private by convention
        print(f"Created account: {account_number}")

    def deposit(self, amount):
        """
        Deposit money into account

        Args:
            amount: Amount to deposit

        Returns:
            bool: True if successful, False otherwise
        """
        if amount <= 0:
            print("Error: Deposit amount must be positive")
            return False

        self._balance += amount
        print(f"Deposited ${amount:.2f}")
        return True

    def withdraw(self, amount):
        """
        Withdraw money from account

        Args:
            amount: Amount to withdraw

        Returns:
            bool: True if successful, False if insufficient funds
        """
        if amount <= 0:
            print("Error: Withdrawal amount must be positive")
            return False

        if amount > self._balance:
            print(f"Error: Insufficient funds. Balance: ${self._balance:.2f}")
            return False

        self._balance -= amount
        print(f"Withdrew ${amount:.2f}")
        return True

    def get_balance(self):
        """
        Get current account balance

        Returns:
            float: Current balance
        """
        return self._balance

    def __str__(self):
        """String representation for printing"""
        return f"Account {self.account_number}: ${self._balance:.2f}"

    def __repr__(self):
        """Developer-friendly representation"""
        return f"BankAccount('{self.account_number}', {self._balance})"


def main():
    """Demo the BankAccount class"""
    print("=" * 60)
    print("Python: Bank Account Example")
    print("=" * 60)

    # Create account
    account = BankAccount("ACC001", 1000)
    print(f"Initial balance: ${account.get_balance():.2f}\n")

    # Deposit
    account.deposit(500)
    print(f"After deposit of $500: ${account.get_balance():.2f}\n")

    # Withdraw
    account.withdraw(200)
    print(f"After withdrawal of $200: ${account.get_balance():.2f}\n")

    # Failed withdrawal
    account.withdraw(2000)
    print(f"Final balance: ${account.get_balance():.2f}\n")

    # String representation
    print("Using __str__:", account)
    print("Using __repr__:", repr(account))


if __name__ == "__main__":
    main()
