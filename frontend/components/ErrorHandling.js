"use client";
import { Component } from "react";

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card" style={{
          margin: 32,
          textAlign: "center",
          padding: 48,
          animation: "fadeIn 0.5s ease both",
        }}>
          <div style={{ fontSize: "3rem", marginBottom: 16 }}>😵</div>
          <h2 style={{ marginBottom: 8 }}>Something went wrong</h2>
          <p style={{ color: "var(--text-muted)", marginBottom: 24, maxWidth: 400, margin: "0 auto 24px" }}>
            {this.state.error?.message || "An unexpected error occurred. Please try again."}
          </p>
          <button
            className="btn btn-primary"
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export function ConnectionBanner({ onRetry }) {
  return (
    <div className="connection-banner">
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span>⚠️</span>
        <span>Unable to connect to the backend server. Make sure it&apos;s running on port 8000.</span>
      </div>
      <button onClick={onRetry}>Retry</button>
    </div>
  );
}

export function SkeletonDashboard() {
  return (
    <div className="page-body" style={{ animation: "fadeIn 0.3s ease both" }}>
      <div className="stats-grid">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton skeleton-card" />
        ))}
      </div>
      <div className="grid-2" style={{ marginTop: 24 }}>
        <div className="skeleton skeleton-card" style={{ height: 300 }} />
        <div className="skeleton skeleton-card" style={{ height: 300 }} />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5 }) {
  return (
    <div style={{ padding: 24 }}>
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="skeleton-row">
          <div className="skeleton skeleton-avatar" />
          <div style={{ flex: 1 }}>
            <div className="skeleton skeleton-text medium" />
            <div className="skeleton skeleton-text short" />
          </div>
        </div>
      ))}
    </div>
  );
}
