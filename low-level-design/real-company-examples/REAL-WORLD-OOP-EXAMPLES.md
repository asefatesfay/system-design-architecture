# Real-World OOP Examples - From Daily Life to Code

> **🌍 Multi-Language Support:** Examples use Python for clarity. For complete multi-language implementations:
> - **[Four Pillars - All Languages](../03-oop-fundamentals/four-pillars.md)** ⭐⭐⭐ - Python, Go, Java, JavaScript side-by-side
> - **[Language Comparison Guide](../lld-coding/multi-language/LANGUAGE-COMPARISON.md)** - Choose your interview language
> - **[Complete Interview Examples](../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md)** - Practice in all 4 languages
>
> This guide focuses on WHY concepts matter. For HOW to implement them in your language, see the links above.

This guide shows how **Abstraction, Encapsulation, Inheritance, and Polymorphism** appear in everyday life, then translates them into code.

## 📑 Table of Contents

1. [Abstraction - Hiding Complexity](#1-abstraction---hiding-complexity)
2. [Encapsulation - Protecting Data](#2-encapsulation---protecting-data)
3. [Inheritance - Reusing and Extending](#3-inheritance---reusing-and-extending)
4. [Polymorphism - Same Interface, Different Forms](#4-polymorphism---same-interface-different-forms)
5. [All Four Together - Real System](#5-all-four-together---real-system)

---

# 1. Abstraction - Hiding Complexity

## 🎯 The Core Idea

**Abstraction** means showing only essential features while hiding complex implementation details.

**Everyday analogy**: You drive a car by using the steering wheel, gas pedal, and brake. You don't need to know about fuel injection, transmission gears, or engine combustion.

## 🚗 Real-World Example 1: Driving a Car

```python
# Without Abstraction - TOO COMPLEX FOR USER!
class CarWithoutAbstraction:
    def start(self):
        print("User must do all this:")
        print("1. Check fuel pressure: 40-60 PSI")
        print("2. Prime fuel pump")
        print("3. Engage starter motor at 200 RPM")
        print("4. Adjust air-fuel mixture ratio to 14.7:1")
        print("5. Fire spark plugs in sequence: 1-3-4-2")
        print("6. Monitor engine temperature")
        print("7. Regulate idle speed to 800 RPM")
        print("... 50 more steps ...")

# With Abstraction - SIMPLE FOR USER!
class Car:
    """Simple interface, complex implementation hidden"""

    def __init__(self, make, model):
        self.make = make
        self.model = model
        # Complex internal state hidden
        self.__engine_running = False
        self.__fuel_system = FuelSystem()
        self.__ignition = IgnitionSystem()
        self.__transmission = Transmission()

    def start(self):
        """Simple interface - just turn the key!"""
        print(f"🚗 Starting {self.make} {self.model}")
        self.__fuel_system._prime()
        self.__ignition._engage()
        self.__engine_running = True
        print("✓ Engine running")

    def drive(self, speed_mph):
        """Simple interface - just press gas!"""
        if self.__engine_running:
            self.__transmission._adjust_for_speed(speed_mph)
            print(f"🏎️ Driving at {speed_mph} mph")
        else:
            print("❌ Start the car first!")

    def stop(self):
        """Simple interface - just press brake!"""
        print("🛑 Car stopped")
        self.__engine_running = False

# User experience is simple!
my_car = Car("Tesla", "Model 3")
my_car.start()      # One simple call
my_car.drive(60)    # Another simple call
my_car.stop()       # Easy!
```

## 📱 Real-World Example 2: Your Smartphone

```python
from abc import ABC, abstractmethod

# Abstract interface - what users see
class Smartphone(ABC):
    """Users interact with simple methods"""

    @abstractmethod
    def send_message(self, to: str, message: str):
        """User just types and sends"""
        pass

    @abstractmethod
    def make_call(self, phone_number: str):
        """User just dials and calls"""
        pass

    @abstractmethod
    def take_photo(self):
        """User just clicks the button"""
        pass

# Concrete implementation - all complexity hidden
class iPhone(Smartphone):
    def __init__(self):
        # Hidden complex systems
        self.__network_module = NetworkModule()
        self.__camera_system = CameraSystem()
        self.__display = Display()
        self.__battery = Battery()

    def send_message(self, to: str, message: str):
        """Simple for user, complex internally"""
        print(f"📱 Sending message to {to}")

        # All this complexity is hidden:
        self.__network_module._establish_connection()
        self.__network_module._encrypt_message(message)
        self.__network_module._route_through_towers()
        self.__network_module._handle_delivery_confirmation()

        print("✓ Message sent!")

    def make_call(self, phone_number: str):
        """User perspective: simple button press"""
        print(f"📞 Calling {phone_number}")

        # Hidden complexity:
        self.__network_module._connect_to_cellular()
        self.__network_module._establish_voice_channel()
        self.__network_module._encode_audio()
        self.__network_module._maintain_connection_quality()

        print("✓ Call connected!")

    def take_photo(self):
        """User perspective: click button"""
        print("📸 Taking photo")

        # Hidden complexity:
        self.__camera_system._adjust_focus()
        self.__camera_system._set_exposure()
        self.__camera_system._capture_raw_data()
        self.__camera_system._apply_image_processing()
        self.__camera_system._apply_AI_enhancements()
        self.__camera_system._compress_image()

        print("✓ Photo saved!")

# User experience is beautifully simple
phone = iPhone()
phone.send_message("Mom", "On my way home!")
phone.make_call("555-1234")
phone.take_photo()
```

## 🏦 Real-World Example 3: ATM Machine

> **📂 Complete runnable implementation**: See [examples/complete-atm-example.py](examples/complete-atm-example.py)
>
> This includes all supporting classes: BankSystem, BankAccount, CashDispenser, CardReader, PINValidator, ReceiptPrinter, and demo scenarios.

**The Abstraction Concept**:

```python
# What the user sees - Simple!
atm.withdraw_cash(card_number="1234567890123456", pin="1234", amount=200.00)

# What happens behind the scenes (hidden from user):
# 1. CardReader reads magnetic stripe/chip
# 2. BankSystem connects to mainframe
# 3. PINValidator checks PIN (tracks failed attempts)
# 4. BankAccount checks balance and daily limit
# 5. CashDispenser counts optimal bills
# 6. CashDispenser physically dispenses cash
# 7. BankAccount updates balance
# 8. BankSystem logs transaction
# 9. ReceiptPrinter prints receipt
# 10. Error handling throughout
```

**Simplified Overview** (see complete implementation for full code):

```python
class ATM:
    """Simple interface for users, complex backend"""

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
        Insert card → Enter PIN → Get cash

        HIDDEN COMPLEXITY: 10-step process
        """
        print(f"💳 Processing withdrawal of ${amount}")

        # Step 1: Read card
        card_data = self.__card_reader.read_card(card_number)
        if not card_data['read_successful']:
            return False

        # Step 2: Validate PIN
        if not self.__pin_validator.verify(card_number, pin):
            print("❌ Invalid PIN")
            return False

        # Step 3: Get account from bank
        account = self.__bank_system.get_account(card_number)
        if not account:
            return False

        # Step 4-5: Check balance and limits
        if account.get_balance() < amount:
            print("❌ Insufficient funds")
            return False

        # Step 6-7: Count and dispense bills
        bills = self.__cash_dispenser.count_bills(amount)
        if bills is None:
            return False
        self.__cash_dispenser.dispense(bills)

        # Step 8-9: Update account and log
        account.debit(amount)
        self.__bank_system.log_transaction(card_number, amount)

        # Step 10: Print receipt
        self.__receipt_printer.print_receipt(
            amount, account.get_balance(), card_number[-4:]
        )

        print(f"✅ Please take your ${amount}")
        return True

# User sees simple interface
atm = ATM("ATM-001", "Downtown Branch")
atm.withdraw_cash("1234567890123456", "1234", 200.00)
```

**Key Abstraction Points**:
- ✅ User sees: 1 simple method call
- ✅ Hidden: 10+ complex operations
- ✅ Hidden: 6 different subsystem classes
- ✅ Hidden: Error handling, logging, security
- ✅ Result: Easy to use, hard to break

## 🎮 Real-World Example 4: Video Game Character

```python
class GameCharacter:
    """Player sees simple controls, complex game logic hidden"""

    def __init__(self, name):
        self.name = name
        # Hidden complex state
        self.__position = Vector3D(0, 0, 0)
        self.__health = 100
        self.__stamina = 100
        self.__inventory = Inventory()
        self.__animation_state = AnimationStateMachine()
        self.__physics_body = PhysicsBody()
        self.__collision_detector = CollisionDetector()

    def move_forward(self):
        """Player presses 'W' - simple!"""
        print(f"🏃 {self.name} moving forward")

        # Hidden complexity:
        self.__stamina -= 0.1
        self.__animation_state.transition_to('running')

        # Complex physics calculations
        new_position = self.__calculate_new_position()
        collisions = self.__collision_detector.check(new_position)

        if not collisions:
            self.__position = new_position
            self.__update_camera()
            self.__trigger_footstep_sounds()

    def jump(self):
        """Player presses 'Space' - simple!"""
        print(f"⬆️ {self.name} jumping")

        # Hidden complexity:
        if self.__stamina < 10:
            print("Too tired to jump!")
            return

        self.__stamina -= 10
        self.__animation_state.transition_to('jumping')
        self.__physics_body.apply_force(Vector3D(0, 500, 0))
        self.__play_jump_sound()

    def attack(self):
        """Player clicks mouse - simple!"""
        print(f"⚔️ {self.name} attacking")

        # Hidden complexity:
        weapon = self.__inventory.get_equipped_weapon()
        targets = self.__detect_enemies_in_range()

        for target in targets:
            damage = self.__calculate_damage(weapon, target)
            target.take_damage(damage)

        self.__animation_state.transition_to('attacking')
        self.__stamina -= 5

# Player experience is intuitive
player = GameCharacter("Hero")
player.move_forward()  # Simple key press
player.jump()          # Simple key press
player.attack()        # Simple click
```

## 🍳 Real-World Example 5: Coffee Machine

```python
class CoffeeMachine:
    """User presses button, machine handles complexity"""

    def __init__(self):
        # Complex internal systems
        self.__water_reservoir = WaterReservoir()
        self.__grinder = CoffeeGrinder()
        self.__heater = WaterHeater()
        self.__pump = WaterPump()
        self.__milk_frother = MilkFrother()

    def make_espresso(self):
        """User interface: just press one button!"""
        print("☕ Making espresso...")

        # All this complexity is hidden:
        self.__water_reservoir._check_water_level()
        self.__heater._heat_water_to(92)  # degrees Celsius
        self.__grinder._grind_beans(7)    # grams
        self.__pump._build_pressure(9)    # bars
        self.__pump._extract_for(25)      # seconds

        print("✅ Espresso ready!")

    def make_cappuccino(self):
        """User interface: just press one button!"""
        print("☕ Making cappuccino...")

        # Hidden complexity:
        self.make_espresso()  # Reuse espresso logic

        # Additional steps for cappuccino:
        self.__milk_frother._heat_milk_to(65)
        self.__milk_frother._create_microfoam()
        self.__milk_frother._pour_with_pattern('heart')

        print("✅ Cappuccino ready!")

    def make_latte(self):
        """User interface: just press one button!"""
        print("☕ Making latte...")

        # Hidden complexity:
        self.make_espresso()
        self.__milk_frother._heat_milk_to(70)
        self.__milk_frother._create_foam()
        self.__milk_frother._pour_simple()

        print("✅ Latte ready!")

# User experience: beautifully simple
coffee_machine = CoffeeMachine()
coffee_machine.make_espresso()     # One button
coffee_machine.make_cappuccino()   # One button
coffee_machine.make_latte()        # One button
```

## 💡 Key Takeaways for Abstraction

1. **Hide Complexity**: Users shouldn't need to know internal details
2. **Simple Interface**: Provide easy-to-use methods
3. **Maintain Encapsulation**: Keep internal workings private
4. **Think User-First**: Design from user's perspective

---

# 2. Encapsulation - Protecting Data

## 🎯 The Core Idea

**Encapsulation** means bundling data with methods that operate on that data, and restricting direct access to some components.

**Everyday analogy**: Your house has valuable items inside, but doors and locks control who can enter. You don't let everyone access everything.

## 🏦 Real-World Example 1: Bank Account Security

```python
class BankAccount:
    """
    Real bank security:
    - You can't directly access the vault
    - You can't modify balance directly
    - All access is controlled and logged
    """

    def __init__(self, account_holder, initial_balance):
        self.account_holder = account_holder  # Public: can see name
        self.__balance = initial_balance       # Private: can't touch directly!
        self.__transaction_history = []       # Private: protected data
        self.__pin = self.__generate_secure_pin()  # Private: very sensitive!

    # PUBLIC INTERFACE - Controlled access

    def deposit(self, amount, pin):
        """Add money - but with validation!"""
        if not self.__verify_pin(pin):
            print("❌ Invalid PIN")
            self.__log_failed_attempt("deposit")
            return False

        if amount <= 0:
            print("❌ Amount must be positive")
            return False

        # Only modify balance through controlled method
        self.__balance += amount
        self.__log_transaction("deposit", amount)
        print(f"✅ Deposited ${amount}")
        return True

    def withdraw(self, amount, pin):
        """Remove money - with multiple checks!"""
        if not self.__verify_pin(pin):
            print("❌ Invalid PIN")
            self.__log_failed_attempt("withdraw")
            return False

        if amount <= 0:
            print("❌ Amount must be positive")
            return False

        if amount > self.__balance:
            print("❌ Insufficient funds")
            return False

        # Check daily withdrawal limit
        daily_total = self.__get_todays_withdrawals()
        if daily_total + amount > 1000:
            print("❌ Daily withdrawal limit exceeded")
            return False

        self.__balance -= amount
        self.__log_transaction("withdraw", amount)
        print(f"✅ Withdrew ${amount}")
        return True

    # PROPERTY - Safe read-only access
    @property
    def balance(self):
        """Can VIEW balance, but not change it directly"""
        return self.__balance

    @property
    def recent_transactions(self):
        """Can VIEW last 5 transactions"""
        return self.__transaction_history[-5:]

    # PRIVATE METHODS - Internal use only

    def __verify_pin(self, pin):
        """Security check - private method"""
        return pin == self.__pin

    def __log_transaction(self, type, amount):
        """Record keeping - private method"""
        self.__transaction_history.append({
            'type': type,
            'amount': amount,
            'timestamp': datetime.now(),
            'balance_after': self.__balance
        })

    def __log_failed_attempt(self, attempted_action):
        """Security logging - private method"""
        print(f"⚠️ Security alert: Failed {attempted_action} attempt")
        # In real system, would alert fraud detection

    def __get_todays_withdrawals(self):
        """Internal calculation - private method"""
        today = datetime.now().date()
        return sum(
            t['amount'] for t in self.__transaction_history
            if t['type'] == 'withdraw' and t['timestamp'].date() == today
        )

    def __generate_secure_pin(self):
        """Generate PIN - private method"""
        import random
        return f"{random.randint(1000, 9999)}"

# Usage - Protected!
account = BankAccount("Alice", 1000)

# ✅ GOOD - Using controlled interface
account.deposit(500, "1234")
account.withdraw(200, "1234")
print(f"Balance: ${account.balance}")  # Safe viewing

# ❌ BAD - Can't do these!
# account.__balance = 1000000  # AttributeError: can't access
# account.__pin = "0000"       # AttributeError: can't access
# account.balance = 5000       # AttributeError: read-only property
```

## 🏠 Real-World Example 2: Smart Home Thermostat

```python
class SmartThermostat:
    """
    Real smart home:
    - Temperature sensor is internal
    - Heating/cooling logic is internal
    - Users just set desired temperature
    """

    def __init__(self, location):
        self.location = location  # Public

        # PRIVATE - Internal state users shouldn't touch
        self.__current_temp = 72
        self.__target_temp = 72
        self.__heater_on = False
        self.__ac_on = False
        self.__fan_speed = 0
        self.__filter_hours = 0
        self.__maintenance_alerts = []

    # PUBLIC INTERFACE

    def set_temperature(self, temp):
        """Simple interface - users just set desired temp"""
        if not 60 <= temp <= 85:
            print("❌ Temperature must be between 60-85°F")
            return False

        print(f"🌡️ Setting temperature to {temp}°F")
        self.__target_temp = temp
        self.__adjust_climate()  # Internal method handles complexity
        return True

    def set_mode(self, mode):
        """User-friendly mode selection"""
        valid_modes = ['heat', 'cool', 'auto', 'off']
        if mode not in valid_modes:
            print(f"❌ Invalid mode. Choose from: {valid_modes}")
            return False

        self.__mode = mode
        self.__adjust_climate()
        return True

    # PROPERTIES - Controlled access

    @property
    def current_temperature(self):
        """Users can READ current temp"""
        return self.__current_temp

    @property
    def target_temperature(self):
        """Users can READ target temp"""
        return self.__target_temp

    @property
    def is_heating(self):
        """Users can see status"""
        return self.__heater_on

    @property
    def is_cooling(self):
        """Users can see status"""
        return self.__ac_on

    @property
    def needs_filter_change(self):
        """Alert users when maintenance needed"""
        return self.__filter_hours > 720  # 30 days

    # PRIVATE METHODS - Internal logic

    def __adjust_climate(self):
        """Complex climate control logic - users don't see this"""
        diff = self.__target_temp - self.__current_temp

        if diff > 2:  # Too cold
            self.__activate_heater()
        elif diff < -2:  # Too hot
            self.__activate_ac()
        else:  # Just right
            self.__turn_off_systems()

    def __activate_heater(self):
        """Internal method"""
        self.__heater_on = True
        self.__ac_on = False
        self.__fan_speed = self.__calculate_fan_speed()
        print("🔥 Heater activated")
        self.__log_energy_usage('heater')

    def __activate_ac(self):
        """Internal method"""
        self.__ac_on = True
        self.__heater_on = False
        self.__fan_speed = self.__calculate_fan_speed()
        print("❄️ AC activated")
        self.__log_energy_usage('ac')

    def __turn_off_systems(self):
        """Internal method"""
        self.__heater_on = False
        self.__ac_on = False
        self.__fan_speed = 0
        print("✓ Climate control idle - temp is perfect")

    def __calculate_fan_speed(self):
        """Complex calculation - internal only"""
        temp_diff = abs(self.__target_temp - self.__current_temp)
        if temp_diff > 5:
            return 100  # Maximum
        elif temp_diff > 3:
            return 75
        else:
            return 50

    def __log_energy_usage(self, system):
        """Track usage - internal logging"""
        # In real system, would save to database
        self.__filter_hours += 1

    def __check_maintenance(self):
        """Internal health monitoring"""
        if self.__filter_hours > 720:
            self.__maintenance_alerts.append("Replace air filter")
        if self.__filter_hours > 1440:
            self.__maintenance_alerts.append("Schedule HVAC service")

# Usage
thermostat = SmartThermostat("Living Room")

# ✅ GOOD - Simple user interface
thermostat.set_temperature(75)
print(f"Current: {thermostat.current_temperature}°F")
print(f"Heating: {thermostat.is_heating}")

if thermostat.needs_filter_change:
    print("⚠️ Time to change filter!")

# ❌ BAD - Can't do these!
# thermostat.__heater_on = True  # Can't directly control hardware
# thermostat.__current_temp = 100  # Can't fake sensor reading
# thermostat.current_temperature = 80  # Read-only property
```

## 💊 Real-World Example 3: Medicine Dispenser

```python
from datetime import datetime, timedelta

class MedicineDispenser:
    """
    Real medicine safety:
    - Pills stored securely
    - Dosage controlled
    - Timing enforced
    - Overdose prevention
    """

    def __init__(self, patient_name, medicine_name, dosage_mg):
        self.patient_name = patient_name  # Public
        self.medicine_name = medicine_name  # Public

        # PRIVATE - Safety-critical data
        self.__pills_remaining = 30
        self.__dosage_mg = dosage_mg
        self.__last_dose_time = None
        self.__min_hours_between_doses = 6
        self.__max_daily_doses = 4
        self.__dose_history = []
        self.__locked = True
        self.__pin = "1234"

    # PUBLIC INTERFACE

    def dispense_dose(self, pin):
        """Controlled pill dispensing"""
        print(f"💊 Attempting to dispense {self.medicine_name}")

        # Check 1: Verify PIN
        if not self.__verify_pin(pin):
            print("❌ Invalid PIN")
            self.__log_failed_attempt()
            return False

        # Check 2: Pills available?
        if self.__pills_remaining == 0:
            print("❌ No pills remaining - refill needed")
            return False

        # Check 3: Too soon since last dose?
        if not self.__can_take_dose():
            hours_to_wait = self.__hours_until_next_dose()
            print(f"❌ Too soon! Wait {hours_to_wait:.1f} more hours")
            return False

        # Check 4: Daily limit reached?
        if self.__exceeded_daily_limit():
            print("❌ Daily dose limit reached")
            return False

        # All checks passed - dispense!
        self.__dispense_pill()
        return True

    # PROPERTIES - Safe viewing only

    @property
    def pills_remaining(self):
        return self.__pills_remaining

    @property
    def time_since_last_dose(self):
        if not self.__last_dose_time:
            return "No doses taken yet"
        elapsed = datetime.now() - self.__last_dose_time
        hours = elapsed.total_seconds() / 3600
        return f"{hours:.1f} hours ago"

    @property
    def can_take_next_dose(self):
        return self.__can_take_dose()

    @property
    def doses_today(self):
        return self.__count_doses_today()

    # PRIVATE METHODS - Safety logic

    def __verify_pin(self, pin):
        return pin == self.__pin

    def __can_take_dose(self):
        if not self.__last_dose_time:
            return True

        time_since_last = datetime.now() - self.__last_dose_time
        hours_since_last = time_since_last.total_seconds() / 3600
        return hours_since_last >= self.__min_hours_between_doses

    def __hours_until_next_dose(self):
        if not self.__last_dose_time:
            return 0

        time_since_last = datetime.now() - self.__last_dose_time
        hours_since_last = time_since_last.total_seconds() / 3600
        return self.__min_hours_between_doses - hours_since_last

    def __exceeded_daily_limit(self):
        return self.__count_doses_today() >= self.__max_daily_doses

    def __count_doses_today(self):
        today = datetime.now().date()
        return sum(
            1 for dose_time in self.__dose_history
            if dose_time.date() == today
        )

    def __dispense_pill(self):
        self.__pills_remaining -= 1
        self.__last_dose_time = datetime.now()
        self.__dose_history.append(datetime.now())

        print(f"✅ Dispensed {self.__dosage_mg}mg {self.medicine_name}")
        print(f"   Pills remaining: {self.__pills_remaining}")
        print(f"   Next dose available in {self.__min_hours_between_doses} hours")

    def __log_failed_attempt(self):
        # In real system, would alert caregiver
        print("⚠️ Failed dispensing attempt logged")

# Usage
dispenser = MedicineDispenser("John Doe", "Aspirin", 500)

# ✅ GOOD - Safe controlled access
dispenser.dispense_dose("1234")
print(f"Pills left: {dispenser.pills_remaining}")
print(f"Last dose: {dispenser.time_since_last_dose}")

# ❌ BAD - Can't bypass safety!
# dispenser.__pills_remaining = 100  # Can't fake pill count
# dispenser.__last_dose_time = None  # Can't reset timer
# dispenser.__dosage_mg = 5000  # Can't increase dosage
```

## 💡 Key Takeaways for Encapsulation

1. **Protect Sensitive Data**: Use private variables (`__variable`)
2. **Control Access**: Provide public methods with validation
3. **Use Properties**: For read-only or controlled access
4. **Hide Implementation**: Users shouldn't see internal logic
5. **Prevent Invalid States**: Validate all inputs

---

# 3. Inheritance - Reusing and Extending

## 🎯 The Core Idea

**Inheritance** allows a class to inherit properties and methods from another class, promoting code reuse.

**Everyday analogy**: Your genetic traits from parents (eye color, height tendency) plus your unique traits (personality, learned skills).

## 👨‍👩‍👧‍👦 Real-World Example 1: Employee Hierarchy

```python
from datetime import datetime
from typing import List

class Employee:
    """
    Base class: What ALL employees have in common

    Like genetics: every employee is a person with:
    - Name, ID, salary
    - Can work, take breaks, get paid
    """

    # Class variable - applies to all employees
    company_name = "TechCorp Inc."

    def __init__(self, emp_id, name, base_salary):
        self.emp_id = emp_id
        self.name = name
        self.base_salary = base_salary
        self.hire_date = datetime.now()
        self.vacation_days = 20

    def work(self):
        """All employees work"""
        print(f"👔 {self.name} is working")

    def take_break(self):
        """All employees take breaks"""
        print(f"☕ {self.name} is on break")

    def request_vacation(self, days):
        """All employees can request vacation"""
        if days <= self.vacation_days:
            self.vacation_days -= days
            print(f"✓ {self.name} approved for {days} days vacation")
            return True
        else:
            print(f"❌ Not enough vacation days")
            return False

    def calculate_monthly_pay(self):
        """Base implementation - can be overridden"""
        return self.base_salary / 12

    def __str__(self):
        return f"{self.name} ({self.emp_id})"

# ============================================
# INHERITANCE: Specialized employee types
# ============================================

class Developer(Employee):
    """
    Developer IS-AN Employee
    + Programming skills
    + GitHub commits
    + Code reviews
    """

    def __init__(self, emp_id, name, base_salary, programming_languages):
        super().__init__(emp_id, name, base_salary)  # Inherit from parent

        # Developer-specific attributes
        self.programming_languages = programming_languages
        self.commits_this_month = 0
        self.bugs_fixed = 0

    # Developer-specific methods
    def write_code(self, project):
        """Only developers write code"""
        self.commits_this_month += 1
        print(f"💻 {self.name} writing code for {project}")
        print(f"   Languages: {', '.join(self.programming_languages)}")

    def fix_bug(self, bug_id):
        """Only developers fix bugs"""
        self.bugs_fixed += 1
        print(f"🐛 {self.name} fixed bug #{bug_id}")

    def code_review(self, other_developer):
        """Only developers do code reviews"""
        print(f"👀 {self.name} reviewing {other_developer.name}'s code")

    # Override parent method with developer-specific logic
    def calculate_monthly_pay(self):
        """Developers get bonus for commits and bug fixes"""
        base_pay = super().calculate_monthly_pay()
        commit_bonus = self.commits_this_month * 10
        bug_bonus = self.bugs_fixed * 50
        total = base_pay + commit_bonus + bug_bonus
        print(f"💰 {self.name}'s pay: ${base_pay:.2f} base + "
              f"${commit_bonus} (commits) + ${bug_bonus} (bugs) = ${total:.2f}")
        return total

class Manager(Employee):
    """
    Manager IS-AN Employee
    + Team management
    + Budget control
    + Meetings
    """

    def __init__(self, emp_id, name, base_salary, department):
        super().__init__(emp_id, name, base_salary)

        # Manager-specific attributes
        self.department = department
        self.team_members: List[Employee] = []
        self.meetings_this_week = 0

    def hire_employee(self, employee):
        """Only managers can hire"""
        self.team_members.append(employee)
        print(f"✓ {self.name} hired {employee.name} to {self.department}")

    def conduct_meeting(self, topic):
        """Managers conduct meetings"""
        self.meetings_this_week += 1
        print(f"📊 {self.name} conducting meeting about '{topic}'")

    def approve_timeoff(self, employee, days):
        """Only managers can approve"""
        if employee in self.team_members:
            print(f"✓ {self.name} approved {days} days for {employee.name}")
            return True
        else:
            print(f"❌ {employee.name} is not in {self.name}'s team")
            return False

    def calculate_monthly_pay(self):
        """Managers get higher base + team size bonus"""
        base_pay = super().calculate_monthly_pay()
        team_bonus = len(self.team_members) * 200
        meeting_bonus = self.meetings_this_week * 25
        total = base_pay + team_bonus + meeting_bonus
        print(f"💰 {self.name}'s pay: ${base_pay:.2f} base + "
              f"${team_bonus} (team) + ${meeting_bonus} (meetings) = ${total:.2f}")
        return total

class Intern(Developer):
    """
    Intern IS-A Developer (which IS-AN Employee)
    Multi-level inheritance!

    + Learning
    + Mentorship
    + Limited responsibilities
    """

    def __init__(self, emp_id, name, hourly_rate, programming_languages, university):
        # Can't use base_salary, interns are hourly
        super().__init__(emp_id, name, 0, programming_languages)
        self.hourly_rate = hourly_rate
        self.hours_worked = 0
        self.university = university
        self.mentor = None

    def assign_mentor(self, developer):
        """Interns get mentors"""
        self.mentor = developer
        print(f"🎓 {developer.name} is now mentoring {self.name}")

    def attend_training(self, topic):
        """Interns attend training"""
        print(f"📚 {self.name} learning about {topic}")

    def log_hours(self, hours):
        """Interns track hours"""
        self.hours_worked += hours
        print(f"⏰ {self.name} logged {hours} hours")

    def calculate_monthly_pay(self):
        """Interns paid hourly"""
        total = self.hours_worked * self.hourly_rate
        print(f"💰 {self.name}'s pay: {self.hours_worked} hours × "
              f"${self.hourly_rate}/hr = ${total:.2f}")
        self.hours_worked = 0  # Reset for next month
        return total

# ============================================
# Usage: Inheritance in action!
# ============================================

# All inherit from Employee - common interface
alice = Developer("D001", "Alice", 120000, ["Python", "JavaScript", "Go"])
bob = Manager("M001", "Bob", 150000, "Engineering")
carol = Intern("I001", "Carol", 25, ["Python"], "Stanford University")

# ✅ All can do basic employee things (inherited)
alice.work()
bob.work()
carol.take_break()

# ✅ Each has specialized abilities
alice.write_code("Payment Service")
alice.fix_bug("BUG-123")

bob.hire_employee(alice)
bob.conduct_meeting("Q4 Planning")

carol.assign_mentor(alice)
carol.attend_training("Cloud Architecture")
carol.log_hours(20)

# ✅ Pay calculation - polymorphic behavior!
print("\n💰 Monthly Payroll:")
print("="*50)
alice.calculate_monthly_pay()
bob.calculate_monthly_pay()
carol.calculate_monthly_pay()
```

## 🐾 Real-World Example 2: Animal Kingdom

```python
class Animal:
    """Base class - what ALL animals have"""

    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age
        self.hunger_level = 50
        self.energy_level = 100

    def eat(self, food):
        """All animals eat"""
        self.hunger_level = max(0, self.hunger_level - 30)
        print(f"🍽️ {self.name} is eating {food}")

    def sleep(self, hours):
        """All animals sleep"""
        self.energy_level = min(100, self.energy_level + (hours * 10))
        print(f"😴 {self.name} slept for {hours} hours")

    def make_sound(self):
        """Generic sound - subclasses should override"""
        print(f"{self.name} makes a sound")

class Dog(Animal):
    """Dog IS-AN Animal + dog-specific traits"""

    def __init__(self, name, breed, age):
        super().__init__(name, "Canis familiaris", age)
        self.breed = breed
        self.is_good_boy = True  # Always true!

    def make_sound(self):
        """Override with dog-specific sound"""
        print(f"🐕 {self.name} says: Woof! Woof!")

    def fetch(self, item="ball"):
        """Only dogs fetch"""
        if self.energy_level > 20:
            self.energy_level -= 15
            print(f"🎾 {self.name} is fetching the {item}!")
        else:
            print(f"😴 {self.name} is too tired to fetch")

    def wag_tail(self):
        """Only dogs wag tails"""
        print(f"🐕 {self.name} is wagging tail excitedly!")

class Cat(Animal):
    """Cat IS-AN Animal + cat-specific traits"""

    def __init__(self, name, fur_color, age):
        super().__init__(name, "Felis catus", age)
        self.fur_color = fur_color
        self.is_grumpy = True  # Cats...

    def make_sound(self):
        """Override with cat-specific sound"""
        if self.hunger_level > 70:
            print(f"🐱 {self.name} says: MEOOOW! (feed me!)")
        else:
            print(f"🐱 {self.name} says: meow")

    def scratch(self, furniture):
        """Only cats scratch furniture"""
        print(f"🐱 {self.name} is scratching the {furniture}")

    def knock_over(self, item):
        """Cats knock things over"""
        print(f"🐱 {self.name} knocked the {item} off the table")
        print(f"   (and watched it fall)")

class Bird(Animal):
    """Bird IS-AN Animal + bird-specific traits"""

    def __init__(self, name, species, age, can_fly):
        super().__init__(name, species, age)
        self.can_fly = can_fly

    def make_sound(self):
        """Override with bird-specific sound"""
        print(f"🐦 {self.name} says: Chirp chirp!")

    def fly(self):
        """Only birds (that can) fly"""
        if self.can_fly:
            if self.energy_level > 30:
                self.energy_level -= 20
                print(f"🦅 {self.name} is flying through the air!")
            else:
                print(f"😴 {self.name} is too tired to fly")
        else:
            print(f"{self.name} cannot fly")

# Usage
buddy = Dog("Buddy", "Golden Retriever", 3)
whiskers = Cat("Whiskers", "Orange Tabby", 5)
tweety = Bird("Tweety", "Canary", 2, can_fly=True)

# All can do animal things (inherited)
buddy.eat("kibble")
whiskers.eat("tuna")
tweety.eat("seeds")

# Each makes their own sound (polymorphism)
buddy.make_sound()     # Woof!
whiskers.make_sound()  # Meow
tweety.make_sound()    # Chirp!

# Each has unique abilities
buddy.fetch()
buddy.wag_tail()

whiskers.scratch("couch")
whiskers.knock_over("vase")

tweety.fly()
```

## 💡 Key Takeaways for Inheritance

1. **Reuse Code**: Don't repeat common functionality
2. **IS-A Relationship**: Child IS-A Parent
3. **Extend Behavior**: Add new methods, override existing ones
4. **Call Parent**: Use `super()` to access parent methods
5. **Multiple Levels**: Grandparent → Parent → Child

---

# 4. Polymorphism - Same Interface, Different Forms

## 🎯 The Core Idea

**Polymorphism** means "many forms" - same method name, different behavior based on the object.

**Everyday analogy**: The verb "open" - you open a door differently than you open a laptop, a car, or an umbrella, but the action is conceptually the same.

## 🔓 Real-World Example 1: Universal "Open" Operation

```python
class Door:
    def open(self):
        print("🚪 Turning doorknob")
        print("   Pushing door forward")
        print("   Door is open")

class Car:
    def open(self):
        print("🚗 Pressing key fob button")
        print("   Doors unlock with beep")
        print("   All 4 doors unlocked")

class Laptop:
    def open(self):
        print("💻 Lifting laptop lid")
        print("   Screen powers on")
        print("   System ready")

class Umbrella:
    def open(self):
        print("☂️ Pressing release button")
        print("   Umbrella springs open")
        print("   Protection from rain")

class BankAccount:
    def open(self):
        print("🏦 Filling out application")
        print("   Verifying identity")
        print("   Account created")

# Polymorphism: Same method name, different implementations!
def open_something(thing):
    """Works with ANY object that has open() method"""
    print(f"\nOpening {thing.__class__.__name__}:")
    thing.open()

# All work the same way from caller's perspective
open_something(Door())
open_something(Car())
open_something(Laptop())
open_something(Umbrella())
open_something(BankAccount())
```

## 💳 Real-World Example 2: Payment Processing (Very Common in Interviews!)

```python
from abc import ABC, abstractmethod
from datetime import datetime

class PaymentMethod(ABC):
    """Abstract base - defines the contract"""

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        """All payment methods must implement this"""
        pass

    @abstractmethod
    def refund(self, amount: float) -> bool:
        """All payment methods must handle refunds"""
        pass

class CreditCardPayment(PaymentMethod):
    """Specific implementation for credit cards"""

    def __init__(self, card_number, cvv, expiry):
        self.card_number = card_number[-4:]  # Store last 4 only
        self.cvv = cvv
        self.expiry = expiry

    def process_payment(self, amount: float) -> bool:
        print(f"💳 Processing ${amount:.2f} with Credit Card")
        print(f"   Card ending in {self.card_number}")
        print(f"   Connecting to Visa/Mastercard network...")
        print(f"   Authorizing transaction...")
        print(f"   Checking credit limit...")
        print(f"   ✓ Transaction approved")
        return True

    def refund(self, amount: float) -> bool:
        print(f"💳 Refunding ${amount:.2f} to Credit Card ****{self.card_number}")
        print(f"   Processing in 3-5 business days")
        return True

class PayPalPayment(PaymentMethod):
    """Specific implementation for PayPal"""

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def process_payment(self, amount: float) -> bool:
        print(f"🅿️ Processing ${amount:.2f} with PayPal")
        print(f"   Account: {self.email}")
        print(f"   Logging into PayPal...")
        print(f"   Checking PayPal balance...")
        print(f"   Sending payment...")
        print(f"   ✓ Payment sent")
        return True

    def refund(self, amount: float) -> bool:
        print(f"🅿️ Refunding ${amount:.2f} to PayPal account {self.email}")
        print(f"   Instant refund to balance")
        return True

class CryptocurrencyPayment(PaymentMethod):
    """Specific implementation for crypto"""

    def __init__(self, wallet_address, crypto_type):
        self.wallet_address = wallet_address
        self.crypto_type = crypto_type  # BTC, ETH, etc.

    def process_payment(self, amount: float) -> bool:
        print(f"₿ Processing ${amount:.2f} with {self.crypto_type}")
        print(f"   Wallet: {self.wallet_address[:10]}...")
        print(f"   Creating transaction...")
        print(f"   Broadcasting to blockchain...")
        print(f"   Waiting for confirmation...")
        print(f"   ✓ Transaction confirmed")
        return True

    def refund(self, amount: float) -> bool:
        print(f"₿ Refunding ${amount:.2f} in {self.crypto_type}")
        print(f"   Sending to wallet: {self.wallet_address[:10]}...")
        return True

class ApplePayPayment(PaymentMethod):
    """Specific implementation for Apple Pay"""

    def __init__(self, device_id):
        self.device_id = device_id

    def process_payment(self, amount: float) -> bool:
        print(f"🍎 Processing ${amount:.2f} with Apple Pay")
        print(f"   Hold iPhone near terminal...")
        print(f"   Authenticating with Face ID...")
        print(f"   Generating secure token...")
        print(f"   ✓ Payment complete")
        return True

    def refund(self, amount: float) -> bool:
        print(f"🍎 Refunding ${amount:.2f} to Apple Pay")
        return True

class BankTransferPayment(PaymentMethod):
    """Specific implementation for bank transfer"""

    def __init__(self, account_number, routing_number):
        self.account_number = account_number[-4:]
        self.routing_number = routing_number

    def process_payment(self, amount: float) -> bool:
        print(f"🏦 Processing ${amount:.2f} via Bank Transfer")
        print(f"   Account: ****{self.account_number}")
        print(f"   Initiating ACH transfer...")
        print(f"   ⚠️ Will complete in 2-3 business days")
        return True

    def refund(self, amount: float) -> bool:
        print(f"🏦 Refunding ${amount:.2f} to account ****{self.account_number}")
        print(f"   Reverse ACH initiated")
        return True

# ==================================================
# Polymorphism in Action - E-commerce Checkout
# ==================================================

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item_name, price):
        self.items.append({'name': item_name, 'price': price})

    def get_total(self):
        return sum(item['price'] for item in self.items)

    def checkout(self, payment_method: PaymentMethod):
        """
        POLYMORPHISM: This method works with ANY payment method!
        It doesn't care if it's credit card, PayPal, crypto, etc.
        """
        print("\n" + "="*60)
        print("🛒 CHECKOUT")
        print("="*60)

        # Show cart
        for item in self.items:
            print(f"  • {item['name']}: ${item['price']:.2f}")

        total = self.get_total()
        print(f"\nTotal: ${total:.2f}")
        print("-"*60)

        # Process payment - polymorphic call!
        if payment_method.process_payment(total):
            print("="*60)
            print("✅ ORDER COMPLETE!")
            print("="*60)
            self.items = []  # Clear cart
            return True
        else:
            print("❌ Payment failed")
            return False

# ==================================================
# Usage - Different customers, different payment methods
# ==================================================

# Customer 1: Pays with credit card
cart1 = ShoppingCart()
cart1.add_item("Laptop", 999.99)
cart1.add_item("Mouse", 29.99)
cart1.checkout(CreditCardPayment("1234567890123456", "123", "12/25"))

# Customer 2: Pays with PayPal
cart2 = ShoppingCart()
cart2.add_item("Headphones", 199.99)
cart2.checkout(PayPalPayment("alice@example.com", "password"))

# Customer 3: Pays with cryptocurrency
cart3 = ShoppingCart()
cart3.add_item("Monitor", 399.99)
cart3.checkout(CryptocurrencyPayment("1A2B3C4D5E6F7G8H9I", "Bitcoin"))

# Customer 4: Pays with Apple Pay
cart4 = ShoppingCart()
cart4.add_item("iPhone", 1199.99)
cart4.checkout(ApplePayPayment("iPhone-12345"))

# The beauty: checkout() code never changes!
# We can add 100 more payment methods, and checkout() still works!
```

## 🚚 Real-World Example 3: Shipping Methods

```python
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class ShippingMethod(ABC):
    """Abstract shipping interface"""

    @abstractmethod
    def calculate_cost(self, weight_kg, distance_km):
        pass

    @abstractmethod
    def estimated_delivery(self):
        pass

    @abstractmethod
    def track_package(self, tracking_number):
        pass

class StandardShipping(ShippingMethod):
    def calculate_cost(self, weight_kg, distance_km):
        base_cost = 5.00
        weight_cost = weight_kg * 0.50
        distance_cost = distance_km * 0.01
        return base_cost + weight_cost + distance_cost

    def estimated_delivery(self):
        delivery_date = datetime.now() + timedelta(days=7)
        return f"📦 Standard: {delivery_date.strftime('%B %d, %Y')}"

    def track_package(self, tracking_number):
        print(f"📍 Tracking {tracking_number}")
        print("   Status: In transit")
        print("   Location: Distribution center")

class ExpressShipping(ShippingMethod):
    def calculate_cost(self, weight_kg, distance_km):
        base_cost = 15.00
        weight_cost = weight_kg * 1.00
        distance_cost = distance_km * 0.02
        return base_cost + weight_cost + distance_cost

    def estimated_delivery(self):
        delivery_date = datetime.now() + timedelta(days=2)
        return f"🚀 Express: {delivery_date.strftime('%B %d, %Y')}"

    def track_package(self, tracking_number):
        print(f"📍 Tracking {tracking_number}")
        print("   Status: Out for delivery")
        print("   Estimated: Today by 8 PM")

class OvernightShipping(ShippingMethod):
    def calculate_cost(self, weight_kg, distance_km):
        base_cost = 30.00
        weight_cost = weight_kg * 2.00
        distance_cost = distance_km * 0.05
        return base_cost + weight_cost + distance_cost

    def estimated_delivery(self):
        delivery_date = datetime.now() + timedelta(days=1)
        return f"⚡ Overnight: Tomorrow by 10 AM"

    def track_package(self, tracking_number):
        print(f"📍 Tracking {tracking_number}")
        print("   Status: Priority processing")
        print("   Next-day delivery guaranteed")

class DroneDelivery(ShippingMethod):
    def calculate_cost(self, weight_kg, distance_km):
        if weight_kg > 2:
            return float('inf')  # Too heavy for drone
        base_cost = 25.00
        distance_cost = distance_km * 0.10
        return base_cost + distance_cost

    def estimated_delivery(self):
        delivery_time = datetime.now() + timedelta(hours=2)
        return f"🚁 Drone: Today at {delivery_time.strftime('%I:%M %p')}"

    def track_package(self, tracking_number):
        print(f"📍 Real-time drone tracking {tracking_number}")
        print("   Status: In flight")
        print("   Live GPS: View on map")

# Polymorphic shipping selection
def process_shipment(order, shipping_method: ShippingMethod):
    """Works with ANY shipping method!"""
    weight = order['weight']
    distance = order['distance']

    print(f"\n📦 Processing shipment")
    cost = shipping_method.calculate_cost(weight, distance)
    print(f"   Cost: ${cost:.2f}")
    print(f"   {shipping_method.estimated_delivery()}")

    return cost

# Customer chooses shipping method
order = {'weight': 1.5, 'distance': 500, 'items': ['Book', 'Mug']}

print("Choose shipping method:")
print("-" * 40)
process_shipment(order, StandardShipping())
process_shipment(order, ExpressShipping())
process_shipment(order, OvernightShipping())
process_shipment(order, DroneDelivery())
```

## 💡 Key Takeaways for Polymorphism

1. **Same Interface**: All implementations follow same method signatures
2. **Different Behavior**: Each class implements differently
3. **Interchangeable**: Can swap implementations without changing client code
4. **Flexibility**: Easy to add new implementations
5. **Duck Typing**: In Python, don't even need inheritance!

---

# 5. All Four Together - Real System

## 🎬 Complete Example: Netflix-like Streaming Service

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from datetime import datetime

# ==================================================
# ABSTRACTION: Hide complex video streaming details
# ==================================================

class VideoQuality(Enum):
    SD = "480p"
    HD = "720p"
    FULL_HD = "1080p"
    ULTRA_HD = "4K"

class VideoPlayer(ABC):
    """Abstract interface - users don't see complexity"""

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def adjust_quality(self, quality: VideoQuality):
        pass

# ==================================================
# ENCAPSULATION: Protect user data and payment info
# ==================================================

class User:
    """Encapsulated user data"""

    def __init__(self, user_id, email, name):
        self.user_id = user_id
        self.email = email
        self.name = name

        # PRIVATE: Sensitive data protected
        self.__password_hash = None
        self.__payment_method = None
        self.__watch_history = []
        self.__preferences = {}

    def set_password(self, password):
        """Controlled password setting with hashing"""
        # In real system, would use proper hashing
        self.__password_hash = hash(password)

    def verify_password(self, password):
        """Verify password without exposing hash"""
        return hash(password) == self.__password_hash

    def add_payment_method(self, payment_method):
        """Controlled payment method setting"""
        self.__payment_method = payment_method

    def record_watch(self, video):
        """Private watch history"""
        self.__watch_history.append({
            'video': video,
            'timestamp': datetime.now()
        })

    @property
    def recent_watches(self):
        """Controlled access to history"""
        return self.__watch_history[-10:]  # Last 10 only

# ==================================================
# INHERITANCE: Content hierarchy
# ==================================================

class Content(ABC):
    """Base class for all streamable content"""

    def __init__(self, content_id, title, duration_minutes, genre):
        self.content_id = content_id
        self.title = title
        self.duration_minutes = duration_minutes
        self.genre = genre
        self.rating = 0.0
        self.views = 0

    def play(self):
        """All content can be played"""
        self.views += 1
        print(f"▶️ Playing: {self.title}")

    @abstractmethod
    def get_description(self):
        pass

class Movie(Content):
    """Movie IS-A Content + movie-specific features"""

    def __init__(self, content_id, title, duration_minutes, genre, director, year):
        super().__init__(content_id, title, duration_minutes, genre)
        self.director = director
        self.year = year
        self.actors = []

    def get_description(self):
        return f"🎬 {self.title} ({self.year}) - Directed by {self.director}"

class TVShow(Content):
    """TV Show IS-A Content + seasons and episodes"""

    def __init__(self, content_id, title, genre):
        super().__init__(content_id, title, 0, genre)  # Duration varies
        self.seasons = []

    def add_season(self, season_number, episodes):
        self.seasons.append({
            'season': season_number,
            'episodes': episodes
        })

    def get_description(self):
        total_episodes = sum(len(s['episodes']) for s in self.seasons)
        return f"📺 {self.title} - {len(self.seasons)} seasons, {total_episodes} episodes"

class Documentary(Content):
    """Documentary IS-A Content + educational features"""

    def __init__(self, content_id, title, duration_minutes, subject, narrator):
        super().__init__(content_id, title, duration_minutes, "Documentary")
        self.subject = subject
        self.narrator = narrator

    def get_description(self):
        return f"📚 {self.title} - About {self.subject}, narrated by {self.narrator}"

# ==================================================
# POLYMORPHISM: Different subscription plans
# ==================================================

class SubscriptionPlan(ABC):
    """Polymorphic subscription interface"""

    @abstractmethod
    def get_monthly_cost(self):
        pass

    @abstractmethod
    def get_max_quality(self):
        pass

    @abstractmethod
    def get_simultaneous_streams(self):
        pass

    @abstractmethod
    def has_downloads(self):
        pass

class BasicPlan(SubscriptionPlan):
    def get_monthly_cost(self):
        return 8.99

    def get_max_quality(self):
        return VideoQuality.SD

    def get_simultaneous_streams(self):
        return 1

    def has_downloads(self):
        return False

class StandardPlan(SubscriptionPlan):
    def get_monthly_cost(self):
        return 13.99

    def get_max_quality(self):
        return VideoQuality.HD

    def get_simultaneous_streams(self):
        return 2

    def has_downloads(self):
        return True

class PremiumPlan(SubscriptionPlan):
    def get_monthly_cost(self):
        return 17.99

    def get_max_quality(self):
        return VideoQuality.ULTRA_HD

    def get_simultaneous_streams(self):
        return 4

    def has_downloads(self):
        return True

# ==================================================
# Complete System Using All Four Concepts
# ==================================================

class StreamingService:
    """Netflix-like service demonstrating all OOP concepts"""

    def __init__(self, service_name):
        self.service_name = service_name
        self.content_library: List[Content] = []
        self.users: dict = {}

    def add_content(self, content: Content):
        """Abstraction: Simple interface to add content"""
        self.content_library.append(content)

    def register_user(self, user: User, plan: SubscriptionPlan):
        """Encapsulation: User data protected"""
        self.users[user.user_id] = {
            'user': user,
            'plan': plan,
            'joined': datetime.now()
        }
        print(f"✓ {user.name} registered with {plan.__class__.__name__}")

    def stream_content(self, user: User, content: Content):
        """
        Polymorphism: Works with any content type
        Encapsulation: Checks user permissions
        """
        user_data = self.users.get(user.user_id)
        if not user_data:
            print("❌ User not registered")
            return

        plan = user_data['plan']
        max_quality = plan.get_max_quality()

        print(f"\n{content.get_description()}")
        print(f"Quality: {max_quality.value}")
        content.play()
        user.record_watch(content)

    def show_plan_comparison(self):
        """Polymorphism: Same interface, different plans"""
        plans = [BasicPlan(), StandardPlan(), PremiumPlan()]

        print(f"\n{'='*60}")
        print(f"{self.service_name} - Subscription Plans")
        print(f"{'='*60}")

        for plan in plans:
            print(f"\n{plan.__class__.__name__}:")
            print(f"  💰 Cost: ${plan.get_monthly_cost()}/month")
            print(f"  📺 Quality: {plan.get_max_quality().value}")
            print(f"  👥 Streams: {plan.get_simultaneous_streams()}")
            print(f"  💾 Downloads: {'Yes' if plan.has_downloads() else 'No'}")

# ==================================================
# Demo: All concepts working together
# ==================================================

# Create service
netflix = StreamingService("NetStream")

# Add content (Inheritance - different types)
netflix.add_content(Movie("M1", "Inception", 148, "Sci-Fi", "Christopher Nolan", 2010))
netflix.add_content(TVShow("T1", "Stranger Things", "Sci-Fi"))
netflix.add_content(Documentary("D1", "Planet Earth", 50, "Nature", "David Attenborough"))

# Create users (Encapsulation)
alice = User("U1", "alice@email.com", "Alice")
alice.set_password("secret123")

bob = User("U2", "bob@email.com", "Bob")
bob.set_password("password456")

# Register with different plans (Polymorphism)
netflix.register_user(alice, PremiumPlan())
netflix.register_user(bob, BasicPlan())

# Show plan comparison (Polymorphism)
netflix.show_plan_comparison()

# Stream content
print("\n" + "="*60)
print("Streaming Sessions:")
print("="*60)

for content in netflix.content_library:
    netflix.stream_content(alice, content)

print("\n✓ All OOP concepts demonstrated!")
print("  • Abstraction: Simple streaming interface")
print("  • Encapsulation: Protected user data")
print("  • Inheritance: Movie, TVShow, Documentary")
print("  • Polymorphism: Different subscription plans")
```

## 🎯 Final Summary

| Concept | What It Does | Real-World Analogy |
|---------|--------------|-------------------|
| **Abstraction** | Hide complexity | Car dashboard vs engine internals |
| **Encapsulation** | Protect data | Bank vault with controlled access |
| **Inheritance** | Reuse code | Family traits passed to children |
| **Polymorphism** | Same interface, different behavior | "Open" works on door, laptop, umbrella |

---

**You now have deep, real-world intuition for all OOP concepts! Practice these examples and you'll ace any LLD interview!** 🚀
