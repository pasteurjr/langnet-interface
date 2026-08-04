import React from "react";

const styles = {
  block: { background: "#f5f9fc", padding: 12, borderRadius: 4, marginBottom: 12, borderLeft: "3px solid #1976d2" },
  title: { fontWeight: 600, color: "#1976d2", marginBottom: 6 },
  pre: { fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap", margin: 0, maxHeight: 400, overflow: "auto" },
  empty: { color: "#666", padding: 20, textAlign: "center" },
};

const OutputsTab = ({ project, exec }) => {
  const entries = Object.entries(exec.outputs || {});
  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Outputs por place ({entries.length})</h3>
      {entries.length === 0 && (
        <div style={styles.empty}>
          Nenhum output ainda. Vá para a aba <strong>Execução</strong> e dispare a Petri Net,
          ou use <strong>Operação</strong> pra disparar uma task isolada.
        </div>
      )}
      {entries.map(([placeId, out]) => (
        <div key={placeId} style={styles.block}>
          <div style={styles.title}>{placeId}</div>
          <pre style={styles.pre}>{JSON.stringify(out, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
};

export default OutputsTab;
