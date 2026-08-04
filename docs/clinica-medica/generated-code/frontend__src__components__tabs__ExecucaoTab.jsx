import React from "react";

const styles = {
  controls: { display: "flex", gap: 8, marginBottom: 16 },
  btn: (color = "#1976d2") => ({ background: color, color: "white", border: "none", padding: "8px 16px", borderRadius: 4, cursor: "pointer", fontSize: 13 }),
  btnSec: { background: "white", color: "#1976d2", border: "1px solid #1976d2", padding: "8px 16px", borderRadius: 4, cursor: "pointer" },
  stats: { display: "flex", gap: 16, padding: 12, background: "#f5f9fc", borderRadius: 4, marginBottom: 16, fontSize: 13 },
  placesList: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(280px,1fr))", gap: 10 },
  place: (active, hasToken) => ({
    padding: 12,
    background: hasToken ? "#e3f2fd" : "#fafafa",
    border: active ? "2px solid #1976d2" : "1px solid #ddd",
    borderRadius: 6,
    fontSize: 13,
  }),
  trans: (enabled) => ({
    padding: "6px 10px",
    background: enabled ? "#c8e6c9" : "#eceff1",
    border: "1px solid " + (enabled ? "#4caf50" : "#cfd8dc"),
    borderRadius: 4,
    margin: "4px 6px 4px 0",
    display: "inline-block",
    fontSize: 12,
  }),
};

const ExecucaoTab = ({ project, exec }) => {
  const places = project.petriNet?.lugares || [];
  const transitions = project.petriNet?.transicoes || [];
  const enabledIds = new Set(exec.enabledTransitions.map((t) => t.id));

  return (
    <div>
      <div style={styles.controls}>
        <button style={styles.btn()} onClick={exec.runOneStep} disabled={exec.running}>▶ Próximo passo</button>
        <button style={styles.btn("#43a047")} onClick={() => exec.runAll(50)} disabled={exec.running}>⏩ Executar tudo</button>
        <button style={styles.btnSec} onClick={exec.reset}>↺ Reset</button>
      </div>

      <div style={styles.stats}>
        <span><strong>Step:</strong> {exec.step}</span>
        <span><strong>Eventos:</strong> {exec.events.length}</span>
        <span><strong>Habilitadas:</strong> {exec.enabledTransitions.length}</span>
        <span><strong>Status:</strong> {exec.running ? "🟡 executando" : "⚪ idle"}</span>
      </div>

      <h4>Transições</h4>
      <div style={{ marginBottom: 16 }}>
        {transitions.map((t) => (
          <span key={t.id} style={styles.trans(enabledIds.has(t.id))} title={t.guard || ""}>
            {t.nome || t.id} {enabledIds.has(t.id) ? "✓" : ""}
          </span>
        ))}
      </div>

      <h4>Lugares ({places.length})</h4>
      <div style={styles.placesList}>
        {places.map((p) => {
          const tokens = exec.marking[p.id] || 0;
          return (
            <div key={p.id} style={styles.place(false, tokens > 0)}>
              <strong>{p.id}</strong> — {p.nome}
              <div style={{ marginTop: 4 }}>
                <span style={{ background: tokens > 0 ? "#1976d2" : "#bbb", color: "white", padding: "2px 8px", borderRadius: 10, fontSize: 11 }}>
                  {tokens} token{tokens !== 1 ? "s" : ""}
                </span>
                {p.agentId && <span style={{ marginLeft: 6, fontSize: 11, color: "#666" }}>🤖 {p.agentId}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ExecucaoTab;
