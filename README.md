---
title: TraceAgent
emoji: 🕵️
sdk: docker
app_port: 7860
pinned: false
---

[![CI](https://github.com/eholt723/traceagent/actions/workflows/ci.yml/badge.svg)](https://github.com/eholt723/traceagent/actions/workflows/ci.yml)

# TraceAgent

An observable agentic research platform that runs a live AI pipeline and exposes every internal reasoning step in real time. Enter a research question, watch the agent plan its approach, search the web, decide whether the results are sufficient, and synthesize a final report — with the full reasoning trace visible and persistent.

The key distinction from a standard chatbot or RAG pipeline is that every decision is stored and displayed: what the planner decomposed the query into, what the reflector decided about search adequacy, whether it triggered another search loop, and what sources the synthesizer cited. Runs are public, forkable, and comparable side by side.

**[Live demo](https://eholt723-traceagent.hf.space)** — Hugging Face Spaces (Docker)

**[AWS demo](http://32.192.175.42:8000)** — EC2 + RDS + CloudWatch (plain HTTP, no domain yet)

---

## Features

- **Live reasoning trace** — WebSocket streaming shows each step as the agent executes it
- **Persistent run history** — all runs stored in PostgreSQL with full step detail; nothing is ephemeral
- **Activity wall** — public feed of all research runs with attribution
- **Fork** — clone any run with a modified query; lineage is tracked
- **Compare** — side-by-side diff of two runs: synthesis, steps, sources, loop count
- **Reflection loop** — agent explicitly evaluates whether search results are adequate and re-searches if not (up to 3 iterations)
- **Pipeline dashboard** — live stats page showing run counts, success rate, avg execution time, and reflection loop frequency; auto-refreshes every 30 seconds

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
| Database | PostgreSQL (RDS on AWS / Neon serverless), SQLAlchemy ORM |
| Validation | Pydantic v2 (schema-first) |
| Real-time | WebSocket via FastAPI |
| Frontend | React 19, Vite, Tailwind CSS |
| Hosting | EC2 (t3.micro) + RDS (db.t4g.micro), Hugging Face Spaces (Docker) |
| Observability | CloudWatch Logs + custom CloudWatch Metrics (6 metrics, live dashboard) |

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Browser (React)                     │
│      ActivityWall · RunDetail · Compare · Dashboard    │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP + WebSocket
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI backend                      │
│    /runs · /stats · /users/upsert · /ws/runs/{id}      │
└──────────────────────┬─────────────────────────────────┘
                       │ background task (POST /runs)
                       ▼
┌────────────────────────────────────────────────────────┐
│                   Agent Pipeline                       │
│                                                        │
│     ┌──────────┐     ┌──────────┐     ┌──────────┐     │
│     │ Planner  │────▶│ Searcher │────▶│ Reflector│     │
│     │ (Groq)   │     │ (Tavily) │     │  (Groq)  │     │
│     └──────────┘     └──────────┘     └─────┬────┘     │
│                            ▲                │ adequate │
│                            └── re-search ───┤          │
│                                             ▼          │
│                                     ┌────────────┐     │
│                                     │ Synthesizer│     │
│                                     │  (Groq)    │     │
│                                     └────────────┘     │
└──────────────────────┬─────────────────────────────────┘
                       │ step records written per stage
            ┌──────────┴───────────────┐
            ▼                          ▼
┌─────────────────────┐    ┌────────────────────────┐
│  PostgreSQL         │    │  AWS CloudWatch        │
│  (RDS / Neon)       │    │  Logs + 6 Metrics      │
└─────────────────────┘    └────────────────────────┘
```

| Layer | Responsibility |
|---|---|
| Browser (React) | SPA: submits queries, renders step trace, streams live via WebSocket |
| FastAPI backend | Routes, background task dispatch, WebSocket hub, static file serving |
| Agent Pipeline | Orchestrates planner → search → reflect → synthesize; persists each step |
| Groq (LLM) | Planner decomposition, reflection adequacy judgment, synthesis report |
| Tavily | Web search — one request per sub-question from the planner |
| PostgreSQL | Persistent store for Runs, Steps, Users; queried for activity wall and stats |
| CloudWatch | Structured logs (watchtower) + 6 custom metrics per run in `TraceAgent` namespace |
| Migrations | Alembic tracks schema versions; migrations applied manually before deploy |

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
.venv/bin/python -m pytest tests/unit/ -v
```

All external calls are mocked — no API keys or database credentials required to run the tests.

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
│   │   ├── search_client.py  # Tavily client wrapper
│   │   └── llm.py            # Groq wrapper (chat, chat_json)
│   ├── api/
│   │   ├── runs.py           # /runs endpoints
│   │   ├── users.py          # /users/upsert
│   │   ├── stats.py          # /stats endpoint
│   │   └── ws.py             # WebSocket /ws/runs/{id}
│   ├── schemas/              # Pydantic models (Run, Step, User, Stats, enums)
│   ├── models/               # SQLAlchemy ORM models
│   ├── crud.py               # DB operations (including get_stats aggregates)
│   ├── metrics.py            # CloudWatch custom metrics (6 metrics per run)
│   ├── database.py           # Engine, session, Base
│   ├── config.py             # Settings from environment
│   └── main.py               # FastAPI app, CORS, CloudWatch logging, static file serving
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
│           ├── About.jsx              # Portfolio/employer showcase page
│           ├── ActivityWall.jsx       # Public run feed + new research form
│           ├── RunDetail.jsx          # Full step trace, live WS, fork, compare
│           ├── Compare.jsx            # Side-by-side run comparison
│           └── Dashboard.jsx          # Pipeline metrics (auto-refreshes every 30s)
├── tests/
│   ├── conftest.py           # SQLite in-memory fixtures, pipeline mocked, get_db override
│   └── unit/
│       ├── test_core.py      # Unit tests for planner + reflector (parametrized LLM response shapes)
│       └── test_routes.py    # Full route coverage + stats endpoint
├── migrations/
│   ├── env.py                # Alembic runtime config — reads DATABASE_URL, sets target_metadata
│   └── versions/             # One .py file per schema revision
├── scripts/
│   └── test_cloudwatch.py    # Direct boto3 credential diagnostic
├── alembic.ini               # Alembic config (URL injected at runtime from env)
├── Dockerfile                # Multi-stage: Vite build → FastAPI serve
└── requirements.txt
```

---

## Migrations

TraceAgent uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations. Schema changes are tracked as versioned files in `migrations/versions/` so they can be applied incrementally to any live database without recreating tables from scratch.

### Apply all pending migrations

```bash
export DATABASE_URL=<your-connection-string>
.venv/bin/alembic upgrade head
```

Run this against each database separately — AWS RDS and Neon are independent and both need to be updated when a schema change is deployed.

**Always review the migration file before running against production.** The migration files are in `migrations/versions/`.

### Generate a new migration after changing ORM models

```bash
export DATABASE_URL=<your-connection-string>
.venv/bin/alembic revision --autogenerate -m "describe the change"
```

Alembic diffs the SQLAlchemy ORM models (`app/models/`) against the live schema and generates a migration file. Review the generated file before committing — autogenerate is not always perfect (it can miss some constraint changes or generate spurious ops).

### View migration history

```bash
.venv/bin/alembic history
.venv/bin/alembic current   # what revision the live DB is at
```

### Notes

- Migrations must be run against both **AWS RDS** and **Neon** separately when deploying schema changes.
- Neon connection strings require `?sslmode=require` — `migrations/env.py` adds it automatically if missing.
- `app/main.py` retains `create_all` as a fallback for environments that haven't been migrated yet (CI, fresh local installs). Once Alembic has been applied, `alembic_version` exists and `create_all` becomes a no-op.
- The `migrations/` folder is committed to the repo.

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

## AWS deployment

TraceAgent runs on AWS within the free tier alongside the Hugging Face Spaces demo.

**Infrastructure**

- **EC2** (t3.micro, us-east-1) — hosts the FastAPI backend and serves the built React frontend as static files
- **RDS** (PostgreSQL, db.t4g.micro, us-east-1) — VPC-only, not publicly accessible; EC2 connects via private subnet
- **CloudWatch Logs** — all application logs stream via `watchtower`; activates automatically when `AWS_ACCESS_KEY_ID` is present
- **CloudWatch Metrics** — 6 custom metrics emitted per run to the `TraceAgent` namespace: `RunsCompleted`, `RunsFailed`, `RateLimitErrors`, `PipelineDurationMs`, `ReflectionLoops`, `SearchLoopTriggered`

**EC2 environment variables**

```
GROQ_API_KEY=...
TAVILY_API_KEY=...
DATABASE_URL=postgresql://user:pass@your-rds-endpoint:5432/postgres
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
CLOUDWATCH_LOG_GROUP=traceagent
```

**Starting the server**

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```
