# 🚀 CareerPilot: Production-Oriented AI Job Search & Career Recommendation Agent

CareerPilot is an AI career assistant and recommendation engine designed to bridge software engineers with high-alignment job opportunities. Unlike standard job boards or simple chatbot wrappers, CareerPilot combines **dense vector embeddings** (pgvector), **deterministic skill-overlap math**, and an **autonomous conversational agent with native tool execution**.

---

## 🏗️ Architecture & Technical Stack

```
               +--------------------------------------------------------+
               |             React 18 + Vite + TypeScript               |
               |         Tailwind CSS • Lucide Icons • Axios            |
               +---------------------------+----------------------------+
                                           |  REST API / JWT
                                           v
               +--------------------------------------------------------+
               |              FastAPI Application Server                |
               |      Pydantic v2 • Security (bcrypt/JWT) • CORS        |
               +-------------+----------------------------+-------------+
                             |                            |
       +---------------------+---+            +-----------+------------+
       | Deterministic Scoring   |            | Autonomous Agent Loop  |
       | Skill Overlap (35%)     |            | Tools: search_jobs,    |
       | Semantic Cosine (30%)   |            | recommend_jobs,        |
       | Role Alignment (15%)    |            | get_user_profile,      |
       | Location Match (10%)    |            | save_job               |
       | Compensation (10%)      |            +-----------+------------+
       +-------------+-----------+                        |
                     |                                    v
                     |                        +------------------------+
                     |                        |  Google Gemini API     |
                     |                        |  gemini-1.5-flash      |
                     |                        |  text-embedding-004    |
                     |                        +------------------------+
                     v                                    |
+---------------------------------------------------------+------------+
|                        PostgreSQL + pgvector                         |
|   10 Relational & Vector Tables: users, candidate_profiles, jobs,    |
|   job_skills, resumes, saved_jobs, recommendations, conversations    |
+----------------------------------------------------------------------+
```

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Axios.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0.
- **Database & Vectors**: PostgreSQL with `pgvector` (with automatic fallback vector math for local SQLite zero-config testing).
- **Intelligence**: Google Gemini API (`gemini-1.5-flash`) + `text-embedding-004` (with offline fallback heuristics).
- **Testing & Evals**: Pytest (100% test pass rate), Retrieval Benchmarks ($P@K$, $R@K$, MRR, NDCG).
- **Deployment**: Multi-stage Dockerfiles, Docker Compose, Render Blueprint (`render.yaml`).

---

## ✨ Verified Key Features

| Feature | Engineering Implementation | Status |
| :--- | :--- | :--- |
| **Authentication & Profiles** | JWT Bearer tokens, bcrypt hashing, automated candidate profile & preferences creation. | ✅ Verified |
| **Resume Text & PDF Ingestion** | `pypdf` text extraction from uploaded PDF resumes. | ✅ Verified |
| **Structured Resume Parsing** | Gemini JSON structuring into skills, experience, education, headline, and summary. | ✅ Verified |
| **Embedding Generation** | 768-dimensional dense representations for candidate skills and job descriptions. | ✅ Verified |
| **Semantic & Hybrid Search** | Cosine similarity ranking combined with keyword overlap and metadata filters. | ✅ Verified |
| **Deterministic Recommendation Engine** | Strictly mathematical multi-factor scoring ($S_{skills}, S_{sem}, S_{role}, S_{loc}, S_{pref}$). Zero LLM hallucinated match percentages. | ✅ Verified |
| **Autonomous Conversational Agent** | Genuine backend tool execution (`recommend_jobs`, `search_jobs`, `get_user_profile`, `save_job`) with context memory. | ✅ Verified |
| **Application Pipeline Tracker** | Full CRUD for tracking status: SAVED $\rightarrow$ APPLIED $\rightarrow$ INTERVIEWING $\rightarrow$ OFFERED $\rightarrow$ REJECTED. | ✅ Verified |
| **Retrieval Benchmarks & Evals** | Evaluation script calculating $P@K$, $R@K$, MRR, NDCG, and schema validity. | ✅ Verified |
| **Local & Render Deployability** | Standard Dockerfiles, Docker Compose, and `render.yaml` infrastructure blueprint. | ✅ Verified |

---

