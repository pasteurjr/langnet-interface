import React, { useEffect, useState } from 'react';

interface Session {
  id: string;
  session_name: string;
  status: string;
  created_at: string;
}

interface GenerateCodeModalProps {
  isOpen: boolean;
  projectId: string;
  onClose: () => void;
  onConfirm: (sel: {
    agentsYamlSessionId: string;
    tasksYamlSessionId: string;
    taskExecutionFlowSessionId?: string;
    agentTaskSpecSessionId?: string;
    websocketPort: number;
  }) => void;
}

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
};

const overlay: React.CSSProperties = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
};
const modal: React.CSSProperties = {
  background: '#fff', borderRadius: 8, padding: 24,
  width: '90%', maxWidth: 600, maxHeight: '85vh', overflow: 'auto',
};
const labelStyle: React.CSSProperties = { display: 'block', marginTop: 16, fontWeight: 600 };
const selectStyle: React.CSSProperties = { width: '100%', padding: 8, marginTop: 4 };

const fmt = (s: string) => { try { return new Date(s).toLocaleString('pt-BR'); } catch { return s; } };

const GenerateCodeModal: React.FC<GenerateCodeModalProps> = ({
  isOpen, projectId, onClose, onConfirm,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentsSessions, setAgentsSessions] = useState<Session[]>([]);
  const [tasksSessions, setTasksSessions] = useState<Session[]>([]);
  const [tefSessions, setTefSessions] = useState<Session[]>([]);
  const [atsSessions, setAtsSessions] = useState<Session[]>([]);
  const [selAgents, setSelAgents] = useState('');
  const [selTasks, setSelTasks] = useState('');
  const [selTef, setSelTef] = useState('');
  const [selAts, setSelAts] = useState('');
  const [wsPort, setWsPort] = useState(5002);

  useEffect(() => {
    if (!isOpen || !projectId) return;
    setLoading(true); setError(null);
    setSelAgents(''); setSelTasks(''); setSelTef(''); setSelAts('');

    const headers = getAuthHeaders();
    const fetchSessions = (path: string) =>
      fetch(`${API_BASE}/${path}/?project_id=${projectId}`, { headers })
        .then(r => (r.ok ? r.json() : { sessions: [] }))
        .then(body => (body.sessions || []) as any[])
        .then(list => list.map((s: any) => ({ ...s, id: s.id || s.session_id })))
        .catch(() => []);

    Promise.all([
      fetchSessions('agents-yaml'),
      fetchSessions('tasks-yaml'),
      fetchSessions('task-execution-flow'),
      fetch(`${API_BASE}/agent-task-spec/sessions?project_id=${projectId}`, { headers })
        .then(r => (r.ok ? r.json() : { sessions: [] }))
        .then(body => (body.sessions || []) as any[])
        .then(list => list.map((s: any) => ({ ...s, id: s.id || s.session_id })))
        .catch(() => []),
    ])
      .then(([a, t, tef, ats]) => {
        setAgentsSessions(a.filter(s => s.status === 'completed'));
        setTasksSessions(t.filter(s => s.status === 'completed'));
        setTefSessions(tef.filter(s => s.status === 'completed'));
        setAtsSessions(ats.filter(s => s.status === 'completed'));
      })
      .catch(() => setError('Erro ao carregar sessões'))
      .finally(() => setLoading(false));
  }, [isOpen, projectId]);

  if (!isOpen) return null;
  const canConfirm = !!selAgents && !!selTasks;

  return (
    <div style={overlay} onClick={onClose}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>
        <h2 style={{ marginTop: 0 }}>💻 Gerar Código Python</h2>
        <p style={{ color: '#555' }}>
          Gera o projeto Python completo (CrewAI + WebSocket + Petri Net) a partir
          dos artefatos prévios. A Rede de Petri em <code>projects.project_data</code>
          é embarcada com <code>place.logica</code> apontando para o WebSocket configurado.
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
                  <option key={s.id} value={s.id}>{s.session_name} ({fmt(s.created_at)})</option>
                ))}
              </select>
              {agentsSessions.length === 0 && <small style={{ color: '#888' }}>Nenhuma sessão concluída.</small>}
            </label>

            <label style={labelStyle}>
              tasks.yaml (obrigatório)
              <select style={selectStyle} value={selTasks} onChange={(e) => setSelTasks(e.target.value)}>
                <option value="">— selecione —</option>
                {tasksSessions.map(s => (
                  <option key={s.id} value={s.id}>{s.session_name} ({fmt(s.created_at)})</option>
                ))}
              </select>
              {tasksSessions.length === 0 && <small style={{ color: '#888' }}>Nenhuma sessão concluída.</small>}
            </label>

            <label style={labelStyle}>
              Sequência de Tasks (opcional)
              <select style={selectStyle} value={selTef} onChange={(e) => setSelTef(e.target.value)}>
                <option value="">— nenhum —</option>
                {tefSessions.map(s => (
                  <option key={s.id} value={s.id}>{s.session_name} ({fmt(s.created_at)})</option>
                ))}
              </select>
            </label>

            <label style={labelStyle}>
              Especificação de Agentes & Tarefas (recomendado — extrai tools)
              <select style={selectStyle} value={selAts} onChange={(e) => setSelAts(e.target.value)}>
                <option value="">— nenhum —</option>
                {atsSessions.map(s => (
                  <option key={s.id} value={s.id}>{s.session_name} ({fmt(s.created_at)})</option>
                ))}
              </select>
              <small style={{ color: '#888' }}>
                Sem isso, <code>websocket_server.py</code> não amarra tools às tasks (Agent/Task ficam <code>tools=[]</code>).
              </small>
            </label>

            <label style={labelStyle}>
              Porta do WebSocket (servidor do sistema gerado)
              <input
                type="number"
                style={selectStyle}
                value={wsPort}
                min={1024}
                max={65535}
                onChange={(e) => setWsPort(parseInt(e.target.value, 10) || 5002)}
              />
              <small style={{ color: '#888' }}>
                Será gravada no <code>.env.example</code> e nas chamadas <code>new WebSocket()</code> dentro de <code>place.logica</code>.
              </small>
            </label>
          </>
        )}

        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 20 }}>
          <button onClick={onClose} style={{ padding: '8px 16px' }}>Cancelar</button>
          <button
            onClick={() => onConfirm({
              agentsYamlSessionId: selAgents,
              tasksYamlSessionId: selTasks,
              taskExecutionFlowSessionId: selTef || undefined,
              agentTaskSpecSessionId: selAts || undefined,
              websocketPort: wsPort,
            })}
            disabled={!canConfirm}
            style={{
              padding: '8px 16px',
              background: canConfirm ? '#1976d2' : '#aaa',
              color: '#fff', border: 'none', borderRadius: 4,
              cursor: canConfirm ? 'pointer' : 'not-allowed',
            }}
          >
            Gerar Código
          </button>
        </div>
      </div>
    </div>
  );
};

export default GenerateCodeModal;
