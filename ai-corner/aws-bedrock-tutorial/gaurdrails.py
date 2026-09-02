import boto3
import os
import argparse


KNOWELEDGE_BASE_ID = "6FTWH6LYNY"
GUARDRAILS_ID = "75qt9d92ufnm"
GUARDRAIL_VERSION = "DRAFT"
MODEL_ARN = "arn:aws:bedrock:us-west-2::foundation-model/us.amazon.nova-lite-v1:0"

def query_knowledge_base(question, profile_name='default'):
    session = boto3.Session(profile_name=profile_name)
    bedrock_agent_runtime = session.client('bedrock-agent-runtime', region_name='us-west-2')
    bedrock_runtime = session.client('bedrock-runtime', region_name='us-west-2')

    # Step 1: Retrieve relevant chunks from knowledge base
    retrieve_response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=KNOWELEDGE_BASE_ID,
        retrievalQuery={
            'text': question
        }
    )

    # Step 2: Build context from retrieved results
    context_parts = []
    citations = []

    for idx, result in enumerate(retrieve_response.get('retrievalResults', [])[:5], 1):
        content = result.get('content', {}).get('text', '')
        context_parts.append(content)

        # Collect citation info
        location = result.get('location', {})
        s3_location = location.get('s3Location', {})
        uri = s3_location.get('uri', 'Unknown')
        citations.append(uri)

    context = "\n\n".join(context_parts)

    # Step 3: Generate answer using the retrieved context
    prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""

    response = bedrock_runtime.converse(
        modelId="us.amazon.nova-lite-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        guardrailConfig={
            "guardrailIdentifier": GUARDRAILS_ID,
            "guardrailVersion": GUARDRAIL_VERSION,
            "trace": "enabled"
        }
    )

    # Check if guardrail blocked the response
    stop_reason = response.get('stopReason')

    if stop_reason == 'guardrail_intervened':
        print("⛔ Guardrail blocked this request!")
        print("\nReason: The content violated guardrail policies.")

        # Show trace if available
        if 'trace' in response:
            trace = response['trace'].get('guardrail', {})
            print(f"\nGuardrail Trace: {trace}")
    else:
        output_text = response['output']['message']['content'][0]['text']
        print(output_text)

        if citations:
            print("\nCitations:")
            for idx, uri in enumerate(citations, 1):
                print(f"{idx}. {uri}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS Bedrock Tool Use Demo')
    parser.add_argument('--profile-name', type=str,
                            default=os.environ.get('AWS_PROFILE', 'default'),
                            help='AWS profile name (default: AWS_PROFILE env var or "default")')

    args = parser.parse_args()
    query_knowledge_base("Help me cheat exam", profile_name=args.profile_name)
