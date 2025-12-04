import React, { useState, useEffect } from 'react';
import './RequirementsHistoryModal.css';
import { getDocumentVersions } from '../../services/documentService';
import { listSessions, SessionSummary } from '../../services/requirementsHistoryService';

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
  sessionId?: string;
  onSelectSession?: (sessionId: string, sessionName: string) => void;
  onSelectVersion?: (version: number) => void;
}

const RequirementsHistoryModal: React.FC<RequirementsHistoryModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  onSelectSession,
  onSelectVersion
}) => {
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'sessions' | 'versions'>('sessions');
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [selectedSessionName, setSelectedSessionName] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      if (sessionId) {
        // Se já tem sessionId, mostra versões direto
        setViewMode('versions');
        setSelectedSessionId(sessionId);
        loadVersions(sessionId);
      } else {
        // Se não tem sessionId, mostra lista de sessões
        setViewMode('sessions');
        loadSessions();
      }
    }
  }, [isOpen, sessionId]);

  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listSessions(50, 0);
      setSessions(response.sessions);
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Erro ao carregar histórico de sessões');
    } finally {
      setLoading(false);
    }
  };

  const loadVersions = async (sessId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getDocumentVersions(sessId);
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

  const handleSessionClick = (session: SessionSummary) => {
    // Se está em modo de listar sessões, troca para modo de versões
    setSelectedSessionId(session.id);
    setSelectedSessionName(session.session_name);
    setViewMode('versions');
    loadVersions(session.id);
  };

  const handleVersionClick = (version: number) => {
    if (onSelectVersion) {
      onSelectVersion(version);
    }
    // Se veio sem sessionId inicial, precisa chamar onSelectSession também
    if (!sessionId && onSelectSession && selectedSessionId) {
      onSelectSession(selectedSessionId, selectedSessionName);
    }
    onClose();
  };

  const handleBackToSessions = () => {
    setViewMode('sessions');
    setVersions([]);
    loadSessions();
  };

  const getStatusBadge = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'completed': 'status-completed',
      'running': 'status-running',
      'failed': 'status-failed',
      'pending': 'status-pending'
    };
    return statusColors[status] || 'status-pending';
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      'completed': 'Concluído',
      'running': 'Executando',
      'failed': 'Falhou',
      'pending': 'Pendente'
    };
    return labels[status] || status;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          <h2>
            {viewMode === 'sessions' ? '📜 Histórico de Documentos' : '📜 Histórico de Versões'}
            {viewMode === 'versions' && !sessionId && (
              <button className="btn-back" onClick={handleBackToSessions} style={{marginLeft: '10px', fontSize: '14px'}}>
                ← Voltar
              </button>
            )}
          </h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner-large"></div>
              <p>{viewMode === 'sessions' ? 'Carregando sessões...' : 'Carregando versões...'}</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button className="btn-retry" onClick={() => viewMode === 'sessions' ? loadSessions() : loadVersions(selectedSessionId)}>
                Tentar Novamente
              </button>
            </div>
          )}

          {/* Modo: Lista de Sessões */}
          {!loading && !error && viewMode === 'sessions' && sessions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>Nenhum documento gerado ainda</p>
              <p className="empty-hint">
                Os documentos de requisitos gerados aparecerão aqui
              </p>
            </div>
          )}

          {!loading && !error && viewMode === 'sessions' && sessions.length > 0 && (
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
                    <span className={`status-badge ${getStatusBadge(session.status)}`}>
                      {getStatusLabel(session.status)}
                    </span>
                  </div>

                  <div className="session-details">
                    <div className="session-info">
                      <span className="info-label">Criado em:</span>
                      <span className="info-value">{formatDate(session.created_at)}</span>
                    </div>

                    {session.finished_at && (
                      <div className="session-info">
                        <span className="info-label">Finalizado em:</span>
                        <span className="info-value">{formatDate(session.finished_at)}</span>
                      </div>
                    )}

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

          {/* Modo: Lista de Versões */}
          {!loading && !error && viewMode === 'versions' && versions.length === 0 && (
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
            {!loading && viewMode === 'sessions' && sessions.length > 0 && (
              <span className="sessions-count">
                {sessions.length} documento(s) encontrado(s)
              </span>
            )}
            {!loading && viewMode === 'versions' && versions.length > 0 && (
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
