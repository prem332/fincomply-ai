export default function DeadlineTimeline({ deadlines }) {
  if (!deadlines || deadlines.length === 0) return null;

  const urgencyStyle = {
    HIGH:   { dot: "#DC2626", text: "#DC2626", bg: "rgba(220,38,38,0.08)" },
    MEDIUM: { dot: "#D97706", text: "#D97706", bg: "rgba(217,119,6,0.08)" },
    LOW:    { dot: "#059669", text: "#059669", bg: "rgba(5,150,105,0.08)" },
  };

  return (
    <div style={{ marginBottom: "20px" }}>
      <p style={{ fontFamily: "DM Mono, monospace", fontSize: "0.7rem", color: "#6B8E89", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "10px" }}>
        Compliance Deadlines
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
        {deadlines.map((dl, i) => {
          const urgency = dl.urgency || "LOW";
          const style   = urgencyStyle[urgency] || urgencyStyle.LOW;
          return (
            <div key={i} style={{ backgroundColor: style.bg, borderRadius: "8px", padding: "9px 12px", borderLeft: `3px solid ${style.dot}` }}>
              <div style={{ fontFamily: "DM Sans, sans-serif", fontSize: "0.82rem", color: "#1A2E2B", fontWeight: 500, marginBottom: "2px" }}>
                {dl.description}
              </div>
              {dl.date && (
                <div style={{ fontFamily: "DM Mono, monospace", fontSize: "0.72rem", color: style.text, fontWeight: 600 }}>
                  📅 {dl.date} · {urgency}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}