# Trishul — The 3-Tier AI Privacy Framework

*Named after Shiva's trident (त्रिशूल) — three prongs, three tiers of protection.*

A practical guide to using AI tools while controlling how much of your personal data you expose to model providers.

---

## The Problem

When you use AI services like ChatGPT, Claude, or Gemini through their consumer apps, every conversation is tied to your account — your email, your payment info, your identity. Over weeks and months of usage, the provider accumulates a rich profile of who you are: your job, your business ideas, your travel plans, your health concerns, your financial situation, your relationships.

This isn't necessarily malicious. Memory and personalization features are genuinely useful. But the result is that multiple corporations now hold an intimate portrait of your life, and you have limited control over how that data is stored, used, or shared.

**Trishul** (त्रिशूल) provides a practical, implementable architecture for controlling your AI privacy at three distinct levels — from zero precautions to full data isolation — so you can make conscious choices about what you share and with whom.

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

## Documentation

- [Framework Overview](docs/overview.md) — Architecture, tier selection UX, and use case examples
- [Tier 3: Open Use](docs/tier-3-open-use.md) — Using AI services directly with no precautions
- [Tier 2: Anonymous Use](docs/tier-2-anonymous-use.md) — Identity delinking via OpenRouter + PII redaction
- [Tier 1: Full Isolation](docs/tier-1-full-isolation.md) — AWS Bedrock, Azure AI, or local models
- [Threat Model](docs/threat-model.md) — What each tier protects against
- [FAQ](docs/faq.md) — Common questions answered

## Code

The `src/pii_redactor/` module provides a working PII redaction engine for Tier 2:

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

```python
from src.pii_redactor import PIIRedactor, RedactionMapping

redactor = PIIRedactor(
    custom_terms={"company": ["Acme Corp"], "project": ["Project Atlas"]},
    use_ner=True,
)
mapping = RedactionMapping()

redacted = redactor.redact("Contact John at john@acme.com", mapping)
# "Contact [PERSON_1] at [EMAIL_1]"
```

See [`examples/`](examples/) for runnable scripts covering each tier.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Areas we'd especially love help with:
- PII patterns for different countries and jurisdictions
- Alternative routing providers to OpenRouter
- Benchmarks comparing local model quality vs. frontier models
- UI/UX designs for the tier selection interface
- Docker compose configurations for the full self-hosted stack

## License

Released under the [MIT License](LICENSE).

---

*Trishul (त्रिशूल) — because privacy is not binary. It's a spectrum, and you should be able to choose where you sit on it for each interaction.*
