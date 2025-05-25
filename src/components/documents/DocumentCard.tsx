import React from 'react';
import { Document, DocumentStatus } from '../../types';
import './DocumentCard.css';

interface DocumentCardProps {
  document: Document;
  onView: (document: Document) => void;
  onDelete: (documentId: string) => void;
  onReanalyze: (documentId: string) => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({
  document,
  onView,
  onDelete,
  onReanalyze
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

      {document.status === DocumentStatus.ANALYZING && document.analysisProgress && (
        <div className="analysis-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${document.analysisProgress}%` }}
            ></div>
          </div>
          <span className="progress-text">{document.analysisProgress}%</span>
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