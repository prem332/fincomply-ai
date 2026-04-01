export default function SourceCitations({ answer }) {
  if (!answer?.source_url) return null;

  const isGovVerified = answer.is_gov_verified ?? answer.source_url?.includes(".gov.in");

  return (
    <div style={{ marginTop: "16px" }}>
      <p style={{ fontFamily: "DM Mono, monospace", fontSize: "0.72rem", color: "#6B8E89", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "8px" }}>
        Source Citation
      </p>
      <div style={{ backgroundColor: "#B8D4CF", borderRadius: "10px", border: "1px solid #A8CCCC", padding: "14px 16px", display: "flex", flexDirection: "column", gap: "6px" }}>

        {isGovVerified && (
          <span style={{ display: "inline-flex", alignItems: "center", gap: "5px", alignSelf: "flex-start", padding: "2px 10px", borderRadius: "99px", fontSize: "0.72rem", fontFamily: "DM Mono, monospace", fontWeight: 600, color: "#065F46", backgroundColor: "#D1FAE5", border: "1px solid #6EE7B7" }}>
            ✓ GOVT VERIFIED
          </span>
        )}

        {answer.circular_number && answer.circular_number !== "Unknown" && (
          <div style={{ display: "flex", gap: "8px" }}>
            <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.75rem", color: "#6B8E89", flexShrink: 0 }}>Circular</span>
            <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.78rem", color: "#0F766E", fontWeight: 500 }}>{answer.circular_number}</span>
          </div>
        )}

        {answer.published_date && (
          <div style={{ display: "flex", gap: "8px" }}>
            <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.75rem", color: "#6B8E89", flexShrink: 0 }}>Date</span>
            <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.78rem", color: "#1A2E2B" }}>{answer.published_date}</span>
          </div>
        )}

        {answer.source_url && answer.source_url !== "Unknown" && (
          <div style={{ display: "flex", gap: "8px" }}>
            <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.75rem", color: "#6B8E89", flexShrink: 0 }}>URL</span>
            <a href={answer.source_url} target="_blank" rel="noopener noreferrer"
              style={{ fontFamily: "DM Mono, monospace", fontSize: "0.75rem", color: "#0F766E", textDecoration: "none", wordBreak: "break-all", borderBottom: "1px dashed #0F766E" }}>
              {answer.source_url}
            </a>
          </div>
        )}

      </div>
    </div>
  );
}