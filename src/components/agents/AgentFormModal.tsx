// src/components/agents/AgentFormModal.tsx
import React, { useState, useEffect } from 'react';
import { Agent } from '../../types';
import './AgentFormModal.css';

interface AgentFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (agent: Partial<Agent>) => void;
  agent: Agent | null;
}

const AgentFormModal: React.FC<AgentFormModalProps> = ({
  isOpen,
  onClose,
  onSave,
  agent
}) => {
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    goal: '',
    backstory: '',
    tools: [] as string[],
    verbose: true,
    allow_delegation: false,
    allow_code_execution: false,
    max_iter: 25,
    max_rpm: 15
  });

  const [newTool, setNewTool] = useState('');

  // Lista de ferramentas disponíveis (exemplo)
  const availableTools = [
    'knowledge_base_tool',
    'ticket_creation_tool',
    'customer_history_tool',
    'diagnostic_tool',
    'remote_access_tool',
    'analytics_tool',
    'communication_tool',
    'database_query_tool',
    'file_manager_tool',
    'api_integration_tool'
  ];

  useEffect(() => {
    if (agent) {
      setFormData({
        name: agent.name,
        role: agent.role,
        goal: agent.goal,
        backstory: agent.backstory,
        tools: agent.tools,
        verbose: agent.verbose,
        allow_delegation: agent.allow_delegation,
        allow_code_execution: agent.allow_code_execution || false,
        max_iter: agent.max_iter || 25,
        max_rpm: agent.max_rpm || 15
      });
    } else {
      // Reset form for new agent
      setFormData({
        name: '',
        role: '',
        goal: '',
        backstory: '',
        tools: [],
        verbose: true,
        allow_delegation: false,
        allow_code_execution: false,
        max_iter: 25,
        max_rpm: 15
      });
    }
  }, [agent]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      setFormData(prev => ({ ...prev, [name]: parseInt(value) || 0 }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleAddTool = () => {
    if (newTool && !formData.tools.includes(newTool)) {
      setFormData(prev => ({ ...prev, tools: [...prev.tools, newTool] }));
      setNewTool('');
    }
  };

  const handleRemoveTool = (tool: string) => {
    setFormData(prev => ({ 
      ...prev, 
      tools: prev.tools.filter(t => t !== tool) 
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validação básica
    if (!formData.name || !formData.role || !formData.goal || !formData.backstory) {
      alert('Por favor, preencha todos os campos obrigatórios');
      return;
    }

    onSave(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="agent-form-modal">
        <div className="modal-header">
          <h2>{agent ? 'EDITAR AGENTE' : 'CRIAR NOVO AGENTE'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h3>Informações Básicas</h3>
            
            <div className="form-group">
              <label htmlFor="name">Nome do Agente*</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="ex: customer_service_agent"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="role">Role (Função)*</label>
              <textarea
                id="role"
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                placeholder="Descreva a função principal do agente"
                rows={3}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="goal">Goal (Objetivo)*</label>
              <textarea
                id="goal"
                name="goal"
                value={formData.goal}
                onChange={handleInputChange}
                placeholder="Qual é o objetivo principal deste agente?"
                rows={3}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="backstory">Backstory (História)*</label>
              <textarea
                id="backstory"
                name="backstory"
                value={formData.backstory}
                onChange={handleInputChange}
                placeholder="Contexto e experiência do agente"
                rows={4}
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Ferramentas</h3>
            
            <div className="tools-manager">
              <div className="tool-input-group">
                <select
                  value={newTool}
                  onChange={(e) => setNewTool(e.target.value)}
                >
                  <option value="">Selecione uma ferramenta</option>
                  {availableTools
                    .filter(tool => !formData.tools.includes(tool))
                    .map(tool => (
                      <option key={tool} value={tool}>{tool}</option>
                    ))
                  }
                </select>
                <button type="button" onClick={handleAddTool}>
                  + Adicionar
                </button>
              </div>

              <div className="selected-tools">
                {formData.tools.map(tool => (
                  <div key={tool} className="tool-item">
                    <span>{tool}</span>
                    <button 
                      type="button" 
                      onClick={() => handleRemoveTool(tool)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Configurações</h3>
            
            <div className="config-grid">
              <div className="form-group-checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="verbose"
                    checked={formData.verbose}
                    onChange={handleInputChange}
                  />
                  Verbose (Modo detalhado)
                </label>
              </div>

              <div className="form-group-checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="allow_delegation"
                    checked={formData.allow_delegation}
                    onChange={handleInputChange}
                  />
                  Permitir Delegação
                </label>
              </div>

              <div className="form-group-checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="allow_code_execution"
                    checked={formData.allow_code_execution}
                    onChange={handleInputChange}
                  />
                  Permitir Execução de Código
                </label>
              </div>

              <div className="form-group-number">
                <label htmlFor="max_iter">Max Iterações</label>
                <input
                  type="number"
                  id="max_iter"
                  name="max_iter"
                  value={formData.max_iter}
                  onChange={handleInputChange}
                  min="1"
                  max="100"
                />
              </div>

              <div className="form-group-number">
                <label htmlFor="max_rpm">Max RPM</label>
                <input
                  type="number"
                  id="max_rpm"
                  name="max_rpm"
                  value={formData.max_rpm}
                  onChange={handleInputChange}
                  min="1"
                  max="60"
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-save">
              {agent ? 'Salvar Alterações' : 'Criar Agente'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AgentFormModal;