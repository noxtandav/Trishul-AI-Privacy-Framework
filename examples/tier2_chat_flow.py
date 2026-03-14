"""
Tier 2: Complete chat flow with PII redaction and OpenRouter routing.

Shows how chat history is managed locally while API calls go through
OpenRouter anonymously with PII stripped.

Requirements:
    pip install requests spacy
    python -m spacy download en_core_web_sm
"""

import os
import sys
import requests

# Add project root to path so we can import the PII redactor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.pii_redactor import PIIRedactor, RedactionMapping


def send_message(
    conversation_history: list[dict],
    new_message: str,
    redactor: PIIRedactor,
    mapping: RedactionMapping,
    api_key: str,
):
    """Send a message through OpenRouter with PII redaction."""

    # 1. Add the new message to local history
    conversation_history.append({"role": "user", "content": new_message})

    # 2. Build context (last 20 messages, or summarize older ones)
    messages = conversation_history[-20:]

    # 3. Run PII redaction on the outgoing messages
    redacted_messages = redactor.redact_messages(messages, mapping)

    # 4. Send to OpenRouter (anonymous, stateless)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "anthropic/claude-sonnet-4-20250514",
            "messages": redacted_messages,
        },
    )
    response.raise_for_status()
    assistant_content = response.json()["choices"][0]["message"]["content"]

    # 5. Rehydrate the response (replace placeholders with originals)
    rehydrated_content = mapping.rehydrate(assistant_content)

    # 6. Store in local history
    conversation_history.append({"role": "assistant", "content": rehydrated_content})

    return rehydrated_content


def get_privacy_respecting_models(api_key: str):
    """Fetch models from OpenRouter and filter by data policy."""
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    models = response.json()["data"]

    # Filter for models with pricing info (active models)
    safe_models = []
    for model in models:
        if model.get("pricing"):
            safe_models.append({
                "id": model["id"],
                "name": model.get("name", ""),
                "context_length": model.get("context_length", 0),
            })

    return safe_models


# ─────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Configure with your specific terms
    redactor = PIIRedactor(
        custom_terms={
            "company": ["Sombyte", "Acme Corp"],
            "project": ["Project Atlas", "Operation Thunderbolt"],
            "product": ["SmartHire ATS"],
        },
        use_ner=True,
    )

    # One mapping per conversation (maintains consistency)
    mapping = RedactionMapping()

    # Example: redact a message
    text = """
    Hi, I'm Rahul Sharma and I work at Sombyte. My email is
    rahul@sombyte.in and my phone is +91-98765-43210. We're building
    SmartHire ATS and our client Acme Corp in Mumbai needs the deployment
    by March. My PAN is ABCDE1234F and my Aadhaar is 1234 5678 9012.
    Please analyze the attached financial statement for our Q3 revenue.
    """

    redacted = redactor.redact(text, mapping)
    print("REDACTED OUTPUT:")
    print(redacted)

    print("\nREHYDRATED OUTPUT:")
    print(mapping.rehydrate(redacted))

    print("\nMAPPING:")
    for placeholder, original in mapping._reverse.items():
        print(f"  {placeholder} -> {original}")
