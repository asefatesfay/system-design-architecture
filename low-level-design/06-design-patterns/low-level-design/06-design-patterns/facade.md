# Facade Pattern

Provide a unified, simplified interface to a complex subsystem. Hide the complexities of the system and provide a simple interface.

## Why Facade?

**Problems it solves:**
- Complex subsystems are hard to use
- Too many classes and dependencies to manage
- Tight coupling between client and subsystem
- Need simple interface for common tasks

```python
# WITHOUT Facade - client deals with complexity
cpu = CPU()
memory = Memory()
disk = HardDrive()

cpu.freeze()
memory.load(BOOT_ADDRESS, disk.read(BOOT_SECTOR, SECTOR_SIZE))
cpu.execute()

# WITH Facade - simple interface
computer = ComputerFacade()
computer.start()  # All complexity hidden!
```

---

## 1. Basic Facade Pattern

```python
# Complex subsystem classes
class CPU:
    def freeze(self):
        print("CPU: Freezing processor")

    def jump(self, position: int):
        print(f"CPU: Jumping to {position}")

    def execute(self):
        print("CPU: Executing instructions")


class Memory:
    def load(self, position: int, data: str):
        print(f"Memory: Loading data '{data}' at position {position}")


class HardDrive:
    def read(self, sector: int, size: int) -> str:
        print(f"HardDrive: Reading {size} bytes from sector {sector}")
        return "boot_data"


# Facade - provides simple interface
class ComputerFacade:
    """Simplifies computer startup"""

    BOOT_ADDRESS = 0
    BOOT_SECTOR = 0
    SECTOR_SIZE = 1024

    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()

    def start(self):
        """Simple method that hides complex startup process"""
        print("Starting computer...\n")

        self.cpu.freeze()
        self.memory.load(
            self.BOOT_ADDRESS,
            self.hard_drive.read(self.BOOT_SECTOR, self.SECTOR_SIZE)
        )
        self.cpu.jump(self.BOOT_ADDRESS)
        self.cpu.execute()

        print("\nComputer started successfully!")


# Usage - client code is simple
computer = ComputerFacade()
computer.start()

# Output:
# Starting computer...
# CPU: Freezing processor
# HardDrive: Reading 1024 bytes from sector 0
# Memory: Loading data 'boot_data' at position 0
# CPU: Jumping to 0
# CPU: Executing instructions
# Computer started successfully!
```

---

## 2. Real-World Example: Home Theater System

```python
# Complex subsystem
class Amplifier:
    def on(self):
        print("Amplifier: Powering on")

    def off(self):
        print("Amplifier: Powering off")

    def set_volume(self, level: int):
        print(f"Amplifier: Setting volume to {level}")

    def set_surround_sound(self):
        print("Amplifier: Enabling surround sound")


class DVDPlayer:
    def on(self):
        print("DVD Player: Powering on")

    def off(self):
        print("DVD Player: Powering off")

    def play(self, movie: str):
        print(f"DVD Player: Playing '{movie}'")

    def stop(self):
        print("DVD Player: Stopping playback")


class Projector:
    def on(self):
        print("Projector: Powering on")

    def off(self):
        print("Projector: Powering off")

    def wide_screen_mode(self):
        print("Projector: Setting widescreen mode")


class Lights:
    def dim(self, level: int):
        print(f"Lights: Dimming to {level}%")

    def on(self):
        print("Lights: Turning on")


class Screen:
    def down(self):
        print("Screen: Lowering screen")

    def up(self):
        print("Screen: Raising screen")


# Facade - simplifies the home theater system
class HomeTheaterFacade:
    """Provides simple methods for common operations"""

    def __init__(self):
        self.amplifier = Amplifier()
        self.dvd_player = DVDPlayer()
        self.projector = Projector()
        self.lights = Lights()
        self.screen = Screen()

    def watch_movie(self, movie: str):
        """One method to set up everything for watching a movie"""
        print("=== Getting ready to watch movie ===\n")

        self.lights.dim(10)
        self.screen.down()
        self.projector.on()
        self.projector.wide_screen_mode()
        self.amplifier.on()
        self.amplifier.set_surround_sound()
        self.amplifier.set_volume(50)
        self.dvd_player.on()
        self.dvd_player.play(movie)

        print("\n=== Enjoy your movie! ===")

    def end_movie(self):
        """One method to shut everything down"""
        print("\n=== Shutting down movie theater ===\n")

        self.dvd_player.stop()
        self.dvd_player.off()
        self.amplifier.off()
        self.projector.off()
        self.screen.up()
        self.lights.on()

        print("\n=== Theater shut down complete ===")


# Usage - simple!
home_theater = HomeTheaterFacade()

# Start movie - one simple call
home_theater.watch_movie("The Matrix")

# End movie - one simple call
home_theater.end_movie()
```

