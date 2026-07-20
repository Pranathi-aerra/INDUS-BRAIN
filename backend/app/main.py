"""
Nazar — AI for Industrial Knowledge Intelligence
FastAPI entry point. Initializes DB, seeds data, starts the server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.services import database as db
from app.services.knowledge_graph import knowledge_graph
from app.services.vector_store import vector_store
from app.services.supabase_db import is_connected as supabase_connected, sync_all_to_cloud
from app.seed_data import generate_all_seed_data
from app.config import GEMINI_API_KEY
from app.routers.api import (
    query_router, dashboard_router, documents_router,
    knowledge_router, compliance_router, maintenance_router,
    equipment_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    print("=" * 60)
    print("  Nazar — Starting Up")
    print("=" * 60)

    # Validate env
    if not GEMINI_API_KEY:
        print("[WARN] GEMINI_API_KEY not set in .env — AI features will be limited")

    # 1. Initialize database
    await db.init_db()

    # 2. Generate and seed data
    seed_data = generate_all_seed_data()

    for eq in seed_data["equipment"]:
        await db.insert_equipment(eq)
    print(f"[Seed] Loaded {len(seed_data['equipment'])} equipment records")

    for wo in seed_data["work_orders"]:
        await db.insert_work_order(wo)
    print(f"[Seed] Loaded {len(seed_data['work_orders'])} work orders")

    for insp in seed_data["inspections"]:
        await db.insert_inspection(insp)
    print(f"[Seed] Loaded {len(seed_data['inspections'])} inspections")

    for inc in seed_data["incidents"]:
        await db.insert_incident(inc)
    print(f"[Seed] Loaded {len(seed_data['incidents'])} incidents")

    for req in seed_data["compliance_requirements"]:
        await db.insert_compliance_req(req)
    print(f"[Seed] Loaded {len(seed_data['compliance_requirements'])} compliance requirements")

    for sop in seed_data["sops"]:
        await db.insert_document({
            "doc_id": sop["doc_id"],
            "title": sop["title"],
            "doc_type": sop["doc_type"],
            "content_text": sop["content_text"],
            "status": "completed",
        })
    print(f"[Seed] Loaded {len(seed_data['sops'])} SOP documents")

    # 3. Build knowledge graph
    knowledge_graph.build_from_seed_data(seed_data)

    # 4. Seed vector store
    vector_store.seed_from_data(seed_data)

    # 5. Supabase cloud sync (optional)
    if supabase_connected():
        result = sync_all_to_cloud(seed_data)
        print(f"[Supabase] Cloud sync: {result}")
    else:
        print("[Supabase] Not configured — running in local-only mode")

    print("=" * 60)
    print("  Nazar — Ready!")
    print("  API: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("=" * 60)

    yield

    print("[Shutdown] Nazar shutting down.")


# Create FastAPI app
app = FastAPI(
    title="Nazar",
    description="AI for Industrial Knowledge Intelligence — Unified Asset & Operations Brain",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(query_router)
app.include_router(dashboard_router)
app.include_router(documents_router)
app.include_router(knowledge_router)
app.include_router(compliance_router)
app.include_router(maintenance_router)
app.include_router(equipment_router)


@app.get("/")
async def root():
    return {
        "name": "Nazar",
        "version": "1.0.0",
        "description": "AI for Industrial Knowledge Intelligence — Unified Asset & Operations Brain",
        "status": "running",
        "supabase": "connected" if supabase_connected() else "local_only",
    }


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    kg_stats = knowledge_graph.get_stats() if knowledge_graph.is_initialized() else {}
    vs_stats = vector_store.get_stats()
    return {
        "status": "healthy",
        "knowledge_graph": kg_stats,
        "vector_store": vs_stats,
        "supabase": "connected" if supabase_connected() else "not_configured",
    }
