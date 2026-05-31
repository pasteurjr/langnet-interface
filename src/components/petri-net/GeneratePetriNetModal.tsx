import React, { useEffect, useState } from 'react';

interface Session {
  id: string;
  session_name: string;
  status: string;
  created_at: string;
}

interface GeneratePetriNetModalProps {
  isOpen: boolean;
  projectId: string;
  onClose: () => void;
  onConfirm: (sel: {
    agentsYamlSessionId: string;
    tasksYamlSessionId: string;
    taskExecutionFlowSessionId?: string;
  }) => void;
}

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
};

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const overlayStyle: React.CSSProperties = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
};
const modalStyle: React.CSSProperties = {
  background: '#fff', borderRadius: 8, padding: 24,
  width: '90%', maxWidth: 600, maxHeight: '85vh', overflow: 'auto',
};
const labelStyle: React.CSSProperties = { display: 'block', marginTop: 16, fontWeight: 600 };
const selectStyle: React.CSSProperties = { width: '100%', padding: 8, marginTop: 4 };
const footerStyle: React.CSSProperties = {
  display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 20,
};

const formatDate = (s: string) => {
  try { return new Date(s).toLocaleString('pt-BR'); } catch { return s; }
};

const GeneratePetriNetModal: React.FC<GeneratePetriNetModalProps> = ({
  isOpen, projectId, onClose, onConfirm,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentsSessions, setAgentsSessions] = useState<Session[]>([]);
  const [tasksSessions, setTasksSessions] = useState<Session[]>([]);
  const [tefSessions, setTefSessions] = useState<Session[]>([]);
  const [selAgents, setSelAgents] = useState('');
  const [selTasks, setSelTasks] = useState('');
  const [selTef, setSelTef] = useState('');

  useEffect(() => {
    if (!isOpen || !projectId) return;
    setLoading(true);
    setError(null);
    setSelAgents(''); setSelTasks(''); setSelTef('');

    const headers = getAuthHeaders();
    const fetchSessions = (path: string) =>
      fetch(`${API_BASE}/${path}/?project_id=${projectId}`, { headers })
        .then(r => (r.ok ? r.json() : { sessions: [] }))
        .then(body => (body.sessions || []) as Session[])
        .catch(() => []);

    Promise.all([
      fetchSessions('agents-yaml'),
      fetchSessions('tasks-yaml'),
      fetchSessions('task-execution-flow'),
    ])
      .then(([a, t, tef]) => {
        setAgentsSessions(a.filter(s => s.status === 'completed'));
        setTasksSessions(t.filter(s => s.status === 'completed'));
        setTefSessions(tef.filter(s => s.status === 'completed'));
      })
      .catch(() => setError('Erro ao carregar sessões'))
      .finally(() => setLoading(false));
  }, [isOpen, projectId]);

  if (!isOpen) return null;

  const canConfirm = !!selAgents && !!selTasks;

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={{ marginTop: 0 }}>🔗 Gerar Rede de Petri</h2>
        <p style={{ color: '#555' }}>
          O agente <strong>petri_net_designer</strong> usará os artefatos abaixo para
          gerar a rede automaticamente. O resultado será salvo em
          <code> projects.project_data</code>.
        </p>

        {loading && <div>⏳ Carregando sessões…</div>}
        {error && <div style={{ color: '#c00' }}>❌ {error}</div>}

        {!loading && !error && (
          <>
            <label style={labelStyle}>
              agents.yaml (obrigatório)
              <select style={selectStyle} value={selAgents} onChange={(e) => setSelAgents(e.target.value)}>
                <option value="">— selecione —</option>
                {agentsSessions.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.session_name} ({formatDate(s.created_at)})
                  </option>
                ))}
              </select>
              {agentsSessions.length === 0 && (
                <small style={{ color: '#888' }}>Nenhuma sessão concluída encontrada.</small>
              )}
            </label>

            <label style={labelStyle}>
              tasks.yaml (obrigatório)
              <select style={selectStyle} value={selTasks} onChange={(e) => setSelTasks(e.target.value)}>
                <option value="">— selecione —</option>
                {tasksSessions.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.session_name} ({formatDate(s.created_at)})
                  </option>
                ))}
              </select>
              {tasksSessions.length === 0 && (
                <small style={{ color: '#888' }}>Nenhuma sessão concluída encontrada.</small>
              )}
            </label>

            <label style={labelStyle}>
              Sequência de Tasks (task_execution_flow) — opcional
              <select style={selectStyle} value={selTef} onChange={(e) => setSelTef(e.target.value)}>
                <option value="">— nenhum —</option>
                {tefSessions.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.session_name} ({formatDate(s.created_at)})
                  </option>
                ))}
              </select>
            </label>
          </>
        )}

        <div style={footerStyle}>
          <button onClick={onClose} style={{ padding: '8px 16px' }}>Cancelar</button>
          <button
            onClick={() => onConfirm({
              agentsYamlSessionId: selAgents,
              tasksYamlSessionId: selTasks,
              taskExecutionFlowSessionId: selTef || undefined,
            })}
            disabled={!canConfirm}
            style={{
              padding: '8px 16px',
              background: canConfirm ? '#1976d2' : '#aaa',
              color: '#fff', border: 'none', borderRadius: 4,
              cursor: canConfirm ? 'pointer' : 'not-allowed',
            }}
          >
            Gerar Rede
          </button>
        </div>
      </div>
    </div>
  );
};

export default GeneratePetriNetModal;
