"use client";
import { useEffect, useState } from "react";
import { getKnowledgeGraph, searchGraph, getGraphNode } from "@/lib/api";
import { LoadingSpinner, Badge, EmptyState } from "@/components/UIComponents";

const NODE_COLORS = {
  equipment: "#6366f1",
  work_order: "#f59e0b",
  inspection: "#3b82f6",
  incident: "#ef4444",
  compliance: "#22c55e",
  person: "#8b5cf6",
  area: "#14b8a6",
  regulation: "#ec4899",
  document: "#64748b",
};

const NODE_ICONS = {
  equipment: "⚙️", work_order: "🔧", inspection: "🔍", incident: "⚠️",
  compliance: "📋", person: "👤", area: "📍", regulation: "⚖️", document: "📄",
};

export default function KnowledgePage() {
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodeDetail, setNodeDetail] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [filterType, setFilterType] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getKnowledgeGraph(150);
        setGraphData(data);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    }
    load();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const data = await searchGraph(searchQuery, filterType !== "all" ? filterType : undefined);
      setSearchResults(data.results);
    } catch (err) { console.error(err); }
  };

  const handleNodeClick = async (nodeId) => {
    setSelectedNode(nodeId);
    try {
      const data = await getGraphNode(nodeId);
      setNodeDetail(data);
    } catch (err) { console.error(err); }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <LoadingSpinner size={48} />
      </div>
    );
  }

  const stats = graphData?.stats || {};
  const filteredNodes = graphData?.nodes?.filter(n =>
    filterType === "all" || n.node_type === filterType
  ) || [];

  return (
    <>
      <div className="page-header">
        <h1>Knowledge Graph</h1>
        <p>{stats.total_nodes || 0} entities &middot; {stats.total_edges || 0} relationships</p>
      </div>

      <div className="page-body">
        {/* Search Bar */}
        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", gap: 12 }}>
            <input
              className="input"
              placeholder="Search entities (e.g., pump, V-102, safety)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 12, flexWrap: "wrap" }}>
            {["all", ...Object.keys(NODE_COLORS)].map(t => (
              <button key={t} className={`mode-chip ${filterType === t ? "active" : ""}`}
                onClick={() => setFilterType(t)}>
                {t === "all" ? "🌐 All" : `${NODE_ICONS[t] || ""} ${t}`}
              </button>
            ))}
          </div>
        </div>

        {/* Results / Graph Nodes */}
        <div className="grid-2">
          {/* Node List */}
          <div className="card" style={{ maxHeight: 600, overflowY: "auto" }}>
            <div className="card-header">
              <div className="card-title">
                {searchResults ? `Search Results (${searchResults.length})` : `Entities (${filteredNodes.length})`}
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {(searchResults || filteredNodes).slice(0, 50).map((node) => (
                <div
                  key={node.id}
                  onClick={() => handleNodeClick(node.id)}
                  style={{
                    padding: "10px 14px",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    background: selectedNode === node.id ? "var(--primary-lighter)" : "transparent",
                    transition: "background 0.15s",
                    borderBottom: "1px solid var(--border-light)",
                  }}
                >
                  <span style={{
                    width: 10, height: 10,
                    borderRadius: "50%",
                    background: NODE_COLORS[node.node_type] || "#94a3b8",
                    flexShrink: 0,
                  }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "0.85rem", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {node.label || node.id}
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                      {node.node_type}
                    </div>
                  </div>
                </div>
              ))}
              {(searchResults || filteredNodes).length === 0 && (
                <EmptyState icon="🔍" title="No entities found" message="Try a different search term" />
              )}
            </div>
          </div>

          {/* Node Detail Panel */}
          <div className="card" style={{ maxHeight: 600, overflowY: "auto" }}>
            {nodeDetail ? (
              <div className="animate-fade-in">
                <div className="card-header">
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: "1.5rem" }}>{NODE_ICONS[nodeDetail.node?.node_type] || "📦"}</span>
                    <div>
                      <div className="card-title">{nodeDetail.node?.label || nodeDetail.node?.id}</div>
                      <Badge type="primary">{nodeDetail.node?.node_type}</Badge>
                    </div>
                  </div>
                </div>

                {/* Node Properties */}
                <div style={{ marginBottom: 20 }}>
                  <h4 style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    Properties
                  </h4>
                  {Object.entries(nodeDetail.node || {}).filter(([k]) =>
                    !["id", "node_type", "label"].includes(k)
                  ).map(([key, val]) => (
                    <div key={key} style={{
                      display: "flex", padding: "6px 0",
                      borderBottom: "1px solid var(--border-light)",
                      fontSize: "0.8rem", gap: 12,
                    }}>
                      <span style={{ color: "var(--text-muted)", fontWeight: 500, minWidth: 120 }}>{key}</span>
                      <span style={{ color: "var(--text-primary)", wordBreak: "break-word" }}>
                        {typeof val === "string" ? val : JSON.stringify(val)}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Connections */}
                <h4 style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Connections ({nodeDetail.neighbors?.length || 0})
                </h4>
                {nodeDetail.neighbors?.slice(0, 15).map((nb, i) => (
                  <div key={i}
                    onClick={() => handleNodeClick(nb.id)}
                    style={{
                      padding: "8px 12px",
                      borderRadius: "var(--radius-sm)",
                      cursor: "pointer",
                      display: "flex", alignItems: "center", gap: 8,
                      fontSize: "0.8rem",
                      borderBottom: "1px solid var(--border-light)",
                      transition: "background 0.15s",
                    }}
                  >
                    <span style={{
                      width: 8, height: 8, borderRadius: "50%",
                      background: NODE_COLORS[nb.node_type] || "#94a3b8",
                    }} />
                    <span style={{ fontWeight: 600 }}>{nb.id}</span>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.7rem" }}>
                      {nb.relationship?.relationship || "related"}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState icon="👈" title="Select an entity" message="Click on a node to see its details and connections" />
            )}
          </div>
        </div>

        {/* Graph Stats */}
        <div className="card" style={{ marginTop: 20 }}>
          <div className="card-header">
            <div className="card-title">Graph Statistics</div>
          </div>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            {stats.node_types && Object.entries(stats.node_types).map(([type, count]) => (
              <div key={type} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{
                  width: 12, height: 12, borderRadius: "50%",
                  background: NODE_COLORS[type] || "#94a3b8",
                }} />
                <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>{type}</span>
                <Badge type="neutral">{count}</Badge>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
