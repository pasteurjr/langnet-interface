// src/components/agents/AgentCard.tsx
import React from 'react';
import { Agent, AgentStatus } from '../../types';
import './AgentCard.css';

interface AgentCardProps {
  agent: Agent;
  onEdit: (agent: Agent) => void;
  onDelete: (agentId: string) => void;
  onToggleStatus: (agentId: string) => void;
}

const AgentCard: React.FC<AgentCardProps> = ({ 
  agent, 
  onEdit, 
  onDelete, 
  onToggleStatus 
}) => {
  const getStatusClass = (status: AgentStatus) => {
    switch (status) {
      case AgentStatus.ACTIVE:
        return 'status-active';
      case AgentStatus.INACTIVE:
        return 'status-inactive';
      case AgentStatus.DRAFT:
        return 'status-draft';
      default:
        return '';
    }
  };

  const getStatusLabel = (status: AgentStatus) => {
    switch (status) {
      case AgentStatus.ACTIVE:
        return 'Ativo';
      case AgentStatus.INACTIVE:
        return 'Inativo';
      case AgentStatus.DRAFT:
        return 'Rascunho';
      default:
        return '';
    }
  };

  return (
    <div className="agent-card">
      <div className="agent-card-header">
        <h3 className="agent-name">{agent.name}</h3>
        <span className={`agent-status ${getStatusClass(agent.status)}`}>
          {getStatusLabel(agent.status)}
        </span>
      </div>
      
      <div className="agent-card-content">
        <div className="agent-field">
          <label>Role:</label>
          <p>{agent.role}</p>
        </div>
        
        <div className="agent-field">
          <label>Goal:</label>
          <p>{agent.goal}</p>
        </div>
        
        <div className="agent-field">
          <label>Tools:</label>
          <div className="agent-tools">
            {agent.tools.map((tool, index) => (
              <span key={index} className="tool-badge">{tool}</span>
            ))}
          </div>
        </div>
        
        <div className="agent-properties">
          {agent.verbose && <span className="property-badge">Verbose</span>}
          {agent.allow_delegation && <span className="property-badge">Delegation</span>}
          {agent.allow_code_execution && <span className="property-badge">Code Exec</span>}
        </div>
      </div>
      
      <div className="agent-card-footer">
        <button 
          className="btn-toggle-status"
          onClick={() => onToggleStatus(agent.id)}
        >
          {agent.status === AgentStatus.ACTIVE ? '⏸️' : '▶️'}
        </button>
        <button className="btn-edit" onClick={() => onEdit(agent)}>
          ✏️ Editar
        </button>
        <button className="btn-delete" onClick={() => onDelete(agent.id)}>
          🗑️ Excluir
        </button>
      </div>
    </div>
  );
};

export default AgentCard;