from strands import Agent, tool
from strands_tools import calculator
from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent


def log_tool_call(event):
    print(f"Calling tool: {event.tool_use['name']}")
    print(f"With input: {event.tool_use['input']}")

def log_tool_result(event):
    print(f"Tool {event.tool_use['name']} completed")

@tool
def get_weather(location):
    return f"Weather in {location}: Sunny, 75°F"

agent = Agent(
    system_prompt="You are helpful assistant",
    tools=[get_weather, calculator]
)

agent.add_hook(log_tool_call, BeforeToolCallEvent)
agent.add_hook(log_tool_result, AfterToolCallEvent)

message = """
I have few questions:
1. What's the weather in Seattle?
2. What is 1547 * 382?
"""

response = agent(message)
print(response)