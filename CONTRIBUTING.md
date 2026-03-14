# Contributing to Trishul

Contributions to Trishul are welcome! This is a living framework and benefits from community input.

## Areas We Need Help With

- **PII patterns** — Additional regex patterns for different countries and jurisdictions (e.g., Canadian SIN, UK National Insurance numbers, EU VAT IDs)
- **Alternative routing providers** — Documentation or examples for providers other than OpenRouter
- **Benchmarks** — Comparing local model quality vs. frontier models for specific tasks (financial analysis, legal review, etc.)
- **UI/UX designs** — Mockups or implementations for the tier selection interface
- **Docker compose** — Configurations for the full self-hosted Tier 2 stack
- **Mobile implementations** — iOS or Android chat clients with tier support

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b add-canadian-pii-patterns`)
3. Make your changes
4. Submit a pull request with a clear description of what you added

## Adding PII Patterns

To add patterns for a new country or data type, edit `src/pii_redactor/patterns.py`:

```python
# Add your pattern to the PII_PATTERNS dict
"new_pattern_name": re.compile(
    r'your-regex-here'
),
```

Include test cases that show what the pattern matches and what it doesn't.

## Code Style

- Python code should be readable and well-commented
- Follow existing patterns in the codebase
- Keep examples self-contained and runnable

## Documentation

- Keep docs concise and practical
- Include real-world examples where possible
- If you're documenting a new provider or tool, include setup instructions

## Questions?

Open an issue if you have questions about contributing.