---

## 3. Real-World Example: E-commerce Order Processing

```python
from typing import Dict, List


# Complex subsystem - Inventory
class InventorySystem:
    def check_stock(self, product_id: str, quantity: int) -> bool:
        print(f"Inventory: Checking stock for {product_id} (qty: {quantity})")
        return True

    def reserve_items(self, product_id: str, quantity: int) -> str:
        print(f"Inventory: Reserving {quantity} of {product_id}")
        return f"RES-{product_id}"

    def reduce_stock(self, reservation_id: str):
        print(f"Inventory: Reducing stock for {reservation_id}")


# Complex subsystem - Payment
class PaymentGateway:
    def authorize(self, amount: float, card_number: str) -> str:
        print(f"Payment: Authorizing ${amount} on card {card_number[-4:]}")
        return f"AUTH-{card_number[-4:]}"

    def charge(self, auth_id: str, amount: float) -> str:
        print(f"Payment: Charging ${amount} with {auth_id}")
        return f"CHG-{auth_id}"

    def refund(self, charge_id: str):
        print(f"Payment: Refunding {charge_id}")


# Complex subsystem - Shipping
class ShippingService:
    def calculate_shipping(self, weight: float, zip_code: str) -> float:
        print(f"Shipping: Calculating cost for {weight}kg to {zip_code}")
        return 9.99

    def create_label(self, address: Dict) -> str:
        print(f"Shipping: Creating label for {address['zip_code']}")
        return "LABEL-12345"

    def schedule_pickup(self, label_id: str):
        print(f"Shipping: Scheduling pickup for {label_id}")


# Complex subsystem - Notification
class NotificationService:
    def send_email(self, email: str, subject: str, body: str):
        print(f"Notification: Sending email to {email}")

    def send_sms(self, phone: str, message: str):
        print(f"Notification: Sending SMS to {phone}")


# Facade - simplifies order processing
class OrderFacade:
    """Simplifies the entire order process"""

    def __init__(self):
        self.inventory = InventorySystem()
        self.payment = PaymentGateway()
        self.shipping = ShippingService()
        self.notification = NotificationService()

    def place_order(
        self,
        customer: Dict,
        items: List[Dict],
        card_number: str,
        shipping_address: Dict
    ) -> Dict:
        """
        One method to handle entire order process.
        Hides all the complexity of multiple subsystems.
        """
        print("=== Processing Order ===\n")

        try:
            # Step 1: Check inventory
            for item in items:
                if not self.inventory.check_stock(item['id'], item['quantity']):
                    raise Exception(f"Out of stock: {item['id']}")

            # Step 2: Calculate total
            item_total = sum(item['price'] * item['quantity'] for item in items)
            shipping_cost = self.shipping.calculate_shipping(
                weight=5.0,
                zip_code=shipping_address['zip_code']
            )
            total = item_total + shipping_cost

            # Step 3: Process payment
            auth_id = self.payment.authorize(total, card_number)
            charge_id = self.payment.charge(auth_id, total)

            # Step 4: Reserve inventory
            reservations = []
            for item in items:
                res_id = self.inventory.reserve_items(item['id'], item['quantity'])
                reservations.append(res_id)

            # Step 5: Reduce stock
            for res_id in reservations:
                self.inventory.reduce_stock(res_id)

            # Step 6: Create shipping label
            label_id = self.shipping.create_label(shipping_address)
            self.shipping.schedule_pickup(label_id)

            # Step 7: Send notifications
            self.notification.send_email(
                customer['email'],
                "Order Confirmed",
                f"Your order total: ${total}"
            )
            self.notification.send_sms(
                customer['phone'],
                f"Order confirmed! Tracking: {label_id}"
            )

            print("\n=== Order Completed Successfully ===")

            return {
                'order_id': f"ORD-{charge_id}",
                'total': total,
                'tracking': label_id,
                'status': 'confirmed'
            }

        except Exception as e:
            print(f"\n!!! Order Failed: {e} !!!")
            # Rollback logic would go here
            return {'status': 'failed', 'error': str(e)}


# Usage - one simple call handles everything!
order_facade = OrderFacade()

customer = {
    'email': 'customer@example.com',
    'phone': '+1234567890'
}

items = [
    {'id': 'PROD-001', 'price': 29.99, 'quantity': 2},
    {'id': 'PROD-002', 'price': 49.99, 'quantity': 1}
]

shipping_address = {
    'street': '123 Main St',
    'city': 'Boston',
    'zip_code': '02101'
}

result = order_facade.place_order(
    customer=customer,
    items=items,
    card_number='4111111111111111',
    shipping_address=shipping_address
)

print(f"\nOrder Result: {result}")
```

