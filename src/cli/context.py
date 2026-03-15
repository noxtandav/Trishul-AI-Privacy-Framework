"""
ContextBuilder — builds minimal, privacy-aware context for LLM calls.

The CLI agent should never send your entire codebase to the LLM. This module
builds a focused context window for each step, optionally redacting PII and
anonymizing file paths for Tier 2 usage.
"""

import os

from ..pii_redactor import PIIRedactor, RedactionMapping


class ContextBuilder:
    """Builds minimal, privacy-aware context for LLM calls."""

    def __init__(self, project_root: str, redactor: PIIRedactor, tier: int):
        self.project_root = project_root
        self.redactor = redactor
        self.tier = tier
        self.mapping = RedactionMapping()

    def build_context(self, task: str, relevant_files: list[str]) -> str:
        """
        Build a focused context string from relevant files.
        Only includes files the LLM needs for the current step.
        """
        context_parts = []

        for filepath in relevant_files:
            full_path = os.path.join(self.project_root, filepath)
            if not os.path.isfile(full_path):
                continue

            with open(full_path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            if self.tier == 2:
                content = self.redactor.redact(content, self.mapping)
                filepath = self._anonymize_path(filepath)

            context_parts.append(f"--- {filepath} ---\n{content}")

        full_context = "\n\n".join(context_parts)

        if self.tier == 2:
            full_context = self.redactor.redact(full_context, self.mapping)

        return full_context

    def _anonymize_path(self, filepath: str) -> str:
        """Replace project-specific path components with generic ones."""
        return os.path.relpath(filepath, self.project_root)

    def rehydrate(self, response: str) -> str:
        """Restore original values in LLM response."""
        return self.mapping.rehydrate(response)
