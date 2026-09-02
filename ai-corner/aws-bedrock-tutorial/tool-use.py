import argparse
import json
import os
import boto3

def get_weather(location, unit="fahrenheit"):
    """
    Simulate a weather API call to get the current weather for a given location.
    """
    weather_data = {
        "location": location,
        "temperature": 75 if unit == "fahrenheit" else 24,
        "unit": unit,
        "condition": "Sunny",
        "humidity": 50
    }
    return weather_data

# ---------------------------------------------------------------------------
# Step 2: Describe your functions as "tools" for the model
# ---------------------------------------------------------------------------
# The model needs a description of each tool so it knows:
#   - What the tool does (description)
#   - What inputs it expects (inputSchema)
#
# This is like writing documentation so someone else can use your function.

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get the current weather for a given location.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. 'San Francisco, CA'",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["fahrenheit", "celsius"],
                                "description": "Temperature unit (default: fahrenheit)",
                            },
                        },
                        "required": ["location"],
                    }
                },
            }
        }
    ]
}

TOOL_FUNCTIONS = {
    "get_weather": get_weather
}

def run_tool(tool_name, tool_input):
    
    func = TOOL_FUNCTIONS.get(tool_name)
    
    if func is None:
        return {
            "error": f"Unknown tool: {tool_name}"
        }
        
    return func(**tool_input)


inferenceConfig = {
    "maxTokens": 2000,
    "temperature": 0.7
}

def tool_use_demo(profile_name='default'):
    session = boto3.Session(profile_name=profile_name)
    bedrock_runtime = session.client('bedrock-runtime', region_name='us-west-2')
    model_id = "us.amazon.nova-lite-v1:0"
    
    user_message = "What is the current weather in Seattle Today?"
    
    messages = [
        {
            "role": "user",
            "content": [{"text": user_message}]
        }
    ]
    
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig=inferenceConfig,
        toolConfig = TOOL_CONFIG
    )
    
    stop_reason = response["stopReason"]
    assistant_message = response['output']['message']
    
    if stop_reason == "tool_use":
        tool_use_block = None
        
        for block in assistant_message["content"]:
            if "toolUse" in block:
                tool_use_block = block["toolUse"]
                break
        tool_name = tool_use_block["name"]
        tool_input = tool_use_block["input"]
        tool_use_id = tool_use_block["toolUseId"]
        
        result = run_tool(tool_name, tool_input)
        
        messages.append(assistant_message)
        
        messages.append({
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"json": result}]
                    }
                }
            ]
        })
        
        final_response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inferenceConfig,
            toolConfig = TOOL_CONFIG
        )
        
        final_text = final_response['output']['message']["content"][0]['text']
        print("Assistant Response:", final_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS Bedrock Tool Use Demo')
    parser.add_argument('--profile-name', type=str,
                        default=os.environ.get('AWS_PROFILE', 'default'),
                        help='AWS profile name (default: AWS_PROFILE env var or "default")')

    args = parser.parse_args()
    tool_use_demo(profile_name=args.profile_name)
