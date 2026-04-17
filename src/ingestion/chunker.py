"""
Document chunker for the HDFC Mutual Fund RAG Chatbot.

Reads scraped ``.txt`` files from ``data/raw/``, parses their YAML-style
metadata headers, splits the body text with LangChain's
``RecursiveCharacterTextSplitter``, and persists the resulting
``Document`` list as a pickle file in ``data/chunks/``.
"""

from __future__ import annotations

import logging
import pickle
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../Rag_Chatbot
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
CHUNKS_OUTPUT = CHUNKS_DIR / "chunks_latest.pkl"

# ---------------------------------------------------------------------------
# Splitter config
# ---------------------------------------------------------------------------
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
MIN_TOTAL_CHUNKS = 100
MAX_TOTAL_CHUNKS = 1500


# ============================================================================
# Header parsing
# ============================================================================

def _parse_header(text: str) -> tuple[dict[str, str], str]:
    """Parse the ``---`` delimited metadata header from a raw scraped file.

    Args:
        text: Full file content including the header block.

    Returns:
        A tuple of ``(metadata_dict, body_text)`` where *body_text* is
        everything after the closing ``---`` fence.
    """
    # Match the front-matter block: ---\n...\n---
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text  # no header found — return full text as body

    header_block = match.group(1)
    body = text[match.end():]

    metadata: dict[str, str] = {}
    for line in header_block.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()

    return metadata, body


# ============================================================================
# Core chunking
# ============================================================================

def chunk_documents() -> list[Document]:
    """Read raw files, split into chunks, and save as a pickle.

    Workflow
    -------
    1. Glob all ``.txt`` files in ``data/raw/``.
    2. For each file, parse the metadata header and strip it.
    3. Split the body using ``RecursiveCharacterTextSplitter``
       (chunk_size=400, chunk_overlap=50, length_function=len).
    4. Attach metadata to every resulting ``Document``:
       ``source_url``, ``scheme_name``, ``scrape_date``,
       ``source_tier``, ``chunk_index``, ``total_chunks``,
       ``word_count``.
    5. Persist the full list to ``data/chunks/chunks_latest.pkl``.
    6. Assert total chunks is between 100 and 500.

    Returns:
        List of chunked ``Document`` objects.

    Raises:
        ValueError: If total chunk count is outside [100, 500].
        FileNotFoundError: If ``data/raw/`` contains no ``.txt`` files.
    """
    txt_files = sorted(RAW_DATA_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(
            f"No .txt files found in {RAW_DATA_DIR}. Run the scraper first."
        )

    logger.info("Found %d raw files in %s", len(txt_files), RAW_DATA_DIR)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    all_chunks: list[Document] = []

    for filepath in txt_files:
        raw = filepath.read_text(encoding="utf-8")
        metadata, body = _parse_header(raw)

        # Extract the four required header fields
        source_url = metadata.get("source_url", "")
        scheme_name = metadata.get("scheme_name", filepath.stem)
        scrape_date = metadata.get("scrape_date", "")
        source_tier = metadata.get("tier", "")

        # Split body into chunks
        chunks = splitter.split_text(body)

        total_chunks = len(chunks)
        logger.info(
            "  %-60s -> %3d chunks",
            filepath.name,
            total_chunks,
        )

        for idx, chunk_text in enumerate(chunks):
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "source_url": source_url,
                    "scheme_name": scheme_name,
                    "scrape_date": scrape_date,
                    "source_tier": source_tier,
                    "chunk_index": idx,
                    "total_chunks": total_chunks,
                    "word_count": len(chunk_text.split()),
                },
            )
            all_chunks.append(doc)

    # ------------------------------------------------------------------
    # Validate total chunk count
    # ------------------------------------------------------------------
    total = len(all_chunks)
    logger.info("Total chunks across all files: %d", total)

    if not (MIN_TOTAL_CHUNKS <= total <= MAX_TOTAL_CHUNKS):
        raise ValueError(
            f"Total chunk count {total} is outside the expected range "
            f"[{MIN_TOTAL_CHUNKS}, {MAX_TOTAL_CHUNKS}]. "
            f"Check raw data quality or adjust chunking parameters."
        )

    # ------------------------------------------------------------------
    # Save to pickle
    # ------------------------------------------------------------------
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHUNKS_OUTPUT, "wb") as f:
        pickle.dump(all_chunks, f)

    logger.info("Saved %d chunks to %s", total, CHUNKS_OUTPUT)
    return all_chunks


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the chunker from the command line."""
    chunks = chunk_documents()
    print(f"\n[OK] {len(chunks)} chunks saved to {CHUNKS_OUTPUT}")

    # Quick stats
    files = {c.metadata["source_url"] for c in chunks}
    print(f"     Sources:  {len(files)} unique URLs")
    wc = sum(c.metadata["word_count"] for c in chunks)
    print(f"     Words:    {wc:,} total across all chunks")


if __name__ == "__main__":
    main()
