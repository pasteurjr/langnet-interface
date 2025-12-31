import React, { useState, useEffect } from 'react';
import '../documents/RequirementsHistoryModal.css'; // Reusa CSS do RequirementsHistoryModal

interface TasksYamlSession {
  id: string;
  session_name: string;
  project_id: string;
  status: string;
  spec_session_id: string;
  spec_version: number;
  started_at: string;
  finished_at?: string;
  total_tasks?: number;
}

interface TasksYamlVersion {
  version: number;
  created_at: string;
  change_description: string;
  change_type: 'initial_generation' | 'ai_refinement' | 'manual_edit';
  yaml_size: number;
}

interface TasksYamlHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId?: string;
  onSelectSession?: (sessionId: string, sessionName: string) => void;
  onSelectVersion?: (sessionId: string, version: number) => void;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

const TasksYamlHistoryModal: React.FC<TasksYamlHistoryModalProps> = ({
  isOpen,
  onClose,
  projectId,
  onSelectSession,
  onSelectVersion
}) => {
  const [sessions, setSessions] = useState<TasksYamlSession[]>([]);
  const [versions, setVersions] = useState<TasksYamlVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'sessions' | 'versions'>('sessions');
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [selectedSessionName, setSelectedSessionName] = useState<string>('');
  const [canGoBack, setCanGoBack] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setViewMode('sessions');
      setCanGoBack(false);
      loadSessions();
    }
  }, [isOpen, projectId]);

  const loadSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `${API_BASE_URL}/tasks-yaml?limit=50&offset=0`;
      if (projectId) {
        url += `&project_id=${projectId}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Failed to load agents YAML sessions');
      }

      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error('Error loading agents YAML sessions:', err);
      setError('Erro ao carregar histórico de tasks.yaml');
    } finally {
      setLoading(false);
    }
  };

  const loadVersions = async (sessId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/tasks-yaml/${sessId}/versions`, {
        method: 'GET',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        throw new Error('Failed to load agents YAML versions');
      }

      const data = await response.json();
      setVersions(data.versions || []);
    } catch (err) {
      console.error('Error loading agents YAML versions:', err);
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
      'initial_generation': '🚀',
      'ai_refinement': '✨',
      'manual_edit': '📝'
    };
    return icons[type] || '📄';
  };

  const getTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'initial_generation': 'Geração Inicial',
      'ai_refinement': 'Refinamento IA',
      'manual_edit': 'Edição Manual'
    };
    return labels[type] || type;
  };

  const getTypeBadge = (type: string) => {
    const typeColors: { [key: string]: string } = {
      'initial_generation': 'type-analysis',
      'ai_refinement': 'type-refinement',
      'manual_edit': 'type-manual'
    };
    return typeColors[type] || 'type-manual';
  };

  const getStatusBadge = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'completed': 'status-completed',
      'generating': 'status-running',
      'processing': 'status-running',
      'failed': 'status-failed',
      'pending': 'status-pending'
    };
    return statusColors[status] || 'status-pending';
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      'completed': 'Concluído',
      'generating': 'Gerando...',
      'processing': 'Processando...',
      'failed': 'Falhou',
      'pending': 'Pendente'
    };
    return labels[status] || status;
  };

  const handleSessionClick = (session: TasksYamlSession) => {
    setSelectedSessionId(session.id);
    setSelectedSessionName(session.session_name);
    setViewMode('versions');
    setCanGoBack(true);
    loadVersions(session.id);
  };

  const handleVersionClick = (version: number) => {
    if (onSelectVersion && selectedSessionId) {
      onSelectVersion(selectedSessionId, version);
    }
    if (onSelectSession && selectedSessionId) {
      onSelectSession(selectedSessionId, selectedSessionName);
    }
    onClose();
  };

  const handleBackToSessions = () => {
    setViewMode('sessions');
    setVersions([]);
    setCanGoBack(false);
    loadSessions();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          <h2>{viewMode === 'sessions' ? '📜 Histórico de tasks.yaml' : '📜 Histórico de Versões'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {/* Botão Voltar */}
        {viewMode === 'versions' && canGoBack && (
          <div style={{
            padding: '10px 20px',
            borderBottom: '1px solid #eee',
            backgroundColor: '#f8f9fa'
          }}>
            <button
              onClick={handleBackToSessions}
              style={{
                padding: '8px 16px',
                fontSize: '14px',
                fontWeight: 'bold',
                cursor: 'pointer',
                border: '1px solid #007bff',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#007bff'
              }}
            >
              ← Voltar para Lista de tasks.yaml
            </button>
          </div>
        )}

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner-large"></div>
              <p>{viewMode === 'sessions' ? 'Carregando tasks.yaml...' : 'Carregando versões...'}</p>
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

          {/* Lista de Sessões */}
          {!loading && !error && viewMode === 'sessions' && sessions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <p>Nenhum tasks.yaml gerado ainda</p>
              <p className="empty-hint">
                Os arquivos tasks.yaml gerados aparecerão aqui
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
                      <span className="session-icon">📋</span>
                      <span className="session-name">{session.session_name}</span>
                    </div>
                    <span className={`status-badge ${getStatusBadge(session.status)}`}>
                      {getStatusLabel(session.status)}
                    </span>
                  </div>

                  <div className="session-details">
                    <div className="session-info">
                      <span className="info-label">Criado em:</span>
                      <span className="info-value">{formatDate(session.started_at)}</span>
                    </div>

                    {session.finished_at && (
                      <div className="session-info">
                        <span className="info-label">Finalizado em:</span>
                        <span className="info-value">{formatDate(session.finished_at)}</span>
                      </div>
                    )}

                    <div className="session-info">
                      <span className="info-label">Baseado em:</span>
                      <span className="info-value">Espec Tarefas/Tarefas v{session.spec_version}</span>
                    </div>

                    {session.total_tasks !== undefined && (
                      <div className="session-info">
                        <span className="info-label">Tarefas:</span>
                        <span className="info-value">{session.total_tasks}</span>
                      </div>
                    )}
                  </div>

                  <div className="session-action">
                    <span className="action-hint">Clique para ver versões →</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Lista de Versões */}
          {!loading && !error && viewMode === 'versions' && versions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>Nenhuma versão encontrada</p>
              <p className="empty-hint">
                As versões do tasks.yaml aparecerão aqui
              </p>
            </div>
          )}

          {!loading && !error && viewMode === 'versions' && versions.length > 0 && (
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
                      <span className="info-value">{formatFileSize(version.yaml_size)}</span>
                    </div>
                  </div>

                  <div className="session-action">
                    <span className="action-hint">Clique para carregar →</span>
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
                {sessions.length} tasks.yaml encontrado(s)
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

export default TasksYamlHistoryModal;
