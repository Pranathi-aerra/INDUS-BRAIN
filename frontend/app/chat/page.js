"use client";
import { useState, useRef, useEffect } from "react";
import { sendQuery } from "@/lib/api";
import { Badge } from "@/components/UIComponents";
import { useToast } from "@/components/Toast";
import ReactMarkdown from "react-markdown";

const MODES = [
  { key: "copilot", label: "General Copilot", icon: "💬" },
  { key: "maintenance", label: "Maintenance RCA", icon: "🔧" },
  { key: "compliance", label: "Compliance", icon: "📋" },
  { key: "failure", label: "Failure Analysis", icon: "⚠️" },
];

const WELCOME_SUGGESTIONS = [
  "What is the maintenance history of pump P-201-A?",
  "Show me the OISD-118 compliance gaps",
  "What incidents occurred in the CDU area?",
  "Explain the startup procedure for the crude distillation unit",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("copilot");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const { addToast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => { scrollToBottom(); }, [messages]);

  const handleSend = async (text) => {
    const query = text || input.trim();
    if (!query || isLoading) return;

    setInput("");
    const userMessage = { role: "user", content: query, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await sendQuery(query, mode);
      const assistantMessage = {
        role: "assistant",
        content: result.answer,
        confidence: result.confidence,
        sources: result.sources || [],
        followUps: result.follow_up_questions || [],
        mode: result.mode,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      addToast(err.message || "Failed to get response", "error");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Sorry, I encountered an error: ${err.message}. Please try again.`, timestamp: new Date() },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const confidenceColor = (c) =>
    c >= 70 ? "var(--success)" : c >= 40 ? "var(--warning)" : "var(--danger)";

  return (
    <>
      <div className="page-header">
        <h1>AI Assistant</h1>
        <p>Ask questions about equipment, maintenance, compliance, and operations</p>
      </div>

      <div className="chat-container">
        {/* Messages Area */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="animate-fade-in" style={{
              display: "flex", flexDirection: "column", alignItems: "center",
              justifyContent: "center", flex: 1, gap: 24, paddingTop: 60,
            }}>
              <div style={{
                width: 80, height: 80,
                background: "var(--primary-lighter)",
                borderRadius: "var(--radius-xl)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "2.5rem",
              }}>
                👁
              </div>
              <div style={{ textAlign: "center" }}>
                <h2 style={{ marginBottom: 8 }}>How can I help you today?</h2>
                <p style={{ color: "var(--text-muted)", maxWidth: 500 }}>
                  I have access to your plant&apos;s equipment data, maintenance history,
                  compliance records, and SOPs. Ask me anything!
                </p>
              </div>
              <div className="follow-ups" style={{ justifyContent: "center", maxWidth: 600 }}>
                {WELCOME_SUGGESTIONS.map((s, i) => (
                  <button key={i} className="follow-up-chip" onClick={() => handleSend(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.role}`}>
              <div className="chat-bubble">
                {msg.role === "assistant" ? (
                  <div className="markdown-body">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
                )}
              </div>

              {/* Sources */}
              {msg.sources?.length > 0 && (
                <div className="chat-sources">
                  {msg.sources.map((s, j) => (
                    <span key={j} className="chat-source-tag" title={s.excerpt}>
                      📄 {s.title || s.doc_id}
                    </span>
                  ))}
                </div>
              )}

              {/* Confidence */}
              {msg.confidence != null && msg.confidence > 0 && (
                <div className="chat-confidence">
                  <span>Confidence:</span>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${msg.confidence}%`,
                        background: confidenceColor(msg.confidence),
                      }}
                    />
                  </div>
                  <span>{msg.confidence}%</span>
                  <Badge type={msg.mode === "copilot" ? "primary" : "info"}>
                    {MODES.find(m => m.key === msg.mode)?.label || msg.mode}
                  </Badge>
                </div>
              )}

              {/* Follow-ups */}
              {msg.followUps?.length > 0 && (
                <div className="follow-ups">
                  {msg.followUps.map((f, j) => (
                    <button key={j} className="follow-up-chip" onClick={() => handleSend(f)}>
                      {f}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="chat-message assistant">
              <div className="chat-bubble">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span style={{ color: "var(--text-muted)", fontSize: "0.82rem", paddingLeft: 4 }}>Thinking...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          <div className="chat-mode-selector">
            {MODES.map((m) => (
              <button
                key={m.key}
                className={`mode-chip ${mode === m.key ? "active" : ""}`}
                onClick={() => setMode(m.key)}
              >
                {m.icon} {m.label}
              </button>
            ))}
          </div>
          <div className="chat-input-wrapper">
            <textarea
              ref={inputRef}
              className="chat-input"
              placeholder={`Ask about equipment, maintenance, compliance...`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button
              className="chat-send-btn"
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
            >
              ➤
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
