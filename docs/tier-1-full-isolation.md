# Tier 1: Full Isolation

**Privacy Level:** Maximum — neither your identity nor your content leaves your trust boundary
**Best For:** Financial documents, tax returns, legal contracts, health records, trade secrets, M&A analysis
**Setup Effort:** Significant (cloud configuration or hardware investment)

## The Core Idea

The model runs within infrastructure you control, under contractual guarantees that prevent the model provider from accessing your data. Or, for absolute isolation, the model runs entirely on your own hardware with no network calls.

## Option A: Cloud Isolation (AWS Bedrock / Azure AI)

Managed cloud AI services like AWS Bedrock and Azure AI run models within your cloud account boundary. The key contractual commitments:

- Your input/output data is not used to train or improve the models
- The model provider (Anthropic, Meta, etc.) does not have access to your data
- Data stays within your chosen AWS region or Azure region
- You get enterprise-grade audit logging (CloudTrail, Azure Monitor)

See [`examples/tier1_bedrock.py`](../examples/tier1_bedrock.py) and [`examples/tier1_azure.py`](../examples/tier1_azure.py) for working code.

### Additional Hardening for Bedrock/Azure

```
VPC Endpoint for Bedrock (no internet transit):
- Create a VPC endpoint for com.amazonaws.us-east-1.bedrock-runtime
- Attach a security group that only allows your application

CloudTrail logging for audit:
- All Bedrock API calls are automatically logged to CloudTrail
- You can verify no data exfiltration by reviewing these logs

KMS encryption:
- Bedrock encrypts data in transit (TLS) and at rest (AWS-managed keys)
- You can use your own KMS key for additional control
```

## Option B: Local Models (Full Air-Gap)

For absolute isolation, run open-source models on your own hardware. Nothing leaves your machine.

See [`examples/tier1_ollama.py`](../examples/tier1_ollama.py) for a working example.

### Quick Start with Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a capable model
ollama pull llama3.1:70b      # Best quality, needs ~40GB RAM
ollama pull llama3.1:8b       # Lighter, needs ~8GB RAM
ollama pull qwen2.5:32b       # Good for structured analysis
ollama pull mistral:7b        # Fast, lightweight

# Run with API server
ollama serve
```

### Hardware Requirements

| Model Size | RAM Required | GPU VRAM | Quality Level |
|-----------|-------------|----------|---------------|
| 7B params | 8 GB | 8 GB | Good for simple tasks, summaries |
| 13B params | 16 GB | 16 GB | Decent for analysis, writing |
| 32B params | 24 GB | 24 GB | Good for complex reasoning |
| 70B params | 40-48 GB | 2x 24 GB | Near-frontier for most tasks |

CPU inference is possible but 5-10x slower than GPU. For occasional use (analyzing a document once a week), CPU is fine. For interactive chat, you want a GPU.

## Choosing Between Bedrock/Azure and Local

| Factor | Bedrock / Azure | Local Models |
|--------|----------------|--------------|
| **Trust boundary** | Your cloud account (with legal guarantees) | Your physical hardware |
| **Model quality** | Frontier models (Claude, GPT-4 class) | Open-source (Llama, Qwen, Mistral) |
| **Setup effort** | AWS/Azure account + IAM configuration | Hardware purchase + software setup |
| **Running cost** | Per-token pricing (~$3-15 per million tokens) | Electricity + hardware amortization |
| **Scalability** | Unlimited | Limited by your hardware |
| **Best for** | Complex analysis needing frontier intelligence | Simpler tasks, absolute zero-trust |

## Limitations of Tier 1

- **Cloud option:** You're trusting AWS/Azure as infrastructure providers. They process your data on their servers, even if the model provider can't see it.
- **Local option:** Model quality is significantly lower than frontier models. A 70B parameter model is roughly equivalent to GPT-3.5-level, which may not be adequate for complex financial or legal analysis.
- **Cost:** Bedrock/Azure is more expensive per token than direct API access. Local hardware requires upfront investment (a capable GPU costs $500-2000+).
- **Maintenance:** Both options require ongoing infrastructure management.
