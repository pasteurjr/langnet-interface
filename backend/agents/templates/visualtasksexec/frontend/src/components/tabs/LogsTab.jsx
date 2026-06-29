import React from "react";

const styles = {
  log: { fontFamily: "monospace", fontSize: 12, background: "#0d1117", color: "#c9d1d9", padding: 12, borderRadius: 6, maxHeight: 500, overflow: "auto" },
  line: { padding: "2px 0", borderBottom: "1px solid #21262d" },
  ts: { color: "#7d8590" },
  tag: (kind) => {
    const colors = {
      transition_fired: "#79c0ff",
      place_start: "#d2a8ff",
      place_done: "#7ee787",
      place_error: "#ff7b72",
      manual_task_start: "#d2a8ff",
      manual_task_done: "#7ee787",
      manual_task_error: "#ff7b72",
      run_started: "#79c0ff",
      run_finished: "#7ee787",
      no_transitions: "#ffa657",
    };
    return { color: colors[kind] || "#c9d1d9", fontWeight: 700, margin: "0 8px" };
  },
};

const LogsTab = ({ exec }) => {
  if (!exec.events || exec.events.length === 0) {
    return <p style={{ color: "#666" }}>Sem eventos ainda.</p>;
  }
  return (
    <div>
      <h3 style={{ marginTop: 0 }}>Eventos ({exec.events.length})</h3>
      <div style={styles.log}>
        {exec.events.map((e, i) => (
          <div key={i} style={styles.line}>
            <span style={styles.ts}>{new Date(e.ts).toLocaleTimeString()}</span>
            <span style={styles.tag(e.type)}>[{e.type}]</span>
            {e.place && <span>{e.place}</span>}
            {e.task_name && <span style={{ color: "#a5d6ff" }}> {e.task_name}</span>}
            {e.data && <span style={{ color: "#8b949e" }}> {JSON.stringify(e.data).slice(0, 200)}</span>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogsTab;
