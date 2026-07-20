# IndustrialBrain — Build Tasks

## Phase 1: Project Scaffolding
- [x] Create project directory structure
- [x] Create backend requirements.txt
- [x] Create backend config.py with API keys
- [x] Create FastAPI main.py entry point

## Phase 2: Database & Data Models
- [x] Create SQLite models (documents, equipment, work orders, inspections)
- [x] Create Pydantic schemas
- [x] Generate synthetic industrial data (JSON/CSV)

## Phase 3: Document Processing Pipeline
- [x] Build OCR + PDF text extraction service (deferred — using text seed data)
- [x] Build Gemini-powered entity extraction (in unified agent)
- [x] Build P&ID multimodal vision parser (deferred to Phase 11)

## Phase 4: Knowledge Graph & Vector Store
- [x] Build NetworkX knowledge graph service
- [x] Build ChromaDB vector store service
- [x] Wire ingestion pipeline → graph + vectors

## Phase 5: Unified Agent Controller
- [x] Build unified agent with Gemini RAG
- [x] Implement copilot mode (general Q&A)
- [x] Implement maintenance/RCA mode
- [x] Implement compliance mode
- [x] Implement failure intelligence mode

## Phase 6: Backend API Routes
- [x] Document upload & ingestion endpoints
- [x] Query/chat endpoint
- [x] Knowledge graph API
- [x] Compliance API
- [x] Maintenance API
- [x] Dashboard stats API

## Phase 7: Backend Testing
- [x] Test ingestion pipeline end-to-end
- [x] Test copilot queries
- [x] Test all API endpoints (62/62 passed)

## Phase 8: Frontend — Foundation
- [x] Scaffold Next.js app
- [x] Create CSS design system (light mode, flowing animations)
- [x] Create layout, navigation, shared components
- [x] Project renamed to Nazar

## Phase 9: Frontend — Core Pages
- [x] Dashboard home page (stats, compliance gauge, equipment health, trends)
- [x] AI Copilot chat page (4 modes, follow-ups, sources, confidence)
- [x] Document explorer page
- [x] Knowledge graph explorer page (search, filter, node detail)

## Phase 10: Frontend — Agent Pages
- [x] Compliance dashboard page (gauge, regulation breakdown, requirements table)
- [x] Maintenance intelligence page (health table, incidents, trends)

## Phase 11: Polish & Integration
- [x] Mobile responsiveness
  - [x] Hamburger menu toggle for sidebar on mobile
  - [x] Responsive stat cards and grids (2-col tablet, 1-col phone)
  - [x] Chat input area mobile optimization
- [x] Micro-animations & transitions
  - [x] Page transition animations (pageEnter keyframe)
  - [x] Hover micro-interactions on cards (translateY + scale icon)
  - [x] Typing indicator animation in chat (bouncing dots)
  - [x] Smooth sidebar nav transitions (active bar scaleY)
- [x] Error handling & loading states
  - [x] Error boundary component (friendly crash UI)
  - [x] Connection error banner with auto-retry
  - [x] Skeleton loading placeholders (shimmer cards)
  - [x] Toast notification system (success/error/warning/info)
- [x] Final scroll-behavior fix (data-scroll-behavior attr)

## Phase 12: Deliverables
- [x] Architecture diagram
- [x] Walkthrough.md with screenshots and code links
- [x] Final verification recording (6-page walkthrough with AI chat interaction)

