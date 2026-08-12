"""
Complete ATM Machine Example - Demonstrating Abstraction
=========================================================

This shows the FULL implementation including all supporting classes
that were referenced in the ATM example.
"""

from datetime import datetime
from typing import Optional, Dict, List

# ============= SUPPORTING CLASSES (Implementation Details) =============

class BankAccount:
    """Represents a bank account"""
    def __init__(self, account_number: str, card_number: str, balance: float):
        self.account_number = account_number
        self.card_number = card_number
        self._balance = balance
        self._daily_limit = 1000.0
        self._daily_withdrawn = 0.0
        self._transaction_history = []

    def get_balance(self) -> float:
        return self._balance

    def debit(self, amount: float):
        """Remove money from account"""
        self._balance -= amount
        self._daily_withdrawn += amount
        self._transaction_history.append({
            'type': 'debit',
            'amount': amount,
            'timestamp': datetime.now(),
            'balance_after': self._balance
        })

    def can_withdraw_today(self, amount: float) -> bool:
        """Check if within daily limit"""
        return (self._daily_withdrawn + amount) <= self._daily_limit

    def reset_daily_limit(self):
        """Reset at midnight"""
        self._daily_withdrawn = 0.0

class BankSystem:
    """
    Simulates connection to bank's central system
    In reality, this would connect to actual bank servers
    """
    def __init__(self):
        # Simulate database of accounts
        self._accounts: Dict[str, BankAccount] = {}
        self._card_to_account: Dict[str, str] = {}

        # Add some test accounts
        self._initialize_test_data()

    def _initialize_test_data(self):
        """Create some test accounts"""
        # Alice's account
        alice_account = BankAccount("ACC-001", "1234567890123456", 5000.00)
        self._accounts["ACC-001"] = alice_account
        self._card_to_account["1234567890123456"] = "ACC-001"

        # Bob's account
        bob_account = BankAccount("ACC-002", "9876543210987654", 1200.00)
        self._accounts["ACC-002"] = bob_account
        self._card_to_account["9876543210987654"] = "ACC-002"

    def get_account(self, card_number: str) -> Optional[BankAccount]:
        """
        Complex logic to connect to bank's mainframe
        In reality: secure connection, encryption, authentication
        """
        print("   [Bank System] Connecting to mainframe...")
        print("   [Bank System] Authenticating request...")

        account_number = self._card_to_account.get(card_number)
        if account_number:
            print("   [Bank System] Account found")
            return self._accounts[account_number]
        else:
            print("   [Bank System] Account not found")
            return None

    def log_transaction(self, card_number: str, amount: float):
        """Log transaction in central system"""
        print(f"   [Bank System] Logging transaction: ${amount} for card {card_number[-4:]}")
        # In reality: write to database, audit logs, compliance tracking

class PINValidator:
    """
    Handles PIN verification
    In reality: encrypted, multiple security layers
    """
    def __init__(self):
        # Simulated PIN database (in reality: encrypted and hashed)
        self._pins = {
            "1234567890123456": "1234",  # Alice's PIN
            "9876543210987654": "5678",  # Bob's PIN
        }
        self._failed_attempts = {}

    def verify(self, card_number: str, entered_pin: str) -> bool:
        """
        Verify PIN with security checks
        """
        print("   [PIN Validator] Verifying PIN...")

        # Check if card is locked due to too many attempts
        if self._failed_attempts.get(card_number, 0) >= 3:
            print("   [PIN Validator] Card locked due to too many failed attempts")
            return False

        # Verify PIN
        correct_pin = self._pins.get(card_number)
        if not correct_pin:
            print("   [PIN Validator] Card not found")
            return False

        if entered_pin == correct_pin:
            print("   [PIN Validator] ✓ PIN verified")
            self._failed_attempts[card_number] = 0  # Reset on success
            return True
        else:
            # Track failed attempt
            self._failed_attempts[card_number] = self._failed_attempts.get(card_number, 0) + 1
            attempts_left = 3 - self._failed_attempts[card_number]
            print(f"   [PIN Validator] ✗ Invalid PIN. {attempts_left} attempts remaining")
            return False

class CardReader:
    """
    Reads card data from magnetic stripe or chip
    """
    def read_card(self, card_number: str) -> Dict:
        """
        Simulate reading card
        In reality: reads magnetic stripe or chip data
        """
        print("   [Card Reader] Reading card...")
        print("   [Card Reader] Processing chip data...")

        return {
            'card_number': card_number,
            'card_type': 'debit',
            'bank_code': card_number[:6],
            'read_successful': True
        }

