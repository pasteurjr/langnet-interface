import React from "react";

const styles = {
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(320px,1fr))", gap: 16 },
  card: {
    background: "white",
    borderRadius: 8,
    padding: 20,
    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  cardHover: { boxShadow: "0 4px 12px rgba(0,0,0,0.15)", transform: "translateY(-2px)" },
  name: { margin: "0 0 8px", fontSize: 18, color: "#1976d2" },
  desc: { margin: "0 0 16px", fontSize: 13, color: "#666", minHeight: 36 },
  stats: { display: "flex", gap: 12, flexWrap: "wrap", fontSize: 12 },
  stat: { background: "#f0f4f8", padding: "4px 10px", borderRadius: 12, color: "#37474f" },
};

const ProjectSelector = ({ projects, onSelect }) => {
  const [hover, setHover] = React.useState(null);
  if (!projects || projects.length === 0) {
    return <div style={{ padding: 40, textAlign: "center", color: "#666" }}>Nenhum projeto disponível.</div>;
  }
  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Selecione um projeto</h2>
      <div style={styles.grid}>
        {projects.map((p) => (
          <div
            key={p.id}
            style={{ ...styles.card, ...(hover === p.id ? styles.cardHover : {}) }}
            onMouseEnter={() => setHover(p.id)}
            onMouseLeave={() => setHover(null)}
            onClick={() => onSelect(p.id)}
          >
            <h3 style={styles.name}>{p.name}</h3>
            <p style={styles.desc}>{p.description || "(sem descrição)"}</p>
            <div style={styles.stats}>
              <span style={styles.stat}>📍 {p.stats?.places || 0} lugares</span>
              <span style={styles.stat}>🔀 {p.stats?.transitions || 0} transições</span>
              <span style={styles.stat}>🤖 {p.stats?.agents || 0} agentes</span>
              <span style={styles.stat}>⚡ {p.stats?.tasks || 0} tasks</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectSelector;
