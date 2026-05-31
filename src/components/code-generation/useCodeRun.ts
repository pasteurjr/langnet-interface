import { useCallback, useEffect, useRef, useState } from 'react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const WS_BASE = API_BASE.replace(/^http/, 'ws');

export type RunStatus = 'preparing' | 'installing' | 'running' | 'stopped' | 'crashed';

export interface RunState {
  run_id: string;
  session_id: string;
  status: RunStatus;
  started_at?: string;
  finished_at?: string;
  exit_code?: number | null;
  work_dir?: string;
  total_lines?: number;
}

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
};

interface UseCodeRunResult {
  run: RunState | null;
  lines: string[];
  isStarting: boolean;
  error: string | null;
  start: () => Promise<void>;
  stop: () => Promise<void>;
  clear: () => void;
}

export function useCodeRun(sessionId: string | undefined): UseCodeRunResult {
  const [run, setRun] = useState<RunState | null>(null);
  const [lines, setLines] = useState<string[]>([]);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const teardownWs = useCallback(() => {
    if (wsRef.current) {
      try { wsRef.current.close(); } catch {}
      wsRef.current = null;
    }
  }, []);

  const attachWs = useCallback((runId: string) => {
    teardownWs();
    const token = localStorage.getItem('accessToken') || localStorage.getItem('token') || '';
    const url = `${WS_BASE}/code-generation/run/${runId}/ws?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (payload.type === 'line') {
          setLines((prev) => [...prev, payload.data]);
        } else if (payload.type === 'status') {
          setRun(payload.data as RunState);
        }
      } catch {
        setLines((prev) => [...prev, String(e.data)]);
      }
    };
    ws.onerror = () => setError('Erro na conexão WebSocket');
    ws.onclose = () => { if (wsRef.current === ws) wsRef.current = null; };
  }, [teardownWs]);

  const start = useCallback(async () => {
    if (!sessionId) return;
    setIsStarting(true);
    setError(null);
    setLines([]);
    try {
      const res = await fetch(`${API_BASE}/code-generation/${sessionId}/run`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: RunState = await res.json();
      setRun(data);
      attachWs(data.run_id);
    } catch (err: any) {
      setError(err?.message || String(err));
    } finally {
      setIsStarting(false);
    }
  }, [sessionId, attachWs]);

  const stop = useCallback(async () => {
    if (!run?.run_id) return;
    try {
      const res = await fetch(`${API_BASE}/code-generation/run/${run.run_id}/stop`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: RunState = await res.json();
      setRun(data);
    } catch (err: any) {
      setError(err?.message || String(err));
    }
  }, [run?.run_id]);

  const clear = useCallback(() => {
    teardownWs();
    setRun(null);
    setLines([]);
    setError(null);
  }, [teardownWs]);

  // Cleanup on unmount
  useEffect(() => () => teardownWs(), [teardownWs]);

  // Clear quando muda de sessão
  useEffect(() => { clear(); }, [sessionId, clear]);

  return { run, lines, isStarting, error, start, stop, clear };
}
