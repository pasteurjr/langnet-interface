import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Document, DocumentStatus } from '../types';
import DocumentCard from '../components/documents/DocumentCard';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import DocumentViewModal from '../components/documents/DocumentViewModal';
import ChatInterface, { ChatMessage } from '../components/documents/ChatInterface';
import * as documentService from '../services/documentService';
import langnetService from '../services/langnetService';
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
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);

  // TESTE: Adicionar mensagens de exemplo ao carregar (remover depois)
  useEffect(() => {
    if (chatMessages.length === 0) {
      const demoMessages: ChatMessage[] = [
        {
          id: '1',
          sender: 'system',
          text: '🎉 Bem-vindo à nova interface de chat para análise de requisitos!',
          timestamp: new Date(Date.now() - 60000),
          type: 'status'
        },
        {
          id: '2',
          sender: 'agent',
          text: '👋 Olá! Faça upload de documentos na sidebar e clique em "Iniciar Análise" para começar.',
          timestamp: new Date(Date.now() - 50000),
        }
      ];
      // Descomentar a linha abaixo para ver mensagens de demo:
      // setChatMessages(demoMessages);
    }
  }, [chatMessages.length]);

  useEffect(() => {
    loadDocuments();
  }, [projectId]);

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

    // Add user message with instructions
    addChatMessage(
      'user',
      analysisInstructions || 'Analisar documentos e extrair requisitos',
      'status'
    );

    addChatMessage(
      'system',
      `🚀 Iniciando análise de ${documents.length} documento(s)...${enableWebResearch ? ' (com pesquisa web)' : ''}`
    );

    try {
      if (!projectId) return;

      // Get all uploaded document IDs
      const documentIds = documents
        .filter(doc => doc.status === DocumentStatus.UPLOADED)
        .map(doc => parseInt(doc.id));

      if (documentIds.length === 0) {
        addChatMessage('system', '⚠️ Nenhum documento pendente de análise');
        setIsAnalyzing(false);
        setIsChatProcessing(false);
        return;
      }

      // Start analysis
      addChatMessage('agent', '🔍 Processando documentos e extraindo conteúdo...', 'progress');

      const executionId = await langnetService.analyzeDocumentsWithLangNet(
        parseInt(projectId),
        documentIds,
        analysisInstructions,
        enableWebResearch
      );

      setCurrentExecutionId(executionId);

      // Connect WebSocket for real-time updates
      connectWebSocket(executionId);

      addChatMessage('agent', `📊 Análise iniciada. ID de execução: ${executionId}`, 'status');

      // Poll execution status
      const result = await langnetService.pollExecutionStatus(executionId);

      // Fetch updated documents and requirements
      await loadDocuments();

      addChatMessage(
        'agent',
        `✅ Análise concluída! ${result.tasks_completed || 0} tarefas executadas com sucesso.`,
        'result'
      );

      // Show generated requirements document
      addChatMessage(
        'agent',
        `# Documento de Requisitos Gerado\n\n## Resumo da Análise\n\nA análise foi concluída com sucesso para ${documents.length} documento(s).\n\n### Requisitos Extraídos\n- Requisitos Funcionais: Identificados\n- Requisitos Não Funcionais: Identificados\n- Regras de Negócio: Documentadas\n\n### Próximos Passos\n1. Revisar os requisitos extraídos\n2. Refinar através desta interface de chat\n3. Exportar para especificação formal`,
        'document',
        { projectId, executionId }
      );

      toast.success('Análise concluída com sucesso!');
    } catch (err) {
      console.error('Failed to analyze documents:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze documents';
      addChatMessage('system', `❌ Erro na análise: ${errorMessage}`, 'status');
      toast.error(`Erro na análise: ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
      setIsChatProcessing(false);
    }
  };

  // TESTE: Simular análise completa com mensagens fake
  const testSimulateAnalysis = () => {
    setChatMessages([]);
    setIsChatProcessing(true);

    // Mensagem do usuário
    addChatMessage('user', analysisInstructions || 'Analisar documentos e extrair requisitos');

    // Mensagens de progresso simuladas
    setTimeout(() => {
      addChatMessage('system', '🚀 Iniciando análise de 3 documento(s)... (com pesquisa web)');
    }, 500);

    setTimeout(() => {
      addChatMessage('system', '🔌 Conectado ao sistema de análise em tempo real');
    }, 1000);

    setTimeout(() => {
      addChatMessage('agent', '🔍 Processando documentos e extraindo conteúdo...', 'progress');
    }, 1500);

    setTimeout(() => {
      addChatMessage('agent', '📊 Análise iniciada. ID de execução: exec-test-12345', 'status');
    }, 2000);

    setTimeout(() => {
      addChatMessage('system', '📄 Documento 1/3: Extraindo texto do PDF... (1.2 MB)', 'progress');
    }, 3000);

    setTimeout(() => {
      addChatMessage('system', '📄 Documento 2/3: Processando chunks... (47 chunks)', 'progress');
    }, 4500);

    setTimeout(() => {
      addChatMessage('agent', '🌐 Iniciando pesquisa web por best practices...', 'progress');
    }, 6000);

    setTimeout(() => {
      addChatMessage('agent', '✅ Tarefa completada: Web Research finalizada', 'status');
    }, 8000);

    setTimeout(() => {
      addChatMessage('agent', '✅ Análise concluída! 12 tarefas executadas com sucesso.', 'result');
    }, 9000);

    setTimeout(() => {
      const requirementsDoc = `# Documento de Requisitos - Sistema de E-commerce

## 📋 Resumo Executivo

Análise concluída com sucesso para 3 documento(s). Sistema identificado como plataforma de e-commerce com requisitos de alta disponibilidade e conformidade com LGPD.

## ✅ Requisitos Funcionais

### RF001 - Autenticação de Usuários
**Prioridade**: Alta
- Login via email/senha
- OAuth2 com Google e Facebook
- Autenticação de dois fatores (2FA)
- Recuperação de senha via email

### RF002 - Catálogo de Produtos
**Prioridade**: Alta
- Listagem com filtros e ordenação
- Busca textual com autocomplete
- Visualização detalhada com zoom de imagens
- Variações de produto (cor, tamanho)

### RF003 - Carrinho de Compras
**Prioridade**: Alta
- Adicionar/remover produtos
- Atualizar quantidades
- Persistência entre sessões
- Cálculo de frete em tempo real

## 🔒 Requisitos Não Funcionais

### RNF001 - Performance
- Tempo de resposta < 2s para 95% das requisições
- Suporte a 10.000 usuários simultâneos
- Cache de produtos com Redis

### RNF002 - Segurança
- Conformidade com OWASP Top 10
- Criptografia TLS 1.3
- Proteção contra SQL Injection e XSS
- Tokenização de dados de pagamento (PCI-DSS)

### RNF003 - Disponibilidade
- SLA de 99.9% uptime
- Backup diário automatizado
- Disaster recovery < 4 horas

## 🌐 Integrações Identificadas

1. **Gateway de Pagamento**: Stripe, PayPal
2. **Serviço de Frete**: Correios API, Melhor Envio
3. **Email Marketing**: SendGrid
4. **Analytics**: Google Analytics 4

## 📊 Regras de Negócio

- **BR001**: Desconto máximo de 70% por produto
- **BR002**: Frete grátis acima de R$ 150
- **BR003**: Cancelamento permitido até 24h após compra
- **BR004**: Estoque mínimo de 5 unidades para disponibilizar produto

## 🎯 Próximos Passos

1. ✅ Revisar requisitos extraídos
2. 🔄 Refinar através da interface de chat
3. 📝 Exportar para especificação formal
4. 🏗️ Iniciar design de arquitetura`;

      addChatMessage('agent', requirementsDoc, 'document', {
        projectId,
        executionId: 'exec-test-12345'
      });
      setIsChatProcessing(false);
    }, 10000);
  };

  // Handle chat messages for conversational refinement
  const handleSendChatMessage = async (message: string) => {
    if (!currentExecutionId || !projectId) {
      toast.error('Inicie uma análise primeiro');
      return;
    }

    // Add user message
    addChatMessage('user', message);
    setIsChatProcessing(true);

    try {
      // Send refinement request to backend
      addChatMessage('agent', '🤔 Processando seu pedido de refinamento...', 'progress');

      // Here you would call a backend endpoint to refine the requirements
      // For now, simulating a response
      setTimeout(() => {
        addChatMessage(
          'agent',
          `Entendi seu pedido: "${message}"\n\nVou ajustar os requisitos de acordo. Por favor, aguarde...`,
          'status'
        );
        setIsChatProcessing(false);
      }, 1500);
    } catch (err) {
      console.error('Failed to process chat message:', err);
      addChatMessage('system', '❌ Erro ao processar mensagem');
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

              {/* BOTÃO DE TESTE - REMOVER EM PRODUÇÃO */}
              <button
                className="btn-test-simulation"
                onClick={testSimulateAnalysis}
                disabled={isChatProcessing}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginTop: '8px',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  color: 'white',
                  border: '2px dashed rgba(255,255,255,0.5)',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  opacity: isChatProcessing ? 0.5 : 1
                }}
              >
                🧪 TESTE: Simular Análise Completa (10s)
              </button>
            </div>
          </div>

          {/* RIGHT AREA: Chat Interface */}
          <div className="chat-area">
            <ChatInterface
              messages={chatMessages}
              onSendMessage={handleSendChatMessage}
              isProcessing={isChatProcessing}
              executionId={currentExecutionId}
            />
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
