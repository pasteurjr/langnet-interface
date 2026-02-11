import React, { useState, useEffect } from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { toast } from 'react-toastify';
import './YamlSelectionModal.css';

interface YamlSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (
    specificationId: string,
    agentTaskSpecId: string,
    tasksYamlId: string
  ) => void;
}

interface Session {
  id: string;
  session_name: string;
  status: string;
  created_at: string;
}

type TabType = 'specification' | 'agentTask' | 'tasksYaml';

const YamlSelectionModal: React.FC<YamlSelectionModalProps> = ({
  isOpen,
  onClose,
  onSelect
}) => {
  const { projectContext } = useNavigation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('specification');

  // Listas de sessões
  const [specificationSessions, setSpecificationSessions] = useState<Session[]>([]);
  const [agentTaskSpecSessions, setAgentTaskSpecSessions] = useState<Session[]>([]);
  const [tasksYamlSessions, setTasksYamlSessions] = useState<Session[]>([]);

  // Seleções
  const [selectedSpecificationId, setSelectedSpecificationId] = useState<string>('');
  const [selectedAgentTaskSpecId, setSelectedAgentTaskSpecId] = useState<string>('');
  const [selectedTasksYamlId, setSelectedTasksYamlId] = useState<string>('');

  useEffect(() => {
    if (isOpen) {
      resetState();
      loadAllSessions();
    }
  }, [isOpen, projectContext.projectId]);

  const resetState = () => {
    setSelectedSpecificationId('');
    setSelectedAgentTaskSpecId('');
    setSelectedTasksYamlId('');
    setError(null);
  };

  const loadAllSessions = async () => {
    setLoading(true);
    setError(null);

    try {
      const projectId = projectContext.projectId || 'project1';
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

      // Buscar Specification sessions
      const specificationResponse = await fetch(`${API_BASE_URL}/specifications?project_id=${projectId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (specificationResponse.ok) {
        const specificationData = await specificationResponse.json();
        const completed = (specificationData.sessions || []).filter((s: Session) => s.status === 'completed');
        setSpecificationSessions(completed);
      }

      // Buscar Agent Task Spec sessions
      const agentTaskSpecResponse = await fetch(`${API_BASE_URL}/agent-task-spec/sessions?project_id=${projectId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (agentTaskSpecResponse.ok) {
        const agentTaskSpecData = await agentTaskSpecResponse.json();
        const completed = (agentTaskSpecData.sessions || []).filter((s: Session) => s.status === 'completed');
        setAgentTaskSpecSessions(completed);
      }

      // Buscar Tasks YAML sessions
      const tasksYamlResponse = await fetch(`${API_BASE_URL}/tasks-yaml?project_id=${projectId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (tasksYamlResponse.ok) {
        const tasksYamlData = await tasksYamlResponse.json();
        const completed = (tasksYamlData.sessions || []).filter((s: Session) => s.status === 'completed');
        setTasksYamlSessions(completed);
      }

    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Erro ao carregar sessões. Verifique se as sessões foram geradas.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    if (!selectedSpecificationId || !selectedAgentTaskSpecId || !selectedTasksYamlId) {
      toast.error('Selecione os 3 documentos obrigatórios antes de confirmar!');
      return;
    }

    onSelect(selectedSpecificationId, selectedAgentTaskSpecId, selectedTasksYamlId);
    onClose();
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

  const handleSelectSpecification = (id: string) => {
    setSelectedSpecificationId(id);
    // Auto-navegar para próxima aba não selecionada
    if (!selectedAgentTaskSpecId) {
      setActiveTab('agentTask');
    } else if (!selectedTasksYamlId) {
      setActiveTab('tasksYaml');
    }
  };

  const handleSelectAgentTaskSpec = (id: string) => {
    setSelectedAgentTaskSpecId(id);
    // Auto-navegar para próxima aba não selecionada
    if (!selectedTasksYamlId) {
      setActiveTab('tasksYaml');
    }
  };

  const handleSelectTasksYaml = (id: string) => {
    setSelectedTasksYamlId(id);
  };

  const renderSessionCard = (session: Session, isSelected: boolean, onSelect: () => void) => (
    <div
      className={`session-item ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      key={session.id}
    >
      <div className="session-header">
        <div className="session-title">
          <span className="session-icon">📄</span>
          <span className="session-name">{session.session_name}</span>
        </div>
        <span className="status-badge status-completed">✅ Concluído</span>
      </div>

      <div className="session-details">
        <div className="session-info">
          <span className="info-label">Criado em:</span>
          <span className="info-value">{formatDate(session.created_at)}</span>
        </div>
      </div>
    </div>
  );

  if (!isOpen) return null;

  const allSelected = selectedSpecificationId && selectedAgentTaskSpecId && selectedTasksYamlId;
  const selectionCount = [selectedSpecificationId, selectedAgentTaskSpecId, selectedTasksYamlId]
    .filter(Boolean).length;

  return (
    <div className="yaml-selection-modal-overlay" onClick={onClose}>
      <div className="yaml-selection-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="yaml-selection-modal-header">
          <h2>📋 Selecionar Specs & Docs</h2>
          <button className="yaml-selection-modal-close" onClick={onClose}>×</button>
        </div>

        {/* Abas de Navegação */}
        <div className="yaml-selection-tabs">
          <button
            className={`tab-button ${activeTab === 'specification' ? 'active' : ''}`}
            onClick={() => setActiveTab('specification')}
          >
            📋 Especificação Funcional
          </button>
          <button
            className={`tab-button ${activeTab === 'agentTask' ? 'active' : ''}`}
            onClick={() => setActiveTab('agentTask')}
          >
            🤖 Especificação de Agentes/Tarefas
          </button>
          <button
            className={`tab-button ${activeTab === 'tasksYaml' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasksYaml')}
          >
            📋 Tasks YAML
          </button>
        </div>

        <div className="yaml-selection-modal-body">
          {loading && <div className="yaml-selection-loading">⏳ Carregando sessões...</div>}
          {error && <div className="yaml-selection-error">❌ {error}</div>}

          {!loading && !error && (
            <>
              {/* Aba 1: Especificação Funcional */}
              {activeTab === 'specification' && (
                <div className="sessions-list">
                  {specificationSessions.length === 0 ? (
                    <p className="yaml-selection-empty">
                      Nenhuma especificação funcional concluída.
                      Gere uma na página "Especificação".
                    </p>
                  ) : (
                    specificationSessions.map(session =>
                      renderSessionCard(
                        session,
                        selectedSpecificationId === session.id,
                        () => handleSelectSpecification(session.id)
                      )
                    )
                  )}
                </div>
              )}

              {/* Aba 2: Agent/Task Spec */}
              {activeTab === 'agentTask' && (
                <div className="sessions-list">
                  {agentTaskSpecSessions.length === 0 ? (
                    <p className="yaml-selection-empty">
                      Nenhuma especificação de agentes/tarefas concluída.
                      Gere uma na página "Especificação de Agentes e Tarefas".
                    </p>
                  ) : (
                    agentTaskSpecSessions.map(session =>
                      renderSessionCard(
                        session,
                        selectedAgentTaskSpecId === session.id,
                        () => handleSelectAgentTaskSpec(session.id)
                      )
                    )
                  )}
                </div>
              )}

              {/* Aba 3: Tasks YAML */}
              {activeTab === 'tasksYaml' && (
                <div className="sessions-list">
                  {tasksYamlSessions.length === 0 ? (
                    <p className="yaml-selection-empty">
                      Nenhum tasks.yaml concluído.
                      Gere um na página "Geração de YAML".
                    </p>
                  ) : (
                    tasksYamlSessions.map(session =>
                      renderSessionCard(
                        session,
                        selectedTasksYamlId === session.id,
                        () => handleSelectTasksYaml(session.id)
                      )
                    )
                  )}
                </div>
              )}
            </>
          )}
        </div>

        <div className="yaml-selection-modal-footer">
          <div className="selection-progress">
            <span className="progress-text">
              {selectionCount} de 3 selecionados
            </span>
          </div>

          <button
            className="yaml-selection-btn-cancel"
            onClick={onClose}
          >
            Cancelar
          </button>
          <button
            className="yaml-selection-btn-confirm"
            onClick={handleConfirm}
            disabled={!allSelected}
          >
            {allSelected ? '✓ Confirmar Seleção' : 'Selecione os 3 Documentos'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default YamlSelectionModal;
