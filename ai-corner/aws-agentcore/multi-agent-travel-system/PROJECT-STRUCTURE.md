# Project Structure Guide

How to organize your multi-agent travel system as you build through the tutorial.

## Final Structure (What You're Building Towards)

```
multi-agent-travel-system/
├── src/
│   └── multi_agent_travel_system/
│       ├── __init__.py
│       ├── main.py                    # Application entry point
│       ├── config.py                  # Configuration (AWS, models, etc.)
│       │
│       ├── agents/                    # All agent definitions
│       │   ├── __init__.py
│       │   ├── coordinator.py         # Main coordinator agent
│       │   ├── flight_agent.py        # Flight specialist
│       │   ├── hotel_agent.py         # Hotel specialist
│       │   ├── activity_agent.py      # Activity specialist
│       │   └── budget_agent.py        # Budget tracker
│       │
│       ├── tools/                     # Tools that agents use
│       │   ├── __init__.py
│       │   ├── flight_tools.py        # Flight search/booking
│       │   ├── hotel_tools.py         # Hotel search/booking
│       │   ├── activity_tools.py      # Activity search
│       │   └── budget_tools.py        # Budget calculations
│       │
│       ├── models/                    # Data models/schemas
│       │   ├── __init__.py
│       │   ├── trip.py                # Trip data structure
│       │   ├── booking.py             # Booking data structure
│       │   └── message.py             # Agent communication
│       │
│       └── utils/                     # Utilities
│           ├── __init__.py
│           ├── memory.py              # Shared memory/state
│           └── logger.py              # Custom logging
│
├── tests/                             # Tests
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_integration.py
│
├── .env.example                       # Example environment variables
├── .gitignore
├── pyproject.toml                     # Dependencies
├── README.md                          # Overview
├── TUTORIAL.md                        # Step-by-step guide
├── PROJECT-STRUCTURE.md              # This file
└── uv.lock
```

## Evolution Through Tutorial Steps

### Step 1: Single Agent
```
src/multi_agent_travel_system/
├── __init__.py
├── main.py          # Simple agent, no tools yet
└── config.py        # AWS configuration
```

### Step 2: Add Tools
```
src/multi_agent_travel_system/
├── __init__.py
├── main.py
├── config.py
└── tools/
    ├── __init__.py
    └── flight_tools.py    # Flight search functions
```

### Step 3: Multiple Agents
```
src/multi_agent_travel_system/
├── __init__.py
├── main.py
├── config.py
├── agents/
│   ├── __init__.py
│   ├── coordinator.py     # Coordinator
│   └── flight_agent.py    # Flight specialist
└── tools/
    ├── __init__.py
    └── flight_tools.py
```

### Step 4: Add Memory
```
src/multi_agent_travel_system/
├── __init__.py
├── main.py
├── config.py
├── agents/
│   ├── __init__.py
│   ├── coordinator.py
│   └── flight_agent.py
├── tools/
│   ├── __init__.py
│   └── flight_tools.py
├── models/
│   ├── __init__.py
│   └── trip.py           # Trip data model
└── utils/
    ├── __init__.py
    └── memory.py         # Shared state
```

### Steps 5-7: Complete System
(Full structure shown above)

## Setting Up the Structure

### 1. Create the Base Directories

```bash
cd ai-corner/aws-agentcore/multi-agent-travel-system

# Create all directories at once
mkdir -p src/multi_agent_travel_system/{agents,tools,models,utils}
mkdir -p tests

# Create __init__.py files
touch src/multi_agent_travel_system/__init__.py
touch src/multi_agent_travel_system/agents/__init__.py
touch src/multi_agent_travel_system/tools/__init__.py
touch src/multi_agent_travel_system/models/__init__.py
touch src/multi_agent_travel_system/utils/__init__.py
touch tests/__init__.py

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
EOF

# Create .env.example
cat > .env.example << 'EOF'
# AWS Configuration
AWS_PROFILE=admin-user
AWS_DEFAULT_REGION=us-west-2

# Bedrock Model
BEDROCK_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Optional: Real API keys (when you're ready)
# AMADEUS_API_KEY=your_key_here
# BOOKING_API_KEY=your_key_here
# GETYOURGUIDE_API_KEY=your_key_here
EOF
```

### 2. Create config.py (Configuration Management)

```bash
cat > src/multi_agent_travel_system/config.py << 'EOF'
"""Application configuration"""
import os
from typing import Optional

class Config:
    """Application configuration"""

    # AWS Configuration
    AWS_PROFILE: str = os.getenv("AWS_PROFILE", "admin-user")
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-west-2")

    # Bedrock Model
    BEDROCK_MODEL: str = os.getenv(
        "BEDROCK_MODEL",
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    )

    # Optional API Keys
    AMADEUS_API_KEY: Optional[str] = os.getenv("AMADEUS_API_KEY")
    BOOKING_API_KEY: Optional[str] = os.getenv("BOOKING_API_KEY")
    GETYOURGUIDE_API_KEY: Optional[str] = os.getenv("GETYOURGUIDE_API_KEY")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8080"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if "AWS_PROFILE" not in os.environ:
            raise ValueError("AWS_PROFILE environment variable is required")

# Create global config instance
config = Config()
EOF
```

## File Responsibilities

### `main.py` - Application Entry Point
```python
"""
Main application entry point.

Responsibilities:
- Initialize BedrockAgentCoreApp
- Set up AWS configuration
- Create and wire agents
- Define API endpoints
- Start the server
"""
```

