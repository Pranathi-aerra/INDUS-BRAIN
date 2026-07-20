import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { ToastProvider } from "@/components/Toast";
import ClientErrorBoundary from "@/components/ClientErrorBoundary";

export const metadata = {
  title: "Nazar — AI for Industrial Knowledge Intelligence",
  description: "Unified Asset & Operations Brain for industrial plant management. AI-powered knowledge graph, compliance tracking, and maintenance intelligence.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body>
        <ToastProvider>
          <div className="app-layout">
            <Sidebar />
            <main className="main-content">
              <ClientErrorBoundary>
                <div className="page-transition">
                  {children}
                </div>
              </ClientErrorBoundary>
            </main>
          </div>
        </ToastProvider>
      </body>
    </html>
  );
}
