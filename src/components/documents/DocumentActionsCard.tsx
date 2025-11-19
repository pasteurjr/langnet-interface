import React from 'react';
import './DocumentActionsCard.css';

interface DocumentActionsCardProps {
  filename: string;
  content: string;
  executionId?: string;
  projectId?: string;
  onEdit?: () => void;
  onView?: () => void;
  onExportPDF?: () => void;
}

const DocumentActionsCard: React.FC<DocumentActionsCardProps> = ({
  filename,
  content,
  executionId,
  projectId,
  onEdit,
  onView,
  onExportPDF
}) => {
  const getFileSize = () => {
    const len = content?.length || 0;
    return len > 1000 ? `${Math.round(len / 1024)}KB` : `${len} chars`;
  };

  const getExecutionIdShort = () => {
    return executionId ? executionId.substring(0, 8) + '...' : '';
  };

  return (
    <div className="document-actions-card">
      <div className="doc-card-header">
        <span className="doc-icon">📋</span>
        <div className="doc-info">
          <h4 className="doc-filename">{filename || 'requisitos.md'}</h4>
          <span className="doc-meta">
            {executionId && `ID: ${getExecutionIdShort()}`}
            {executionId && ' • '}
            {getFileSize()}
          </span>
        </div>
      </div>

      <div className="doc-card-actions">
        {onEdit && (
          <button className="btn-doc-action btn-edit" onClick={onEdit}>
            <span className="icon">✏️</span>
            <span>Editar</span>
          </button>
        )}
        {onView && (
          <button className="btn-doc-action btn-view" onClick={onView}>
            <span className="icon">👁️</span>
            <span>Visualizar</span>
          </button>
        )}
        {onExportPDF && (
          <button className="btn-doc-action btn-pdf" onClick={onExportPDF}>
            <span className="icon">📄</span>
            <span>Exportar PDF</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default DocumentActionsCard;
