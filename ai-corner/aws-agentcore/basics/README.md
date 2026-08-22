# AWS Bedrock AgentCore - Basics

A guide to building AI agents with AWS Bedrock AgentCore and Claude models.

## What is AWS Bedrock AgentCore?

AWS Bedrock AgentCore is a framework for building and deploying AI agents on AWS infrastructure. It integrates with:
- **AWS Bedrock**: Amazon's managed service for foundation models
- **Strands Agents**: A library for building AI agents that can take actions (not just chat). Think of it as the "brain" that lets Claude make decisions, call APIs, access databases, run code, use tools, and orchestrate complex multi-step workflows.
- **Claude Models**: Anthropic's Claude models accessible through Bedrock

**Real-world example**: Instead of just a chatbot that answers questions, you can build:
- A **customer service agent** that checks order status in your database, processes refunds, and updates tickets
- A **code assistant** that reads your codebase, runs tests, debugs errors, and commits fixes
- A **travel booking agent** that searches flights, compares prices, books hotels, and sends confirmation emails
- A **data analyst** that queries databases, generates reports, creates visualizations, and sends insights via Slack

The framework provides a simple way to create REST APIs that expose these AI agent capabilities.

## Prerequisites

- Python 3.14+
- AWS Account with Bedrock access
- AWS CLI configured with credentials
- Access to Claude models in AWS Bedrock (model access must be enabled in AWS Console)
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Install dependencies using uv
uv sync

# Or install manually
uv add bedrock-agentcore strands-agents boto3
```

## AWS Configuration

### 1. AWS Credentials

You need AWS credentials configured. This project supports multiple authentication methods:

**Option A: Environment Variable**
```bash
export AWS_PROFILE=your-profile-name
```

**Option B: AWS CLI Configuration**

Your AWS config should be in `~/.aws/config` and `~/.aws/credentials`:

```ini
# ~/.aws/config
[profile your-profile]
region = us-west-2
```

```ini
# ~/.aws/credentials
[your-profile]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

### 2. Enable Bedrock Model Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Model access"
3. Enable access to Anthropic Claude models
4. Wait for approval (usually instant for on-demand models)

### 3. Supported Regions

Bedrock is available in specific regions. Common ones:
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)

## Project Structure

```
basics/
├── main.py              # Main application entry point
├── pyproject.toml       # Project dependencies
├── README.md           # This file
└── .venv/              # Virtual environment (created by uv)
```

## Usage

### Basic Example

```python
import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

# Initialize the application
app = BedrockAgentCoreApp()

# Set AWS configuration
if 'AWS_PROFILE' not in os.environ:
    os.environ['AWS_PROFILE'] = 'your-profile'

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Create an agent with Claude model
agent = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # Cross-region inference profile
)

# Define an endpoint
@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}

# Run the application
if __name__ == "__main__":
    app.run()
```

### Running the Application

```bash
# Run with default profile (defined in code)
uv run main.py

# Run with specific AWS profile
AWS_PROFILE=your-profile uv run main.py

# Run with specific region
AWS_REGION=us-east-1 AWS_PROFILE=your-profile uv run main.py
```

The application starts a local server on `http://localhost:8080`.

### Testing the API

Once the server is running, test it with curl:

```bash
# Basic request
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello! How are you?"}'

# Travel planning example
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Plan a 3-day trip to Goa!"}'

# Pretty print with jq
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}' | jq
```

## Key Concepts

### BedrockAgentCoreApp

The main application class that provides:
- REST API server
- Request routing
- Error handling
- Observability (logging, tracing)

### Agent (from Strands)

The AI agent that:
- Handles conversations with Claude models
- Manages context and memory
- Executes tool calls
- Streams responses

## Core AgentCore Concepts

### 1. Runtime

**What it is**: The execution environment where your agent runs (local, Lambda, ECS, etc.)

**Real-world examples**:
- **Local Development**: Running `uv run main.py` on your laptop for testing
- **AWS Lambda**: Deploy your agent as a serverless function that scales automatically
  ```python
  # Lambda automatically handles requests
  # No need to manage servers
  # Pay only for actual invocations
  ```
- **ECS/Fargate**: Run as a container for long-running agents that need persistent connections
- **EC2**: Full control for specialized hardware requirements (GPUs for local models)

**Use case**: A customer service agent deployed on Lambda that handles 10 requests/day costs pennies, but can instantly scale to 10,000 requests during a sale event.

### 2. Gateway

**What it is**: The entry point that routes requests to your agent and handles API management

**Real-world examples**:
- **API Gateway Integration**:
  ```
  Customer → API Gateway → Lambda (Agent) → Bedrock → Response
  ```
