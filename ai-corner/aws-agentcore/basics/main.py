import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

# Initialize the application
app = BedrockAgentCoreApp()

# Set AWS profile via environment variable if not already set
# The Agent will use this when creating its internal boto3 session
if 'AWS_PROFILE' not in os.environ:
    os.environ['AWS_PROFILE'] = 'admin-user'

# Set AWS region for Bedrock
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

agent = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # Cross-region inference profile
)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello!, how can I help you today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