class CashDispenser:
    """
    Physical cash dispensing mechanism
    """
    def __init__(self):
        # Simulated cash cassettes
        self._bills = {
            100: 50,  # 50 x $100 bills
            50: 100,  # 100 x $50 bills
            20: 200,  # 200 x $20 bills
            10: 300,  # 300 x $10 bills
        }

    def count_bills(self, amount: float) -> Optional[Dict[int, int]]:
        """
        Calculate optimal bill combination
        """
        print(f"   [Cash Dispenser] Calculating bills for ${amount}")

        # Must be multiple of 10
        if amount % 10 != 0:
            print("   [Cash Dispenser] Amount must be multiple of $10")
            return None

        # Greedy algorithm: use largest bills first
        bills_needed = {}
        remaining = int(amount)

        for bill_value in sorted(self._bills.keys(), reverse=True):
            if remaining == 0:
                break

            available = self._bills[bill_value]
            needed = remaining // bill_value

            use = min(needed, available)

            if use > 0:
                bills_needed[bill_value] = use
                remaining -= use * bill_value

        if remaining > 0:
            print("   [Cash Dispenser] ✗ Cannot dispense exact amount")
            return None

        print(f"   [Cash Dispenser] ✓ Bills prepared: {bills_needed}")
        return bills_needed

    def dispense(self, bills: Dict[int, int]):
        """
        Physically dispense the bills
        """
        print("   [Cash Dispenser] Dispensing cash...")

        for bill_value, count in bills.items():
            self._bills[bill_value] -= count
            print(f"   [Cash Dispenser] → {count} x ${bill_value} bills")

        print("   [Cash Dispenser] ✓ Cash dispensed")

    def get_cash_status(self) -> Dict[int, int]:
        """Check remaining cash"""
        return self._bills.copy()

class ReceiptPrinter:
    """
    Prints transaction receipts
    """
    def print_receipt(self, amount: float, balance: float, card_last4: str):
        """
        Print formatted receipt
        """
        print("   [Receipt Printer] Printing receipt...")
        print()
        print("   ┌─────────────────────────────────┐")
        print("   │     MEGA BANK ATM RECEIPT       │")
        print("   ├─────────────────────────────────┤")
        print(f"   │ Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  │")
        print(f"   │ Card: ************{card_last4}     │")
        print("   ├─────────────────────────────────┤")
        print(f"   │ Withdrawal:         ${amount:>7.2f}  │")
        print(f"   │ Balance:            ${balance:>7.2f}  │")
        print("   ├─────────────────────────────────┤")
        print("   │   Thank you for banking with us!│")
        print("   └─────────────────────────────────┘")
        print()

# ============= ATM MACHINE (Simple User Interface) =============

