<p align="center">
  <img src="https://img.shields.io/badge/Nazar-AI%20Platform-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDRjLTQuNTcgMC04LjM1IDMuMDQtOS41NiA3LjE5QTEgMSAwIDAgMCAyIDEyYzAgLjI4LjA5LjU0LjI0Ljc2QzMuNjUgMTYuOTYgNy40MyAyMCAxMiAyMHM4LjM1LTMuMDQgOS41Ni03LjE5LjQ0LS40NC40NC0uODEgMC0uNzYtLjI0LS43NkMxMy41NiA0LjA0IDEyLjU3IDQgMTIgNHptMCAxNGMtMy4zNiAwLTYuMjItMi4xOS03LjMyLTUuMjVDNS43OCA5LjE5IDguNjQgNyAxMiA3czYuMjIgMi4xOSA3LjMyIDUuMjVDMTguMjIgMTUuODEgMTUuMzYgMTggMTIgMTh6Ii8+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMy41Ii8+PC9zdmc+" alt="Nazar" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
  <img src="https://img.shields.io/badge/Supabase-Cloud-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
</p>

# 👁 Nazar — AI for Industrial Knowledge Intelligence

> **Unified Asset & Operations Brain** — An AI-powered platform that unifies fragmented industrial knowledge across engineering drawings, maintenance records, safety procedures, inspection reports, and regulatory documents.

*"Every document connected. Every answer sourced. Every risk visible."*

---

## 🏭 Problem Statement

| Metric | Impact |
|--------|--------|
| **35%** of working hours wasted searching for information (McKinsey 2024) |
| **7–12** disconnected document systems per large Indian plant (NASSCOM-EY) |
| **18–22%** of unplanned downtime due to knowledge fragmentation (BIS Research) |
| **25%** of experienced engineers retiring within a decade — taking undocumented knowledge |

Nazar solves this by building a **unified knowledge brain** that connects all industrial documents, equipment data, and regulatory requirements into a single queryable AI platform.

---

## ✨ Key Features

### 🤖 AI-Powered Chat Assistant
- **4 Agent Modes**: General Copilot, Maintenance RCA, Compliance, Failure Analysis
- **Hybrid RAG**: Vector search (ChromaDB) + Knowledge Graph traversal (NetworkX)
- **Source Citations**: Every answer linked to originating documents
- **Confidence Scores**: 0-100% confidence per response
- **Markdown Rendering**: Rich formatted responses with tables, lists, code

### 🔗 Industrial Knowledge Graph
- **157 entities** connected via **228 relationships**
- Equipment → Processes → Documents → Regulations → Failures
- Interactive force-directed visualization
- Click-to-explore entity details

### 📋 Compliance Intelligence
- Maps Indian regulatory frameworks (Factory Act, OISD-118/144/150, PESO)
- Real-time compliance scoring with gap analysis
- Per-regulation drill-down with audit timelines

### 🔧 Maintenance Intelligence
- Equipment health monitoring with MTBF analysis
- Failure trend visualization
- Incident tracking with severity-coded cards
- Work order analytics (60+ records)

### 📄 Document Repository
- SOP management with processing status
- Auto-chunking & embedding for RAG retrieval
- 212 vector-indexed document chunks

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│         Dashboard · Chat · KG · Compliance · Docs        │
├─────────────────────────────────────────────────────────┤
│                   REST API (FastAPI)                      │
├──────────┬──────────┬───────────┬──────────┬────────────┤
│  SQLite  │ ChromaDB │ NetworkX  │ Gemini   │  Supabase  │
│  (Local) │ (Vectors)│ (Graph)   │ (AI/LLM) │  (Cloud)   │
└──────────┴──────────┴───────────┴──────────┴────────────┘
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16 (App Router) | Responsive SPA with light mode UI |
| **Backend** | FastAPI + Uvicorn | Async REST API, 62 tested endpoints |
| **AI/LLM** | Google Gemini 3.5 Flash | RAG generation, entity extraction |
| **Vector DB** | ChromaDB | Semantic search over 212 document chunks |
| **Graph DB** | NetworkX | Knowledge graph (157 nodes, 228 edges) |
| **Local DB** | SQLite (aiosqlite) | Equipment, work orders, inspections |
| **Cloud DB** | Supabase (PostgreSQL) | Optional cloud persistence & sync |
| **Embeddings** | sentence-transformers | all-MiniLM-L6-v2 for document embedding |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Nazar.git
cd Nazar
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend will:
- Initialize SQLite database
- Seed 24 equipment + 60 work orders + 20 inspections + 10 incidents
- Build knowledge graph (157 nodes, 228 edges)
- Index 212 document chunks in ChromaDB

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Start the dev server
npm run dev
```

### 4. Open the App

Navigate to **http://localhost:3000** in your browser.

---

## 📁 Project Structure

```
Nazar/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # App entry point & lifespan
│   │   ├── config.py          # Environment config (.env loader)
│   │   ├── seed_data.py       # Synthetic industrial data generator
│   │   ├── agents/            # AI agent implementations
│   │   │   └── unified_agent.py  # Gemini-powered unified agent (4 modes)
│   │   ├── models/            # Pydantic data models
│   │   ├── routers/           # API route handlers
│   │   │   └── api.py         # All REST endpoints
│   │   └── services/          # Core business logic
│   │       ├── database.py    # SQLite async operations
│   │       ├── knowledge_graph.py  # NetworkX graph engine
│   │       ├── vector_store.py     # ChromaDB vector search
│   │       └── supabase_db.py      # Supabase cloud sync
│   ├── requirements.txt
│   ├── .env.example           # Environment template
│   └── tests/                 # 62 API tests
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── layout.js          # Root layout (ToastProvider, ErrorBoundary)
│   │   ├── page.js            # Dashboard with skeleton loading
│   │   ├── chat/page.js       # AI Chat with markdown rendering
│   │   ├── knowledge/page.js  # Knowledge graph explorer
│   │   ├── compliance/page.js # Compliance dashboard
│   │   ├── maintenance/page.js# Maintenance intelligence
│   │   ├── documents/page.js  # Document repository
│   │   └── globals.css        # Design system (1300+ lines)
│   ├── components/            # Reusable UI components
│   │   ├── Sidebar.js         # Navigation with mobile hamburger
│   │   ├── Toast.js           # Toast notification system
│   │   ├── ErrorHandling.js   # Error boundary + skeletons
│   │   └── UIComponents.js    # Shared UI primitives
│   ├── lib/api.js             # API client
│   └── .env.example           # Frontend env template
├── docs/
│   └── supabase_schema.sql    # Supabase table creation SQL
├── data/                       # Synthetic demo data reference
├── .gitignore                  # Git ignore (secrets, caches, DBs)
└── README.md                   # This file
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Model name (default: `gemini-2.0-flash`) |
| `SUPABASE_URL` | No | Supabase project URL |
| `SUPABASE_KEY` | No | Supabase anon/service key |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | No | Backend URL (default: `http://localhost:8000`) |

