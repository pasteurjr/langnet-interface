// src/components/agents/AgentDebugPanel.tsx
import React, { useState } from "react";
import { Agent, AgentInternalState } from "../../types/agentChat";
import "./AgentDebugPanel.css";

interface AgentDebugPanelProps {
  selectedAgent?: Agent; // ✅ CORRIGIDO: aceita undefined
  agentInternalState?: AgentInternalState;
  onIntrospectionRequest: (
    agentId: string,
    type: "reasoning" | "memory" | "performance" | "context"
  ) => void;
}

const AgentDebugPanel: React.FC<AgentDebugPanelProps> = ({
  selectedAgent,
  agentInternalState,
  onIntrospectionRequest,
}) => {
  const [activeTab, setActiveTab] = useState<
    "overview" | "reasoning" | "memory" | "performance"
  >("overview");

  if (!selectedAgent) {
    return (
      <div className="agent-debug-panel">
        <div className="no-agent-selected">
          <p>Selecione um agente na tabela para ver informações de debug</p>
        </div>
      </div>
    );
  }

  const renderOverview = () => (
    <div className="debug-overview">
      <div className="agent-summary">
        <h4>{selectedAgent.name}</h4>
        <p className="agent-role">{selectedAgent.role}</p>
      </div>

      <div className="debug-stats">
        <div className="stat-item">
          <span className="stat-label">Status:</span>
          <span className={`stat-value status-${selectedAgent.status}`}>
            {selectedAgent.status}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Carga:</span>
          <span className="stat-value">{selectedAgent.load}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Fila:</span>
          <span className="stat-value">{selectedAgent.queue}</span>
        </div>
        {agentInternalState?.currentTask && (
          <div className="stat-item">
            <span className="stat-label">Tarefa Atual:</span>
            <span className="stat-value">{agentInternalState.currentTask}</span>
          </div>
        )}
      </div>

      <div className="introspection-controls">
        <h5>Introspecção:</h5>
        <div className="introspection-buttons">
          <button
            className="introspection-btn"
            onClick={() =>
              onIntrospectionRequest(selectedAgent.id, "reasoning")
            }
          >
            🧠 Raciocínio
          </button>
          <button
            className="introspection-btn"
            onClick={() => onIntrospectionRequest(selectedAgent.id, "memory")}
          >
            💾 Memória
          </button>
          <button
            className="introspection-btn"
            onClick={() =>
              onIntrospectionRequest(selectedAgent.id, "performance")
            }
          >
            📊 Performance
          </button>
          <button
            className="introspection-btn"
            onClick={() => onIntrospectionRequest(selectedAgent.id, "context")}
          >
            📋 Contexto
          </button>
        </div>
      </div>
    </div>
  );

  const renderReasoning = () => (
    <div className="reasoning-panel">
      <h5>Raciocínio do Agente</h5>
      {agentInternalState?.reasoningTrace &&
      agentInternalState.reasoningTrace.length > 0 ? (
        <div className="reasoning-trace">
          {agentInternalState.reasoningTrace.map((step, index) => (
            <div key={index} className="reasoning-step">
              <span className="step-number">{index + 1}</span>
              <span className="step-content">{step}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-data">Nenhum trace de raciocínio disponível</p>
      )}

      {agentInternalState?.lastDecision && (
        <div className="last-decision">
          <h6>Última Decisão:</h6>
          <p>{agentInternalState.lastDecision.description}</p>
          <span className="confidence">
            Confiança:{" "}
            {(agentInternalState.lastDecision.confidence * 100).toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );

  const renderMemory = () => (
    <div className="memory-panel">
      <h5>Estado da Memória</h5>
      {agentInternalState ? (
        <div className="memory-stats">
          <div className="memory-usage">
            <span className="memory-label">Uso de Memória:</span>
            <div className="memory-bar">
              <div
                className="memory-fill"
                style={{ width: `${agentInternalState.memoryUsage}%` }}
              />
            </div>
            <span className="memory-text">
              {agentInternalState.memoryUsage}%
            </span>
          </div>

          <div className="context-window">
            <span className="context-label">Janela de Contexto:</span>
            <div className="context-bar">
              <div
                className="context-fill"
                style={{
                  width: `${
                    (agentInternalState.contextWindow.used /
                      agentInternalState.contextWindow.total) *
                    100
                  }%`,
                }}
              />
            </div>
            <span className="context-text">
              {agentInternalState.contextWindow.used}/
              {agentInternalState.contextWindow.total}
            </span>
          </div>
        </div>
      ) : (
        <p className="no-data">Informações de memória não disponíveis</p>
      )}
    </div>
  );

  const renderPerformance = () => (
    <div className="performance-panel">
      <h5>Métricas de Performance</h5>
      {agentInternalState?.performance ? (
        <div className="performance-metrics">
          <div className="metric-grid">
            <div className="metric-item">
              <span className="metric-label">Taxa de Sucesso:</span>
              <span className="metric-value">
                {agentInternalState.performance.successRate.toFixed(1)}%
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Tempo Médio de Resposta:</span>
              <span className="metric-value">
                {agentInternalState.performance.avgResponseTime.toFixed(2)}s
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Tokens Utilizados:</span>
              <span className="metric-value">
                {agentInternalState.performance.tokensUsed.toLocaleString()}
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Requests/Hora:</span>
              <span className="metric-value">
                {agentInternalState.performance.requestsPerHour}
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Taxa de Erro:</span>
              <span className="metric-value">
                {agentInternalState.performance.errorRate.toFixed(2)}%
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Confiança Média:</span>
              <span className="metric-value">
                {(agentInternalState.performance.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      ) : (
        <p className="no-data">Métricas de performance não disponíveis</p>
      )}
    </div>
  );

  return (
    <div className="agent-debug-panel">
      <div className="debug-header">
        <h3>Debug & Introspecção</h3>
        <div className="debug-tabs">
          <button
            className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            Visão Geral
          </button>
          <button
            className={`tab-btn ${activeTab === "reasoning" ? "active" : ""}`}
            onClick={() => setActiveTab("reasoning")}
          >
            Raciocínio
          </button>
          <button
            className={`tab-btn ${activeTab === "memory" ? "active" : ""}`}
            onClick={() => setActiveTab("memory")}
          >
            Memória
          </button>
          <button
            className={`tab-btn ${activeTab === "performance" ? "active" : ""}`}
            onClick={() => setActiveTab("performance")}
          >
            Performance
          </button>
        </div>
      </div>

      <div className="debug-content">
        {activeTab === "overview" && renderOverview()}
        {activeTab === "reasoning" && renderReasoning()}
        {activeTab === "memory" && renderMemory()}
        {activeTab === "performance" && renderPerformance()}
      </div>
    </div>
  );
};

export default AgentDebugPanel;
