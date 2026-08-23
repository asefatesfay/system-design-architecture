# Troubleshooting Guide

## Tool Registration Error

### Error Message:
```
tool=<<function search_flights at 0x10d137c10>> | unrecognized tool specification
```

### What This Means:
The Strands Agent library doesn't recognize how tools are being passed. This can happen due to:

1. **Missing or incorrect type hints** - Tools must have proper Python type hints
2. **Import issues** - Tools imported incorrectly
3. **Library version mismatch** - Strands library expects a different format

### Solution 1: Verify Type Hints (Current Fix)

Make sure your tool functions have **complete type hints**:

```python
from typing import List, Dict, Any

def search_flights(
    origin: str,              # ✅ Type hint
    destination: str,         # ✅ Type hint
    date: str,               # ✅ Type hint
    passengers: int = 1      # ✅ Type hint with default
) -> List[Dict[str, Any]]:   # ✅ Return type hint
    """
    Complete docstring explaining the function.

    Args:
        origin: Description
        destination: Description
        ...

    Returns:
        Description
    """
    pass
```

### Solution 2: Use Tool Wrapper (If Needed)

If basic functions don't work, wrap them:

```python
from strands.tools import tool

@tool
def search_flights(origin: str, destination: str, date: str, passengers: int = 1):
    """Search for flights"""
    # Implementation
    pass
```

### Solution 3: Start Without Tools (Recommended for Now)

**This is what we've done** - Start with a basic agent without tools:

```python
# Step 1: Basic agent (NO TOOLS)
travel_agent = Agent(
    model=config.BEDROCK_MODEL,
    system_prompt="You are a travel assistant"
    # No tools parameter
)
```

Then add tools in Step 2 once the basic setup works.

### Current Status:

✅ **Working**: Basic agent without tools (Step 1)
⏳ **Next**: Add tools properly in Step 2

### To Add Tools Later:

1. Ensure tool functions have complete type hints
2. Ensure tool functions have detailed docstrings
3. Import tools correctly
4. Pass as list: `tools=[search_flights, get_flight_details]`

### Testing Without Tools:

```bash
# Start the server
uv run python -m multi_agent_travel_system.main

# Test basic functionality
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to visit Paris"}'

# Should work! Agent responds conversationally
```

### Next Steps:

1. ✅ Get Step 1 working (basic agent)
2. ⏳ Debug tool registration for Step 2
3. ⏳ Once tools work, continue with tutorial

## Other Common Issues

### Issue: Module Not Found
```
ModuleNotFoundError: No module named 'multi_agent_travel_system'
```

**Solution**: Make sure you're running from project root:
```bash
cd /path/to/multi-agent-travel-system
uv run python -m multi_agent_travel_system.main
```

### Issue: AWS Profile Not Set
```
ValueError: AWS_PROFILE environment variable is required
```

**Solution**: Set the environment variable:
```bash
export AWS_PROFILE=admin-user
```

### Issue: Import Error from tools
```
ImportError: cannot import name 'search_flights'
```

**Solution**: Check that `tools/__init__.py` exports the function:
```python
# tools/__init__.py
from .flight_tools import search_flights
```

## Need Help?

1. Check [TUTORIAL.md](TUTORIAL.md) for step-by-step guidance
2. Check [IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md) for what's implemented
3. Review error messages carefully - they often tell you exactly what's wrong!
