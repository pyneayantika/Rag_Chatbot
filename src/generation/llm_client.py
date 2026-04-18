"""
LLM client for the HDFC Mutual Fund RAG Chatbot.

Uses Groq (via ``langchain-groq``) with temperature=0 to produce
factual, context-only responses. No investment advice, no opinions,
no PII handling.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

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

MAX_CONTEXT_CHUNKS = 1
MAX_CHARS_PER_CHUNK = 600
RATE_LIMIT_RETRIES = 2
MAX_OUTPUT_TOKENS = 160


# ============================================================================
# LLM initialisation
# ============================================================================

def _get_llm() -> ChatGroq:
    """Initialise the Groq LLM client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment")

    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=api_key,
        max_tokens=MAX_OUTPUT_TOKENS,
        max_retries=2,
    )


# ============================================================================
# Context formatting
# ============================================================================

def _format_context(chunks: list[Document]) -> str:
    """Format retrieved chunks into a numbered context block."""
    parts: list[str] = []
    for idx, chunk in enumerate(chunks[:MAX_CONTEXT_CHUNKS], start=1):
        meta = chunk.metadata
        content = chunk.page_content[:MAX_CHARS_PER_CHUNK]
        parts.append(
            f"[Context {idx}]\n"
            f"Source URL: {meta.get('source_url', 'N/A')}\n"
            f"Last updated: {meta.get('scrape_date', 'N/A')}\n"
            f"{content}"
        )
    return "\n\n".join(parts)


def _rate_limit_fallback(chunks: list[Document]) -> str:
    if not chunks:
        return "I do not have verified information for this. Please check https://www.hdfcfund.com"

    top = chunks[0]
    meta = top.metadata or {}
    source_url = meta.get("source_url", "https://www.hdfcfund.com")
    last_updated = meta.get("scrape_date", meta.get("last_updated", "N/A"))
    snippet = " ".join(top.page_content.split())[:220]

    return (
        f"I could not generate a full response right now due to high traffic. "
        f"Verified snippet: {snippet}\n"
        f"Source: {source_url}\n"
        f"Last updated from sources: {last_updated}"
    )


# ============================================================================
# Main generation function
# ============================================================================

def generate_response(query: str, chunks: list[Document]) -> str:
    """Generate a factual response using Groq with retrieved context.

    Args:
        query: The user's natural-language question.
        chunks: List of relevant ``Document`` objects from the retriever.

    Returns:
        The LLM's response as a string.

    Raises:
        ValueError: If ``GROQ_API_KEY`` is not set in the environment.
    """
    try:
        llm = _get_llm()

        context = _format_context(chunks)
        user_message = f"{context}\n\nQuestion: {query}"

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        for attempt in range(RATE_LIMIT_RETRIES + 1):
            try:
                response = llm.invoke(messages)
                return response.content
            except Exception as exc:
                error_msg = str(exc).lower()

                if (
                    "429" in str(exc)
                    or "rate limit" in error_msg
                    or "resource_exhausted" in error_msg
                ) and attempt < RATE_LIMIT_RETRIES:
                    time.sleep(3 * (attempt + 1))
                    continue

                if "timeout" in error_msg or "deadline" in error_msg:
                    return "Response timeout. Please try again."

                if "429" in str(exc) or "rate limit" in error_msg or "resource_exhausted" in error_msg:
                    return _rate_limit_fallback(chunks)

                raise

    except ValueError as exc:
        return str(exc)

    except Exception as exc:
        error_msg = str(exc).lower()
        if "too many requests. please wait 30 seconds." in error_msg:
            return _rate_limit_fallback(chunks)
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
