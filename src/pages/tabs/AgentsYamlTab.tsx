/* src/pages/tabs/AgentsYamlTab.tsx */
import React, { useState, useEffect } from 'react';
import ChatInterface, { ChatMessage } from '../../components/documents/ChatInterface';
import AgentTaskSpecHistoryModal from '../../components/agent-task/AgentTaskSpecHistoryModal';
import AgentsYamlHistoryModal from '../../components/yaml/AgentsYamlHistoryModal';
import ReviewSuggestionsModal from '../../components/agent-task/ReviewSuggestionsModal';
import DocumentActionsCard from '../../components/documents/DocumentActionsCard';
import MarkdownViewerModal from '../../components/documents/MarkdownViewerModal';
import MarkdownEditorModal from '../../components/documents/MarkdownEditorModal';
import DiffViewerModal from '../../components/documents/DiffViewerModal';
import { toast } from 'react-toastify';
import '../DocumentsPage.css'; // USA O MESMO CSS
import * as agentsYamlService from '../../services/agentsYamlService';

interface AgentsYamlTabProps {
  projectId?: string;
}

const AgentsYamlTab: React.FC<AgentsYamlTabProps> = ({ projectId }) => {

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
  const [customInstructions, setCustomInstructions] = useState('');
  const [detailLevel, setDetailLevel] = useState<'concise' | 'balanced' | 'detailed'>('balanced');
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>(['CrewAI']);

  // Results states
  const [generatedYaml, setGeneratedYaml] = useState<string>('');
  const [currentLoadedVersion, setCurrentLoadedVersion] = useState<number | null>(null);
  const [totalAgents, setTotalAgents] = useState<number>(0);

  // Modal states
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [yamlFilename, setYamlFilename] = useState<string>('agents.yaml');

  // Diff states (seguindo padrão do SpecificationPage)
  const [showDiff, setShowDiff] = useState(false);
  const [oldYaml, setOldYaml] = useState<string>('');
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);

  // Review modal states
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [reviewSuggestions, setReviewSuggestions] = useState<string>('');
  const [isReviewing, setIsReviewing] = useState(false);
  const [isApplyingSuggestions, setIsApplyingSuggestions] = useState(false);

  // useEffect para detectar diffs automaticamente (padrão SpecificationPage)
  useEffect(() => {
    if (chatMessages.length === 0) return;

    const lastMessage = chatMessages[chatMessages.length - 1];

    // Backend envia has_diff=true quando há alteração
    if (lastMessage?.data?.has_diff &&
        lastMessage.data.old_yaml &&
        lastMessage.data.new_yaml) {
      console.log('📊 Diff detectado na última mensagem');

      // Armazena versões antiga e nova
      setOldYaml(lastMessage.data.old_yaml);
      setGeneratedYaml(lastMessage.data.new_yaml);
      setShowDiff(true);
      setIsDiffModalOpen(true);

      toast.success('agents.yaml refinado! Clique em "Ver Diferenças" para comparar as alterações.');
    }
  }, [chatMessages]);

  // Handler for specification selection (from SpecificationHistoryModal)
  const handleSpecSessionSelect = (sessionId: string, sessionName: string) => {
    setSelectedSpecSessionId(sessionId);
    setSelectedSpecName(sessionName);
  };

  const handleSpecVersionSelect = (sessionId: string, version: number) => {
    setSelectedSpecSessionId(sessionId);
    setSelectedSpecVersion(version);
    toast.success(`Documento selecionado: v${version}`);
  };

  // Handler for loading agents.yaml session from history
  const handleHistorySessionSelect = async (sessionId: string, sessionName: string) => {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}`, {
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
      setGeneratedYaml(session.agents_yaml_content || '');
      setCurrentLoadedVersion(null); // Reset version when loading session
      setTotalAgents(session.total_agents || 0);

      toast.success(`agents.yaml carregado: ${sessionName}`);
    } catch (error: any) {
      console.error('Erro ao carregar sessão:', error);
      toast.error('Erro ao carregar agents.yaml do histórico');
    }
  };

  // Handler for loading specific version from history (padrão SpecificationPage)
  const handleHistoryVersionSelect = async (sessionId: string, version: number) => {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      // Buscar TODAS as versões da API
      const response = await fetch(`${API_BASE_URL}/agents-yaml/${sessionId}/versions`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Falha ao carregar versões');
      }

      const versions = await response.json();

      // Buscar a versão solicitada
      const versionData = versions.find((v: any) => v.version === version);

      if (!versionData || !versionData.agents_yaml_content) {
        throw new Error('Versão não encontrada');
      }

      // Buscar a versão ANTERIOR (se existir) para diff
      let previousVersionYaml = '';
      if (version > 1) {
        const previousVersionData = versions.find((v: any) => v.version === version - 1);
        if (previousVersionData && previousVersionData.agents_yaml_content) {
          previousVersionYaml = previousVersionData.agents_yaml_content;
        }
      }

      // Atualizar estados
      setCurrentSessionId(sessionId);
      setGeneratedYaml(versionData.agents_yaml_content);
      setCurrentLoadedVersion(version);
      setYamlFilename(`agents_v${version}.yaml`);

      // Ativar diff se houver versão anterior
      if (previousVersionYaml) {
        setOldYaml(previousVersionYaml);
        setShowDiff(true);
        toast.success(`Versão ${version} carregada. Clique em "Ver Diferenças" para comparar com v${version - 1}.`);
      } else {
        // Limpar diff se for a versão 1
        setOldYaml('');
        setShowDiff(false);
        toast.success(`Versão ${version} carregada (versão inicial)`);
      }
    } catch (error: any) {
      console.error('Erro ao carregar versão:', error);
      toast.error('Erro ao carregar versão do histórico');
    }
  };

  // Handler for generation
  const startGeneration = async () => {
    if (!selectedSpecSessionId) {
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
        text: '🚀 Gerando agents.yaml...',
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages([systemMsg]);

      // Chamar API para gerar agents.yaml
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/agents-yaml/`, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_task_spec_session_id: selectedSpecSessionId,
          agent_task_spec_version: selectedSpecVersion,
          custom_instructions: customInstructions || undefined,
          detail_level: detailLevel,
          selected_frameworks: selectedFrameworks
        })
      });

      if (!response.ok) {
        throw new Error('Falha ao gerar agents.yaml');
      }

      const result = await response.json();
      setCurrentSessionId(result.session_id);

      // Polling para obter agents.yaml gerado
      const pollInterval = setInterval(async () => {
        const statusRes = await fetch(`${API_BASE_URL}/agents-yaml/${result.session_id}`, {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
          }
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);

            setGeneratedYaml(statusData.agents_yaml_content || '');
            setTotalAgents(statusData.total_agents || 0);

            const successMsg: ChatMessage = {
              id: (Date.now() + 1).toString(),
              sender: 'agent',
              text: `✅ agents.yaml gerado com sucesso!\n\n📊 ${statusData.total_agents} agentes configurados.`,
              timestamp: new Date(),
              type: 'result'
            };
            setChatMessages(prev => [...prev, successMsg]);

            setIsChatProcessing(false);
            toast.success('agents.yaml gerado com sucesso');
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            throw new Error('Geração falhou');
          }
        }
      }, 3000); // Poll a cada 3 segundos

    } catch (error: any) {
      console.error('Erro ao gerar agents.yaml:', error);

      const errorMsg: ChatMessage = {
        id: (Date.now() + 2).toString(),
        sender: 'system',
        text: `❌ Erro: ${error.message || 'Falha ao gerar agents.yaml'}`,
        timestamp: new Date(),
        type: 'status'
      };
      setChatMessages(prev => [...prev, errorMsg]);

      toast.error(error.message || 'Erro ao gerar agents.yaml');
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

    // Salvar YAML atual como oldYaml para comparação posterior
    const yamlBeforeRefinement = generatedYaml;

    try {
      // Chamar API para refinar agents.yaml
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/agents-yaml/${currentSessionId}/refine`, {
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
        throw new Error('Falha ao refinar agents.yaml');
      }

      // Iniciar polling para aguardar refinamento
      const pollInterval = setInterval(async () => {
        const statusRes = await fetch(`${API_BASE_URL}/agents-yaml/${currentSessionId}`, {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
          }
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);

            const refinedYaml = statusData.agents_yaml_content || '';

            // Atualizar YAML refinado
            setGeneratedYaml(refinedYaml);
            setTotalAgents(statusData.total_agents || 0);

            // Ativar diff (seguindo padrão SpecificationPage)
            setOldYaml(yamlBeforeRefinement);
            setShowDiff(true);

            // Incrementar versão
            const newVersion = (currentLoadedVersion || 1) + 1;
            setCurrentLoadedVersion(newVersion);
            setYamlFilename(`agents_v${newVersion}.yaml`);

            // Mensagem da assistente no chat com has_diff
            const assistantMsg: ChatMessage = {
              id: (Date.now() + 1).toString(),
              sender: 'agent',
              text: `✅ Refinamento aplicado com sucesso!\n\nVersão ${newVersion} criada. Clique em "Ver Diferenças" para comparar as alterações.`,
              timestamp: new Date(),
              type: 'result',
              data: {
                has_diff: true,
                old_yaml: yamlBeforeRefinement,
                new_yaml: refinedYaml
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

  // Handler for review
  const handleReview = async () => {
    if (!currentSessionId) {
      toast.error('Gere agents.yaml primeiro');
      return;
    }

    setIsReviewing(true);
    try {
      console.log('🔍 Iniciando revisão do agents.yaml...');
      const result = await agentsYamlService.reviewAgentsYaml(currentSessionId);
      setReviewSuggestions(result.suggestions);
      setIsReviewModalOpen(true);

      // Add review message to chat
      const reviewMsg: ChatMessage = {
        id: result.review_message_id,
        sender: 'agent',
        text: result.suggestions,
        timestamp: new Date(),
        type: 'result'
      };
      setChatMessages(prev => [...prev, reviewMsg]);

      toast.success('Revisão concluída!');
    } catch (error: any) {
      console.error('Erro ao revisar agents.yaml:', error);
      toast.error('Erro ao revisar agents.yaml. Tente novamente.');
    } finally {
      setIsReviewing(false);
    }
  };

  // Handler for applying suggestions
  const handleApplySuggestions = async (additionalInstructions?: string) => {
    if (!currentSessionId) {
      toast.error('Nenhuma sessão ativa');
      return;
    }

    setIsApplyingSuggestions(true);

    // Salvar YAML antes do refinamento para diff
    const yamlBeforeRefinement = generatedYaml;

    try {
      // Build refinement message
      let message = "Aplique as seguintes sugestões de melhoria ao agents.yaml:\n\n";
      message += reviewSuggestions;

      if (additionalInstructions) {
        message += `\n\n---\n\nINSTRUÇÕES COMPLEMENTARES:\n${additionalInstructions}`;
      }

      console.log('✏️ Aplicando sugestões de revisão...');

      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const token = localStorage.getItem('accessToken') || localStorage.getItem('token');

      // Chamar endpoint de refinamento
      const response = await fetch(`${API_BASE_URL}/agents-yaml/${currentSessionId}/refine`, {
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
        throw new Error('Falha ao aplicar sugestões');
      }

      setIsReviewModalOpen(false);
      setIsChatProcessing(true);
      toast.success('Aplicando sugestões... Aguarde a atualização do agents.yaml.');

      // Iniciar polling para aguardar refinamento
      const pollInterval = setInterval(async () => {
        const statusRes = await fetch(`${API_BASE_URL}/agents-yaml/${currentSessionId}`, {
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json'
          }
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);

            const refinedYaml = statusData.agents_yaml_content || '';

            // Atualizar YAML refinado
            setGeneratedYaml(refinedYaml);
            setTotalAgents(statusData.total_agents || 0);

            // Ativar diff
            setOldYaml(yamlBeforeRefinement);
            setShowDiff(true);

            // Incrementar versão
            const newVersion = (currentLoadedVersion || 1) + 1;
            setCurrentLoadedVersion(newVersion);
            setYamlFilename(`agents_v${newVersion}.yaml`);

            // Mensagem da assistente no chat
            const assistantMsg: ChatMessage = {
              id: (Date.now() + 1).toString(),
              sender: 'agent',
              text: `✅ Sugestões aplicadas com sucesso!\n\nVersão ${newVersion} criada. Clique em "Ver Diferenças" para comparar as alterações.`,
              timestamp: new Date(),
              type: 'result',
              data: {
                has_diff: true,
                old_yaml: yamlBeforeRefinement,
                new_yaml: refinedYaml
              }
            };
            setChatMessages(prev => [...prev, assistantMsg]);

            setIsChatProcessing(false);
            setIsApplyingSuggestions(false);
            toast.success(`Sugestões aplicadas - v${newVersion} criada`);
          } else if (statusData.status === 'failed') {
            clearInterval(pollInterval);
            setIsChatProcessing(false);
            setIsApplyingSuggestions(false);
            toast.error('Refinamento falhou');
          }
        }
      }, 3000); // Poll a cada 3 segundos

    } catch (error: any) {
      console.error('Erro ao aplicar sugestões:', error);
      toast.error('Erro ao aplicar sugestões. Tente novamente.');
      setIsApplyingSuggestions(false);
      setIsChatProcessing(false);
    }
  };

  const handleDownloadMarkdown = () => {
    if (!generatedYaml) {
      toast.error('Nenhum agents.yaml para baixar');
      return;
    }

    try {
      const blob = new Blob([generatedYaml], { type: 'text/yaml' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = yamlFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('agents.yaml baixado com sucesso');
    } catch (error) {
      console.error('Erro ao baixar agents.yaml:', error);
      toast.error('Erro ao baixar agents.yaml');
    }
  };

  const handleSaveEdit = (newContent: string) => {
    setGeneratedYaml(newContent);
    toast.success('agents.yaml editado localmente. Use "Download" para salvar.');
  };

  return (
    <div className="documents-page-chat">
      <div className="documents-chat-container">
        {/* LEFT SIDEBAR: Configuration */}
        <div className="documents-sidebar">
          <div className="sidebar-header">
            <h3>📋 Configuração</h3>
            <div className="header-buttons">
              <button
                className="btn-history-compact"
                onClick={() => setIsHistoryModalOpen(true)}
                title="Histórico de Gerações de agents.yaml"
              >
                📜 Histórico
              </button>
              <button
                className={`btn-requirements-compact ${selectedSpecSessionId ? 'selected' : ''}`}
                onClick={() => setIsSpecModalOpen(true)}
                title="Selecionar Documento de Agentes/Tarefas Base"
              >
                📝 {selectedSpecSessionId ? 'Doc MD ✓' : 'Doc MD'}
              </button>
            </div>
          </div>

          {/* Mostrar documento selecionado */}
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

          {/* Empty state quando sem documento */}
          {!selectedSpecSessionId && (
            <div className="documents-compact-list">
              <div className="empty-sidebar">
                <p>Selecione um documento de especificação de agentes/tarefas</p>
                <button onClick={() => setIsSpecModalOpen(true)}>
                  📝 Selecionar Documento MD
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
              {isGenerating ? '⏳ Gerando...' : '🚀 Gerar agents.yaml'}
            </button>

            <button
              className="btn-review"
              onClick={handleReview}
              disabled={isReviewing || !generatedYaml}
              title="Revisar agents.yaml e obter sugestões de melhoria"
              style={{ marginTop: '12px' }}
            >
              {isReviewing ? '⏳ Revisando...' : '🔍 Revisar agents.yaml'}
            </button>

            {!selectedSpecSessionId && (
              <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                ⚠️ Selecione um documento MD de especificação primeiro
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
                <strong>🚀 GERANDO AGENTS.YAML...</strong>
                <span className="blink">Aguarde, isso pode levar 1-2 minutos</span>
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
          {generatedYaml ? (
            <DocumentActionsCard
              filename={yamlFilename}
              content={generatedYaml}
              executionId={currentSessionId}
              projectId={projectId}
              hasDiff={showDiff && !!oldYaml}
              version={currentLoadedVersion}
              onViewDiff={() => setIsDiffModalOpen(true)}
              onEdit={() => setIsEditorOpen(true)}
              onView={() => setIsViewerOpen(true)}
              onExportPDF={async () => {
                const { exportMarkdownToPDF } = await import('../../services/pdfExportService');
                await exportMarkdownToPDF(generatedYaml, yamlFilename.replace('.yaml', '.pdf'));
              }}
            />
          ) : (
            <div className="no-document-placeholder">
              <div className="placeholder-icon">🤖</div>
              <h3>Nenhum agents.yaml Gerado</h3>
              <p>Selecione um documento MD de especificação e clique em "Gerar agents.yaml"</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal for Agent/Task Spec Document Selection */}
      <AgentTaskSpecHistoryModal
        isOpen={isSpecModalOpen}
        onClose={() => setIsSpecModalOpen(false)}
        projectId={projectId || ''}
        onSelectSession={handleSpecSessionSelect}
        onSelectVersion={handleSpecVersionSelect}
      />

      {/* Modal for agents.yaml History */}
      <AgentsYamlHistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        projectId={projectId || ''}
        onSelectSession={handleHistorySessionSelect}
        onSelectVersion={handleHistoryVersionSelect}
      />

      {/* Markdown Viewer Modal */}
      <MarkdownViewerModal
        isOpen={isViewerOpen}
        content={generatedYaml}
        filename={yamlFilename}
        onClose={() => setIsViewerOpen(false)}
        onDownload={async () => {
          const { exportMarkdownToPDF } = await import('../../services/pdfExportService');
          await exportMarkdownToPDF(generatedYaml, yamlFilename.replace('.yaml', '.pdf'));
        }}
      />

      {/* Markdown Editor Modal */}
      <MarkdownEditorModal
        isOpen={isEditorOpen}
        content={generatedYaml}
        filename={yamlFilename}
        onSave={handleSaveEdit}
        onClose={() => setIsEditorOpen(false)}
      />

      {/* Diff Viewer Modal */}
      <DiffViewerModal
        isOpen={isDiffModalOpen}
        oldDocument={oldYaml}
        newDocument={generatedYaml}
        onClose={() => setIsDiffModalOpen(false)}
      />

      {/* Review Suggestions Modal */}
      <ReviewSuggestionsModal
        isOpen={isReviewModalOpen}
        suggestions={reviewSuggestions}
        onClose={() => setIsReviewModalOpen(false)}
        onApply={handleApplySuggestions}
        isApplying={isApplyingSuggestions}
      />
    </div>
  );
};

export default AgentsYamlTab;