- **Authentication**: Gateway validates API keys before reaching your agent
- **Rate Limiting**: Prevents abuse (e.g., max 100 requests/minute per user)
- **Request Transformation**: Converts webhook payloads to agent-friendly format
  ```python
  # Slack webhook → Gateway transforms → Agent processes
  {"text": "Book meeting"} → {"prompt": "Book meeting", "user_id": "U123"}
  ```

**Use case**: A Slack bot where the Gateway receives Slack events, validates the workspace token, transforms the payload, and routes to your agent.

### 3. Memory

**What it is**: How agents remember context across conversations and sessions

**Real-world examples**:
- **Short-term Memory (Conversation Context)**:
  ```python
  User: "Book a flight to Paris"
  Agent: "When would you like to travel?"
  User: "Next Monday"  # Agent remembers we're booking to Paris
  ```

- **Long-term Memory (DynamoDB/Redis)**:
  ```python
  # Agent remembers user preferences across sessions
  user_preferences = {
      "user_id": "123",
      "preferred_airline": "Delta",
      "seat_preference": "aisle",
      "dietary": "vegetarian"
  }
  # Next time user books, agent suggests Delta aisle seats
  ```

- **Shared Memory (Team Knowledge)**:
  ```python
  # Support agent remembers all past issues for a customer
  agent.recall("What issues has customer #456 reported?")
  # Returns: [printer issue, login problem, billing question]
  ```

**Use case**: A medical assistant that remembers patient allergies, medications, and past visits across multiple appointments.

### 4. Identity

**What it is**: Authentication and authorization - knowing WHO is using the agent and WHAT they can do

**Real-world examples**:
- **User Authentication**:
  ```python
  @app.entrypoint
  def invoke(payload, context):
      user_id = context.identity.user_id
      role = context.identity.role  # "admin", "user", "guest"

      if role == "admin":
          # Can access all data
          return process_admin_request(payload)
      else:
          # Can only access own data
          return process_user_request(payload, user_id)
  ```

- **OAuth/SSO Integration**:
  ```
  User logs in via Google → Token validated → Agent knows user's email, name, permissions
  ```

- **Multi-tenant Isolation**:
  ```python
  # Company A's agent can't access Company B's data
  tenant_id = context.identity.tenant_id
  data = database.query(tenant_id=tenant_id)
  ```

**Use case**: A corporate HR assistant where managers can query all team data, but employees only see their own payroll and vacation info.

### 5. Tools

**What it is**: External capabilities agents can use (APIs, databases, code execution)

**Real-world examples**:
- **Database Query Tool**:
  ```python
  @app.tool
  def get_order_status(order_id: str):
      """Check order status in database"""
      return db.query("SELECT status FROM orders WHERE id = ?", order_id)

  # Agent: "Let me check that order for you..."
  # Agent calls: get_order_status("ORD-123")
  # Agent: "Your order is out for delivery!"
  ```

- **API Integration Tool**:
  ```python
  @app.tool
  def search_flights(origin: str, destination: str, date: str):
      """Search available flights"""
      response = requests.get(f"https://api.flights.com/search", params={...})
      return response.json()
  ```

- **Code Execution Tool**:
  ```python
  @app.tool
  def run_analysis(data: list):
      """Run statistical analysis"""
      import pandas as pd
      df = pd.DataFrame(data)
      return df.describe().to_dict()
  ```

- **Multi-step Tool Chain**:
  ```python
  # Agent orchestrates multiple tools:
  # 1. search_flights("NYC", "LAX", "2024-03-15")
  # 2. check_price_history("NYC-LAX")
  # 3. book_flight(flight_id="FL123")
  # 4. send_confirmation_email(user_email)
  ```

**Use case**: A DevOps agent that uses tools to check server health, query logs, restart services, and post alerts to Slack - all without human intervention.

### 6. Observability

**What it is**: Monitoring, logging, and tracing to understand what your agent is doing

**Real-world examples**:
- **Structured Logging**:
  ```json
  {
    "timestamp": "2024-03-15T10:30:00Z",
    "level": "INFO",
    "message": "Agent invoked",
    "user_id": "user-123",
    "prompt": "Book flight to Paris",
    "duration_ms": 1250,
    "tokens_used": 450,
    "cost": 0.0023
  }
  ```

- **Distributed Tracing** (see the full flow):
  ```
  Request arrives
  ├─ Gateway validates (12ms)
  ├─ Agent receives prompt (5ms)
  ├─ Call Bedrock API (800ms)
  │  └─ Model inference (750ms)
  ├─ Execute tool: search_flights (400ms)
  │  └─ External API call (380ms)
  ├─ Call Bedrock again (600ms)
  └─ Return response (8ms)
  Total: 1825ms
  ```

- **Metrics Dashboard**:
  ```
  - Total requests today: 1,247
  - Average response time: 1.2s
  - Error rate: 0.3%
  - Top tools used: search_flights (402), get_order_status (201)
  - Cost today: $12.34
  ```

