"use client";
import { useEffect, useState } from "react";
import { getDashboardStats, getMaintenanceDashboard, getComplianceDashboard } from "@/lib/api";
import { StatCard, ComplianceGauge, Badge, ProgressBar } from "@/components/UIComponents";
import { ConnectionBanner, SkeletonDashboard } from "@/components/ErrorHandling";
import { useToast } from "@/components/Toast";

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [maintenance, setMaintenance] = useState(null);
  const [compliance, setCompliance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(false);
  const { addToast } = useToast();

  const loadData = async () => {
    setLoading(true);
    setConnectionError(false);
    try {
      const [s, m, c] = await Promise.all([
        getDashboardStats(),
        getMaintenanceDashboard(),
        getComplianceDashboard(),
      ]);
      setStats(s);
      setMaintenance(m);
      setCompliance(c);
      if (connectionError) addToast("Reconnected to server", "success");
    } catch (err) {
      console.error("Dashboard load error:", err);
      setConnectionError(true);
      addToast("Could not connect to backend server", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1>Welcome to Nazar</h1>
          <p>Loading operations overview...</p>
        </div>
        <SkeletonDashboard />
      </>
    );
  }

  if (connectionError) {
    return (
      <>
        <ConnectionBanner onRetry={loadData} />
        <div className="page-header" style={{ marginTop: 44 }}>
          <h1>Welcome to Nazar</h1>
          <p>AI-powered Industrial Knowledge Intelligence</p>
        </div>
        <div className="page-body">
          <div className="card" style={{ textAlign: "center", padding: 64 }}>
            <div style={{ fontSize: "3rem", marginBottom: 16 }}>🔌</div>
            <h3 style={{ marginBottom: 8 }}>Backend Unavailable</h3>
            <p style={{ color: "var(--text-muted)", marginBottom: 24 }}>
              Make sure the FastAPI server is running on port 8000
            </p>
            <button className="btn btn-primary" onClick={loadData}>
              Try Again
            </button>
          </div>
        </div>
      </>
    );
  }

  const openWOs = stats?.work_orders_by_status?.open || 0;
  const inProgressWOs = stats?.work_orders_by_status?.in_progress || 0;

  return (
    <>
      <div className="page-header">
        <h1>Welcome to Nazar</h1>
        <p>AI-powered Industrial Knowledge Intelligence — Jamnagar Unit-3 Operations Overview</p>
      </div>

      <div className="page-body">
        {/* Stats Grid */}
        <div className="stats-grid">
          <StatCard icon="⚙️" iconColor="purple" value={stats?.total_equipment || 0} label="Total Equipment" delay={0} />
          <StatCard icon="📄" iconColor="blue" value={stats?.total_documents || 0} label="Documents Indexed" delay={1} />
          <StatCard icon="🔧" iconColor="teal" value={openWOs + inProgressWOs} label="Active Work Orders" delay={2} />
          <StatCard icon="🔍" iconColor="amber" value={stats?.overdue_inspections || 0} label="Overdue Inspections" delay={3} />
          <StatCard icon="📋" iconColor="green" value={`${stats?.compliance_score || 0}%`} label="Compliance Score" delay={4} />
          <StatCard icon="⚠️" iconColor="rose" value={stats?.open_incidents || 0} label="Open Incidents" delay={5} />
        </div>

        {/* Two Column Layout */}
        <div className="grid-2" style={{ marginBottom: 24 }}>
          {/* Compliance Overview */}
          <div className="card animate-slide-up" style={{ animationDelay: "0.3s" }}>
            <div className="card-header">
              <div>
                <div className="card-title">Compliance Overview</div>
                <div className="card-subtitle">Regulatory compliance status</div>
              </div>
              <Badge type={compliance?.overall_score >= 80 ? "success" : compliance?.overall_score >= 50 ? "warning" : "danger"}>
                {compliance?.overall_score >= 80 ? "Good" : compliance?.overall_score >= 50 ? "Needs Attention" : "Critical"}
              </Badge>
            </div>
            <ComplianceGauge score={compliance?.overall_score || 0} />
            <div style={{ marginTop: 16 }}>
              {compliance?.by_regulation && Object.entries(compliance.by_regulation).map(([reg, data]) => (
                <div key={reg} style={{
                  display: "flex", alignItems: "center", gap: 12,
                  padding: "10px 0", borderBottom: "1px solid var(--border-light)"
                }}>
                  <div style={{ flex: 1, fontSize: "0.85rem", fontWeight: 500 }}>{reg}</div>
                  <div style={{ width: 100 }}>
                    <ProgressBar value={data.score} />
                  </div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, width: 40, textAlign: "right", color: "var(--text-secondary)" }}>
                    {data.score}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Equipment Health */}
          <div className="card animate-slide-up" style={{ animationDelay: "0.4s" }}>
            <div className="card-header">
              <div>
                <div className="card-title">Equipment Health</div>
                <div className="card-subtitle">Top equipment requiring attention</div>
              </div>
            </div>
            <div>
              {maintenance?.top_failing_equipment?.map((eq, i) => (
                <div key={eq.tag} style={{
                  display: "flex", alignItems: "center", gap: 12,
                  padding: "12px 0", borderBottom: "1px solid var(--border-light)"
                }}>
                  <div style={{
                    width: 36, height: 36,
                    borderRadius: "var(--radius-sm)",
                    background: i === 0 ? "var(--danger-bg)" : i < 3 ? "var(--warning-bg)" : "var(--info-bg)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "0.85rem", fontWeight: 700,
                    color: i === 0 ? "var(--danger)" : i < 3 ? "var(--warning)" : "var(--info)",
                  }}>
                    #{i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: "0.875rem", fontWeight: 600 }}>{eq.tag}</div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{eq.name}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "0.875rem", fontWeight: 700, color: "var(--danger)" }}>
                      {eq.total_failures} failures
                    </div>
                    {eq.mtbf_days && (
                      <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                        MTBF: {eq.mtbf_days}d
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Compliance Gaps */}
        <div className="card animate-slide-up" style={{ animationDelay: "0.5s" }}>
          <div className="card-header">
            <div>
              <div className="card-title">Compliance Gaps</div>
              <div className="card-subtitle">{compliance?.gaps?.length || 0} items need attention</div>
            </div>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Regulation</th>
                  <th>Clause</th>
                  <th>Requirement</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {compliance?.gaps?.slice(0, 6).map((gap) => (
                  <tr key={gap.req_id}>
                    <td style={{ fontWeight: 600 }}>{gap.regulation}</td>
                    <td><code style={{ color: "var(--primary)" }}>{gap.clause}</code></td>
                    <td style={{ fontSize: "0.8rem", maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {gap.requirement_text}
                    </td>
                    <td>
                      <Badge type={gap.current_status === "non_compliant" ? "danger" : "warning"}>
                        {gap.current_status === "non_compliant" ? "Non-Compliant" : "Partial"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Failure Trends */}
        {maintenance?.failure_trends?.length > 0 && (
          <div className="card animate-slide-up" style={{ animationDelay: "0.6s", marginTop: 24 }}>
            <div className="card-header">
              <div>
                <div className="card-title">Failure Trends</div>
                <div className="card-subtitle">Monthly corrective/emergency work orders</div>
              </div>
            </div>
            <div style={{
              display: "flex", alignItems: "flex-end", gap: 4,
              height: 160, padding: "16px 0",
            }}>
              {maintenance.failure_trends.slice(-12).map((t, i) => {
                const maxCount = Math.max(...maintenance.failure_trends.slice(-12).map(x => x.count));
                const height = maxCount > 0 ? (t.count / maxCount) * 120 : 0;
                return (
                  <div key={i} style={{
                    flex: 1, display: "flex", flexDirection: "column",
                    alignItems: "center", gap: 4,
                  }}>
                    <div style={{ fontSize: "0.65rem", fontWeight: 600, color: "var(--text-muted)" }}>
                      {t.count}
                    </div>
                    <div style={{
                      width: "100%", maxWidth: 32,
                      height: Math.max(4, height),
                      background: t.count >= 4 ? "var(--danger)" : t.count >= 2 ? "var(--warning)" : "var(--primary)",
                      borderRadius: "4px 4px 0 0",
                      transition: "height 0.8s ease",
                      opacity: 0.85,
                    }} />
                    <div style={{
                      fontSize: "0.6rem", color: "var(--text-muted)",
                      writingMode: "vertical-lr", transform: "rotate(180deg)",
                      maxHeight: 50, overflow: "hidden",
                    }}>
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
