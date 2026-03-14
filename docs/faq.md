# FAQ

**Q: Can I use a VPN with Tier 2 for extra anonymity?**
A: The OpenRouter API calls already go server-to-server from your backend, so the model provider never sees your IP. A VPN would only mask your IP from OpenRouter itself. If you're running the backend on a VPS, your IP is already that of the VPS provider, not your personal IP.

**Q: What about self-hosted open-source models for Tier 2?**
A: You could skip OpenRouter entirely and run open-source models on rented GPU instances (Lambda Labs, Vast.ai, RunPod). This eliminates the intermediary but requires more infrastructure management. The model quality tradeoff is the same as Tier 1 local models.

**Q: Is OpenRouter trustworthy?**
A: OpenRouter is a single point of trust in Tier 2. Review their privacy policy and data retention practices. The tradeoff is trusting one company (OpenRouter) instead of five (each model provider). You can mitigate this further by self-hosting a routing layer, but that significantly increases complexity.

**Q: How much does each tier cost?**
A: Tier 3 is whatever your existing subscriptions cost ($0-20/month). Tier 2 adds OpenRouter API costs (typically $1-10/month for moderate use) plus minimal hosting for your backend. Tier 1 with Bedrock adds 2-5x the token cost vs direct API. Tier 1 local requires $500-2000+ in GPU hardware upfront.

**Q: What if I accidentally use the wrong tier?**
A: That's why the tier should be set per-conversation and immutable. The UI should make the current tier clearly visible. Consider adding a confirmation prompt when creating a Tier 3 conversation: "This conversation will be sent directly to the provider with your identity. Continue?"

**Q: Can the PII redactor handle languages other than English?**
A: The regex patterns work for universal formats (emails, phone numbers, card numbers). The spaCy NER model (`en_core_web_sm`) is English-only. For multilingual support, use `xx_ent_wiki_sm` (multilingual NER) or language-specific models. Custom dictionary terms work regardless of language.

**Q: What about file uploads (PDFs, images)?**
A: For Tier 2, you'd need to redact PII from files before uploading, which is significantly harder than text redaction. For documents with embedded PII (financial statements, ID scans), use Tier 1. Text extraction + redaction + sending as text (rather than the original file) is a reasonable middle ground.
