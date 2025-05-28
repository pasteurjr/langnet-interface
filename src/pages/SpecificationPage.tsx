/* src/pages/SpecificationPage.tsx */
import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  Share2, 
  Eye, 
  Edit, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw,
  MessageSquare,
  History,
  Settings
} from 'lucide-react';
import {
  SpecificationDocument,
  SpecificationStatus,
  SpecificationSection,
  SpecificationSectionType,
  SpecificationIssue,
  FunctionalRequirement,
  NonFunctionalRequirement
} from '../types/';
import SpecificationGenerationModal from '../components/specification/SpecificationGenerationModal';
import {SpecificationEditorModal} from '../components/specification/SpecificationEditorModal';
import RequirementsTable from '../components/specification/RequirementsTable';
import {DataModelViewer} from '../components/specification/DataModelViewer';
import './SpecificationPage.css';

// Mock data for demonstration
const mockSpecification: SpecificationDocument = {
  id: '1',
  projectId: 'project1',
  title: 'Sistema de Atendimento ao Cliente - Especificação Funcional',
  version: '2.1',
  status: SpecificationStatus.APPROVED,
  createdAt: '2024-03-01T09:00:00',
  updatedAt: '2024-03-15T14:30:00',
  lastGeneratedAt: '2024-03-15T10:00:00',
  sections: [
    {
      id: 'intro',
      type: SpecificationSectionType.INTRODUCTION,
      title: '1. Introdução',
      content: `## 1.1 Propósito

Este documento especifica os requisitos funcionais e não-funcionais para o Sistema de Atendimento ao Cliente, projetado para automatizar e otimizar o processo de suporte ao cliente através de agentes inteligentes.

## 1.2 Escopo

O sistema abrangerá:
- Classificação automática de consultas
- Roteamento inteligente para agentes especializados
- Geração de respostas automatizadas
- Análise de sentimento em tempo real
- Escalação de casos complexos
- Monitoramento de performance e qualidade`,
      order: 1,
      isRequired: true,
      isGenerated: true,
      lastModified: '2024-03-15T10:00:00',
      wordCount: 89,
      completeness: 95,
      issues: []
    },
    {
      id: 'overview',
      type: SpecificationSectionType.OVERVIEW,
      title: '2. Visão Geral do Sistema',
      content: `## 2.1 Contexto do Negócio

O sistema será implementado para atender a crescente demanda de suporte ao cliente, oferecendo respostas rápidas e precisas através de tecnologia de inteligência artificial.

## 2.2 Objetivos do Sistema

- Reduzir tempo médio de resposta de 24h para 5 minutos
- Aumentar satisfação do cliente para >95%
- Automatizar 80% das consultas rotineiras
- Melhorar rastreabilidade e análise de problemas

## 2.3 Arquitetura Conceitual

O sistema utilizará uma arquitetura baseada em agentes inteligentes, onde cada agente possui especialização específica:
- Agente de Atendimento Geral
- Agente de Suporte Técnico
- Agente de Análise de Sentimento
- Agente de Escalação`,
      order: 2,
      isRequired: true,
      isGenerated: true,
      lastModified: '2024-03-15T10:00:00',
      wordCount: 124,
      completeness: 90,
      issues: [
        {
          id: 'issue1',
          type: 'clarity',
          severity: 'medium',
          title: 'Métricas específicas necessárias',
          description: 'Detalhar como será medida a satisfação do cliente',
          sectionId: 'overview',
          suggestions: ['Incluir metodologia de pesquisa NPS', 'Definir intervalos de medição'],
          isResolved: false
        }
      ]
    }
  ],
  functionalRequirements: [
    {
      id: 'fr001',
      code: 'FR001',
      title: 'Processamento de Consultas',
      description: 'O sistema deve ser capaz de receber e processar consultas de clientes em texto natural',
      priority: 'must_have',
      complexity: 'high',
      source: 'requirements.pdf',
      dependencies: [],
      acceptanceCriteria: [
        'Processar consultas em português',
        'Responder em menos de 5 segundos',
        'Identificar intenção com 95% de precisão'
      ],
      category: 'Processamento',
      status: 'approved' as any
    },
    {
      id: 'fr002',
      code: 'FR002',
      title: 'Análise de Sentimento',
      description: 'O sistema deve analisar o sentimento das mensagens do cliente (positivo, neutro, negativo)',
      priority: 'should_have',
      complexity: 'medium',
      source: 'business_rules.docx',
      dependencies: ['fr001'],
      acceptanceCriteria: [
        'Classificar sentimento com 90% de precisão',
        'Detectar urgência em mensagens negativas',
        'Priorizar atendimento baseado no sentimento'
      ],
      category: 'Análise',
      status: 'approved' as any
    }
  ],
  nonFunctionalRequirements: [
    {
      id: 'nfr001',
      code: 'NFR001',
      title: 'Tempo de Resposta',
      description: 'O sistema deve responder a consultas em menos de 5 segundos',
      category: 'performance',
      metric: 'Tempo médio de resposta',
      targetValue: '< 5 segundos',
      priority: 'must_have',
      testMethod: 'Testes de carga com 1000 consultas simultâneas',
      status: 'approved' as any
    },
    {
      id: 'nfr002',
      code: 'NFR002',
      title: 'Disponibilidade do Sistema',
      description: 'O sistema deve estar disponível 99.9% do tempo',
      category: 'reliability',
      metric: 'Uptime percentual',
      targetValue: '99.9%',
      priority: 'must_have',
      testMethod: 'Monitoramento contínuo por 30 dias',
      status: 'approved' as any
    },
    {
      id: 'nfr003',
      code: 'NFR003',
      title: 'Segurança de Dados',
      description: 'Todos os dados do cliente devem ser criptografados em trânsito e em repouso',
      category: 'security',
      metric: 'Nível de criptografia',
      targetValue: 'AES-256',
      priority: 'must_have',
      testMethod: 'Auditoria de segurança e testes de penetração',
      status: 'approved' as any
    }
  ],
  dataEntities: [
    {
      id: 'customer',
      name: 'Customer',
      description: 'Entidade que representa um cliente do sistema',
      attributes: [
        {
          id: 'customer_id',
          name: 'customer_id',
          type: 'UUID',
          isRequired: true,
          isPrimaryKey: true,
          isForeignKey: false,
          description: 'Identificador único do cliente',
          constraints: ['NOT NULL', 'UNIQUE']
        },
        {
          id: 'name',
          name: 'name',
          type: 'VARCHAR(255)',
          isRequired: true,
          isPrimaryKey: false,
          isForeignKey: false,
          description: 'Nome completo do cliente',
          constraints: ['NOT NULL']
        },
        {
          id: 'email',
          name: 'email',
          type: 'VARCHAR(255)',
          isRequired: true,
          isPrimaryKey: false,
          isForeignKey: false,
          description: 'Email do cliente',
          constraints: ['NOT NULL', 'UNIQUE', 'EMAIL_FORMAT']
        }
      ],
      relationships: [
        {
          id: 'customer_tickets',
          sourceEntityId: 'customer',
          targetEntityId: 'ticket',
          type: 'one_to_many',
          description: 'Um cliente pode ter múltiplos tickets',
          isRequired: false
        }
      ],
      businessRules: [
        'Email deve ser único no sistema',
        'Nome não pode estar vazio',
        'Cliente deve ser maior de idade'
      ]
    }
  ],
  userStories: [
    {
      id: 'us001',
      title: 'Enviar consulta como cliente',
      description: 'Como cliente, eu quero enviar uma consulta para receber suporte',
      asA: 'cliente',
      iWant: 'enviar uma consulta ao sistema',
      soThat: 'possa receber suporte rápido e eficiente',
      acceptanceCriteria: [
        'Posso digitar minha consulta em texto livre',
        'Recebo confirmação de que a consulta foi recebida',
        'Sou notificado quando há uma resposta'
      ],
      priority: 1,
      storyPoints: 5,
      epic: 'Atendimento Básico',
      theme: 'Experiência do Cliente',
      relatedRequirements: ['fr001']
    }
  ],
  businessRules: [
    {
      id: 'br001',
      code: 'BR001',
      name: 'Priorização por Sentimento',
      description: 'Consultas com sentimento negativo devem ter prioridade alta',
      type: 'action_enabler',
      condition: 'sentiment_score < -0.5',
      action: 'set_priority = HIGH',
      priority: 'high',
      source: 'business_rules.docx',
      relatedRequirements: ['fr002'],
      examples: [
        'Cliente reclamando de produto = prioridade alta',
        'Cliente elogiando = prioridade normal'
      ]
    }
  ],
  metadata: {
    totalWordCount: 2847,
    totalPages: 12,
    completeness: 85,
    qualityScore: 92,
    lastReviewDate: '2024-03-14T16:00:00',
    reviewers: ['João Silva', 'Maria Santos'],
    approvers: ['Carlos Oliveira']
  },
  generationConfig: {
    includeDataModel: true,
    includeUserStories: true,
    includeBusinessRules: true,
    includeGlossary: true,
    detailLevel: 'detailed',
    targetAudience: 'mixed',
    templateStyle: 'agile'
  }
};

