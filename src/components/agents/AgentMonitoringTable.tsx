// src/components/agents/AgentMonitoringTable.tsx
import React from "react";
import { Agent } from "../../types/agentChat";
import "./AgentMonitoringTable.css";

interface AgentMonitoringTableProps {
  agents: Agent[];
  selectedAgent?: Agent;
  onAgentSelect: (agent: Agent) => void;
  onAgentAction: (agentId: string, action: string) => void; // ✅ CORRIGIDO: aceita string genérico
}

const AgentMonitoringTable: React.FC<AgentMonitoringTableProps> = ({
  agents,
  selectedAgent,
  onAgentSelect,
  onAgentAction,
}) => {
  const getStatusIcon = (status: Agent["status"]) => {
    switch (status) {
      case "active":
        return "🟢";
      case "busy":
        return "🟡";
      case "error":
        return "🔴";
      case "inactive":
        return "⚫";
      default:
        return "⚪";
    }
  };

  const getStatusColor = (status: Agent["status"]) => {
    switch (status) {
      case "active":
        return "#22c55e";
      case "busy":
        return "#eab308";
      case "error":
        return "#ef4444";
      case "inactive":
        return "#6b7280";
      default:
        return "#9ca3af";
    }
  };

  const getLoadColor = (load: number) => {
    if (load < 50) return "#22c55e";
    if (load < 80) return "#eab308";
    return "#ef4444";
  };

  const formatLastActivity = (lastActivity: string) => {
    const date = new Date(lastActivity);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return "agora";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}min atrás`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h atrás`;
    return date.toLocaleDateString();
  };

  return (
    <div className="agent-monitoring-table">
      <div className="table-header">
        <h3>Monitoramento de Agentes</h3>
        <div className="table-controls">
          <span className="agent-count">{agents.length} agentes</span>
          <button className="refresh-btn" title="Atualizar">
            🔄
          </button>
        </div>
      </div>

      <div className="table-container">
        <table className="agents-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Agente</th>
              <th>Tipo</th>
              <th>Carga</th>
              <th>Fila</th>
              <th>Última Atividade</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {agents.map((agent) => (
              <tr
                key={agent.id}
                className={`agent-row ${
                  selectedAgent?.id === agent.id ? "selected" : ""
                }`}
                onClick={() => onAgentSelect(agent)}
              >
                <td className="status-cell">
                  <div className="status-indicator">
                    <span className="status-icon">
                      {getStatusIcon(agent.status)}
                    </span>
                    <span
                      className="status-text"
                      style={{ color: getStatusColor(agent.status) }}
                    >
                      {agent.status}
                    </span>
                  </div>
                </td>

                <td className="agent-cell">
                  <div className="agent-info">
                    <span className="agent-name">{agent.name}</span>
                    <span className="agent-role">{agent.role}</span>
                  </div>
                </td>

                <td className="type-cell">
                  <span className="agent-type">
                    {agent.type.replace("_", " ")}
                  </span>
                </td>

                <td className="load-cell">
                  <div className="load-indicator">
                    <div className="load-bar">
                      <div
                        className="load-fill"
                        style={{
                          width: `${agent.load}%`,
                          backgroundColor: getLoadColor(agent.load),
                        }}
                      />
                    </div>
                    <span className="load-text">{agent.load}%</span>
                  </div>
                </td>

                <td className="queue-cell">
                  <span
                    className={`queue-count ${agent.queue > 5 ? "high" : ""}`}
                  >
                    {agent.queue}
                  </span>
                </td>

                <td className="activity-cell">
                  <span className="last-activity">
                    {formatLastActivity(agent.lastActivity)}
                  </span>
                </td>

                <td className="actions-cell">
                  <div className="action-buttons">
                    <button
                      className="action-btn restart-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAgentAction(agent.id, "restart");
                      }}
                      title="Reiniciar"
                    >
                      🔄
                    </button>
                    <button
                      className="action-btn debug-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAgentAction(agent.id, "debug");
                      }}
                      title="Debug"
                    >
                      🐛
                    </button>
                    {agent.status === "active" ? (
                      <button
                        className="action-btn pause-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onAgentAction(agent.id, "pause");
                        }}
                        title="Pausar"
                      >
                        ⏸️
                      </button>
                    ) : (
                      <button
                        className="action-btn resume-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onAgentAction(agent.id, "resume");
                        }}
                        title="Retomar"
                      >
                        ▶️
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedAgent && (
        <div className="selected-agent-info">
          <h4>Agente Selecionado: {selectedAgent.name}</h4>
          <div className="agent-details">
            <div className="detail-item">
              <span className="detail-label">ID:</span>
              <span className="detail-value">{selectedAgent.id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Role:</span>
              <span className="detail-value">{selectedAgent.role}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Tipo:</span>
              <span className="detail-value">{selectedAgent.type}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status:</span>
              <span
                className="detail-value"
                style={{ color: getStatusColor(selectedAgent.status) }}
              >
                {selectedAgent.status}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentMonitoringTable;
