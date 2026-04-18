"""
Embedder for the HDFC Mutual Fund RAG Chatbot.

Uses pluggable embeddings and stores vectors in a persistent
ChromaDB collection.

Default runtime provider is local HuggingFace embeddings (no API key).
Optional provider: Gemini embeddings via ``EMBEDDING_PROVIDER=gemini``.
"""

from __future__ import annotations

import os
import pickle
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../Rag_Chatbot
CHUNKS_PKL = PROJECT_ROOT / "data" / "chunks" / "chunks_latest.pkl"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
EMBEDDING_PROVIDER_FILE = CHROMA_DIR / "embedding_provider.txt"

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv(PROJECT_ROOT / ".env")

COLLECTION_NAME = "hdfc_mf_faq_corpus"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()

LOCAL_MODEL_NAME = "BAAI/bge-small-en-v1.5"
LOCAL_MODEL_KWARGS = {"device": "cpu"}
LOCAL_ENCODE_KWARGS = {"normalize_embeddings": True}


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


def _get_embeddings():
    """Initialise embedding model based on EMBEDDING_PROVIDER."""
    if EMBEDDING_PROVIDER == "local":
        print("Loading local HuggingFace embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name=LOCAL_MODEL_NAME,
            model_kwargs=LOCAL_MODEL_KWARGS,
            encode_kwargs=LOCAL_ENCODE_KWARGS,
        )
        print(f"Local embeddings loaded: {LOCAL_MODEL_NAME}")
        return embeddings

    if EMBEDDING_PROVIDER == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required when EMBEDDING_PROVIDER=gemini"
            )
        print("Loading Google Generative AI Embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key,
        )
        print("Google Generative AI Embeddings loaded: models/gemini-embedding-001")
        return embeddings

    raise ValueError(
        "Unsupported EMBEDDING_PROVIDER. Use 'local' or 'gemini'."
    )


def _write_provider_marker(provider: str) -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDING_PROVIDER_FILE.write_text(provider, encoding="utf-8")


def _read_provider_marker() -> str | None:
    if not EMBEDDING_PROVIDER_FILE.exists():
        return None
    return EMBEDDING_PROVIDER_FILE.read_text(encoding="utf-8").strip().lower()


def embed_and_store() -> Chroma:
    """Embed all chunks and store them in ChromaDB.

    1. Loads ``data/chunks/chunks_latest.pkl``
    2. Initialises embeddings (local by default)
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

    total = len(chunks)
    print(f"Embedding {total} chunks into ChromaDB (provider={EMBEDDING_PROVIDER})...")
    start = time.time()

    if EMBEDDING_PROVIDER == "gemini":
        batch_size = 40
        first_batch = chunks[:batch_size]
        vectorstore = Chroma.from_documents(
            documents=first_batch,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=str(CHROMA_DIR),
        )
        print(f"  Batch 1/{-(-total // batch_size)}: {len(first_batch)} chunks embedded")

        for i in range(batch_size, total, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = -(-total // batch_size)
            print("  Waiting 60s for rate limit cooldown...")
            time.sleep(60)
            vectorstore.add_documents(batch)
            print(f"  Batch {batch_num}/{total_batches}: {len(batch)} chunks embedded")
    else:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=str(CHROMA_DIR),
        )

    _write_provider_marker(EMBEDDING_PROVIDER)

    elapsed = time.time() - start
    count = vectorstore._collection.count()
    print(f"Successfully upserted {count} chunks into ChromaDB")
    print(f"Time taken: {elapsed:.1f}s")
    print(f"Persist directory: {CHROMA_DIR}")

    return vectorstore


def get_vectorstore() -> Chroma:
    """Load the persisted ChromaDB vectorstore.

    Initialises the same embedding provider and connects
    to the existing ``chroma_db/`` directory.

    Returns:
        The ``Chroma`` vectorstore instance ready for queries.
    """
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"ChromaDB directory not found: {CHROMA_DIR}\n"
            "Run embed_and_store() first."
        )

    stored_provider = _read_provider_marker()
    if stored_provider is None and EMBEDDING_PROVIDER == "local":
        raise RuntimeError(
            "Existing ChromaDB has no embedding provider marker. "
            "To use local runtime retrieval, rebuild index once: "
            "python -c \"from src.ingestion.embedder import embed_and_store; embed_and_store()\""
        )

    if stored_provider and stored_provider != EMBEDDING_PROVIDER:
        raise RuntimeError(
            f"Embedding provider mismatch. Index was built with '{stored_provider}', "
            f"but runtime is '{EMBEDDING_PROVIDER}'. Rebuild index with current provider."
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
