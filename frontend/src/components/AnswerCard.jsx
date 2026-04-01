export default function AnswerCard({ answer, responseTimeMs }) {
  if (!answer?.final_answer) return null;

  return (
    <div style={{ backgroundColor: "#C8E0DB", borderRadius: "12px", border: "1px solid #A8CCCC", padding: "20px 24px", marginTop: "18px", boxShadow: "0 2px 8px rgba(15,118,110,0.08)" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
        <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.72rem", color: "#0F766E", backgroundColor: "rgba(15,118,110,0.12)", padding: "3px 10px", borderRadius: "99px", border: "1px solid rgba(15,118,110,0.2)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
          ✓ Supervisor Verified Answer
        </span>
        {responseTimeMs && (
          <span style={{ fontFamily: "DM Mono, monospace", fontSize: "0.72rem", color: "#6B8E89" }}>
            {responseTimeMs.toFixed(0)}ms
          </span>
        )}
      </div>

      <p style={{ fontFamily: "DM Sans, sans-serif", fontSize: "1rem", color: "#1A2E2B", lineHeight: 1.7, marginBottom: "16px" }}>
        {answer.final_answer}
      </p>

      {answer.action_required && (
        <div style={{ backgroundColor: "#FEF3C7", border: "1px solid #FCD34D", borderRadius: "8px", padding: "12px 16px", marginBottom: "12px" }}>
          <p style={{ fontFamily: "DM Mono, monospace", fontSize: "0.72rem", color: "#92400E", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "4px" }}>
            Action Required
          </p>
          <p style={{ fontFamily: "DM Sans, sans-serif", fontSize: "0.9rem", color: "#78350F" }}>
            {answer.action_required}
          </p>
        </div>
      )}

      {answer.gaps_acknowledged?.length > 0 && (
        <div style={{ marginTop: "10px" }}>
          <p style={{ fontFamily: "DM Mono, monospace", fontSize: "0.72rem", color: "#6B8E89", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "6px" }}>
            Areas to verify manually
          </p>
          <ul style={{ paddingLeft: "16px" }}>
            {answer.gaps_acknowledged.map((gap, i) => (
              <li key={i} style={{ fontFamily: "DM Sans, sans-serif", fontSize: "0.85rem", color: "#3D5A56", marginBottom: "3px" }}>
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}