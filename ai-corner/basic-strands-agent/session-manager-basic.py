from strands import Agent

agent = Agent(
    system_prompt="You are a helpful assistant",
)

agent("My name is Assefa")

response = agent("What is my name?")
print(response)