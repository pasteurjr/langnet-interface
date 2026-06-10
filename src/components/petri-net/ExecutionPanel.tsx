/**
 * Painel de execução real conectando ao framework agêntico gerado (websocket_server.py).
 * 5 abas no padrão TropicalSales: Operação · Execução · Inputs · Outputs · Logs.
 */
import React, { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState } from 'react';
import {
  ConnectionStatus,
  ExecutionEvent,
  useWebSocketExecution,
} from './useWebSocketExecution';

export interface ExecutionPanelHandle {
  /** Conecta (se ainda não estiver) e dispara execute_task. Retorna true se enviou. */
  triggerTask: (taskName: string, inputData?: any) => Promise<boolean>;
  open: () => void;
}

type TabId = 'operacao' | 'execucao' | 'inputs' | 'outputs' | 'logs';

interface ExecutionPanelProps {
  isOpen: boolean;
  defaultUrl?: string;
  /** Se definido, conecta automaticamente ao abrir (uso típico: chegou via
   *  /project/X/petri-net?autoconnect=ws://localhost:5002 depois de Executar). */
  autoconnectUrl?: string;
  onClose: () => void;
  onRequestOpen?: () => void;
}

const panelStyle: React.CSSProperties = {
  position: 'fixed', right: 0, top: 0, bottom: 0, width: 520,
  background: '#fff', borderLeft: '1px solid #ccc', zIndex: 900,
  display: 'flex', flexDirection: 'column', boxShadow: '-4px 0 12px rgba(0,0,0,0.08)',
};
const headerStyle: React.CSSProperties = {
  padding: 12, borderBottom: '1px solid #e0e0e0', background: '#fafafa',
};
const rowStyle: React.CSSProperties = { display: 'flex', gap: 6, alignItems: 'center', marginTop: 6 };
const inputStyle: React.CSSProperties = { flex: 1, padding: 6, border: '1px solid #ccc', borderRadius: 4, fontSize: 12 };
const tabsStyle: React.CSSProperties = { display: 'flex', borderBottom: '1px solid #e0e0e0' };
const tabBtn = (active: boolean): React.CSSProperties => ({
  flex: 1, padding: '8px 10px', cursor: 'pointer', border: 'none',
  background: active ? '#1976d2' : 'transparent', color: active ? '#fff' : '#333',
  fontSize: 12, fontWeight: active ? 700 : 500,
});
const btn = (color = '#1976d2'): React.CSSProperties => ({
  padding: '6px 12px', background: color, color: '#fff', border: 'none',
  borderRadius: 4, cursor: 'pointer', fontSize: 12,
});

const statusBadge = (s: ConnectionStatus): React.CSSProperties => ({
  display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: 11, fontWeight: 700,
  color: '#fff', marginLeft: 6,
  background: s === 'connected' ? '#2e7d32' : s === 'connecting' ? '#f57c00' : s === 'error' ? '#c62828' : '#666',
});

const statusLabel: Record<ConnectionStatus, string> = {
  connected: 'CONECTADO',
  connecting: 'CONECTANDO...',
  disconnected: 'DESCONECTADO',
  error: 'ERRO',
};

const STEP_GROUPS = {
  inputs: ['tool_input', 'task_start'],
  outputs: ['tool_output', 'task_completed', 'task_result'],
  execucao: ['task_start', 'crew_start', 'agent_start', 'tool_executing', 'verbose'],
  logs: ['log', 'error', 'connected', 'task_info'],
} as const;

function eventMatchesTab(e: ExecutionEvent, tab: TabId): boolean {
  if (tab === 'operacao') return true; // Operação consolidada (todas mas exibe só task atual)
  const list = (STEP_GROUPS as any)[tab] as string[];
  return list.includes(e.type);
}

function truncate(s: any, max = 600): string {
  const str = typeof s === 'string' ? s : JSON.stringify(s, null, 2);
  if (str === undefined || str === null) return '';
  return str.length > max ? str.slice(0, max) + ` ... [+${str.length - max} chars]` : str;
}

