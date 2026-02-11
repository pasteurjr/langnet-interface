import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Document, DocumentStatus } from '../types';
import DocumentCard from '../components/documents/DocumentCard';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import DocumentViewModal from '../components/documents/DocumentViewModal';
import ChatInterface, { ChatMessage } from '../components/documents/ChatInterface';
import ProgressBar from '../components/documents/ProgressBar';
import DocumentActionsCard from '../components/documents/DocumentActionsCard';
import MarkdownEditorModal from '../components/documents/MarkdownEditorModal';
import MarkdownViewerModal from '../components/documents/MarkdownViewerModal';
import RequirementsHistoryModal from '../components/documents/RequirementsHistoryModal';
import DiffViewerModal from '../components/documents/DiffViewerModal';
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

  // Reload chat history periodically while processing
  useEffect(() => {
    if (!isChatProcessing || !currentSessionId) return;

    const intervalId = setInterval(() => {
      console.log('🔄 Reloading chat history...');
      loadChatHistory(currentSessionId);
    }, 2000); // Reload every 2 seconds for real-time updates

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
        const status = await chatService.getSessionStatus(currentSessionId);
        console.log('📊 Status atual:', status.status);

        // Se status mudou para completed, atualizar documento
        if (status.status === 'completed' && status.requirements_document) {
          console.log('✅ Sessão concluída, atualizando documento...');

          // Atualizar documento
          setGeneratedDocument(status.requirements_document);

          // Recarregar mensagens do chat para pegar mensagem de conclusão
          await loadChatHistory(currentSessionId);

          toast.success('Refinamento concluído!');
          setIsChatProcessing(false);
        } else if (status.status === 'processing') {
          console.log('⏳ Refinamento em andamento...');
          // Continua polling
        } else if (status.status === 'failed') {
          console.log('❌ Sessão falhou');
          setIsChatProcessing(false);
          toast.error('Processamento falhou');
        }
      } catch (err) {
        console.error('Erro ao verificar status:', err);
      }
    }, 5000); // Verificar a cada 5 segundos

    return () => {
      console.log('🛑 Polling de documento encerrado');
      clearInterval(intervalId);
    };
  }, [isChatProcessing, currentSessionId]);

  // Detectar quando mensagens do chat foram atualizadas e verificar se tem diff
  useEffect(() => {
    if (chatMessages.length === 0) return;

    const lastMessage = chatMessages[chatMessages.length - 1];

    // Verificar se a última mensagem tem dados de diff
    if (lastMessage?.data?.has_diff && lastMessage.data.old_document && lastMessage.data.new_document) {
      console.log('📊 Diff detectado na última mensagem:', lastMessage);

      setOldDocument(lastMessage.data.old_document);
      setGeneratedDocument(lastMessage.data.new_document);
      setShowDiff(true);
      setIsDiffModalOpen(true); // Abrir modal automaticamente
      toast.success('Documento refinado! Clique em "Ver Diferenças" para comparar as alterações.');
    }
  }, [chatMessages]);

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

      // MERGE STRATEGY: Adicionar apenas mensagens novas, não substituir todas
      setChatMessages(prev => {
        // Criar set com IDs das mensagens existentes
        const existingIds = new Set(prev.map(m => m.id));

        // Filtrar apenas mensagens novas que ainda não existem
        const newMessages = converted.filter(m => !existingIds.has(m.id));

        // Se não há mensagens novas, retornar estado anterior
        if (newMessages.length === 0) {
          console.log('📭 Nenhuma mensagem nova encontrada');
          return prev;
        }

        console.log(`✨ ${newMessages.length} novas mensagens adicionadas`);

        // Combinar mensagens existentes com novas e ordenar por timestamp
        return [...prev, ...newMessages].sort((a, b) =>
          a.timestamp.getTime() - b.timestamp.getTime()
        );
      });

      return true;
    } catch (err) {
      console.error('❌ Failed to load chat history:', err);
      toast.error('Erro ao carregar mensagens do chat');
      setIsChatProcessing(false); // Garantir que desbloqueia em caso de erro
      return false;
    }
  };

  // Carrega documento de requisitos gerado
  const loadGeneratedDocument = async (sessionId: string) => {
    try {
      console.log('📄 loadGeneratedDocument: Iniciando para session', sessionId);
      const requirementsService = await import('../services/requirementsService');
      const doc = await requirementsService.getRequirementsDocument(sessionId);

      console.log('📄 loadGeneratedDocument: Resposta recebida', {
        hasDoc: !!doc,
        hasContent: !!doc?.content,
        contentLength: doc?.content?.length || 0,
        filename: doc?.filename,
        status: doc?.status
      });

      if (doc && doc.content && doc.content.trim()) {
        console.log('✅ loadGeneratedDocument: Documento carregado com sucesso!', {
          length: doc.content.length,
          preview: doc.content.substring(0, 100) + '...'
        });
        setGeneratedDocument(doc.content);
        setDocumentFilename(doc.filename || 'requisitos.md');

        // SUCESSO: Desligar polling agora que documento foi carregado
        console.log('✅ Documento carregado - desligando polling');
        setIsChatProcessing(false);
      } else {
        console.warn('⚠️ loadGeneratedDocument: Documento vazio ou não encontrado', {
          hasDoc: !!doc,
          hasContent: !!doc?.content,
          isEmpty: doc?.content?.trim() === ''
        });
      }
    } catch (err) {
      console.error('❌ loadGeneratedDocument: Erro ao carregar:', err);
      if (err instanceof Error) {
        console.error('   Detalhes:', {
          message: err.message,
          name: err.name,
          stack: err.stack?.split('\n').slice(0, 3)
        });
      }
    }
  };

  // Handler para salvar edições do documento
  const handleSaveEdit = async (newContent: string) => {
    if (!currentSessionId) {
      console.error('❌ handleSaveEdit: Nenhuma sessão ativa');
      alert('❌ Erro: Nenhuma sessão ativa');
      return;
    }

    try {
      console.log('💾 handleSaveEdit: Salvando documento editado...', {
        sessionId: currentSessionId,
        contentLength: newContent.length
      });

      const requirementsService = await import('../services/requirementsService');
      await requirementsService.updateRequirementsDocument(currentSessionId, newContent);

      // Atualiza o estado local
      setGeneratedDocument(newContent);

      console.log('✅ handleSaveEdit: Documento salvo com sucesso!');
      alert('✅ Documento salvo com sucesso!');
    } catch (error) {
      console.error('❌ handleSaveEdit: Erro ao salvar documento:', error);
      alert('❌ Erro ao salvar documento. Veja o console para detalhes.');
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
      const docs = await documentService.listDocuments(projectId);

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
            // NÃO DESLIGAR isChatProcessing AQUI - deixar polling continuar até documento carregar

            const sessionId = response.session_id;

            // Load final chat history and document from database
            loadChatHistory(sessionId);

            // GARANTIA MULTI-CAMADA: Tentar carregar documento múltiplas vezes
            console.log('🔄 Tentativa #1: Carregando documento imediatamente...');
            loadGeneratedDocument(sessionId);

            // Retry após 2 segundos (fallback se primeira tentativa falhar)
            setTimeout(() => {
              console.log('🔄 Tentativa #2: Retry após 2s...');
              loadGeneratedDocument(sessionId);
            }, 2000);

            // Retry final após 5 segundos
            setTimeout(() => {
              console.log('🔄 Tentativa #3: Retry final após 5s...');
              loadGeneratedDocument(sessionId);
            }, 5000);

            // Timeout de segurança: Desligar polling após 30s se documento não carregar
            setTimeout(() => {
              console.log('⏱️  Timeout: Desligando polling após 30s');
              setIsChatProcessing(false);
            }, 30000);

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

    // OPTIMISTIC UPDATE: Adicionar mensagem do usuário imediatamente
    const userMessage: ChatMessage = {
      id: `temp-user-${Date.now()}`,
      sender: 'user',
      text: message,
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    console.log('💬 Mensagem do usuário adicionada otimisticamente');

    try {
      console.log('📤 Enviando mensagem de refinamento:', message);

      // Send refinement request to backend
      const response = await chatService.refineRequirements(currentSessionId, {
        message: message
      });

      console.log('✅ Resposta do backend recebida:', response);

      // Recarregar histórico do chat para mostrar mensagens do backend
      // O merge strategy garantirá que não haja duplicatas
      const success = await loadChatHistory(currentSessionId);

      if (!success) {
        console.error('❌ Falha ao recarregar mensagens do chat');
        setIsChatProcessing(false);
        return;
      }

      console.log('✅ Mensagens recarregadas com sucesso');
      toast.success('Pedido de refinamento enviado!');

      // Don't stop processing here - let polling detect completion
    } catch (err) {
      console.error('❌ Failed to process chat message:', err);
      const errorMessage = err instanceof Error ? err.message : 'Erro ao processar mensagem';
      toast.error(errorMessage);
      addChatMessage('system', `❌ ${errorMessage}`, 'status');
      setIsChatProcessing(false); // Only stop processing on error
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

  // Handler para quando usuário seleciona uma sessão do histórico
  const handleSelectHistorySession = async (sessionId: string, sessionName: string) => {
    console.log('📜 Selecionando sessão do histórico:', sessionId, sessionName);

    // Atualiza o sessionId atual
    setCurrentSessionId(sessionId);

    // IMPORTANTE: Carrega chat PRIMEIRO para evitar race condition com useEffect
    await loadChatHistory(sessionId);

    // Depois carrega o documento (não será sobrescrito pelo useEffect)
    await loadGeneratedDocument(sessionId);

    // O card de visualização aparecerá automaticamente pois generatedDocument será populado
    toast.info(`Carregando documento: ${sessionName}`);
  };

  // Handler para quando usuário seleciona uma versão específica
  const handleSelectVersion = async (version: number) => {
    if (!currentSessionId) {
      toast.error('Nenhuma sessão ativa');
      return;
    }

    try {
      console.log('📜 Carregando versão:', version, 'da sessão:', currentSessionId);

      // IMPORTANTE: Carrega chat PRIMEIRO para evitar race condition com useEffect
      await loadChatHistory(currentSessionId);

      // Depois busca e seta a versão do documento (não será sobrescrito)
      const versionData = await documentService.getDocumentVersion(currentSessionId, version);

      if (versionData && versionData.content) {
        setGeneratedDocument(versionData.content);
        setDocumentFilename(`requisitos_v${version}.md`);
        toast.success(`Versão ${version} carregada com sucesso`);
      } else {
        toast.error('Conteúdo da versão não encontrado');
      }
    } catch (err) {
      console.error('❌ Erro ao carregar versão:', err);
      toast.error('Erro ao carregar versão do documento');
    }
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
              <div className="header-buttons">
                <button className="btn-upload-compact" onClick={() => setIsUploadModalOpen(true)}>
                  + Upload
                </button>
                <button className="btn-history-compact" onClick={() => setIsHistoryModalOpen(true)} title="Histórico de Documentos Gerados">
                  📜 Histórico
                </button>
              </div>
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
                onViewDiff={() => setIsDiffModalOpen(true)}
                onEdit={() => {
                  console.log('📝 Abrindo editor de documento...');
                  setIsEditorOpen(true);
                }}
                onView={() => {
                  console.log('👁️ Abrindo visualizador de documento...');
                  setIsViewerOpen(true);
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

      {/* Editor de Documento Gerado */}
      <MarkdownEditorModal
        isOpen={isEditorOpen}
        content={generatedDocument}
        filename={documentFilename}
        onSave={handleSaveEdit}
        onClose={() => setIsEditorOpen(false)}
      />

      {/* Visualizador de Documento Gerado */}
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

      {/* Modal de Histórico de Versões */}
      <RequirementsHistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        sessionId={currentSessionId}
        onSelectSession={handleSelectHistorySession}
        onSelectVersion={handleSelectVersion}
      />

      {/* Modal de Diff Fullscreen */}
      <DiffViewerModal
        isOpen={isDiffModalOpen}
        oldDocument={oldDocument}
        newDocument={generatedDocument}
        onClose={() => setIsDiffModalOpen(false)}
      />
    </div>
  );
};

export default DocumentsPage;
