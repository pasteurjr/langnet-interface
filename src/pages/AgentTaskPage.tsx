/* src/pages/AgentTaskPage.tsx */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ChatInterface, { ChatMessage } from '../components/documents/ChatInterface';
import SpecificationHistoryModal from '../components/specification/SpecificationHistoryModal';
import AgentTaskSpecHistoryModal from '../components/agent-task/AgentTaskSpecHistoryModal';
import DocumentActionsCard from '../components/documents/DocumentActionsCard';
import MarkdownViewerModal from '../components/documents/MarkdownViewerModal';
import MarkdownEditorModal from '../components/documents/MarkdownEditorModal';
import DiffViewerModal from '../components/documents/DiffViewerModal';
import { useNavigation } from '../contexts/NavigationContext';
import { toast } from 'react-toastify';
import './DocumentsPage.css'; // USA O MESMO CSS
import * as agentTaskService from '../services/agentTaskService';

const AgentTaskPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { projectContext } = useNavigation();

  // Specification selection states
  const [isSpecModalOpen, setIsSpecModalOpen] = useState(false);
  const [selectedSpecSessionId, setSelectedSpecSessionId] = useState<string>('');
  const [selectedSpecVersion, setSelectedSpecVersion] = useState<number>(1);
  const [selectedSpecName, setSelectedSpecName] = useState<string>('');

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
  const [generatedDocument, setGeneratedDocument] = useState<string>('');
  const [currentLoadedVersion, setCurrentLoadedVersion] = useState<number | null>(null);
  const [totalAgents, setTotalAgents] = useState<number>(0);
  const [totalTasks, setTotalTasks] = useState<number>(0);
  const [generatedAgents, setGeneratedAgents] = useState<any[]>([]);
  const [generatedTasks, setGeneratedTasks] = useState<any[]>([]);
  const [agentsYaml, setAgentsYaml] = useState<string>('');
  const [tasksYaml, setTasksYaml] = useState<string>('');

  // Modal states
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [documentFilename, setDocumentFilename] = useState<string>('especificacao_agentes_tarefas.md');

  // Diff states (seguindo padrão do SpecificationPage)
  const [showDiff, setShowDiff] = useState(false);
  const [oldDocument, setOldDocument] = useState<string>('');
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);

  // useEffect para detectar diffs automaticamente (padrão SpecificationPage)
  useEffect(() => {
    if (chatMessages.length === 0) return;

    const lastMessage = chatMessages[chatMessages.length - 1];

    // Backend envia has_diff=true quando há alteração
    if (lastMessage?.data?.has_diff &&
        lastMessage.data.old_document &&
        lastMessage.data.new_document) {
      console.log('📊 Diff detectado na última mensagem');

      // Armazena versões antiga e nova
      setOldDocument(lastMessage.data.old_document);
      setGeneratedDocument(lastMessage.data.new_document);
      setShowDiff(true);
      setIsDiffModalOpen(true);

      toast.success('Documento refinado! Clique em "Ver Diferenças" para comparar as alterações.');
    }
  }, [chatMessages]);

  // Handler for specification selection (from SpecificationHistoryModal)
  const handleSpecSessionSelect = (sessionId: string, sessionName: string) => {
    setSelectedSpecSessionId(sessionId);
    setSelectedSpecName(sessionName);
  };

  const handleSpecVersionSelect = (version: number) => {
    setSelectedSpecVersion(version);
    toast.success(`Especificação selecionada: ${selectedSpecName} (v${version})`);
  };

  // Handler for loading agent/task spec session from history
  const handleHistorySessionSelect = async (sessionId: string, sessionName: string) => {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/agent-task-spec/${sessionId}`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Falha ao carregar sessão');
      }

      const session = await response.json();

      setCurrentSessionId(session.session_id);
      setGeneratedDocument(session.agent_task_spec_document || '');
      setCurrentLoadedVersion(null); // Reset version when loading session
      setTotalAgents(session.total_agents || 0);
      setTotalTasks(session.total_tasks || 0);

      toast.success(`Documento carregado: ${sessionName}`);
    } catch (error: any) {
      console.error('Erro ao carregar sessão:', error);
      toast.error('Erro ao carregar documento do histórico');
    }
  };

  // Handler for loading specific version from history (padrão SpecificationPage)
  const handleHistoryVersionSelect = async (sessionId: string, version: number) => {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      // Buscar versão específica da API
      const response = await fetch(`${API_BASE_URL}/agent-task-spec/${sessionId}/versions`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Falha ao carregar versões');
      }

      const versions = await response.json();
      const versionData = versions.find((v: any) => v.version === version);

      if (!versionData || !versionData.agent_task_spec_document) {
        throw new Error('Versão não encontrada');
      }

      // Atualizar estados
      setCurrentSessionId(sessionId);
      setGeneratedDocument(versionData.agent_task_spec_document);
      setCurrentLoadedVersion(version);
      setDocumentFilename(`especificacao_agentes_tarefas_v${version}.md`);

      toast.success(`Versão ${version} carregada com sucesso`);
    } catch (error: any) {
      console.error('Erro ao carregar versão:', error);
      toast.error('Erro ao carregar versão do histórico');
    }
  };

  // Handler for generation
  const startGeneration = async () => {
    if (!selectedSpecSessionId) {
      toast.error('Selecione uma especificação funcional primeiro');
      return;
    }

    setIsGenerating(true);
    setIsChatProcessing(true);

    try {
      // Mensagem inicial no chat
      const systemMsg: ChatMessage = {
        id: Date.now().toString(),
        sender: 'system',
        text: '🚀 Gerando documento de especificação de agentes e tarefas...',
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages([systemMsg]);

      // Chamar API para gerar especificação de agentes/tarefas (documento MD)
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/agent-task-spec/`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          specification_session_id: selectedSpecSessionId,
          specification_version: selectedSpecVersion,
          detail_level: detailLevel,
          frameworks: selectedFrameworks,
          max_agents: 15,
          custom_instructions: customInstructions || undefined
        })
      });

      if (!response.ok) {
        throw new Error('Falha ao gerar especificação de agentes e tarefas');
      }

      const result = await response.json();
      setCurrentSessionId(result.session_id);

      // Polling para obter documento gerado
      const pollInterval = setInterval(async () => {
        const statusRes = await fetch(`${API_BASE_URL}/agent-task-spec/${result.session_id}`, {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
          }
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);

            setGeneratedDocument(statusData.agent_task_spec_document || '');
            setTotalAgents(statusData.total_agents || 0);
            setTotalTasks(statusData.total_tasks || 0);

            const successMsg: ChatMessage = {
              id: (Date.now() + 1).toString(),
              sender: 'agent',
              text: `✅ Documento gerado com sucesso!\n\n📊 ${statusData.total_agents} agentes e ${statusData.total_tasks} tarefas especificados.`,
              timestamp: new Date(),
              type: 'result'
            };
            setChatMessages(prev => [...prev, successMsg]);

            setIsChatProcessing(false);
            toast.success('Documento de especificação gerado');
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            throw new Error('Geração falhou');
          }
        }
      }, 3000); // Poll a cada 3 segundos

    } catch (error: any) {
      console.error('Erro ao gerar especificação:', error);

      const errorMsg: ChatMessage = {
        id: (Date.now() + 2).toString(),
        sender: 'system',
        text: `❌ Erro: ${error.message || 'Falha ao gerar especificação'}`,
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages(prev => [...prev, errorMsg]);

      toast.error(error.message || 'Erro ao gerar especificação');
      setIsChatProcessing(false);
    } finally {
      setIsGenerating(false);
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

    // Salvar documento atual como oldDocument para comparação posterior
    const documentBeforeRefinement = generatedDocument;

    try {
      // Chamar API para refinar DOCUMENTO DE ESPECIFICAÇÃO (não YAMLs!)
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/agent-task-spec/${currentSessionId}/refine`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          action_type: 'refine'
        })
      });

      if (!response.ok) {
        throw new Error('Falha ao refinar documento');
      }

      // Iniciar polling para aguardar refinamento
      const pollInterval = setInterval(async () => {
        const statusRes = await fetch(`${API_BASE_URL}/agent-task-spec/${currentSessionId}`, {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
          }
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);

            const refinedDocument = statusData.agent_task_spec_document || '';

            // Atualizar documento refinado
            setGeneratedDocument(refinedDocument);
            setTotalAgents(statusData.total_agents || 0);
            setTotalTasks(statusData.total_tasks || 0);

            // Ativar diff (seguindo padrão SpecificationPage)
            setOldDocument(documentBeforeRefinement);
            setShowDiff(true);

            // Incrementar versão
            const newVersion = (currentLoadedVersion || 1) + 1;
            setCurrentLoadedVersion(newVersion);
            setDocumentFilename(`especificacao_agentes_tarefas_v${newVersion}.md`);

            // Mensagem da assistente no chat com has_diff
            const assistantMsg: ChatMessage = {
              id: (Date.now() + 1).toString(),
              sender: 'agent',
              text: `✅ Refinamento aplicado com sucesso!\n\nVersão ${newVersion} criada. Clique em "Ver Diferenças" para comparar as alterações.`,
              timestamp: new Date(),
              type: 'result',
              data: {
                has_diff: true,
                old_document: documentBeforeRefinement,
                new_document: refinedDocument
              }
            };
            setChatMessages(prev => [...prev, assistantMsg]);

            setIsChatProcessing(false);
            toast.success(`Refinamento aplicado - v${newVersion} criada`);
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setIsChatProcessing(false);
            throw new Error('Refinamento falhou');
          }
        }
      }, 3000); // Poll a cada 3 segundos

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
      setIsChatProcessing(false);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!generatedDocument) {
      toast.error('Nenhum documento para baixar');
      return;
    }

    try {
      const blob = new Blob([generatedDocument], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = documentFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('Documento baixado com sucesso');
    } catch (error) {
      console.error('Erro ao baixar documento:', error);
      toast.error('Erro ao baixar documento');
    }
  };

  const handleSaveEdit = (newContent: string) => {
    setGeneratedDocument(newContent);
    toast.success('Documento editado localmente. Use "Download" para salvar.');
  };

  return (
    <div className="documents-page-chat">
      <div className="page-header">
        <div className="header-content">
          <h1>📋 Especificação de Agentes & Tarefas {projectContext.isInProject && `- ${projectContext.projectName}`}</h1>
          <p>Gere documento estruturado de agentes e tarefas a partir de especificação funcional</p>
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
                className={`btn-requirements-compact ${selectedSpecSessionId ? 'selected' : ''}`}
                onClick={() => setIsSpecModalOpen(true)}
                title="Selecionar Especificação Funcional Base"
              >
                📝 {selectedSpecSessionId ? 'Espec ✓' : 'Especificação'}
              </button>
            </div>
          </div>

          {/* Mostrar especificação selecionada */}
          {selectedSpecSessionId && (
            <div style={{
              padding: '8px 12px',
              backgroundColor: '#d4edda',
              borderBottom: '1px solid #c3e6cb',
              fontSize: '12px'
            }}>
              <strong>📝 Base:</strong> {selectedSpecName} (v{selectedSpecVersion})
            </div>
          )}

          {/* Empty state quando sem especificação */}
          {!selectedSpecSessionId && (
            <div className="documents-compact-list">
              <div className="empty-sidebar">
                <p>Selecione uma especificação funcional</p>
                <button onClick={() => setIsSpecModalOpen(true)}>
                  📝 Selecionar Especificação
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
              disabled={isGenerating || !selectedSpecSessionId}
            >
              {isGenerating ? '⏳ Gerando...' : '🚀 Gerar Agentes & Tarefas'}
            </button>

            {!selectedSpecSessionId && (
              <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                ⚠️ Selecione uma especificação funcional primeiro
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
                <strong>🚀 GERANDO DOCUMENTO DE ESPECIFICAÇÃO...</strong>
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

        {/* RIGHT PANEL: Document Actions */}
        <div className="actions-panel">
          {generatedDocument ? (
            <DocumentActionsCard
              filename={documentFilename}
              content={generatedDocument}
              executionId={currentSessionId}
              projectId={projectId}
              hasDiff={showDiff && !!oldDocument}
              version={currentLoadedVersion}
              onViewDiff={() => setIsDiffModalOpen(true)}
              onEdit={() => setIsEditorOpen(true)}
              onView={() => setIsViewerOpen(true)}
              onExportPDF={async () => {
                const { exportMarkdownToPDF } = await import('../services/pdfExportService');
                await exportMarkdownToPDF(generatedDocument, documentFilename.replace('.md', '.pdf'));
              }}
            />
          ) : (
            <div className="no-document-placeholder">
              <div className="placeholder-icon">📋</div>
              <h3>Nenhum Documento Gerado</h3>
              <p>Selecione uma especificação funcional e clique em "Gerar Especificação de Agentes & Tarefas"</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal for Specification Selection */}
      <SpecificationHistoryModal
        isOpen={isSpecModalOpen}
        onClose={() => setIsSpecModalOpen(false)}
        projectId={projectId}
        onSelectSession={handleSpecSessionSelect}
        onSelectVersion={handleSpecVersionSelect}
      />

      {/* Markdown Viewer Modal */}
      <MarkdownViewerModal
        isOpen={isViewerOpen}
        content={generatedDocument}
        filename={documentFilename}
        onClose={() => setIsViewerOpen(false)}
        onDownload={async () => {
          const { exportMarkdownToPDF } = await import('../services/pdfExportService');
          await exportMarkdownToPDF(generatedDocument, documentFilename.replace('.md', '.pdf'));
        }}
      />

      {/* Markdown Editor Modal */}
      <MarkdownEditorModal
        isOpen={isEditorOpen}
        content={generatedDocument}
        filename={documentFilename}
        onSave={handleSaveEdit}
        onClose={() => setIsEditorOpen(false)}
      />

      {/* Modal for Agent/Task Spec History */}
      <AgentTaskSpecHistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        projectId={projectId || ''}
        onSelectSession={handleHistorySessionSelect}
        onSelectVersion={handleHistoryVersionSelect}
      />

      {/* Diff Viewer Modal */}
      <DiffViewerModal
        isOpen={isDiffModalOpen}
        oldDocument={oldDocument}
        newDocument={generatedDocument}
        onClose={() => setIsDiffModalOpen(false)}
      />
    </div>
  );
};

export default AgentTaskPage;
