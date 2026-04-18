"""
LLM client for the HDFC Mutual Fund RAG Chatbot.

Uses Google Gemini (via ``langchain-google-genai``) with temperature=0
to produce factual, context-only responses. No investment advice,
no opinions, no PII handling.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a facts-only FAQ assistant for HDFC Mutual Fund schemes.

STRICT RULES:
1. Answer ONLY from the provided context chunks below. Do not use any external knowledge.
2. Never give investment advice, opinions, or recommendations.
3. Keep your answer to a maximum of 3 sentences.
4. Always end your answer with exactly these two lines:
   Source: [source_url from the most relevant context chunk]
   Last updated from sources: [scrape_date from the most relevant context chunk]
5. If the context does not contain the answer, respond with exactly:
   "I do not have verified information for this. Please check https://www.hdfcfund.com"
6. Never request, reference, or process personal information (PAN, Aadhaar, account numbers).
7. Do not speculate, extrapolate, or provide forward-looking statements.
"""


# ============================================================================
# LLM initialisation
# ============================================================================

def _get_llm() -> ChatGoogleGenerativeAI:
    """Initialise the Gemini LLM client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
        timeout=60,
        max_retries=2,
    )


# ============================================================================
# Context formatting
# ============================================================================

def _format_context(chunks: list[Document]) -> str:
    """Format retrieved chunks into a numbered context block."""
    parts: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk.metadata
        parts.append(
            f"[Context {idx}]\n"
            f"Source URL: {meta.get('source_url', 'N/A')}\n"
            f"Last updated: {meta.get('scrape_date', 'N/A')}\n"
            f"{chunk.page_content}"
        )
    return "\n\n".join(parts)


# ============================================================================
# Main generation function
# ============================================================================

def generate_response(query: str, chunks: list[Document]) -> str:
    """Generate a factual response using Gemini with retrieved context.

    Args:
        query: The user's natural-language question.
        chunks: List of relevant ``Document`` objects from the retriever.

    Returns:
        The LLM's response as a string.

    Raises:
        ValueError: If ``GEMINI_API_KEY`` is not set in the environment.
    """
    llm = _get_llm()

    context = _format_context(chunks)
    user_message = f"{context}\n\nQuestion: {query}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    try:
        response = llm.invoke(messages)
        return response.content

    except Exception as exc:
        error_msg = str(exc).lower()

        if "timeout" in error_msg or "deadline" in error_msg:
            return "Response timeout. Please try again."

        if "429" in str(exc) or "rate limit" in error_msg or "resource_exhausted" in error_msg:
            return "Too many requests. Please wait 30 seconds."

        # Re-raise unexpected errors
        raise


# ---------------------------------------------------------------------------
# CLI entry-point / quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from src.retrieval.retriever import retrieve

    test_query = "What is the expense ratio of HDFC Mid Cap?"
    print(f"Query: {test_query}\n")

    print("Retrieving chunks...")
    chunks = retrieve(test_query)
    print(f"Retrieved {len(chunks)} chunks\n")

    for i, c in enumerate(chunks, 1):
        print(f"  Chunk {i}: {c.metadata.get('scheme_name', '?')} "
              f"({c.metadata.get('source_url', '?')[:60]}...)")

    print("\nGenerating response...\n")
    answer = generate_response(test_query, chunks)
    print("=" * 60)
    print(answer)
    print("=" * 60)
