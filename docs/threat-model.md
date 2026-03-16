# Threat Model Summary

## What Each Tier Protects Against

| Threat | Tier 3 | Tier 2 | Tier 1 (Cloud) | Tier 1 (Local) |
|--------|--------|--------|-----------------|-----------------|
| Provider builds a persistent profile of you | Exposed | Protected | Protected | Protected |
| Provider links your conversations across sessions | Exposed | Protected | Protected | Protected |
| Provider uses your data for training | Exposed | Varies by provider | Contractually protected | Protected |
| Provider sees your content during inference | Exposed | Exposed | AWS/Azure processes it | Protected |
| Third party intercepts data in transit | TLS only | TLS only | VPC endpoint available | Air-gapped |
| Government subpoena to provider | Exposed | OpenRouter only | AWS/Azure only | Protected |
| Data breach at provider | Exposed | Content exposed (no identity) | Content exposed | Protected |

## Trust Boundaries

```
Tier 3:  You ──→ Provider (full trust in provider)
Tier 2:  You ──→ OpenRouter ──→ Provider (trust OpenRouter with identity,
                                           provider sees anonymous content)
Tier 1a: You ──→ AWS/Azure (trust cloud infra, not model provider)
Tier 1b: You ──→ Your hardware (trust no one)
```

## Key Takeaways

- **No tier is perfect.** Even Tier 1 Local requires trusting your hardware, OS, and the model weights you downloaded.
- **Tier 2's main value is identity delinking**, not content protection. The provider still processes your content during inference.
- **Tier 1 Cloud trades one trust relationship for another.** You're no longer trusting the model provider, but you are trusting AWS/Azure infrastructure.
- **The biggest practical risk for most people is Tier 3 profiling** — the slow accumulation of personal data across hundreds of conversations over months and years.
