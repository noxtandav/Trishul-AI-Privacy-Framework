# Architecture Overview

## Unified Trishul Client

The recommended approach is a single self-hosted chat application — your **Trishul client** — that supports all three tiers, with routing based on the sensitivity of each conversation.

```
┌──────────────────────────────────────────────────────────────────────┐
│                      TRISHUL CHAT APPLICATION                        │
│                                                                      │
│  ┌────────────┐    ┌───────────────────────────────────────────────┐ │
│  │            │    │              ROUTING ENGINE                    │ │
│  │  Chat UI   │    │                                               │ │
│  │            │───▶│  Tier 3 ──▶ Direct API (Claude/GPT/Gemini)   │ │
│  │ [Tier      │    │                                               │ │
│  │  Selector] │    │  Tier 2 ──▶ PII Redactor ──▶ OpenRouter ──▶  │ │
│  │            │    │             Anonymous model providers          │ │
│  └────────────┘    │                                               │ │
│                    │  Tier 1 ──▶ AWS Bedrock / Local Ollama        │ │
│                    │                                               │ │
│                    └───────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    ENCRYPTED LOCAL DATABASE                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │  │
│  │  │Conversations │  │  Messages    │  │ Redaction Mappings   │ │  │
│  │  │(id, title,   │  │(id, conv_id, │  │(placeholder → real   │ │  │
│  │  │ tier, dates) │  │ role, content│  │ value, per session)  │ │  │
│  │  └──────────────┘  │ redacted)    │  └──────────────────────┘ │  │
│  │                    └──────────────┘                            │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Tier Selection UX

When starting a new conversation, the user selects the privacy tier. The tier can be displayed as a simple indicator in the chat header:

- **Open** — Tier 3, direct provider access
- **Anonymous** — Tier 2, identity delinked via OpenRouter
- **Isolated** — Tier 1, Bedrock or local model

The tier choice should be immutable for a conversation — you don't want to accidentally send Tier 1 content through a Tier 3 channel.

## Examples by Use Case

| Use Case | Recommended Tier | Why |
|----------|-----------------|-----|
| "How do I write a for loop in Python?" | Tier 3 | Zero sensitivity |
| "What's the best restaurant in Tokyo?" | Tier 3 | No personal data |
| "Help me plan a marketing strategy for my SaaS product" | Tier 2 | Competitive strategy, don't want it profiled |
| "Analyze my competitors and their pricing" | Tier 2 | Business intelligence, identity-sensitive |
| "I'm feeling stressed about my startup failing" | Tier 2 | Personal emotional content |
| "Review my tax return and suggest deductions" | Tier 1 | Financial documents with PII |
| "Analyze this bank statement for spending patterns" | Tier 1 | Sensitive financial data |
| "Summarize this legal contract for my company" | Tier 1 | Confidential business documents |
| "What medications interact with my prescription?" | Tier 1 | Health information |
