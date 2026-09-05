from strands import Agent
from strands.vended_plugins.context_injector import ContextInjector
import datetime

def get_current_time():
    return f"Current server time: {datetime.datetime.now().isoformat(timespec='seconds')}"

agent = Agent(
    plugins=[ContextInjector(get_current_time)]
)

response = agent("Are our support lines open right now?")

print(response)