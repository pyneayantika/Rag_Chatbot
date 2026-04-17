"""
Intent classifier and PII detector for the HDFC Mutual Fund RAG Chatbot.

Provides guardrails that run **before** any retrieval or LLM call:
- Advisory / opinion queries are refused with a standard message.
- Queries containing PII (PAN, Aadhaar) are blocked immediately.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Advisory keyword patterns (case-insensitive)
# ---------------------------------------------------------------------------
ADVISORY_PATTERNS: list[str] = [
    "should i",
    "is it good",
    "which is better",
    "recommend",
    "best fund",
    "is now a good time",
    "will it give",
    "expected return",
    "should i buy",
    "should i sell",
    "compare",
    "which fund",
    "will grow",
    'will my sip',
'will my investment',
'sip grow',
'will it grow',
    "is hdfc better",
    "timing",
    "should i invest",
    "is this good",
    "worth investing",
]

# ---------------------------------------------------------------------------
# PII regex patterns
# ---------------------------------------------------------------------------
PAN_PATTERN = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")
AADHAAR_PATTERN = re.compile(r"\d{4}\s\d{4}\s\d{4}")

# ---------------------------------------------------------------------------
# Standard refusal messages
# ---------------------------------------------------------------------------
REFUSAL_MESSAGE = (
    "I can only share verified facts about HDFC Mutual Fund schemes. "
    "For investment guidance please visit "
    "https://www.amfiindia.com/investor or "
    "https://www.sebi.gov.in/investors/investor-charter/mutual-funds.html"
)

PII_MESSAGE = (
    "I cannot process personal information. "
    "Please do not share PAN, Aadhaar, account numbers "
    "or any personal details."
)


# ============================================================================
# Classifier functions
# ============================================================================

def is_advisory(query: str) -> bool:
    """Check if a query is asking for investment advice or opinions.

    Args:
        query: The user's input text.

    Returns:
        ``True`` if the query matches any advisory pattern
        (case-insensitive), ``False`` otherwise.
    """
    query_lower = query.lower()
    return any(pattern in query_lower for pattern in ADVISORY_PATTERNS)


def contains_pii(query: str) -> bool:
    """Check if a query contains personally identifiable information.

    Detects:
    - **PAN** — Indian Permanent Account Number (e.g. ``ABCDE1234F``)
    - **Aadhaar** — 12-digit number in ``XXXX XXXX XXXX`` format

    Args:
        query: The user's input text.

    Returns:
        ``True`` if PAN or Aadhaar patterns are found, ``False`` otherwise.
    """
    if PAN_PATTERN.search(query.upper()):
        return True
    if AADHAAR_PATTERN.search(query):
        return True
    return False
