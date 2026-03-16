# Trishul — The 3-Tier AI Privacy Framework

*Named after Shiva's trident (त्रिशूल) — three prongs, three tiers of protection.*

A philosophical framework for using AI tools while controlling how much of your personal data you expose to model providers. No custom tools to build — just a mental model and a curated set of existing tools for each tier.

---

## The Problem

When you use AI services like ChatGPT, Claude, or Gemini through their consumer apps, every conversation is tied to your account — your email, your payment info, your identity. Over weeks and months of usage, the provider accumulates a rich profile of who you are: your job, your business ideas, your travel plans, your health concerns, your financial situation, your relationships.

This isn't necessarily malicious. Memory and personalization features are genuinely useful. But the result is that multiple corporations now hold an intimate portrait of your life, and you have limited control over how that data is stored, used, or shared.

**Trishul** provides a thinking framework for controlling your AI privacy at three distinct levels — from zero precautions to full data isolation — so you can make conscious choices about what you share and with whom.

---

## The Trishul Model

| Tier | Name | What You Protect | What You Trade Off |
|------|------|------------------|--------------------|
| **Tier 3** | Open Use | Nothing | Nothing — full convenience |
| **Tier 2** | Anonymous Use | Your identity and persistent profile | Some convenience, slight latency |
| **Tier 1** | Full Isolation | Everything — identity and content | Cost, model capability, or hardware investment |

The core insight: **not everything you do with AI needs the same level of privacy.** Asking for a pasta recipe doesn't need the same protection as analyzing your tax returns. Trishul lets you route each conversation to the appropriate level — like the three prongs of Shiva's trident, each serving a distinct purpose.

### Quick Decision Guide

```
Is this content sensitive at all?
│
├── No → TIER 3 (Open Use)
│         General research, coding, learning, casual chat
│
└── Yes
    │
    ├── Is the CONTENT itself sensitive?
    │   (Financial data, health records, legal docs, trade secrets)
    │
    │   ├── Yes → TIER 1 (Full Isolation)
    │   │         Use Bedrock/Azure or local models
    │   │
    │   └── No, but I don't want it LINKED TO ME
    │             → TIER 2 (Anonymous Use)
    │               Business strategy, competitive research,
    │               personal reflections, sensitive brainstorming
    │
    └── Am I unsure? → Default to TIER 2
        Better to over-protect than under-protect
```

---

## Tier 3: Open Use

**Privacy Level:** None
**Best For:** General research, coding help, brainstorming, learning, casual conversation
**Setup Effort:** Zero

Use AI services directly with your account — Claude, ChatGPT, Gemini, Copilot — with all their features enabled. Memory, personalization, conversation history, file uploads, web search. The provider knows who you are and builds a profile over time.

### When to Use

- Looking up technical documentation or getting coding help
- Brainstorming ideas that aren't competitively sensitive
- Learning new concepts, getting explanations
- Writing help for non-sensitive content
- General research on public topics

### What You Get

- Best model capabilities (all features enabled)
- Persistent memory across sessions
- File handling, web browsing, tool use
- Zero setup or maintenance

### What You Accept

- The provider ties all conversations to your identity
- A persistent profile is built from your usage patterns
- Your data is subject to the provider's privacy policy (which can change)
- Multiple providers may each hold different slices of your personal information

### Recommended Tools

No special tools needed. Use the services as-is:

