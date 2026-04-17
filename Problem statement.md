GROWW × HDFC Mutual Fund | RAG Chatbot — Product Problem Statement

Confidential · April 2026

PRODUCT PROBLEM STATEMENT

Mutual Fund FAQ Assistant — RAG Chatbot
Built for Groww × HDFC Mutual Fund

Milestone: Milestone 1 — FAQ RAG
Product: Groww
AMC: HDFC Mutual Fund
Version: v1.0 · April 2026

1. Objective of the Chatbot

Build a facts-only, RAG-powered FAQ assistant that answers objective, verifiable questions about HDFC Mutual Fund schemes available on Groww using only official public sources (AMC, AMFI, SEBI).

Requirements:

Every response must include one source citation
No investment advice
No opinions
No hallucinations

The assistant is NOT:

A financial advisor
A returns calculator
A comparison engine

Its sole purpose is to:

Retrieve verified facts from a curated corpus of 20 official URLs
Present answers with a source link and freshness date
2. Target Users

Retail Investor

Need: Quick factual checks before investing
Example: What is the expense ratio of HDFC Mid Cap Fund?

First-Time Investor

Need: Understand ELSS lock-in, SIP minimums, riskometer
Example: What is the lock-in period for ELSS funds?

Customer Support Team

Need: Resolve repetitive factual queries
Example: How do I download my capital gains statement?

Content / Compliance Team

Need: Verify scheme facts
Example: What is the benchmark index for HDFC Flexi Cap Fund?
3. Scope of Work
3.1 AMC & Product Selection

Platform: Groww
Reason: User familiarity and structured scheme data

AMC: HDFC Mutual Fund
Reason: Clean static pages, easy scraping

Scheme Count: 5
Reason: One per SEBI category for diversity

Plan Type: Direct Growth
Reason: Consistent NAV and no commission noise

3.2 Selected HDFC Schemes
HDFC Mid Cap Opportunities Fund – Direct Growth
Category: Mid-cap
Benchmark: Nifty Midcap 150 TRI
HDFC Flexi Cap Fund – Direct Growth
Category: Flexi-cap
Benchmark: BSE 500 TRI
HDFC ELSS Tax Saver Fund – Direct Growth
Category: ELSS
Benchmark: Nifty 500 TRI
HDFC Large Cap Fund – Direct Growth
Category: Large-cap
Benchmark: Nifty 100 TRI
HDFC Small Cap Fund – Direct Growth
Category: Small-cap
Benchmark: Nifty Smallcap 250 TRI

Each scheme represents a unique query type to ensure retrieval diversity.

4. Corpus Definition — 20 URLs

Only official public sources allowed.

Tier 1 — Groww (5 URLs)
Scheme pages containing expense ratio, SIP, exit load, etc.
Tier 2 — HDFC AMC (8 URLs)
Factsheets, SID, KIM, TER, FAQs, statements, tax docs, riskometer
Tier 3 — AMFI (4 URLs)
Riskometer, ELSS rules, SIP guide, MF categories
Tier 4 — SEBI (3 URLs)
Categorisation rules, TRI benchmark rules, investor charter

Total: 20 URLs

5. FAQ Assistant Requirements
5.1 Must-Answer Query Types
Expense ratio
Exit load
Minimum SIP
ELSS lock-in
Riskometer
Benchmark index
Statement download
5.2 Must-Refuse Queries

Examples:

Should I invest in HDFC ELSS or Large Cap Fund?
Which fund gave best returns?
Is now a good time to invest?
What will my SIP grow to?
Is HDFC better than Nippon?

Refusal format:
"I can only share verified facts about mutual fund schemes. For guidance, please visit [AMFI/SEBI link]."

5.3 Response Format

Every answer must follow:

Answer (≤ 3 sentences, factual only)
Source: exact URL
Last updated from sources: DD MMM YYYY

6. Must-Have Criteria
Functional
Correct answers for all query types
≤ 3 sentence limit
Exactly 1 source citation
Date from metadata
Advisory queries refused
Multi-session support
UI includes welcome + sample questions + disclaimer
Non-Functional
Daily scheduler (9:15 AM IST)
Auto-refresh corpus
No PII collection
Strict source allowlist
Metadata preserved
7. Constraints

Data Sources

Only AMC, AMFI, SEBI

PII

No PAN, Aadhaar, email, phone

Performance Data

No return calculations

Investment Advice

No recommendations

Response Length

Max 3 sentences

Scope

Only 5 HDFC schemes
8. Architecture

Pipeline:

Scheduler
GitHub Actions (9:15 AM IST)
Scraper
Python
Playwright (Groww)
Requests (others)
Chunker
LangChain
400 tokens, 50 overlap
Embedder
OpenAI embeddings
ChromaDB
Retriever + LLM
Top-K = 3
GPT-4o / Claude
UI
Streamlit
Session isolation
Flow

Scheduler → Scraper → Chunker → Embedder → Retriever → LLM → Response → UI

System Prompt

"You are a facts-only mutual fund FAQ assistant. Answer only from provided context. Never give advice or projections."

Response format:

≤ 3 sentences
Source URL
Last updated date
9. Known Limitations
Groww pages require Playwright
SID/KIM are PDFs
Factsheets may be 30 days old
No live NAV or AUM
Only 5 schemes supported
English only
10. Deliverables
Working prototype / demo
Source list (20 URLs)
README
Sample Q&A (10 queries)
Disclaimer snippet
11. Definition of Done
Correct factual answers with source
Advisory queries refused properly
Date shown from metadata
No PII fields
Scheduler runs automatically
UI Disclaimer

Facts-only. No investment advice. Source data from HDFC Mutual Fund, AMFI, and SEBI official pages only. Last updated from sources shown on each response. This assistant does not store any personal information.