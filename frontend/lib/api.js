/**
 * Nazar — API Client
 * Handles all communication with the FastAPI backend.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  };

  const res = await fetch(url, config);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

// Dashboard
export const getDashboardStats = () => request("/api/dashboard/stats");

// Equipment
export const getEquipmentList = (type) =>
  request(`/api/equipment/list${type ? `?eq_type=${type}` : ""}`);
export const getEquipment = (tag) => request(`/api/equipment/${tag}`);

// Chat / Query
export const sendQuery = (query, mode = "copilot", equipmentTag = null) =>
  request("/api/query/chat", {
    method: "POST",
    body: JSON.stringify({ query, mode, equipment_tag: equipmentTag }),
  });

// Knowledge Graph
export const getKnowledgeGraph = (maxNodes = 200) =>
  request(`/api/knowledge/graph?max_nodes=${maxNodes}`);
export const getGraphNode = (nodeId) => request(`/api/knowledge/node/${nodeId}`);
export const getSubgraph = (nodeId, depth = 2) =>
  request(`/api/knowledge/subgraph/${nodeId}?depth=${depth}`);
export const searchGraph = (q, nodeType) =>
  request(`/api/knowledge/search?q=${q}${nodeType ? `&node_type=${nodeType}` : ""}`);

// Compliance
export const getComplianceDashboard = () => request("/api/compliance/dashboard");
export const getComplianceRequirements = (regulation, status) => {
  const params = new URLSearchParams();
  if (regulation) params.set("regulation", regulation);
  if (status) params.set("status", status);
  return request(`/api/compliance/requirements?${params}`);
};

// Maintenance
export const getMaintenanceDashboard = () => request("/api/maintenance/dashboard");
export const getWorkOrders = (equipmentTag, status, limit = 100) => {
  const params = new URLSearchParams();
  if (equipmentTag) params.set("equipment_tag", equipmentTag);
  if (status) params.set("status", status);
  params.set("limit", limit);
  return request(`/api/maintenance/work-orders?${params}`);
};
export const getInspections = (equipmentTag, status) => {
  const params = new URLSearchParams();
  if (equipmentTag) params.set("equipment_tag", equipmentTag);
  if (status) params.set("status", status);
  return request(`/api/maintenance/inspections?${params}`);
};
export const getIncidents = (severity, status) => {
  const params = new URLSearchParams();
  if (severity) params.set("severity", severity);
  if (status) params.set("status", status);
  return request(`/api/maintenance/incidents?${params}`);
};

// Documents
export const getDocuments = (docType) =>
  request(`/api/documents/list${docType ? `?doc_type=${docType}` : ""}`);

// Health
export const getHealth = () => request("/api/health");
