# FAQ

**Q: Do I need to build anything to use the Trishul framework?**
A: No. Trishul is a thinking framework, not a software product. All the tools you need already exist — you just need to choose the right ones for each privacy tier and be intentional about which tier you use for each conversation.

**Q: Can I use a VPN with Tier 2 for extra anonymity?**
A: If you're using OpenRouter's API directly (from a CLI tool or self-hosted UI), the model provider never sees your IP — only OpenRouter's. A VPN would only mask your IP from OpenRouter itself. For most people, this is unnecessary.

**Q: What about self-hosted open-source models for Tier 2?**
A: You could skip OpenRouter entirely and run open-source models on rented GPU instances (Lambda Labs, Vast.ai, RunPod). This eliminates the intermediary but requires more infrastructure management and gives you lower model quality.

**Q: Is OpenRouter trustworthy?**
A: OpenRouter is a single point of trust in Tier 2. Review their [privacy policy](https://openrouter.ai/privacy). The tradeoff is trusting one company (OpenRouter) instead of five (each model provider separately).

**Q: How much does each tier cost?**
A: Tier 3 is whatever your existing subscriptions cost ($0-20/month). Tier 2 adds OpenRouter API costs (typically $1-10/month for moderate use). Tier 1 with Bedrock adds 2-5x the per-token cost vs direct API. Tier 1 local requires $500-2000+ in GPU hardware upfront.

**Q: What if I accidentally use the wrong tier?**
A: Build the habit of pausing before each conversation: "Is this sensitive? Is the content itself sensitive, or just the identity link?" The decision flowchart in the README becomes second nature after a week. Using shell aliases (`ai`, `ai-anon`, `ai-secure`) also helps make the choice explicit.

**Q: Can PII redaction tools handle languages other than English?**
A: Microsoft Presidio supports multiple languages. Stanza supports 60+ languages for NER. For manual redaction, the approach is language-agnostic — just replace identifying terms with placeholders before pasting.

**Q: What about file uploads (PDFs, images)?**
A: For Tier 2, you'd need to redact PII from files before uploading — significantly harder than text. For documents with embedded PII (financial statements, ID scans), use Tier 1 directly. Text extraction + manual redaction + sending as text (rather than the original file) is a reasonable middle ground.

**Q: Daniel Miessler's PAI/Kai system doesn't address privacy at all. Why should I care?**
A: Daniel's system is optimized for maximum productivity with full trust in Anthropic (essentially all Tier 3). That's a valid choice. Trishul exists for people who want to be intentional about *which* conversations get that level of trust and which don't. The two approaches are complementary, not competing.

**Q: What's the simplest way to start using Trishul?**
A: Add three shell aliases (see the "Practical Setup" section in the README): one for open use, one for anonymous use via OpenRouter, one for isolated use via Bedrock. Start by just being mindful about which alias you use for each task.
