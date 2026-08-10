# Deployment Postmortem: HDFC MF FAQ Assistant

## Summary

This document captures the full deployment journey for the HDFC Mutual Fund FAQ Assistant, including production guardrails, operational failures encountered, root-cause analysis, and final stabilization actions.

Final production topology:
- Frontend: Vercel (Next.js)
- Backend API: Fly.io (FastAPI)
- LLM generation: Groq (`llama-3.1-8b-instant`)
- Retrieval embeddings: Local HuggingFace by default (`BAAI/bge-small-en-v1.5`), with optional Gemini mode

---

## Guardrails Implemented

### 1) Query Safety Guardrails
- PII detection and blocking (PAN/Aadhaar/account-related patterns).
- Advisory intent refusal for recommendation-style prompts ("Should I invest", "best fund", etc.).
- Facts-only policy response for objective scheme information only.

### 2) Response Integrity Guardrails
- Strict system prompt constraints:
  - Answer from retrieved context only.
  - No speculation/opinion/recommendation.
  - Keep answers concise.
- Mandatory provenance formatting with source and last-updated details.
- Explicit fallback response when verified context is insufficient.

### 3) Resilience Guardrails
- Rate-limit retry and backoff logic on provider throttling.
- Fallback response path for high-traffic/rate-limit events.
- Timeout handling and user-facing timeout messages.

### 4) Retrieval Consistency Guardrails
- Embedding provider marker persisted in `chroma_db/embedding_provider.txt`.
- Runtime safety checks to fail fast on provider mismatch between index build and runtime provider.
- Configurable embedding provider via `EMBEDDING_PROVIDER` (`local` or `gemini`).

### 5) Operational Guardrails
- `/health` endpoint for liveness checks.
- `/debug/paths` endpoint for runtime diagnostics (vectorstore loading, env visibility, data paths).
- Frontend health-check timeout tuning to reduce false "Cannot connect" states.

---

## Key Challenges Faced

### A) Render Memory Limits and Runtime Instability
- Repeated instance failures on Render free tier due to memory overrun (`>512MB`).
- Symptoms:
  - Intermittent `/health` availability
  - `/api/chat` timeouts/connection closures
  - service recoveries followed by repeated failures

Root cause:
- RAG factual path (retrieval + embedding model load + generation) exceeded free-tier memory envelope.

### B) Cold Starts and False-Negative Availability
- Frontend showed backend-unavailable banners during startup delays.
- Cause:
  - health-check timeout too short for cold/waking instances.

Mitigation:
- Increased frontend health-check timeout.

### C) Fly Migration Friction
- CLI install and account verification blockers (high-risk account check).
- Build failures caused by buildpacks attempting full `requirements.txt` install.
- `pymupdf` build failure during image build in cloud environment.

Root cause:
- Buildpacks included ingestion-only heavy/native dependencies unnecessary for API serving.

### D) Build Strategy Misconfiguration
- Deploys initially used Python buildpacks instead of Dockerfile path.
- Resulted in repeated build/install failures despite Dockerfile being present.

Mitigation:
- Added root `fly.toml` with explicit Dockerfile build config.
- Corrected config location and repository path usage.

### E) Deployment URL Drift in Vercel
- Multiple immutable deployment URLs showed inconsistent behavior.
- Some deployments retained older environment/runtime behavior.

Mitigation:
- Updated environment variable globally.
- Redeployed and promoted intended deployment.
- Aligned frontend fallback URL to Fly backend to reduce env drift risk.

---

## Changes Applied

### Backend Hosting and Runtime
- Migrated backend from Render to Fly.io for more stable runtime behavior.
- Configured Fly app to keep a machine warm:
  - `auto_start_machines = true`
  - `auto_stop_machines = false`
  - `min_machines_running = 1`

### Build and Dependencies
- Added Dockerfile-based deployment flow.
- Added `requirements-api.txt` to isolate serving-time dependencies.
- Updated Dockerfile to install `requirements-api.txt` instead of full ingestion stack.

### Frontend Stability
- Updated API fallback URL to Fly backend.
- Increased frontend chat timeout from 60s to 120s.
- Increased health-check timeout to reduce false outages during startup delays.

### UI Update
- Updated header logo to Groww-style mark beside `HDFC MF AI Assistant`.

---

## Validation Results

### Passed
- `/health` returns OK on Fly.
- Advisory query path returns refusal payload correctly.
- Factual query path returns grounded answer with source and last-updated fields.
- Frontend-to-backend integration works after env alignment and redeploy.

### Intermittent behaviors observed during stabilization
- Initial 502 / keep-alive closure on factual path before warm-machine and timeout tuning.
- Cross-deployment inconsistencies when testing older Vercel deployment URLs.

---

## Final Working Configuration

### Fly
- `fly.toml` in repository root.
- Docker build forced via:

```toml
[build]
  dockerfile = "Dockerfile"
```

- Runtime service:

```toml
[http_service]
  internal_port = 8080
  force_https = true
  auto_start_machines = true
  auto_stop_machines = false
  min_machines_running = 1
```

### Vercel
- `NEXT_PUBLIC_API_URL=https://rag-chatbot-wbqkcg.fly.dev`
- Redeploy after env updates.
- Prefer promoted production URL for testing over older immutable deployment URLs.

---

## Incident Runbook (Quick)

If users report timeout/502:
1. Check `GET /health`.
2. Check `GET /debug/paths`.
3. Test advisory query (light path).
4. Test factual query (heavy path).
5. Inspect Fly runtime logs around request timestamp.
6. Verify machine state in Fly `Machines` tab (started, not repeatedly restarting).
7. Verify Vercel env target and deployment freshness.

---

## Follow-Up Recommendations

- Add structured timing logs for each `/api/chat` stage: guardrail -> retrieval -> generation.
- Add uptime checks and alerting for 5xx spikes.
- Keep a rollback-ready previous deployment in Vercel.
- Periodically review dependency split to keep runtime image minimal.
- Consider managed vector backend if traffic or corpus size grows substantially.
