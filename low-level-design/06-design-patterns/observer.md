# Observer Pattern

## Overview

**Observer Pattern** defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically.

**Type**: Behavioral Pattern
**Interview Frequency**: ⭐⭐⭐ VERY HIGH
**Also Known As**: Publish-Subscribe, Event-Subscriber, Listener

> **🌍 Multi-Language Note:** Examples use Python. For other languages:
> - [Language Comparison Guide](../lld-coding/multi-language/LANGUAGE-COMPARISON.md)
> - [Multi-Language Interview Examples](../COMPLETE-INTERVIEW-WALKTHROUGHS-MULTILANG.md)

## When to Use

- One object change should notify multiple other objects
- You want loose coupling between objects
- You need a publish-subscribe mechanism
- Multiple objects need to react to events

## Real-World Examples

- Newsletter subscriptions (one publisher, many subscribers)
- Social media notifications (one post, many followers notified)
- Stock price updates (one stock, many investors watching)
- Event handling in UI (button click notifies multiple listeners)
- Weather station (one station, multiple displays)

## Structure

```
Subject (Observable)
  ├── attach(observer)
  ├── detach(observer)
  └── notify()
       ↓
Observer interface
  ├── ConcreteObserverA
  ├── ConcreteObserverB
  └── ConcreteObserverC
```

## Implementation

### Basic Example: Newsletter System

```python
from abc import ABC, abstractmethod
from typing import List

# Observer Interface
class Observer(ABC):
    @abstractmethod
    def update(self, message: str):
        pass

# Concrete Observers
class EmailSubscriber(Observer):
    def __init__(self, email: str):
        self.email = email

    def update(self, message: str):
        print(f"📧 Email sent to {self.email}: {message}")

class SMSSubscriber(Observer):
    def __init__(self, phone: str):
        self.phone = phone

    def update(self, message: str):
        print(f"📱 SMS sent to {phone}: {message}")

class PushNotificationSubscriber(Observer):
    def __init__(self, device_id: str):
        self.device_id = device_id

    def update(self, message: str):
        print(f"🔔 Push notification to {self.device_id}: {message}")

# Subject (Observable)
class Newsletter:
    def __init__(self, name: str):
        self.name = name
        self._subscribers: List[Observer] = []

    def subscribe(self, observer: Observer):
        """Add a subscriber"""
        if observer not in self._subscribers:
            self._subscribers.append(observer)
            print(f"✓ New subscriber added to {self.name}")

    def unsubscribe(self, observer: Observer):
        """Remove a subscriber"""
        if observer in self._subscribers:
            self._subscribers.remove(observer)
            print(f"✓ Subscriber removed from {self.name}")

    def notify(self, message: str):
        """Notify all subscribers"""
        print(f"\n📢 {self.name} publishing: {message}")
        for subscriber in self._subscribers:
            subscriber.update(message)

    def publish_article(self, title: str, content: str):
        """Publish new content"""
        message = f"New article: {title}"
        self.notify(message)

# Usage
newsletter = Newsletter("Tech Daily")

# Create subscribers
email1 = EmailSubscriber("alice@example.com")
email2 = EmailSubscriber("bob@example.com")
sms1 = SMSSubscriber("+1-555-1234")
push1 = PushNotificationSubscriber("device-123")

# Subscribe
newsletter.subscribe(email1)
newsletter.subscribe(email2)
newsletter.subscribe(sms1)
newsletter.subscribe(push1)

# Publish content - all subscribers notified
newsletter.publish_article("Python 3.12 Released", "Exciting new features...")

print("\n" + "="*50)

# Unsubscribe one
newsletter.unsubscribe(sms1)

# Publish again - one less subscriber
newsletter.publish_article("AI Breakthrough", "New model achieves...")
```

**Output**:
```
✓ New subscriber added to Tech Daily
✓ New subscriber added to Tech Daily
✓ New subscriber added to Tech Daily
✓ New subscriber added to Tech Daily

📢 Tech Daily publishing: New article: Python 3.12 Released
📧 Email sent to alice@example.com: New article: Python 3.12 Released
📧 Email sent to bob@example.com: New article: Python 3.12 Released
📱 SMS sent to +1-555-1234: New article: Python 3.12 Released
🔔 Push notification to device-123: New article: Python 3.12 Released

==================================================
✓ Subscriber removed from Tech Daily

📢 Tech Daily publishing: New article: AI Breakthrough
📧 Email sent to alice@example.com: New article: AI Breakthrough
📧 Email sent to bob@example.com: New article: AI Breakthrough
🔔 Push notification to device-123: New article: AI Breakthrough
```

## Advanced Example: Stock Market

