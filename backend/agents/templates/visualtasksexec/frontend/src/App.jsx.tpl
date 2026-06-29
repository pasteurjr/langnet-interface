import React, { useEffect, useState } from "react";
import ProjectSelector from "./components/ProjectSelector";
import MainExecutor from "./components/MainExecutor";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:{{BACKEND_PORT}}";

const styles = {
  app: { fontFamily: '-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif', minHeight: "100vh", background: "#f5f7fa" },
  header: { background: "#1976d2", color: "white", padding: "16px 32px", display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { margin: 0, fontSize: 20 },
  badge: { background: "rgba(255,255,255,0.2)", padding: "4px 12px", borderRadius: 12, fontSize: 12 },
  body: { padding: 24, maxWidth: 1400, margin: "0 auto" },
  loading: { padding: 40, textAlign: "center", color: "#666" },
  error: { padding: 16, background: "#ffebee", color: "#c62828", borderRadius: 4, marginBottom: 16 },
};

function App() {
  const [projects, setProjects] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/projects`)
      .then((r) => r.json())
      .then((d) => {
        setProjects(d.projects || []);
        if ((d.projects || []).length === 1) {
          loadProject(d.projects[0].id);
        }
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadProject = (id) => {
    setLoading(true);
    fetch(`${BACKEND_URL}/api/projects/${id}`)
      .then((r) => r.json())
      .then((d) => {
        setSelected(d.project);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  };

  return (
    <div style={styles.app}>
      <div style={styles.header}>
        <h1 style={styles.title}>🌐 {{PROJECT_NAME}} — Visual Task Execution</h1>
        <span style={styles.badge}>v1.0</span>
      </div>
      <div style={styles.body}>
        {error && <div style={styles.error}>⚠ {error}</div>}
        {loading && <div style={styles.loading}>Carregando…</div>}
        {!loading && !selected && (
          <ProjectSelector projects={projects} onSelect={loadProject} />
        )}
        {!loading && selected && (
          <MainExecutor project={selected} onBack={() => setSelected(null)} />
        )}
      </div>
    </div>
  );
}

export default App;
