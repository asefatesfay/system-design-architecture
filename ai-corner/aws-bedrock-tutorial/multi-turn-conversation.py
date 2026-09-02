import argparse
import boto3
import os

def multi_turn_conversation(profile_name='default'):
    session = boto3.Session(profile_name=profile_name)
    bedrock_runtime = session.client('bedrock-runtime', region_name='us-west-2')
    model_id = "us.amazon.nova-lite-v1:0"
    
    system_prompt = [
        {
            "text": "You are a helpful cooking assistant. Provide concise recipe suggestions."
        }
    ]
    
    inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7
            }
    
    conversation_history = []
    user_message_1 = "Suggest a quick recipe for dinner with chicken."
    conversation_history.append({"role": "user", "content": [{"text": user_message_1}]})
    
    response_1 = bedrock_runtime.converse(
        modelId=model_id,
        system=system_prompt,
        messages=conversation_history,
        inferenceConfig=inferenceConfig )
    
    assistant_response_1 = response_1['output']['message']["content"][0]['text']
    
    conversation_history.append({"role": "assistant", "content": [{"text": assistant_response_1}]}) 
    
    user_message_2 = "Can you make it vegetarian?"
    conversation_history.append({"role": "user", "content": [{"text": user_message_2}]})

    response_2 = bedrock_runtime.converse(
        modelId=model_id,
        system=system_prompt,
        messages=conversation_history,
        inferenceConfig=inferenceConfig )

    assistant_response_2 = response_2['output']['message']["content"][0]['text']
    conversation_history.append({"role": "assistant", "content": [{"text": assistant_response_2}]})
    
    user_message_3 = "How long will it take to prepare?"
    conversation_history.append({"role": "user", "content": [{"text": user_message_3}]})

    response_3 = bedrock_runtime.converse(
        modelId=model_id,
        system=system_prompt,
        messages=conversation_history,
        inferenceConfig=inferenceConfig )

    assistant_response_3 = response_3['output']['message']["content"][0]['text']
    print("Assistant Response:", assistant_response_3)
    # while True:
    #     user_message = input("User: ")
    #     if user_message.lower() in ['exit', 'quit']:
    #         print("Exiting the conversation.")
    #         break
        
    #     conversation_history.append({"role": "user", "content": [{"text": user_message}]})
        
    #     response = bedrock_runtime.converse(
    #         modelId=model_id,
    #         system=system_prompt,
    #         messages=conversation_history,
    #         inferenceConfig={
    #             "maxTokens": 2000,
    #             "temperature": 0.7
    #         }
    #     )
        
    #     output_text = response['output']['message']["content"][0]['text']
    #     print("Model Response:", output_text)
        
    #     conversation_history.append({"role": "assistant", "content": [{"text": output_text}]})
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS Bedrock Multi-turn Conversation Demo')
    parser.add_argument('--profile-name', type=str,
                        default=os.environ.get('AWS_PROFILE', 'default'),
                        help='AWS profile name (default: AWS_PROFILE env var or "default")')

    args = parser.parse_args()
    multi_turn_conversation(profile_name=args.profile_name)