```python
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime

# Observer Interface
class StockObserver(ABC):
    @abstractmethod
    def update(self, stock_symbol: str, price: float):
        pass

# Concrete Observers
class InvestorObserver(StockObserver):
    def __init__(self, name: str, buy_threshold: float, sell_threshold: float):
        self.name = name
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.holdings: Dict[str, int] = {}

    def update(self, stock_symbol: str, price: float):
        if price < self.buy_threshold:
            print(f"👤 {self.name}: BUY signal for {stock_symbol} at ${price}")
            self.holdings[stock_symbol] = self.holdings.get(stock_symbol, 0) + 10
        elif price > self.sell_threshold:
            if stock_symbol in self.holdings and self.holdings[stock_symbol] > 0:
                print(f"👤 {self.name}: SELL signal for {stock_symbol} at ${price}")
                self.holdings[stock_symbol] -= 10

class AlertObserver(StockObserver):
    def __init__(self, alert_price: float, condition: str):
        self.alert_price = alert_price
        self.condition = condition  # "above" or "below"

    def update(self, stock_symbol: str, price: float):
        if self.condition == "above" and price > self.alert_price:
            print(f"🚨 ALERT: {stock_symbol} is above ${self.alert_price} (now ${price})")
        elif self.condition == "below" and price < self.alert_price:
            print(f"🚨 ALERT: {stock_symbol} is below ${self.alert_price} (now ${price})")

class DisplayObserver(StockObserver):
    def __init__(self, display_name: str):
        self.display_name = display_name

    def update(self, stock_symbol: str, price: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"📊 [{self.display_name}] {timestamp} - {stock_symbol}: ${price:.2f}")

# Subject
class Stock:
    def __init__(self, symbol: str, initial_price: float):
        self.symbol = symbol
        self._price = initial_price
        self._observers: List[StockObserver] = []

    def attach(self, observer: StockObserver):
        self._observers.append(observer)

    def detach(self, observer: StockObserver):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self.symbol, self._price)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_price: float):
        if new_price != self._price:
            self._price = new_price
            self.notify()  # Notify all observers of price change

# Usage
apple = Stock("AAPL", 150.0)

# Create different types of observers
investor1 = InvestorObserver("Alice", buy_threshold=145, sell_threshold=160)
investor2 = InvestorObserver("Bob", buy_threshold=140, sell_threshold=165)
alert1 = AlertObserver(alert_price=155, condition="above")
alert2 = AlertObserver(alert_price=145, condition="below")
display1 = DisplayObserver("Trading Dashboard")
display2 = DisplayObserver("Mobile App")

# Attach observers
apple.attach(investor1)
apple.attach(investor2)
apple.attach(alert1)
apple.attach(alert2)
apple.attach(display1)
apple.attach(display2)

# Simulate price changes
print("Initial price: $150")
print("\n" + "="*60)

apple.price = 155  # Price increase
print("\n" + "="*60)

apple.price = 143  # Price drop
print("\n" + "="*60)

apple.price = 161  # Big increase
```

## Real Interview Example: Weather Station

```python
from abc import ABC, abstractmethod
from typing import List

# Observer Interface
class WeatherObserver(ABC):
    @abstractmethod
    def update(self, temperature: float, humidity: float, pressure: float):
        pass

# Concrete Observers
class CurrentConditionsDisplay(WeatherObserver):
    def update(self, temperature: float, humidity: float, pressure: float):
        print(f"📱 Current conditions: {temperature}°F, {humidity}% humidity")

class StatisticsDisplay(WeatherObserver):
    def __init__(self):
        self.temperatures: List[float] = []

    def update(self, temperature: float, humidity: float, pressure: float):
        self.temperatures.append(temperature)
        avg_temp = sum(self.temperatures) / len(self.temperatures)
        max_temp = max(self.temperatures)
        min_temp = min(self.temperatures)
        print(f"📊 Avg/Max/Min temperature: {avg_temp:.1f}/{max_temp:.1f}/{min_temp:.1f}°F")

class ForecastDisplay(WeatherObserver):
    def __init__(self):
        self.last_pressure = 0

    def update(self, temperature: float, humidity: float, pressure: float):
        if pressure > self.last_pressure:
            print(f"🌤️  Forecast: Improving weather!")
        elif pressure < self.last_pressure:
            print(f"🌧️  Forecast: Watch out for rain!")
        else:
            print(f"☁️  Forecast: More of the same")
        self.last_pressure = pressure

# Subject
class WeatherStation:
    def __init__(self):
        self._observers: List[WeatherObserver] = []
        self._temperature = 0
        self._humidity = 0
        self._pressure = 0

    def register_observer(self, observer: WeatherObserver):
        self._observers.append(observer)

    def remove_observer(self, observer: WeatherObserver):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update(self._temperature, self._humidity, self._pressure)

    def set_measurements(self, temperature: float, humidity: float, pressure: float):
        """New measurements arrived"""
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.notify_observers()

# Usage
weather_station = WeatherStation()

# Create displays
current_display = CurrentConditionsDisplay()
stats_display = StatisticsDisplay()
forecast_display = ForecastDisplay()

# Register displays
weather_station.register_observer(current_display)
weather_station.register_observer(stats_display)
weather_station.register_observer(forecast_display)

# Simulate weather changes
print("Weather Update 1:")
weather_station.set_measurements(80, 65, 30.4)

print("\nWeather Update 2:")
weather_station.set_measurements(82, 70, 29.2)

print("\nWeather Update 3:")
weather_station.set_measurements(78, 90, 29.2)
```

