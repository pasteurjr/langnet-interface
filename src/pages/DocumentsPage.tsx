import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Document, DocumentStatus } from '../types';
import DocumentCard from '../components/documents/DocumentCard';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import DocumentViewModal from '../components/documents/DocumentViewModal';
import ChatInterface, { ChatMessage } from '../components/documents/ChatInterface';
import ProgressBar from '../components/documents/ProgressBar';
import DocumentActionsCard from '../components/documents/DocumentActionsCard';
import * as documentService from '../services/documentService';
import langnetService from '../services/langnetService';
import * as chatService from '../services/chatService';
import * as analysisService from '../services/documentAnalysisService';
import { useNavigation } from '../contexts/NavigationContext';
import { toast } from 'react-toastify';
import './DocumentsPage.css';

const DocumentsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { projectContext } = useNavigation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | 'all'>('all');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisInstructions, setAnalysisInstructions] = useState('');
  const [enableWebResearch, setEnableWebResearch] = useState(true);
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);

  // Chat states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatProcessing, setIsChatProcessing] = useState(false);
  const [currentExecutionId, setCurrentExecutionId] = useState<string | undefined>(undefined);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  // Progress states (separate from chat)
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [currentTask, setCurrentTask] = useState<string>('');
  const [currentPhase, setCurrentPhase] = useState<string>('');
  const [completedTasks, setCompletedTasks] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);

  // Document states
  const [generatedDocument, setGeneratedDocument] = useState<string>('');
  const [documentFilename, setDocumentFilename] = useState<string>('requisitos.md');

  useEffect(() => {
    loadDocuments();
  }, [projectId]);

  // Reload chat history periodically while processing
  useEffect(() => {
    if (!isChatProcessing || !currentSessionId) return;

    const intervalId = setInterval(() => {
      console.log('🔄 Reloading chat history...');
      loadChatHistory(currentSessionId);
    }, 3000); // Reload every 3 seconds

    return () => clearInterval(intervalId);
  }, [isChatProcessing, currentSessionId]);

  // Converte mensagens do backend para formato do frontend
  const convertBackendMessage = (msg: chatService.ChatMessage): ChatMessage => {
    return {
      id: msg.id,
      sender: msg.sender_type === 'assistant' ? 'agent' : msg.sender_type,
      text: msg.message_text,
      timestamp: new Date(msg.timestamp),
      type: msg.message_type === 'chat' ? undefined : msg.message_type as any,
      data: msg.metadata
    };
  };

  // Carrega histórico de chat quando houver sessionId
  const loadChatHistory = async (sessionId: string) => {
    try {
      console.log('🔄 Carregando histórico da sessão:', sessionId);
      const response = await chatService.loadChatMessages(sessionId);
      console.log('📨 Resposta do backend:', response);
      const converted = response.messages.map(convertBackendMessage);
      console.log('✅ Mensagens convertidas:', converted);
      setChatMessages(converted);
    } catch (err) {
      console.error('❌ Failed to load chat history:', err);
    }
  };

  // Carrega documento de requisitos gerado
  const loadGeneratedDocument = async (sessionId: string) => {
    try {
      console.log('📄 Carregando documento gerado para sessão:', sessionId);
      const requirementsService = await import('../services/requirementsService');
      const doc = await requirementsService.getRequirementsDocument(sessionId);

      if (doc && doc.content) {
        console.log('✅ Documento carregado:', doc.content.substring(0, 100) + '...');
        setGeneratedDocument(doc.content);
        setDocumentFilename(doc.filename || 'requisitos.md');
      }
    } catch (err) {
      console.error('❌ Failed to load generated document:', err);
    }
  };

  const loadDocuments = async () => {
    if (!projectId) return;

    // Validate UUID format first
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(projectId)) {
      setError(`❌ ID de projeto inválido: ${projectId}\n\n` +
               `O ID do projeto deve ser um UUID válido.\n` +
               `Verifique a URL: /project/{uuid-válido}/documents\n\n` +
               `Exemplo: /project/a62c0d72-89f3-4cca-9da2-5a88867cd32e/documents`);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      const docs = await documentService.listDocuments(parseInt(projectId));

      // Transform backend response to frontend format
      const transformedDocs: Document[] = docs.map((doc: any) => ({
        id: doc.id.toString(),
        projectId: doc.project_id.toString(),
        name: doc.name,
        originalName: doc.name,
        size: 0, // Backend doesn't return size
        type: doc.type,
        uploadedAt: doc.created_at,
        status: mapBackendStatus(doc.status),
        extractedEntities: [],
        requirements: [],
        analysisIssues: [],
        analysisResults: doc.analysis_result ? parseAnalysisResult(doc.analysis_result) : undefined
      }));

      setDocuments(transformedDocs);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError(err instanceof Error ? err.message : 'Failed to load documents');
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

  const parseAnalysisResult = (analysisResultStr: string): any => {
    try {
      return typeof analysisResultStr === 'string' ? JSON.parse(analysisResultStr) : analysisResultStr;
    } catch {
      return null;
    }
  };

  const handleUpload = async (files: FileList) => {
    if (!projectId) {
      toast.error('Projeto não identificado');
      return;
    }

    // Validate project ID format (UUID)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(projectId)) {
      toast.error(`ID de projeto inválido: ${projectId}. Verifique a URL.`);
      setError(`ID de projeto inválido. URL esperada: /project/{project-id}/documents`);
      return;
    }

    // Check if user is authenticated
    const token = localStorage.getItem('accessToken');
    if (!token) {
      toast.error('Você precisa fazer login para fazer upload de documentos');
      setError('Não autenticado. Por favor, faça login primeiro.');
      return;
    }

    console.log('📤 Starting upload...', {
      projectId,
      filesCount: files.length,
      instructions: analysisInstructions,
      webResearch: enableWebResearch,
      hasToken: !!token
    });

    setIsUploading(true);
    setError(null);

    try {
      console.log('📁 Uploading files to backend...');
      const uploadPromises = Array.from(files).map(file =>
        documentService.uploadDocument(file, projectId)
      );

      const uploadedDocs = await Promise.all(uploadPromises);
      console.log('✅ Files uploaded successfully:', uploadedDocs);

      // Transform and add to documents list
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
        analysisIssues: [],
        analysisInstructions: analysisInstructions,
        enableWebResearch: enableWebResearch
      }));

      setDocuments(prev => [...transformedDocs, ...prev]);
      setIsUploadModalOpen(false);
      toast.success(`${transformedDocs.length} arquivo(s) carregado(s) com sucesso. Use o botão "Extrair Requisitos" para iniciar a análise.`);
    } catch (err) {
      console.error('❌ Failed to upload documents:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload documents';
      setError(errorMessage);
      toast.error(`Erro no upload: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback((executionId: string) => {
    // Close existing connection
    if (websocket) {
      websocket.close();
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/langnet/${executionId}`);

    ws.onopen = () => {
      console.log('WebSocket connected for execution:', executionId);
      addChatMessage('system', '🔌 Conectado ao sistema de análise em tempo real');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message:', data);

      if (data.type === 'progress') {
        addChatMessage('system', data.message, 'progress', data);
      } else if (data.type === 'task_complete') {
        addChatMessage('agent', `✅ ${data.message}`, 'status', data);
      } else if (data.type === 'document_generated') {
        addChatMessage('agent', data.document, 'document', data);
      } else if (data.type === 'error') {
        addChatMessage('system', `❌ Erro: ${data.message}`, 'status', data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      addChatMessage('system', '❌ Erro na conexão em tempo real');
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      addChatMessage('system', '🔌 Conexão encerrada');
    };

    setWebsocket(ws);
  }, [websocket]);

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

  const startAnalysis = async () => {
    if (documents.length === 0) {
      toast.error('Faça upload de documentos primeiro');
      return;
    }

    setIsAnalyzing(true);
    setIsChatProcessing(true);

    try {
      if (!projectId) return;

      // Get all uploaded document IDs
      const documentIds = documents.map(doc => doc.id);

      if (documentIds.length === 0) {
        toast.warning('Nenhum documento para análise');
        setIsAnalyzing(false);
        setIsChatProcessing(false);
        return;
      }

      // Start batch analysis using new API
      const response = await analysisService.analyzeDocumentsBatch({
        document_ids: documentIds,
        project_id: projectId,
        instructions: analysisInstructions,
        use_web_research: enableWebResearch
      });

      // Set session and execution IDs
      setCurrentSessionId(response.session_id);
      setCurrentExecutionId(response.execution_id);

      console.log('📊 Sessão criada:', response.session_id);
      console.log('🔍 Execution ID:', response.execution_id);

      // Load chat history from database
      await loadChatHistory(response.session_id);
      console.log('💬 Mensagens carregadas:', chatMessages.length);

      // Connect WebSocket for real-time updates
      const ws = analysisService.connectToExecutionWebSocket(
        response.execution_id,
        (data) => {
          console.log('📨 WebSocket message received:', data.type);

          // Handle WebSocket messages - UPDATE PROGRESS ONLY, NO CHAT MESSAGES
          if (data.type === 'task_started') {
            setCurrentTask(data.task || 'Iniciando tarefa...');
            setCurrentPhase(data.phase || '');
          } else if (data.type === 'task_completed') {
            setCompletedTasks(prev => prev + 1);
          } else if (data.type === 'progress') {
            setProgressPercentage(data.percentage || 0);
            if (data.current_task) setCurrentTask(data.current_task);
            if (data.current_phase) setCurrentPhase(data.current_phase);
            if (data.completed_tasks !== undefined) setCompletedTasks(data.completed_tasks);
            if (data.total_tasks !== undefined) setTotalTasks(data.total_tasks);
          } else if (data.type === 'execution_completed') {
            console.log('✅ Execution completed, loading final document...');
            setProgressPercentage(100);
            setCurrentTask('Análise concluída!');

            // Load final chat history and document from database
            loadChatHistory(response.session_id);
            loadGeneratedDocument(response.session_id);

            setIsChatProcessing(false);
            // Close WebSocket
            if (ws) ws.close();
          } else if (data.type === 'execution_failed') {
            setCurrentTask(`❌ Erro: ${data.error || 'Erro desconhecido'}`);
            setIsChatProcessing(false);
            // Close WebSocket
            if (ws) ws.close();
          }
        },
        (error) => {
          console.error('WebSocket error:', error);
          setIsChatProcessing(false);
        },
        () => {
          console.log('WebSocket closed');
          setIsChatProcessing(false);
        }
      );

      setWebsocket(ws);

      toast.success('Análise iniciada com sucesso!');
    } catch (err) {
      console.error('Failed to analyze documents:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze documents';
      toast.error(`Erro na análise: ${errorMessage}`);
      addChatMessage('system', `❌ Erro: ${errorMessage}`, 'status');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle chat messages for conversational refinement
  const handleSendChatMessage = async (message: string) => {
    if (!currentSessionId) {
      toast.error('Inicie uma análise primeiro');
      return;
    }

    setIsChatProcessing(true);

    try {
      // Send refinement request to backend
      const response = await chatService.refineRequirements(currentSessionId, {
        message: message
      });

      // Add user and agent messages from response
      await loadChatHistory(currentSessionId);

      toast.success('Pedido de refinamento enviado!');
    } catch (err) {
      console.error('Failed to process chat message:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao processar mensagem';
      toast.error(errorMessage);
      addChatMessage('system', `❌ ${errorMessage}`, 'status');
    } finally {
      setIsChatProcessing(false);
    }
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [websocket]);

  const handleView = (document: Document) => {
    setSelectedDocument(document);
    setIsViewModalOpen(true);
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este documento?')) {
      return;
    }

    try {
      await documentService.deleteDocument(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      toast.success('Documento excluído com sucesso');
    } catch (err) {
      console.error('Failed to delete document:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete document';
      setError(errorMsg);
      toast.error(`Erro ao excluir: ${errorMsg}`);
    }
  };


  const handleExport = (doc: Document, format: 'json' | 'csv' | 'pdf') => {
    // Simular exportação
    const data = {
      document: doc.name,
      entities: doc.extractedEntities.length,
      requirements: doc.requirements.length,
      issues: doc.analysisIssues.length
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${doc.name}_analysis.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Filtrar documentos
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.originalName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusCount = (status: DocumentStatus) => {
    return documents.filter(doc => doc.status === status).length;
  };

  return (
    <div className="documents-page-chat">
      <div className="page-header">
        <div className="header-content">
          <h1>📄 Análise de Requisitos {projectContext.isInProject && `- ${projectContext.projectName}`}</h1>
          <p>Upload de documentos e extração inteligente de requisitos</p>
        </div>
      </div>

      {error && (
        <div className="error-banner">{error}</div>
      )}

      {isLoading ? (
        <div className="loading-container">
          <span className="spinner"></span> Carregando documentos...
        </div>
      ) : (
        <div className="documents-chat-container">
          {/* LEFT SIDEBAR: Documents List + Configuration */}
          <div className="documents-sidebar">
            <div className="sidebar-header">
              <h3>📁 Documentos ({documents.length})</h3>
              <button className="btn-upload-compact" onClick={() => setIsUploadModalOpen(true)}>
                + Upload
              </button>
            </div>

            {/* Compact Documents List */}
            <div className="documents-compact-list">
              {documents.length === 0 ? (
                <div className="empty-sidebar">
                  <p>Nenhum documento</p>
                  <button onClick={() => setIsUploadModalOpen(true)}>
                    📤 Fazer Upload
                  </button>
                </div>
              ) : (
                documents.map(doc => (
                  <div key={doc.id} className={`document-item ${doc.status}`}>
                    <div className="doc-icon">📄</div>
                    <div className="doc-info">
                      <div className="doc-name" title={doc.name}>{doc.name}</div>
                      <div className="doc-status">
                        {doc.status === DocumentStatus.UPLOADED && '⏸️ Pendente'}
                        {doc.status === DocumentStatus.ANALYZING && '🔄 Analisando'}
                        {doc.status === DocumentStatus.ANALYZED && '✅ Analisado'}
                        {doc.status === DocumentStatus.ERROR && '❌ Erro'}
                      </div>
                    </div>
                    <button className="btn-delete-small" onClick={() => handleDelete(doc.id)}>×</button>
                  </div>
                ))
              )}
            </div>

            {/* Analysis Configuration */}
            <div className="analysis-config">
              <h4>⚙️ Configuração</h4>

              <label>Instruções para Análise</label>
              <textarea
                value={analysisInstructions}
                onChange={(e) => setAnalysisInstructions(e.target.value)}
                placeholder="Ex: Focar em requisitos de segurança..."
                rows={3}
              />

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={enableWebResearch}
                  onChange={(e) => setEnableWebResearch(e.target.checked)}
                />
                <span>🌐 Pesquisa Web {enableWebResearch && '(6-10 min)'}</span>
              </label>

              <button
                className="btn-start-analysis"
                onClick={startAnalysis}
                disabled={isAnalyzing || documents.filter(d => d.status === DocumentStatus.UPLOADED).length === 0}
              >
                {isAnalyzing ? '⏳ Analisando...' : '🚀 Iniciar Análise'}
              </button>
            </div>
          </div>

          {/* MIDDLE AREA: Chat Interface with Progress Bar */}
          <div className="chat-area">
            {/* Progress Bar - OUTSIDE chat window */}
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
              isProcessing={isChatProcessing}
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
                onEdit={() => {
                  // TODO: Open editor modal
                  console.log('Edit document');
                }}
                onView={() => {
                  // TODO: Open viewer modal
                  console.log('View document');
                }}
                onExportPDF={async () => {
                  const { exportMarkdownToPDF } = await import('../services/pdfExportService');
                  await exportMarkdownToPDF(generatedDocument, documentFilename.replace('.md', '.pdf'));
                }}
              />
            ) : (
              <div className="no-document-placeholder">
                <div className="placeholder-icon">📄</div>
                <h3>Documento não gerado</h3>
                <p>Faça upload de documentos e inicie a análise para gerar o documento de requisitos.</p>
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
    </div>
  );
};

export default DocumentsPage;
