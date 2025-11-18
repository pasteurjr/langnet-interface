import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Document, DocumentStatus } from '../types';
import DocumentCard from '../components/documents/DocumentCard';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import DocumentViewModal from '../components/documents/DocumentViewModal';
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
      toast.success(`${transformedDocs.length} arquivo(s) carregado(s) com sucesso`);

      console.log('🔍 Starting analysis...');
      // Automatically start analysis
      const documentIds = transformedDocs.map(doc => doc.id);
      startAnalysis(documentIds);
    } catch (err) {
      console.error('❌ Failed to upload documents:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload documents';
      setError(errorMessage);
      toast.error(`Erro no upload: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  const startAnalysis = async (documentIds: string[]) => {
    setIsAnalyzing(true);

    for (const docId of documentIds) {
      try {
        // Update status to analyzing
        setDocuments(prev => prev.map(doc =>
          doc.id === docId
            ? { ...doc, status: DocumentStatus.ANALYZING, analysisProgress: 0 }
            : doc
        ));

        // Get document to extract instructions and web research setting
        const doc = documents.find(d => d.id === docId);
        const instructions = doc?.analysisInstructions || "";
        const enableWebResearch = doc?.enableWebResearch ?? true;

        // Call LangNet analysis API (full pipeline with optional web research)
        if (!projectId) return;

        const executionId = await langnetService.analyzeDocumentWithLangNet(
          parseInt(projectId),
          parseInt(docId),
          instructions,
          enableWebResearch
        );

        // Poll execution status
        const result = await langnetService.pollExecutionStatus(executionId);

        // Fetch updated requirements
        const requirements = await documentService.getDocumentRequirements(parseInt(docId));

        // Update document with analysis results and execution_id
        setDocuments(prev => prev.map(doc =>
          doc.id === docId
            ? {
                ...doc,
                status: DocumentStatus.ANALYZED,
                analysisProgress: 100,
                executionId: executionId, // Store execution ID for viewing requirements document
                analysisResults: {
                  summary: `Análise LangNet concluída com ${result.tasks_completed || 0} tarefas executadas`,
                  keyFindings: ['Documento de requisitos gerado', 'Pesquisa web realizada', 'Requisitos validados'],
                  recommendedActions: ['Ver Documento de Requisitos', 'Refinar com agente', 'Prosseguir para especificação']
                },
                requirements: requirements.map((req: any) => ({
                  id: req.id.toString(),
                  type: req.type,
                  title: req.requirement_id,
                  description: req.description,
                  priority: req.priority,
                  source: doc.name
                }))
              }
            : doc
        ));
      } catch (err) {
        console.error(`Failed to analyze document ${docId}:`, err);
        setDocuments(prev => prev.map(doc =>
          doc.id === docId
            ? { ...doc, status: DocumentStatus.ERROR }
            : doc
        ));
      }
    }

    setIsAnalyzing(false);
  };

  const handleView = (document: Document) => {
    setSelectedDocument(document);
    setIsViewModalOpen(true);
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Tem certeza que deseja excluir este documento?')) {
      return;
    }

    try {
      await documentService.deleteDocument(parseInt(documentId));
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (err) {
      console.error('Failed to delete document:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const handleReanalyze = async (documentId: string) => {
    if (!window.confirm('Deseja reanalisar este documento?')) {
      return;
    }

    await startAnalysis([documentId]);
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
    <div className="documents-page">
      <div className="page-header">
        <div className="header-content">
          <h1>📄 Documentação {projectContext.isInProject && `- ${projectContext.projectName}`}</h1>
          <p>Gerencie e analise documentos do projeto</p>
        </div>
        <button
          className="btn-upload-primary"
          onClick={() => setIsUploadModalOpen(true)}
        >
          📤 Upload de Documentos
        </button>
      </div>

      {/* Analysis Configuration Section */}
      <div className="analysis-config-section" style={{
        background: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '24px',
        border: '1px solid #dee2e6'
      }}>
        <h3 style={{ marginTop: 0, marginBottom: '16px', fontSize: '16px', fontWeight: '600' }}>
          ⚙️ Configuração da Análise
        </h3>

        <div className="instructions-section" style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
            Instruções Adicionais para Análise
          </label>
          <textarea
            className="instructions-textarea"
            placeholder="Adicione instruções específicas para orientar a análise dos documentos. Por exemplo: 'Focar em requisitos de segurança', 'Identificar integrações com sistemas externos', etc."
            value={analysisInstructions}
            onChange={(e) => setAnalysisInstructions(e.target.value)}
            rows={3}
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '14px',
              border: '1px solid #ced4da',
              borderRadius: '4px',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
        </div>

        <div className="web-research-option" style={{
          padding: '14px',
          background: enableWebResearch ? '#e8f5e9' : '#fff',
          border: `2px solid ${enableWebResearch ? '#4caf50' : '#ddd'}`,
          borderRadius: '6px',
          transition: 'all 0.3s'
        }}>
          <label style={{
            display: 'flex',
            alignItems: 'flex-start',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            <input
              type="checkbox"
              checked={enableWebResearch}
              onChange={(e) => setEnableWebResearch(e.target.checked)}
              style={{
                marginRight: '12px',
                marginTop: '2px',
                width: '18px',
                height: '18px',
                cursor: 'pointer',
                flexShrink: 0
              }}
            />
            <div>
              <span style={{ fontWeight: '600', fontSize: '14px' }}>
                🌐 Habilitar Pesquisa Web (Web Research)
              </span>
              <p style={{
                marginTop: '6px',
                marginBottom: 0,
                fontSize: '13px',
                color: '#666',
                lineHeight: '1.5'
              }}>
                {enableWebResearch ? (
                  <>
                    ✅ <strong>Análise Completa:</strong> Busca best practices, padrões da indústria (OWASP, LGPD),
                    tecnologias recomendadas e compliance. <em>Tempo estimado: 6-10 min</em>
                  </>
                ) : (
                  <>
                    ⚡ <strong>Análise Rápida:</strong> Apenas extração de requisitos dos documentos enviados.
                    <em>Tempo estimado: 3-4 min</em>
                  </>
                )}
              </p>
            </div>
          </label>
        </div>

        <div className="instructions-help" style={{
          marginTop: '12px',
          padding: '12px',
          background: '#fff',
          borderRadius: '4px',
          fontSize: '13px',
          color: '#666'
        }}>
          <p style={{ margin: '0 0 8px 0', fontWeight: '500', color: '#333' }}>💡 Dicas para melhores resultados:</p>
          <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.6' }}>
            <li>Mencione o domínio da aplicação (ex: e-commerce, saúde, financeiro)</li>
            <li>Especifique aspectos importantes (performance, segurança, usabilidade)</li>
            <li>Indique se há padrões ou frameworks específicos a seguir</li>
            <li>Destaque integrações ou sistemas legados existentes</li>
          </ul>
        </div>
      </div>

      <div className="page-content">
        {error && (
          <div className="error-message" style={{
            padding: '12px',
            marginBottom: '16px',
            background: '#fee',
            border: '1px solid #fcc',
            borderRadius: '4px',
            color: '#c33'
          }}>
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="loading-state" style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px',
            fontSize: '18px',
            color: '#666'
          }}>
            <span className="spinner"></span> Carregando documentos...
          </div>
        ) : (
          <>
        <div className="filters-section">
          <div className="search-container">
            <input
              type="text"
              placeholder="Buscar documentos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="status-filters">
            <button
              className={`status-filter ${statusFilter === 'all' ? 'active' : ''}`}
              onClick={() => setStatusFilter('all')}
            >
              Todos ({documents.length})
            </button>
            <button
              className={`status-filter ${statusFilter === DocumentStatus.UPLOADED ? 'active' : ''}`}
              onClick={() => setStatusFilter(DocumentStatus.UPLOADED)}
            >
              Carregados ({getStatusCount(DocumentStatus.UPLOADED)})
            </button>
            <button
              className={`status-filter ${statusFilter === DocumentStatus.ANALYZING ? 'active' : ''}`}
              onClick={() => setStatusFilter(DocumentStatus.ANALYZING)}
            >
              Analisando ({getStatusCount(DocumentStatus.ANALYZING)})
            </button>
            <button
              className={`status-filter ${statusFilter === DocumentStatus.ANALYZED ? 'active' : ''}`}
              onClick={() => setStatusFilter(DocumentStatus.ANALYZED)}
            >
              Analisados ({getStatusCount(DocumentStatus.ANALYZED)})
            </button>
            <button
              className={`status-filter ${statusFilter === DocumentStatus.ERROR ? 'active' : ''}`}
              onClick={() => setStatusFilter(DocumentStatus.ERROR)}
            >
              Erros ({getStatusCount(DocumentStatus.ERROR)})
            </button>
          </div>
        </div>

        <div className="documents-list">
          {filteredDocuments.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h3>Nenhum documento encontrado</h3>
              <p>
                {documents.length === 0 
                  ? 'Faça upload de documentos para começar a análise'
                  : 'Tente ajustar os filtros de busca'
                }
              </p>
              {documents.length === 0 && (
                <button 
                  className="btn-upload-empty"
                  onClick={() => setIsUploadModalOpen(true)}
                >
                  📤 Fazer Upload
                </button>
              )}
            </div>
          ) : (
            filteredDocuments.map((document) => (
              <DocumentCard
                key={document.id}
                document={document}
                onView={handleView}
                onDelete={handleDelete}
                onReanalyze={handleReanalyze}
              />
            ))
          )}
        </div>

        {isAnalyzing && (
          <div className="analysis-status">
            <div className="analysis-notification">
              <span className="spinner"></span>
              Análise em andamento...
            </div>
          </div>
        )}
          </>
        )}
      </div>

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
