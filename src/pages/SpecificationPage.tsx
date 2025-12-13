/* src/pages/SpecificationPage.tsx */
/* CÓPIA do DocumentsPage com botão "Doctos Requisitos" adicionado */
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
import SpecificationHistoryModal from '../components/specification/SpecificationHistoryModal';
import DiffViewerModal from '../components/documents/DiffViewerModal';
import SpecificationGenerationModal from '../components/specification/SpecificationGenerationModal';
import RequirementsSelectionModal from '../components/specification/RequirementsSelectionModal';
import * as documentService from '../services/documentService';
import * as chatService from '../services/chatService';
import {
  createSpecificationSession,
  getSpecification,
  updateSpecification,
  listSpecificationVersions,
  getSpecificationVersion
} from '../services/specificationService';
import {
  refineSpecification,
  getChatHistory,
  getSessionStatus
} from '../services/specificationChatService';
import { useNavigation } from '../contexts/NavigationContext';
import { toast } from 'react-toastify';
import './DocumentsPage.css'; // USA O MESMO CSS

const SpecificationPage: React.FC = () => {
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
  const [analysisInstructions, setAnalysisInstructions] = useState('');

  // NOVO: Estado para modal de seleção de requisitos
  const [isRequirementsModalOpen, setIsRequirementsModalOpen] = useState(false);
  const [selectedRequirementsSessionId, setSelectedRequirementsSessionId] = useState<string>('');
  const [selectedRequirementsVersion, setSelectedRequirementsVersion] = useState<number>(1);
  const [selectedRequirementsName, setSelectedRequirementsName] = useState<string>('');
  const [selectedRequirementsContent, setSelectedRequirementsContent] = useState<string>('');

  // Chat states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatProcessing, setIsChatProcessing] = useState(false);
  const [currentExecutionId, setCurrentExecutionId] = useState<string | undefined>(undefined);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);

  // Progress states
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [currentTask, setCurrentTask] = useState<string>('');
  const [currentPhase, setCurrentPhase] = useState<string>('');
  const [completedTasks, setCompletedTasks] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);

  // Document states
  const [generatedDocument, setGeneratedDocument] = useState<string>('');
  const [documentFilename, setDocumentFilename] = useState<string>('especificacao.md');
  const [currentLoadedVersion, setCurrentLoadedVersion] = useState<number | null>(null);

  // Diff states
  const [showDiff, setShowDiff] = useState(false);
  const [oldDocument, setOldDocument] = useState<string>('');

  // Modal states
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);

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

        if (status.status === 'completed' && status.specification_document) {
          console.log('✅ Sessão concluída, atualizando documento...');
          setGeneratedDocument(status.specification_document);
          const version = status.current_version || 1;
          setCurrentLoadedVersion(version);
          setDocumentFilename(`especificacao_v${version}.md`);
          await loadChatHistory(currentSessionId);
          toast.success(`Geração/Refinamento concluído! (v${version})`);
          setIsChatProcessing(false);
        } else if (status.status === 'failed') {
          console.log('❌ Sessão falhou');
          setIsChatProcessing(false);
          toast.error('Processamento falhou');
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
      await updateSpecification(currentSessionId, { content: newContent });
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
      const docs = await documentService.listDocuments(parseInt(projectId));

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

  // GERAR ESPECIFICAÇÃO
  const startGeneration = async () => {
    if (!selectedRequirementsSessionId) {
      toast.error('Selecione um documento de requisitos primeiro (botão "📋 Doctos Requisitos")');
      return;
    }

    setIsAnalyzing(true);
    setIsChatProcessing(true);
    setChatMessages([]);
    setGeneratedDocument('');
    setCurrentLoadedVersion(null);

    try {
      const currentProjectId = projectId || 'project1';

      // Coletar IDs dos documentos complementares (opcional)
      const complementaryDocIds = documents.map(doc => doc.id);

      addChatMessage('system', `🚀 Iniciando geração de especificação funcional...`);
      addChatMessage('system', `📋 Documento de requisitos base: ${selectedRequirementsName} (v${selectedRequirementsVersion})`);

      if (complementaryDocIds.length > 0) {
        addChatMessage('system', `📎 ${complementaryDocIds.length} documento(s) complementar(es) incluído(s)`);
      }

      // Chamar API de criação de especificação
      const response = await createSpecificationSession({
        project_id: currentProjectId,
        requirements_session_id: selectedRequirementsSessionId,
        requirements_version: selectedRequirementsVersion,
        complementary_document_ids: complementaryDocIds,
        session_name: `Especificação - ${new Date().toLocaleDateString('pt-BR')}`,
        detail_level: 'detailed',
        target_audience: 'mixed',
        include_data_model: true,
        include_use_cases: true,
        include_business_rules: true,
        include_glossary: true,
        custom_instructions: analysisInstructions || undefined
      });

      setCurrentSessionId(response.session_id);
      console.log('📊 Sessão de especificação criada:', response.session_id);

      addChatMessage('agent', '✅ Sessão iniciada! Gerando especificação funcional. Isso pode levar alguns minutos...');

      // Polling vai detectar quando terminar
      toast.success('Geração de especificação iniciada!');
    } catch (err) {
      console.error('Failed to start specification generation:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao gerar especificação';
      toast.error(errorMessage);
      addChatMessage('system', `❌ Erro: ${errorMessage}`, 'status');
      setIsChatProcessing(false);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle chat messages for conversational refinement
  const handleSendChatMessage = async (message: string) => {
    if (!currentSessionId) {
      toast.error('Gere uma especificação primeiro');
      return;
    }

    setIsChatProcessing(true);

    const userMessage: ChatMessage = {
      id: `temp-user-${Date.now()}`,
      sender: 'user',
      text: message,
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);

    try {
      console.log('📤 Enviando mensagem de refinamento:', message);

      const response = await refineSpecification(currentSessionId, {
        message: message
      });

      console.log('✅ Resposta do backend recebida:', response);
      await loadChatHistory(currentSessionId);
      toast.success('Pedido de refinamento enviado!');
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
      const spec = await getSpecification(sessionId);
      if (spec.specification_document) {
        setGeneratedDocument(spec.specification_document);
        const version = spec.current_version || 1;
        setCurrentLoadedVersion(version);
        setDocumentFilename(`${sessionName || 'especificacao'}_v${version}.md`);
      }
      await loadChatHistory(sessionId);
      toast.info(`Carregando: ${sessionName} (v${spec.current_version || 1})`);
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
      const versionData = await getSpecificationVersion(currentSessionId, version);
      if (versionData && versionData.specification_document) {
        setGeneratedDocument(versionData.specification_document);
        setDocumentFilename(`especificacao_v${version}.md`);
        setCurrentLoadedVersion(version);
        toast.success(`Versão ${version} carregada`);
      }
    } catch (err) {
      console.error('Erro ao carregar versão:', err);
      toast.error('Erro ao carregar versão');
    }
  };

  return (
    <div className="documents-page-chat">
      <div className="page-header">
        <div className="header-content">
          <h1>📝 Especificação Funcional {projectContext.isInProject && `- ${projectContext.projectName}`}</h1>
          <p>Gere especificações funcionais a partir de documentos de requisitos</p>
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
                <button className="btn-history-compact" onClick={() => setIsHistoryModalOpen(true)} title="Histórico de Especificações">
                  📜 Histórico
                </button>
                {/* NOVO BOTÃO: Doctos Requisitos */}
                <button
                  className={`btn-requirements-compact ${selectedRequirementsSessionId ? 'selected' : ''}`}
                  onClick={() => setIsRequirementsModalOpen(true)}
                  title="Selecionar Documento de Requisitos Base"
                >
                  📋 {selectedRequirementsSessionId ? 'Requisitos ✓' : 'Requisitos'}
                </button>
              </div>
            </div>

            {/* Mostrar requisitos selecionados */}
            {selectedRequirementsSessionId && (
              <div style={{
                padding: '8px 12px',
                backgroundColor: '#d4edda',
                borderBottom: '1px solid #c3e6cb',
                fontSize: '12px'
              }}>
                <strong>📋 Base:</strong> {selectedRequirementsName} (v{selectedRequirementsVersion})
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

              <label>Instruções Adicionais</label>
              <textarea
                value={analysisInstructions}
                onChange={(e) => setAnalysisInstructions(e.target.value)}
                placeholder="Ex: Focar em requisitos de segurança, detalhar casos de uso..."
                rows={3}
              />

              <button
                className="btn-start-analysis"
                onClick={startGeneration}
                disabled={isAnalyzing || !selectedRequirementsSessionId}
              >
                {isAnalyzing ? '⏳ Gerando...' : '🚀 Gerar Especificação'}
              </button>

              {!selectedRequirementsSessionId && (
                <p style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                  ⚠️ Selecione um documento de requisitos primeiro
                </p>
              )}
            </div>
          </div>

          {/* MIDDLE AREA: Chat Interface with Progress Bar */}
          <div className="chat-area">
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
              onSendMessage={handleSendChatMessage}
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
                <div className="placeholder-icon">📄</div>
                <h3>Especificação não gerada</h3>
                <p>1. Selecione um documento de requisitos (📋 Requisitos)<br/>
                   2. Opcionalmente adicione docs complementares<br/>
                   3. Clique em "Gerar Especificação"</p>
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

      {/* Modal de Histórico de Especificações */}
      <SpecificationHistoryModal
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

      {/* NOVO: Modal para selecionar documento de requisitos base */}
      <RequirementsSelectionModal
        isOpen={isRequirementsModalOpen}
        onClose={() => setIsRequirementsModalOpen(false)}
        onSelect={(sessionId, sessionName, version, content) => {
          setSelectedRequirementsSessionId(sessionId);
          setSelectedRequirementsName(sessionName);
          setSelectedRequirementsVersion(version);
          setSelectedRequirementsContent(content);
          toast.success(`Requisitos selecionados: ${sessionName} v${version}`);
        }}
      />
    </div>
  );
};

export default SpecificationPage;
