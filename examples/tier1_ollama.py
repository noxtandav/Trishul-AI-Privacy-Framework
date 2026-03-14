"""
Tier 1: Local Ollama — query models on your own hardware.

Nothing leaves your machine. Full air-gap privacy.

Requirements:
    pip install requests
    # Install Ollama: https://ollama.com
    # Pull a model: ollama pull llama3.1:8b
    # Start server: ollama serve
"""

import requests


def query_local(messages: list, model: str = "llama3.1:8b"):
    """Query a local model via Ollama. Nothing leaves your machine."""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
        },
    )
    response.raise_for_status()

    return response.json()["message"]["content"]


# ─────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = query_local([
        {
            "role": "user",
            "content": "Analyze my monthly expenses and suggest areas to cut:\n\n"
                       "Rent: $2000\nGroceries: $600\nDining out: $400\n"
                       "Subscriptions: $150\nTransportation: $300\nUtilities: $200",
        }
    ])
    print(result)