- **Error Tracking**:
  ```python
  # When something breaks, you see:
  {
    "error": "ConnectionTimeout",
    "message": "Database connection timed out after 30s",
    "stack_trace": "...",
    "context": {
      "user_id": "123",
      "tool": "get_order_status",
      "order_id": "ORD-456"
    }
  }
  ```

- **Real-time Monitoring**:
  ```python
  # CloudWatch alerts you when:
  # - Response time > 3 seconds
  # - Error rate > 5%
  # - Daily cost > $100
  # - A specific user making suspicious requests
  ```

**Use case**: When a customer complains "the bot didn't book my flight", you can trace the exact conversation, see which tool failed, view the error message, and fix the issue with complete context.

## How They Work Together

**Real-world scenario**: Customer service agent for an e-commerce platform

1. **Gateway**: Customer sends message via website chatbot
2. **Identity**: System identifies user (logged-in customer with order history)
3. **Runtime**: Request routes to Lambda function running the agent
4. **Memory**: Agent recalls customer's previous orders and preferences
5. **Agent**: Claude processes "Where is my order?"
6. **Tools**: Agent calls `get_order_status(order_id="ORD-789")`
7. **Tools**: Agent calls `get_tracking_info(tracking_number="1Z999")`
8. **Observability**: Logs show: request time, tokens used, tools called, response time
9. **Response**: "Your order is out for delivery, expected by 5 PM today"

All of this happens in ~2 seconds, fully traced, logged, and monitored.

### Model IDs and Inference Profiles

**Important**: Use cross-region inference profiles for better availability:

✅ **Correct** (Cross-region profile):
```python
model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

❌ **Incorrect** (Direct model ID - may not work with on-demand throughput):
```python
model="anthropic.claude-sonnet-4-5-20250929-v1:0"
```

Available Claude models:
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0` - Claude 4.5 Sonnet (latest)
- `us.anthropic.claude-opus-4-6` - Claude 4.6 Opus
- `us.anthropic.claude-haiku-4-5-20251001` - Claude 4.5 Haiku

### Entrypoint Decorator

The `@app.entrypoint` decorator marks a function as an API endpoint:

```python
@app.entrypoint
def invoke(payload):
    # payload is the JSON body from the request
    # Return a dictionary that will be serialized to JSON
    return {"result": "some value"}
```

## Common Issues and Solutions

### Issue 1: Credential Retrieval Error

**Error:**
```
botocore.exceptions.CredentialRetrievalError: Error when retrieving credentials
```

**Solution:**
- Ensure AWS credentials are configured
- Set `AWS_PROFILE` environment variable
- Verify credentials: `aws sts get-caller-identity --profile your-profile`

### Issue 2: ValidationException - On-demand Throughput Not Supported

**Error:**
```
ValidationException: Invocation of model ID ... with on-demand throughput isn't supported
```

**Solution:**
Use cross-region inference profile (prefix with `us.`):
```python
model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

### Issue 3: Model Access Denied

**Error:**
```
AccessDeniedException: You don't have access to the model
```

**Solution:**
1. Go to AWS Bedrock Console
2. Enable model access for Claude models
3. Wait for approval
4. Verify region supports Bedrock

### Issue 4: Region Not Supported

**Solution:**
Ensure you're using a supported region:
```python
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_PROFILE` | AWS credentials profile | `admin-user` |
| `AWS_DEFAULT_REGION` | AWS region | `us-west-2` |
| `AWS_ACCESS_KEY_ID` | AWS access key (alternative to profile) | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (alternative to profile) | `wJal...` |

## API Reference

### Request Format

```json
{
  "prompt": "Your message to the agent"
}
```

### Response Format

```json
{
  "result": "Agent's response message"
}
```

### Error Response

```json
{
  "error": "Error message",
  "type": "ErrorType"
}
```

## Advanced Usage

### Custom System Prompt

```python
agent = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    system_prompt="You are a helpful travel planning assistant."
)
```

### Conversation History

```python
@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    history = payload.get("history", [])  # Previous messages

    # Agent maintains conversation context
    result = agent(user_message)
    return {"result": result.message}
```

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands Agents Documentation](https://strandsagents.com/docs/)
- [Bedrock AgentCore on GitHub](https://github.com/awslabs/bedrock-agentcore)
- [Anthropic Claude Models](https://www.anthropic.com/claude)

## Troubleshooting

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check AWS Configuration

```bash
# Verify credentials
aws sts get-caller-identity --profile your-profile

# List available Bedrock models
aws bedrock list-foundation-models --region us-west-2

# Test Bedrock access
aws bedrock-runtime invoke-model \
  --model-id us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
  --body '{"prompt":"Hello"}' \
  --region us-west-2 \
  output.json
```

## License

See project root for license information.
