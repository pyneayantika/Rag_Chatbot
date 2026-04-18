import sys
import os

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
)

import logging
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.guardrails.intent_classifier import *
from src.retrieval.retriever import retrieve
from src.generation.llm_client import generate_response


load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="HDFC MF FAQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    source_url: str = ""
    last_updated: str = ""
    is_refusal: bool = False
    is_pii: bool = False
    session_id: str
    query_type: str = "factual"


@app.get("/health")
def health():
    return {"status": "ok", "message": "HDFC MF FAQ API running"}


@app.get("/")
def root():
    return {
        "name": "HDFC MF FAQ API",
        "version": "1.0.0",
        "disclaimer": "Facts-only. No investment advice.",
    }


@app.get("/debug/paths")
def debug_paths():
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[2]
    chroma_dir = project_root / "chroma_db"
    return {
        "project_root": str(project_root),
        "chroma_dir": str(chroma_dir),
        "chroma_exists": chroma_dir.exists(),
        "chroma_contents": [str(f.name) for f in chroma_dir.iterdir()] if chroma_dir.exists() else [],
        "root_contents": [str(f.name) for f in project_root.iterdir() if not str(f.name).startswith('.')],
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        session_id = req.session_id or str(uuid.uuid4())

        query = (req.query or "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if contains_pii(query):
            return ChatResponse(
                answer=PII_MESSAGE,
                is_pii=True,
                is_refusal=True,
                session_id=session_id,
                query_type="factual",
            )

        if is_advisory(query):
            return ChatResponse(
                answer=REFUSAL_MESSAGE,
                is_refusal=True,
                is_pii=False,
                session_id=session_id,
                query_type="advisory",
            )

        chunks = retrieve(query, k=3)
        if not chunks:
            return ChatResponse(
                answer=(
                    "I could not find verified information.\n"
                    "Please check https://www.hdfcfund.com"
                ),
                source_url="https://www.hdfcfund.com",
                session_id=session_id,
                query_type="factual",
            )

        answer = generate_response(query, chunks)

        meta = getattr(chunks[0], "metadata", {}) or {}
        source_url = meta.get("source_url", "")
        last_updated = meta.get("scrape_date", meta.get("last_updated", ""))

        return ChatResponse(
            answer=answer,
            source_url=source_url or "",
            last_updated=last_updated or "",
            is_refusal=False,
            is_pii=False,
            session_id=session_id,
            query_type="factual",
        )

    except HTTPException:
        raise

    except Exception:
        logger.error("Unhandled error in /api/chat", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        )
