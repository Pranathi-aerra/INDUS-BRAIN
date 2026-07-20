"""
Nazar — Database Service
SQLite database with async support via aiosqlite.
Manages all structured data: documents, equipment, work orders, inspections, incidents.
"""
import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from app.config import DB_PATH


async def get_db():
    """Get database connection."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
        print(f"[DB] Database initialized at {DB_PATH}")


SCHEMA_SQL = """
-- Documents table: tracks every ingested document
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL,  -- pid, work_order, inspection, sop, incident, compliance, general
    file_path TEXT,
    file_name TEXT,
    file_size INTEGER,
    mime_type TEXT,
    content_text TEXT,       -- extracted full text
    summary TEXT,            -- AI-generated summary
    entities_json TEXT,      -- extracted entities as JSON
    status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Equipment registry: all plant assets
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT UNIQUE NOT NULL,         -- e.g., P-201-A, V-101, HX-301
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,     -- pump, vessel, heat_exchanger, valve, instrument
    area TEXT,                        -- plant area/unit
    manufacturer TEXT,
    model TEXT,
    install_date TEXT,
    criticality TEXT DEFAULT 'medium',  -- low, medium, high, critical
    status TEXT DEFAULT 'operational',  -- operational, degraded, failed, decommissioned
    specifications_json TEXT,
    parent_tag TEXT,                    -- for parent-child equipment hierarchy
    created_at TEXT DEFAULT (datetime('now'))
);

-- Work orders: maintenance records
CREATE TABLE IF NOT EXISTS work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wo_number TEXT UNIQUE NOT NULL,
    equipment_tag TEXT NOT NULL,
    wo_type TEXT NOT NULL,          -- preventive, corrective, emergency, inspection
    priority TEXT DEFAULT 'medium', -- low, medium, high, critical
    status TEXT DEFAULT 'open',     -- open, in_progress, completed, cancelled
    description TEXT,
    root_cause TEXT,
    action_taken TEXT,
    technician TEXT,
    reported_date TEXT,
    completed_date TEXT,
    downtime_hours REAL DEFAULT 0,
    parts_used TEXT,               -- JSON array of parts
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (equipment_tag) REFERENCES equipment(tag)
);

-- Inspection records
CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id TEXT UNIQUE NOT NULL,
    equipment_tag TEXT,
    inspection_type TEXT NOT NULL,  -- safety, regulatory, routine, special
    inspector TEXT,
    inspection_date TEXT,
    next_due_date TEXT,
    status TEXT DEFAULT 'completed', -- scheduled, completed, overdue
    findings TEXT,
    severity TEXT DEFAULT 'none',    -- none, minor, major, critical
    corrective_actions TEXT,
    regulatory_ref TEXT,             -- e.g., OISD-118, Factory Act Section 36
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (equipment_tag) REFERENCES equipment(tag)
);

-- Incident / near-miss reports
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT UNIQUE NOT NULL,
    incident_type TEXT NOT NULL,    -- incident, near_miss, unsafe_condition
    severity TEXT DEFAULT 'low',    -- low, medium, high, critical
    date_occurred TEXT,
    area TEXT,
    equipment_tag TEXT,
    description TEXT,
    root_cause TEXT,
    corrective_actions TEXT,
    lessons_learned TEXT,
    reported_by TEXT,
    status TEXT DEFAULT 'open',     -- open, investigating, closed
    created_at TEXT DEFAULT (datetime('now'))
);

-- Compliance requirements mapping
CREATE TABLE IF NOT EXISTS compliance_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    req_id TEXT UNIQUE NOT NULL,
    regulation TEXT NOT NULL,       -- Factory Act, OISD-118, PESO, BIS
    clause TEXT,
    requirement_text TEXT NOT NULL,
    category TEXT,                  -- fire_protection, electrical, pressure_vessel, etc.
    applicable_equipment TEXT,      -- JSON array of equipment types
    current_status TEXT DEFAULT 'unknown', -- compliant, non_compliant, partial, unknown
    evidence_doc_ids TEXT,          -- JSON array of document IDs providing evidence
    last_audit_date TEXT,
    next_audit_date TEXT,
    gap_description TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Processing queue for document ingestion
