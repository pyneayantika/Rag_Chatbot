"""
Embedder for the HDFC Mutual Fund RAG Chatbot.

Uses Google Generative AI Embeddings (embedding-001) and
stores vectors in a persistent ChromaDB collection.
"""

from __future__ import annotations

import os
import pickle
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../Rag_Chatbot
CHUNKS_PKL = PROJECT_ROOT / "data" / "chunks" / "chunks_latest.pkl"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv(PROJECT_ROOT / ".env")

COLLECTION_NAME = "hdfc_mf_faq_corpus"


# ============================================================================
# Core functions
# ============================================================================

def _load_chunks() -> list[Document]:
    """Load chunked Documents from the pickle file."""
    if not CHUNKS_PKL.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PKL}\n"
            "Run the chunker first: python src/ingestion/chunker.py"
        )
    with open(CHUNKS_PKL, "rb") as f:
        chunks = pickle.load(f)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PKL.name}")
    return chunks


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Initialise the Google Generative AI embedding model."""
    print("Loading Google Generative AI Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )
    print("Google Generative AI Embeddings loaded: models/embedding-001")
    return embeddings


def embed_and_store() -> Chroma:
    """Embed all chunks and store them in ChromaDB.

    1. Loads ``data/chunks/chunks_latest.pkl``
    2. Initialises Google Generative AI embeddings
    3. Deletes existing ``chroma_db/`` directory if present
    4. Creates a ChromaDB collection via ``Chroma.from_documents()``
    5. Prints total chunks upserted

    Returns:
        The populated ``Chroma`` vectorstore instance.
    """
    chunks = _load_chunks()
    embeddings = _get_embeddings()

    # Clear old vectorstore
    if CHROMA_DIR.exists():
        print(f"Deleting existing {CHROMA_DIR}/ ...")
        shutil.rmtree(CHROMA_DIR)

    BATCH_SIZE = 40  # stay well under Gemini free-tier 100 RPM limit
    total = len(chunks)
    print(f"Embedding {total} chunks into ChromaDB (batches of {BATCH_SIZE})...")
    start = time.time()

    # First batch creates the vectorstore
    first_batch = chunks[:BATCH_SIZE]
    vectorstore = Chroma.from_documents(
        documents=first_batch,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )
    print(f"  Batch 1/{-(-total // BATCH_SIZE)}: {len(first_batch)} chunks embedded")

    # Remaining batches added with rate-limit delay
    for i in range(BATCH_SIZE, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = -(-total // BATCH_SIZE)
        print(f"  Waiting 60s for rate limit cooldown...")
        time.sleep(60)
        vectorstore.add_documents(batch)
        print(f"  Batch {batch_num}/{total_batches}: {len(batch)} chunks embedded")

    elapsed = time.time() - start
    count = vectorstore._collection.count()
    print(f"Successfully upserted {count} chunks into ChromaDB")
    print(f"Time taken: {elapsed:.1f}s")
    print(f"Persist directory: {CHROMA_DIR}")

    return vectorstore


def get_vectorstore() -> Chroma:
    """Load the persisted ChromaDB vectorstore.

    Initialises the same Google embedding model and connects
    to the existing ``chroma_db/`` directory.

    Returns:
        The ``Chroma`` vectorstore instance ready for queries.
    """
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"ChromaDB directory not found: {CHROMA_DIR}\n"
            "Run embed_and_store() first."
        )

    embeddings = _get_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    count = vectorstore._collection.count()
    print(f"Loaded vectorstore with {count} documents")
    return vectorstore


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the embedding pipeline from the command line."""
    embed_and_store()
    print("\n[OK] Embedding complete.")


if __name__ == "__main__":
    main()