---

## 4. Real-World Example: Video Conversion System

```python
from typing import Optional


# Complex subsystem - Video Codec
class VideoCodec:
    def decode(self, filename: str) -> bytes:
        print(f"VideoCodec: Decoding {filename}")
        return b"video_data"

    def encode(self, data: bytes, format: str) -> bytes:
        print(f"VideoCodec: Encoding to {format}")
        return b"encoded_data"


# Complex subsystem - Audio Mixer
class AudioMixer:
    def extract_audio(self, video_data: bytes) -> bytes:
        print("AudioMixer: Extracting audio")
        return b"audio_data"

    def adjust_volume(self, audio: bytes, level: float) -> bytes:
        print(f"AudioMixer: Adjusting volume to {level}")
        return audio

    def mix_audio(self, audio1: bytes, audio2: bytes) -> bytes:
        print("AudioMixer: Mixing audio tracks")
        return b"mixed_audio"


# Complex subsystem - BitRate Reader
class BitrateReader:
    def read(self, filename: str) -> str:
        print(f"BitrateReader: Reading {filename}")
        return "mpeg4"

    def convert(self, data: bytes, codec: str) -> bytes:
        print(f"BitrateReader: Converting to {codec}")
        return data


# Complex subsystem - File System
class VideoFile:
    def __init__(self, filename: str):
        self.filename = filename

    def save(self, data: bytes, filename: str):
        print(f"VideoFile: Saving to {filename}")


# Facade - simplifies video conversion
class VideoConversionFacade:
    """Provides simple methods for video operations"""

    def __init__(self):
        self.codec = VideoCodec()
        self.audio = AudioMixer()
        self.bitrate = BitrateReader()

    def convert_video(
        self,
        input_file: str,
        output_file: str,
        format: str = "mp4"
    ) -> str:
        """
        Simple method to convert video.
        Hides all the complexity of codecs, audio mixing, etc.
        """
        print(f"=== Converting {input_file} to {format} ===\n")

        # Read file
        source_codec = self.bitrate.read(input_file)

        # Decode
        video_data = self.codec.decode(input_file)

        # Extract audio
        audio_data = self.audio.extract_audio(video_data)

        # Adjust audio
        audio_data = self.audio.adjust_volume(audio_data, 1.0)

        # Convert format if needed
        if source_codec != format:
            video_data = self.bitrate.convert(video_data, format)

        # Encode
        final_data = self.codec.encode(video_data, format)

        # Save
        video_file = VideoFile(input_file)
        video_file.save(final_data, output_file)

        print(f"\n=== Conversion Complete: {output_file} ===")
        return output_file


# Usage - simple!
converter = VideoConversionFacade()
converter.convert_video("movie.avi", "movie.mp4", format="mp4")

# All the complex subsystem interactions are hidden!
```

---

## 5. Facade with Additional Facade Methods

```python
class DatabaseFacade:
    """Facade for complex database operations"""

    def __init__(self):
        self.connection_pool = ConnectionPool()
        self.query_builder = QueryBuilder()
        self.cache = CacheSystem()
        self.logger = Logger()

    def get_user_by_id(self, user_id: int) -> dict:
        """Simple method - hides connection, caching, logging"""
        # Check cache
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            self.logger.log(f"Cache hit for user {user_id}")
            return cached

        # Build query
        query = self.query_builder.select("users").where("id", user_id).build()

        # Execute
        conn = self.connection_pool.get_connection()
        result = conn.execute(query)
        conn.release()

        # Cache result
        self.cache.set(f"user:{user_id}", result)
        self.logger.log(f"Fetched user {user_id} from database")

        return result

    def create_user(self, name: str, email: str) -> int:
        """Another simple method"""
        query = self.query_builder.insert("users", {
            "name": name,
            "email": email
        }).build()

        conn = self.connection_pool.get_connection()
        user_id = conn.execute(query)
        conn.release()

        self.cache.invalidate(f"user:{user_id}")
        self.logger.log(f"Created user {user_id}")

        return user_id
```

---

## 6. When to Use Facade Pattern

### ✅ Use When:

1. **Complex subsystem**
   ```python
   # Many classes and complex interactions
   facade.simple_method()  # Instead of calling 10 classes
   ```

2. **Multiple subsystems**
   ```python
   # Coordinate multiple subsystems
   order_facade.place_order()  # Handles inventory, payment, shipping
   ```

