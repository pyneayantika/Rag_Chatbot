"""
Retriever for the HDFC Mutual Fund RAG Chatbot.

Applies guardrails (PII / advisory checks) before performing
similarity search against the ChromaDB vectorstore. Filters
results by detected scheme name when possible.
"""

from __future__ import annotations

from langchain_core.documents import Document

from src.guardrails.intent_classifier import (
    contains_pii,
    is_advisory,
    PII_MESSAGE,
    REFUSAL_MESSAGE,
)
from src.ingestion.embedder import get_vectorstore

# ---------------------------------------------------------------------------
# Scheme keyword mapping
# Maps a canonical scheme key to:
#   - keywords: phrases to detect in the user query (case-insensitive)
#   - scheme_names: matching scheme_name metadata values in ChromaDB
# ---------------------------------------------------------------------------
SCHEME_KEYWORDS: dict[str, dict] = {
    "hdfc_midcap": {
        "keywords": ["mid cap", "midcap", "mid-cap"],
        "scheme_names": [
            "mutual-funds_hdfc-mid-cap-opportunities-fund-direct-growth",
            "hdfc-mid-cap-fund_direct",
        ],
    },
    "hdfc_flexicap": {
        "keywords": ["flexi cap", "flexicap", "flexi-cap", "equity fund"],
        "scheme_names": [
            "mutual-funds_hdfc-equity-fund-direct-growth",
            "hdfc-flexi-cap-fund_direct",
        ],
    },
    "hdfc_elss": {
        "keywords": ["elss", "tax saver", "tax saving", "80c", "lock-in", "lock in"],
        "scheme_names": [
            "mutual-funds_hdfc-elss-tax-saver-fund-direct-plan-growth",
            "hdfc-elss-tax-saver_direct",
        ],
    },
    "hdfc_largecap": {
        "keywords": ["large cap", "largecap", "large-cap"],
        "scheme_names": [
            "mutual-funds_hdfc-large-cap-fund-direct-growth",
            "hdfc-large-cap-fund_direct",
        ],
    },
    "hdfc_smallcap": {
        "keywords": ["small cap", "smallcap", "small-cap"],
        "scheme_names": [
            "mutual-funds_hdfc-small-cap-fund-direct-growth",
            "hdfc-small-cap-fund_direct",
        ],
    },
}

# Scheme-agnostic / general documents (AMFI, SEBI, TER, SID, KIM, etc.)
GENERAL_SCHEME_NAMES: list[str] = [
    "investor",
    "categorizationofmutualfundschemes",
    "typesofmutualfundschemes",
    "articles_mutual-fund",
    "fund-documents_sid",
    "fund-documents_kim",
    "total-expense-ratio-of-mutual-fund-schemes_notices",
    "investor-charter_mutual-funds.html",
    "oct-2017_categorization-and-rationalization-of-mutual-fund-schemes_36199.html",
    "jan-2018_performance-benchmarking-of-mutual-fund-schemes_37415.html",
]


# ============================================================================
# Scheme detection
# ============================================================================

def _detect_scheme(query: str) -> list[str] | None:
    """Detect which scheme the query is about.

    Args:
        query: The user's input text.

    Returns:
        A list of matching ``scheme_name`` metadata values,
        or ``None`` if no specific scheme is detected.
    """
    query_lower = query.lower()
    for _key, mapping in SCHEME_KEYWORDS.items():
        if any(kw in query_lower for kw in mapping["keywords"]):
            return mapping["scheme_names"]
    return None


# ============================================================================
# Main retrieval function
# ============================================================================

def retrieve(query: str, k: int = 3) -> list[Document]:
    """Retrieve the top-k most relevant chunks for a user query.

    Applies guardrails before retrieval:
    - Blocks queries containing PII (PAN / Aadhaar).
    - Blocks advisory / opinion queries.

    Filters ChromaDB results by detected scheme name when the
    query mentions a specific fund. General documents (AMFI,
    SEBI, TER, SID/KIM) are always included in the search scope.

    Args:
        query: The user's natural-language question.
        k: Number of top results to return (default: 3).

    Returns:
        A list of ``Document`` objects with full metadata.

    Raises:
        ValueError: If the query contains PII or is advisory.
    """
    # --- Guardrails ---
    if contains_pii(query):
        raise ValueError(PII_MESSAGE)

    if is_advisory(query):
        raise ValueError(REFUSAL_MESSAGE)

    # --- Scheme detection ---
    detected = _detect_scheme(query)

    if detected is not None:
        # Include both scheme-specific and general documents
        allowed_names = detected + GENERAL_SCHEME_NAMES
        metadata_filter = {"scheme_name": {"$in": allowed_names}}
    else:
        # No specific scheme — search across all documents
        metadata_filter = None

    # --- Retrieval ---
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(
        query=query,
        k=k,
        filter=metadata_filter,
    )

    return results
