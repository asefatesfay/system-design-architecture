# Ambassador Pattern - Quick Start

## Installation

```bash
# Navigate to the pattern directory
cd design-patterns/01-ambassador

# Install dependencies
pip install -r requirements.txt
```

## Running the Demo

### Step 1: Start Mock API Server

```bash
# Terminal 1
python demo/mock_api.py
```

This starts a mock API server on `http://localhost:8080` that simulates an unreliable external API with:
- 30% random failures (500 errors)
- 20% slow responses (2s delay)
- Multiple endpoints (payment, shipping, email)

### Step 2: Run the Comparison Demo

```bash
# Terminal 2
python demo/run_demo.py
```

This runs a side-by-side comparison showing:
1. ❌ **Without Ambassador**: Code with duplicate retry logic, inconsistent behavior
2. ✅ **With Ambassador**: Clean code with centralized connectivity handling

### Step 3: Run Benchmarks

```bash
# Terminal 2 (with API server still running)
python benchmarks/benchmark.py
```

This runs 50 iterations of each approach and compares:
- Total execution time
- Average latency per request
- Success rate
- Memory usage
- Retry efficiency

## Example Output

```
╔══════════════════════════════════════════════════════════════════╗
║                     FINAL COMPARISON                              ║
╚══════════════════════════════════════════════════════════════════╝

┌─────────────────────────┬──────────────┬──────────────┐
│ Metric                  │ Without      │ With         │
├─────────────────────────┼──────────────┼──────────────┤
│ Code Duplication        │ ❌ High      │ ✅ None      │
│ Consistency             │ ❌ Low       │ ✅ High      │
│ Maintainability         │ ❌ Hard      │ ✅ Easy      │
│ Circuit Breaker         │ ❌ No        │ ✅ Yes       │
│ Rate Limiting           │ ❌ No        │ ✅ Yes       │
└─────────────────────────┴──────────────┴──────────────┘
```

## Code Examples

### Without Ambassador (Duplicate Code)

```python
class PaymentService:
    def process_payment(self, amount, currency):
        # Manual retry logic
        for attempt in range(3):
            try:
                response = requests.post(f"{self.api_url}/charge",
                                       json={"amount": amount})
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                elif response.status_code >= 500:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            except requests.exceptions.Timeout:
                time.sleep(2 ** attempt)
                continue
        return {"success": False}
```

### With Ambassador (Clean Code)

```python
class PaymentService:
    def __init__(self, ambassador: APIAmbassador):
        self.ambassador = ambassador

    def process_payment(self, amount, currency):
        # All retry/logging/monitoring handled by Ambassador!
        return self.ambassador.request(
            method="POST",
            endpoint="/charge",
            data={"amount": amount, "currency": currency}
        )
```

## Key Features Demonstrated

### 🔄 Automatic Retries
- Exponential backoff (1s, 2s, 4s)
- Configurable retry count
- Smart retry (don't retry 4xx errors)

### 🛡️ Circuit Breaker
- Prevents cascading failures
- Opens after threshold failures
- Auto-recovery with half-open state

### 📊 Centralized Metrics
- Success/failure rates
- Average latency
- Total retries
- Circuit breaker state

### ⚡ Rate Limiting
- Token bucket algorithm
- Prevents API bans
- Configurable rate

### 📝 Unified Logging
- All requests logged consistently
- Request/response correlation
- Error tracking

## File Structure

```
01-ambassador/
├── README.md                   # Detailed pattern documentation
├── QUICKSTART.md              # This file
├── requirements.txt           # Python dependencies
│
├── without_pattern/           # ❌ Problem demonstration
│   └── main.py               # Duplicate retry logic
│
├── with_pattern/             # ✅ Solution with Ambassador
│   └── main.py               # Clean code with Ambassador
│
├── demo/                     # Interactive demos
│   ├── mock_api.py          # Mock API server
│   └── run_demo.py          # Comparison demo
│
└── benchmarks/               # Performance testing
    └── benchmark.py         # Benchmark script
```

## Next Steps

1. **Read the full documentation**: [README.md](./README.md)
2. **Explore other patterns**: [../README.md](../README.md)
3. **Try modifying the Ambassador**: Add custom features like:
   - Custom headers injection
   - Request/response transformation
   - Advanced caching
   - Metrics export (Prometheus, etc.)

## Common Issues

### API Server Not Running
```
❌ ERROR: Mock API server not running!
```
**Solution**: Start the mock API server first: `python demo/mock_api.py`

### Port Already in Use
```
Address already in use
```
**Solution**: Kill the process using port 8080 or change the port in the code

### Import Errors
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: Install dependencies: `pip install -r requirements.txt`

## Learn More

- [Microsoft Azure Ambassador Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/ambassador)
- [Sidecar Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar)
- [Circuit Breaker Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