| Tool | What It Is |
|------|-----------|
| [Claude](https://claude.ai) | Anthropic's assistant — chat, analysis, coding |
| [ChatGPT](https://chat.openai.com) | OpenAI's assistant — chat, DALL-E, browsing |
| [Gemini](https://gemini.google.com) | Google's assistant — deep Google integration |
| [GitHub Copilot](https://github.com/features/copilot) | AI coding assistant in your IDE |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's CLI coding agent |

Just be mindful of what you discuss — this tier works best when you consciously avoid sharing deeply personal, financial, or strategic information.

---

## Tier 2: Anonymous Use (Identity Delinking)

**Privacy Level:** Medium — content is seen by model providers during inference, but not linked to your identity
**Best For:** Business strategy, competitive research, personal reflections, travel planning, sensitive brainstorming
**Setup Effort:** Minimal — just sign up for OpenRouter and use existing tools

### The Core Idea

Instead of building your own chat interface, use existing AI tools that support OpenRouter as a backend. OpenRouter acts as a privacy buffer — your account is with OpenRouter (one entity to trust), and they proxy requests to dozens of model providers without passing your identity downstream.

When an anonymous API call arrives from OpenRouter, the model provider sees a single stateless request — no identity, no account, no email, no link to any previous or future request.

### Recommended Tools for Chat

| Tool | What It Is | OpenRouter Support |
|------|-----------|-------------------|
| [OpenRouter Chat](https://openrouter.ai/chat) | OpenRouter's built-in chat UI | Native |
| [TypingMind](https://www.typingmind.com) | Polished chat UI, bring your own API key | Yes — set OpenRouter as provider |
| [LibreChat](https://github.com/danny-avila/LibreChat) | Self-hosted ChatGPT clone | Yes — configure as OpenAI-compatible endpoint |
| [Big-AGI](https://github.com/enricoros/big-agi) | Open-source AI chat with multi-model support | Yes — OpenAI-compatible |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted UI for local and remote models | Yes — OpenAI-compatible endpoint |
| [Jan](https://jan.ai) | Desktop app, local-first with remote model support | Yes — OpenAI-compatible |

### Recommended Tools for Coding (Tier 2)

For multi-step coding tasks where you want identity delinking:

| Tool | What It Is | OpenRouter Support |
|------|-----------|-------------------|
| [Aider](https://aider.chat) | Terminal-based AI coding assistant | Yes — `--openai-api-base https://openrouter.ai/api/v1` |
| [OpenCode](https://github.com/opencode-ai/opencode) | Open-source coding agent | Yes — OpenAI-compatible |
| [Cline](https://github.com/cline/cline) | Autonomous coding agent for VS Code | Yes — configure OpenRouter as provider |
| [Continue](https://continue.dev) | Open-source AI code assistant for IDEs | Yes — OpenAI-compatible |
| [Cursor](https://cursor.com) | AI-native code editor | Partial — can configure custom API endpoint |

**Example: Aider with OpenRouter**

```bash
# Install
pip install aider-chat

# Configure for anonymous use via OpenRouter
export OPENROUTER_API_KEY="your-key-here"
aider --model openrouter/anthropic/claude-sonnet-4-20250514
```

### PII Redaction with Existing Tools

Before sending sensitive content through Tier 2, strip personally identifiable information. You don't need to build a custom redactor — several tools exist:

| Tool | What It Does | Best For |
|------|-------------|----------|
| [Microsoft Presidio](https://github.com/microsoft/presidio) | Open-source PII detection and anonymization SDK | Programmatic redaction in Python pipelines |
| [PasteGuard](https://chromewebstore.google.com/detail/pasteguard) | Browser extension that redacts PII before pasting | Quick manual redaction when copying into chat UIs |
| [Stanza (Stanford NLP)](https://stanfordnlp.github.io/stanza/) | NLP toolkit with NER for 60+ languages | Multilingual PII detection |
| [spaCy + custom pipeline](https://spacy.io) | Industrial NLP with NER models | Building automated redaction into workflows |
| [Amazon Comprehend](https://aws.amazon.com/comprehend/) | Managed NLP service with PII detection | AWS-native workflows |
| [Google Cloud DLP](https://cloud.google.com/sensitive-data-protection) | Cloud-based sensitive data detection | GCP-native workflows |

**Example: Microsoft Presidio**

```python
# pip install presidio-analyzer presidio-anonymizer
# python -m spacy download en_core_web_lg

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "My name is Rahul Sharma and my email is rahul@sombyte.in"

# Detect PII
results = analyzer.analyze(text=text, language="en")

# Anonymize
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
print(anonymized.text)
# "My name is <PERSON> and my email is <EMAIL_ADDRESS>"
```

**Example: Manual Approach (No Tools)**

For quick, one-off redaction when you don't want to install anything:

1. Before pasting into any AI chat, mentally scan for: names, emails, phone numbers, company names, addresses, account numbers
2. Replace them with generic placeholders: "My company" instead of "Acme Corp", "the CEO" instead of "John Smith"
3. After getting the response, mentally map the placeholders back

This is imperfect but covers the 80% case for casual Tier 2 use.

### What PII Redaction Does NOT Catch

- **Contextual identifiers**: "I'm the only AI startup founder in my small town who previously worked at [specific company]"
- **Behavioral fingerprints**: Unique writing style, timezone patterns, topic combinations
- **Indirect references**: "My building on 5th and Main"
- **Domain-specific identifiers**: Employee IDs, internal ticket numbers, proprietary terminology

If the content itself is sensitive enough that you wouldn't want *anyone* to see it, use Tier 1.

### Limitations of Tier 2

- **Content is still seen during inference.** The model provider processes your tokens. They just can't link them to you.
- **OpenRouter knows your identity.** You're trusting one intermediary instead of many providers.
- **PII redaction is imperfect.** No tool catches everything. Be mindful of context.
- **Conversation context can leak identity.** Highly specific scenarios may be identifying even without explicit PII.

---

## Tier 1: Full Isolation

**Privacy Level:** Maximum — neither your identity nor your content leaves your trust boundary
**Best For:** Financial documents, tax returns, legal contracts, health records, trade secrets, M&A analysis
**Setup Effort:** Moderate (cloud configuration) to Significant (local hardware)

### Option A: Cloud Isolation (AWS Bedrock / Azure AI)

Managed cloud AI services run models within your cloud account boundary. Key guarantees:

- Your input/output data is not used to train or improve the models
- The model provider (Anthropic, Meta, etc.) does not have access to your data
- Data stays within your chosen region
- Enterprise-grade audit logging (CloudTrail, Azure Monitor)

**Recommended tools with Bedrock/Azure:**

| Tool | What It Is | Bedrock/Azure Support |
|------|-----------|----------------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Anthropic's CLI coding agent | Yes — `CLAUDE_CODE_USE_BEDROCK=1` |
| [Claude Code Desktop (Claude Desktop)](https://claude.ai/download) | Desktop app for Claude | Yes — configure Bedrock |
| [Amazon Q Developer](https://aws.amazon.com/q/developer/) | AWS's AI coding assistant | Native Bedrock |
| [Bedrock Chat](https://aws.amazon.com/bedrock/) | AWS Console chat playground | Native |
| [Azure AI Foundry](https://ai.azure.com) | Azure's AI studio and playground | Native |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted UI | Yes — OpenAI-compatible with Bedrock gateway |

**Claude Code with Bedrock (the simplest Tier 1 setup for coding):**

```bash
# Set environment variables
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_PROFILE=your-profile
export AWS_REGION=us-east-1
export ANTHROPIC_MODEL=us.anthropic.claude-sonnet-4-20250514-v1:0

# Use Claude Code normally — all data stays in your AWS account
claude
```

**Additional hardening:**
- VPC Endpoint for Bedrock (no internet transit)
- CloudTrail logging for full audit trail
- KMS encryption with your own keys
- IAM policies to restrict who can invoke models

### Option B: Local Models (Full Air-Gap)

For absolute isolation, run open-source models on your own hardware. Nothing leaves your machine.

**Recommended tools:**

| Tool | What It Is |
|------|-----------|
| [Ollama](https://ollama.com) | Simplest way to run local models — one command setup |
| [LM Studio](https://lmstudio.ai) | Desktop app for running local models with a chat UI |
| [Jan](https://jan.ai) | Desktop app, local-first design |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted chat UI that connects to Ollama |
| [LocalAI](https://localai.io) | OpenAI-compatible local API server |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Bare-metal inference engine for maximum performance |
| [Aider](https://aider.chat) | Coding assistant — works with Ollama local models |

**Quick start with Ollama:**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh    # Linux/macOS
# Or download from https://ollama.com for Windows

# Pull a capable model
ollama pull llama3.1:70b      # Best quality, needs ~40GB RAM
ollama pull llama3.1:8b       # Lighter, needs ~8GB RAM
ollama pull qwen2.5:32b       # Good for structured analysis
ollama pull deepseek-r1:14b   # Good for reasoning tasks

# Start chatting
ollama run llama3.1:8b
```

**Hardware requirements:**

| Model Size | RAM Required | GPU VRAM | Quality Level |
|-----------|-------------|----------|---------------|
| 7-8B params | 8 GB | 8 GB | Good for simple tasks, summaries |
| 13-14B params | 16 GB | 16 GB | Decent for analysis, writing |
| 32B params | 24 GB | 24 GB | Good for complex reasoning |
| 70B params | 40-48 GB | 2x 24 GB | Near-frontier for most tasks |

### Choosing Between Cloud and Local

| Factor | Bedrock / Azure | Local Models |
|--------|----------------|--------------|
| **Trust boundary** | Your cloud account (with legal guarantees) | Your physical hardware |
| **Model quality** | Frontier models (Claude, GPT-4 class) | Open-source (Llama, Qwen, DeepSeek) |
| **Setup effort** | AWS/Azure account + IAM configuration | Hardware purchase + software setup |
| **Running cost** | Per-token pricing (~$3-15 per million tokens) | Electricity + hardware amortization |
| **Scalability** | Unlimited | Limited by your hardware |
| **Best for** | Complex analysis needing frontier intelligence | Simpler tasks, absolute zero-trust |

### Limitations of Tier 1

- **Cloud option:** You're trusting AWS/Azure as infrastructure providers. They process your data on their servers, even if the model provider can't see it.
- **Local option:** Model quality is significantly lower than frontier models. Open-source models are improving rapidly but still lag behind Claude/GPT-4 for complex reasoning.
- **Cost:** Bedrock/Azure is more expensive per token than direct API. Local hardware requires $500-2000+ upfront.
- **Maintenance:** Both options require ongoing infrastructure management.

---

## Choosing the Right Tier — Examples

| Use Case | Recommended Tier | Why |
|----------|-----------------|-----|
| "How do I write a for loop in Python?" | Tier 3 | Zero sensitivity |
| "What's the best restaurant in Tokyo?" | Tier 3 | No personal data |
| "Help me plan a marketing strategy for my SaaS" | Tier 2 | Competitive strategy, don't want it profiled |
| "Analyze my competitors and their pricing" | Tier 2 | Business intelligence, identity-sensitive |
| "I'm feeling stressed about my startup failing" | Tier 2 | Personal emotional content |
| "Review my tax return and suggest deductions" | Tier 1 | Financial documents with PII |
| "Analyze this bank statement for spending patterns" | Tier 1 | Sensitive financial data |
| "Summarize this legal contract for my company" | Tier 1 | Confidential business documents |
| "What medications interact with my prescription?" | Tier 1 | Health information |

---

## Threat Model Summary

| Threat | Tier 3 | Tier 2 | Tier 1 (Cloud) | Tier 1 (Local) |
|--------|--------|--------|-----------------|-----------------|
| Provider builds a persistent profile of you | Exposed | Protected | Protected | Protected |
| Provider links your conversations across sessions | Exposed | Protected | Protected | Protected |
| Provider uses your data for training | Exposed | Varies | Contractually protected | Protected |
| Provider sees your content during inference | Exposed | Exposed | AWS/Azure processes it | Protected |
| Third party intercepts data in transit | TLS only | TLS only | VPC endpoint available | Air-gapped |
| Government subpoena to provider | Exposed | OpenRouter only | AWS/Azure only | Protected |
| Data breach at provider | Exposed | Content exposed | Content exposed | Protected |

### Trust Boundaries

```
Tier 3:  You ──→ Provider (full trust in provider)
Tier 2:  You ──→ OpenRouter ──→ Provider (trust OpenRouter with identity,
                                           provider sees anonymous content)
Tier 1a: You ──→ AWS/Azure (trust cloud infra, not model provider)
Tier 1b: You ──→ Your hardware (trust no one)
```

---

## The Practical Setup (Three Shell Aliases)

The simplest implementation of Trishul is three aliases in your shell config:

```bash
# ~/.bashrc or ~/.zshrc

# Tier 3: Open use — Claude Code with your Anthropic account
alias ai="claude"

# Tier 2: Anonymous use — Aider via OpenRouter
alias ai-anon="OPENAI_API_BASE=https://openrouter.ai/api/v1 OPENAI_API_KEY=$OPENROUTER_API_KEY aider --model openrouter/anthropic/claude-sonnet-4-20250514"

# Tier 1: Full isolation — Claude Code via AWS Bedrock
alias ai-secure="CLAUDE_CODE_USE_BEDROCK=1 AWS_PROFILE=bedrock AWS_REGION=us-east-1 claude"
```

That's it. Three commands, three privacy levels. No backend, no frontend, no Docker.

---

## FAQ

**Q: Do I need to build anything?**
A: No. Trishul is a thinking framework. The tools already exist — you just need to choose the right ones for each tier and be intentional about which tier you use for each conversation.

**Q: Can I use a VPN with Tier 2 for extra anonymity?**
A: If you're using OpenRouter's API directly (from a server or CLI tool), the model provider never sees your IP — only OpenRouter's. A VPN would only mask your IP from OpenRouter itself.

**Q: Is OpenRouter trustworthy?**
A: OpenRouter is a single point of trust in Tier 2. Review their [privacy policy](https://openrouter.ai/privacy). The tradeoff is trusting one company instead of five model providers separately.

**Q: How much does each tier cost?**
A: Tier 3 is whatever your existing subscriptions cost ($0-20/month). Tier 2 adds OpenRouter API costs (typically $1-10/month for moderate use). Tier 1 with Bedrock adds 2-5x the per-token cost. Tier 1 local requires $500-2000+ in GPU hardware upfront.

**Q: What if I accidentally use the wrong tier?**
A: Build the habit of pausing before each conversation: "Is this sensitive? Is the content itself sensitive, or just the identity link?" The decision flowchart above becomes second nature after a week.

**Q: Can PII redaction tools handle languages other than English?**
A: Microsoft Presidio supports multiple languages. Stanza supports 60+ languages. For manual redaction, the approach is language-agnostic — just replace identifying terms with placeholders before pasting.

**Q: What about file uploads (PDFs, images)?**
A: For Tier 2, you'd need to redact PII from files before uploading — significantly harder than text. For documents with embedded PII (financial statements, ID scans), use Tier 1 directly.

**Q: Daniel Miessler's PAI/Kai system doesn't address privacy at all. Why should I care?**
A: Daniel's system is optimized for maximum productivity with full trust in Anthropic (Tier 3). That's a valid choice for many use cases. Trishul exists for people who want to be intentional about *which* conversations get that level of trust and which don't.

---

## Documentation

- [Tier 3: Open Use — Detailed Guide](docs/tier-3-open-use.md)
- [Tier 2: Anonymous Use — Detailed Guide](docs/tier-2-anonymous-use.md)
- [Tier 1: Full Isolation — Detailed Guide](docs/tier-1-full-isolation.md)
- [Threat Model](docs/threat-model.md)
- [FAQ](docs/faq.md)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Areas we'd especially love help with:
- Tool recommendations and reviews for each tier
- PII redaction tool comparisons and benchmarks
- Guides for setting up Bedrock/Azure with specific tools
- Translations of the framework into other languages
- Real-world usage patterns and case studies

## License

Released under the [MIT License](LICENSE).

---

*Trishul (त्रिशूल) — because privacy is not binary. It's a spectrum, and you should be able to choose where you sit on it for each interaction.*