### `config.py` - Configuration
```python
"""
Application configuration.

Responsibilities:
- Load environment variables
- Provide configuration values
- Validate required settings
- Default values
"""
```

### `agents/*.py` - Agent Definitions
```python
"""
Each file defines one specialized agent.

Responsibilities:
- Create agent with specific system prompt
- Register tools the agent can use
- Define agent's specialty/purpose
- Export agent factory function
"""
```

### `tools/*.py` - Tool Implementations
```python
"""
Each file contains related tools.

Responsibilities:
- Implement tool functions
- Handle API calls (real or mock)
- Return structured data
- Document tool parameters
"""
```

### `models/*.py` - Data Models
```python
"""
Data structures used across the application.

Responsibilities:
- Define data schemas
- Type hints and validation
- Data transformation helpers
- Serialization/deserialization
"""
```

### `utils/*.py` - Utilities
```python
"""
Shared utilities and helpers.

Responsibilities:
- Shared memory/state management
- Logging helpers
- Common functions used across modules
"""
```

## Import Patterns

### Importing from Tools
```python
# In agents/flight_agent.py
from multi_agent_travel_system.tools.flight_tools import (
    search_flights,
    get_flight_details
)
```

### Importing Agents
```python
# In main.py
from multi_agent_travel_system.agents.coordinator import create_coordinator
from multi_agent_travel_system.agents.flight_agent import create_flight_agent
```

### Importing Models
```python
# In agents/coordinator.py
from multi_agent_travel_system.models.trip import Trip
from multi_agent_travel_system.models.message import AgentMessage
```

### Importing Utils
```python
# In main.py
from multi_agent_travel_system.utils.memory import trip_memory
from multi_agent_travel_system.config import config
```

## Package Exports

### `agents/__init__.py`
```python
"""Agent exports"""
from .coordinator import create_coordinator
from .flight_agent import create_flight_agent
from .hotel_agent import create_hotel_agent
from .activity_agent import create_activity_agent
from .budget_agent import create_budget_agent

__all__ = [
    "create_coordinator",
    "create_flight_agent",
    "create_hotel_agent",
    "create_activity_agent",
    "create_budget_agent",
]
```

### `tools/__init__.py`
```python
"""Tool exports"""
from .flight_tools import search_flights, get_flight_details, book_flight
from .hotel_tools import search_hotels, get_hotel_details, book_hotel
from .activity_tools import search_activities, get_activity_details
from .budget_tools import track_expense, get_budget_summary

__all__ = [
    "search_flights",
    "get_flight_details",
    "book_flight",
    "search_hotels",
    "get_hotel_details",
    "book_hotel",
    "search_activities",
    "get_activity_details",
    "track_expense",
    "get_budget_summary",
]
```

## Running the Application

### Development
```bash
# From project root
cd ai-corner/aws-agentcore/multi-agent-travel-system

# Set environment
export AWS_PROFILE=admin-user

# Run the app
uv run python -m multi_agent_travel_system.main

# Or use the installed script
uv run multi-agent-travel-system
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agents.py

# Run with coverage
uv run pytest --cov=multi_agent_travel_system
```

## Best Practices

### 1. Keep Files Focused
- Each file should have a single, clear responsibility
- Agents go in `agents/`, tools in `tools/`
- Don't mix concerns

### 2. Use Type Hints
```python
def search_flights(
    origin: str,
    destination: str,
    date: str,
    passengers: int = 1
) -> list[dict]:
    """Type hints make code clearer"""
    pass
```

### 3. Document Everything
```python
def search_flights(origin: str, destination: str, date: str):
    """
    Search for available flights.

    Args:
        origin: Origin airport code (e.g., 'JFK')
        destination: Destination airport code (e.g., 'CDG')
        date: Departure date in YYYY-MM-DD format

    Returns:
        List of flight dictionaries with pricing and schedule

    Example:
        >>> search_flights('JFK', 'CDG', '2024-03-15')
        [{'id': 'FL001', 'price': 450, ...}]
    """
    pass
```

### 4. Use Relative Imports Within Package
```python
# In agents/coordinator.py
from ..tools.flight_tools import search_flights
from ..utils.memory import trip_memory
from ..config import config
```

### 5. Mock Data During Development
```python
# tools/flight_tools.py
def search_flights(origin, destination, date, passengers=1):
    # Use mock data while learning
    if config.DEBUG or not config.AMADEUS_API_KEY:
        return _mock_flight_data()
    else:
        return _real_api_call()
```

## Growing the Application

As you progress through the tutorial:

1. **Step 1**: Create `main.py` and `config.py`
2. **Step 2**: Add `tools/flight_tools.py`
3. **Step 3**: Add `agents/coordinator.py` and `agents/flight_agent.py`
4. **Step 4**: Add `models/trip.py` and `utils/memory.py`
5. **Steps 5-7**: Add remaining agents and tools

Each step builds on the previous structure without breaking anything!

## Quick Setup Script

Run this to create the entire structure:

```bash
#!/bin/bash
# setup-structure.sh

cd "$(dirname "$0")"

# Create directories
mkdir -p src/multi_agent_travel_system/{agents,tools,models,utils}
mkdir -p tests

# Create __init__.py files
for dir in src/multi_agent_travel_system src/multi_agent_travel_system/{agents,tools,models,utils} tests; do
    touch "$dir/__init__.py"
done

# Create .gitignore and .env.example (as shown above)

echo "✅ Project structure created!"
echo "Next: Start with TUTORIAL.md Step 1"
```

Save this as `setup-structure.sh`, make it executable, and run it:
```bash
chmod +x setup-structure.sh
./setup-structure.sh
```
