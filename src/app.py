"""
Streamlit chat application for the HDFC Mutual Fund FAQ Assistant.

Facts-only RAG chatbot — no investment advice, no PII handling.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so src.* imports resolve
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.guardrails.intent_classifier import (
    contains_pii,
    is_advisory,
    PII_MESSAGE,
    REFUSAL_MESSAGE,
)
from src.retrieval.retriever import retrieve
from src.generation.llm_client import generate_response

# ============================================================================
# 1. Page config
# ============================================================================
st.set_page_config(
    page_title="HDFC MF FAQ Assistant",
    page_icon=":chart_with_upwards_trend:",
)

# ============================================================================
# 2. Header
# ============================================================================
st.title(":chart_with_upwards_trend: HDFC Mutual Fund FAQ Assistant")
st.caption("Powered by Groww data | Facts only — no investment advice")

# ============================================================================
# 3. Persistent disclaimer banner
# ============================================================================
st.warning(
    "Facts-only. No investment advice. "
    "Source data from HDFC AMC, AMFI and SEBI official pages only. "
    "No personal data stored."
)

# ============================================================================
# 4. Example question buttons
# ============================================================================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Expense ratio of HDFC Mid Cap?", use_container_width=True):
        st.session_state.prefill = "Expense ratio of HDFC Mid Cap?"

with col2:
    if st.button("ELSS lock-in period?", use_container_width=True):
        st.session_state.prefill = "ELSS lock-in period?"

with col3:
    if st.button("How to download capital gains statement?", use_container_width=True):
        st.session_state.prefill = "How to download capital gains statement?"

# ============================================================================
# 5. Session isolation
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ============================================================================
# 6. Chat history display
# ============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("caption"):
            st.caption(msg["caption"])

# ============================================================================
# 7. Chat input
# ============================================================================

# Check for prefilled query from example buttons
prefill_query = st.session_state.pop("prefill", None)
user_input = st.chat_input("Ask about HDFC Mutual Fund schemes...")

# Use prefill if no direct input
query = prefill_query or user_input

if query:
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # --- Guardrails (run BEFORE retriever / LLM) ---
    if contains_pii(query):
        response_text = PII_MESSAGE
        caption_text = None

    elif is_advisory(query):
        response_text = REFUSAL_MESSAGE
        caption_text = None

    else:
        # --- RAG pipeline ---
        with st.chat_message("assistant"):
            with st.spinner("Searching verified sources..."):
                try:
                    chunks = retrieve(query, k=3)
                    response_text = generate_response(query, chunks)

                    # Build caption from top chunk metadata
                    if chunks:
                        top = chunks[0].metadata
                        source_url = top.get("source_url", "")
                        scrape_date = top.get("scrape_date", "")
                        caption_text = (
                            f"Source: {source_url} | "
                            f"Last updated: {scrape_date}"
                        )
                    else:
                        caption_text = None

                except ValueError as exc:
                    # Guardrail errors from retriever
                    response_text = str(exc)
                    caption_text = None
                except Exception as exc:
                    response_text = (
                        "An error occurred while processing your request. "
                        "Please try again."
                    )
                    caption_text = None
                    st.error(f"Error details: {exc}")

            st.markdown(response_text)
            if caption_text:
                st.caption(caption_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "caption": caption_text,
        })

        # Skip the duplicate display block below
        query = None

    # Display guardrail responses (PII / advisory)
    if query is not None:
        with st.chat_message("assistant"):
            st.markdown(response_text)
            if caption_text:
                st.caption(caption_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "caption": caption_text,
        })
