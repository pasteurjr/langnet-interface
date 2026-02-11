/* src/pages/SequenciaTarefasPage.tsx */
/* Página para geração de Sequência de Tarefas (Task Execution Flow) */
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Document, DocumentStatus } from '../types';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import DocumentViewModal from '../components/documents/DocumentViewModal';
import ChatInterface, { ChatMessage } from '../components/documents/ChatInterface';
import ProgressBar from '../components/documents/ProgressBar';
import DocumentActionsCard from '../components/documents/DocumentActionsCard';
import MarkdownEditorModal from '../components/documents/MarkdownEditorModal';
import MarkdownViewerModal from '../components/documents/MarkdownViewerModal';
import TaskExecutionFlowHistoryModal from '../components/task-execution-flow/TaskExecutionFlowHistoryModal';
import DiffViewerModal from '../components/documents/DiffViewerModal';
import ReviewSuggestionsModal from '../components/specification/ReviewSuggestionsModal';
import YamlSelectionModal from '../components/task-execution-flow/YamlSelectionModal';
import * as documentService from '../services/documentService';
import * as chatService from '../services/chatService';
import {
  createTaskExecutionFlowSession,
  getTaskExecutionFlow,
  getSessionStatus,
  updateTaskExecutionFlow,
  listTaskExecutionFlowVersions,
  getTaskExecutionFlowVersion,
  refineTaskExecutionFlow,
  reviewTaskExecutionFlow,
  getChatHistory
} from '../services/taskExecutionFlowService';
import { useNavigation } from '../contexts/NavigationContext';
import { toast } from 'react-toastify';
import './SequenciaTarefasPage.css';

const SequenciaTarefasPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { projectContext } = useNavigation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estado para modal de seleção de Specs & Docs (specification, agent_task_spec, tasks.yaml)
  const [isYamlsModalOpen, setIsYamlsModalOpen] = useState(false);
  const [selectedSpecificationSessionId, setSelectedSpecificationSessionId] = useState<string>('');
  const [selectedAgentTaskSpecSessionId, setSelectedAgentTaskSpecSessionId] = useState<string>('');
  const [selectedTasksYamlSessionId, setSelectedTasksYamlSessionId] = useState<string>('');
  const [customInstructions, setCustomInstructions] = useState<string>('');

  // Chat states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatProcessing, setIsChatProcessing] = useState(false);
  const [currentExecutionId, setCurrentExecutionId] = useState<string | undefined>(undefined);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);
  const [isInitialGeneration, setIsInitialGeneration] = useState(false);

  // Progress states
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [currentTask, setCurrentTask] = useState<string>('');
  const [currentPhase, setCurrentPhase] = useState<string>('');
  const [completedTasks, setCompletedTasks] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);

  // Document states
  const [generatedDocument, setGeneratedDocument] = useState<string>('');
  const [documentFilename, setDocumentFilename] = useState<string>('task_execution_flow.md');
  const [currentLoadedVersion, setCurrentLoadedVersion] = useState<number | null>(null);

  // Diff states
  const [showDiff, setShowDiff] = useState(false);
  const [oldDocument, setOldDocument] = useState<string>('');

  // Modal states
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);

  // Review modal states
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [reviewSuggestions, setReviewSuggestions] = useState<string>('');
  const [isReviewing, setIsReviewing] = useState(false);
  const [isApplyingSuggestions, setIsApplyingSuggestions] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, [projectId]);

  // Polling: Reload chat history periodically while processing
  useEffect(() => {
    if (!isChatProcessing || !currentSessionId) return;

    const intervalId = setInterval(() => {
      console.log('🔄 Reloading chat history...');
      loadChatHistory(currentSessionId);
    }, 2000);

    return () => clearInterval(intervalId);
  }, [isChatProcessing, currentSessionId]);

  // POLLING: Verificar status da sessão e atualizar documento durante processamento
  useEffect(() => {
    if (!isChatProcessing || !currentSessionId) {
      return;
    }

    console.log('🔄 Polling de status iniciado para sessão:', currentSessionId);

    const intervalId = setInterval(async () => {
      try {
        console.log('🔄 Polling: Verificando status da sessão...');
        const status = await getSessionStatus(currentSessionId);
        console.log('📊 Status atual:', status.status);

        if (status.status === 'completed' && status.flow_document) {
          console.log('✅ Sessão concluída, atualizando documento...');
          setGeneratedDocument(status.flow_document);
          const version = status.current_version || 1;
          setCurrentLoadedVersion(version);
          setDocumentFilename(`task_execution_flow_v${version}.md`);
          await loadChatHistory(currentSessionId);
          toast.success(`Geração/Refinamento concluído! (v${version})`);
          setIsChatProcessing(false);
          setIsInitialGeneration(false); // Reset indicator
          clearInterval(intervalId); // Stop polling quando completo
          console.log('🛑 Polling encerrado: sessão concluída');
        } else if (status.status === 'failed') {
          console.log('❌ Sessão falhou');
          setIsChatProcessing(false);
          setIsInitialGeneration(false); // Reset indicator
          toast.error('Processamento falhou');
          clearInterval(intervalId); // Stop polling quando falha
          console.log('🛑 Polling encerrado: sessão falhou');
        }
      } catch (err) {
        console.error('Erro ao verificar status:', err);
      }
    }, 5000);

    return () => {
      console.log('🛑 Polling de documento encerrado');
      clearInterval(intervalId);
    };
  }, [isChatProcessing, currentSessionId]);

  // Detectar quando mensagens do chat têm diff
  useEffect(() => {
    if (chatMessages.length === 0) return;

    const lastMessage = chatMessages[chatMessages.length - 1];

    if (lastMessage?.data?.has_diff && lastMessage.data.old_document && lastMessage.data.new_document) {
      console.log('📊 Diff detectado na última mensagem');
      setOldDocument(lastMessage.data.old_document);
      setGeneratedDocument(lastMessage.data.new_document);
      setShowDiff(true);
      setIsDiffModalOpen(true);
      toast.success('Documento refinado! Clique em "Ver Diferenças" para comparar as alterações.');
    }
  }, [chatMessages]);

  // Converte mensagens do backend para formato do frontend
  const convertBackendMessage = (msg: any): ChatMessage => {
    return {
      id: msg.id,
      sender: msg.sender_type === 'assistant' ? 'agent' : msg.sender_type,
      text: msg.message_text,
      timestamp: new Date(msg.timestamp),
      type: msg.message_type === 'chat' ? undefined : msg.message_type as any,
      data: msg.metadata
    };
  };

  // Carrega histórico de chat
  const loadChatHistory = async (sessionId: string) => {
    try {
      console.log('🔄 Carregando histórico da sessão:', sessionId);
      const response = await getChatHistory(sessionId);
      const converted = response.messages.map(convertBackendMessage);
      console.log('✅ Mensagens convertidas:', converted.length);

      setChatMessages(prev => {
        const existingIds = new Set(prev.map(m => m.id));
        const newMessages = converted.filter(m => !existingIds.has(m.id));

        if (newMessages.length === 0) {
          return prev;
        }

        console.log(`✨ ${newMessages.length} novas mensagens adicionadas`);
        return [...prev, ...newMessages].sort((a, b) =>
          a.timestamp.getTime() - b.timestamp.getTime()
        );
      });

      return true;
    } catch (err) {
      console.error('❌ Failed to load chat history:', err);
      return false;
    }
  };

  // Handler para salvar edições do documento
  const handleSaveEdit = async (newContent: string) => {
    if (!currentSessionId) {
      toast.error('Nenhuma sessão ativa');
      return;
    }

    try {
      console.log('💾 Salvando documento editado...');
      await updateTaskExecutionFlow(currentSessionId, { content: newContent });
      setGeneratedDocument(newContent);
      toast.success('Documento salvo com sucesso!');
    } catch (error) {
      console.error('❌ Erro ao salvar documento:', error);
      toast.error('Erro ao salvar documento');
    }
  };

  const loadDocuments = async () => {
    if (!projectId) return;

    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(projectId)) {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const docs = await documentService.listDocuments(projectId);

      const transformedDocs: Document[] = docs.map((doc: any) => ({
        id: doc.id.toString(),
        projectId: doc.project_id.toString(),
        name: doc.name,
        originalName: doc.name,
        size: 0,
        type: doc.type,
        uploadedAt: doc.created_at,
        status: mapBackendStatus(doc.status),
        extractedEntities: [],
        requirements: [],
        analysisIssues: []
      }));

      setDocuments(transformedDocs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const mapBackendStatus = (status: string): DocumentStatus => {
    switch (status) {
      case 'uploaded': return DocumentStatus.UPLOADED;
      case 'analyzing': return DocumentStatus.ANALYZING;
      case 'analyzed': return DocumentStatus.ANALYZED;
      case 'error': return DocumentStatus.ERROR;
      default: return DocumentStatus.UPLOADED;
    }
  };

  const handleUpload = async (files: FileList) => {
    if (!projectId) {
      toast.error('Projeto não identificado');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const uploadPromises = Array.from(files).map(file =>
        documentService.uploadDocument(file, projectId)
      );

      const uploadedDocs = await Promise.all(uploadPromises);

      const transformedDocs: Document[] = uploadedDocs.map((doc: any) => ({
        id: doc.id.toString(),
        projectId: doc.project_id.toString(),
        name: doc.original_filename || doc.name,
        originalName: doc.original_filename || doc.name,
        size: doc.file_size || 0,
        type: doc.type || doc.file_type || 'unknown',
        uploadedAt: doc.uploaded_at || new Date().toISOString(),
        status: mapBackendStatus(doc.status),
        extractedEntities: [],
        requirements: [],
        analysisIssues: []
      }));

      setDocuments(prev => [...transformedDocs, ...prev]);
      setIsUploadModalOpen(false);
      toast.success(`${transformedDocs.length} documento(s) complementar(es) carregado(s)`);
    } catch (err) {
      console.error('Failed to upload documents:', err);
      toast.error('Erro no upload');
    } finally {
      setIsUploading(false);
    }
  };

  // Add message to chat
  const addChatMessage = (
    sender: 'user' | 'agent' | 'system',
    text: string,
    type?: 'status' | 'progress' | 'result' | 'document',
    data?: any
  ) => {
    const message: ChatMessage = {
      id: Date.now().toString() + Math.random(),
      sender,
      text,
      timestamp: new Date(),
      type,
      data
    };
    setChatMessages(prev => [...prev, message]);
  };

  // GERAR SEQUÊNCIA DE TAREFAS
  const startGeneration = async () => {
    if (!selectedSpecificationSessionId || !selectedAgentTaskSpecSessionId || !selectedTasksYamlSessionId) {
      toast.error('Selecione os 3 documentos obrigatórios primeiro! (botão "📋 Specs & Docs")');
      return;
    }

    setIsAnalyzing(true);
    setIsChatProcessing(true);
    setIsInitialGeneration(true); // Indicar que é geração inicial
    setChatMessages([]);
    setGeneratedDocument('');
    setCurrentLoadedVersion(null);

    try {
      const currentProjectId = projectId || 'project1';

      // Coletar IDs dos documentos complementares (opcional)
      const complementaryDocIds = documents.map(doc => doc.id);

      addChatMessage('system', `🚀 Iniciando geração de fluxo de execução de tarefas...`);
      addChatMessage('system', `📋 Especificação Funcional: ${selectedSpecificationSessionId}`);
      addChatMessage('system', `🤖 Agent/Task Spec: ${selectedAgentTaskSpecSessionId}`);
      addChatMessage('system', `📋 Tasks YAML: ${selectedTasksYamlSessionId}`);
      if (complementaryDocIds.length > 0) {
        addChatMessage('system', `📄 + ${complementaryDocIds.length} documento(s) externo(s)`);
      }

      // Chamar API de criação de task execution flow
      const response = await createTaskExecutionFlowSession({
        specification_session_id: selectedSpecificationSessionId,
        agent_task_spec_session_id: selectedAgentTaskSpecSessionId,
        tasks_yaml_session_id: selectedTasksYamlSessionId,
        uploaded_document_ids: complementaryDocIds,
        custom_instructions: customInstructions || undefined
      });

      setCurrentSessionId(response.session_id);
      console.log('📊 Sessão de task execution flow criada:', response.session_id);

      addChatMessage('agent', '✅ Sessão iniciada! Gerando fluxo de execução. Isso pode levar alguns minutos...');

      // Polling vai detectar quando terminar
      toast.success('Geração de fluxo de execução iniciada!');
    } catch (err) {
      console.error('Failed to start task execution flow generation:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao gerar fluxo de execução';
      toast.error(errorMessage);
      addChatMessage('system', `❌ Erro: ${errorMessage}`, 'status');
      setIsChatProcessing(false);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle chat messages for conversational refinement
  const handleSendChatMessage = async (message: string, actionType: 'refine' | 'chat' = 'refine') => {
    if (!currentSessionId) {
      toast.error('Gere um fluxo de execução primeiro');
      return;
    }

    setIsChatProcessing(true);
    setIsInitialGeneration(false); // É refinamento ou análise, não geração inicial

    const userMessage: ChatMessage = {
      id: `temp-user-${Date.now()}`,
      sender: 'user',
      text: message,
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);

    try {
      const actionLabel = actionType === 'chat' ? 'análise' : 'refinamento';
      console.log(`📤 Enviando mensagem de ${actionLabel}:`, message);

      const response = await refineTaskExecutionFlow(currentSessionId, {
        message: message,
        action_type: actionType
      });

      console.log('✅ Resposta do backend recebida:', response);
      await loadChatHistory(currentSessionId);
      toast.success(`Pedido de ${actionLabel} enviado!`);
    } catch (err) {
      console.error('❌ Failed to process chat message:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao processar mensagem';
      toast.error(errorMessage);
      setIsChatProcessing(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este documento complementar?')) {
      return;
    }

    try {
      await documentService.deleteDocument(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      toast.success('Documento excluído');
    } catch (err) {
      console.error('Failed to delete document:', err);
      toast.error('Erro ao excluir');
    }
  };

  const handleExport = (doc: Document, format: 'json' | 'csv' | 'pdf') => {
    const data = { document: doc.name };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${doc.name}_analysis.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Handler para histórico (similar ao de requisitos)
  const handleSelectHistorySession = async (sessionId: string, sessionName: string) => {
    console.log('📜 Selecionando sessão do histórico:', sessionId, sessionName);
    setCurrentSessionId(sessionId);

    try {
      const flow = await getTaskExecutionFlow(sessionId);
      if (flow.flow_document) {
        setGeneratedDocument(flow.flow_document);
        const version = flow.current_version || 1;
        setCurrentLoadedVersion(version);
        setDocumentFilename(`${sessionName || 'task_execution_flow'}_v${version}.md`);
      }
      await loadChatHistory(sessionId);
      toast.info(`Carregando: ${sessionName}`);
    } catch (err) {
      console.error('Erro ao carregar sessão:', err);
      toast.error('Erro ao carregar sessão');
    }
  };

  const handleSelectVersion = async (version: number) => {
    if (!currentSessionId) {
      toast.error('Nenhuma sessão ativa');
      return;
    }

    try {
      const versionData = await getTaskExecutionFlowVersion(currentSessionId, version);
      if (versionData && versionData.flow_document) {
        setGeneratedDocument(versionData.flow_document);
        setDocumentFilename(`task_execution_flow_v${version}.md`);
        setCurrentLoadedVersion(version);
        toast.success(`Versão ${version} carregada`);
      }
    } catch (err) {
      console.error('Erro ao carregar versão:', err);
      toast.error('Erro ao carregar versão');
    }
  };

  // Review: Analisa documento e mostra sugestões em modal
  const handleReview = async () => {
    if (!currentSessionId) {
      toast.error('Gere um fluxo de execução primeiro');
      return;
    }

    setIsReviewing(true);
    try {
      console.log('🔍 Iniciando revisão do fluxo de execução...');
      const result = await reviewTaskExecutionFlow(currentSessionId);
      setReviewSuggestions(result.suggestions);
      setIsReviewModalOpen(true);

      // Add review message to chat
      const reviewMsg: ChatMessage = {
        id: result.review_message_id || `review-${Date.now()}`,
        sender: 'agent',
        text: result.suggestions,
        timestamp: new Date(),
        type: 'result'
      };
      setChatMessages(prev => [...prev, reviewMsg]);

      toast.success('Revisão concluída!');
    } catch (error) {
      console.error('Erro ao revisar fluxo de execução:', error);
      toast.error('Erro ao revisar fluxo de execução. Tente novamente.');
    } finally {
      setIsReviewing(false);
    }
  };

  // Apply: Aplica sugestões de revisão com instruções opcionais
  const handleApplySuggestions = async (additionalInstructions?: string) => {
    if (!currentSessionId) {
      toast.error('Nenhuma sessão ativa');
      return;
    }

    setIsApplyingSuggestions(true);
    try {
      // Build refinement message
      let message = "Aplique as seguintes sugestões de melhoria ao documento:\n\n";
      message += reviewSuggestions;

      if (additionalInstructions) {
        message += `\n\n---\n\nINSTRUÇÕES COMPLEMENTARES:\n${additionalInstructions}`;
      }

      console.log('✏️ Aplicando sugestões de revisão...');

      // Send refinement request
      await refineTaskExecutionFlow(currentSessionId, {
        message: message,
        action_type: 'refine'
      });

      setIsReviewModalOpen(false);
      setIsChatProcessing(true);
      toast.success('Aplicando sugestões... Aguarde a atualização do documento.');
    } catch (error) {
      console.error('Erro ao aplicar sugestões:', error);
      toast.error('Erro ao aplicar sugestões. Tente novamente.');
    } finally {
      setIsApplyingSuggestions(false);
    }
  };

  return (
    <div className="documents-page-chat">
      <div className="page-header">
        <div className="header-content">
          <h1>🔄 Sequência de Tarefas {projectContext.isInProject && `- ${projectContext.projectName}`}</h1>
          <p>Gere o fluxo de execução de tarefas a partir de agents.yaml e tasks.yaml</p>
        </div>
      </div>

      {error && (
        <div className="error-banner">{error}</div>
      )}

      {isLoading ? (
        <div className="loading-container">
          <span className="spinner"></span> Carregando...
        </div>
      ) : (
        <div className="documents-chat-container">
          {/* LEFT SIDEBAR: Documents List + Configuration */}
          <div className="documents-sidebar">
            <div className="sidebar-header">
              <h3>📁 Docs Complementares ({documents.length})</h3>
              <div className="header-buttons">
                <button className="btn-upload-compact" onClick={() => setIsUploadModalOpen(true)}>
                  + Upload
                </button>
                <button className="btn-history-compact" onClick={() => setIsHistoryModalOpen(true)} title="Histórico de Fluxos de Tarefas">
                  📜 Histórico
                </button>
                {/* BOTÃO: Specs & Docs */}
                <button
                  className={`btn-yamls-compact ${(selectedSpecificationSessionId && selectedAgentTaskSpecSessionId && selectedTasksYamlSessionId) ? 'selected' : ''}`}
                  onClick={() => setIsYamlsModalOpen(true)}
                  title="Selecionar Documentos Base (Specification, Agent/Task Spec, Tasks YAML)"
                >
                  📋 {(selectedSpecificationSessionId && selectedAgentTaskSpecSessionId && selectedTasksYamlSessionId) ? 'Specs ✓' : 'Specs & Docs'}
                </button>
              </div>
            </div>

            {/* Mostrar Documentos selecionados */}
            {(selectedSpecificationSessionId || selectedAgentTaskSpecSessionId || selectedTasksYamlSessionId) && (
              <div style={{
                padding: '8px 12px',
                backgroundColor: '#d4edda',
                borderBottom: '1px solid #c3e6cb',
                fontSize: '11px',
                lineHeight: '1.6'
              }}>
                <strong>📋 Documentos Selecionados:</strong><br/>
                {selectedSpecificationSessionId && '✓ Especificação Funcional'}<br/>
                {selectedAgentTaskSpecSessionId && '✓ Especificação de Agentes/Tarefas'}<br/>
                {selectedTasksYamlSessionId && '✓ Tasks YAML'}<br/>
                {documents.length > 0 && `✓ + ${documents.length} documento(s) externo(s)`}
              </div>
            )}

            {/* Compact Documents List (complementares) */}
            <div className="documents-compact-list">
              {documents.length === 0 ? (
                <div className="empty-sidebar">
                  <p>Nenhum doc complementar</p>
                  <button onClick={() => setIsUploadModalOpen(true)}>
                    📤 Adicionar
                  </button>
                </div>
              ) : (
                documents.map(doc => (
                  <div key={doc.id} className={`document-item ${doc.status}`}>
                    <div className="doc-icon">📄</div>
                    <div className="doc-info">
                      <div className="doc-name" title={doc.name}>{doc.name}</div>
                      <div className="doc-status">
                        {doc.status === DocumentStatus.UPLOADED && '📎 Complementar'}
                        {doc.status === DocumentStatus.ANALYZING && '🔄 Processando'}
                        {doc.status === DocumentStatus.ANALYZED && '✅ Incluído'}
                        {doc.status === DocumentStatus.ERROR && '❌ Erro'}
                      </div>
                    </div>
                    <button className="btn-delete-small" onClick={() => handleDelete(doc.id)}>×</button>
                  </div>
                ))
              )}
            </div>

            {/* Configuration */}
            <div className="analysis-config">
              <h4>⚙️ Configuração</h4>

              <label>Instruções Customizadas (Opcional)</label>
              <textarea
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                placeholder="Ex: Enfatizar dependências entre tasks, detalhar input/output formats, etc..."
                rows={3}
              />

              <button
                className="btn-start-analysis"
                onClick={startGeneration}
                disabled={isAnalyzing || !selectedSpecificationSessionId || !selectedAgentTaskSpecSessionId || !selectedTasksYamlSessionId}
              >
                {isAnalyzing ? '⏳ Gerando...' : '🚀 Gerar Sequência de Tarefas'}
              </button>

              {(!selectedSpecificationSessionId || !selectedAgentTaskSpecSessionId || !selectedTasksYamlSessionId) && (
                <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                  ⚠️ Selecione os 3 documentos obrigatórios primeiro (📋 Specs & Docs)
                </p>
              )}

              <button
                className="btn-review"
                onClick={handleReview}
                disabled={isReviewing || !generatedDocument}
                title="Revisar fluxo de execução e obter sugestões de melhoria"
              >
                {isReviewing ? '⏳ Revisando...' : '🔍 Revisar Fluxo de Tarefas'}
              </button>

              {!generatedDocument && (
                <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                  💡 Gere um fluxo de execução primeiro para revisar
                </p>
              )}
            </div>
          </div>

          {/* MIDDLE AREA: Chat Interface with Progress Bar */}
          <div className="chat-area">
            {isChatProcessing && (
              <div className="generating-indicator">
                <div className="indicator-content">
                  {isInitialGeneration ? (
                    <>
                      <span className="spinner">⏳</span>
                      <strong>🚀 GERANDO FLUXO DE TAREFAS INICIAL...</strong>
                      <span className="blink">Aguarde, isso pode levar 1-3 minutos</span>
                    </>
                  ) : (
                    <>
                      <span className="spinner">⏳</span>
                      <strong>✏️ GERANDO REFINAMENTO...</strong>
                      <span className="blink">Processando com IA...</span>
                    </>
                  )}
                </div>
              </div>
            )}

            {isChatProcessing && (
              <ProgressBar
                percentage={progressPercentage}
                currentTask={currentTask}
                currentPhase={currentPhase}
                completedTasks={completedTasks}
                totalTasks={totalTasks}
              />
            )}

            <ChatInterface
              messages={chatMessages}
              onSendMessage={(msg) => handleSendChatMessage(msg, 'refine')}
              onAnalyze={(msg) => handleSendChatMessage(msg, 'chat')}
              isProcessing={false}
              executionId={currentExecutionId}
              sessionId={currentSessionId}
            />
          </div>

          {/* RIGHT PANEL: Document Actions */}
          <div className="actions-panel">
            {generatedDocument ? (
              <DocumentActionsCard
                filename={documentFilename}
                content={generatedDocument}
                executionId={currentExecutionId}
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
                <div className="placeholder-icon">🔄</div>
                <h3>Sequência de Tarefas não gerada</h3>
                <p>
                  1. Selecione YAMLs de configuração (⚙️ YAMLs Config):<br/>
                  &nbsp;&nbsp;&nbsp;• Agent/Task Spec (especificação de agentes e tarefas)<br/>
                  &nbsp;&nbsp;&nbsp;• Agents YAML (configuração de agentes)<br/>
                  &nbsp;&nbsp;&nbsp;• Tasks YAML (configuração de tarefas)<br/>
                  2. Opcionalmente adicione instruções customizadas<br/>
                  3. Clique em "🚀 Gerar Sequência de Tarefas"
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modals */}
      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUpload={handleUpload}
        isUploading={isUploading}
      />

      <DocumentViewModal
        isOpen={isViewModalOpen}
        document={selectedDocument}
        onClose={() => setIsViewModalOpen(false)}
        onExport={handleExport}
      />

      <MarkdownEditorModal
        isOpen={isEditorOpen}
        content={generatedDocument}
        filename={documentFilename}
        onSave={handleSaveEdit}
        onClose={() => setIsEditorOpen(false)}
      />

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

      {/* Modal de Histórico de Fluxos de Tarefas */}
      <TaskExecutionFlowHistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        projectId={projectId}
        onSelectSession={handleSelectHistorySession}
        onSelectVersion={handleSelectVersion}
      />

      <DiffViewerModal
        isOpen={isDiffModalOpen}
        oldDocument={oldDocument}
        newDocument={generatedDocument}
        onClose={() => setIsDiffModalOpen(false)}
      />

      {/* Modal para selecionar Specs & Docs */}
      <YamlSelectionModal
        isOpen={isYamlsModalOpen}
        onClose={() => setIsYamlsModalOpen(false)}
        onSelect={(specificationId, agentTaskSpecId, tasksYamlId) => {
          setSelectedSpecificationSessionId(specificationId);
          setSelectedAgentTaskSpecSessionId(agentTaskSpecId);
          setSelectedTasksYamlSessionId(tasksYamlId);
          setIsYamlsModalOpen(false);
          toast.success('3 documentos selecionados com sucesso! 🎉');
        }}
      />

      {/* Modal de Revisão de Sugestões */}
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

export default SequenciaTarefasPage;
