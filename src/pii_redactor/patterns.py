"""
PII regex patterns for structured data detection.

To add patterns for a new country or data type, add a new entry to the
PII_PATTERNS dict. The key is the category name (used in placeholders like
[EMAIL_1], [PHONE_1]) and the value is a compiled regex pattern.

See CONTRIBUTING.md for guidelines on adding new patterns.
"""

import re

PII_PATTERNS = {
    "email": re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ),
    "phone": re.compile(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b'
    ),
    "ip_address": re.compile(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ),
    "credit_card": re.compile(
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    ),
    "ssn": re.compile(
        r'\b\d{3}-\d{2}-\d{4}\b'
    ),
    "aadhaar": re.compile(
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    ),
    "pan_card": re.compile(
        r'\b[A-Z]{5}\d{4}[A-Z]\b'
    ),
    "url": re.compile(
        r'https?://[^\s<>\"\']+|www\.[^\s<>\"\']+',
    ),
    "date_of_birth": re.compile(
        r'\b(?:DOB|Date of Birth|Born|Birthday)[:\s]*'
        r'(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
        re.IGNORECASE
    ),
}
