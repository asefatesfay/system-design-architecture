# Quick Start Guide

Get up and running in 5 minutes!

## ✅ What's Already Set Up

Your project structure is ready:
```
multi-agent-travel-system/
├── src/multi_agent_travel_system/
│   ├── __init__.py          ✓ Package initialization
│   ├── main.py              ✓ Step 1 code (ready to run!)
│   ├── config.py            ✓ Configuration management
│   ├── agents/              ✓ (empty, will add agents here)
│   ├── tools/               ✓ (empty, will add tools here)
│   ├── models/              ✓ (empty, will add data models)
│   └── utils/               ✓ (empty, will add utilities)
├── tests/                   ✓ (for tests)
├── .env.example             ✓ Example configuration
├── .gitignore               ✓ Git ignore rules
├── pyproject.toml           ✓ Dependencies
├── README.md                ✓ Project overview
├── TUTORIAL.md              ✓ Step-by-step guide
├── PROJECT-STRUCTURE.md     ✓ Structure documentation
└── QUICKSTART.md            ✓ This file!
```

## 🚀 Run Step 1 Right Now

### 1. Set AWS Profile
```bash
export AWS_PROFILE=admin-user
```

### 2. Navigate to Project
```bash
cd ai-corner/aws-agentcore/multi-agent-travel-system
```

### 3. Run the Application
```bash
uv run python -m multi_agent_travel_system.main
```

You should see:
```
🌍 Multi-Agent Travel System
==================================================
✓ AWS Profile: admin-user
✓ AWS Region: us-west-2
✓ Bedrock Model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
✓ Travel Agent created
==================================================
🚀 Server starting on http://localhost:8080
==================================================
```

### 4. Test It (in another terminal)
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to visit Paris"}' \
  | jq
```

Expected response:
```json
{
  "response": "Great! Paris is a wonderful destination. To help you plan your trip, I need a few more details:\n\n1. When are you planning to travel?\n2. How many days will you be staying?\n3. How many people will be traveling?\n4. What's your approximate budget?\n5. What are your main interests? (art, food, history, etc.)"
}
```

## 📚 What to Do Next

### Option 1: Follow the Tutorial
Open [TUTORIAL.md](TUTORIAL.md) and go through Steps 1-7 to build the complete system.

Each step teaches you one concept:
- **Step 1**: Basic agent (you just ran this!)
- **Step 2**: Add flight search tools
- **Step 3**: Multiple agents working together
- **Step 4**: Shared memory
- **Steps 5-7**: Complete the system

### Option 2: Understand the Structure
Read [PROJECT-STRUCTURE.md](PROJECT-STRUCTURE.md) to understand:
- Where each file goes
- How imports work
- How the structure grows with each tutorial step

### Option 3: Read the Overview
Check [README.md](README.md) for the big picture of what you're building.

## 🛠️ How to Add New Features

### Adding a Tool (Step 2)
Create `src/multi_agent_travel_system/tools/flight_tools.py`:
```python
def search_flights(origin: str, destination: str, date: str):
    """Search for flights"""
    # Your implementation
    pass
```

Then use it in `main.py`:
```python
from .tools.flight_tools import search_flights

travel_agent = Agent(
    model=config.BEDROCK_MODEL,
    tools=[search_flights]  # Add your tool here
)
```

### Adding an Agent (Step 3)
Create `src/multi_agent_travel_system/agents/flight_agent.py`:
```python
from strands import Agent
from ..config import config
from ..tools.flight_tools import search_flights

def create_flight_agent():
    """Create specialized flight agent"""
    return Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="You are a flight specialist...",
        tools=[search_flights]
    )
```

Then use it in `main.py`:
```python
from .agents.flight_agent import create_flight_agent

flight_agent = create_flight_agent()
```

## 📁 Current Project State

You're at **Step 1** with:
- ✅ Basic application structure
- ✅ Configuration management
- ✅ Single travel agent
- ✅ API endpoint
- ⏳ Tools (coming in Step 2)
- ⏳ Multiple agents (coming in Step 3)
- ⏳ Shared memory (coming in Step 4)

## 🐛 Troubleshooting

### "AWS_PROFILE not set"
```bash
export AWS_PROFILE=admin-user
```

### "Module not found: multi_agent_travel_system"
Make sure you're in the project root:
```bash
cd ai-corner/aws-agentcore/multi-agent-travel-system
uv run python -m multi_agent_travel_system.main
```

### "No module named 'bedrock_agentcore'"
Install dependencies:
```bash
uv sync
```

### Want to use a different AWS profile?
Edit `.env.example`, copy it to `.env`, and update:
```bash
cp .env.example .env
# Edit .env with your settings
```

## 🎯 Recommended Learning Path

1. **Day 1**: Run Step 1 (basic agent) ✓ You're here!
2. **Day 2**: Add flight search tools (Step 2)
3. **Day 3**: Create multiple agents (Step 3)
4. **Day 4**: Add shared memory (Step 4)
5. **Day 5**: Add hotel agent (Step 5)
6. **Day 6**: Add budget tracking (Step 6)
7. **Day 7**: Complete system (Step 7)

Take your time with each step. Understand before moving forward!

## 💡 Tips

1. **Test after each change**: Don't wait until the end
2. **Read the code comments**: They explain what's happening
3. **Experiment**: Try changing prompts, adding features
4. **Keep it simple**: Don't overcomplicate at first
5. **Ask questions**: If stuck, that's normal! Debug and learn

## 🎉 You're Ready!

The structure is set up. The Step 1 code is working. Now follow the tutorial at your own pace.

**Start here**: Open [TUTORIAL.md](TUTORIAL.md) and read Step 1 to understand what you just ran!
