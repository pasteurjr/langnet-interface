import React, { useState } from 'react';
import { Document, ExtractedEntity, RequirementItem, AnalysisIssue } from '../../types';
import './DocumentViewModal.css';

interface DocumentViewModalProps {
  isOpen: boolean;
  document: Document | null;
  onClose: () => void;
  onExport: (document: Document, format: 'json' | 'csv' | 'pdf') => void;
}

const DocumentViewModal: React.FC<DocumentViewModalProps> = ({
  isOpen,
  document,
  onClose,
  onExport
}) => {
  const [activeTab, setActiveTab] = useState<'texto' | 'overview' | 'entities' | 'requirements' | 'issues'>('overview');
  // Texto do documento carregado: sem isto, o visualizador mostrava só o que a análise extraiu,
  // e não havia como ler no sistema a fonte que originou todo o pipeline.
  const [textoDoArquivo, setTextoDoArquivo] = React.useState<string>('');
  const [carregandoTexto, setCarregandoTexto] = React.useState(false);
  React.useEffect(() => {
    if (!isOpen || !document?.id || String(activeTab) !== 'texto' || textoDoArquivo) return;
    const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
    setCarregandoTexto(true);
    fetch(`${API}/documents/${document.id}/conteudo`, {
      headers: { Authorization: token ? `Bearer ${token}` : '' },
    })
      .then((r) => r.json())
      .then((d) => setTextoDoArquivo(d.conteudo || d.aviso || 'Sem conteúdo legível.'))
      .catch((e) => setTextoDoArquivo(`Não foi possível ler o arquivo: ${e.message}`))
      .finally(() => setCarregandoTexto(false));
  }, [isOpen, document, activeTab, textoDoArquivo]);

  if (!isOpen || !document) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getEntityTypeIcon = (type: ExtractedEntity['type']) => {
    switch (type) {
      case 'actor': return '👤';
      case 'system': return '💻';
      case 'process': return '⚙️';
      case 'rule': return '📋';
      case 'concept': return '💡';
      default: return '📌';
    }
  };

  const getRequirementTypeColor = (type: RequirementItem['type']) => {
    switch (type) {
      case 'functional': return '#3b82f6';
      case 'non_functional': return '#8b5cf6';
      case 'business_rule': return '#f59e0b';
      case 'constraint': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority: RequirementItem['priority']) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getIssueIcon = (type: AnalysisIssue['type']) => {
    switch (type) {
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'suggestion': return '💡';
      default: return 'ℹ️';
    }
  };

  return (
    <div className="modal-overlay">
      <div className="view-modal">
        <div className="modal-header">
          <div className="header-info">
            <h2>{document.name}</h2>
            <div className="document-metadata">
              <span>📄 {formatFileSize(document.size)}</span>
              <span>📅 {formatDate(document.uploadedAt)}</span>
              <span className={`status-badge status-${document.status}`}>
                {document.status}
              </span>
            </div>
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Visão Geral
          </button>
          <button
            className={`tab ${activeTab === 'texto' ? 'active' : ''}`}
            onClick={() => setActiveTab('texto')}
          >
            📄 Texto do documento
          </button>
          <button 
            className={`tab ${activeTab === 'entities' ? 'active' : ''}`}
            onClick={() => setActiveTab('entities')}
          >
            🏷️ Entidades ({document.extractedEntities.length})
          </button>
          <button 
            className={`tab ${activeTab === 'requirements' ? 'active' : ''}`}
            onClick={() => setActiveTab('requirements')}
          >
            📋 Requisitos ({document.requirements.length})
          </button>
          <button 
            className={`tab ${activeTab === 'issues' ? 'active' : ''}`}
            onClick={() => setActiveTab('issues')}
          >
            ⚠️ Issues ({document.analysisIssues.length})
          </button>
        </div>

        <div className="modal-content">
          {activeTab === 'texto' && (
            <div className="texto-tab">
              {carregandoTexto ? (
                <p>Lendo o arquivo…</p>
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'ui-monospace, monospace',
                              fontSize: 13, lineHeight: 1.5, background: '#f8fafc',
                              border: '1px solid #e5e7eb', borderRadius: 6, padding: 16,
                              maxHeight: '60vh', overflow: 'auto' }}>
                  {textoDoArquivo}
                </pre>
              )}
            </div>
          )}
          {activeTab === 'overview' && (
            <div className="overview-tab">
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">🏷️</div>
                  <div className="stat-info">
                    <div className="stat-number">{document.extractedEntities.length}</div>
                    <div className="stat-label">Entidades Extraídas</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📋</div>
                  <div className="stat-info">
                    <div className="stat-number">{document.requirements.length}</div>
                    <div className="stat-label">Requisitos Identificados</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">⚠️</div>
                  <div className="stat-info">
                    <div className="stat-number">{document.analysisIssues.length}</div>
                    <div className="stat-label">Issues Detectadas</div>
                  </div>
                </div>
              </div>

              {document.analysisResults && (
                <div className="analysis-results">
                  <h3>Resumo da Análise</h3>
                  <p className="analysis-summary">{document.analysisResults.summary}</p>
                  
                  {document.analysisResults.keyFindings.length > 0 && (
                    <div className="key-findings">
                      <h4>Principais Descobertas</h4>
                      <ul>
                        {document.analysisResults.keyFindings.map((finding, index) => (
                          <li key={index}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {document.analysisResults.recommendedActions.length > 0 && (
                    <div className="recommended-actions">
                      <h4>Ações Recomendadas</h4>
                      <ul>
                        {document.analysisResults.recommendedActions.map((action, index) => (
                          <li key={index}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {document.analysisInstructions && (
                <div className="analysis-instructions">
                  <h3>Instruções de Análise Utilizadas</h3>
                  <p>{document.analysisInstructions}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'entities' && (
            <div className="entities-tab">
              <div className="entities-grid">
                {document.extractedEntities.map((entity, index) => (
                  <div key={index} className="entity-card">
                    <div className="entity-header">
                      <span className="entity-icon">{getEntityTypeIcon(entity.type)}</span>
                      <div className="entity-info">
                        <div className="entity-name">{entity.name}</div>
                        <div className="entity-type">{entity.type}</div>
                      </div>
                      <div className="confidence-badge">
                        {Math.round(entity.confidence * 100)}%
                      </div>
                    </div>
                    <div className="entity-description">
                      {entity.description}
                    </div>
                  </div>
                ))}
              </div>
              {document.extractedEntities.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">🏷️</div>
                  <p>Nenhuma entidade foi extraída deste documento.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'requirements' && (
            <div className="requirements-tab">
              <div className="requirements-list">
                {document.requirements.map((requirement, index) => (
                  <div key={index} className="requirement-card">
                    <div className="requirement-header">
                      <div className="requirement-info">
                        <div className="requirement-title">{requirement.title}</div>
                        <div className="requirement-meta">
                          <span 
                            className="requirement-type"
                            style={{ backgroundColor: getRequirementTypeColor(requirement.type) }}
                          >
                            {requirement.type}
                          </span>
                          <span 
                            className="requirement-priority"
                            style={{ color: getPriorityColor(requirement.priority) }}
                          >
                            {requirement.priority}
                          </span>
                          <span className="requirement-source">
                            📄 {requirement.source}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="requirement-description">
                      {requirement.description}
                    </div>
                  </div>
                ))}
              </div>
              {document.requirements.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">📋</div>
                  <p>Nenhum requisito foi identificado neste documento.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'issues' && (
            <div className="issues-tab">
              <div className="issues-list">
                {document.analysisIssues.map((issue, index) => (
                  <div key={index} className={`issue-card issue-${issue.type}`}>
                    <div className="issue-header">
                      <span className="issue-icon">{getIssueIcon(issue.type)}</span>
                      <div className="issue-info">
                        <div className="issue-title">{issue.title}</div>
                        {issue.documentName && (
                          <div className="issue-location">
                            📄 {issue.documentName}
                            {issue.location && ` - ${issue.location}`}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="issue-description">
                      {issue.description}
                    </div>
                  </div>
                ))}
              </div>
              {document.analysisIssues.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">✅</div>
                  <p>Nenhuma issue foi detectada neste documento.</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            <span className="document-id">ID: {document.id}</span>
          </div>
          <div className="footer-actions">
            <button 
              className="btn-export" 
              onClick={() => onExport(document, 'json')}
            >
              📄 Exportar JSON
            </button>
            <button 
              className="btn-export" 
              onClick={() => onExport(document, 'csv')}
            >
              📊 Exportar CSV
            </button>
            <button 
              className="btn-close" 
              onClick={onClose}
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewModal;