from strands import Agent, tool
from strands_tools import calculator, current_time

# Define custom tool
@tool
def letter_counter(word, letter):
    
    if not word or not letter:
        return 0
    if len(letter) != 1:
        raise ValueError("The 'letter' argument must be a single character.")
    return word.count(letter)

agent = Agent(tools=[letter_counter, calculator, current_time])

message = """
I have 4 requests:

1. What is the current time right now?
2. Calculate 3111696 / 74088
3. Tell me how many letter R's are in the word "strawberry"
4. Tell me how many letter A's are in the word "banana"
"""

agent(message)
