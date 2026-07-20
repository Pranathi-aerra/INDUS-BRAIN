"use client";
import { ErrorBoundary } from "./ErrorHandling";

export default function ClientErrorBoundary({ children }) {
  return <ErrorBoundary>{children}</ErrorBoundary>;
}
