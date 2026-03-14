# Threat Model Summary

## What Each Tier Protects Against

| Threat | Tier 3 | Tier 2 | Tier 1 (Cloud) | Tier 1 (Local) |
|--------|--------|--------|-----------------|-----------------|
| Provider builds a persistent profile of you | No | Yes | Yes | Yes |
| Provider links your conversations across sessions | No | Yes | Yes | Yes |
| Provider uses your data for training | No | Varies | Yes (contractual) | Yes |
| Provider sees your content during inference | No | No | AWS/Azure sees it | Yes |
| Third party intercepts data in transit | TLS only | TLS only | Yes (VPC endpoint) | Yes (air-gapped) |
| Government subpoena to provider | No | Partial (OpenRouter) | Partial (AWS/Azure) | Yes |
| Data breach at provider | No | Content exposed | Content exposed | Yes |
| Your local database is compromised | N/A | Encrypt it | Encrypt it | Encrypt it |

## Trust Boundaries

```
Tier 3:  You → Provider (full trust)
Tier 2:  You → OpenRouter → Provider (trust OpenRouter with identity,
                                       provider sees anonymous content)
Tier 1a: You → AWS/Azure (trust cloud infra, not model provider)
Tier 1b: You → Your hardware (trust no one)
```
