"""
Tier 1: Azure AI — query models within your Azure subscription boundary.

Data stays within your Azure subscription. The model provider
does not have access to your inputs or outputs.

Requirements:
    pip install azure-ai-inference azure-identity
    az login  # Set up your Azure credentials
"""

from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential


def query_azure_ai(messages: list, endpoint: str, model: str = "claude-3-5-sonnet"):
    """Send a query to a model via Azure AI.
    Data stays within your Azure subscription boundary."""

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    response = client.complete(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    AZURE_ENDPOINT = "https://<your-resource>.services.ai.azure.com/"

    # Example: Analyzing a contract
    with open("contract.txt", "r") as f:
        contract_text = f.read()

    result = query_azure_ai(
        messages=[
            {
                "role": "user",
                "content": f"Review this contract and flag any unfavorable clauses:\n\n{contract_text}",
            }
        ],
        endpoint=AZURE_ENDPOINT,
    )
    print(result)