CREATE TABLE IF NOT EXISTS processing_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT NOT NULL,
    status TEXT DEFAULT 'queued',  -- queued, processing, completed, failed
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_equipment_tag ON equipment(tag);
CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(equipment_type);
CREATE INDEX IF NOT EXISTS idx_work_orders_equipment ON work_orders(equipment_tag);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_inspections_equipment ON inspections(equipment_tag);
CREATE INDEX IF NOT EXISTS idx_inspections_status ON inspections(status);
CREATE INDEX IF NOT EXISTS idx_incidents_equipment ON incidents(equipment_tag);
CREATE INDEX IF NOT EXISTS idx_compliance_regulation ON compliance_requirements(regulation);
CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_requirements(current_status);
"""


# ----- CRUD Operations -----

async def insert_document(doc: dict) -> int:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """INSERT OR REPLACE INTO documents 
               (doc_id, title, doc_type, file_path, file_name, file_size, mime_type, 
                content_text, summary, entities_json, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (doc["doc_id"], doc["title"], doc["doc_type"], doc.get("file_path"),
             doc.get("file_name"), doc.get("file_size"), doc.get("mime_type"),
             doc.get("content_text"), doc.get("summary"),
             json.dumps(doc.get("entities", {})), doc.get("status", "completed"))
        )
        await db.commit()
        return cursor.lastrowid


async def insert_equipment(eq: dict) -> int:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """INSERT OR REPLACE INTO equipment 
               (tag, name, equipment_type, area, manufacturer, model, install_date,
                criticality, status, specifications_json, parent_tag)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (eq["tag"], eq["name"], eq["equipment_type"], eq.get("area"),
             eq.get("manufacturer"), eq.get("model"), eq.get("install_date"),
             eq.get("criticality", "medium"), eq.get("status", "operational"),
             json.dumps(eq.get("specifications", {})), eq.get("parent_tag"))
        )
        await db.commit()
        return cursor.lastrowid


async def insert_work_order(wo: dict) -> int:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """INSERT OR REPLACE INTO work_orders 
               (wo_number, equipment_tag, wo_type, priority, status, description,
                root_cause, action_taken, technician, reported_date, completed_date,
                downtime_hours, parts_used)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (wo["wo_number"], wo["equipment_tag"], wo["wo_type"],
             wo.get("priority", "medium"), wo.get("status", "completed"),
             wo.get("description"), wo.get("root_cause"), wo.get("action_taken"),
             wo.get("technician"), wo.get("reported_date"), wo.get("completed_date"),
             wo.get("downtime_hours", 0), json.dumps(wo.get("parts_used", [])))
        )
        await db.commit()
        return cursor.lastrowid


async def insert_inspection(insp: dict) -> int:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """INSERT OR REPLACE INTO inspections 
               (inspection_id, equipment_tag, inspection_type, inspector, 
                inspection_date, next_due_date, status, findings, severity,
                corrective_actions, regulatory_ref)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (insp["inspection_id"], insp.get("equipment_tag"), insp["inspection_type"],
             insp.get("inspector"), insp.get("inspection_date"), insp.get("next_due_date"),
             insp.get("status", "completed"), insp.get("findings"),
             insp.get("severity", "none"), insp.get("corrective_actions"),
             insp.get("regulatory_ref"))
        )
        await db.commit()
        return cursor.lastrowid


async def insert_incident(inc: dict) -> int:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """INSERT OR REPLACE INTO incidents 
               (incident_id, incident_type, severity, date_occurred, area,
                equipment_tag, description, root_cause, corrective_actions,
                lessons_learned, reported_by, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (inc["incident_id"], inc["incident_type"], inc.get("severity", "low"),
             inc.get("date_occurred"), inc.get("area"), inc.get("equipment_tag"),
             inc.get("description"), inc.get("root_cause"),
             inc.get("corrective_actions"), inc.get("lessons_learned"),
             inc.get("reported_by"), inc.get("status", "open"))
        )
        await db.commit()
        return cursor.lastrowid


