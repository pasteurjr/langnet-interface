/* src/components/code/ExecutionConsole.tsx */
import React from 'react';
import { ExecutionLogEntry, PetriNetExecutionState } from '../../types/codeGeneration';

interface ExecutionConsoleProps {
  logs: ExecutionLogEntry[];
  isExecuting: boolean;
  petriNetState: PetriNetExecutionState;
}

const ExecutionConsole: React.FC<ExecutionConsoleProps> = ({
  logs,
  isExecuting,
  petriNetState
}) => {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getLogIcon = (source: string) => {
    switch (source) {
      case 'system': return '⚙️';
      case 'agent': return '🤖';
      case 'task': return '📋';
      case 'petri_net': return '🔄';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="execution-console">
      <div className="console-header">
        <h4>🖥️ Console de Execução</h4>
        <div className="console-controls">
          <button className="console-button clear">
            🗑️ Limpar
          </button>
          {isExecuting ? (
            <button className="console-button stop">
              ⏹️ Parar
            </button>
          ) : (
            <button className="console-button start">
              ▶️ Executar
            </button>
          )}
        </div>
      </div>
      
      <div className="code-terminal">
        <div className="terminal-output">
          {logs.map((log, index) => (
            <div key={index} className={`terminal-line ${log.level}`}>
              <span className="terminal-time">[{formatTimestamp(log.timestamp)}]</span>
              <span className="terminal-source">{getLogIcon(log.source)}</span>
              <span className="terminal-message">{log.message}</span>
            </div>
          ))}
          {isExecuting && (
            <div className="terminal-line info">
              <span className="terminal-cursor">▋</span>
              <span className="terminal-message">Executando...</span>
            </div>
          )}
        </div>
      </div>

      <div className="petri-net-state">
        <div className="state-header">🔄 Estado da Rede de Petri</div>
        <div className="places-tokens">
          {Object.entries(petriNetState.currentPlaces).map(([place, tokens]) => (
            <div key={place} className="place-token">
              <div className="place-name">{place}</div>
              <div className="token-count">{tokens}</div>
            </div>
          ))}
        </div>
        <div className="enabled-transitions">
          <strong>Transições Habilitadas:</strong>
          <div className="transition-list">
            {petriNetState.enabledTransitions.map(transition => (
              <span key={transition} className="transition-item">
                {transition}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default ExecutionConsole;