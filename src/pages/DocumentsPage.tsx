import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Document, DocumentStatus } from '../types';
import DocumentCard from '../components/documents/DocumentCard';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import DocumentViewModal from '../components/documents/DocumentViewModal';
import './DocumentsPage.css';

const DocumentsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | 'all'>('all');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    // Simular carregamento de documentos
    loadMockDocuments();
  }, [projectId]);

  const loadMockDocuments = () => {
    const mockDocuments: Document[] = [
      {
        id: 'doc_1',
        projectId: projectId || 'default',
        name: 'requirements.pdf',
        originalName: 'Requisitos do Sistema - v2.1.pdf',
        size: 2048576, // 2MB
        type: 'application/pdf',
        uploadedAt: '2025-05-20T10:00:00Z',
        status: DocumentStatus.ANALYZED,
        extractedEntities: [
          {
            name: 'Sistema de Gestão',
            type: 'system',
            description: 'Sistema principal para gerenciamento de recursos',
            confidence: 0.95
          },
          {
            name: 'Usuário Administrador',
            type: 'actor',
            description: 'Responsável pela configuração do sistema',
            confidence: 0.90
          }
        ],
        requirements: [
          {
            id: 'req_1',
            type: 'functional',
            title: 'Autenticação de Usuários',
            description: 'O sistema deve permitir login seguro com validação de credenciais',
            priority: 'high',
            source: 'requirements.pdf'
          },
          {
            id: 'req_2',
            type: 'non_functional',
            title: 'Performance do Sistema',
            description: 'Tempo de resposta deve ser inferior a 2 segundos',
            priority: 'medium',
            source: 'requirements.pdf'
          }
        ],
        analysisIssues: [
          {
            type: 'warning',
            title: 'Requisito Ambíguo',
            description: 'O requisito de segurança precisa ser mais específico',
            documentName: 'requirements.pdf',
            location: 'Seção 3.2'
          }
        ],
        analysisInstructions: 'Focar em requisitos de segurança e performance',
        analysisResults: {
          summary: 'Documento contém especificações técnicas abrangentes com foco em funcionalidades de autenticação e gestão de usuários.',
          keyFindings: [
            'Sistema requer autenticação multi-fator',
            'Necessidade de integração com Active Directory',
            'Requisitos de auditoria bem definidos'
          ],
          recommendedActions: [
            'Detalhar requisitos de segurança',
            'Especificar critérios de performance',
            'Adicionar casos de uso para recovery'
          ]
        }
      },
      {
        id: 'doc_2',
        projectId: projectId || 'default',
        name: 'business_rules.docx',
        originalName: 'Regras de Negócio - Versão Final.docx',
        size: 1536000, // 1.5MB
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        uploadedAt: '2025-05-20T11:30:00Z',
        status: DocumentStatus.ANALYZING,
        analysisProgress: 67,
        extractedEntities: [],
        requirements: [],
        analysisIssues: [],
        analysisInstructions: 'Identificar regras de negócio e processos críticos'
      },
      {
        id: 'doc_3',
        projectId: projectId || 'default',
        name: 'user_stories.md',
        originalName: 'User Stories - Sprint Planning.md',
        size: 512000, // 500KB
        type: 'text/markdown',
        uploadedAt: '2025-05-20T14:15:00Z',
        status: DocumentStatus.ANALYZED,
        extractedEntities: [
          {
            name: 'Cliente',
            type: 'actor',
            description: 'Usuário final do sistema',
            confidence: 0.88
          },
          {
            name: 'Processo de Compra',
            type: 'process',
            description: 'Fluxo de aquisição de produtos',
            confidence: 0.92
          }
        ],
        requirements: [
          {
            id: 'req_3',
            type: 'functional',
            title: 'Carrinho de Compras',
            description: 'Usuário deve poder adicionar produtos ao carrinho',
            priority: 'high',
            source: 'user_stories.md'
          }
        ],
        analysisIssues: [],
        analysisResults: {
          summary: 'Documentação de user stories bem estruturada com cenários de uso detalhados.',
          keyFindings: [
            'Cobertura completa do fluxo de e-commerce',
            'Definição clara de personas',
            'Critérios de aceitação bem definidos'
          ],
          recommendedActions: [
            'Considerar casos de erro',
            'Adicionar cenários de edge cases'
          ]
        }
      }
    ];
    setDocuments(mockDocuments);
  };

  const handleUpload = async (files: FileList, instructions?: string) => {
    setIsUploading(true);
    
    // Simular upload e análise
    const newDocuments: Document[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const newDoc: Document = {
        id: `doc_${Date.now()}_${i}`,
        projectId: projectId || 'default',
        name: file.name.toLowerCase().replace(/\s+/g, '_'),
        originalName: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
        status: DocumentStatus.UPLOADED,
        extractedEntities: [],
        requirements: [],
        analysisIssues: [],
        analysisInstructions: instructions
      };
      
      newDocuments.push(newDoc);
    }

    // Adicionar documentos à lista
    setDocuments(prev => [...prev, ...newDocuments]);
    setIsUploading(false);
    setIsUploadModalOpen(false);

    // Simular início da análise após um delay
    setTimeout(() => {
      startAnalysis(newDocuments.map(doc => doc.id));
    }, 1000);
  };

  const startAnalysis = (documentIds: string[]) => {
    setIsAnalyzing(true);

    documentIds.forEach((docId, index) => {
      // Atualizar status para "analisando"
      setTimeout(() => {
        setDocuments(prev => prev.map(doc => 
          doc.id === docId 
            ? { ...doc, status: DocumentStatus.ANALYZING, analysisProgress: 0 }
            : doc
        ));

        // Simular progresso da análise
        let progress = 0;
        const progressInterval = setInterval(() => {
          progress += Math.random() * 20;
          if (progress >= 100) {
            clearInterval(progressInterval);
            // Finalizar análise
            completeAnalysis(docId);
          } else {
            setDocuments(prev => prev.map(doc => 
              doc.id === docId 
                ? { ...doc, analysisProgress: Math.round(progress) }
                : doc
            ));
          }
        }, 500);
      }, index * 2000);
    });
  };

  const completeAnalysis = (documentId: string) => {
    // Simular resultado da análise
    const mockAnalysisResult = {
      extractedEntities: [
        {
          name: 'Sistema Novo',
          type: 'system' as const,
          description: 'Sistema identificado na análise',
          confidence: 0.85
        }
      ],
      requirements: [
        {
          id: `req_${Date.now()}`,
          type: 'functional' as const,
          title: 'Nova Funcionalidade',
          description: 'Funcionalidade identificada na análise',
          priority: 'medium' as const,
          source: 'documento_analisado'
        }
      ],
      analysisIssues: [],
      analysisResults: {
        summary: 'Análise concluída com sucesso. Documento processado e informações extraídas.',
        keyFindings: ['Requisitos bem definidos', 'Estrutura clara'],
        recommendedActions: ['Validar com stakeholders']
      }
    };

    setDocuments(prev => prev.map(doc => 
      doc.id === documentId 
        ? { 
            ...doc, 
            status: DocumentStatus.ANALYZED,
            analysisProgress: 100,
            ...mockAnalysisResult
          }
        : doc
    ));

    setIsAnalyzing(false);
  };

  const handleView = (document: Document) => {
    setSelectedDocument(document);
    setIsViewModalOpen(true);
  };

  const handleDelete = (documentId: string) => {
    if (window.confirm('Tem certeza que deseja excluir este documento?')) {
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    }
  };

  const handleReanalyze = (documentId: string) => {
    if (window.confirm('Deseja reanalisar este documento?')) {
      startAnalysis([documentId]);
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
    <div className="documents-page">
      <div className="page-header">
        <div className="header-content">
          <h1>📄 Documentação</h1>
          <p>Gerencie e analise documentos do projeto</p>
        </div>
        <button 
          className="btn-upload-primary"
          onClick={() => setIsUploadModalOpen(true)}
        >
          📤 Upload de Documentos
        </button>
      </div>

      <div className="page-content">
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