async def insert_compliance_req(req: dict) -> int:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """INSERT OR REPLACE INTO compliance_requirements 
               (req_id, regulation, clause, requirement_text, category,
                applicable_equipment, current_status, evidence_doc_ids,
                last_audit_date, next_audit_date, gap_description)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (req["req_id"], req["regulation"], req.get("clause"),
             req["requirement_text"], req.get("category"),
             json.dumps(req.get("applicable_equipment", [])),
             req.get("current_status", "unknown"),
             json.dumps(req.get("evidence_doc_ids", [])),
             req.get("last_audit_date"), req.get("next_audit_date"),
             req.get("gap_description"))
        )
        await db.commit()
        return cursor.lastrowid


# ----- Query Operations -----

async def get_all_documents(doc_type: str = None, limit: int = 100):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        if doc_type:
            cursor = await db.execute(
                "SELECT * FROM documents WHERE doc_type = ? ORDER BY created_at DESC LIMIT ?",
                (doc_type, limit))
        else:
            cursor = await db.execute(
                "SELECT * FROM documents ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_all_equipment(eq_type: str = None):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        if eq_type:
            cursor = await db.execute(
                "SELECT * FROM equipment WHERE equipment_type = ? ORDER BY tag", (eq_type,))
        else:
            cursor = await db.execute("SELECT * FROM equipment ORDER BY tag")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_equipment_by_tag(tag: str):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM equipment WHERE tag = ?", (tag,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_work_orders(equipment_tag: str = None, status: str = None, limit: int = 100):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM work_orders WHERE 1=1"
        params = []
        if equipment_tag:
            query += " AND equipment_tag = ?"
            params.append(equipment_tag)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY reported_date DESC LIMIT ?"
        params.append(limit)
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_inspections(equipment_tag: str = None, status: str = None):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM inspections WHERE 1=1"
        params = []
        if equipment_tag:
            query += " AND equipment_tag = ?"
            params.append(equipment_tag)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY inspection_date DESC"
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_incidents(severity: str = None, status: str = None):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY date_occurred DESC"
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_compliance_requirements(regulation: str = None, status: str = None):
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM compliance_requirements WHERE 1=1"
        params = []
        if regulation:
            query += " AND regulation = ?"
            params.append(regulation)
        if status:
            query += " AND current_status = ?"
            params.append(status)
        query += " ORDER BY regulation, clause"
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_dashboard_stats():
    """Get aggregate statistics for the dashboard."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        stats = {}
        
        # Document counts by type
        cursor = await db.execute(
            "SELECT doc_type, COUNT(*) as count FROM documents GROUP BY doc_type")
        rows = await cursor.fetchall()
        stats["documents_by_type"] = {r[0]: r[1] for r in rows}
        stats["total_documents"] = sum(stats["documents_by_type"].values())
        
        # Equipment counts
        cursor = await db.execute(
            "SELECT status, COUNT(*) as count FROM equipment GROUP BY status")
        rows = await cursor.fetchall()
        stats["equipment_by_status"] = {r[0]: r[1] for r in rows}
        stats["total_equipment"] = sum(stats["equipment_by_status"].values())
        
        # Work order stats
        cursor = await db.execute(
            "SELECT status, COUNT(*) as count FROM work_orders GROUP BY status")
        rows = await cursor.fetchall()
        stats["work_orders_by_status"] = {r[0]: r[1] for r in rows}
        
        # Overdue inspections
        cursor = await db.execute(
            """SELECT COUNT(*) FROM inspections 
               WHERE next_due_date < datetime('now') AND status != 'completed'""")
        row = await cursor.fetchone()
        stats["overdue_inspections"] = row[0] if row else 0
        
        # Open incidents
        cursor = await db.execute(
            "SELECT COUNT(*) FROM incidents WHERE status != 'closed'")
        row = await cursor.fetchone()
        stats["open_incidents"] = row[0] if row else 0
        
        # Compliance summary
        cursor = await db.execute(
            "SELECT current_status, COUNT(*) as count FROM compliance_requirements GROUP BY current_status")
        rows = await cursor.fetchall()
        stats["compliance_by_status"] = {r[0]: r[1] for r in rows}
        total_reqs = sum(stats["compliance_by_status"].values())
        compliant = stats["compliance_by_status"].get("compliant", 0)
        stats["compliance_score"] = round((compliant / total_reqs * 100) if total_reqs > 0 else 0, 1)
        
        return stats
