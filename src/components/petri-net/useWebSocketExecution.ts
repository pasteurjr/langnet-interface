/**
 * Hook que gerencia a conexão WebSocket com o servidor agêntico gerado
 * (websocket_server.py default :5002). Padrão de mensagens compatível com o
 * framework visualtasksexec/tropicalsales.
 *
 * Eventos client → server:
 *   { type: "execute_task", data: { task_name, input_data } }
 *   { type: "get_task_info" }
 *   { type: "ping" }
 *
 * Eventos server → client (capturados em events[]):
 *   connected, task_start, verbose, task_completed, task_result, error, task_info, pong
 */
import { useCallback, useEffect, useRef, useState } from 'react';

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export type StepType =
  | 'connected'
  | 'task_start'
  | 'verbose'
  | 'task_completed'
  | 'task_result'
  | 'error'
  | 'task_info'
  | 'tool_input'
  | 'tool_output'
  | 'crew_start'
  | 'agent_start'
  | 'log'
  | string;

export interface ExecutionEvent {
  id: string;
  type: StepType;
  timestamp: string;
  task_name?: string;
  agent_name?: string;
  tool_name?: string;
  step_description?: string;
  input_data?: any;
  output_data?: any;
  message?: string;
  raw: any;
}

export interface ExecutionStats {
  task_starts: number;
  task_completeds: number;
  errors: number;
  verboses: number;
  current_task?: string;
}

interface UseWSExecutionResult {
  status: ConnectionStatus;
  error: string | null;
  events: ExecutionEvent[];
  stats: ExecutionStats;
  availableTasks: string[];
  url: string;
  setUrl: (u: string) => void;
  connect: (url?: string) => void;
  disconnect: () => void;
  executeTask: (taskName: string, inputData?: any) => boolean;
  clearEvents: () => void;
}

let _eventCounter = 0;
const _eid = () => `evt-${Date.now()}-${++_eventCounter}`;

function categorize(payload: any): ExecutionEvent {
  // payload é o que vem no onmessage parseado como JSON
  const type = (payload?.type as string) || 'log';
  const ts = payload?.timestamp || new Date().toISOString();
  const data = payload?.data || {};

  // O backend tropical/framework às vezes manda "step_type" dentro de data — usar como tipo se presente
  const inner_step = (data?.step_type as string) || null;
  const effective_type = inner_step || type;

  return {
    id: _eid(),
    type: effective_type as StepType,
    timestamp: ts,
    task_name: data?.task_name,
    agent_name: data?.agent_name,
    tool_name: data?.tool_name,
    step_description: data?.step_description,
    input_data: data?.input_data ?? data?.input,
    output_data: data?.output_data ?? data?.output ?? data?.result,
    message: data?.message || data?.error,
    raw: payload,
  };
}

export function useWebSocketExecution(defaultUrl = 'ws://localhost:5002'): UseWSExecutionResult {
  const [url, setUrl] = useState(defaultUrl);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [availableTasks, setAvailableTasks] = useState<string[]>([]);
  const [stats, setStats] = useState<ExecutionStats>({
    task_starts: 0,
    task_completeds: 0,
    errors: 0,
    verboses: 0,
  });
  const wsRef = useRef<WebSocket | null>(null);

  const pushEvent = useCallback((e: ExecutionEvent) => {
    setEvents((prev) => [...prev, e]);
    setStats((s) => {
      const next = { ...s };
      if (e.type === 'task_start') {
        next.task_starts += 1;
        if (e.task_name) next.current_task = e.task_name;
      } else if (e.type === 'task_completed' || e.type === 'task_result') {
        next.task_completeds += 1;
      } else if (e.type === 'error') {
        next.errors += 1;
      } else if (e.type === 'verbose') {
        next.verboses += 1;
      }
      return next;
    });
    // Capturar lista de tasks anunciada pelo servidor
    if (e.type === 'connected' || e.type === 'task_info') {
      const list = e.raw?.data?.available_tasks || e.raw?.data?.tasks;
      if (Array.isArray(list)) setAvailableTasks(list);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      try { wsRef.current.close(); } catch {}
      wsRef.current = null;
    }
    setStatus('disconnected');
  }, []);

  const connect = useCallback((nextUrl?: string) => {
    const target = nextUrl || url;
    if (nextUrl && nextUrl !== url) setUrl(nextUrl);
    if (wsRef.current) {
      try { wsRef.current.close(); } catch {}
      wsRef.current = null;
    }
    setStatus('connecting');
    setError(null);
    try {
      const ws = new WebSocket(target);
      wsRef.current = ws;
      ws.onopen = () => {
        setStatus('connected');
        try { ws.send(JSON.stringify({ type: 'get_task_info' })); } catch {}
      };
      ws.onmessage = (e) => {
        try {
          const payload = JSON.parse(e.data);
          pushEvent(categorize(payload));
        } catch {
          pushEvent({
            id: _eid(),
            type: 'log',
            timestamp: new Date().toISOString(),
            message: String(e.data),
            raw: e.data,
          });
        }
      };
      ws.onerror = () => {
        setStatus('error');
        setError('Erro de conexão WebSocket');
      };
      ws.onclose = () => {
        if (wsRef.current === ws) {
          wsRef.current = null;
          setStatus((s) => (s === 'error' ? 'error' : 'disconnected'));
        }
      };
    } catch (err: any) {
      setStatus('error');
      setError(err?.message || String(err));
    }
  }, [url, pushEvent]);

  const executeTask = useCallback((taskName: string, inputData: any = {}) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      setError('WebSocket não conectado');
      return false;
    }
    try {
      ws.send(JSON.stringify({
        type: 'execute_task',
        data: { task_name: taskName, input_data: inputData },
      }));
      return true;
    } catch (err: any) {
      setError(err?.message || String(err));
      return false;
    }
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setStats({ task_starts: 0, task_completeds: 0, errors: 0, verboses: 0 });
  }, []);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => { if (wsRef.current) { try { wsRef.current.close(); } catch {} } };
  }, []);

  return {
    status,
    error,
    events,
    stats,
    availableTasks,
    url,
    setUrl,
    connect,
    disconnect,
    executeTask,
    clearEvents,
  };
}
