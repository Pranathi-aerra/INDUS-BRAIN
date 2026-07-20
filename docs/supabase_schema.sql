-- ============================================
-- NAZAR — Supabase Database Schema
-- AI for Industrial Knowledge Intelligence
-- Run this in Supabase SQL Editor
-- ============================================

-- 1. Equipment Table
CREATE TABLE IF NOT EXISTS equipment (
    id BIGSERIAL PRIMARY KEY,
    tag TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    area TEXT,
    manufacturer TEXT,
    model TEXT,
    install_date DATE,
    criticality TEXT DEFAULT 'medium' CHECK (criticality IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'operational' CHECK (status IN ('operational', 'degraded', 'failed', 'under_maintenance', 'decommissioned')),
    specifications JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Work Orders Table
CREATE TABLE IF NOT EXISTS work_orders (
    id BIGSERIAL PRIMARY KEY,
    wo_number TEXT UNIQUE NOT NULL,
    equipment_tag TEXT REFERENCES equipment(tag) ON DELETE SET NULL,
    wo_type TEXT NOT NULL CHECK (wo_type IN ('preventive', 'corrective', 'emergency', 'inspection', 'modification')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled', 'deferred')),
    description TEXT,
    assigned_to TEXT,
    created_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    completed_date DATE,
    downtime_hours REAL DEFAULT 0,
    root_cause TEXT,
    corrective_action TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Inspections Table
CREATE TABLE IF NOT EXISTS inspections (
    id BIGSERIAL PRIMARY KEY,
    inspection_id TEXT UNIQUE NOT NULL,
    equipment_tag TEXT REFERENCES equipment(tag) ON DELETE SET NULL,
    inspection_type TEXT NOT NULL CHECK (inspection_type IN ('routine', 'statutory', 'regulatory', 'special', 'pre_startup')),
    inspector TEXT,
    inspection_date DATE NOT NULL,
    next_due_date DATE,
    status TEXT DEFAULT 'completed' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'overdue', 'cancelled')),
    findings TEXT,
    severity TEXT DEFAULT 'none' CHECK (severity IN ('none', 'minor', 'major', 'critical')),
    regulatory_ref TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Incidents Table
CREATE TABLE IF NOT EXISTS incidents (
    id BIGSERIAL PRIMARY KEY,
    incident_id TEXT UNIQUE NOT NULL,
    equipment_tag TEXT REFERENCES equipment(tag) ON DELETE SET NULL,
    incident_type TEXT NOT NULL CHECK (incident_type IN ('near_miss', 'unsafe_condition', 'injury', 'environmental', 'process_upset', 'fire', 'explosion')),
    severity TEXT DEFAULT 'low' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    incident_date DATE NOT NULL,
    area TEXT,
    description TEXT NOT NULL,
    root_cause TEXT,
    corrective_action TEXT,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'closed')),
    reported_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Compliance Requirements Table
CREATE TABLE IF NOT EXISTS compliance_requirements (
    id BIGSERIAL PRIMARY KEY,
    req_id TEXT UNIQUE NOT NULL,
    regulation TEXT NOT NULL,
    clause TEXT NOT NULL,
    requirement_text TEXT NOT NULL,
    applicable_to TEXT,
    current_status TEXT DEFAULT 'compliant' CHECK (current_status IN ('compliant', 'partially_compliant', 'non_compliant', 'not_assessed')),
    evidence_doc TEXT,
    last_audit_date DATE,
    next_audit_date DATE,
    gap_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    doc_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL CHECK (doc_type IN ('sop', 'pid', 'inspection_report', 'work_order', 'compliance', 'manual', 'other')),
    content TEXT,
    status TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(equipment_type);
CREATE INDEX IF NOT EXISTS idx_equipment_area ON equipment(area);
CREATE INDEX IF NOT EXISTS idx_equipment_criticality ON equipment(criticality);

CREATE INDEX IF NOT EXISTS idx_wo_equipment ON work_orders(equipment_tag);
CREATE INDEX IF NOT EXISTS idx_wo_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_wo_type ON work_orders(wo_type);
CREATE INDEX IF NOT EXISTS idx_wo_created ON work_orders(created_date);

CREATE INDEX IF NOT EXISTS idx_insp_equipment ON inspections(equipment_tag);
CREATE INDEX IF NOT EXISTS idx_insp_status ON inspections(status);
CREATE INDEX IF NOT EXISTS idx_insp_due ON inspections(next_due_date);

CREATE INDEX IF NOT EXISTS idx_inc_equipment ON incidents(equipment_tag);
CREATE INDEX IF NOT EXISTS idx_inc_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_inc_date ON incidents(incident_date);

CREATE INDEX IF NOT EXISTS idx_comp_regulation ON compliance_requirements(regulation);
CREATE INDEX IF NOT EXISTS idx_comp_status ON compliance_requirements(current_status);

CREATE INDEX IF NOT EXISTS idx_doc_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_doc_status ON documents(status);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
ALTER TABLE equipment ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspections ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read on equipment" ON equipment FOR SELECT USING (true);
CREATE POLICY "Allow public read on work_orders" ON work_orders FOR SELECT USING (true);
CREATE POLICY "Allow public read on inspections" ON inspections FOR SELECT USING (true);
CREATE POLICY "Allow public read on incidents" ON incidents FOR SELECT USING (true);
CREATE POLICY "Allow public read on compliance_requirements" ON compliance_requirements FOR SELECT USING (true);
CREATE POLICY "Allow public read on documents" ON documents FOR SELECT USING (true);

CREATE POLICY "Allow service insert on equipment" ON equipment FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service insert on work_orders" ON work_orders FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service insert on inspections" ON inspections FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service insert on incidents" ON incidents FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service insert on compliance_requirements" ON compliance_requirements FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service insert on documents" ON documents FOR INSERT WITH CHECK (true);

-- ============================================
-- AUTO-UPDATE TRIGGER
-- ============================================
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_equipment_modtime
    BEFORE UPDATE ON equipment
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_documents_modtime
    BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
