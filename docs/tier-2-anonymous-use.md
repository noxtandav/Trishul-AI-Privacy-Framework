# Tier 2: Anonymous Use (Identity Delinking)

**Privacy Level:** Medium — content is seen by model providers during inference, but not linked to your identity
**Best For:** Business strategy, competitive research, personal reflections, travel planning, sensitive brainstorming
**Setup Effort:** Moderate (a weekend project)

## The Core Idea

You build your own chat interface that routes requests through an intermediary (like OpenRouter) to model providers. The model provider sees the content of each request but has no idea who sent it. There's no account, no email, no persistent session on their end. Each API call is a stateless, anonymous request.

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

**OpenRouter acts as a privacy buffer.** Your account is with OpenRouter (one entity to trust), and they proxy requests to dozens of model providers without passing your identity downstream.

## What You Need to Build

1. **A chat frontend** — web app or terminal UI
2. **A backend server** — manages chat history, routes requests
3. **A local database** — stores your conversation history (encrypted)
4. **A PII redaction layer** — strips identifying information before API calls
5. **An OpenRouter account** — for model routing

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    YOUR INFRASTRUCTURE                        │
│                                                              │
│  ┌────────────┐    ┌────────────────┐    ┌───────────────┐  │
│  │  Chat UI   │───▶│  Backend API   │───▶│ PII Redaction │  │
│  │ (Frontend) │    │  (FastAPI /    │    │   Middleware   │  │
│  └────────────┘    │   Express)     │    └───────┬───────┘  │
│                    └───────┬────────┘            │           │
│                            │                     │           │
│                    ┌───────▼────────┐            │           │
│                    │  Encrypted DB  │            │           │
│                    │  (SQLite +     │            │           │
│                    │   SQLCipher)   │            │           │
│                    └────────────────┘            │           │
└──────────────────────────────────────────────────┼───────────┘
                                                   │
                                          ┌────────▼────────┐
                                          │   OpenRouter    │
                                          │   (Routing)     │
                                          └────────┬────────┘
                                                   │
                              ┌─────────────┬──────┴──────┬─────────────┐
                              ▼             ▼             ▼             ▼
                          Anthropic      Google       DeepSeek      Mistral
                          (Claude)      (Gemini)

                     ─── These providers see anonymous, stateless requests ───
```

## Chat History Management

Your backend maintains full conversation history locally. When resuming a conversation, you load the history from your database and include the relevant context in the API call. The model provider never stores it — they just see a single request with some context, process it, and return a response.

See [`examples/tier2_chat_flow.py`](../examples/tier2_chat_flow.py) for a working example.

## PII Redaction: The Critical Layer

Before any message leaves your infrastructure, a redaction layer strips out identifying information — names, emails, phone numbers, company names, addresses — and replaces them with generic placeholders. When the response comes back, you can optionally rehydrate the placeholders.

The PII redaction engine is implemented in [`src/pii_redactor/`](../src/pii_redactor/). It uses a layered approach:

1. **Custom dictionary** — catch context-specific terms you define (your company name, project names)
2. **Regex patterns** — catch structured PII (emails, phones, IPs, credit cards, Aadhaar, PAN)
3. **Named Entity Recognition (NER)** — catch unstructured PII (names, organizations, locations)

### What Gets Redacted

| Category | Examples | Detection Method |
|----------|----------|-----------------|
| **Email addresses** | user@domain.com | Regex |
| **Phone numbers** | +91-98765-43210, (555) 123-4567 | Regex |
| **Indian PAN** | ABCDE1234F | Regex |
| **Indian Aadhaar** | 1234 5678 9012 | Regex |
| **US SSN** | 123-45-6789 | Regex |
| **Credit card numbers** | 4111-1111-1111-1111 | Regex |
| **IP addresses** | 192.168.1.1 | Regex |
| **URLs** | https://mycompany.com/internal | Regex |
| **Person names** | "Rahul Sharma", "John" | NER (spaCy) |
| **Organizations** | "Google", "Reserve Bank of India" | NER (spaCy) |
| **Locations** | "Mumbai", "Silicon Valley" | NER (spaCy) |
| **Custom terms** | Your company name, project codenames | Dictionary |

### What Redaction Does NOT Catch

PII redaction is a best-effort defense. It will miss:

- **Contextual identifiers**: "I'm the only AI startup founder in my small town who previously worked at [specific company]" — this is identifying even without explicit PII.
- **Behavioral fingerprints**: Unique writing style, timezone patterns, topic combinations.
- **Indirect references**: "My building on 5th and Main" — not flagged as PII but could identify you.
- **Domain-specific identifiers**: Employee IDs, internal ticket numbers, proprietary terminology.

Mitigation: For Tier 2, accept that content-level privacy is not the goal — identity delinking is. If the content itself is sensitive enough that you wouldn't want *anyone* to see it, use Tier 1.

## Provider Selection

Not all providers on OpenRouter have the same data policies. When routing through OpenRouter, prefer providers that explicitly commit to not logging API inputs or using them for training.

See [`examples/tier2_chat_flow.py`](../examples/tier2_chat_flow.py) for an example of filtering privacy-respecting models.

## Database Encryption

Your local chat history is sensitive — it contains the unredacted versions of all your conversations. Encrypt it at rest using SQLCipher.

See [`examples/database_setup.py`](../examples/database_setup.py) for the full setup.

## CLI Agent for Multi-Step Tasks

For coding and complex multi-step workflows, the Trishul CLI agent operates at Tier 2 by default. It keeps all file I/O and command execution local while routing LLM reasoning through OpenRouter anonymously.

See [cli-agent.md](cli-agent.md) for full documentation, including the agent loop, context builder, and unified Web + CLI architecture.

## Limitations of Tier 2

- **Content is still seen during inference.** The model provider processes your tokens. They just can't link them to you.
- **OpenRouter knows your identity.** You're trusting one intermediary instead of many providers. Review their data retention policy.
- **PII redaction is imperfect.** Regex-based approaches miss context-specific identifiers. NER models are better but not foolproof.
- **Conversation context can leak identity.** If you discuss highly specific scenarios ("I'm building an ATS for Indian SMBs using FastAPI"), the content itself may be identifying even without explicit PII. Be mindful of what you include.
