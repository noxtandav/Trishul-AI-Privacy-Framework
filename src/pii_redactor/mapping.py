"""
RedactionMapping — maintains consistent placeholder-to-original mappings
within a conversation session.

One instance per conversation ensures that "Rahul Sharma" always maps to
[PERSON_1] across all messages in that conversation.
"""

from dataclasses import dataclass, field


@dataclass
class RedactionMapping:
    """Stores the mapping between original values and placeholders.
    One instance per conversation session."""

    _forward: dict = field(default_factory=dict)   # original → placeholder
    _reverse: dict = field(default_factory=dict)   # placeholder → original
    _counters: dict = field(default_factory=dict)   # category → count

    def get_or_create(self, original: str, category: str) -> str:
        """Get existing placeholder or create a new one."""
        key = f"{category}:{original.lower()}"
        if key not in self._forward:
            count = self._counters.get(category, 0) + 1
            self._counters[category] = count
            placeholder = f"[{category.upper()}_{count}]"
            self._forward[key] = placeholder
            self._reverse[placeholder] = original
        return self._forward[key]

    def rehydrate(self, text: str) -> str:
        """Replace all placeholders with original values."""
        for placeholder, original in self._reverse.items():
            text = text.replace(placeholder, original)
        return text

    def to_dict(self) -> dict:
        """Serialize for database storage."""
        return {
            "forward": self._forward,
            "reverse": self._reverse,
            "counters": self._counters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RedactionMapping":
        """Deserialize from database storage."""
        mapping = cls()
        mapping._forward = data.get("forward", {})
        mapping._reverse = data.get("reverse", {})
        mapping._counters = data.get("counters", {})
        return mapping
