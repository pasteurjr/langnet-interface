// src/components/agents/InterventionControls.tsx
import React, { useState } from "react";
import { PetriNetState } from "../../types/agentChat";
import "./InterventionControls.css";

interface InterventionControlsProps {
  petriNetState: PetriNetState;
  onEmergencyStop: () => void;
  onPauseSystem: () => void;
  onRestartSystem: () => void;
  onManualIntervention: (action: string, data?: any) => void;
  onSystemTuning: (action: string, params: any) => void;
}

const InterventionControls: React.FC<InterventionControlsProps> = ({
  petriNetState,
  onEmergencyStop,
  onPauseSystem,
  onRestartSystem,
  onManualIntervention,
  onSystemTuning,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [manualMode, setManualMode] = useState(false);

  const handleEmergencyAction = (action: string) => {
    const confirmed = window.confirm(
      `Tem certeza que deseja ${action}? Esta ação afetará todo o sistema.`
    );
    if (confirmed) {
      switch (action) {
        case "stop":
          onEmergencyStop();
          break;
        case "pause":
          onPauseSystem();
          break;
        case "restart":
          onRestartSystem();
          break;
      }
    }
  };

  const handleManualIntervention = (action: string) => {
    switch (action) {
      case "override":
        const decision = prompt("Digite a decisão override:");
        if (decision) {
          onManualIntervention("override_decision", { decision });
        }
        break;
      case "route":
        const route = prompt("Digite a rota forçada (ex: technical_support):");
        if (route) {
          onManualIntervention("force_route", { route });
        }
        break;
      case "inject":
        const message = prompt("Digite a mensagem para injetar:");
        if (message) {
          onManualIntervention("inject_message", { message });
        }
        break;
      case "priority":
        onManualIntervention("priority_queue", {});
        break;
    }
  };

  const handleSystemTuning = (action: string) => {
    switch (action) {
      case "load_balance":
        onSystemTuning("load_balance", {});
        break;
      case "adjust_params":
        setShowAdvanced(true);
        break;
      case "ab_test":
        const variant = prompt("Digite a variante do teste A/B:");
        if (variant) {
          onSystemTuning("ab_test", { variant });
        }
        break;
      case "experiment":
        setManualMode(!manualMode);
        break;
    }
  };

  return (
    <div className="intervention-controls">
      <div className="controls-header">
        <h3>Controles de Intervenção</h3>
        <div className="manual-mode-toggle">
          <label>
            <input
              type="checkbox"
              checked={manualMode}
              onChange={(e) => setManualMode(e.target.checked)}
            />
            Modo Manual
          </label>
        </div>
      </div>

      {/* Emergency Controls */}
      <div className="control-section emergency-section">
        <h4>🚨 Controles de Emergência</h4>
        <div className="emergency-buttons">
          <button
            className="emergency-btn stop-btn"
            onClick={() => handleEmergencyAction("stop")}
          >
            🛑 Parar Tudo
          </button>
          <button
            className="emergency-btn pause-btn"
            onClick={() => handleEmergencyAction("pause")}
          >
            ⏸️ Pausar Sistema
          </button>
          <button
            className="emergency-btn restart-btn"
            onClick={() => handleEmergencyAction("restart")}
          >
            🔄 Reiniciar
          </button>
        </div>
      </div>

      {/* Manual Intervention */}
      <div className="control-section intervention-section">
        <h4>✋ Intervenção Manual</h4>
        <div className="intervention-buttons">
          <button
            className="intervention-btn"
            onClick={() => handleManualIntervention("override")}
            disabled={!manualMode}
          >
            📝 Override Decisão
          </button>
          <button
            className="intervention-btn"
            onClick={() => handleManualIntervention("route")}
            disabled={!manualMode}
          >
            🎯 Forçar Rota
          </button>
          <button
            className="intervention-btn"
            onClick={() => handleManualIntervention("inject")}
            disabled={!manualMode}
          >
            💬 Injetar Mensagem
          </button>
          <button
            className="intervention-btn"
            onClick={() => handleManualIntervention("priority")}
            disabled={!manualMode}
          >
            ⚡ Fila Prioritária
          </button>
        </div>
      </div>

      {/* System Tuning */}
      <div className="control-section tuning-section">
        <h4>🔧 Ajuste do Sistema</h4>
        <div className="tuning-buttons">
          <button
            className="tuning-btn"
            onClick={() => handleSystemTuning("load_balance")}
          >
            ⚖️ Balancear Carga
          </button>
          <button
            className="tuning-btn"
            onClick={() => handleSystemTuning("adjust_params")}
          >
            🎛️ Ajustar Parâmetros
          </button>
          <button
            className="tuning-btn"
            onClick={() => handleSystemTuning("ab_test")}
          >
            📊 Teste A/B
          </button>
          <button
            className="tuning-btn"
            onClick={() => handleSystemTuning("experiment")}
          >
            🧪 Modo Experimental
          </button>
        </div>
      </div>

      {/* System Status & Network State */}
      <div className="control-section status-section">
        <h4>📊 Estado da Rede de Petri</h4>
        <div className="network-status">
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Estado Atual:</span>
              <span className="status-value">{petriNetState.currentState}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Transições Ativas:</span>
              <span className="status-value">
                {petriNetState.activeTransitions}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Local Atual:</span>
              <span className="status-value">{petriNetState.currentPlace}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Tokens:</span>
              <span className="status-value">{petriNetState.tokens}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Próxima Transição:</span>
              <span className="status-value">
                {petriNetState.nextTransition || "N/A"}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Taxa de Fluxo:</span>
              <span className="status-value">
                {petriNetState.flowRate} req/min
              </span>
            </div>
          </div>

          {petriNetState.bottlenecks.length > 0 && (
            <div className="bottlenecks">
              <h5>⚠️ Gargalos Detectados:</h5>
              <ul>
                {petriNetState.bottlenecks.map((bottleneck, index) => (
                  <li key={index}>{bottleneck}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Parameters Modal */}
      {showAdvanced && (
        <div className="modal-overlay" onClick={() => setShowAdvanced(false)}>
          <div
            className="advanced-params-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h3>Ajustar Parâmetros do Sistema</h3>
              <button
                className="btn-close"
                onClick={() => setShowAdvanced(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-content">
              <div className="param-group">
                <label>Timeout (ms):</label>
                <input
                  type="number"
                  defaultValue={30000}
                  min={1000}
                  max={120000}
                />
              </div>
              <div className="param-group">
                <label>Max Workers:</label>
                <input type="number" defaultValue={4} min={1} max={20} />
              </div>
              <div className="param-group">
                <label>Queue Size:</label>
                <input type="number" defaultValue={100} min={10} max={1000} />
              </div>
              <div className="param-group">
                <label>Retry Attempts:</label>
                <input type="number" defaultValue={3} min={1} max={10} />
              </div>
              <div className="param-group">
                <label>Temperature:</label>
                <input
                  type="number"
                  defaultValue={0.3}
                  min={0}
                  max={1}
                  step={0.1}
                />
              </div>
            </div>
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => setShowAdvanced(false)}
              >
                Cancelar
              </button>
              <button
                className="btn-primary"
                onClick={() => {
                  onSystemTuning("apply_params", {});
                  setShowAdvanced(false);
                }}
              >
                Aplicar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InterventionControls;
