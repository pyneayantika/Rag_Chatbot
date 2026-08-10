# Deploy backend to Railway (Hobby plan)

Frontend stays on **Vercel**. Backend runs on **Railway** using the root `Dockerfile`.

Recommended for portfolio hosting: **~$5/month**, **1 GB RAM**, daily corpus scheduler **paused**.

## 1. Prerequisites

- [Railway](https://railway.app) account on the **Hobby** plan ($5/mo minimum)
- GitHub repo connected
- **Groq API key** for chat generation
- **Vercel** project for the Next.js frontend

## 2. Create the Railway service

1. Railway Dashboard → **New Project** → **Deploy from GitHub repo**
2. Select `pyneayantika/Rag_Chatbot`
3. Railway detects the **Dockerfile** automatically
4. Open the service → **Settings**:
   - **Builder:** Dockerfile
   - **Dockerfile path:** `Dockerfile`
   - **Root directory:** `/` (repo root)

## 3. Set resources (important)

Open **Settings** → **Resources** (or **Deploy** → resource slider):

| Setting | Value |
|---------|-------|
| **Memory** | **1024 MB (1 GB)** |
| **vCPU** | 1 (default is fine) |

512 MB is **not enough** for local HuggingFace embeddings + torch (same issue as Render free tier).

## 4. Environment variables

In **Variables**:

| Variable | Value | Required |
|----------|-------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |
| `EMBEDDING_PROVIDER` | `local` | Yes (matches committed `chroma_db`) |
| `CHROMA_API_IMPL` | `chromadb.api.segment.SegmentAPI` | Yes |
| `PORT` | Railway sets this automatically | No action needed |

Optional (only for Gemini lite profile):

| Variable | Value |
|----------|-------|
| `EMBEDDING_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | Your Gemini key |

Use `Dockerfile.lite` instead of `Dockerfile` if you switch to Gemini embeddings.

## 5. Networking

1. Service → **Settings** → **Networking** → **Generate domain**
2. Copy the public URL (e.g. `https://rag-chatbot-production.up.railway.app`)

## 6. Point Vercel at Railway

Vercel → Project → **Settings** → **Environment Variables**:

```
NEXT_PUBLIC_API_URL=https://your-service.up.railway.app
```

Redeploy the Vercel frontend (**Deployments** → **Redeploy**).

## 7. Verify

```bash
curl https://your-service.up.railway.app/health
curl https://your-service.up.railway.app/debug/paths
```

Expected:

- `/health` → `{"status":"ok",...}`
- `/debug/paths` → `"vectorstore_loaded": true`, `"doc_count": ~401`

Test a factual question in the UI (e.g. expense ratio of HDFC Mid Cap).

## 8. Corpus scheduler (paused)

The daily GitHub Actions workflow (`.github/workflows/daily_ingestion.yml`) is **paused** so:

- No daily git commits / redeploy churn
- Stable demo for portfolio visitors
- Existing `chroma_db` in the repo continues to serve answers

**Manual refresh** (optional): GitHub → **Actions** → **Daily Corpus Refresh** → **Run workflow**.

**Re-enable daily cron:** uncomment the `schedule` block in `daily_ingestion.yml`.

## 9. Cost tips (~$5/month)

- Run **one** Railway service only
- Keep RAM at **1 GB** (not 2–4 GB unless needed)
- Leave scheduler paused for portfolio mode
- Disconnect **Fly.io** GitHub integration if still enabled (avoids failed deploy noise)

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Service crashes on first chat | Increase RAM to 1 GB |
| `vectorstore_loaded: false` | Check `EMBEDDING_PROVIDER=local` matches `chroma_db/embedding_provider.txt` |
| Vercel shows errors | Confirm `NEXT_PUBLIC_API_URL` and redeploy frontend |
| OOM in Railway logs | Use `Dockerfile.lite` + `EMBEDDING_PROVIDER=gemini` and rebuild Chroma |
| Slow first response | Normal on cold start while embedding model loads (~30–60s) |

## Local development

```bash
pip install -r requirements-api.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8080
```

Frontend defaults to `http://localhost:8080` when `NEXT_PUBLIC_API_URL` is unset.