interface EventRowProps { e: ExecutionEvent; }
const EventRow: React.FC<EventRowProps> = ({ e }) => {
  const bg =
    e.type === 'error' ? '#ffebee' :
    e.type === 'task_completed' || e.type === 'task_result' ? '#e8f5e9' :
    e.type === 'task_start' ? '#fff8e1' :
    '#fafafa';
  return (
    <div style={{ background: bg, padding: 8, marginBottom: 6, borderRadius: 4, fontSize: 12, border: '1px solid #e0e0e0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <strong>{e.type}</strong>
        <span style={{ color: '#888', fontSize: 10 }}>{new Date(e.timestamp).toLocaleTimeString('pt-BR')}</span>
      </div>
      {e.task_name && <div style={{ fontSize: 11, color: '#1976d2' }}>task: <strong>{e.task_name}</strong></div>}
      {e.agent_name && <div style={{ fontSize: 11, color: '#555' }}>agent: {e.agent_name}</div>}
      {e.tool_name && <div style={{ fontSize: 11, color: '#555' }}>tool: {e.tool_name}</div>}
      {e.message && <div style={{ marginTop: 4, whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 11 }}>{truncate(e.message)}</div>}
      {e.input_data !== undefined && (
        <details style={{ marginTop: 4 }}>
          <summary style={{ cursor: 'pointer', fontSize: 11, color: '#666' }}>input</summary>
          <pre style={{ margin: '4px 0', fontSize: 10, whiteSpace: 'pre-wrap' }}>{truncate(e.input_data, 1500)}</pre>
        </details>
      )}
      {e.output_data !== undefined && (
        <details style={{ marginTop: 4 }} open={e.type === 'task_completed'}>
          <summary style={{ cursor: 'pointer', fontSize: 11, color: '#666' }}>output</summary>
          <pre style={{ margin: '4px 0', fontSize: 10, whiteSpace: 'pre-wrap' }}>{truncate(e.output_data, 1500)}</pre>
        </details>
      )}
    </div>
  );
};

const ExecutionPanel = forwardRef<ExecutionPanelHandle, ExecutionPanelProps>(({ isOpen, defaultUrl, autoconnectUrl, onClose, onRequestOpen }, ref) => {
  const ws = useWebSocketExecution(autoconnectUrl || defaultUrl);
  const [activeTab, setActiveTab] = useState<TabId>('execucao');
  const [taskName, setTaskName] = useState('');
  const [inputJson, setInputJson] = useState('{}');
  const [parseErr, setParseErr] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const autoConnectedRef = useRef(false);

  // Autoconnect quando isOpen + autoconnectUrl, uma única vez
  useEffect(() => {
    if (isOpen && autoconnectUrl && !autoConnectedRef.current && ws.status === 'disconnected') {
      autoConnectedRef.current = true;
      ws.connect(autoconnectUrl);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, autoconnectUrl]);

  // Expõe API imperativa para PetriNetEditor.jsx disparar tasks pelo canvas
  useImperativeHandle(ref, () => ({
    triggerTask: async (name: string, inputData: any = {}) => {
      onRequestOpen?.();
      // Conecta se ainda não está conectado e aguarda brevemente
      const needsConnect = ws.status !== 'connected';
      if (needsConnect) {
        ws.connect();
      }
      // Espera defensiva — o status muda assincronamente.
      await new Promise(r => setTimeout(r, needsConnect ? 1500 : 300));
      const ok = ws.executeTask(name, inputData);
      if (ok) {
        setTaskName(name);
        setInputJson(JSON.stringify(inputData, null, 2));
        setActiveTab('execucao');
      }
      return ok;
    },
    open: () => { onRequestOpen?.(); },
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [ws.status, ws.executeTask, onRequestOpen]);

  // Auto-scroll
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [ws.events, activeTab]);

  // Atualiza taskName default quando lista chega
  useEffect(() => {
    if (!taskName && ws.availableTasks.length > 0) setTaskName(ws.availableTasks[0]);
  }, [ws.availableTasks, taskName]);

  const visibleEvents = useMemo(() => ws.events.filter((e) => eventMatchesTab(e, activeTab)), [ws.events, activeTab]);

  // Aba Operação: filtra eventos da task atual + organiza em 3 colunas (Inputs / Steps / Outputs)
  const currentTaskEvents = useMemo(() => {
    if (!ws.stats.current_task) return [];
    return ws.events.filter((e) => e.task_name === ws.stats.current_task);
  }, [ws.events, ws.stats.current_task]);

  const handleExecute = () => {
    setParseErr(null);
    let parsed: any = {};
    try { parsed = inputJson.trim() ? JSON.parse(inputJson) : {}; }
    catch (err: any) { setParseErr(`JSON inválido: ${err.message}`); return; }
    if (!taskName.trim()) { setParseErr('Selecione um task_name'); return; }
    ws.executeTask(taskName.trim(), parsed);
  };

  if (!isOpen) return null;

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong>▶ Execução Real</strong>
            <span style={statusBadge(ws.status)}>{statusLabel[ws.status]}</span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer' }}>×</button>
        </div>

        <div style={rowStyle}>
          <input
            style={inputStyle}
            placeholder="ws://localhost:5002"
            value={ws.url}
            onChange={(e) => ws.setUrl(e.target.value)}
            disabled={ws.status === 'connected' || ws.status === 'connecting'}
          />
          {ws.status === 'connected' ? (
            <button onClick={ws.disconnect} style={btn('#c62828')}>Desconectar</button>
          ) : (
            <button onClick={() => ws.connect()} style={btn('#2e7d32')} disabled={ws.status === 'connecting'}>
              {ws.status === 'connecting' ? '⏳' : 'Conectar'}
            </button>
          )}
        </div>

        {ws.error && <div style={{ color: '#c00', fontSize: 11, marginTop: 6 }}>⚠ {ws.error}</div>}

        <div style={{ ...rowStyle, marginTop: 10, alignItems: 'flex-start' }}>
          {ws.availableTasks.length > 0 ? (
            <select
              style={{ ...inputStyle, maxWidth: 180 }}
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
            >
              {ws.availableTasks.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          ) : (
            <input
              style={{ ...inputStyle, maxWidth: 180 }}
              placeholder="task_name"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
            />
          )}
          <textarea
            style={{ ...inputStyle, fontFamily: 'monospace', minHeight: 32, maxHeight: 80 }}
            placeholder='input_data JSON (ex: {"key":"value"})'
            value={inputJson}
            onChange={(e) => setInputJson(e.target.value)}
          />
          <button onClick={handleExecute} style={btn(ws.status === 'connected' ? '#1976d2' : '#888')} disabled={ws.status !== 'connected'}>
            ▶ Executar
          </button>
        </div>
        {parseErr && <div style={{ color: '#c00', fontSize: 11, marginTop: 4 }}>{parseErr}</div>}

        <div style={{ marginTop: 8, fontSize: 11, color: '#555' }}>
          ▸ task_start: {ws.stats.task_starts} · completed: {ws.stats.task_completeds} · errors: {ws.stats.errors} · verboses: {ws.stats.verboses}
          {ws.stats.current_task && <span> · atual: <strong>{ws.stats.current_task}</strong></span>}
          <button onClick={ws.clearEvents} style={{ ...btn('#666'), marginLeft: 8, padding: '2px 8px', fontSize: 10 }}>Limpar</button>
        </div>
      </div>

      <div style={tabsStyle}>
        {(['operacao', 'execucao', 'inputs', 'outputs', 'logs'] as TabId[]).map((tab) => (
          <button key={tab} style={tabBtn(activeTab === tab)} onClick={() => setActiveTab(tab)}>
            {tab === 'operacao' ? '⚙ Operação' :
             tab === 'execucao' ? '⚡ Execução' :
             tab === 'inputs' ? '📥 Inputs' :
             tab === 'outputs' ? '📤 Outputs' : '📝 Logs'}
            {tab === 'execucao' && ws.events.length > 0 && ` (${ws.events.length})`}
          </button>
        ))}
      </div>

      <div ref={listRef} style={{ flex: 1, overflowY: 'auto', padding: 10 }}>
        {activeTab === 'operacao' ? (
          ws.stats.current_task ? (
            <>
              <div style={{ fontSize: 12, color: '#1976d2', marginBottom: 8 }}>
                Task atual: <strong>{ws.stats.current_task}</strong>
              </div>
              {currentTaskEvents.length === 0 && <div style={{ color: '#888' }}>Sem eventos.</div>}
              {currentTaskEvents.map((e) => <EventRow key={e.id} e={e} />)}
            </>
          ) : (
            <div style={{ color: '#888', fontSize: 12 }}>Nenhuma task em execução. Acione um execute_task.</div>
          )
        ) : (
          <>
            {visibleEvents.length === 0 && (
              <div style={{ color: '#888', fontSize: 12 }}>
                {ws.status === 'connected' ? 'Aguardando eventos...' : 'Conecte ao servidor primeiro.'}
              </div>
            )}
            {visibleEvents.map((e) => <EventRow key={e.id} e={e} />)}
          </>
        )}
      </div>
    </div>
  );
});

ExecutionPanel.displayName = 'ExecutionPanel';

export default ExecutionPanel;
