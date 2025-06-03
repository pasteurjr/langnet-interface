// src/components/agents/AgentPerformanceDashboard.tsx
import React from "react";
import { SystemStatus } from "../../types/agentChat";
import "./AgentPerformanceDashboard.css";

interface AgentPerformanceDashboardProps {
  systemStatus: SystemStatus;
  onRefresh: () => void;
}

const AgentPerformanceDashboard: React.FC<AgentPerformanceDashboardProps> = ({
  systemStatus,
  onRefresh,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "#22c55e";
      case "warning":
        return "#eab308";
      case "error":
        return "#ef4444";
      default:
        return "#6b7280";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return "🟢";
      case "warning":
        return "🟡";
      case "error":
        return "🔴";
      default:
        return "⚪";
    }
  };

  return (
    <div className="performance-dashboard">
      <div className="dashboard-header">
        <h3>Performance Dashboard</h3>
        <div className="dashboard-controls">
          <span className="real-time-indicator">
            <span className="indicator-dot"></span>
            Tempo Real
          </span>
          <button className="refresh-btn" onClick={onRefresh} title="Atualizar">
            🔄
          </button>
        </div>
      </div>

      <div className="status-overview">
        <div
          className="status-indicator"
          style={{ backgroundColor: getStatusColor(systemStatus.overall) }}
        >
          <span className="status-icon">
            {getStatusIcon(systemStatus.overall)}
          </span>
          <span className="status-text">
            Sistema{" "}
            {systemStatus.overall === "healthy"
              ? "Saudável"
              : systemStatus.overall === "warning"
              ? "Atenção"
              : "Erro"}
          </span>
        </div>
        <div className="uptime">Uptime: {systemStatus.uptime}</div>
      </div>

      <div className="metrics-grid">
        <div className="metric-item">
          <div className="metric-icon">👥</div>
          <div className="metric-content">
            <div className="metric-value">{systemStatus.activeSessions}</div>
            <div className="metric-label">Sessões Ativas</div>
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-icon">📋</div>
          <div className="metric-content">
            <div className="metric-value">{systemStatus.queueDepth}</div>
            <div className="metric-label">Fila</div>
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-icon">⚡</div>
          <div className="metric-content">
            <div className="metric-value">{systemStatus.avgResponseTime}s</div>
            <div className="metric-label">Resp. Média</div>
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <div className="metric-value">{systemStatus.successRate}%</div>
            <div className="metric-label">Taxa Sucesso</div>
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-icon">🪙</div>
          <div className="metric-content">
            <div className="metric-value">{systemStatus.tokenUsage}K</div>
            <div className="metric-label">Tokens</div>
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-value">${systemStatus.costPerHour}</div>
            <div className="metric-label">/hora</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentPerformanceDashboard;
