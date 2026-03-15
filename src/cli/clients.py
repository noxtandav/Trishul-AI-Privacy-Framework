"""
LLM client wrappers for each privacy tier.

Each client implements the same interface so the agent can swap
routing transparently based on the conversation tier.
"""

import json
import requests
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Common interface for all LLM routing backends."""

    @abstractmethod
    def chat(self, messages: list[dict], model: str | None = None) -> str:
        """Send messages and return the assistant's response text."""
        ...


class OpenRouterClient(BaseLLMClient):
    """Tier 2 — anonymous requests via OpenRouter."""

    def __init__(self, config: dict):
        self.api_key = config["openrouter_api_key"]
        self.default_model = config.get(
            "openrouter_model", "anthropic/claude-sonnet-4-20250514"
        )
        self.base_url = config.get(
            "openrouter_base_url", "https://openrouter.ai/api/v1"
        )

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model or self.default_model,
                "messages": messages,
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class BedrockClient(BaseLLMClient):
    """Tier 1 — AWS Bedrock (data stays in your AWS account)."""

    def __init__(self, config: dict):
        import boto3

        self.default_model = config.get(
            "bedrock_model", "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=config.get("aws_region", "us-east-1"),
        )

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": messages,
        })

        response = self.client.invoke_model(
            modelId=model or self.default_model,
            body=body,
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]


class OllamaClient(BaseLLMClient):
    """Tier 1 — local Ollama models (nothing leaves your machine)."""

    def __init__(self, config: dict):
        self.default_model = config.get("ollama_model", "llama3.1:8b")
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model or self.default_model,
                "messages": messages,
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


class DirectAPIClient(BaseLLMClient):
    """Tier 3 — direct API calls (no privacy, full convenience)."""

    def __init__(self, config: dict):
        self.api_key = config["direct_api_key"]
        self.default_model = config.get("direct_model", "claude-sonnet-4-20250514")
        self.base_url = config.get(
            "direct_base_url", "https://api.anthropic.com/v1"
        )

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        response = requests.post(
            f"{self.base_url}/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": model or self.default_model,
                "max_tokens": 4096,
                "messages": messages,
            },
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]
