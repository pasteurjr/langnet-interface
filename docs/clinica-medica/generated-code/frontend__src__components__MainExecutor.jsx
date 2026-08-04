import React, { useState } from "react";
import usePetriNetExecution from "../hooks/usePetriNetExecution";
import OperacaoTab from "./tabs/OperacaoTab";
import ExecucaoTab from "./tabs/ExecucaoTab";
import InputsTab from "./tabs/InputsTab";
import OutputsTab from "./tabs/OutputsTab";
import LogsTab from "./tabs/LogsTab";

const styles = {
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 },
  backBtn: { background: "transparent", border: "1px solid #ccc", padding: "6px 12px", borderRadius: 4, cursor: "pointer" },
  pjName: { margin: 0, fontSize: 22 },
  pjMeta: { color: "#666", fontSize: 13 },
  tabsBar: { display: "flex", borderBottom: "2px solid #e0e0e0", marginBottom: 16 },
  tab: (active) => ({
    padding: "10px 18px",
    border: "none",
    background: "transparent",
    borderBottom: active ? "3px solid #1976d2" : "3px solid transparent",
    color: active ? "#1976d2" : "#555",
    fontWeight: active ? 700 : 500,
    cursor: "pointer",
    fontSize: 14,
  }),
  panel: { background: "white", padding: 20, borderRadius: 8, minHeight: 400 },
};

const TABS = [
  { id: "execucao", label: "🚀 Execução", Component: ExecucaoTab },
  { id: "operacao", label: "⚙ Operação", Component: OperacaoTab },
  { id: "inputs", label: "📥 Inputs", Component: InputsTab },
  { id: "outputs", label: "📤 Outputs", Component: OutputsTab },
  { id: "logs", label: "📋 Logs", Component: LogsTab },
];

const MainExecutor = ({ project, onBack }) => {
  const [active, setActive] = useState("execucao");
  const exec = usePetriNetExecution(project);

  const Tab = TABS.find((t) => t.id === active)?.Component || ExecucaoTab;

  return (
    <div>
      <div style={styles.header}>
        <div>
          <button style={styles.backBtn} onClick={onBack}>← projetos</button>
        </div>
        <div style={{ textAlign: "right" }}>
          <h2 style={styles.pjName}>{project.name}</h2>
          <div style={styles.pjMeta}>
            {project.petriNet?.lugares?.length || 0} lugares · {project.petriNet?.transicoes?.length || 0} transições · {project.agents?.length || 0} agentes
          </div>
        </div>
      </div>

      <div style={styles.tabsBar}>
        {TABS.map((t) => (
          <button key={t.id} style={styles.tab(active === t.id)} onClick={() => setActive(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      <div style={styles.panel}>
        <Tab project={project} exec={exec} />
      </div>
    </div>
  );
};

export default MainExecutor;
