"""
Multi-Agent Travel System - Main Entry Point

Start here for Step 1 of the tutorial!
"""
import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from .config import config


# Initialize the app
app = BedrockAgentCoreApp()


def setup_environment():
    """Configure AWS environment"""
    config.validate()
    os.environ['AWS_DEFAULT_REGION'] = config.AWS_REGION
    print(f"✓ AWS Profile: {config.AWS_PROFILE}")
    print(f"✓ AWS Region: {config.AWS_REGION}")
    print(f"✓ Bedrock Model: {config.BEDROCK_MODEL}")


# STEP 1: Simple Travel Agent
# This will be expanded in later steps
travel_agent = None


def create_travel_agent():
    """Create the main travel agent (Step 1)"""
    global travel_agent
    travel_agent = Agent(
        model=config.BEDROCK_MODEL,
        system_prompt="""You are a helpful travel planning assistant.
        Help users plan trips by asking about destination, dates, budget, and interests.
        Be friendly and ask clarifying questions."""
    )
    print("✓ Travel Agent created")


@app.entrypoint
def plan_trip(payload):
    """
    Main endpoint for trip planning

    This will be expanded in later tutorial steps.
    """
    user_message = payload.get("message", "I want to plan a trip")

    # Step 1: Simple response
    result = travel_agent(user_message)

    return {"response": result.message}


def main():
    """Main entry point"""
    print("🌍 Multi-Agent Travel System")
    print("=" * 50)

    # Setup
    setup_environment()
    create_travel_agent()

    print("=" * 50)
    print("🚀 Server starting on http://localhost:8080")
    print("=" * 50)

    # Start the server
    app.run()


if __name__ == "__main__":
    main()
