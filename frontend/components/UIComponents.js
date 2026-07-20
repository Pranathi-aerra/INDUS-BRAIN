"use client";

export function StatCard({ icon, iconColor, value, label, trend, delay = 0 }) {
  return (
    <div
      className={`stat-card animate-slide-up`}
      style={{ animationDelay: `${delay * 0.08}s` }}
    >
      <div className={`stat-card-icon ${iconColor || "purple"}`}>{icon}</div>
      <div className="stat-card-value">{value}</div>
      <div className="stat-card-label">{label}</div>
      {trend && (
        <div style={{
          fontSize: "0.75rem",
          marginTop: 6,
          color: trend > 0 ? "var(--success)" : "var(--danger)",
          fontWeight: 600,
        }}>
          {trend > 0 ? "▲" : "▼"} {Math.abs(trend)}% vs last month
        </div>
      )}
    </div>
  );
}

export function Badge({ type = "neutral", children }) {
  return <span className={`badge badge-${type}`}>{children}</span>;
}

export function LoadingSpinner({ size = 32 }) {
  return (
    <div
      className="loading-spinner"
      style={{ width: size, height: size }}
    />
  );
}

export function LoadingDots() {
  return (
    <span className="loading-dots">
      <span></span><span></span><span></span>
    </span>
  );
}

export function EmptyState({ icon = "📭", title, message }) {
  return (
    <div className="empty-state animate-fade-in">
      <div className="empty-state-icon">{icon}</div>
      <div className="empty-state-title">{title}</div>
      <p>{message}</p>
    </div>
  );
}

export function ProgressBar({ value, max = 100, color }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const bg = color || (pct >= 80 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)");
  return (
    <div className="progress-bar">
      <div className="progress-fill" style={{ width: `${pct}%`, background: bg }} />
    </div>
  );
}

export function ComplianceGauge({ score }) {
  const circumference = 2 * Math.PI * 50;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? "var(--success)" : score >= 50 ? "var(--warning)" : "var(--danger)";

  return (
    <div className="gauge-container">
      <div className="gauge-ring">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle
            className="gauge-ring-bg"
            cx="60" cy="60" r="50"
            fill="none" strokeWidth="8"
          />
          <circle
            className="gauge-ring-fill"
            cx="60" cy="60" r="50"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="gauge-value">{score}%</div>
      </div>
    </div>
  );
}

export function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="card-header" style={{ marginBottom: 0 }}>
      <div>
        <h3 className="card-title">{title}</h3>
        {subtitle && <div className="card-subtitle">{subtitle}</div>}
      </div>
      {action}
    </div>
  );
}
