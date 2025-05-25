// src/components/tasks/TaskSpecifierModal.tsx
import React, { useState } from 'react';
import { Agent } from '../../types';
import './TaskSpecifierModal.css';

interface TaskSpecifierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSpecify: (tasks: any[]) => void;
  agents: Agent[];
  projectId: string;
}

const TaskSpecifierModal: React.FC<TaskSpecifierModalProps> = ({
  isOpen,
  onClose,
  onSpecify,
  agents
// src/components/tasks/TaskSpecifierModal.tsx (continuação)
}) => {
  const [documents, setDocuments] = useState<File[]>([]);
  const [instructions, setInstructions] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [taskGenerationMode, setTaskGenerationMode] = useState<'auto' | 'guided'>('auto');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setDocuments([...documents, ...newFiles]);
    }
  };

  const handleRemoveDocument = (index: number) => {
    setDocuments(documents.filter((_, i) => i !== index));
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files);
      setDocuments([...documents, ...newFiles]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleAgentToggle = (agentId: string) => {
    setSelectedAgents(prev => 
      prev.includes(agentId) 
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const handleSpecify = async () => {
    if (documents.length === 0 && !instructions) {
      alert('Por favor, adicione documentos ou instruções');
      return;
    }

    setIsProcessing(true);

    // Simular processamento - aqui você faria a chamada real para o LLM
    setTimeout(() => {
      // Resultado simulado baseado nos agentes selecionados
      const specifiedTasks = [
        {
          name: 'receive_customer_query_task',
          description: 'Receber e validar a consulta inicial do cliente, extraindo informações básicas',
          expected_output: 'Objeto estruturado com campos: tipo_consulta, urgencia, dados_cliente',
          agent: selectedAgents[0] || agents[0]?.id,
          context: [],
          tools: ['InputValidatorTool', 'DataExtractorTool'],
          human_input: false,
          async_execution: false
        },
        {
          name: 'classify_query_task',
          description: 'Classificar a consulta em categorias predefinidas e determinar prioridade',
          expected_output: 'Classificação com categoria, subcategoria, nível de prioridade e justificativa',
          agent: selectedAgents[0] || agents[0]?.id,
          context: ['task_1'],
          tools: ['ClassificationModel', 'PriorityAnalyzer'],
          human_input: false,
          async_execution: true,
          output_json: '{ "category": "string", "subcategory": "string", "priority": "number" }'
        },
        {
          name: 'route_to_specialist_task',
          description: 'Direcionar a consulta para o especialista apropriado baseado na classificação',
          expected_output: 'Identificação do agente especialista e instruções de roteamento',
          agent: selectedAgents[1] || agents[1]?.id || selectedAgents[0],
          context: ['task_2'],
          tools: ['RoutingEngine', 'AgentSelectorTool'],
          human_input: false,
          async_execution: false
        },
        {
          name: 'generate_response_task',
          description: 'Gerar resposta apropriada baseada no contexto e histórico do cliente',
          expected_output: 'Resposta formatada e personalizada para o cliente',
          agent: selectedAgents[1] || agents[1]?.id || selectedAgents[0],
          context: ['task_1', 'task_2', 'task_3'],
          tools: ['ResponseGeneratorTool', 'CustomerHistoryTool'],
          human_input: true,
          async_execution: false,
          output_file: 'customer_response.txt'
        }
      ];

      onSpecify(specifiedTasks);
      setIsProcessing(false);
      
      // Limpar o modal
      setDocuments([]);
      setInstructions('');
      setSelectedAgents([]);
    }, 3000);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="task-specifier-modal">
        <div className="modal-header">
          <h2>📋 ESPECIFICADOR DE TAREFAS</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="specifier-intro">
            <p>
              O Especificador de Tarefas utiliza IA para analisar documentos e gerar 
              automaticamente definições de tarefas baseadas nos requisitos e fluxos identificados.
            </p>
          </div>

          <div className="generation-mode">
            <h3>Modo de Geração</h3>
            <div className="mode-selector">
              <label>
                <input
                  type="radio"
                  value="auto"
                  checked={taskGenerationMode === 'auto'}
                  onChange={(e) => setTaskGenerationMode(e.target.value as 'auto' | 'guided')}
                />
                <span>Automático</span>
                <p>Gera tarefas automaticamente baseado na análise</p>
              </label>
              <label>
                <input
                  type="radio"
                  value="guided"
                  checked={taskGenerationMode === 'guided'}
                  onChange={(e) => setTaskGenerationMode(e.target.value as 'auto' | 'guided')}
                />
                <span>Guiado</span>
                <p>Permite mais controle sobre a geração</p>
              </label>
            </div>
          </div>

          <div className="form-section">
            <h3>📄 Documentos de Entrada</h3>
            
            <div 
              className="drop-zone"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <p>Arraste arquivos aqui ou clique para selecionar</p>
              <p className="file-types">Suportados: PDF, DOC, DOCX, TXT, MD, Diagramas</p>
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md,.png,.jpg,.svg"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                id="file-upload"
              />
              <label htmlFor="file-upload" className="btn-upload">
                Selecionar Arquivos
              </label>
            </div>

            {documents.length > 0 && (
              <div className="uploaded-files">
                <h4>Arquivos carregados:</h4>
                {documents.map((file, index) => (
                  <div key={index} className="file-item">
                    <span className="file-icon">📄</span>
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                    <button 
                      className="btn-remove"
                      onClick={() => handleRemoveDocument(index)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>🤖 Agentes Disponíveis</h3>
            <p className="help-text">Selecione os agentes que executarão as tarefas</p>
            
            <div className="agents-selector">
              {agents.length > 0 ? (
                agents.map(agent => (
                  <label key={agent.id} className="agent-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(agent.id)}
                      onChange={() => handleAgentToggle(agent.id)}
                    />
                    <div className="agent-info">
                      <span className="agent-name">{agent.name}</span>
                      <span className="agent-role">{agent.role}</span>
                    </div>
                  </label>
                ))
              ) : (
                <p className="no-agents">Nenhum agente disponível. Crie agentes primeiro.</p>
              )}
            </div>
          </div>

          <div className="form-section">
            <h3>📝 Instruções Adicionais</h3>
            <textarea
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="Forneça instruções específicas sobre os tipos de tarefas, fluxos de trabalho, dependências entre tarefas, critérios de sucesso, etc."
              rows={6}
            />
          </div>

          <div className="specifier-options">
            <h3>⚙️ Opções de Geração</h3>
            <div className="options-grid">
              <label>
                <input type="checkbox" defaultChecked />
                Criar tarefas sequenciais
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Incluir validações
              </label>
              <label>
                <input type="checkbox" />
                Gerar tarefas de rollback
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Otimizar dependências
              </label>
              <label>
                <input type="checkbox" />
                Incluir tarefas de monitoramento
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Definir outputs estruturados
              </label>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {selectedAgents.length === 0 && agents.length > 0 && (
              <span className="warning">⚠️ Nenhum agente selecionado</span>
            )}
          </div>
          <div className="footer-actions">
            <button className="btn-cancel" onClick={onClose} disabled={isProcessing}>
              Cancelar
            </button>
            <button 
              className="btn-specify" 
              onClick={handleSpecify}
              disabled={isProcessing || (selectedAgents.length === 0 && agents.length > 0)}
            >
              {isProcessing ? (
                <>
                  <span className="spinner"></span>
                  Processando...
                </>
              ) : (
                '🚀 Especificar Tarefas'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskSpecifierModal;