import { useState } from "react";

export default function QueryBox({ onSubmit, isLoading }) {
  const [query, setQuery] = useState("");

  const handleSubmit = () => {
    if (!query.trim() || isLoading) return;
    onSubmit(query);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div style={{ backgroundColor: "#FFFFFF", borderRadius: "12px", border: "2px solid #A8CCCC", padding: "16px", boxShadow: "0 4px 16px rgba(15,118,110,0.10)" }}>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a compliance question... e.g. 'What is the GST rate for software services?'"
        rows={3}
        style={{ width: "100%", border: "none", outline: "none", fontFamily: "DM Sans, sans-serif", fontSize: "0.9375rem", color: "#1A2E2B", resize: "none", backgroundColor: "transparent", lineHeight: 1.6 }}
      />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
        <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.75rem", color: "#6B8E89" }}>
          {query.length}/1000 · Press Enter to submit
        </span>
        <button onClick={handleSubmit} disabled={isLoading || !query.trim()}
          style={{ backgroundColor: "#0F766E", color: "#FFFFFF", border: "none", borderRadius: "8px", padding: "9px 20px", fontFamily: "DM Sans, sans-serif", fontWeight: 600, fontSize: "0.9rem", cursor: isLoading || !query.trim() ? "not-allowed" : "pointer", opacity: isLoading || !query.trim() ? 0.55 : 1 }}>
          {isLoading ? "Analysing..." : "Analyse Now →"}
        </button>
      </div>
    </div>
  );
}