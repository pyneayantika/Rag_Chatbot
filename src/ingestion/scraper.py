"""
Web scraper for the HDFC Mutual Fund RAG Chatbot.

Routes each URL from the allowlist to the correct extraction strategy:
    - Tier 1 (Groww)          → Playwright (async, headless Chromium)
    - Tier 2/3/4 (static HTML)→ Requests + BeautifulSoup
    - PDF links               → PyMuPDF (fitz)

Saves raw text output to ``data/raw/`` with a metadata header.
Includes exponential-backoff retry logic (max 3 attempts).
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import logging
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

from src.config.url_allowlist import (
    TIER_1_GROWW,
    TIER_2_HDFC_AMC,
    TIER_3_AMFI,
    TIER_4_SEBI,
    URLS,
    validate_url,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # …/Rag_Chatbot
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
IST = timezone(timedelta(hours=5, minutes=30))

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2  # doubles on each retry → 2, 4, 8
MIN_WORD_COUNT = 50

REQUEST_TIMEOUT = 30  # seconds
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ============================================================================
# Helpers
# ============================================================================

def _domain(url: str) -> str:
    """Return the bare domain (without ``www.`` prefix)."""
    hostname = urlparse(url).hostname or ""
    return hostname.lower().removeprefix("www.")


def _tier_label(url: str) -> str:
    """Return a human-readable tier label for a URL."""
    if url in TIER_1_GROWW:
        return "tier_1_groww"
    if url in TIER_2_HDFC_AMC:
        return "tier_2_hdfc_amc"
    if url in TIER_3_AMFI:
        return "tier_3_amfi"
    if url in TIER_4_SEBI:
        return "tier_4_sebi"
    return "unknown"


def _scheme_name_from_url(url: str) -> str:
    """Derive a short scheme / page name from the URL path.

    Uses the last **two** meaningful path segments joined with an
    underscore to avoid filename collisions (e.g. multiple HDFC AMC
    scheme pages that all end in ``/direct``).

    When a URL contains a ``zoneName`` query parameter (e.g. AMFI
    knowledge-center pages), the parameter value is used instead,
    producing a unique filename per page.

    Examples
    --------
    >>> _scheme_name_from_url("https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth")
    'mutual-funds_hdfc-mid-cap-opportunities-fund-direct-growth'
    >>> _scheme_name_from_url("https://www.hdfcfund.com/explore/mutual-funds/hdfc-mid-cap-fund/direct")
    'hdfc-mid-cap-fund_direct'
    >>> _scheme_name_from_url("https://www.amfiindia.com/investor/knowledge-center-info?zoneName=CategorizationOfMutualFundSchemes")
    'categorizationofmutualfundschemes'
    >>> _scheme_name_from_url("https://www.hdfcfund.com/faq")
    'faq'
    """
    parsed = urlparse(url)

    # If the URL has a zoneName query param, use it as the scheme name
    from urllib.parse import parse_qs
    query_params = parse_qs(parsed.query)
    if "zoneName" in query_params:
        return query_params["zoneName"][0].lower()

    path = parsed.path.strip("/")
    segments = [s for s in path.split("/") if s]
    if len(segments) >= 2:
        return f"{segments[-2]}_{segments[-1]}"
    return segments[-1] if segments else _domain(url)


def _safe_filename(scheme_name: str, domain: str, date_str: str) -> str:
    """Build a filesystem-safe filename: ``{scheme}_{domain}_{date}.txt``."""
    safe = re.sub(r"[^\w\-]", "_", f"{scheme_name}_{domain}_{date_str}")
    return f"{safe}.txt"


def _clean_text(raw: str) -> str:
    """Collapse excessive whitespace while preserving paragraph breaks."""
    # Replace multiple blank lines with a single one
    text = re.sub(r"\n{3,}", "\n\n", raw)
    # Collapse runs of spaces / tabs (but not newlines)
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()


def _word_count(text: str) -> int:
    return len(text.split())


def _retry(func):
    """Decorator: retry *func* with exponential backoff (sync or async)."""

    if asyncio.iscoroutinefunction(func):
        async def _async_wrapper(*args, **kwargs):
            backoff = INITIAL_BACKOFF_SECONDS
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if attempt == MAX_RETRIES:
                        logger.error(
                            "Failed after %d attempts: %s — %s",
                            MAX_RETRIES, args, exc,
                        )
                        raise
                    logger.warning(
                        "Attempt %d/%d failed (%s). Retrying in %ds …",
                        attempt, MAX_RETRIES, exc, backoff,
                    )
                    await asyncio.sleep(backoff)
                    backoff *= 2
        return _async_wrapper

    def _sync_wrapper(*args, **kwargs):
        backoff = INITIAL_BACKOFF_SECONDS
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if attempt == MAX_RETRIES:
                    logger.error(
                        "Failed after %d attempts: %s — %s",
                        MAX_RETRIES, args, exc,
                    )
                    raise
                logger.warning(
                    "Attempt %d/%d failed (%s). Retrying in %ds …",
                    attempt, MAX_RETRIES, exc, backoff,
                )
                time.sleep(backoff)
                backoff *= 2
    return _sync_wrapper


# ============================================================================
# Scraping functions
# ============================================================================

@_retry
async def scrape_with_playwright(url: str) -> str:
    """Scrape a JavaScript-rendered page using async Playwright.

    Launches a headless Chromium browser, navigates to *url* with
    ``wait_until='networkidle'``, waits an extra 3 seconds for any
    remaining JS hydration, then returns the cleaned ``<body>`` text.

    Args:
        url: A Tier 1 (Groww) URL.

    Returns:
        Cleaned body text as a string.
    """
    from playwright.async_api import async_playwright  # heavy import; deferred

    logger.info("Playwright → %s", url)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=REQUEST_HEADERS["User-Agent"],
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle", timeout=60_000)
        # Extra wait for client-side hydration / lazy-loaded sections
        await page.wait_for_timeout(3_000)

        body_text = await page.evaluate("() => document.body.innerText")

        await context.close()
        await browser.close()

    return _clean_text(body_text)


@_retry
def scrape_with_requests(url: str) -> str:
    """Scrape a static HTML page with ``requests`` + ``BeautifulSoup``.

    Suitable for Tier 2 (HDFC AMC), Tier 3 (AMFI), and Tier 4 (SEBI)
    pages that do not require JavaScript execution.

    Args:
        url: Any static HTML URL from the allowlist.

    Returns:
        Cleaned body text extracted via ``BeautifulSoup.get_text()``.
    """
    logger.info("Requests  → %s", url)

    response = requests.get(
        url,
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    raw_text = soup.get_text(separator="\n")
    return _clean_text(raw_text)


@_retry
def scrape_pdf(url: str) -> str:
    """Download a PDF from *url* and extract text page-by-page with PyMuPDF.

    Args:
        url: Direct link to a PDF document.

    Returns:
        Cleaned concatenated text from all PDF pages.
    """
    logger.info("PDF       → %s", url)

    response = requests.get(
        url,
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    pdf_bytes = io.BytesIO(response.content)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages_text: list[str] = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pages_text.append(page.get_text())

    doc.close()
    return _clean_text("\n\n".join(pages_text))


# ============================================================================
# Routing
# ============================================================================

def _is_pdf_url(url: str) -> bool:
    """Heuristic: treat the URL as a PDF if the path ends with ``.pdf``."""
    return urlparse(url).path.lower().endswith(".pdf")


async def _scrape_single(url: str) -> str:
    """Route *url* to the appropriate scraper and return the extracted text."""
    validate_url(url)  # guard — raises ValueError for disallowed domains

    if _is_pdf_url(url):
        return scrape_pdf(url)

    # Tier 1 (Groww) — JS-rendered SPAs
    if url in TIER_1_GROWW:
        return await scrape_with_playwright(url)

    # SEBI pages also require JS to render content
    if "sebi.gov.in" in url:
        return await scrape_with_playwright(url)

    # Tier 2 / 3 — static HTML
    return scrape_with_requests(url)


# ============================================================================
# Save
# ============================================================================

def _save_raw(
    text: str,
    url: str,
    scheme_name: str,
    tier: str,
    scrape_date: str,
) -> Path:
    """Persist scraped text with a metadata header to ``data/raw/``."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    domain = _domain(url)
    filename = _safe_filename(scheme_name, domain, scrape_date)
    filepath = RAW_DATA_DIR / filename

    content_hash = hashlib.sha256(text.encode()).hexdigest()

    header = (
        f"---\n"
        f"source_url: {url}\n"
        f"scrape_date: {scrape_date}\n"
        f"tier: {tier}\n"
        f"scheme_name: {scheme_name}\n"
        f"domain: {domain}\n"
        f"content_hash: sha256:{content_hash}\n"
        f"word_count: {_word_count(text)}\n"
        f"---\n\n"
    )

    filepath.write_text(header + text, encoding="utf-8")
    logger.info("Saved → %s (%d words)", filepath.name, _word_count(text))
    return filepath


