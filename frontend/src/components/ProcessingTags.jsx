export default function ProcessingTags({ steps, isLoading }) {
  const defaultPills = ["Research Agent", "Critic Agent", "Supervisor Verified"];

  return (
    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "14px" }}>
      {defaultPills.map((pill, i) => {
        const completed = steps.some((s) => s.includes(pill.split(" ")[0]));
        const active    = isLoading && i === steps.length;

        return (
          <span key={pill}
            style={{ display: "inline-flex", alignItems: "center", gap: "5px", padding: "4px 12px", borderRadius: "99px", fontSize: "0.78rem", fontFamily: "DM Mono, monospace", fontWeight: 500, backgroundColor: completed ? "rgba(15,118,110,0.12)" : active ? "rgba(15,118,110,0.06)" : "rgba(168,204,204,0.3)", color: completed ? "#0F766E" : "#6B8E89", border: `1px solid ${completed ? "rgba(15,118,110,0.25)" : "rgba(168,204,204,0.5)"}` }}>
            {active && <span>●</span>}
            {completed && "✓ "}
            {pill}
          </span>
        );
      })}
    </div>
  );
}