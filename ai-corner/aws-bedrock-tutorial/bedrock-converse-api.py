import argparse
import boto3
import json
import os

def use_converse_api(profile_name='default'):
    session = boto3.Session(profile_name=profile_name)
    bedrock_runtime = session.client('bedrock-runtime', region_name='us-west-2')
    model_id = "us.amazon.nova-lite-v1:0"
    system_prompt = [
        {
            "text": "You are a helpful technical assistant that explains concepts clearly and concisely."
        }
    ]
    user_message = "What is serverless computing?"
    
    response = bedrock_runtime.converse(
        modelId=model_id,
        system=system_prompt,
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        inferenceConfig = {
            "maxTokens": 2000,
            "temperature": 0.7
        }
    )
    output_text = response['output']['message']["content"][0]['text']
    print("Model Response:", output_text)
    
    usage = response.get('usage', {})
    print("Usage:", json.dumps(usage, indent=2))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS Bedrock Converse API Demo')
    parser.add_argument('--profile-name', type=str,
                        default=os.environ.get('AWS_PROFILE', 'default'),
                        help='AWS profile name (default: AWS_PROFILE env var or "default")')

    args = parser.parse_args()
    use_converse_api(profile_name=args.profile_name)