## Push vs Pull Model

### Push Model (Data Sent to Observers)
```python
class Subject:
    def notify(self, data):
        for observer in self._observers:
            observer.update(data)  # Push data to observer
```

### Pull Model (Observers Request Data)
```python
class Subject:
    def notify(self):
        for observer in self._observers:
            observer.update(self)  # Observer pulls data from subject

class Observer:
    def update(self, subject):
        data = subject.get_data()  # Pull data from subject
```

## Event-Driven Architecture

```python
from typing import Callable, Dict, List

class EventManager:
    """Advanced observer pattern with event types"""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, listener: Callable):
        """Subscribe to specific event type"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: str, listener: Callable):
        """Unsubscribe from event type"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    def notify(self, event_type: str, data):
        """Notify all listeners of this event type"""
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener(data)

# Usage
events = EventManager()

# Define event handlers
def on_user_registered(data):
    print(f"Send welcome email to {data['email']}")

def on_user_registered_analytics(data):
    print(f"Track user registration: {data['username']}")

def on_order_placed(data):
    print(f"Process order {data['order_id']}")

def on_order_placed_inventory(data):
    print(f"Update inventory for order {data['order_id']}")

def on_order_placed_notification(data):
    print(f"Send order confirmation to {data['email']}")

# Subscribe to events
events.subscribe("user.registered", on_user_registered)
events.subscribe("user.registered", on_user_registered_analytics)
events.subscribe("order.placed", on_order_placed)
events.subscribe("order.placed", on_order_placed_inventory)
events.subscribe("order.placed", on_order_placed_notification)

# Trigger events
print("Event: User Registered")
events.notify("user.registered", {
    "username": "alice",
    "email": "alice@example.com"
})

print("\nEvent: Order Placed")
events.notify("order.placed", {
    "order_id": "ORD-123",
    "email": "alice@example.com"
})
```

## Benefits

✅ **Loose coupling**: Subject and observers are independent
✅ **Dynamic relationships**: Add/remove observers at runtime
✅ **Broadcast communication**: One-to-many notification
✅ **Open/Closed Principle**: Add new observers without modifying subject

## Drawbacks

❌ Observers are notified in random order
❌ Memory leaks if observers not properly unsubscribed
❌ Can cause unexpected cascading updates
❌ Performance issues with many observers

## Observer vs Other Patterns

### Observer vs Mediator
```python
# Observer: One-to-many, direct notification
subject.notify()  # All observers get notified

# Mediator: Many-to-many, centralized communication
mediator.send(message, from, to)  # Mediator coordinates
```

### Observer vs Pub-Sub
```python
# Observer: Subject knows observers directly
subject.attach(observer)

# Pub-Sub: Publisher and subscribers don't know each other
event_bus.subscribe("topic", handler)
event_bus.publish("topic", data)
```

## Interview Questions

**Q: What's the difference between Observer and Pub-Sub?**
A: Observer: Subject knows its observers directly. Pub-Sub: Publishers and subscribers are completely decoupled through an event bus.

**Q: How do you prevent memory leaks?**
A: Always unsubscribe observers when they're done. Use weak references. Implement proper cleanup in destructors.

**Q: When would you use Observer pattern?**
A: When one object's state change should notify multiple dependent objects, like social media notifications or stock price updates.

## Key Takeaways

1. **One-to-many dependency**: One subject, multiple observers
2. **Loose coupling**: Subject doesn't know details about observers
3. **Dynamic subscription**: Add/remove observers at runtime
4. **Automatic updates**: Observers updated automatically
5. **Common in event-driven systems**: UI frameworks, message queues

## Practice Exercise

**Design a Auction System** where:
- Auctioneer is the subject
- Bidders are observers
- When a new bid is placed, all bidders are notified
- Bidders can join/leave auction at any time
- Include automatic bid feature for some bidders

---

**Next Pattern**: [Factory Method →](./factory.md)
