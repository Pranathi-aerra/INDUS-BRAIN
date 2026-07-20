"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

const navItems = [
  { label: "Overview", href: "/", icon: "📊" },
  { label: "AI Assistant", href: "/chat", icon: "💬" },
  { section: "Intelligence" },
  { label: "Knowledge Graph", href: "/knowledge", icon: "🔗" },
  { label: "Maintenance", href: "/maintenance", icon: "🔧" },
  { label: "Compliance", href: "/compliance", icon: "📋" },
  { label: "Documents", href: "/documents", icon: "📁" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Close sidebar on Escape key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") setMobileOpen(false);
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, []);

  return (
    <>
      {/* Hamburger Button (mobile only) */}
      <button
        className={`hamburger-btn ${mobileOpen ? "active" : ""}`}
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle navigation"
      >
        <div className="hamburger-icon">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </button>

      {/* Overlay (mobile only) */}
      <div
        className={`sidebar-overlay ${mobileOpen ? "visible" : ""}`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">👁</div>
          <div>
            <div className="sidebar-brand-text">Nazar</div>
            <div className="sidebar-brand-badge">AI Platform</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {navItems.map((item, i) => {
            if (item.section) {
              return (
                <div key={i} className="nav-section-label">
                  {item.section}
                </div>
              );
            }

            const isActive = pathname === item.href ||
              (item.href !== "/" && pathname?.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-item ${isActive ? "active" : ""}`}
                onClick={() => setMobileOpen(false)}
              >
                <span className="nav-item-icon">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border-light)",
          fontSize: "0.75rem",
          color: "var(--text-muted)"
        }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Bharat Petrochemicals</div>
          <div>Jamnagar Unit-3</div>
        </div>
      </aside>
    </>
  );
}
