"""
Interactive demo comparing code without and with Anti-Corruption Layer

Requirements:
1. Start mock legacy system: python demo/mock_legacy_system.py
2. Run this demo: python demo/run_demo.py
"""

import sys
import os
import time
import requests

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'without_pattern'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'with_pattern'))


def check_legacy_system():
    """Check if mock legacy system is running"""
    try:
        response = requests.get("http://localhost:8081/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def reset_legacy_system():
    """Reset legacy system data"""
    try:
        requests.post("http://localhost:8081/reset", timeout=2)
    except:
        pass


def run_without_acl():
    """Run demo without Anti-Corruption Layer"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "WITHOUT ANTI-CORRUPTION LAYER" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Import here to avoid conflicts
    import main as without_main

    # Reset data
    reset_legacy_system()

    # Capture the execution
    print("Running example...")
    print("-" * 70)

    try:
        without_main.main()
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)
    print("Code Analysis - WITHOUT ACL:")
    print("=" * 70)
    print("""
Key Issues Observed:

1. LEGACY FORMAT POLLUTION:
   customer = customer_service.get_customer(id)
   name = f"{customer['F_NAME']} {customer['L_NAME']}"  # ❌ Ugly!
   status = customer['STATUS_CD']  # ❌ Cryptic code!

2. DUPLICATED TRANSLATION LOGIC:
   Every service parses dates:
   - CustomerService: datetime.strptime(data['CREATE_DT'], "%Y%m%d%H%M%S")
   - OrderService: datetime.strptime(data['ORD_DT'], "%Y%m%d")
   - ReportService: (same parsing repeated again!)

3. STATUS CODE LOGIC SCATTERED:
   status_map = {"A": "Active", "I": "Inactive"}  # Repeated everywhere!

4. BUSINESS LOGIC MIXED WITH LEGACY:
   if customer['STATUS_CD'] != 'A':  # Business logic knows about "A"!
       raise ValueError("Customer not active")

5. HARD TO TEST:
   - Need to understand legacy format to write tests
   - Can't mock cleanly (everything knows legacy structure)
   - Business logic tightly coupled to legacy system
    """)


def run_with_acl():
    """Run demo with Anti-Corruption Layer"""
    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 17 + "WITH ANTI-CORRUPTION LAYER" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Import here to avoid conflicts
    import main as with_main

    # Reset data
    reset_legacy_system()

    # Capture the execution
    print("Running example...")
    print("-" * 70)

    try:
        with_main.main()
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)
    print("Code Analysis - WITH ACL:")
    print("=" * 70)
    print("""
Improvements Demonstrated:

1. CLEAN DOMAIN MODEL:
   customer: Customer = customer_service.get_customer(id)
   name = customer.full_name  # ✅ Clean!
   status = customer.status   # ✅ Enum, not code!

2. NO DUPLICATED LOGIC:
   All translation happens in ACL Translators:
   - CustomerTranslator.to_domain() - one place
   - OrderTranslator.to_domain() - one place
   Services never parse dates or codes!

3. CLEAN ENUMS:
   if customer.status == CustomerStatus.ACTIVE:  # ✅ Readable!
       # or even simpler:
       if customer.is_active():  # ✅ Business method!

4. SEPARATED CONCERNS:
   Business Logic:  Works with Customer, Order objects
   ACL Layer:       Translates between legacy and domain
   Legacy System:   Knows nothing about domain

5. EASY TO TEST:
   - Mock adapters, not legacy system
   - Business logic tests use clean objects
   - ACL tests verify translation only

6. EASY TO MIGRATE:
   - Replace legacy system → update ACL only
   - Domain model unchanged
   - Business logic unchanged
   - Gradual migration possible
    """)


def run_comparison():
    """Run side-by-side comparison"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "ANTI-CORRUPTION LAYER - COMPARISON DEMO" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")

    # Check legacy system
    print("\n🔍 Checking mock legacy system...")
    if not check_legacy_system():
        print("❌ ERROR: Mock legacy system not running!")
        print("\nPlease start it first:")
        print("   python demo/mock_legacy_system.py")
        print("\nThen run this demo again.")
        return

    print("✅ Mock legacy system is running")
    print("   (Simulating old system with cryptic codes and weird formats)")

    # Run both demos
    run_without_acl()
    time.sleep(1)
    run_with_acl()

    # Final comparison
    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 25 + "FINAL COMPARISON" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    print("┌──────────────────────────────┬──────────────┬──────────────┐")
    print("│ Aspect                       │ Without ACL  │ With ACL     │")
    print("├──────────────────────────────┼──────────────┼──────────────┤")
    print("│ Domain Model Purity          │ ❌ Polluted  │ ✅ Clean     │")
    print("│ Code Duplication             │ ❌ High      │ ✅ None      │")
    print("│ Testability                  │ ❌ Hard      │ ✅ Easy      │")
    print("│ Maintainability              │ ❌ Hard      │ ✅ Easy      │")
    print("│ Migration Readiness          │ ❌ Stuck     │ ✅ Ready     │")
    print("│ Business Logic Clarity       │ ❌ Mixed     │ ✅ Clear     │")
    print("│ Status Handling              │ ❌ Codes     │ ✅ Enums     │")
    print("│ Date Handling                │ ❌ Strings   │ ✅ datetime  │")
    print("│ Type Safety                  │ ❌ dict/Any  │ ✅ Dataclass │")
    print("│ IDE Support                  │ ❌ Poor      │ ✅ Excellent │")
    print("└──────────────────────────────┴──────────────┴──────────────┘")

    print("\n🎯 Key Architecture Differences:\n")

    print("WITHOUT ACL:")
    print("┌─────────────┐")
    print("│  Services   │")
    print("│             │")
    print("│ - Parse     │")
    print("│   dates     │")
    print("│ - Decode    │")
    print("│   status    │")
    print("│ - Handle    │")
    print("│   legacy    │")
    print("└──────┬──────┘")
    print("       │")
    print("       ▼")
    print("  Legacy API")

    print("\nWITH ACL:")
    print("┌─────────────┐")
    print("│  Services   │ ← Clean domain objects")
    print("│             │")
    print("│ - Business  │")
    print("│   logic     │")
    print("│ - Domain    │")
    print("│   rules     │")
    print("└──────┬──────┘")
    print("       │")
    print("       ▼")
    print("┌─────────────┐")
    print("│     ACL     │ ← Translation layer")
    print("│             │")
    print("│ - Translate │")
    print("│ - Validate  │")
    print("│ - Adapt     │")
    print("└──────┬──────┘")
    print("       │")
    print("       ▼")
    print("  Legacy API")

    print("\n💡 When to use Anti-Corruption Layer:")
    print("   ✓ Integrating with legacy systems")
    print("   ✓ Working with poorly designed third-party APIs")
    print("   ✓ Migrating from old to new systems")
    print("   ✓ Multiple external systems with different models")
    print("   ✓ Want to protect your domain model")

    print("\n❌ When NOT to use:")
    print("   ✗ Internal services you control")
    print("   ✗ Well-designed external APIs")
    print("   ✗ Simple CRUD with no business logic")
    print("   ✗ Over-engineering for systems you own")

    print("\n📚 Real-world examples:")
    print("   • Migrating from mainframe to microservices")
    print("   • Integrating with SAP, Oracle, Salesforce")
    print("   • Wrapping vendor APIs with terrible naming")
    print("   • Multi-supplier e-commerce integration")
    print("   • Gradual replacement of monolithic systems")

    print("\n📖 Learn more:")
    print("   • Microsoft: https://learn.microsoft.com/azure/architecture/patterns/anti-corruption-layer")
    print("   • Pattern README: ../README.md")
    print("\n")


if __name__ == "__main__":
    run_comparison()
