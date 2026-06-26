# Paper to Product Advisor

> **Give your research the weight it deserves.**

Turn a research paper into a venture-ready product blueprint - automatically.

🔗 **Live app:** [paper2product.vercel.app](https://paper2-product.vercel.app/)

---

## What is this?

Most groundbreaking research never becomes a product. Researchers know their domain deeply but rarely have the time — or the cross-disciplinary expertise — to evaluate whether their work has commercial legs, who would buy it, what an MVP would look like, or whether it's even fundable.

**Paper to Product Advisor** closes that gap. Upload a research paper, patent, or technical abstract, and a pipeline of 15 specialist AI agents reads it the way a venture studio team would: a technical reviewer, a market analyst, a product manager, an architect, a CFO, a risk officer, and a VC all weigh in — then debate each other, and a final "judge" agent delivers a verdict.

The output isn't a vague summary. It's a structured report with market sizing, customer personas, a competitive landscape, an MVP roadmap, a technical architecture, a revenue model, a risk matrix, an investment score, and a clear **GO / NO-GO / CONDITIONAL-GO** recommendation — with every claim traceable back to the reasoning that produced it.

---

## Features

- **15-agent analysis pipeline** — each agent is a specialist focused on one dimension of commercial viability
- **Reasoning logs & confidence scores** — every agent explains *why* it reached its conclusion, not just *what* the conclusion is
- **Source citations** — outputs are linked back to specific sections of the input document or to live web search results
- **Agent debate stage** — four agents argue FOR / AGAINST / CHALLENGE / SKEPTICAL on the opportunity before a Judge agent rules
- **Multi-dimensional opportunity score** — a weighted 6-factor score (technical feasibility, market opportunity, competitive advantage, execution difficulty, revenue potential, risk-adjusted return), not just a single number
- **Knowledge graph** — automatically extracted entities, relationships, and concept clusters from the paper
- **Portfolio view** — upload multiple papers and rank them side-by-side by opportunity score
- **Export anywhere** — download the full report as PDF, DOCX, or Markdown
- **Full agent traceability** — runtime, token usage, and cost logged per agent, per run
- **Human-in-the-loop checkpoints** — pause the pipeline for user approval before continuing down a given direction
- **Live progress streaming** — watch each agent work in real time via Server-Sent Events

---

## Tech stack

| Layer | Technology | Why it's used |
|---|---|---|
| **Frontend** | React + Tailwind CSS | Fast, component-based UI with utility-first styling for rapid iteration |
| **Charts** | Recharts | Renders the opportunity-score radar/bar charts and portfolio comparisons |
| **Backend** | FastAPI (Python) | High-performance async API framework with automatic docs and Pydantic validation |
| **Agent orchestration** | LangGraph + LangChain | Defines the multi-agent pipeline as a graph, manages state passing between agents, and standardises LLM calls |
| **LLM provider** | Groq (Llama 3.3 70B & Llama 3.1 8B) | Extremely fast inference at zero cost on the free tier — essential for running 15 agents per analysis without rate-limit pain |
| **Database** | PostgreSQL via Neon | Serverless Postgres with a generous free tier — stores users, projects, and the full per-agent run history for traceability |
| **Cache / streaming** | Redis via Upstash | Serverless Redis used to push live agent-progress updates to the frontend over SSE without hammering the database |
| **Web search** | Tavily | Gives the Market Discovery and Competitor Intelligence agents access to live web results, so market sizes and competitor lists reflect current data rather than the model's training cutoff |
| **PDF/DOCX parsing** | pypdf, python-docx | Extracts raw text from uploaded research papers |
| **Report export** | ReportLab, python-docx, markdown | Generates downloadable PDF, DOCX, and Markdown versions of the final report |
| **Auth** | JWT (python-jose) + passlib | Stateless authentication for multi-user support |
| **Hosting — frontend** | Vercel | Zero-config deploys for React, generous free tier, instant previews |
| **Hosting — backend** | Render | Free-tier web service hosting for the FastAPI backend |

---

## Model architecture

```
                                 ┌───────────────────────────┐
                                 │   User uploads paper      │
                                 │   (PDF / text / abstract) │
                                 └────────────┬──────────────┘
                                              │
                                              ▼
                                 ┌───────────────────────────┐
                                 │   1. Research Analyst     │
                                 │  Extracts problem,        │
                                 │  methodology, novelty     │
                                 └────────────┬──────────────┘
                                              ▼
                ┌─────────────────────────────────────────────────────┐
                │  2. Technical Validator     3. Market Discovery     │
                │  Scores feasibility &       Sizes the market &      │
                │  reproducibility             identifies use cases   │
                └─────────────────────────────────────────────────────┘
                                            ▼
           ┌──────────────────────────────────────────────────────────────────┐
           │  4. Customer Persona   5. Competitor Intel   6. Knowledge Graph  │
           │  Defines who buys      Maps competitors &     Extracts entities  │
           │  and why                whitespace              & relationships  │
           └──────────────────────────────────────────────────────────────────┘
                                            ▼
           ┌────────────────────────────────────────────────────────────────┐
           │  7. Product Strategist   8. MVP Planner   9. Architect         │
           │  Defines product         Scopes the        Designs the system  │
           │  concepts & positioning   minimum build      architecture      │
           └────────────────────────────────────────────────────────────────┘
                                            ▼
           ┌────────────────────────────────────────────────────────────────┐
           │ 10. Revenue Strategy   11. Risk Analyst   12. Investment Agent │
           │ Pricing & projections   Technical, market,  VC-style funding   │
           │                          regulatory risk     score & path      │
           └────────────────────────────────────────────────────────────────┘
                                              ▼
                                 ┌─────────────────────────────┐
                                 │  13. Opportunity Scorer     │
                                 │  Combines all signals into  │
                                 │  a weighted 6-dim score     │
                                 └────────────┬────────────────┘
                                              ▼
                                 ┌─────────────────────────────┐
                                 │      14. Debate Stage       │
                                 │  Product / Risk / Competitor│
                                 │  / Investment agents argue  │
                                 └────────────┬────────────────┘
                                              ▼
                                   ┌──────────────────────────┐
                                   │      15. Judge Agent     │
                                   │  Resolves the debate and │
                                   │  issues final GO / NO-GO │
                                   │  verdict + full report   │
                                   └──────────────────────────┘
```

Every agent reads the shared analysis state, adds its own output (plus reasoning, confidence, and sources), and passes the enriched state to the next stage. The full state — including every intermediate agent output — is persisted, so the entire decision trail is auditable after the fact.

---

## Folder structure

```
research-to-product/
├── backend/
│   ├── app/
│   │   ├── agents/              # 15 specialist agents + shared LLM helper
│   │   │   ├── research_analyst.py
│   │   │   ├── technical_validator.py
│   │   │   ├── market_discovery.py
│   │   │   ├── customer_persona.py
│   │   │   ├── competitor_intel.py
│   │   │   ├── product_strategist.py
│   │   │   ├── mvp_planner.py
│   │   │   ├── architect.py
│   │   │   ├── revenue_strategy.py
│   │   │   ├── risk_analyst.py
│   │   │   ├── investment_agent.py
│   │   │   ├── knowledge_graph.py
│   │   │   ├── opportunity_scorer.py
│   │   │   ├── debate.py
│   │   │   ├── judge.py
│   │   │   └── llm_helpers.py    # Groq client, JSON parsing, retry logic
│   │   ├── core/                 # config, database session, auth, Redis cache
│   │   ├── graph/                # LangGraph workflow definition + shared state schema
│   │   ├── models/                # SQLAlchemy models — User, Project, AgentRun
│   │   ├── routers/                # FastAPI route handlers — auth, projects
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                  # PDF/DOCX text extraction, report export
│   │   ├── main.py                     # FastAPI app entrypoint
│   │   └── worker.py                    # background task that runs the pipeline
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/                  # axios client
    │   ├── components/             # shared UI components
    │   ├── hooks/                    # auth context/provider
    │   ├── pages/                      # Dashboard, Upload, Processing, Report, Portfolio, Auth
    │   └── App.jsx
    ├── package.json
    └── .env.example
```

---

## How it works

1. **Upload** — drag in a PDF, DOCX, or paste raw text/abstract on the Upload page
2. **Processing** — the backend extracts text, kicks off the 15-agent pipeline as a background task, and streams live progress to the frontend (one card per agent, with a loading spinner while it runs)
3. **Pipeline execution** — agents run in sequence, each one reading the outputs of prior agents from a shared state object and adding its own structured output, reasoning trail, confidence score, and sources
4. **Debate** — once all individual analyses are done, four agent personas debate the opportunity from different angles
5. **Judgment** — the Judge agent reads the entire debate transcript plus every prior output and produces the final verdict
6. **Report** — the frontend renders a full multi-tab report: Overview, Market, Product/MVP, Architecture, Revenue, Risk, Investment, Debate, Knowledge Graph, and Agent Logs
7. **Export / Compare** — download the report in PDF/DOCX/Markdown, or view it alongside other analyses in the Portfolio ranking

---

## API overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Get a JWT access token |
| `GET` | `/api/auth/me` | Get current user profile |
| `POST` | `/api/projects` | Upload a paper and start the analysis pipeline |
| `GET` | `/api/projects` | List all projects for the current user |
| `GET` | `/api/projects/{id}/status` | Poll pipeline progress |
| `GET` | `/api/projects/{id}/stream` | Live progress via Server-Sent Events |
| `GET` | `/api/projects/{id}/report` | Full structured report (all 15 agent outputs) |
| `GET` | `/api/projects/{id}/agents` | Per-agent traceability — reasoning, confidence, tokens, cost, duration |
| `GET` | `/api/projects/{id}/export/{format}` | Export report as `pdf`, `docx`, or `markdown` |
| `GET` | `/api/projects/portfolio/ranked` | Ranked list of all completed analyses by opportunity score |

---

## Running locally & deployment

### Built with

- **Local development:** VS Code, backend on `localhost:8000`, frontend on `localhost:3000`
- **Deployed on:**
  - **Vercel** — frontend (React build)
  - **Render** — backend (FastAPI, free web service)
  - **Neon** — managed PostgreSQL database
  - **Upstash** — managed Redis for live progress streaming
  - **Tavily** — live web search for market/competitor agents
  - **Groq** — LLM inference for all 15 agents

### 1. Clone

```bash
git clone https://github.com/<your-username>/research-to-product.git
cd research-to-product
```

### 2. Backend — runs on `localhost:8000`

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# fill in GROQ_API_KEY, DATABASE_URL (Neon), SECRET_KEY,
# and optionally UPSTASH_*  and TAVILY_API_KEY

uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on first run — no migrations needed.

### 3. Frontend — runs on `localhost:3000`

```bash
cd frontend
npm install

cp .env.example .env
# set REACT_APP_API_URL=http://localhost:8000

npm start
```

### 4. Deploying

| Service | What to do |
|---|---|
| **Render** (backend) | New Web Service → root dir `backend` → build `pip install -r requirements.txt` → start `uvicorn app.main:app --host 0.0.0.0 --port $PORT` → add all env vars |
| **Vercel** (frontend) | Import repo → root dir `frontend` → set `REACT_APP_API_URL` to your Render URL → deploy |
| **Neon** | Create a free Postgres project → copy connection string into `DATABASE_URL` |
| **Upstash** | Create a free Redis database → copy REST URL + token into `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` (optional — falls back to polling without it) |
| **Tavily** | Create a free account → copy API key into `TAVILY_API_KEY` (optional — agents fall back to model knowledge without it) |
| **Groq** | Create a free account → copy API key into `GROQ_API_KEY` (required) |

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✔ | LLM inference for all 15 agents |
| `DATABASE_URL` | ✔ | Neon PostgreSQL connection string |
| `SECRET_KEY` | ✔ | Random secret used to sign JWTs |
| `UPSTASH_REDIS_REST_URL` | optional | Enables live SSE progress streaming |
| `UPSTASH_REDIS_REST_TOKEN` | optional | Paired with the URL above |
| `TAVILY_API_KEY` | optional | Enables live web search for Market Discovery & Competitor Intel agents |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `REACT_APP_API_URL` | ✔ | Base URL of the backend API (no trailing slash) |

---

## The 15 agents

| # | Agent | Role |
|---|---|---|
| 1 | **Research Analyst** | Extracts the core problem, methodology, novelty, limitations, and key technologies from the paper |
| 2 | **Technical Validator** | Scores technical feasibility, reproducibility, and innovation level |
| 3 | **Market Discovery** | Sizes the addressable market and identifies concrete use cases (web-search grounded) |
| 4 | **Customer Persona** | Defines who would buy this, their pain points, and willingness to pay |
| 5 | **Competitor Intel** | Maps existing competitors, alternatives, and whitespace opportunities (web-search grounded) |
| 6 | **Product Strategist** | Proposes concrete product concepts and market positioning |
| 7 | **MVP Planner** | Scopes the minimum viable product and build timeline |
| 8 | **Architect** | Designs the technical architecture, stack, and infrastructure |
| 9 | **Revenue Strategy** | Recommends a pricing model and projects revenue |
| 10 | **Risk Analyst** | Surfaces technical, market, regulatory, and competitive risks |
| 11 | **Investment Agent** | Produces a VC-style investment score and funding roadmap |
| 12 | **Knowledge Graph** | Extracts entities, relationships, and concept clusters from the analysis |
| 13 | **Opportunity Scorer** | Combines every signal into a weighted 6-dimension opportunity score |
| 14 | **Debate** | Four personas (Product, Risk, Competitor, Investment) argue the case from different angles |
| 15 | **Judge** | Resolves the debate and delivers the final GO / NO-GO / CONDITIONAL-GO verdict |

---

## App access

🔗 **Live demo:** [https://paper2product.vercel.app](https://paper2-product.vercel.app/)

Create a free account to upload your first paper — analysis typically completes in a few minutes.
⚠ DISCLAIMER : Paper Analysis might not work if the key is out of tokens !!

---
