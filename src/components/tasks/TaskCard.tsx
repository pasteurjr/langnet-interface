// src/components/tasks/TaskCard.tsx
import React from 'react';
import { Task, TaskStatus, Agent } from '../../types';
import './TaskCard.css';

interface TaskCardProps {
  task: Task;
  agent?: Agent;
  allTasks: Task[];
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onToggleStatus: (taskId: string) => void;
  onDuplicate: (taskId: string) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ 
  task, 
  agent,
  allTasks,
  onEdit, 
  onDelete, 
  onToggleStatus,
  onDuplicate
}) => {
  const getStatusClass = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.ACTIVE:
        return 'status-active';
      case TaskStatus.INACTIVE:
        return 'status-inactive';
      case TaskStatus.DRAFT:
        return 'status-draft';
      default:
        return '';
    }
  };

  const getStatusLabel = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.ACTIVE:
        return 'Ativa';
      case TaskStatus.INACTIVE:
        return 'Inativa';
      case TaskStatus.DRAFT:
        return 'Rascunho';
      default:
        return '';
    }
  };

  const getContextTasks = () => {
    return task.context.map(contextId => 
      allTasks.find(t => t.id === contextId)?.name || contextId
    );
  };

  return (
    <div className="task-card">
      <div className="task-card-header">
        <h3 className="task-name">{task.name}</h3>
        <span className={`task-status ${getStatusClass(task.status)}`}>
          {getStatusLabel(task.status)}
        </span>
      </div>
      
      <div className="task-card-content">
        <div className="task-field">
          <label>Descrição:</label>
          <p>{task.description}</p>
        </div>
        
        <div className="task-field">
          <label>Saída Esperada:</label>
          <p>{task.expected_output}</p>
        </div>
        
        <div className="task-field">
          <label>Agente Responsável:</label>
          <p className="agent-name">{agent?.name || 'Não atribuído'}</p>
        </div>

        {task.context.length > 0 && (
          <div className="task-field">
            <label>Contexto:</label>
            <div className="context-list">
              {getContextTasks().map((contextTask, index) => (
                <span key={index} className="context-badge">{contextTask}</span>
              ))}
            </div>
          </div>
        )}
        
        {task.tools.length > 0 && (
          <div className="task-field">
            <label>Ferramentas:</label>
            <div className="task-tools">
              {task.tools.map((tool, index) => (
                <span key={index} className="tool-badge">{tool}</span>
              ))}
            </div>
          </div>
        )}
        
        <div className="task-properties">
          {task.human_input && <span className="property-badge">👤 Input Humano</span>}
          {task.async_execution && <span className="property-badge">⚡ Assíncrono</span>}
          {task.output_json && <span className="property-badge">📄 JSON</span>}
          {task.output_file && <span className="property-badge">💾 Arquivo</span>}
        </div>
      </div>
      
      <div className="task-card-footer">
        <button 
          className="btn-toggle-status"
          onClick={() => onToggleStatus(task.id)}
          title={task.status === TaskStatus.ACTIVE ? 'Desativar' : 'Ativar'}
        >
          {task.status === TaskStatus.ACTIVE ? '⏸️' : '▶️'}
        </button>
        <button 
          className="btn-duplicate" 
          onClick={() => onDuplicate(task.id)}
          title="Duplicar tarefa"
        >
          📋
        </button>
        <button 
          className="btn-edit" 
          onClick={() => onEdit(task)}
          title="Editar tarefa"
        >
          ✏️
        </button>
        <button 
          className="btn-delete" 
          onClick={() => onDelete(task.id)}
          title="Excluir tarefa"
        >
          🗑️
        </button>
      </div>
    </div>
  );
};

export default TaskCard;