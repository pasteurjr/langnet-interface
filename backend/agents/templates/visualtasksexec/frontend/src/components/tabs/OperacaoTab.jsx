import React, { useState } from "react";

const styles = {
  form: { background: "#fafafa", padding: 16, borderRadius: 6, marginBottom: 16 },
  input: { width: "100%", padding: 8, marginTop: 4, border: "1px solid #ccc", borderRadius: 4, fontFamily: "monospace", fontSize: 12 },
  label: { fontSize: 12, color: "#555" },
  btn: { background: "#1976d2", color: "white", border: "none", padding: "8px 16px", borderRadius: 4, cursor: "pointer", marginTop: 8 },
  result: { background: "#f5f9fc", padding: 12, borderRadius: 4, fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap", maxHeight: 400, overflow: "auto" },
  err: { color: "#c62828", marginTop: 8 },
};

const OperacaoTab = ({ project, exec }) => {
  const tasks = project.tasks || [];
  const [taskName, setTaskName] = useState((tasks[0] || {}).name || "");
  const [inputJson, setInputJson] = useState("{}");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);

  const fire = async () => {
    setBusy(true);
    setErr(null);
    setResult(null);
    try {
      const input = JSON.parse(inputJson || "{}");
      const res = await exec.runTask(taskName, input);
      setResult(res);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Disparar task manualmente</h3>
      <div style={styles.form}>
        <label style={styles.label}>
          Task
          <select style={styles.input} value={taskName} onChange={(e) => setTaskName(e.target.value)}>
            {tasks.map((t) => (
              <option key={t.name || t.id} value={t.name || t.id}>{t.name || t.id}</option>
            ))}
          </select>
        </label>
        <label style={{ ...styles.label, display: "block", marginTop: 12 }}>
          Input JSON
          <textarea style={{ ...styles.input, minHeight: 120 }} value={inputJson} onChange={(e) => setInputJson(e.target.value)} />
        </label>
        <button style={styles.btn} disabled={busy} onClick={fire}>{busy ? "Executando..." : "▶ Executar"}</button>
        {err && <div style={styles.err}>⚠ {err}</div>}
      </div>

      {result && (
        <div>
          <h4>Resultado</h4>
          <div style={styles.result}>{JSON.stringify(result, null, 2)}</div>
        </div>
      )}
    </div>
  );
};

export default OperacaoTab;