## ⚡ Quick Start: Running Locally

### Option 1: Native Local Run (Zero-Friction, Fast)

Both frontend and backend are already set up in the workspace.

#### 1. Start the FastAPI Backend
```bash
# In terminal 1:
cd /Users/neerajashokpatil/Downloads/CareerPilot
source backend/venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- API Health Check: `http://localhost:8000/healthz`
- Interactive OpenAPI Swagger Docs: `http://localhost:8000/api/v1/docs`

#### 2. Start the React Frontend
```bash
# In terminal 2:
cd /Users/neerajashokpatil/Downloads/CareerPilot/frontend
npm run dev
```
- Open your browser at: **`http://localhost:5173`**
- Click **"1-Click Test Drive (Demo Account)"** on the top-right to log in instantly.

---

### Option 2: Docker Compose (Full Stack with PostgreSQL + pgvector)

```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- PostgreSQL pgvector: `localhost:5432`

---

## 🧪 Automated Testing & Evaluation Benchmarks

Run the complete Pytest test suite:
```bash
PYTHONPATH=backend ./backend/venv/bin/pytest backend/tests -v
```

### Retrieval & Schema Evaluation Benchmark
To run the evaluation script assessing ranking quality ($P@K$, Recall, NDCG, MRR) against the ground-truth benchmark queries:
```bash
PYTHONPATH=backend ./backend/venv/bin/python3 backend/evals/evaluate_retrieval.py
```

**Benchmark Results:**
```
=======================================================
      CAREERPILOT RETRIEVAL EVALUATION BENCHMARK       
=======================================================
Total Benchmark Queries: 5
Total Database Job Corpus: 8

--- Retrieval Metrics ---
K = 1:  Precision@1: 1.000 | Recall@1: 0.433 | NDCG@1: 1.000
K = 3:  Precision@3: 0.667 | Recall@3: 0.867 | NDCG@3: 0.984
K = 5:  Precision@5: 0.400 | Recall@5: 0.867 | NDCG@5: 0.984
Mean Reciprocal Rank (MRR): 1.000

--- Structured-Output Schema Validity Test ---
Schema Conformance: 100.0%
Extracted Skills Count: 8
Extracted Role: 'Jordan Lee - Staff AI Platform Architect'
=======================================================
✅ ALL BENCHMARK & SCHEMA EVALUATION CHECKS PASSED.
```

---

## 🌐 Render Deployment Walkthrough

CareerPilot is ready to deploy to Render using the included `render.yaml` blueprint.

### Step 1: Push Code to GitHub
```bash
cd /Users/neerajashokpatil/Downloads/CareerPilot
git init
git add .
git commit -m "feat: CareerPilot full-stack AI career recommendation agent"
git branch -M main
git remote add origin https://github.com/<your-username>/careerpilot.git
git push -u origin main
```

### Step 2: Deploy Blueprint on Render
1. Log into your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **Blueprint**.
3. Connect your `careerpilot` GitHub repository.
4. Render will parse `render.yaml` and configure:
   - **`careerpilot-postgres`**: PostgreSQL database with `pgvector` extension.
   - **`careerpilot-backend`**: FastAPI web service with automatic database URL binding and `/healthz` health checks.
   - **`careerpilot-frontend`**: React static site with SPA routing rewrites.
5. In the backend service environment variables, set:
   - **`GEMINI_API_KEY`** to your Google Gemini API key.
   - **`CORS_ORIGINS`** to your deployed frontend URL (for example, `https://careerpilot-frontend.onrender.com`). Separate multiple origins with commas.
6. Click **Apply**. Render will automatically provision the database, install requirements, and deploy both services.

---

## 📌 Remaining Limitations & Production Roadmap

1. **Third-Party Job Sync**: The current seed dataset has 8 realistic tech jobs. In production, connect live API adapters (such as Adzuna, Reed, or GitHub Jobs archives) to ingest tens of thousands of jobs daily.
2. **Asynchronous Background Tasks**: Resume parsing currently runs within the HTTP request cycle (<3 seconds). For large resumes or batch ingestion, offload parsing to Celery / Redis worker queues.
3. **Multi-tenant Auth**: Expand authentication with OAuth2 social providers (GitHub / Google login) alongside standard email/password.
