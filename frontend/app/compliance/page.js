"use client";
import { useEffect, useState } from "react";
import { getComplianceDashboard, getComplianceRequirements } from "@/lib/api";
import { LoadingSpinner, ComplianceGauge, Badge, ProgressBar } from "@/components/UIComponents";

export default function CompliancePage() {
  const [dashboard, setDashboard] = useState(null);
  const [requirements, setRequirements] = useState(null);
  const [activeFilter, setActiveFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [d, r] = await Promise.all([
          getComplianceDashboard(),
          getComplianceRequirements(),
        ]);
        setDashboard(d);
        setRequirements(r.requirements);
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

  const filtered = activeFilter === "all"
    ? requirements
    : requirements?.filter(r => r.current_status === activeFilter);

  const statusBadge = (status) => {
    const map = {
      compliant: { type: "success", label: "Compliant" },
      non_compliant: { type: "danger", label: "Non-Compliant" },
      partial: { type: "warning", label: "Partial" },
      unknown: { type: "neutral", label: "Unknown" },
    };
    const s = map[status] || map.unknown;
    return <Badge type={s.type}>{s.label}</Badge>;
  };

  return (
    <>
      <div className="page-header">
        <h1>Compliance Dashboard</h1>
        <p>Regulatory compliance tracking across Indian industrial standards</p>
      </div>

      <div className="page-body">
        {/* Overview Cards */}
        <div className="grid-3" style={{ marginBottom: 24 }}>
          <div className="card animate-slide-up" style={{ textAlign: "center" }}>
            <ComplianceGauge score={dashboard?.overall_score || 0} />
            <div style={{ fontWeight: 700, fontSize: "1rem", marginTop: 8 }}>Overall Score</div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              {dashboard?.total_requirements || 0} total requirements
            </div>
          </div>

          <div className="card animate-slide-up" style={{ animationDelay: "0.1s" }}>
            <div className="card-header">
              <div className="card-title">By Regulation</div>
            </div>
            {dashboard?.by_regulation && Object.entries(dashboard.by_regulation).map(([reg, data]) => (
              <div key={reg} style={{
                padding: "8px 0", borderBottom: "1px solid var(--border-light)",
                display: "flex", alignItems: "center", gap: 12,
              }}>
                <div style={{ flex: 1, fontSize: "0.8rem", fontWeight: 500 }}>{reg}</div>
                <div style={{ width: 80 }}><ProgressBar value={data.score} /></div>
                <div style={{ fontSize: "0.75rem", fontWeight: 600, width: 35, textAlign: "right" }}>{data.score}%</div>
              </div>
            ))}
          </div>

          <div className="card animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <div className="card-header">
              <div className="card-title">Upcoming Audits</div>
            </div>
            {dashboard?.upcoming_audits?.slice(0, 5).map((a, i) => (
              <div key={i} style={{
                padding: "8px 0", borderBottom: "1px solid var(--border-light)",
                fontSize: "0.8rem",
              }}>
                <div style={{ fontWeight: 600 }}>{a.regulation}</div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
                  {a.clause} &middot; {a.next_audit_date || "TBD"}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Requirements Table */}
        <div className="card animate-slide-up" style={{ animationDelay: "0.3s" }}>
          <div className="card-header">
            <div className="card-title">All Requirements</div>
            <div style={{ display: "flex", gap: 6 }}>
              {["all", "compliant", "non_compliant", "partial"].map(f => (
                <button key={f} className={`mode-chip ${activeFilter === f ? "active" : ""}`}
                  onClick={() => setActiveFilter(f)} style={{ fontSize: "0.75rem" }}>
                  {f === "all" ? "All" : f === "non_compliant" ? "Non-Compliant" : f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Regulation</th>
                  <th>Clause</th>
                  <th>Requirement</th>
                  <th>Category</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered?.map((req) => (
                  <tr key={req.req_id}>
                    <td><code style={{ fontSize: "0.75rem", color: "var(--primary)" }}>{req.req_id}</code></td>
                    <td style={{ fontWeight: 500, fontSize: "0.8rem" }}>{req.regulation}</td>
                    <td style={{ fontSize: "0.8rem" }}>{req.clause}</td>
                    <td style={{
                      fontSize: "0.8rem", maxWidth: 300,
                      overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"
                    }}>
                      {req.requirement_text}
                    </td>
                    <td><Badge type="neutral">{req.category}</Badge></td>
                    <td>{statusBadge(req.current_status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
