// src/components/tasks/TaskFormModal.tsx
import React, { useState, useEffect } from 'react';
import { Task, Agent } from '../../types';
import './TaskFormModal.css';

interface TaskFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (task: Partial<Task>) => void;
  task: Task | null;
  agents: Agent[];
  tasks: Task[];
}

const TaskFormModal: React.FC<TaskFormModalProps> = ({
  isOpen,
  onClose,
  onSave,
  task,
  agents,
  tasks
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    expected_output: '',
    agent: '',
    context: [] as string[],
    tools: [] as string[],
    human_input: false,
    async_execution: false,
    output_json: '',
    output_file: ''
  });

  const [newTool, setNewTool] = useState('');

  // Lista de ferramentas disponíveis
  const availableTools = [
    'TextAnalysisTool',
    'ClassificationModel',
    'SentimentAnalyzer',
    'EmotionDetector',
    'DataExtractorTool',
    'APIIntegrationTool',
    'FileProcessorTool',
    'EmailSenderTool',
    'DatabaseQueryTool',
    'ReportGeneratorTool',
    'TranslationTool',
    'SummarizerTool'
  ];

  useEffect(() => {
    if (task) {
      setFormData({
        name: task.name,
        description: task.description,
        expected_output: task.expected_output,
        agent: task.agent,
        context: task.context,
        tools: task.tools,
        human_input: task.human_input,
        async_execution: task.async_execution,
        output_json: task.output_json || '',
        output_file: task.output_file || ''
      });
    } else {
      // Reset form for new task
      setFormData({
        name: '',
        description: '',
        expected_output: '',
        agent: '',
        context: [],
        tools: [],
        human_input: false,
        async_execution: false,
        output_json: '',
        output_file: ''
      });
    }
  }, [task]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
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

  const handleAddContext = (taskId: string) => {
    if (taskId && !formData.context.includes(taskId)) {
      setFormData(prev => ({ ...prev, context: [...prev.context, taskId] }));
    }
  };

  const handleRemoveContext = (taskId: string) => {
    setFormData(prev => ({ 
      ...prev, 
      context: prev.context.filter(t => t !== taskId) 
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validação básica
    if (!formData.name || !formData.description || !formData.expected_output || !formData.agent) {
      alert('Por favor, preencha todos os campos obrigatórios');
      return;
    }

    onSave(formData);
  };

  // Filtrar tarefas disponíveis para contexto (não pode incluir a própria tarefa)
  const availableContextTasks = tasks.filter(t => 
    t.id !== task?.id && !formData.context.includes(t.id)
  );

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="task-form-modal">
        <div className="modal-header">
          <h2>{task ? 'EDITAR TAREFA' : 'CRIAR NOVA TAREFA'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-section">
              <h3>Informações Básicas</h3>
              
              <div className="form-group">
                <label htmlFor="name">Nome da Tarefa*</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="ex: process_customer_query_task"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Descrição*</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Descreva o que esta tarefa deve fazer"
                  rows={3}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="expected_output">Saída Esperada*</label>
                <textarea
                  id="expected_output"
                  name="expected_output"
                  value={formData.expected_output}
                  onChange={handleInputChange}
                  placeholder="Descreva o resultado esperado desta tarefa"
                  rows={3}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="agent">Agente Responsável*</label>
                <select
                  id="agent"
                  name="agent"
                  value={formData.agent}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Selecione um agente</option>
                  {agents.map(agent => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name} - {agent.role}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-section">
              <h3>Contexto e Dependências</h3>
              
              <div className="context-manager">
                <label>Tarefas de Contexto</label>
                <p className="help-text">Selecione tarefas cujos resultados serão usados como contexto</p>
                
                <select
                  onChange={(e) => {
                    if (e.target.value) {
                      handleAddContext(e.target.value);
                      e.target.value = '';
                    }
                  }}
                >
                  <option value="">Adicionar tarefa ao contexto</option>
                  {availableContextTasks.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>

                <div className="selected-contexts">
                  {formData.context.map(contextId => {
                    const contextTask = tasks.find(t => t.id === contextId);
                    return (
                      <div key={contextId} className="context-item">
                        <span>{contextTask?.name || contextId}</span>
                        <button 
                          type="button" 
                          onClick={() => handleRemoveContext(contextId)}
                        >
                          ×
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

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
          </div>

          <div className="form-section">
            <h3>Configurações de Execução</h3>
            
            <div className="config-grid">
              <div className="form-group-checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="human_input"
                    checked={formData.human_input}
                    onChange={handleInputChange}
                  />
                  Requer Input Humano
                </label>
                <p className="help-text">A tarefa pausará para receber entrada do usuário</p>
              </div>

              <div className="form-group-checkbox">
                <label>
                  <input
                    type="checkbox"
                    name="async_execution"
                    checked={formData.async_execution}
                    onChange={handleInputChange}
                  />
                  Execução Assíncrona
                </label>
                <p className="help-text">A tarefa será executada em background</p>
              </div>
            </div>

            <div className="output-config">
              <div className="form-group">
                <label htmlFor="output_json">Schema JSON de Saída (opcional)</label>
                <textarea
                  id="output_json"
                  name="output_json"
                  value={formData.output_json}
                  onChange={handleInputChange}
                  placeholder='{"campo": "tipo", "outro_campo": "tipo"}'
                  rows={2}
                />
              </div>

              <div className="form-group">
                <label htmlFor="output_file">Arquivo de Saída (opcional)</label>
                <input
                  type="text"
                  id="output_file"
                  name="output_file"
                  value={formData.output_file}
                  onChange={handleInputChange}
                  placeholder="ex: resultado_analise.json"
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-save">
              {task ? 'Salvar Alterações' : 'Criar Tarefa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskFormModal;