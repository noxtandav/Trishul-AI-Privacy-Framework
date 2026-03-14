"""
PII Redaction Engine for Tier 2 Anonymous AI Usage.

Strips personally identifiable information from text before sending
to model providers. Maintains a reversible mapping so responses can
be rehydrated with original values.

Dependencies:
    pip install spacy
    python -m spacy download en_core_web_sm
"""

import re
from typing import Optional

from .mapping import RedactionMapping
from .patterns import PII_PATTERNS


class PIIRedactor:
    """Multi-layered PII redaction engine."""

    def __init__(self, custom_terms: Optional[dict] = None, use_ner: bool = True):
        """
        Initialize the redactor.

        Args:
            custom_terms: Dict mapping category -> list of terms to redact.
                          Example: {"company": ["Acme Corp", "Acme"],
                                    "project": ["Project Phoenix"]}
            use_ner: Whether to use spaCy NER for name/org/location detection.
        """
        self.custom_terms = custom_terms or {}
        self.use_ner = use_ner
        self._nlp = None

        if use_ner:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
            except (ImportError, OSError):
                print(
                    "Warning: spaCy not available. "
                    "Install with: pip install spacy && "
                    "python -m spacy download en_core_web_sm"
                )
                self.use_ner = False

    def redact(self, text: str, mapping: RedactionMapping) -> str:
        """
        Redact all PII from text using layered approach.

        Order matters — custom terms first (most specific),
        then regex (structured patterns), then NER (broad catch).

        Args:
            text: The text to redact.
            mapping: RedactionMapping instance for this conversation.
                     Ensures consistent placeholders across messages.

        Returns:
            Redacted text with placeholders.
        """
        # Layer 1: Custom dictionary (most specific, highest priority)
        for category, terms in self.custom_terms.items():
            # Sort by length descending so "Acme Corporation" is matched
            # before "Acme"
            for term in sorted(terms, key=len, reverse=True):
                if term.lower() in text.lower():
                    placeholder = mapping.get_or_create(term, category)
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    text = pattern.sub(placeholder, text)

        # Layer 2: Regex patterns (structured PII)
        for category, pattern in PII_PATTERNS.items():
            matches = pattern.findall(text)
            for match in matches:
                placeholder = mapping.get_or_create(match, category)
                text = text.replace(match, placeholder)

        # Layer 3: NER (unstructured PII — names, organizations, locations)
        if self.use_ner and self._nlp:
            doc = self._nlp(text)
            # Process entities in reverse order to preserve string positions
            entities = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
            for ent in entities:
                # Only redact relevant entity types
                if ent.label_ in ("PERSON", "ORG", "GPE", "LOC", "FAC"):
                    # Skip if already redacted (contains placeholder brackets)
                    if "[" in ent.text and "]" in ent.text:
                        continue

                    category_map = {
                        "PERSON": "person",
                        "ORG": "org",
                        "GPE": "location",
                        "LOC": "location",
                        "FAC": "location",
                    }
                    category = category_map[ent.label_]
                    placeholder = mapping.get_or_create(ent.text, category)
                    text = text[:ent.start_char] + placeholder + text[ent.end_char:]

        return text

    def redact_messages(
        self, messages: list[dict], mapping: RedactionMapping
    ) -> list[dict]:
        """
        Redact PII from a list of chat messages.

        Args:
            messages: List of {"role": "user/assistant", "content": "..."} dicts.
            mapping: RedactionMapping instance for this conversation.

        Returns:
            New list with redacted content. Original list is not modified.
        """
        redacted = []
        for msg in messages:
            redacted.append({
                "role": msg["role"],
                "content": self.redact(msg["content"], mapping),
            })
        return redacted
