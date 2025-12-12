import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import '../documents/RequirementsHistoryModal.css';
import './RequirementsSelectionModal.css';
import { getDocumentVersions, getDocumentVersion } from '../../services/documentService';
import { listSessions, SessionSummary } from '../../services/requirementsHistoryService';

interface DocumentVersion {
  version: number;
  created_at: string;
  change_description: string;
  change_type: 'analysis' | 'refinement' | 'manual_edit';
  doc_size: number;
}

interface RequirementsSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (sessionId: string, sessionName: string, version: number, documentContent: string) => void;
}

const RequirementsSelectionModal: React.FC<RequirementsSelectionModalProps> = ({
  isOpen,
  onClose,
  onSelect
}) => {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // View mode: sessions -> versions -> preview
  const [viewMode, setViewMode] = useState<'sessions' | 'versions' | 'preview'>('sessions');

  // Selection state
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [selectedSessionName, setSelectedSessionName] = useState<string>('');
  const [selectedVersion, setSelectedVersion] = useState<number>(0);
  const [documentContent, setDocumentContent] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      resetState();
      loadSessions();
    }
  }, [isOpen]);

  const resetState = () => {
    setViewMode('sessions');
    setSelectedSessionId('');
    setSelectedSessionName('');
    setSelectedVersion(0);
    setDocumentContent('');
    setVersions([]);
    setError(null);
  };

  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listSessions(50, 0);
      // Filtra apenas sessões completas
      const completedSessions = response.sessions.filter(s => s.status === 'completed');
      setSessions(completedSessions);
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Erro ao carregar sessões de requisitos');
    } finally {
      setLoading(false);
    }
  };

  const loadVersions = async (sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDocumentVersions(sessionId);
      setVersions(response.versions || []);
    } catch (err) {
      console.error('Error loading versions:', err);
      setError('Erro ao carregar versões');
    } finally {
      setLoading(false);
    }
  };

  const loadDocumentContent = async (sessionId: string, version: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDocumentVersion(sessionId, version);
      setDocumentContent(response.content || '');
    } catch (err) {
      console.error('Error loading document:', err);
      setError('Erro ao carregar documento');
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

  // Handlers
  const handleSessionClick = (session: SessionSummary) => {
    setSelectedSessionId(session.id);
    setSelectedSessionName(session.session_name);
    setViewMode('versions');
    loadVersions(session.id);
  };

  const handleVersionClick = (version: DocumentVersion) => {
    setSelectedVersion(version.version);
    setViewMode('preview');
    loadDocumentContent(selectedSessionId, version.version);
  };

  const handleBackToSessions = () => {
    setViewMode('sessions');
    setVersions([]);
    setSelectedSessionId('');
    setSelectedSessionName('');
    loadSessions();
  };

  const handleBackToVersions = () => {
    setViewMode('versions');
    setDocumentContent('');
    setSelectedVersion(0);
  };

  const handleSelect = () => {
    if (selectedSessionId && selectedVersion && documentContent) {
      onSelect(selectedSessionId, selectedSessionName, selectedVersion, documentContent);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className={`history-modal ${viewMode === 'preview' ? 'preview-mode' : ''}`}>
        <div className="modal-header">
          <h2>
            {viewMode === 'sessions' && '📋 Selecionar Documento de Requisitos'}
            {viewMode === 'versions' && `📋 ${selectedSessionName} - Versões`}
            {viewMode === 'preview' && `📋 ${selectedSessionName} - v${selectedVersion}`}
          </h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {/* Navegação */}
        {(viewMode === 'versions' || viewMode === 'preview') && (
          <div className="navigation-bar">
            <button
              className="btn-back"
              onClick={viewMode === 'preview' ? handleBackToVersions : handleBackToSessions}
            >
              ← {viewMode === 'preview' ? 'Voltar para Versões' : 'Voltar para Sessões'}
            </button>
            {viewMode === 'preview' && (
              <span className="selection-info">
                Sessão: <strong>{selectedSessionName}</strong> | Versão: <strong>v{selectedVersion}</strong>
              </span>
            )}
          </div>
        )}

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner-large"></div>
              <p>
                {viewMode === 'sessions' && 'Carregando sessões...'}
                {viewMode === 'versions' && 'Carregando versões...'}
                {viewMode === 'preview' && 'Carregando documento...'}
              </p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button className="btn-retry" onClick={() => {
                if (viewMode === 'sessions') loadSessions();
                else if (viewMode === 'versions') loadVersions(selectedSessionId);
                else if (viewMode === 'preview') loadDocumentContent(selectedSessionId, selectedVersion);
              }}>
                Tentar Novamente
              </button>
            </div>
          )}

          {/* Lista de Sessões */}
          {!loading && !error && viewMode === 'sessions' && (
            <>
              {sessions.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📄</div>
                  <p>Nenhum documento de requisitos encontrado</p>
                  <p className="empty-hint">
                    Gere um documento de requisitos primeiro na página de Documentos
                  </p>
                </div>
              ) : (
                <div className="sessions-list">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      className="session-item"
                      onClick={() => handleSessionClick(session)}
                    >
                      <div className="session-header">
                        <div className="session-title">
                          <span className="session-icon">📄</span>
                          <span className="session-name">{session.session_name}</span>
                        </div>
                        <span className="status-badge status-completed">Concluído</span>
                      </div>

                      <div className="session-details">
                        <div className="session-info">
                          <span className="info-label">Criado em:</span>
                          <span className="info-value">{formatDate(session.created_at)}</span>
                        </div>
                        <div className="session-info">
                          <span className="info-label">Tamanho:</span>
                          <span className="info-value">{formatFileSize(session.doc_size)}</span>
                        </div>
                      </div>

                      <div className="session-action">
                        <span className="action-hint">Clique para ver versões →</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {/* Lista de Versões */}
          {!loading && !error && viewMode === 'versions' && (
            <>
              {versions.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📄</div>
                  <p>Nenhuma versão encontrada</p>
                </div>
              ) : (
                <div className="sessions-list">
                  {versions.map((version) => (
                    <div
                      key={version.version}
                      className="session-item"
                      onClick={() => handleVersionClick(version)}
                    >
                      <div className="session-header">
                        <div className="session-title">
                          <span className="session-icon">📝</span>
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
            </>
          )}

          {/* Preview do Documento */}
          {!loading && !error && viewMode === 'preview' && (
            <div className="document-preview">
              <div className="preview-header">
                <h3>📄 Preview do Documento</h3>
              </div>
              <div className="preview-content markdown-body">
                <ReactMarkdown>{documentContent}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {viewMode === 'sessions' && sessions.length > 0 && (
              <span className="sessions-count">
                {sessions.length} documento(s) disponível(is)
              </span>
            )}
            {viewMode === 'versions' && versions.length > 0 && (
              <span className="sessions-count">
                {versions.length} versão(ões) disponível(is)
              </span>
            )}
            {viewMode === 'preview' && (
              <span className="sessions-count">
                Seleção: {selectedSessionName} v{selectedVersion}
              </span>
            )}
          </div>
          <div className="footer-actions">
            <button className="btn-close" onClick={onClose}>
              Cancelar
            </button>
            {viewMode === 'preview' && (
              <button
                className="btn-select"
                onClick={handleSelect}
                disabled={!documentContent}
              >
                ✅ Selecionar este Documento
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RequirementsSelectionModal;
