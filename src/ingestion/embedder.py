"""
Embedder for the HDFC Mutual Fund RAG Chatbot.

Uses BAAI/bge-small-en-v1.5 (free, local) embeddings via
HuggingFaceEmbeddings and stores vectors in a persistent
ChromaDB collection.

No API keys required — all inference runs locally on CPU.
"""

from __future__ import annotations

import pickle
import shutil
import time
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../Rag_Chatbot
CHUNKS_PKL = PROJECT_ROOT / "data" / "chunks" / "chunks_latest.pkl"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

# ---------------------------------------------------------------------------
# Embedding model config
# ---------------------------------------------------------------------------
MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_KWARGS = {"device": "cpu"}
ENCODE_KWARGS = {"normalize_embeddings": True}

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


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Initialise the BGE embedding model."""
    print("Loading BGE model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS,
    )
    print(f"BGE model loaded: {MODEL_NAME}")
    return embeddings


def embed_and_store() -> Chroma:
    """Embed all chunks and store them in ChromaDB.

    1. Loads ``data/chunks/chunks_latest.pkl``
    2. Initialises BAAI/bge-small-en-v1.5 embeddings
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

    print(f"Embedding {len(chunks)} chunks into ChromaDB...")
    start = time.time()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    elapsed = time.time() - start
    count = vectorstore._collection.count()
    print(f"Successfully upserted {count} chunks into ChromaDB")
    print(f"Time taken: {elapsed:.1f}s")
    print(f"Persist directory: {CHROMA_DIR}")

    return vectorstore


def get_vectorstore() -> Chroma:
    """Load the persisted ChromaDB vectorstore.

    Initialises the same BGE embedding model and connects
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
