"""
Security & Sanitization utility for Agent 4 - "The Background Check".
Ensures that sensitive system credentials, raw password hashes, or personally
identifiable financial data are stripped before synthesis.
"""

import re
from typing import Any, Dict, List, Union

# Pattern to detect sensitive field names
SENSITIVE_KEY_PATTERNS = [
    re.compile(r"pass(word)?(_?hash|_?salt)?", re.IGNORECASE),
    re.compile(r"pwd", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"api_?key", re.IGNORECASE),
    re.compile(r"auth(entication)?", re.IGNORECASE),
    re.compile(r"ssn|social_?security", re.IGNORECASE),
    re.compile(r"credit_?card|card_?num(ber)?|cvv|cvc", re.IGNORECASE),
    re.compile(r"bank_?(account|routing|details)", re.IGNORECASE),
    re.compile(r"pin(_?code)?", re.IGNORECASE),
    re.compile(r"financial_?(data|account|balance)", re.IGNORECASE),
    re.compile(r"private_?key", re.IGNORECASE),
]


def is_sensitive_key(key: str) -> bool:
    """Checks whether a dictionary key corresponds to sensitive/restricted data."""
    if not isinstance(key, str):
        return False
    return any(pattern.search(key) for pattern in SENSITIVE_KEY_PATTERNS)


def sanitize_dbms_record(data: Any) -> Any:
    """
    Recursively strips and sanitizes sensitive credentials, hashes, and financial data
    from raw DBMS records.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if is_sensitive_key(str(k)):
                continue  # Omit sensitive keys entirely
            sanitized[k] = sanitize_dbms_record(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_dbms_record(item) for item in data]
    else:
        return data