3. **Layer separation**
   ```python
   # Create layers in application
   api_facade = APIFacade(business_layer, data_layer)
   ```

4. **Simplify common tasks**
   ```python
   # Make common operations easy
   computer.start()  # Instead of 7 manual steps
   ```

### ❌ Don't Use When:

1. **Subsystem is already simple** - no need for extra layer
2. **Need full control** - facade hides options
3. **One-to-one wrapping** - that's just delegation, not facade

---

## 7. Facade vs Other Patterns

| Pattern | Purpose | Key Difference |
|---------|---------|----------------|
| **Facade** | Simplify interface | Hides complexity |
| **Adapter** | Make compatible | Changes interface |
| **Decorator** | Add behavior | Wraps single object |
| **Proxy** | Control access | Same interface |

```python
# Facade - simplifies
facade.simple_method()  # Calls multiple subsystems

# Adapter - changes interface
adapter.new_method()  # Maps to old_method()

# Decorator - adds behavior
decorator.method()  # Adds behavior, calls wrapped.method()

# Proxy - controls
proxy.method()  # Checks access, calls real.method()
```

---

## 8. Advanced: Facade with Factory

```python
class ReportFacade:
    """Facade that also acts as factory"""

    def __init__(self):
        self.data_source = DataSource()
        self.formatter = ReportFormatter()
        self.exporter = ReportExporter()

    def generate_sales_report(self, start_date, end_date) -> str:
        """Generate and export sales report"""
        # Fetch data
        data = self.data_source.get_sales(start_date, end_date)

        # Format
        formatted = self.formatter.format_sales(data)

        # Export
        filename = f"sales_{start_date}_{end_date}.pdf"
        self.exporter.export_pdf(formatted, filename)

        return filename

    def generate_inventory_report(self) -> str:
        """Generate and export inventory report"""
        data = self.data_source.get_inventory()
        formatted = self.formatter.format_inventory(data)
        filename = "inventory_report.pdf"
        self.exporter.export_pdf(formatted, filename)
        return filename

    def generate_custom_report(self, query, format="pdf") -> str:
        """Custom report generation"""
        data = self.data_source.execute(query)
        formatted = self.formatter.format_generic(data)

        if format == "pdf":
            filename = "custom_report.pdf"
            self.exporter.export_pdf(formatted, filename)
        elif format == "excel":
            filename = "custom_report.xlsx"
            self.exporter.export_excel(formatted, filename)

        return filename
```

---

## 9. Interview Tips

### Common Questions

**Q: "What's the difference between Facade and Adapter?"**
- **Facade**: Simplifies complex subsystem (new simple interface)
- **Adapter**: Makes incompatible interfaces work together (converts interface)

**Q: "Can clients still access subsystem directly?"**
- Yes! Facade doesn't prevent direct access
- Provides convenient interface for common tasks
- Clients can bypass facade if they need fine-grained control

**Q: "Is Facade a Singleton?"**
- Often yes, but not required
- One facade instance usually sufficient
- Can have multiple facades for different subsystems

**Q: "Implement a facade for a complex system"**
```python
class SystemFacade:
    def __init__(self):
        self.subsystem1 = Subsystem1()
        self.subsystem2 = Subsystem2()
        self.subsystem3 = Subsystem3()

    def simple_operation(self):
        self.subsystem1.operation1()
        self.subsystem2.operation2()
        self.subsystem3.operation3()
```

### Best Practices

✅ Keep facade thin - don't add business logic
✅ Provide simple methods for common tasks
✅ Allow direct subsystem access when needed
✅ One facade per subsystem or layer
✅ Document what complexity is being hidden

### Red Flags

❌ Facade with complex logic (becomes god object)
❌ Too many facades (over-abstraction)
❌ Facade preventing necessary subsystem access
❌ Facade that just delegates one-to-one

---

## Quick Reference

```python
# Subsystems (complex)
class Subsystem1:
    def operation1(self):
        pass

class Subsystem2:
    def operation2(self):
        pass

# Facade (simple interface)
class Facade:
    def __init__(self):
        self.subsystem1 = Subsystem1()
        self.subsystem2 = Subsystem2()

    def simple_operation(self):
        """Hides complexity"""
        self.subsystem1.operation1()
        self.subsystem2.operation2()

# Usage
facade = Facade()
facade.simple_operation()  # One call does everything!
```

---

**Related Patterns:**
- [Adapter Pattern](./adapter.md) - Makes interfaces compatible
- [Decorator Pattern](./decorator.md) - Adds responsibilities
- [Proxy Pattern](./proxy.md) - Controls access
- [Mediator Pattern](./mediator.md) - Coordinates objects

**Back to:** [Design Patterns](./README.md)