---

## ☁️ Supabase Integration

Nazar supports optional cloud persistence via Supabase (PostgreSQL).

### Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Open **SQL Editor** and run the queries from [`docs/supabase_schema.sql`](docs/supabase_schema.sql)
3. Copy your **Project URL** and **anon key** from Settings → API
4. Add them to `backend/.env`:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key
   ```
5. Restart the backend — data will auto-sync to Supabase on startup

### Tables Created

| Table | Records | Description |
|-------|---------|-------------|
| `equipment` | 24 | Industrial assets (pumps, vessels, exchangers) |
| `work_orders` | 60 | Maintenance work orders |
| `inspections` | 20 | Safety & regulatory inspections |
| `incidents` | 10 | Incident & near-miss reports |
| `compliance_requirements` | 15 | Regulatory requirement mappings |
| `documents` | 3+ | Indexed SOPs & procedures |

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
```

**Results: 62/62 tests passing** ✅

| Test Suite | Count | Coverage |
|-----------|-------|----------|
| Root & Health | 8 | Server status, metadata |
| Dashboard | 6 | KPI stats, aggregations |
| Equipment | 6 | CRUD, filtering |
| Knowledge Graph | 10 | Graph queries, search, subgraphs |
| Compliance | 8 | Dashboard, requirements, gaps |
| Maintenance | 12 | Work orders, inspections, incidents |
| Documents | 2 | List, filtering |
| Chat / RAG | 8 | All 4 agent modes, context retrieval |

---

## 📱 Responsive Design

- **Desktop**: Full sidebar + content layout
- **Tablet (≤1024px)**: Compact grids
- **Mobile (≤768px)**: Hamburger menu, stacked layout
- **Phone (≤480px)**: Single-column, optimized inputs

---

## 🎨 UI Polish Features

| Feature | Description |
|---------|-------------|
| 🍔 Mobile hamburger | Animated sidebar toggle with backdrop overlay |
| ✨ Page transitions | Fade + slide-up animations on navigation |
| 🎯 Card hover effects | Lift + shadow bloom + icon scale |
| 💬 Typing indicator | 3-dot bounce animation while AI thinks |
| 🔔 Toast notifications | Slide-in toasts for success/error/warning |
| 💀 Skeleton loading | Shimmer placeholders during data fetch |
| 🔌 Connection banner | Auto-retry when backend is unreachable |
| ⚡ Error boundary | Friendly crash UI with reload button |

---

## 🏆 Evaluation Criteria Alignment

| Criterion | Weight | How Nazar Scores High |
|-----------|--------|-----------------------|
| **Business Impact** | 25% | Directly addresses 35% productivity loss, knowledge cliff |
| **Technical Excellence** | 25% | Hybrid GraphRAG, 4 agent modes, Supabase cloud |
| **Scalability** | 20% | Decoupled services, async API, cloud-ready |
| **User Experience** | 15% | Premium light UI, mobile-first, micro-animations |
| **Innovation** | 15% | Industrial ontology + GraphRAG fusion, Indian regulatory mapping |

---

## 📄 License

This project is built for the **AI for Industrial Knowledge Intelligence** hackathon challenge.

---

<p align="center">
  Built with confidence.
</p>
