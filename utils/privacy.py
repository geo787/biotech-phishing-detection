"""Privacy helpers: simple redaction utilities for logs and reports.
These are intentionally conservative and replace common PHI-like patterns.
"""
import re

# Patterns: SSN-like, long digit sequences (MRNs), email addresses
_RE_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_RE_LONG_DIGITS = re.compile(r"\b\d{6,}\b")
_RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def redact(text: str) -> str:
    if not text:
        return text
    # Replace emails
    text = _RE_EMAIL.sub('[REDACTED_EMAIL]', text)
    # Replace SSN-like
    text = _RE_SSN.sub('[REDACTED_SSN]', text)
    # Replace long digit sequences (MRN, account numbers)
    text = _RE_LONG_DIGITS.sub('[REDACTED_NUM]', text)
    return text


def maybe_redact(text: str, do_redact: bool = True) -> str:
    return redact(text) if do_redact else text
