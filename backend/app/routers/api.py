"""
Nazar — API Routers
All REST API endpoints.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
import json
import uuid

from app.models.schemas import (
    QueryRequest, QueryResponse, DashboardStatsResponse,
    KnowledgeGraphResponse, ComplianceDashboardResponse,
    MaintenanceDashboardResponse, DocumentListResponse,
)
from app.agents.unified_agent import query_agent
from app.services.knowledge_graph import knowledge_graph
from app.services.vector_store import vector_store
from app.services import database as db

# ============================================================
# Router instances
# ============================================================
query_router = APIRouter(prefix="/api/query", tags=["Query"])
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
documents_router = APIRouter(prefix="/api/documents", tags=["Documents"])
knowledge_router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Graph"])
compliance_router = APIRouter(prefix="/api/compliance", tags=["Compliance"])
maintenance_router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])
equipment_router = APIRouter(prefix="/api/equipment", tags=["Equipment"])


# ============================================================
# QUERY / CHAT ENDPOINTS
# ============================================================

@query_router.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """Main chat endpoint — routes to the unified agent."""
    result = await query_agent(
        query=request.query,
        mode=request.mode,
        equipment_tag=request.equipment_tag,
    )
    return QueryResponse(**result)


# ============================================================
# DASHBOARD ENDPOINTS
# ============================================================

@dashboard_router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats():
    """Get aggregate dashboard statistics."""
    stats = await db.get_dashboard_stats()
    
    # Add knowledge graph stats
    if knowledge_graph.is_initialized():
        kg_stats = knowledge_graph.get_stats()
        stats["kg_nodes"] = kg_stats["total_nodes"]
        stats["kg_edges"] = kg_stats["total_edges"]
    
    # Add vector store stats
    vs_stats = vector_store.get_stats()
    stats["vector_chunks"] = vs_stats["total_chunks"]
    
    return DashboardStatsResponse(**stats)


# ============================================================
# DOCUMENT ENDPOINTS
# ============================================================

@documents_router.get("/list")
async def list_documents(doc_type: Optional[str] = None, limit: int = 100):
    """List all documents, optionally filtered by type."""
    docs = await db.get_all_documents(doc_type=doc_type, limit=limit)
    return {"documents": docs, "total": len(docs)}


@documents_router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(""),
    doc_type: str = Form("general"),
):
    """Upload a document for processing."""
    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    content = await file.read()
    content_text = content.decode("utf-8", errors="replace")
    
    doc = {
        "doc_id": doc_id,
        "title": title or file.filename,
        "doc_type": doc_type,
        "file_name": file.filename,
        "file_size": len(content),
        "mime_type": file.content_type,
        "content_text": content_text[:50000],  # Limit text storage
        "status": "completed",
    }
    
    await db.insert_document(doc)
    
    # Index in vector store
    vector_store.add_document(
        doc_id, content_text,
        {"title": doc["title"], "doc_type": doc_type}
    )
    
    return {"doc_id": doc_id, "status": "completed", "message": "Document uploaded and indexed."}


# ============================================================
# KNOWLEDGE GRAPH ENDPOINTS
# ============================================================

@knowledge_router.get("/graph")
async def get_full_graph(max_nodes: int = 200):
    """Get the full knowledge graph for visualization."""
    if not knowledge_graph.is_initialized():
        return {"nodes": [], "edges": [], "stats": {}}
    
    graph_data = knowledge_graph.get_full_graph(max_nodes=max_nodes)
    stats = knowledge_graph.get_stats()
    return {**graph_data, "stats": stats}


@knowledge_router.get("/node/{node_id}")
async def get_node(node_id: str):
    """Get a specific node and its connections."""
    node = knowledge_graph.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    
    neighbors = knowledge_graph.get_neighbors(node_id)
    return {"node": node, "neighbors": neighbors}


@knowledge_router.get("/subgraph/{center_node}")
async def get_subgraph(center_node: str, depth: int = 2):
    """Get a subgraph centered on a node."""
    return knowledge_graph.get_subgraph(center_node, depth=depth)


@knowledge_router.get("/search")
async def search_graph(q: str, node_type: Optional[str] = None):
    """Search the knowledge graph."""
    results = knowledge_graph.search_nodes(q, node_type=node_type)
    return {"results": results[:20], "total": len(results)}


# ============================================================
# EQUIPMENT ENDPOINTS
# ============================================================

@equipment_router.get("/list")
async def list_equipment(eq_type: Optional[str] = None):
    """List all equipment."""
    equipment = await db.get_all_equipment(eq_type=eq_type)
    return {"equipment": equipment, "total": len(equipment)}


@equipment_router.get("/{tag}")
async def get_equipment(tag: str):
    """Get equipment details by tag."""
    eq = await db.get_equipment_by_tag(tag)
    if not eq:
        raise HTTPException(status_code=404, detail=f"Equipment '{tag}' not found")
    
    # Get related work orders
    work_orders = await db.get_work_orders(equipment_tag=tag)
    inspections = await db.get_inspections(equipment_tag=tag)
    
    # Get KG connections
    kg_neighbors = []
    if knowledge_graph.is_initialized():
        kg_neighbors = knowledge_graph.get_neighbors(tag)
    
    return {
        "equipment": eq,
        "work_orders": work_orders,
        "inspections": inspections,
        "graph_connections": kg_neighbors[:20],
    }


# ============================================================
# COMPLIANCE ENDPOINTS
# ============================================================

@compliance_router.get("/dashboard")
async def get_compliance_dashboard():
    """Get compliance dashboard data."""
    all_reqs = await db.get_compliance_requirements()
    
    # Organize by regulation
    by_regulation = {}
    gaps = []
    upcoming = []
    
    for req in all_reqs:
        reg = req["regulation"]
        if reg not in by_regulation:
            by_regulation[reg] = {"total": 0, "compliant": 0, "non_compliant": 0, "partial": 0, "unknown": 0}
        by_regulation[reg]["total"] += 1
        status = req.get("current_status", "unknown")
        by_regulation[reg][status] = by_regulation[reg].get(status, 0) + 1
        
        if status in ("non_compliant", "partial"):
            gaps.append(req)
        
        if req.get("next_audit_date"):
            upcoming.append(req)
    
    # Calculate scores per regulation
    for reg, counts in by_regulation.items():
        total = counts["total"]
        compliant = counts.get("compliant", 0)
        counts["score"] = round((compliant / total * 100) if total > 0 else 0, 1)
    
    # Overall score
    total_reqs = len(all_reqs)
    total_compliant = sum(1 for r in all_reqs if r.get("current_status") == "compliant")
    overall_score = round((total_compliant / total_reqs * 100) if total_reqs > 0 else 0, 1)
    
    # Sort upcoming by date
    upcoming.sort(key=lambda x: x.get("next_audit_date", "9999"))
    
    return {
        "overall_score": overall_score,
        "total_requirements": total_reqs,
        "by_regulation": by_regulation,
        "gaps": gaps,
        "upcoming_audits": upcoming[:10],
    }


@compliance_router.get("/requirements")
async def get_compliance_requirements(
    regulation: Optional[str] = None,
    status: Optional[str] = None,
):
    """Get compliance requirements, optionally filtered."""
    reqs = await db.get_compliance_requirements(regulation=regulation, status=status)
    return {"requirements": reqs, "total": len(reqs)}


# ============================================================
# MAINTENANCE ENDPOINTS
# ============================================================

@maintenance_router.get("/dashboard")
async def get_maintenance_dashboard():
    """Get maintenance intelligence dashboard data."""
    all_equipment = await db.get_all_equipment()
    all_work_orders = await db.get_work_orders(limit=500)
    
    # Calculate per-equipment health
    equipment_health = []
    wo_by_tag = {}
    for wo in all_work_orders:
        tag = wo["equipment_tag"]
        if tag not in wo_by_tag:
            wo_by_tag[tag] = []
        wo_by_tag[tag].append(wo)
    
    for eq in all_equipment:
        tag = eq["tag"]
        eq_wos = wo_by_tag.get(tag, [])
        completed_wos = [w for w in eq_wos if w["status"] == "completed"]
        
        # Calculate MTBF (days between failures)
        failure_dates = sorted([
            w["reported_date"] for w in completed_wos 
            if w.get("wo_type") in ("corrective", "emergency") and w.get("reported_date")
        ])
        
        mtbf = None
        if len(failure_dates) >= 2:
            from datetime import datetime
            intervals = []
            for i in range(1, len(failure_dates)):
                try:
                    d1 = datetime.strptime(failure_dates[i-1], "%Y-%m-%d")
                    d2 = datetime.strptime(failure_dates[i], "%Y-%m-%d")
                    intervals.append((d2 - d1).days)
                except ValueError:
                    pass
            if intervals:
                mtbf = round(sum(intervals) / len(intervals), 1)
        
        # Calculate MTTR (average downtime hours)
        downtimes = [w.get("downtime_hours", 0) for w in completed_wos if w.get("downtime_hours", 0) > 0]
        mttr = round(sum(downtimes) / len(downtimes), 1) if downtimes else None
        
        total_failures = len([w for w in eq_wos if w.get("wo_type") in ("corrective", "emergency")])
        
        last_maintenance = max(
            (w.get("completed_date", "") for w in completed_wos), default=None
        )
        
        equipment_health.append({
            "tag": tag,
            "name": eq["name"],
            "equipment_type": eq["equipment_type"],
            "status": eq["status"],
            "criticality": eq.get("criticality", "medium"),
            "mtbf_days": mtbf,
            "mttr_hours": mttr,
            "total_failures": total_failures,
            "total_work_orders": len(eq_wos),
            "last_maintenance": last_maintenance,
        })
    
    # Sort by failure count (most problematic first)
    equipment_health.sort(key=lambda x: x["total_failures"], reverse=True)
    
    # Summary stats
    open_wos = len([w for w in all_work_orders if w["status"] in ("open", "in_progress")])
    all_downtimes = [w.get("downtime_hours", 0) for w in all_work_orders if w.get("downtime_hours", 0) > 0]
    avg_downtime = round(sum(all_downtimes) / len(all_downtimes), 1) if all_downtimes else 0
    
    # Top failing equipment
    top_failing = [e for e in equipment_health if e["total_failures"] > 0][:5]
    
    # Failure trends by month
    from collections import Counter
    monthly_failures = Counter()
    for wo in all_work_orders:
        if wo.get("wo_type") in ("corrective", "emergency") and wo.get("reported_date"):
            month = wo["reported_date"][:7]  # YYYY-MM
            monthly_failures[month] += 1
    
    failure_trends = [{"month": m, "count": c} for m, c in sorted(monthly_failures.items())]
    
    return {
        "equipment_health": equipment_health,
        "total_work_orders": len(all_work_orders),
        "open_work_orders": open_wos,
        "avg_downtime_hours": avg_downtime,
        "top_failing_equipment": top_failing,
        "failure_trends": failure_trends,
    }


@maintenance_router.get("/work-orders")
async def get_work_orders(
    equipment_tag: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
):
    """Get work orders, optionally filtered."""
    wos = await db.get_work_orders(equipment_tag=equipment_tag, status=status, limit=limit)
    return {"work_orders": wos, "total": len(wos)}


@maintenance_router.get("/inspections")
async def get_inspections(
    equipment_tag: Optional[str] = None,
    status: Optional[str] = None,
):
    """Get inspection records."""
    insps = await db.get_inspections(equipment_tag=equipment_tag, status=status)
    return {"inspections": insps, "total": len(insps)}


@maintenance_router.get("/incidents")
async def get_incidents(
    severity: Optional[str] = None,
    status: Optional[str] = None,
):
    """Get incident records."""
    incs = await db.get_incidents(severity=severity, status=status)
    return {"incidents": incs, "total": len(incs)}
