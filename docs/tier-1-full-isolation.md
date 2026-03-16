# Tier 1: Full Isolation — Detailed Guide

**Privacy Level:** Maximum — neither your identity nor your content leaves your trust boundary
**Best For:** Financial documents, tax returns, legal contracts, health records, trade secrets, M&A analysis
**Setup Effort:** Moderate (cloud configuration) to Significant (local hardware)

---

## The Core Idea

The model runs within infrastructure you control, under contractual guarantees that prevent the model provider from accessing your data. Or, for absolute isolation, the model runs entirely on your own hardware with no network calls.

## Option A: Cloud Isolation (AWS Bedrock / Azure AI)

Managed cloud AI services run models within your cloud account boundary. Key guarantees:

- Your input/output data is not used to train or improve the models
- The model provider (Anthropic, Meta, etc.) does not have access to your data
- Data stays within your chosen region
- Enterprise-grade audit logging (CloudTrail, Azure Monitor)

### Recommended Tools with Bedrock

| Tool | What It Is | How to Configure |
|------|-----------|-----------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | CLI coding agent | `CLAUDE_CODE_USE_BEDROCK=1` |
| [Claude Desktop](https://claude.ai/download) | Desktop chat app | Configure Bedrock in settings |
| [Amazon Q Developer](https://aws.amazon.com/q/developer/) | AWS's AI coding assistant | Native Bedrock integration |
| [Bedrock Console](https://aws.amazon.com/bedrock/) | AWS Console chat playground | Native |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted chat UI | OpenAI-compatible with Bedrock gateway |

### Claude Code with Bedrock (Simplest Tier 1 Setup for Coding)

```bash
# Set environment variables
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
export ANTHROPIC_MODEL=us.anthropic.claude-sonnet-4-20250514-v1:0

# Use Claude Code normally — all data stays in your AWS account
claude
```

### Recommended Tools with Azure AI

| Tool | What It Is | How to Configure |
|------|-----------|-----------------|
| [Azure AI Foundry](https://ai.azure.com) | Azure's AI studio and playground | Native |
| [VS Code + Azure AI](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azure-ai) | IDE integration | Configure Azure endpoint |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted chat UI | OpenAI-compatible with Azure endpoint |

### Additional Hardening

- **VPC Endpoint** for Bedrock — no internet transit, traffic stays within AWS network
- **CloudTrail logging** — full audit trail of every API call
- **KMS encryption** — use your own encryption keys
- **IAM policies** — restrict who can invoke models

## Option B: Local Models (Full Air-Gap)

For absolute isolation, run open-source models on your own hardware. Nothing leaves your machine.

### Recommended Tools

| Tool | What It Is | Best For |
|------|-----------|----------|
| [Ollama](https://ollama.com) | Simplest local model runner — one command setup | Getting started quickly |
| [LM Studio](https://lmstudio.ai) | Desktop app with chat UI for local models | Non-technical users |
| [Jan](https://jan.ai) | Desktop app, local-first design | Privacy-focused desktop chat |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted chat UI, connects to Ollama | ChatGPT-like experience locally |
| [LocalAI](https://localai.io) | OpenAI-compatible local API server | Drop-in replacement for OpenAI API |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Bare-metal inference engine | Maximum performance |
| [Aider](https://aider.chat) | Terminal coding assistant | Coding with local models |

### Quick Start with Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh    # Linux/macOS
# Or download from https://ollama.com for Windows

# Pull a model
ollama pull llama3.1:70b      # Best quality, needs ~40GB RAM
ollama pull llama3.1:8b       # Lighter, needs ~8GB RAM
ollama pull qwen2.5:32b       # Good for structured analysis
ollama pull deepseek-r1:14b   # Good for reasoning tasks

# Start chatting
ollama run llama3.1:8b
```

### Coding with Local Models

```bash
# Aider with Ollama
pip install aider-chat
aider --model ollama/llama3.1:70b
```

### Hardware Requirements

| Model Size | RAM Required | GPU VRAM | Quality Level |
|-----------|-------------|----------|---------------|
| 7-8B params | 8 GB | 8 GB | Good for simple tasks, summaries |
| 13-14B params | 16 GB | 16 GB | Decent for analysis, writing |
| 32B params | 24 GB | 24 GB | Good for complex reasoning |
| 70B params | 40-48 GB | 2x 24 GB | Near-frontier for most tasks |

CPU inference is possible but 5-10x slower than GPU. For occasional use (analyzing a document once a week), CPU is fine. For interactive chat, you want a GPU.

## Choosing Between Cloud and Local

| Factor | Bedrock / Azure | Local Models |
|--------|----------------|--------------|
| **Trust boundary** | Your cloud account (with legal guarantees) | Your physical hardware |
| **Model quality** | Frontier models (Claude, GPT-4 class) | Open-source (Llama, Qwen, DeepSeek) |
| **Setup effort** | AWS/Azure account + IAM configuration | Hardware purchase + software setup |
| **Running cost** | Per-token pricing (~$3-15 per million tokens) | Electricity + hardware amortization |
| **Scalability** | Unlimited | Limited by your hardware |
| **Best for** | Complex analysis needing frontier intelligence | Simpler tasks, absolute zero-trust |

## Limitations of Tier 1

- **Cloud option:** You're trusting AWS/Azure as infrastructure providers. They process your data on their servers, even if the model provider can't see it.
- **Local option:** Model quality is significantly lower than frontier models. Open-source models are improving rapidly but still lag behind Claude/GPT-4 for complex reasoning.
- **Cost:** Bedrock/Azure is more expensive per token than direct API. Local hardware requires $500-2000+ upfront.
- **Maintenance:** Both options require ongoing infrastructure management.
