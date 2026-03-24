# CareerFlow

> **Context-Aware Career Orchestration Engine** — a personalized AI dashboard
> that tailors resumes, humanises cover letters, and simulates interviews across
> distinct professional personas.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Next.js Dashboard                        │
│  Job Description ──► Persona Selector ──► Run Pipeline Button   │
│  Results: Tailored Resume | Cover Letter | Interview Script      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /orchestrate
┌───────────────────────────▼─────────────────────────────────────┐
│                        FastAPI Backend                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   LangGraph Router                        │   │
│  │                                                           │   │
│  │  [START] ──► Resume Tailor ──► Cover Letter Humanizer    │   │
│  │                ──► Interview Simulator ──► [END]          │   │
│  └───────────────────────────┬──────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────▼──────────────────────────────┐   │
│  │           LlamaIndex Memory Bank (VectorStore)            │   │
│  │   Resumes · Essays · Cover Letters  (metadata-tagged)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Pydantic models enforce structured JSON output                  │
│  LangSmith traces every retrieval & LLM call                     │
└─────────────────────────────────────────────────────────────────┘
```

### Key components

| Layer | Technology | Role |
|---|---|---|
| Memory | LlamaIndex + OpenAI Embeddings | Ingests & vectorises resumes, essays, cover letters |
| Orchestration | LangGraph | Stateful graph routing three specialist nodes |
| Node A | LangChain + GPT-4o | **Resume Tailor** — aligns impact metrics; no hallucinations |
| Node B | LangChain + GPT-4o | **Cover Letter Humanizer** — prose only, no jargon |
| Node C | LangChain + GPT-4o | **Interview Simulator** — custom mock script + prep Qs |
| Schema | Pydantic v2 | Strict JSON output consumed by the frontend |
| Observability | LangSmith | Traces every retrieval step and LLM call |
| Frontend | Next.js 14 + Tailwind | Dashboard with tabbed results viewer |

---

## Supported Personas

| Persona | Base resume |
|---|---|
| Software Engineering | `data/resumes/software_engineering/` |
| Product Management | `data/resumes/product_management/` |
| Operations & Marketing | `data/resumes/operations_marketing/` |
| UI/UX & Graphic Design | `data/resumes/ui_ux_design/` |

Drop any `.md` or `.txt` file into the appropriate directory and trigger a
rebuild (`POST /index/rebuild`) to add it to the vector store.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- An OpenAI API key
- *(Optional)* A LangSmith API key for tracing

### 1. Clone & configure

```bash
git clone https://github.com/AAsteriskz7/CareerFlow.git
cd CareerFlow
cp .env.example .env          # fill in OPENAI_API_KEY (and optionally LANGCHAIN_API_KEY)
```

### 2. Backend

```bash
cd backend
pip install poetry
poetry install
poetry run uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

Run tests:
```bash
cd backend
poetry run pytest -v
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 4. Add your own documents

Place your resumes, essays, and cover letters in the `data/` directory:

```
data/
├── resumes/
│   ├── software_engineering/   ← .md / .txt files
│   ├── product_management/
│   ├── operations_marketing/
│   └── ui_ux_design/
├── essays/                     ← personal statements, writing samples
└── cover_letters/              ← past cover letters for style examples
```

Then rebuild the index:
```bash
curl -X POST http://localhost:8000/index/rebuild
```

---

## Project Structure

```
CareerFlow/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── schemas/             # Pydantic output models (schema enforcer)
│   │   ├── memory/              # LlamaIndex ingestion & retrieval
│   │   ├── graph/
│   │   │   ├── router.py        # LangGraph compiled graph
│   │   │   ├── state.py         # Shared GraphState TypedDict
│   │   │   └── nodes/
│   │   │       ├── resume_tailor.py
│   │   │       ├── cover_letter_humanizer.py
│   │   │       └── interview_simulator.py
│   │   └── tracing/             # LangSmith setup
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Landing page
│   │   │   └── dashboard/
│   │   │       └── page.tsx     # Main dashboard
│   │   ├── components/
│   │   │   ├── ResumeViewer.tsx
│   │   │   ├── CoverLetterViewer.tsx
│   │   │   └── InterviewSimulator.tsx
│   │   ├── lib/
│   │   │   └── api.ts           # Typed API client
│   │   └── types/
│   │       └── index.ts         # TypeScript types (mirrors Pydantic models)
│   └── package.json
├── data/
│   ├── resumes/{persona}/
│   ├── essays/
│   └── cover_letters/
├── .env.example
└── README.md
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for LLM calls and embeddings |
| `LANGCHAIN_TRACING_V2` | ☑️ | Set `true` to enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | ☑️ | LangSmith API key |
| `LANGCHAIN_PROJECT` | ☑️ | LangSmith project name (default: `CareerFlow`) |
| `LLAMA_INDEX_STORAGE_DIR` | ☑️ | Where to persist the vector index (default: `./storage`) |
| `NEXT_PUBLIC_API_URL` | ☑️ | Backend URL seen by the browser (default: `http://localhost:8000`) |
