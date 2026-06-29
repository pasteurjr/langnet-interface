import React from "react";

const styles = {
  block: { background: "#fafafa", padding: 12, borderRadius: 4, marginBottom: 12 },
  title: { fontWeight: 600, color: "#1976d2", marginBottom: 6 },
  pre: { fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap", margin: 0 },
};

const InputsTab = ({ project, exec }) => {
  const places = project.petriNet?.lugares || [];
  const withInput = places.filter((p) => p.input_data && Object.keys(p.input_data).length > 0);

  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Inputs declarados nos places ({withInput.length})</h3>
      {withInput.length === 0 && <p style={{ color: "#666" }}>Nenhum place tem input_data declarado.</p>}
      {withInput.map((p) => (
        <div key={p.id} style={styles.block}>
          <div style={styles.title}>{p.id} — {p.nome}</div>
          <pre style={styles.pre}>{JSON.stringify(p.input_data, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
};

export default InputsTab;
