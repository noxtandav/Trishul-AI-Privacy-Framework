"""
Tier 1: AWS Bedrock — query Claude within your AWS account boundary.

Data stays within your AWS account. The model provider (Anthropic)
does not have access to your inputs or outputs.

Requirements:
    pip install boto3
    aws configure  # Set up your AWS credentials
"""

import boto3
import json


def query_bedrock(messages: list, model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"):
    """Send a query to Claude via AWS Bedrock.
    Data stays within your AWS account boundary."""

    client = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",  # Choose your preferred region
    )

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": messages,
    })

    response = client.invoke_model(
        modelId=model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


# ─────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: Analyzing a financial document
    with open("financial_statement.txt", "r") as f:
        statement = f.read()

    result = query_bedrock([
        {
            "role": "user",
            "content": f"Analyze this financial statement and identify key risks:\n\n{statement}",
        }
    ])
    print(result)