# ============================================================================
# Main orchestrator
# ============================================================================

async def scrape_all() -> list[Path]:
    """Scrape every URL in the allowlist and save results to ``data/raw/``.

    Reads ``URLS`` from :pymod:`src.config.url_allowlist`, routes each URL
    to the correct scraping function, validates the minimum word count,
    and writes the output with a metadata header.

    Returns:
        List of file paths that were successfully written.
    """
    today = datetime.now(IST).strftime("%Y%m%d")
    saved_files: list[Path] = []
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in RAW_DATA_DIR.glob("*.txt"):
        old_file.unlink()
        logger.info("Deleted old file: %s", old_file.name)

    logger.info("=" * 60)
    logger.info("Starting scrape_all — %d URLs — %s", len(URLS), today)
    logger.info("=" * 60)

    for idx, url in enumerate(URLS, start=1):
        tier = _tier_label(url)
        scheme_name = _scheme_name_from_url(url)

        logger.info("[%02d/%02d] %s  (%s)", idx, len(URLS), scheme_name, tier)

        try:
            text = await _scrape_single(url)
        except Exception as exc:
            logger.error("Skipping %s — all retries failed: %s", url, exc)
            continue

        # ----- minimum word-count gate -----
        wc = _word_count(text)
        if wc < MIN_WORD_COUNT:
            logger.warning(
                "Skipping %s — only %d words extracted (minimum: %d)",
                url, wc, MIN_WORD_COUNT,
            )
            continue

        filepath = _save_raw(
            text=text,
            url=url,
            scheme_name=scheme_name,
            tier=tier,
            scrape_date=today,
        )
        saved_files.append(filepath)

    logger.info("=" * 60)
    logger.info(
        "scrape_all complete — %d/%d URLs saved successfully.",
        len(saved_files), len(URLS),
    )
    logger.info("=" * 60)
    return saved_files


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full scraper pipeline from the command line."""
    saved = asyncio.run(scrape_all())
    print(f"\n[OK] Saved {len(saved)} files to {RAW_DATA_DIR}")
    for f in saved:
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
