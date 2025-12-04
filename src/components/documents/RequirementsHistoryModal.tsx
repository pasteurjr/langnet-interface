import React, { useState, useEffect } from 'react';
import './RequirementsHistoryModal.css';
import { getDocumentVersions } from '../../services/documentService';

interface DocumentVersion {
  version: number;
  created_at: string;
  change_description: string;
  change_type: 'analysis' | 'refinement' | 'manual_edit';
  doc_size: number;
}

interface RequirementsHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  onSelectVersion: (version: number) => void;
}

const RequirementsHistoryModal: React.FC<RequirementsHistoryModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  onSelectVersion
}) => {
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && sessionId) {
      loadVersions();
    }
  }, [isOpen, sessionId]);

  const loadVersions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDocumentVersions(sessionId);
      setVersions(response.versions || []);
    } catch (err) {
      console.error('Error loading versions:', err);
      setError('Erro ao carregar histórico de versões');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      'analysis': '🔍',
      'refinement': '✏️',
      'manual_edit': '📝'
    };
    return icons[type] || '📄';
  };

  const getTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'analysis': 'Análise Inicial',
      'refinement': 'Refinamento',
      'manual_edit': 'Edição Manual'
    };
    return labels[type] || type;
  };

  const getTypeBadge = (type: string) => {
    const typeColors: { [key: string]: string } = {
      'analysis': 'type-analysis',
      'refinement': 'type-refinement',
      'manual_edit': 'type-manual'
    };
    return typeColors[type] || 'type-manual';
  };

  const handleVersionClick = (version: number) => {
    onSelectVersion(version);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          <h2>📜 Histórico de Versões</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner-large"></div>
              <p>Carregando versões...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button className="btn-retry" onClick={loadVersions}>
                Tentar Novamente
              </button>
            </div>
          )}

          {!loading && !error && versions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>Nenhuma versão encontrada</p>
              <p className="empty-hint">
                As versões do documento aparecerão aqui
              </p>
            </div>
          )}

          {!loading && !error && versions.length > 0 && (
            <div className="sessions-list">
              {versions.map((version) => (
                <div
                  key={version.version}
                  className="session-item"
                  onClick={() => handleVersionClick(version.version)}
                >
                  <div className="session-header">
                    <div className="session-title">
                      <span className="session-icon">{getTypeIcon(version.change_type)}</span>
                      <span className="session-name">Versão {version.version}</span>
                    </div>
                    <span className={`status-badge ${getTypeBadge(version.change_type)}`}>
                      {getTypeLabel(version.change_type)}
                    </span>
                  </div>

                  <div className="session-details">
                    <div className="session-info">
                      <span className="info-label">Criado em:</span>
                      <span className="info-value">{formatDate(version.created_at)}</span>
                    </div>

                    <div className="session-info">
                      <span className="info-label">Descrição:</span>
                      <span className="info-value">{version.change_description}</span>
                    </div>

                    <div className="session-info">
                      <span className="info-label">Tamanho:</span>
                      <span className="info-value">{formatFileSize(version.doc_size)}</span>
                    </div>
                  </div>

                  <div className="session-action">
                    <span className="action-hint">Clique para visualizar →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {!loading && versions.length > 0 && (
              <span className="sessions-count">
                {versions.length} versão(ões) encontrada(s)
              </span>
            )}
          </div>
          <div className="footer-actions">
            <button className="btn-close" onClick={onClose}>
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RequirementsHistoryModal;
