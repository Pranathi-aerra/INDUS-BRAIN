"use client";
import { useEffect, useState } from "react";
import { getMaintenanceDashboard, getWorkOrders, getIncidents } from "@/lib/api";
import { StatCard, LoadingSpinner, Badge, ProgressBar } from "@/components/UIComponents";

export default function MaintenancePage() {
  const [dashboard, setDashboard] = useState(null);
  const [incidents, setIncidents] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("health");

  useEffect(() => {
    async function load() {
      try {
        const [d, inc] = await Promise.all([
          getMaintenanceDashboard(),
          getIncidents(),
        ]);
        setDashboard(d);
        setIncidents(inc.incidents);
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

  const criticalityBadge = (c) => {
    const map = { high: "danger", medium: "warning", low: "info" };
    return <Badge type={map[c] || "neutral"}>{c}</Badge>;
  };

  const statusBadge = (s) => {
    const map = { operational: "success", degraded: "warning", down: "danger", standby: "info" };
    return <Badge type={map[s] || "neutral"}>{s}</Badge>;
  };

  return (
    <>
      <div className="page-header">
        <h1>Maintenance Intelligence</h1>
        <p>Equipment health monitoring, failure analysis & work order tracking</p>
      </div>

      <div className="page-body">
        {/* Summary Stats */}
        <div className="stats-grid">
          <StatCard icon="🔧" iconColor="teal" value={dashboard?.total_work_orders || 0} label="Total Work Orders" delay={0} />
          <StatCard icon="📋" iconColor="amber" value={dashboard?.open_work_orders || 0} label="Open / In Progress" delay={1} />
          <StatCard icon="⏱️" iconColor="rose" value={`${dashboard?.avg_downtime_hours || 0}h`} label="Avg Downtime" delay={2} />
          <StatCard icon="⚠️" iconColor="purple" value={incidents?.length || 0} label="Total Incidents" delay={3} />
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
          {[
            { key: "health", label: "Equipment Health" },
            { key: "incidents", label: "Incidents" },
            { key: "trends", label: "Trends" },
          ].map(t => (
            <button key={t.key} className={`mode-chip ${tab === t.key ? "active" : ""}`}
              onClick={() => setTab(t.key)}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Equipment Health Table */}
        {tab === "health" && (
          <div className="card animate-fade-in">
            <div className="card-header">
              <div className="card-title">Equipment Health Summary</div>
              <div className="card-subtitle">{dashboard?.equipment_health?.length} assets tracked</div>
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Equipment</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Criticality</th>
                    <th>Failures</th>
                    <th>MTBF (days)</th>
                    <th>MTTR (hrs)</th>
                    <th>Total WOs</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard?.equipment_health?.map((eq) => (
                    <tr key={eq.tag}>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>{eq.tag}</div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{eq.name}</div>
                      </td>
                      <td style={{ fontSize: "0.8rem" }}>{eq.equipment_type}</td>
                      <td>{statusBadge(eq.status)}</td>
                      <td>{criticalityBadge(eq.criticality)}</td>
                      <td>
                        <span style={{
                          fontWeight: 700,
                          color: eq.total_failures > 3 ? "var(--danger)" : eq.total_failures > 1 ? "var(--warning)" : "var(--text-primary)"
                        }}>
                          {eq.total_failures}
                        </span>
                      </td>
                      <td>{eq.mtbf_days || "—"}</td>
                      <td>{eq.mttr_hours || "—"}</td>
                      <td>{eq.total_work_orders}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Incidents */}
        {tab === "incidents" && (
          <div className="card animate-fade-in">
            <div className="card-header">
              <div className="card-title">Incident Reports</div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {incidents?.map((inc) => (
                <div key={inc.incident_id} className="card" style={{
                  padding: 16, border: `1px solid ${
                    inc.severity === "high" ? "var(--danger)" :
                    inc.severity === "medium" ? "var(--warning)" : "var(--border)"
                  }`,
                  borderLeft: `4px solid ${
                    inc.severity === "high" ? "var(--danger)" :
                    inc.severity === "medium" ? "var(--warning)" : "var(--info)"
                  }`,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>{inc.incident_id}</span>
                      <Badge type={inc.severity === "high" ? "danger" : inc.severity === "medium" ? "warning" : "info"}>
                        {inc.severity}
                      </Badge>
                      <Badge type="neutral">{inc.incident_type}</Badge>
                    </div>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{inc.date_occurred}</span>
                  </div>
                  <p style={{ fontSize: "0.85rem", marginBottom: 8 }}>{inc.description}</p>
                  {inc.root_cause && (
                    <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", background: "var(--bg-hover)", padding: "8px 12px", borderRadius: "var(--radius-sm)" }}>
                      <strong>Root Cause:</strong> {inc.root_cause}
                    </div>
                  )}
                  {inc.equipment_tag && (
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: 8 }}>
                      Equipment: <strong>{inc.equipment_tag}</strong> &middot; Area: {inc.area}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trends */}
        {tab === "trends" && dashboard?.failure_trends?.length > 0 && (
          <div className="card animate-fade-in">
            <div className="card-header">
              <div className="card-title">Monthly Failure Trends</div>
              <div className="card-subtitle">Corrective & emergency work orders per month</div>
            </div>
            <div style={{
              display: "flex", alignItems: "flex-end", gap: 6,
              height: 220, padding: "20px 0",
            }}>
              {dashboard.failure_trends.map((t, i) => {
                const maxCount = Math.max(...dashboard.failure_trends.map(x => x.count));
                const height = maxCount > 0 ? (t.count / maxCount) * 180 : 0;
                return (
                  <div key={i} style={{
                    flex: 1, display: "flex", flexDirection: "column",
                    alignItems: "center", gap: 4,
                  }}>
                    <div style={{ fontSize: "0.7rem", fontWeight: 600 }}>{t.count}</div>
                    <div style={{
                      width: "100%", maxWidth: 28,
                      height: Math.max(4, height),
                      background: `linear-gradient(to top, ${t.count >= 4 ? "#ef4444" : t.count >= 2 ? "#f59e0b" : "#6366f1"}, ${t.count >= 4 ? "#fca5a5" : t.count >= 2 ? "#fde68a" : "#a5b4fc"})`,
                      borderRadius: "4px 4px 0 0",
                    }} />
                    <div style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>
                      {t.month.slice(5)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
