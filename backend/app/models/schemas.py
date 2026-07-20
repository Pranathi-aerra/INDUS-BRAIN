"""
Nazar — Pydantic Schemas
Request/Response models for the API layer.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ----- Document Schemas -----

class DocumentUpload(BaseModel):
    title: str
    doc_type: str = "general"  # pid, work_order, inspection, sop, incident, compliance, general

class DocumentResponse(BaseModel):
    id: int
    doc_id: str
    title: str
    doc_type: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    summary: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    status: str
    created_at: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


# ----- Equipment Schemas -----

class EquipmentResponse(BaseModel):
    tag: str
    name: str
    equipment_type: str
    area: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    install_date: Optional[str] = None
    criticality: str = "medium"
    status: str = "operational"
    specifications: Optional[Dict[str, Any]] = None

class EquipmentListResponse(BaseModel):
    equipment: List[EquipmentResponse]
    total: int


# ----- Work Order Schemas -----

class WorkOrderResponse(BaseModel):
    wo_number: str
    equipment_tag: str
    wo_type: str
    priority: str
    status: str
    description: Optional[str] = None
    root_cause: Optional[str] = None
    action_taken: Optional[str] = None
    technician: Optional[str] = None
    reported_date: Optional[str] = None
    completed_date: Optional[str] = None
    downtime_hours: float = 0


# ----- Query / Chat Schemas -----

class QueryRequest(BaseModel):
    query: str
    mode: str = "copilot"  # copilot, maintenance, compliance, failure
    equipment_tag: Optional[str] = None

class SourceCitation(BaseModel):
    doc_id: str
    title: str
    doc_type: str
    relevance_score: float
    excerpt: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=100)
    sources: List[SourceCitation] = []
    follow_up_questions: List[str] = []
    mode: str = "copilot"


# ----- Knowledge Graph Schemas -----

class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # equipment, document, process, failure, regulation, person
    properties: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    properties: Dict[str, Any] = {}

class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: Dict[str, int] = {}


# ----- Compliance Schemas -----

class ComplianceRequirementResponse(BaseModel):
    req_id: str
    regulation: str
    clause: Optional[str] = None
    requirement_text: str
    category: Optional[str] = None
    current_status: str
    gap_description: Optional[str] = None
    last_audit_date: Optional[str] = None
    next_audit_date: Optional[str] = None

class ComplianceDashboardResponse(BaseModel):
    overall_score: float
    by_regulation: Dict[str, Dict[str, Any]]
    gaps: List[ComplianceRequirementResponse]
    upcoming_audits: List[ComplianceRequirementResponse]


# ----- Maintenance Schemas -----

class EquipmentHealthResponse(BaseModel):
    tag: str
    name: str
    status: str
    criticality: str
    mtbf_days: Optional[float] = None
    mttr_hours: Optional[float] = None
    total_failures: int = 0
    last_maintenance: Optional[str] = None
    next_maintenance_due: Optional[str] = None
    failure_trend: List[Dict[str, Any]] = []

class MaintenanceDashboardResponse(BaseModel):
    equipment_health: List[EquipmentHealthResponse]
    total_work_orders: int
    open_work_orders: int
    avg_downtime_hours: float
    top_failing_equipment: List[Dict[str, Any]]
    failure_trends: List[Dict[str, Any]]


# ----- Dashboard Schemas -----

class DashboardStatsResponse(BaseModel):
    total_documents: int = 0
    documents_by_type: Dict[str, int] = {}
    total_equipment: int = 0
    equipment_by_status: Dict[str, int] = {}
    work_orders_by_status: Dict[str, int] = {}
    overdue_inspections: int = 0
    open_incidents: int = 0
    compliance_score: float = 0
    compliance_by_status: Dict[str, int] = {}


# ----- Inspection Schemas -----

class InspectionResponse(BaseModel):
    inspection_id: str
    equipment_tag: Optional[str] = None
    inspection_type: str
    inspector: Optional[str] = None
    inspection_date: Optional[str] = None
    next_due_date: Optional[str] = None
    status: str
    findings: Optional[str] = None
    severity: str
    regulatory_ref: Optional[str] = None


# ----- Incident Schemas -----

class IncidentResponse(BaseModel):
    incident_id: str
    incident_type: str
    severity: str
    date_occurred: Optional[str] = None
    area: Optional[str] = None
    equipment_tag: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    lessons_learned: Optional[str] = None
    status: str
