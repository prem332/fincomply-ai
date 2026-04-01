export default function ConfidenceScore({ answer }) {
  if (!answer?.confidence_level) return null;

  const level  = answer.confidence_level;
  const score  = answer.confidence_score ?? 0;
  const pct    = Math.round(score * 100);
  const expl   = answer.confidence_explanation || "";

  const colorMap = {
    HIGH:   { bar: "#059669", badge: { color: "#065F46", bg: "#D1FAE5" } },
    MEDIUM: { bar: "#D97706", badge: { color: "#92400E", bg: "#FEF3C7" } },
    LOW:    { bar: "#DC2626", badge: { color: "#991B1B", bg: "#FEE2E2" } },
  };
  const colors = colorMap[level] || colorMap.LOW;

  return (
    <div style={{ marginBottom: "20px" }}>
      <p style={{ fontFamily: "DM Mono, monospace", fontSize: "0.7rem", color: "#6B8E89", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "10px" }}>
        Confidence Score
      </p>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
        <span style={{ padding: "4px 12px", borderRadius: "99px", fontFamily: "DM Sans, sans-serif", fontWeight: 700, fontSize: "0.875rem", color: colors.badge.color, backgroundColor: colors.badge.bg }}>
          {level}
        </span>
        <span style={{ fontFamily: "DM Mono, monospace", fontSize: "1.1rem", fontWeight: 600, color: colors.bar }}>
          {pct}%
        </span>
      </div>
      <div style={{ height: "6px", backgroundColor: "rgba(168,204,204,0.5)", borderRadius: "3px", overflow: "hidden", marginBottom: "10px" }}>
        <div style={{ height: "100%", width: `${pct}%`, backgroundColor: colors.bar, borderRadius: "3px", transition: "width 0.4s ease" }} />
      </div>
      {expl && (
        <p style={{ fontFamily: "DM Sans, sans-serif", fontSize: "0.8rem", color: "#3D5A56", lineHeight: 1.5 }}>
          {expl}
        </p>
      )}
    </div>
  );
}