class ATM:
    """
    User perspective: Simple interface
    Insert card → Enter PIN → Get cash

    Hidden complexity: All the classes above!
    """

    def __init__(self, atm_id: str, location: str):
        self.atm_id = atm_id
        self.location = location

        # Complex subsystems (user doesn't see these!)
        self.__bank_system = BankSystem()
        self.__cash_dispenser = CashDispenser()
        self.__card_reader = CardReader()
        self.__pin_validator = PINValidator()
        self.__receipt_printer = ReceiptPrinter()

    def withdraw_cash(self, card_number: str, pin: str, amount: float) -> bool:
        """
        USER PERSPECTIVE: Simple operation

        HIDDEN COMPLEXITY:
        1. Read card
        2. Connect to bank
        3. Validate PIN
        4. Check balance
        5. Verify daily limit
        6. Count bills
        7. Dispense cash
        8. Update account
        9. Print receipt
        10. Log everything
        """

        print(f"\n💳 ATM #{self.atm_id} - {self.location}")
        print(f"💰 Processing withdrawal of ${amount:.2f}")
        print("="*50)

        # Step 1: Read card
        card_data = self.__card_reader.read_card(card_number)
        if not card_data['read_successful']:
            print("\n❌ Card read error")
            return False

        # Step 2: Validate PIN
        if not self.__pin_validator.verify(card_number, pin):
            print("\n❌ Invalid PIN")
            return False

        # Step 3: Connect to bank and get account
        account = self.__bank_system.get_account(card_number)
        if not account:
            print("\n❌ Account not found")
            return False

        # Step 4: Check balance
        if account.get_balance() < amount:
            print(f"\n❌ Insufficient funds")
            print(f"   Available: ${account.get_balance():.2f}")
            return False

        # Step 5: Check daily limit
        if not account.can_withdraw_today(amount):
            print("\n❌ Exceeds daily withdrawal limit")
            return False

        # Step 6: Count bills
        bills = self.__cash_dispenser.count_bills(amount)
        if bills is None:
            print("\n❌ Cannot dispense requested amount")
            print("   Please try a different amount")
            return False

        # Step 7: Dispense cash
        self.__cash_dispenser.dispense(bills)

        # Step 8: Update account
        account.debit(amount)
        self.__bank_system.log_transaction(card_number, amount)

        # Step 9: Print receipt
        self.__receipt_printer.print_receipt(
            amount,
            account.get_balance(),
            card_number[-4:]
        )

        print("="*50)
        print(f"✅ Please take your ${amount:.2f}")
        print("✅ Don't forget your card!\n")
        return True

    def check_balance(self, card_number: str, pin: str) -> Optional[float]:
        """Another simple operation with hidden complexity"""
        print(f"\n💳 ATM #{self.atm_id} - Balance Inquiry")
        print("="*50)

        # Read card
        card_data = self.__card_reader.read_card(card_number)
        if not card_data['read_successful']:
            print("\n❌ Card read error")
            return None

        # Verify PIN
        if not self.__pin_validator.verify(card_number, pin):
            print("\n❌ Invalid PIN")
            return None

        # Get account
        account = self.__bank_system.get_account(card_number)
        if not account:
            print("\n❌ Account not found")
            return None

        balance = account.get_balance()
        print(f"\n✅ Current Balance: ${balance:.2f}")
        print("="*50 + "\n")
        return balance

    def get_atm_status(self):
        """Admin function to check ATM status"""
        print(f"\n🏧 ATM Status - {self.atm_id}")
        print("="*50)
        cash_status = self.__cash_dispenser.get_cash_status()
        total_cash = sum(value * count for value, count in cash_status.items())

        print("Cash Available:")
        for bill, count in sorted(cash_status.items(), reverse=True):
            print(f"  ${bill:>3} bills: {count:>3} (${bill * count:>6})")
        print(f"\nTotal: ${total_cash}")
        print("="*50 + "\n")

# ============= DEMO: User Experience vs Hidden Complexity =============

def main():
    print("🏦 ATM MACHINE DEMONSTRATION")
    print("Showing: Simple interface vs Complex implementation\n")

    # Create ATM
    atm = ATM("ATM-001", "Downtown Branch")

    # Show ATM status (admin view)
    atm.get_atm_status()

    # Scenario 1: Successful withdrawal (Alice)
    print("SCENARIO 1: Alice withdraws $200")
    print("-" * 70)
    atm.withdraw_cash(
        card_number="1234567890123456",
        pin="1234",
        amount=200.00
    )

    # Scenario 2: Check balance
    print("\nSCENARIO 2: Alice checks balance")
    print("-" * 70)
    atm.check_balance(
        card_number="1234567890123456",
        pin="1234"
    )

    # Scenario 3: Invalid PIN (Bob enters wrong PIN)
    print("\nSCENARIO 3: Bob enters wrong PIN")
    print("-" * 70)
    atm.withdraw_cash(
        card_number="9876543210987654",
        pin="0000",  # Wrong PIN!
        amount=100.00
    )

    # Scenario 4: Successful withdrawal with correct PIN
    print("\nSCENARIO 4: Bob enters correct PIN")
    print("-" * 70)
    atm.withdraw_cash(
        card_number="9876543210987654",
        pin="5678",  # Correct PIN
        amount=100.00
    )

    # Scenario 5: Insufficient funds
    print("\nSCENARIO 5: Bob tries to withdraw more than balance")
    print("-" * 70)
    atm.withdraw_cash(
        card_number="9876543210987654",
        pin="5678",
        amount=5000.00  # More than his balance
    )

    # Show final ATM status
    print("\nFINAL ATM STATUS:")
    atm.get_atm_status()

    print("\n" + "="*70)
    print("KEY TAKEAWAY:")
    print("="*70)
    print("User sees: Simple withdraw_cash() method")
    print("Behind the scenes: 10+ complex operations!")
    print()
    print("This is ABSTRACTION:")
    print("  ✓ Hide complexity")
    print("  ✓ Simple interface")
    print("  ✓ User-friendly")
    print("  ✓ Maintainable code")
    print("="*70)

if __name__ == "__main__":
    main()
