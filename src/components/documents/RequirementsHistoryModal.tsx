import React, { useState, useEffect } from 'react';
import './RequirementsHistoryModal.css';
import { listSessions, SessionSummary } from '../../services/requirementsHistoryService';

interface RequirementsHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSession: (sessionId: string, sessionName: string) => void;
}

const RequirementsHistoryModal: React.FC<RequirementsHistoryModalProps> = ({
  isOpen,
  onClose,
  onSelectSession
}) => {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadSessions();
    }
  }, [isOpen]);

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

  const handleSessionClick = (session: SessionSummary) => {
    onSelectSession(session.id, session.session_name);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          <h2>📜 Histórico de Documentos</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner-large"></div>
              <p>Carregando histórico...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button className="btn-retry" onClick={loadSessions}>
                Tentar Novamente
              </button>
            </div>
          )}

          {!loading && !error && sessions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>Nenhum documento gerado ainda</p>
              <p className="empty-hint">
                Os documentos de requisitos gerados aparecerão aqui
              </p>
            </div>
          )}

          {!loading && !error && sessions.length > 0 && (
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
                    <span className="action-hint">Clique para visualizar →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {!loading && sessions.length > 0 && (
              <span className="sessions-count">
                {sessions.length} documento(s) encontrado(s)
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