const SpecificationPage: React.FC = () => {
  const [specification, setSpecification] = useState<SpecificationDocument>(mockSpecification);
  const [selectedSection, setSelectedSection] = useState<string>('intro');
  const [sidebarTab, setSidebarTab] = useState<'outline' | 'issues' | 'comments'>('outline');
  const [showGenerationModal, setShowGenerationModal] = useState(false);
  const [showEditorModal, setShowEditorModal] = useState(false);
  const [selectedSectionForEdit, setSelectedSectionForEdit] = useState<SpecificationSection | null>(null);

  const currentProjectId = 'project1'; // This should come from context/props

  const getStatusIcon = (status: SpecificationStatus) => {
    switch (status) {
      case SpecificationStatus.DRAFT:
        return '📝';
      case SpecificationStatus.GENERATED:
        return '✨';
      case SpecificationStatus.REVIEWING:
        return '👁️';
      case SpecificationStatus.APPROVED:
        return '✅';
      case SpecificationStatus.NEEDS_REVISION:
        return '⚠️';
      default:
        return '📄';
    }
  };

  const getStatusText = (status: SpecificationStatus) => {
    switch (status) {
      case SpecificationStatus.DRAFT:
        return 'Rascunho';
      case SpecificationStatus.GENERATED:
        return 'Gerado';
      case SpecificationStatus.REVIEWING:
        return 'Em Revisão';
      case SpecificationStatus.APPROVED:
        return 'Aprovado';
      case SpecificationStatus.NEEDS_REVISION:
        return 'Precisa Revisão';
      default:
        return 'Desconhecido';
    }
  };

  const getSectionIcon = (type: SpecificationSectionType) => {
    switch (type) {
      case SpecificationSectionType.INTRODUCTION:
        return '📖';
      case SpecificationSectionType.OVERVIEW:
        return '🔍';
      case SpecificationSectionType.FUNCTIONAL_REQUIREMENTS:
        return '⚙️';
      case SpecificationSectionType.NON_FUNCTIONAL_REQUIREMENTS:
        return '📊';
      case SpecificationSectionType.DATA_MODEL:
        return '🗃️';
      case SpecificationSectionType.USER_INTERFACE:
        return '🖥️';
      case SpecificationSectionType.INTEGRATION:
        return '🔗';
      case SpecificationSectionType.BUSINESS_RULES:
        return '📋';
      case SpecificationSectionType.GLOSSARY:
        return '📚';
      default:
        return '📄';
    }
  };

  const getSectionStatusIcon = (section: SpecificationSection) => {
    if (section.issues.filter(i => i.severity === 'critical' || i.severity === 'high').length > 0) {
      return '🔴';
    }
    if (section.issues.filter(i => i.severity === 'medium').length > 0) {
      return '🟡';
    }
    if (section.completeness < 80) {
      return '🟠';
    }
    return '🟢';
  };

  const handleGenerateSpecification = () => {
    setShowGenerationModal(true);
  };

  const handleEditSection = (section: SpecificationSection) => {
    setSelectedSectionForEdit(section);
    setShowEditorModal(true);
  };

  const handleSaveSection = (sectionId: string, content: string) => {
    setSpecification(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === sectionId
          ? {
              ...section,
              content,
              lastModified: new Date().toISOString(),
              wordCount: content.split(' ').length
            }
          : section
      ),
      updatedAt: new Date().toISOString()
    }));
    setShowEditorModal(false);
  };

  const handleDownloadSpecification = () => {
    // Simulate download
    console.log('Downloading specification...');
  };

  const handleShareSpecification = () => {
    // Simulate sharing
    console.log('Sharing specification...');
  };

  const handleApproveSpecification = () => {
    setSpecification(prev => ({
      ...prev,
      status: SpecificationStatus.APPROVED,
      updatedAt: new Date().toISOString(),
      metadata: {
        ...prev.metadata,
        approvers: [...prev.metadata.approvers, 'Current User']
      }
    }));
  };

  const getCurrentSection = () => {
    return specification.sections.find(s => s.id === selectedSection);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const allIssues = specification.sections.flatMap(s => s.issues);
  const criticalIssues = allIssues.filter(i => i.severity === 'critical').length;
  const highIssues = allIssues.filter(i => i.severity === 'high').length;
  const totalIssues = allIssues.length;

  return (
    <div className="specification-page">
      <div className="specification-header">
        <div className="specification-header-left">
          <h1>
            {getStatusIcon(specification.status)} Especificação Funcional
            <span className={`spec-status-badge status-${specification.status}`}>
              {getStatusText(specification.status)}
            </span>
          </h1>
          <p>Documente e valide os requisitos funcionais do seu projeto</p>
        </div>
        <div className="specification-header-actions">
          <button className="spec-action-button secondary" onClick={handleDownloadSpecification}>
            <Download size={18} />
            Exportar PDF
          </button>
          <button className="spec-action-button secondary" onClick={handleShareSpecification}>
            <Share2 size={18} />
            Compartilhar
          </button>
          {specification.status !== SpecificationStatus.APPROVED && (
            <button className="spec-action-button success" onClick={handleApproveSpecification}>
              <CheckCircle size={18} />
              Aprovar
            </button>
          )}
          <button className="spec-action-button primary" onClick={handleGenerateSpecification}>
            <RefreshCw size={18} />
            Gerar/Atualizar
          </button>
        </div>
      </div>

      <div className="specification-content">
        <div className="specification-sidebar">
          <div className="spec-sidebar-header">
            <h3>Progresso da Especificação</h3>
            <div className="spec-progress-bar">
              <div 
                className="spec-progress-fill" 
                style={{ width: `${specification.metadata.completeness}%` }}
              />
            </div>
            <div className="spec-stats">
              <div className="spec-stat">
                <span className="spec-stat-number">{specification.metadata.completeness}%</span>
                <span className="spec-stat-label">Completo</span>
              </div>
              <div className="spec-stat">
                <span className="spec-stat-number">{specification.metadata.qualityScore}</span>
                <span className="spec-stat-label">Qualidade</span>
              </div>
              <div className="spec-stat">
                <span className="spec-stat-number">{specification.metadata.totalWordCount}</span>
                <span className="spec-stat-label">Palavras</span>
              </div>
              <div className="spec-stat">
                <span className="spec-stat-number">{totalIssues}</span>
                <span className="spec-stat-label">Issues</span>
              </div>
            </div>
          </div>

          <div className="spec-sidebar-tabs">
            <button 
              className={`spec-sidebar-tab ${sidebarTab === 'outline' ? 'active' : ''}`}
              onClick={() => setSidebarTab('outline')}
            >
              📋 Estrutura
            </button>
            <button 
              className={`spec-sidebar-tab ${sidebarTab === 'issues' ? 'active' : ''}`}
              onClick={() => setSidebarTab('issues')}
            >
              ⚠️ Issues ({totalIssues})
            </button>
            <button 
              className={`spec-sidebar-tab ${sidebarTab === 'comments' ? 'active' : ''}`}
              onClick={() => setSidebarTab('comments')}
            >
              💬 Comentários
            </button>
          </div>

          <div className="spec-sidebar-content">
            {sidebarTab === 'outline' && (
              <ul className="spec-outline-list">
                {specification.sections.map(section => (
                  <li key={section.id} className="spec-outline-item">
                    <a
                      href={`#${section.id}`}
                      className={`spec-outline-link ${selectedSection === section.id ? 'active' : ''}`}
                      onClick={(e) => {
                        e.preventDefault();
                        setSelectedSection(section.id);
                      }}
                    >
                      <span className="section-status-icon">
                        {getSectionStatusIcon(section)}
                      </span>
                      <span>{getSectionIcon(section.type)}</span>
                      <span>{section.title}</span>
                    </a>
                  </li>
                ))}
              </ul>
            )}

            {sidebarTab === 'issues' && (
              <div className="spec-issues-list">
                {allIssues.length === 0 ? (
                  <div className="spec-empty-state">
                    <CheckCircle size={48} />
                    <h4>Nenhuma issue encontrada</h4>
                    <p>A especificação está em conformidade</p>
                  </div>
                ) : (
                  allIssues.map(issue => (
                    <div key={issue.id} className={`spec-issue-item ${issue.severity}`}>
                      <div className="spec-issue-title">{issue.title}</div>
                      <div className="spec-issue-description">{issue.description}</div>
                    </div>
                  ))
                )}
              </div>
            )}

            {sidebarTab === 'comments' && (
              <div className="spec-empty-state">
                <MessageSquare size={48} />
                <h4>Sem comentários</h4>
                <p>Adicione comentários para colaborar na especificação</p>
              </div>
            )}
          </div>
        </div>

        <div className="specification-main">
          <div className="spec-main-header">
            <div className="spec-document-info">
              <h2>{specification.title}</h2>
              <div className="spec-document-meta">
                <div className="spec-version-info">
                  <History size={16} />
                  <span>Versão {specification.version}</span>
                </div>
                <span>Atualizado em {formatDate(specification.updatedAt)}</span>
                <span>{specification.metadata.totalPages} páginas</span>
              </div>
            </div>
            <div className="spec-main-actions">
              <button className="spec-action-button secondary">
                <Eye size={16} />
                Pré-visualizar
              </button>
              <button className="spec-action-button secondary">
                <Settings size={16} />
                Configurar
              </button>
            </div>
          </div>

          <div className="spec-editor-container">
            <div className="spec-editor-main">
              {specification.sections.length === 0 ? (
                <div className="spec-empty-state">
                  <FileText size={64} />
                  <h3>Especificação não gerada</h3>
                  <p>Gere sua especificação funcional a partir dos documentos do projeto</p>
                  <button className="spec-action-button primary" onClick={handleGenerateSpecification}>
                    <RefreshCw size={18} />
                    Gerar Especificação
                  </button>
                </div>
              ) : (
                specification.sections.map(section => (
                  <div key={section.id} id={section.id} className="spec-section">
                    <div className="spec-section-header">
                      <h2 className="spec-section-title">
                        {getSectionIcon(section.type)}
                        {section.title}
                      </h2>
                      <div className="spec-section-actions">
                        <button 
                          className="spec-section-action"
                          onClick={() => handleEditSection(section)}
                        >
                          <Edit size={14} />
                          Editar
                        </button>
                        <button className="spec-section-action">
                          <MessageSquare size={14} />
                          Comentar
                        </button>
                      </div>
                    </div>
                    <div 
                      className="spec-section-content"
                      dangerouslySetInnerHTML={{ __html: section.content.replace(/\n/g, '<br>') }}
                    />
                  </div>
                ))
              )}

              {/* Seção de Requisitos Funcionais */}
              {specification.functionalRequirements.length > 0 && (
                <div id="functional-requirements" className="spec-section">
                  <div className="spec-section-header">
                    <h2 className="spec-section-title">
                      ⚙️ 3. Requisitos Funcionais
                    </h2>
                  </div>
                  <RequirementsTable requirements={specification.functionalRequirements} />
                </div>
              )}

              {/* Seção de Requisitos Não-Funcionais */}
              {specification.nonFunctionalRequirements.length > 0 && (
                <div id="non-functional-requirements" className="spec-section">
                  <div className="spec-section-header">
                    <h2 className="spec-section-title">
                      📊 4. Requisitos Não-Funcionais
                    </h2>
                  </div>
                  <RequirementsTable requirements={specification.nonFunctionalRequirements} />
                </div>
              )}

              {/* Seção do Modelo de Dados */}
              {specification.dataEntities.length > 0 && (
                <div id="data-model" className="spec-section">
                  <div className="spec-section-header">
                    <h2 className="spec-section-title">
                      🗃️ 5. Modelo de Dados
                    </h2>
                  </div>
                  <DataModelViewer entities={specification.dataEntities} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {showGenerationModal && (
        <SpecificationGenerationModal
          isOpen={showGenerationModal}
          onClose={() => setShowGenerationModal(false)}
          onGenerate={(request) => {
            // Simulate generation
            console.log('Generating specification with request:', request);
            setShowGenerationModal(false);
          }}
          projectId={currentProjectId}
        />
      )}

      {showEditorModal && selectedSectionForEdit && (
        <SpecificationEditorModal
          isOpen={showEditorModal}
          section={selectedSectionForEdit}
          onClose={() => setShowEditorModal(false)}
          onSave={handleSaveSection}
        />
      )}
    </div>
  );
};

export default SpecificationPage;