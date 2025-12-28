import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import '../documents/RequirementsHistoryModal.css'; // Reusa CSS

interface AgentTaskSpecSession {
  session_id: string;
  session_name: string;
  total_agents: number;
  total_tasks: number;
  status: string;
  created_at: string;
}

interface AgentTaskSpecVersion {
  version: number;
  created_at: string;
  change_description: string | null;
  change_type: 'initial_generation' | 'ai_refinement' | 'manual_edit' | 'approval_revision' | 'feedback_incorporation';
  doc_size: number;
}

interface AgentTaskSpecHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onSelectSession: (sessionId: string, sessionName: string) => void;
  onSelectVersion?: (sessionId: string, version: number) => void; // CORRIGIDO: recebe sessionId também
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = (): HeadersInit => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

const AgentTaskSpecHistoryModal: React.FC<AgentTaskSpecHistoryModalProps> = ({
  isOpen,
  onClose,
  projectId,
  onSelectSession,
  onSelectVersion
}) => {
  // Estados de sessões
  const [sessions, setSessions] = useState<AgentTaskSpecSession[]>([]);
  const [loading, setLoading] = useState(false);

  // Estados de versões (2-step flow)
  const [viewMode, setViewMode] = useState<'sessions' | 'versions'>('sessions');
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [selectedSessionName, setSelectedSessionName] = useState<string>('');
  const [versions, setVersions] = useState<AgentTaskSpecVersion[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);

  useEffect(() => {
    if (isOpen && projectId) {
      loadSessions();
      // Reset para view de sessões ao abrir
      setViewMode('sessions');
      setSelectedSessionId('');
      setVersions([]);
    }
  }, [isOpen, projectId]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/agent-task-spec/sessions?project_id=${projectId}`,
        { headers: getAuthHeaders() }
      );

      if (!response.ok) {
        throw new Error('Falha ao carregar sessões');
      }

      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error: any) {
      console.error('Erro ao carregar sessões:', error);
      toast.error('Erro ao carregar documentos de especificação');
    } finally {
      setLoading(false);
    }
  };

  const loadVersions = async (sessionId: string, sessionName: string) => {
    setLoadingVersions(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/agent-task-spec/${sessionId}/versions`,
        { headers: getAuthHeaders() }
      );

      if (!response.ok) {
        throw new Error('Falha ao carregar versões');
      }

      const data = await response.json();
      setVersions(data || []);
      setSelectedSessionId(sessionId);
      setSelectedSessionName(sessionName);
      setViewMode('versions'); // Muda para view de versões
    } catch (error: any) {
      console.error('Erro ao carregar versões:', error);
      toast.error('Erro ao carregar versões do documento');
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleSessionClick = (session: AgentTaskSpecSession) => {
    if (onSelectVersion) {
      // Se tem callback de versão, entra no 2-step flow
      loadVersions(session.session_id, session.session_name);
    } else {
      // Senão, comportamento original (seleciona sessão e fecha)
      onSelectSession(session.session_id, session.session_name);
      onClose();
    }
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
    setSelectedSessionId('');
    setVersions([]);
  };

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getChangeTypeLabel = (changeType: string): string => {
    const labels: Record<string, string> = {
      'initial_generation': '📝 Geração Inicial',
      'ai_refinement': '🤖 Refinamento IA',
      'manual_edit': '✏️ Edição Manual',
      'approval_revision': '✅ Revisão de Aprovação',
      'feedback_incorporation': '💬 Feedback Incorporado'
    };
    return labels[changeType] || changeType;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          {viewMode === 'sessions' ? (
            <h2>📋 Documentos de Especificação de Agentes/Tarefas</h2>
          ) : (
            <>
              <button
                className="back-button"
                onClick={handleBackToSessions}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '20px',
                  marginRight: '12px'
                }}
              >
                ←
              </button>
              <h2>📜 Versões: {selectedSessionName}</h2>
            </>
          )}
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {viewMode === 'sessions' ? (
            // VIEW 1: SESSÕES
            loading ? (
              <div className="loading-state">
                <p>Carregando...</p>
              </div>
            ) : sessions.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📋</div>
                <p>Nenhum documento de especificação criado ainda</p>
                <p className="empty-hint">
                  Crie um documento de especificação na página "Agentes & Tarefas" primeiro
                </p>
              </div>
            ) : (
              <div className="sessions-list">
                {sessions.map(session => (
                  <div
                    key={session.session_id}
                    className="session-card"
                    onClick={() => handleSessionClick(session)}
                    style={{
                      cursor: 'pointer',
                      padding: '16px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      marginBottom: '12px',
                      backgroundColor: '#fff',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#3b82f6';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(59, 130, 246, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 600 }}>
                      {session.session_name}
                    </h4>
                    <p style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#666' }}>
                      📊 {session.total_agents} agentes, {session.total_tasks} tarefas
                    </p>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: '#999' }}>
                      <span>
                        {session.status === 'completed' ? '✅' : '⏳'} {session.status}
                      </span>
                      <span>📅 {new Date(session.created_at).toLocaleString()}</span>
                    </div>
                    {onSelectVersion && (
                      <div style={{ marginTop: '8px', fontSize: '11px', color: '#3b82f6' }}>
                        → Clique para ver versões
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )
          ) : (
            // VIEW 2: VERSÕES
            loadingVersions ? (
              <div className="loading-state">
                <p>Carregando versões...</p>
              </div>
            ) : versions.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📜</div>
                <p>Nenhuma versão encontrada</p>
              </div>
            ) : (
              <div className="versions-list">
                {versions.map(version => (
                  <div
                    key={version.version}
                    className="version-card"
                    onClick={() => handleVersionClick(version.version)}
                    style={{
                      cursor: 'pointer',
                      padding: '16px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      marginBottom: '12px',
                      backgroundColor: '#fff',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#3b82f6';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(59, 130, 246, 0.1)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                      <h4 style={{ margin: '0', fontSize: '14px', fontWeight: 600 }}>
                        Versão {version.version}
                      </h4>
                      <span style={{
                        fontSize: '11px',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        backgroundColor: '#eff6ff',
                        color: '#3b82f6'
                      }}>
                        {getChangeTypeLabel(version.change_type)}
                      </span>
                    </div>

                    {version.change_description && (
                      <div style={{
                        margin: '0 0 8px 0',
                        padding: '8px',
                        backgroundColor: '#f9fafb',
                        borderRadius: '4px',
                        borderLeft: '3px solid #3b82f6'
                      }}>
                        <div style={{ fontSize: '10px', fontWeight: 600, color: '#666', marginBottom: '4px' }}>
                          💬 Prompt/Descrição:
                        </div>
                        <div style={{ fontSize: '12px', color: '#374151', fontStyle: 'italic' }}>
                          "{version.change_description.length > 150
                            ? version.change_description.substring(0, 150) + '...'
                            : version.change_description
                          }"
                        </div>
                      </div>
                    )}

                    <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: '#999' }}>
                      <span>📅 {new Date(version.created_at).toLocaleString()}</span>
                      <span>📦 {formatBytes(version.doc_size)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-close" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentTaskSpecHistoryModal;
