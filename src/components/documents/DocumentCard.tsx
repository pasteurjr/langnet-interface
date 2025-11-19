import React from 'react';
import { Document, DocumentStatus } from '../../types';
import './DocumentCard.css';

interface DocumentCardProps {
  document: Document;
  onView: (document: Document) => void;
  onDelete: (documentId: string) => void;
  onReanalyze: (documentId: string) => void;
  onExtractRequirements?: (documentId: string) => void;
  onChatWithAgent?: (documentId: string) => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  onView,
  onDelete,
  onReanalyze,
  onExtractRequirements,
  onChatWithAgent
}) => {
  const getStatusIcon = (status: DocumentStatus) => {
    switch (status) {
      case DocumentStatus.UPLOADED:
        return '📄';
      case DocumentStatus.ANALYZING:
        return '🔄';
      case DocumentStatus.ANALYZED:
        return '✅';
      case DocumentStatus.ERROR:
        return '❌';
      default:
        return '📄';
    }
  };

  const getStatusText = (status: DocumentStatus) => {
    switch (status) {
      case DocumentStatus.UPLOADED:
        return 'Carregado';
      case DocumentStatus.ANALYZING:
        return 'Analisando...';
      case DocumentStatus.ANALYZED:
        return 'Analisado';
      case DocumentStatus.ERROR:
        return 'Erro na análise';
      default:
        return 'Desconhecido';
    }
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('doc')) return '📝';
    if (type.includes('text')) return '📃';
    if (type.includes('markdown')) return '📋';
    return '📄';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="document-card">
      <div className="document-header">
        <div className="document-icon">
          {getFileIcon(document.type)}
        </div>
        <div className="document-info">
          <h3 className="document-name" title={document.originalName}>
            {document.name}
          </h3>
          <div className="document-meta">
            <span className="file-size">{formatFileSize(document.size)}</span>
            <span className="upload-date">
              {new Date(document.uploadedAt).toLocaleDateString('pt-BR')}
            </span>
          </div>
        </div>
        <div className={`document-status status-${document.status}`}>
          <span className="status-icon">{getStatusIcon(document.status)}</span>
          <span className="status-text">{getStatusText(document.status)}</span>
        </div>
      </div>

      {document.status === DocumentStatus.ANALYZING && (
        <div className="analysis-progress" style={{
          padding: '16px',
          background: '#f8f9fa',
          borderRadius: '6px',
          marginTop: '12px'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '12px'
          }}>
            <div>
              <div style={{ fontWeight: '600', fontSize: '14px', color: '#333', marginBottom: '4px' }}>
                🔍 Análise em Andamento
              </div>
              <div style={{ fontSize: '13px', color: '#666' }}>
                {document.enableWebResearch
                  ? '🌐 Com pesquisa web (6-10 min estimados)'
                  : '⚡ Análise rápida (3-4 min estimados)'}
              </div>
            </div>
            <div className="spinner" style={{
              width: '24px',
              height: '24px',
              border: '3px solid #e0e0e0',
              borderTop: '3px solid #2196F3',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
          </div>

          {document.analysisProgress !== undefined && (
            <>
              <div className="progress-bar" style={{
                width: '100%',
                height: '8px',
                background: '#e0e0e0',
                borderRadius: '4px',
                overflow: 'hidden',
                marginBottom: '8px'
              }}>
                <div
                  className="progress-fill"
                  style={{
                    width: `${document.analysisProgress}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #2196F3, #21CBF3)',
                    transition: 'width 0.3s ease'
                  }}
                ></div>
              </div>
              <div style={{ fontSize: '12px', color: '#888', textAlign: 'right' }}>
                {document.analysisProgress}% concluído
              </div>
            </>
          )}

          <div style={{
            marginTop: '12px',
            padding: '10px',
            background: '#fff',
            borderRadius: '4px',
            fontSize: '12px',
            color: '#666'
          }}>
            <div style={{ marginBottom: '6px' }}>
              📋 Fases: Parsing → Extraction → {document.enableWebResearch && 'Web Research → '}Requirements Generation
            </div>
            <div style={{ fontStyle: 'italic', color: '#999' }}>
              Por favor aguarde... A análise está em processamento.
            </div>
          </div>
        </div>
      )}

      {document.status === DocumentStatus.ANALYZED && (
        <div className="analysis-summary">
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-number">{document.extractedEntities.length}</span>
              <span className="stat-label">Entidades</span>
            </div>
            <div className="stat">
              <span className="stat-number">{document.requirements.length}</span>
              <span className="stat-label">Requisitos</span>
            </div>
            <div className="stat">
              <span className="stat-number">{document.analysisIssues.length}</span>
              <span className="stat-label">Issues</span>
            </div>
          </div>
          
          {document.analysisResults && (
            <div className="analysis-preview">
              <p className="summary-text">{document.analysisResults.summary}</p>
            </div>
          )}
        </div>
      )}

      <div className="document-actions">
        <button
          className="btn-view"
          onClick={() => onView(document)}
          disabled={document.status === DocumentStatus.ANALYZING}
        >
          👁️ Visualizar
        </button>

        {(document.status === DocumentStatus.UPLOADED || document.status === DocumentStatus.ERROR) && onExtractRequirements && (
          <button
            className="btn-extract-requirements"
            onClick={() => onExtractRequirements(document.id)}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              fontWeight: '600',
              padding: '10px 18px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'all 0.2s'
            }}
          >
            🔍 Extrair Requisitos
          </button>
        )}

        {document.status === DocumentStatus.ANALYZED && document.executionId && (
          <button
            className="btn-view-requirements"
            onClick={() => window.location.href = `/project/${document.projectId}/requirements/${document.executionId}`}
            title="View generated requirements document"
          >
            📄 Ver Requisitos
          </button>
        )}

        {document.status === DocumentStatus.ANALYZED && onChatWithAgent && (
          <button
            className="btn-chat-agent"
            onClick={() => onChatWithAgent(document.id)}
            style={{
              background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
              color: 'white',
              fontWeight: '600',
              padding: '10px 18px',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'all 0.2s'
            }}
          >
            💬 Refinar com Agente
          </button>
        )}

        {document.status === DocumentStatus.ANALYZED && (
          <button
            className="btn-reanalyze"
            onClick={() => onReanalyze(document.id)}
          >
            🔄 Reanalisar
          </button>
        )}

        <button
          className="btn-delete"
          onClick={() => onDelete(document.id)}
          disabled={document.status === DocumentStatus.ANALYZING}
        >
          🗑️ Excluir
        </button>
      </div>
    </div>
  );
};

export default DocumentCard;