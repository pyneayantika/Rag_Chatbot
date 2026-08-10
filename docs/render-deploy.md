# Deploy backend to Render

Frontend stays on **Vercel**. Backend moves from Fly.io to **Render** using the existing Dockerfile.

## 1. Disconnect Fly.io (optional but recommended)

In GitHub → **Settings → Integrations → Fly.io**, disable auto-deploy for this repo so corpus commits stop showing failed Fly deploys.

## 2. Create the Render service

**Option A — Blueprint (recommended)**

1. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**
2. Connect repo `pyneayantika/Rag_Chatbot`
3. Render reads `render.yaml` and creates `rag-chatbot-api`
4. When prompted, set secrets:
   - `GROQ_API_KEY` — required for chat generation
   - `GEMINI_API_KEY` — only if using `EMBEDDING_PROVIDER=gemini`

**Option B — Manual**

1. **New** → **Web Service** → connect repo
2. **Runtime:** Docker
3. **Dockerfile path:** `./Dockerfile`
4. **Region:** Singapore (closest to India)
5. **Health check path:** `/health`
6. Add environment variables (see below)

## 3. Environment variables (Render)

| Variable | Value | Required |
|----------|-------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes |
| `EMBEDDING_PROVIDER` | `local` (default) or `gemini` | No |
| `CHROMA_API_IMPL` | `chromadb.api.segment.SegmentAPI` | Set in `render.yaml` |
| `GEMINI_API_KEY` | Gemini key | Only if `EMBEDDING_PROVIDER=gemini` |

## 4. Point Vercel at Render

After the first successful deploy, copy the Render URL (e.g. `https://rag-chatbot-api.onrender.com`).

In **Vercel** → Project → **Settings** → **Environment Variables**:

```
NEXT_PUBLIC_API_URL=https://rag-chatbot-api.onrender.com
```

Redeploy the Vercel frontend (Deployments → … → Redeploy).

## 5. Verify

```bash
curl https://rag-chatbot-api.onrender.com/health
curl https://rag-chatbot-api.onrender.com/debug/paths
```

`vectorstore_loaded` should be `true` and `doc_count` around `401`.

---

## Memory: free tier (512 MB)

Render **free** and **Starter** plans have **512 MB RAM**. Loading local HuggingFace embeddings + torch can exceed that (this was the original reason for leaving Render).

**Try first:** default `Dockerfile` (CPU-only torch + singleton caching). First chat request may take 30–90s on a cold start.

**If the service crashes or logs show OOM:**

### Plan A — Gemini embeddings (fits free tier)

1. In Render, set `Dockerfile path` to `./Dockerfile.lite`
2. Set `EMBEDDING_PROVIDER=gemini` and `GEMINI_API_KEY`
3. Rebuild the Chroma index with Gemini (locally or via workflow):
   ```bash
   EMBEDDING_PROVIDER=gemini GEMINI_API_KEY=... python src/ingestion/embedder.py
   git add chroma_db/ && git commit -m "chore: rebuild chroma with gemini for Render" && git push
   ```
4. Redeploy on Render

### Plan B — Upgrade Render plan

Upgrade to **Standard** (2 GB RAM) to keep `EMBEDDING_PROVIDER=local` with the default `Dockerfile`.

---

## Cold starts (free tier)

Free instances spin down after ~15 minutes of inactivity. The first request after idle can take up to a minute. The Vercel frontend health check timeout is tuned for this.

## Local development

```bash
pip install -r requirements-api.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8080
```

Frontend (with `NEXT_PUBLIC_API_URL` unset) defaults to `http://localhost:8080`.
