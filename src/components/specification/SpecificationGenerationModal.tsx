/* src/components/specification/SpecificationGenerationModal.tsx */
import React, { useState, useEffect } from 'react';
import { 
  SpecificationGenerationRequest, 
  SpecificationSectionType 
} from '../../types/';
import { Document } from '../../types';
import './SpecificationGenerationModal.css';

interface SpecificationGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (request: SpecificationGenerationRequest) => void;
  projectId: string;
  isGenerating?: boolean;
}

// Mock documents data
const mockDocuments: Document[] = [
  {
    id: '1',
    projectId: 'project1',
    name: 'requirements.pdf',
    originalName: 'Requisitos do Sistema.pdf',
    size: 2048576,
    type: 'application/pdf',
    uploadedAt: '2024-03-10T09:00:00',
    status: 'analyzed' as any,
    extractedEntities: [],
    requirements: [],
    analysisIssues: []
  },
  {
    id: '2',
    projectId: 'project1',
    name: 'business_rules.docx',
    originalName: 'Regras de Negócio.docx',
    size: 1024768,
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    uploadedAt: '2024-03-10T10:30:00',
    status: 'analyzed' as any,
    extractedEntities: [],
    requirements: [],
    analysisIssues: []
  },
  {
    id: '3',
    projectId: 'project1',
    name: 'user_stories.md',
    originalName: 'Histórias de Usuário.md',
    size: 512384,
    type: 'text/markdown',
    uploadedAt: '2024-03-10T11:15:00',
    status: 'analyzed' as any,
    extractedEntities: [],
    requirements: [],
    analysisIssues: []
  }
];

const SpecificationGenerationModal: React.FC<SpecificationGenerationModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  projectId,
  isGenerating = false
}) => {
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>(['1', '2', '3']);
  const [selectedSections, setSelectedSections] = useState<SpecificationSectionType[]>([
    SpecificationSectionType.INTRODUCTION,
    SpecificationSectionType.OVERVIEW,
    SpecificationSectionType.FUNCTIONAL_REQUIREMENTS,
    SpecificationSectionType.NON_FUNCTIONAL_REQUIREMENTS
  ]);
  const [includeDataModel, setIncludeDataModel] = useState(true);
  const [includeUserStories, setIncludeUserStories] = useState(true);
  const [includeBusinessRules, setIncludeBusinessRules] = useState(true);
  const [includeGlossary, setIncludeGlossary] = useState(false);
  const [detailLevel, setDetailLevel] = useState<'basic' | 'detailed' | 'comprehensive'>('detailed');
  const [targetAudience, setTargetAudience] = useState<'technical' | 'business' | 'mixed'>('mixed');
  const [templateStyle, setTemplateStyle] = useState<'ieee' | 'agile' | 'custom'>('agile');
  const [customInstructions, setCustomInstructions] = useState('');

  const handleDocumentToggle = (documentId: string) => {
    setSelectedDocuments(prev =>
      prev.includes(documentId)
        ? prev.filter(id => id !== documentId)
        : [...prev, documentId]
    );
  };

  const handleSectionToggle = (sectionType: SpecificationSectionType) => {
    setSelectedSections(prev =>
      prev.includes(sectionType)
        ? prev.filter(type => type !== sectionType)
        : [...prev, sectionType]
    );
  };

  const handleGenerate = () => {
    const request: SpecificationGenerationRequest = {
      projectId,
      documentIds: selectedDocuments,
      includeDataModel,
      includeUserStories,
      includeBusinessRules,
      includeGlossary,
      detailLevel,
      targetAudience,
      templateStyle,
      customInstructions: customInstructions.trim() || undefined,
      sectionsToGenerate: selectedSections
    };
    onGenerate(request);
  };

  const getSectionInfo = (type: SpecificationSectionType) => {
    switch (type) {
      case SpecificationSectionType.INTRODUCTION:
        return {
          icon: '📖',
          title: 'Introdução',
          description: 'Propósito, escopo e contexto do projeto'
        };
      case SpecificationSectionType.OVERVIEW:
        return {
          icon: '🔍',
          title: 'Visão Geral',
          description: 'Arquitetura conceitual e objetivos do sistema'
        };
      case SpecificationSectionType.FUNCTIONAL_REQUIREMENTS:
        return {
          icon: '⚙️',
          title: 'Requisitos Funcionais',
          description: 'Funcionalidades específicas que o sistema deve ter'
        };
      case SpecificationSectionType.NON_FUNCTIONAL_REQUIREMENTS:
        return {
          icon: '📊',
          title: 'Requisitos Não-Funcionais',
          description: 'Performance, segurança, usabilidade, etc.'
        };
      case SpecificationSectionType.DATA_MODEL:
        return {
          icon: '🗃️',
          title: 'Modelo de Dados',
          description: 'Estrutura de dados e relacionamentos'
        };
      case SpecificationSectionType.USER_INTERFACE:
        return {
          icon: '🖥️',
          title: 'Interface do Usuário',
          description: 'Especificações de telas e interações'
        };
      case SpecificationSectionType.INTEGRATION:
        return {
          icon: '🔗',
          title: 'Integrações',
          description: 'APIs e sistemas externos'
        };
      case SpecificationSectionType.BUSINESS_RULES:
        return {
          icon: '📋',
          title: 'Regras de Negócio',
          description: 'Lógica e políticas específicas do domínio'
        };
      case SpecificationSectionType.GLOSSARY:
        return {
          icon: '📚',
          title: 'Glossário',
          description: 'Definições de termos técnicos e do domínio'
        };
      default:
        return { icon: '📄', title: 'Seção', description: '' };
    }
  };

  const getDocumentIcon = (type: string) => {
    if (type.includes('pdf')) return '📕';
    if (type.includes('word') || type.includes('document')) return '📘';
    if (type.includes('markdown')) return '📝';
    if (type.includes('text')) return '📄';
    return '📄';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="spec-generation-modal">
        <div className="modal-header">
          <h2>🚀 Gerar Especificação Funcional</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="generation-step">
            <h3>📁 Documentos Fonte</h3>
            <p>Selecione os documentos que serão utilizados para gerar a especificação:</p>
            <div className="documents-grid">
              {mockDocuments.map(doc => (
                <div
                  key={doc.id}
                  className={`document-card ${selectedDocuments.includes(doc.id) ? 'selected' : ''}`}
                  onClick={() => handleDocumentToggle(doc.id)}
                >
                  <div className="document-icon">{getDocumentIcon(doc.type)}</div>
                  <div className="document-info">
                    <div className="document-name">{doc.originalName}</div>
                    <div className="document-meta">
                      {formatFileSize(doc.size)} • {new Date(doc.uploadedAt).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="document-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedDocuments.includes(doc.id)}
                      onChange={() => handleDocumentToggle(doc.id)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="generation-step">
            <h3>📋 Seções a Gerar</h3>
            <p>Escolha quais seções devem ser incluídas na especificação:</p>
            <div className="sections-grid">
              {Object.values(SpecificationSectionType).map(sectionType => {
                const info = getSectionInfo(sectionType);
                return (
                  <div
                    key={sectionType}
                    className={`section-card ${selectedSections.includes(sectionType) ? 'selected' : ''}`}
                    onClick={() => handleSectionToggle(sectionType)}
                  >
                    <div className="section-icon">{info.icon}</div>
                    <div className="section-info">
                      <div className="section-title">{info.title}</div>
                      <div className="section-description">{info.description}</div>
                    </div>
                    <div className="section-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedSections.includes(sectionType)}
                        onChange={() => handleSectionToggle(sectionType)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="generation-step">
            <h3>⚙️ Configurações Avançadas</h3>
            <div className="config-grid">
              <div className="config-group">
                <h4>Componentes Extras</h4>
                <div className="checkbox-options">
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeDataModel}
                      onChange={(e) => setIncludeDataModel(e.target.checked)}
                    />
                    <span>🗃️ Modelo de Dados</span>
                  </label>
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeUserStories}
                      onChange={(e) => setIncludeUserStories(e.target.checked)}
                    />
                    <span>👤 Histórias de Usuário</span>
                  </label>
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeBusinessRules}
                      onChange={(e) => setIncludeBusinessRules(e.target.checked)}
                    />
                    <span>📋 Regras de Negócio</span>
                  </label>
                  <label className="checkbox-option">
                    <input
                      type="checkbox"
                      checked={includeGlossary}
                      onChange={(e) => setIncludeGlossary(e.target.checked)}
                    />
                    <span>📚 Glossário</span>
                  </label>
                </div>
              </div>

              <div className="config-group">
                <h4>Nível de Detalhamento</h4>
                <div className="radio-options">
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="detailLevel"
                      value="basic"
                      checked={detailLevel === 'basic'}
                      onChange={(e) => setDetailLevel(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">📝 Básico</span>
                      <span className="radio-description">Especificação concisa com informações essenciais</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="detailLevel"
                      value="detailed"
                      checked={detailLevel === 'detailed'}
                      onChange={(e) => setDetailLevel(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">📊 Detalhado</span>
                      <span className="radio-description">Especificação completa com exemplos e diagramas</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="detailLevel"
                      value="comprehensive"
                      checked={detailLevel === 'comprehensive'}
                      onChange={(e) => setDetailLevel(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">🔍 Abrangente</span>
                      <span className="radio-description">Especificação exaustiva com análises aprofundadas</span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="config-group">
                <h4>Público-Alvo</h4>
                <div className="radio-options">
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="targetAudience"
                      value="technical"
                      checked={targetAudience === 'technical'}
                      onChange={(e) => setTargetAudience(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">👩‍💻 Técnico</span>
                      <span className="radio-description">Foco em aspectos técnicos e implementação</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="targetAudience"
                      value="business"
                      checked={targetAudience === 'business'}
                      onChange={(e) => setTargetAudience(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">💼 Negócio</span>
                      <span className="radio-description">Linguagem acessível para stakeholders de negócio</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="targetAudience"
                      value="mixed"
                      checked={targetAudience === 'mixed'}
                      onChange={(e) => setTargetAudience(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">🎯 Misto</span>
                      <span className="radio-description">Equilibrio entre aspectos técnicos e de negócio</span>
                    </div>
                  </label>
                </div>
              </div>

              <div className="config-group">
                <h4>Template de Documento</h4>
                <div className="radio-options">
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="templateStyle"
                      value="ieee"
                      checked={templateStyle === 'ieee'}
                      onChange={(e) => setTemplateStyle(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">📐 IEEE</span>
                      <span className="radio-description">Padrão IEEE 830 para documentos de requisitos</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="templateStyle"
                      value="agile"
                      checked={templateStyle === 'agile'}
                      onChange={(e) => setTemplateStyle(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">🚀 Ágil</span>
                      <span className="radio-description">Formato moderno e flexível para metodologias ágeis</span>
                    </div>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="templateStyle"
                      value="custom"
                      checked={templateStyle === 'custom'}
                      onChange={(e) => setTemplateStyle(e.target.value as any)}
                    />
                    <div className="radio-info">
                      <span className="radio-title">🎨 Personalizado</span>
                      <span className="radio-description">Template customizado baseado nas instruções</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="generation-step">
            <h3>📝 Instruções Personalizadas</h3>
            <p>Adicione instruções específicas para personalizar a geração da especificação:</p>
            <textarea
              className="instructions-textarea"
              placeholder="Ex: Incluir diagramas de sequência UML, focar em aspectos de segurança, usar terminologia específica do domínio bancário, incluir métricas de performance detalhadas..."
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              rows={4}
            />
            <div className="instructions-help">
              <p>💡 Exemplos de instruções úteis:</p>
              <ul>
                <li>Incluir diagramas específicos (UML, fluxogramas, wireframes)</li>
                <li>Focar em aspectos particulares (segurança, performance, usabilidade)</li>
                <li>Usar terminologia específica do domínio</li>
                <li>Incluir referências a frameworks ou tecnologias</li>
                <li>Adicionar seções customizadas (compliance, auditoria, etc.)</li>
                <li>Especificar formatos de tabelas ou listas</li>
              </ul>
            </div>
          </div>

          <div className="generation-summary">
            <h3>📋 Resumo da Geração</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Documentos selecionados:</span>
                <span className="summary-value">{selectedDocuments.length}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Seções a gerar:</span>
                <span className="summary-value">{selectedSections.length}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Nível de detalhamento:</span>
                <span className="summary-value">{detailLevel}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Público-alvo:</span>
                <span className="summary-value">{targetAudience}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Template:</span>
                <span className="summary-value">{templateStyle}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Componentes extras:</span>
                <span className="summary-value">
                  {[
                    includeDataModel && 'Modelo de Dados',
                    includeUserStories && 'User Stories',
                    includeBusinessRules && 'Regras de Negócio',
                    includeGlossary && 'Glossário'
                  ].filter(Boolean).join(', ') || 'Nenhum'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {selectedDocuments.length === 0 && (
              <span className="warning">⚠️ Selecione pelo menos um documento fonte</span>
            )}
            {selectedSections.length === 0 && (
              <span className="warning">⚠️ Selecione pelo menos uma seção para gerar</span>
            )}
          </div>
          <div className="footer-actions">
            <button 
              className="btn-cancel" 
              onClick={onClose}
              disabled={isGenerating}
            >
              Cancelar
            </button>
            <button 
              className="btn-generate" 
              onClick={handleGenerate}
              disabled={selectedDocuments.length === 0 || selectedSections.length === 0 || isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Gerando Especificação...
                </>
              ) : (
                <>
                  ✨ Gerar Especificação
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpecificationGenerationModal;