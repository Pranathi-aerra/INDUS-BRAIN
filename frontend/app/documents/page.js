"use client";
import { useEffect, useState } from "react";
import { getDocuments } from "@/lib/api";
import { LoadingSpinner, Badge, EmptyState } from "@/components/UIComponents";

const DOC_ICONS = {
  sop: "📘", work_order: "🔧", inspection: "🔍",
  incident: "⚠️", compliance: "📋", general: "📄",
};

export default function DocumentsPage() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    async function load() {
      try {
        const data = await getDocuments();
        setDocs(data.documents || []);
      } catch (err) { console.error(err); }
      finally { setLoading(false); }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <LoadingSpinner size={48} />
      </div>
    );
  }

  const filtered = filter === "all" ? docs : docs.filter(d => d.doc_type === filter);
  const types = [...new Set(docs.map(d => d.doc_type))];

  return (
    <>
      <div className="page-header">
        <h1>Document Repository</h1>
        <p>{docs.length} documents indexed in the knowledge base</p>
      </div>

      <div className="page-body">
        {/* Filters */}
        <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
          <button className={`mode-chip ${filter === "all" ? "active" : ""}`}
            onClick={() => setFilter("all")}>
            All ({docs.length})
          </button>
          {types.map(t => (
            <button key={t} className={`mode-chip ${filter === t ? "active" : ""}`}
              onClick={() => setFilter(t)}>
              {DOC_ICONS[t] || "📄"} {t} ({docs.filter(d => d.doc_type === t).length})
            </button>
          ))}
        </div>

        {/* Document Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 16 }}>
          {filtered.map((doc, i) => (
            <div key={doc.doc_id} className="card animate-slide-up"
              style={{ animationDelay: `${i * 0.05}s`, cursor: "pointer" }}>
              <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
                <div style={{
                  width: 48, height: 48,
                  borderRadius: "var(--radius-md)",
                  background: "var(--primary-lighter)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "1.5rem", flexShrink: 0,
                }}>
                  {DOC_ICONS[doc.doc_type] || "📄"}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontWeight: 600, fontSize: "0.9rem",
                    overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                    marginBottom: 4,
                  }}>
                    {doc.title}
                  </div>
                  <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 8 }}>
                    <Badge type="primary">{doc.doc_type}</Badge>
                    <Badge type={doc.status === "completed" ? "success" : "warning"}>
                      {doc.status || "indexed"}
                    </Badge>
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    ID: {doc.doc_id}
                    {doc.created_at && ` • ${new Date(doc.created_at).toLocaleDateString()}`}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <EmptyState icon="📭" title="No documents found" message="No documents match the current filter." />
        )}
      </div>
    </>
  );
}
