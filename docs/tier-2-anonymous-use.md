# Tier 2: Anonymous Use (Identity Delinking) — Detailed Guide

**Privacy Level:** Medium — content is seen by model providers during inference, but not linked to your identity
**Best For:** Business strategy, competitive research, personal reflections, travel planning, sensitive brainstorming
**Setup Effort:** Minimal — sign up for OpenRouter and use existing tools

---

## The Core Idea

Instead of building a custom chat interface, use existing AI tools that support OpenRouter as a backend. OpenRouter acts as a privacy buffer — your account is with OpenRouter (one entity to trust), and they proxy requests to dozens of model providers without passing your identity downstream.

## Why This Works

When you use Claude at claude.ai, Anthropic knows:
- Your email and identity
- Every conversation you've ever had
- Your usage patterns over time
- Your uploaded files

When an anonymous API call arrives from OpenRouter:
- The model provider sees a single stateless request
- No identity, no account, no email
- No link to any previous or future request
- After inference, the connection is gone

```
You ──→ OpenRouter ──→ Anthropic / Google / DeepSeek / Mistral
         (knows you)    (sees anonymous, stateless request)
```

## Recommended Tools for Chat

| Tool | What It Is | OpenRouter Support |
|------|-----------|-------------------|
| [OpenRouter Chat](https://openrouter.ai/chat) | OpenRouter's built-in chat UI | Native |
| [TypingMind](https://www.typingmind.com) | Polished chat UI, bring your own API key | Yes — set OpenRouter as provider |
| [LibreChat](https://github.com/danny-avila/LibreChat) | Self-hosted ChatGPT clone | Yes — OpenAI-compatible endpoint |
| [Big-AGI](https://github.com/enricoros/big-agi) | Open-source AI chat with multi-model support | Yes — OpenAI-compatible |
| [Open WebUI](https://github.com/open-webui/open-webui) | Self-hosted UI for local and remote models | Yes — OpenAI-compatible endpoint |
| [Jan](https://jan.ai) | Desktop app, local-first with remote model support | Yes — OpenAI-compatible |

## Recommended Tools for Coding

For multi-step coding tasks where you want identity delinking:

| Tool | What It Is | OpenRouter Support |
|------|-----------|-------------------|
| [Aider](https://aider.chat) | Terminal-based AI coding assistant | Yes — set as OpenAI-compatible base URL |
| [OpenCode](https://github.com/opencode-ai/opencode) | Open-source coding agent | Yes — OpenAI-compatible |
| [Cline](https://github.com/cline/cline) | Autonomous coding agent for VS Code | Yes — configure OpenRouter as provider |
| [Continue](https://continue.dev) | Open-source AI code assistant for IDEs | Yes — OpenAI-compatible |

### Example: Aider with OpenRouter

```bash
pip install aider-chat

export OPENROUTER_API_KEY="your-key-here"
aider --model openrouter/anthropic/claude-sonnet-4-20250514
```

## PII Redaction: Adding an Extra Layer

For Tier 2 conversations involving business-specific terms (company names, project codenames, client names), consider running PII redaction before sending content. You don't need to build a custom redactor — several tools exist:

### Recommended PII Redaction Tools

| Tool | What It Does | Best For |
|------|-------------|----------|
| [Microsoft Presidio](https://github.com/microsoft/presidio) | Open-source PII detection and anonymization SDK | Programmatic redaction in Python pipelines |
| [PasteGuard](https://chromewebstore.google.com/detail/pasteguard) | Browser extension that redacts PII before pasting | Quick manual redaction when copying into chat UIs |
| [Stanza (Stanford NLP)](https://stanfordnlp.github.io/stanza/) | NLP toolkit with NER for 60+ languages | Multilingual PII detection |
| [spaCy](https://spacy.io) | Industrial NLP with NER models | Building automated redaction into workflows |
| [Amazon Comprehend](https://aws.amazon.com/comprehend/) | Managed NLP service with PII detection | AWS-native workflows |
| [Google Cloud DLP](https://cloud.google.com/sensitive-data-protection) | Cloud-based sensitive data detection | GCP-native workflows |

### Example: Microsoft Presidio

```python
# pip install presidio-analyzer presidio-anonymizer
# python -m spacy download en_core_web_lg

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "My name is Rahul Sharma and my email is rahul@sombyte.in"

results = analyzer.analyze(text=text, language="en")
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
print(anonymized.text)
# "My name is <PERSON> and my email is <EMAIL_ADDRESS>"
```

### Manual Approach (No Tools)

For quick, one-off redaction:

1. Before pasting into any AI chat, scan for: names, emails, phone numbers, company names, addresses, account numbers
2. Replace them with generic placeholders: "My company" instead of "Acme Corp", "the CEO" instead of "John Smith"
3. After getting the response, mentally map the placeholders back

This covers the 80% case for casual Tier 2 use.

### What PII Redaction Does NOT Catch

- **Contextual identifiers**: "I'm the only AI startup founder in my small town who previously worked at [specific company]"
- **Behavioral fingerprints**: Unique writing style, timezone patterns, topic combinations
- **Indirect references**: "My building on 5th and Main"
- **Domain-specific identifiers**: Employee IDs, internal ticket numbers, proprietary terminology

If the content itself is sensitive enough that you wouldn't want *anyone* to see it, use Tier 1.

## Provider Selection

Not all providers on OpenRouter have the same data policies. When routing through OpenRouter, prefer providers that explicitly commit to not logging API inputs or using them for training. OpenRouter's model listing includes data policy information — check before selecting a model.

## Limitations of Tier 2

- **Content is still seen during inference.** The model provider processes your tokens. They just can't link them to you.
- **OpenRouter knows your identity.** You're trusting one intermediary instead of many providers. Review their [privacy policy](https://openrouter.ai/privacy).
- **PII redaction is imperfect.** No tool catches everything. Be mindful of context.
- **Conversation context can leak identity.** If you discuss highly specific scenarios ("I'm building an ATS for Indian SMBs using FastAPI"), the content itself may be identifying even without explicit PII.
