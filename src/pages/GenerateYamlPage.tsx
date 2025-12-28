/* src/pages/GenerateYamlPage.tsx */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ChatInterface, { ChatMessage } from '../components/documents/ChatInterface';
import AgentTaskSpecHistoryModal from '../components/agent-task/AgentTaskSpecHistoryModal';
import { useNavigation } from '../contexts/NavigationContext';
import { toast } from 'react-toastify';
import './DocumentsPage.css'; // USA O MESMO CSS
import * as agentTaskService from '../services/agentTaskService';

const GenerateYamlPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { projectContext } = useNavigation();

  // Agent/Task Spec selection states
  const [isAgentTaskSpecModalOpen, setIsAgentTaskSpecModalOpen] = useState(false);
  const [selectedAgentTaskSpecSessionId, setSelectedAgentTaskSpecSessionId] = useState<string>('');
  const [selectedAgentTaskSpecName, setSelectedAgentTaskSpecName] = useState<string>('');

  // Agent/Task history modal
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);

  // Generation states
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);

  // Chat states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatProcessing, setIsChatProcessing] = useState(false);

  // Configuration states
  const [detailLevel, setDetailLevel] = useState<'concise' | 'balanced' | 'detailed'>('balanced');
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>(['CrewAI']);
  const [customInstructions, setCustomInstructions] = useState('');

  // Results states
  const [generatedAgents, setGeneratedAgents] = useState<any[]>([]);
  const [generatedTasks, setGeneratedTasks] = useState<any[]>([]);
  const [agentsYaml, setAgentsYaml] = useState<string>('');
  const [tasksYaml, setTasksYaml] = useState<string>('');

  // Handler for agent/task spec selection
  const handleAgentTaskSpecSelect = (sessionId: string, sessionName: string) => {
    setSelectedAgentTaskSpecSessionId(sessionId);
    setSelectedAgentTaskSpecName(sessionName);
    toast.success(`Documento selecionado: ${sessionName}`);
  };

  // Handler for generation
  const startGeneration = async () => {
    if (!selectedAgentTaskSpecSessionId) {
      toast.error('Selecione um documento de especificação de agentes/tarefas primeiro');
      return;
    }

    setIsGenerating(true);
    setIsChatProcessing(true);

    try {
      // Mensagem inicial no chat
      const systemMsg: ChatMessage = {
        id: Date.now().toString(),
        sender: 'system',
        text: '🚀 Gerando arquivos YAML de agentes e tarefas...',
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages([systemMsg]);

      // Chamar API para gerar YAMLs a partir do documento de especificação
      const response = await agentTaskService.generateAgentsAndTasks({
        agent_task_spec_session_id: selectedAgentTaskSpecSessionId,
        detail_level: detailLevel,
        frameworks: selectedFrameworks,
        auto_generate_yaml: true
      });

      // Atualizar estado com resultado
      setCurrentSessionId(response.session_id);
      setGeneratedAgents(response.agents || []);
      setGeneratedTasks(response.tasks || []);
      setAgentsYaml(response.agents_yaml || '');
      setTasksYaml(response.tasks_yaml || '');

      // Mensagem de sucesso no chat
      const successMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: `✅ ${response.agents.length} agentes e ${response.tasks.length} tarefas gerados com sucesso!\n\n📥 YAMLs prontos para download.`,
        timestamp: new Date(),
        type: 'result'
      };
      setChatMessages(prev => [...prev, successMsg]);

      toast.success('YAMLs gerados com sucesso');

    } catch (error: any) {
      console.error('Erro ao gerar YAMLs:', error);

      const errorMsg: ChatMessage = {
        id: (Date.now() + 2).toString(),
        sender: 'system',
        text: `❌ Erro: ${error.message || 'Falha ao gerar YAMLs'}`,
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages(prev => [...prev, errorMsg]);

      toast.error(error.message || 'Erro ao gerar YAMLs');
    } finally {
      setIsGenerating(false);
      setIsChatProcessing(false);
    }
  };

  // Handler for chat refinement
  const handleChatSend = async (message: string) => {
    if (!currentSessionId) {
      toast.error('Nenhuma sessão ativa');
      return;
    }

    setIsChatProcessing(true);

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: message,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMsg]);

    try {
      // Chamar API para refinar agentes e tarefas
      const response = await agentTaskService.refineAgentsAndTasks(
        currentSessionId,
        message
      );

      // Atualizar estado com agentes/tarefas refinados
      setGeneratedAgents(response.refined_agents || []);
      setGeneratedTasks(response.refined_tasks || []);
      setAgentsYaml(response.agents_yaml || '');
      setTasksYaml(response.tasks_yaml || '');

      // Mensagem da assistente no chat
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.refinement_summary || response.message || '✅ Refinamento aplicado com sucesso!',
        timestamp: new Date(),
        type: 'result'
      };
      setChatMessages(prev => [...prev, assistantMsg]);

      toast.success('Refinamento aplicado');

    } catch (error: any) {
      console.error('Erro ao refinar:', error);

      const errorMsg: ChatMessage = {
        id: (Date.now() + 2).toString(),
        sender: 'system',
        text: `❌ Erro: ${error.message || 'Falha ao refinar'}`,
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages(prev => [...prev, errorMsg]);

      toast.error(error.message || 'Erro ao processar refinamento');
    } finally {
      setIsChatProcessing(false);
    }
  };

  const handleDownloadYamls = () => {
    if (!agentsYaml || !tasksYaml) {
      toast.error('Gere os agentes e tarefas primeiro');
      return;
    }

    try {
      // Criar arquivo agents.yaml
      const agentsBlob = new Blob([agentsYaml], { type: 'text/yaml' });
      const agentsUrl = window.URL.createObjectURL(agentsBlob);
      const agentsLink = document.createElement('a');
      agentsLink.href = agentsUrl;
      agentsLink.download = 'langnet_agents.yaml';
      document.body.appendChild(agentsLink);
      agentsLink.click();
      document.body.removeChild(agentsLink);
      window.URL.revokeObjectURL(agentsUrl);

      // Criar arquivo tasks.yaml
      const tasksBlob = new Blob([tasksYaml], { type: 'text/yaml' });
      const tasksUrl = window.URL.createObjectURL(tasksBlob);
      const tasksLink = document.createElement('a');
      tasksLink.href = tasksUrl;
      tasksLink.download = 'langnet_tasks.yaml';
      document.body.appendChild(tasksLink);
      tasksLink.click();
      document.body.removeChild(tasksLink);
      window.URL.revokeObjectURL(tasksUrl);

      toast.success('YAMLs baixados com sucesso');
    } catch (error) {
      console.error('Erro ao baixar YAMLs:', error);
      toast.error('Erro ao baixar arquivos');
    }
  };

  return (
    <div className="documents-page-chat">
      <div className="page-header">
        <div className="header-content">
          <h1>🔧 Gerar YAML de Agentes & Tarefas {projectContext.isInProject && `- ${projectContext.projectName}`}</h1>
          <p>Gere arquivos YAML a partir do documento de especificação de agentes e tarefas</p>
        </div>
      </div>

      <div className="documents-chat-container">
        {/* LEFT SIDEBAR: Configuration */}
        <div className="documents-sidebar">
          <div className="sidebar-header">
            <h3>📋 Configuração</h3>
            <div className="header-buttons">
              <button
                className="btn-history-compact"
                onClick={() => setIsHistoryModalOpen(true)}
                title="Histórico de Gerações"
              >
                📜 Histórico
              </button>
              <button
                className={`btn-requirements-compact ${selectedAgentTaskSpecSessionId ? 'selected' : ''}`}
                onClick={() => setIsAgentTaskSpecModalOpen(true)}
                title="Selecionar Documento de Especificação de Agentes/Tarefas"
              >
                📋 {selectedAgentTaskSpecSessionId ? 'Doc Spec ✓' : 'Doc Especificação'}
              </button>
            </div>
          </div>

          {/* Mostrar documento selecionado */}
          {selectedAgentTaskSpecSessionId && (
            <div style={{
              padding: '8px 12px',
              backgroundColor: '#d4edda',
              borderBottom: '1px solid #c3e6cb',
              fontSize: '12px'
            }}>
              <strong>📋 Base:</strong> {selectedAgentTaskSpecName}
            </div>
          )}

          {/* Empty state quando sem documento */}
          {!selectedAgentTaskSpecSessionId && (
            <div className="documents-compact-list">
              <div className="empty-sidebar">
                <p>Selecione um documento de especificação de agentes/tarefas</p>
                <button onClick={() => setIsAgentTaskSpecModalOpen(true)}>
                  📋 Selecionar Documento
                </button>
              </div>
            </div>
          )}

          {/* Configuration Options */}
          <div className="analysis-config">
            <h4>⚙️ Opções de Geração</h4>

            <label>Nível de Detalhamento</label>
            <select
              value={detailLevel}
              onChange={(e) => setDetailLevel(e.target.value as any)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontSize: '13px',
                marginBottom: '12px'
              }}
            >
              <option value="concise">Conciso</option>
              <option value="balanced">Balanceado</option>
              <option value="detailed">Detalhado</option>
            </select>

            <label>Frameworks Suportados</label>
            <div style={{ marginBottom: '12px' }}>
              {['CrewAI', 'AutoGen', 'LangChain', 'Custom'].map(fw => (
                <label key={fw} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedFrameworks.includes(fw)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedFrameworks([...selectedFrameworks, fw]);
                      } else {
                        setSelectedFrameworks(selectedFrameworks.filter(f => f !== fw));
                      }
                    }}
                  />
                  <span>{fw}</span>
                </label>
              ))}
            </div>

            <label>Instruções Adicionais</label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="Ex: Priorizar agentes especializados, incluir validações..."
              rows={3}
            />

            <button
              className="btn-start-analysis"
              onClick={startGeneration}
              disabled={isGenerating || !selectedAgentTaskSpecSessionId}
            >
              {isGenerating ? '⏳ Gerando...' : '🚀 Gerar Agentes & Tarefas'}
            </button>

            {!selectedAgentTaskSpecSessionId && (
              <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                ⚠️ Selecione um documento de especificação de agentes/tarefas primeiro
              </p>
            )}
          </div>
        </div>

        {/* MIDDLE AREA: Chat Interface */}
        <div className="chat-area">
          {isChatProcessing && (
            <div className="generating-indicator">
              <div className="indicator-content">
                <span className="spinner">⏳</span>
                <strong>🚀 GERANDO ARQUIVOS YAML...</strong>
                <span className="blink">Aguarde, isso pode levar 1-3 minutos</span>
              </div>
            </div>
          )}

          <ChatInterface
            messages={chatMessages}
            onSendMessage={handleChatSend}
            isProcessing={isChatProcessing}
          />
        </div>

        {/* RIGHT PANEL: Results */}
        <div className="actions-panel">
          {!currentSessionId ? (
            <div className="no-document-placeholder">
              <div className="placeholder-icon">🔧</div>
              <h3>Nenhuma Geração Ativa</h3>
              <p>Gere YAMLs a partir de um documento de especificação para visualizar os resultados aqui.</p>
            </div>
          ) : (
            <>
              {/* Agent Summary */}
              <div style={{ padding: '20px', borderBottom: '2px solid #e5e7eb' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600 }}>
                  🤖 Agentes Gerados ({generatedAgents.length})
                </h4>
                {generatedAgents.length === 0 ? (
                  <p style={{ fontSize: '12px', color: '#999' }}>Nenhum agente gerado ainda</p>
                ) : (
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {generatedAgents.map((agent, idx) => (
                      <div key={idx} style={{
                        padding: '8px',
                        background: '#f9fafb',
                        borderRadius: '4px',
                        marginBottom: '6px'
                      }}>
                        <strong>{agent.name}</strong>: {agent.role}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Tasks Summary */}
              <div style={{ padding: '20px', borderBottom: '2px solid #e5e7eb' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 600 }}>
                  📋 Tarefas Geradas ({generatedTasks.length})
                </h4>
                {generatedTasks.length === 0 ? (
                  <p style={{ fontSize: '12px', color: '#999' }}>Nenhuma tarefa gerada ainda</p>
                ) : (
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {generatedTasks.map((task, idx) => (
                      <div key={idx} style={{
                        padding: '8px',
                        background: '#f9fafb',
                        borderRadius: '4px',
                        marginBottom: '6px'
                      }}>
                        <strong>{task.name}</strong>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div style={{ padding: '20px' }}>
                <button
                  className="btn-start-analysis"
                  onClick={handleDownloadYamls}
                  disabled={!agentsYaml || !tasksYaml}
                  style={{ marginBottom: '12px' }}
                >
                  📥 Download YAMLs
                </button>

                <button
                  className="btn-review"
                  onClick={() => toast.info('Visualização de grafo em breve')}
                  disabled={generatedTasks.length === 0}
                >
                  🔗 Ver Grafo de Dependências
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modal for Agent/Task Spec Selection */}
      <AgentTaskSpecHistoryModal
        isOpen={isAgentTaskSpecModalOpen}
        onClose={() => setIsAgentTaskSpecModalOpen(false)}
        projectId={projectId || ''}
        onSelectSession={handleAgentTaskSpecSelect}
      />

      {/* Modal for Agent/Task History - TODO: criar componente */}
      {isHistoryModalOpen && (
        <div className="modal-overlay">
          <div className="history-modal">
            <div className="modal-header">
              <h2>📜 Histórico de Gerações</h2>
              <button className="close-button" onClick={() => setIsHistoryModalOpen(false)}>×</button>
            </div>
            <div className="modal-content">
              <div className="empty-state">
                <div className="empty-icon">⚙️</div>
                <p>Histórico de gerações em desenvolvimento</p>
                <p className="empty-hint">
                  As sessões de agentes e tarefas geradas aparecerão aqui
                </p>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-close" onClick={() => setIsHistoryModalOpen(false)}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerateYamlPage;
