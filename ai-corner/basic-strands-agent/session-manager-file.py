from strands import Agent
from strands.session.file_session_manager import FileSessionManager

file_session_manager = FileSessionManager(
    session_id="my-session",
    storage_dir="./sessions"
)

agent = Agent(
    system_prompt="You are a helpful assistant",
    session_manager=file_session_manager
)

agent("My name is Assefa")

# Later, even after restart, the agent remembers

agent = Agent(
    system_prompt="You are a helpful assistant",
    session_manager=FileSessionManager(
        session_id="my-session",
        storage_dir="./sessions"
    )
)

response = agent("What is my name?")
print(response)