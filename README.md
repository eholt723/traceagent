---
title: TraceAgent
emoji: 🕵️
sdk: docker
app_port: 7860
pinned: false
---

# TraceAgent

An observable agentic research platform that runs a live AI pipeline and exposes every internal reasoning step in real time. Enter a research question, watch the agent plan its approach, search the web, decide whether the results are sufficient, and synthesize a final report — with the full reasoning trace visible and persistent.

The key distinction from a standard chatbot or RAG pipeline is that every decision is stored and displayed: what the planner decomposed the query into, what the reflector decided about search adequacy, whether it triggered another search loop, and what sources the synthesizer cited. Runs are public, forkable, and comparable side by side.

**[Live demo](https://eholt723-traceagent.hf.space)**

---

## Features

- **Live reasoning trace** — WebSocket streaming shows each step as the agent executes it
- **Persistent run history** — all runs stored in PostgreSQL with full step detail; nothing is ephemeral
- **Activity wall** — public feed of all research runs with attribution
- **Fork** — clone any run with a modified query; lineage is tracked
- **Compare** — side-by-side diff of two runs: synthesis, steps, sources, loop count
- **Reflection loop** — agent explicitly evaluates whether search results are adequate and re-searches if not (up to 3 iterations)

---

## How it works

The agent runs a fixed pipeline with four stages:

1. **Planner** — decomposes the query into 2–4 targeted sub-questions using the LLM before executing any searches
2. **Search** — runs each sub-question against the Tavily Search API and collects results
3. **Reflection** — evaluates result adequacy; if insufficient, generates refined queries and loops back to Search (capped at `max_search_loops`, default 3)
4. **Synthesis** — aggregates all search results and writes a structured markdown report with inline citations

Each step is persisted to the database as it completes and broadcast to connected WebSocket clients. The `POST /runs` endpoint returns immediately (201); the pipeline runs as a background task.

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent pipeline | Custom (no framework) |
| LLM | Groq — `llama-3.3-70b-versatile` |
| Web search | Tavily Search API |
| Backend | FastAPI, Python 3.12 |
| Database | Neon (serverless PostgreSQL), SQLAlchemy ORM |
| Validation | Pydantic v2 (schema-first) |
| Real-time | WebSocket via FastAPI |
| Frontend | React 18, Vite, Tailwind CSS |
| Deployment | Docker (multi-stage), Hugging Face Spaces |

---

## Local development

### Prerequisites

- Python 3.12+
- Node 18+
- A [Groq API key](https://console.groq.com) (free tier)
- A [Tavily API key](https://app.tavily.com) (free tier, 1,000 searches/month)
- A [Neon](https://neon.tech) database (free tier, no credit card)

### Setup

**1. Environment variables**

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/traceagent
```

**2. Python environment**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**3. Frontend dependencies**

```bash
cd ui && npm install && cd ..
```

### Running

Start the backend (terminal 1):

```bash
.venv/bin/uvicorn app.main:app --reload
```

Start the frontend (terminal 2):

```bash
cd ui && npm run dev
```

Open `http://localhost:5173`.

### Tests

```bash
.venv/bin/python -m pytest tests/ -v
```

> Note: the test suite calls the real Groq and Tavily APIs. Avoid running it on days when you need the Groq free-tier token budget for demos.

---

## API

### `POST /runs`

Create a new run. The pipeline starts immediately as a background task.

```json
{ "query": "your research question", "user_id": "optional-uuid" }
```

Returns `201` with the new run record. Connect to the WebSocket to stream progress.

### `GET /runs`

List recent runs (public). Supports `limit` and `offset` query params.

### `GET /runs/{id}`

Get a single run with all steps.

### `POST /runs/{id}/fork`

Fork a run with a new query, preserving the lineage via `forked_from_id`.

### `WebSocket /ws/runs/{id}`

Stream step events for a run. Event types:

| Event | Description |
|---|---|
| `step_complete` | One pipeline step finished (planner / search / reflection / synthesis) |
| `run_complete` | Pipeline finished successfully |
| `run_error` | Pipeline failed; includes a human-readable error message |

---

## Project structure

```
traceagent/
├── app/
│   ├── agent/
│   │   ├── pipeline.py       # Orchestrates full pipeline, persists steps, emits WS events
│   │   ├── planner.py        # Decomposes query into sub-questions
│   │   ├── searcher.py       # Runs Tavily search per sub-question
│   │   ├── reflector.py      # Evaluates adequacy, returns refined queries if needed
│   │   ├── synthesizer.py    # Writes markdown report with inline citations
│   │   └── llm.py            # Groq wrapper (chat, chat_json)
│   ├── api/
│   │   ├── runs.py           # /runs endpoints
│   │   ├── users.py          # /users/upsert
│   │   └── ws.py             # WebSocket /ws/runs/{id}
│   ├── schemas/              # Pydantic models (Run, Step, User, enums)
│   ├── models/               # SQLAlchemy ORM models
│   ├── crud.py               # DB operations
│   ├── database.py           # Engine, session, Base
│   ├── config.py             # Settings from environment
│   └── main.py               # FastAPI app, CORS, static file serving
├── ui/
│   └── src/
│       ├── App.jsx                    # Router, user context, footer
│       ├── UserContext.jsx            # Browser UUID + name, /users/upsert
│       ├── api.js                     # fetch wrappers, BASE URL logic
│       ├── components/
│       │   ├── Header.jsx             # Nav, dark mode toggle
│       │   ├── RunCard.jsx            # Run row in activity wall
│       │   ├── StepBlock.jsx          # Collapsible step renderer
│       │   └── NameModal.jsx          # First-visit name prompt
│       └── pages/
│           ├── ActivityWall.jsx       # Public run feed + new research form
│           ├── RunDetail.jsx          # Full step trace, live WS, fork, compare
│           └── Compare.jsx            # Side-by-side run comparison
├── tests/
├── Dockerfile                # Multi-stage: Vite build → FastAPI serve
└── requirements.txt
```

---

## Deployment

The `Dockerfile` uses a two-stage build: the first stage builds the React app with Vite (`VITE_API_URL=""` so all requests go to the same origin), the second stage runs the FastAPI backend and serves the built frontend as static files.

### Hugging Face Spaces

1. Create a new Space at [huggingface.co](https://huggingface.co), set SDK to **Docker**
2. Push this repo to the Space's git remote
3. Under **Settings → Variables and Secrets**, add:
   - `GROQ_API_KEY` (secret)
   - `TAVILY_API_KEY` (secret)
   - `DATABASE_URL` (secret) — your Neon connection string
4. Click **Factory rebuild** to deploy

---

## Roadmap — v2

The next version will add a live observability dashboard, surfacing aggregate stats computed directly from the existing run and step data:

- **Total runs** and average steps per run
- **Reflection loop rate** — how often the agent decides search results are insufficient and loops back
- **Success rate** — completed runs vs. failed
- **Average execution time** — full pipeline and per-stage breakdown
- **Per-stage timing** — how long planner, search, reflection, and synthesis each take on average

The goal is to make the observability explicit and visual: the user will be able to open the dashboard and immediately see the agent's behavior patterns across all runs.

No database schema changes are required — all metrics are derived from the existing `runs` and `steps` tables.
