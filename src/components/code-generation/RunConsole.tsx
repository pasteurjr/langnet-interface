import React, { useEffect, useRef } from 'react';
import { RunState, RunStatus } from './useCodeRun';

interface RunConsoleProps {
  visible: boolean;
  run: RunState | null;
  lines: string[];
  isStarting: boolean;
  error: string | null;
  onStop: () => void;
  onClose: () => void;
  onClear: () => void;
}

const statusColor = (s: RunStatus | undefined): string => {
  switch (s) {
    case 'running': return '#2e7d32';
    case 'installing': case 'preparing': return '#f57c00';
    case 'stopped': return '#666';
    case 'crashed': return '#c62828';
    default: return '#666';
  }
};

const statusLabel = (s: RunStatus | undefined): string => {
  if (!s) return 'DESCONHECIDO';
  return s.toUpperCase();
};

const wrap: React.CSSProperties = {
  position: 'fixed', bottom: 0, left: 0, right: 0, height: 320,
  borderTop: '1px solid #ccc', background: '#1e1e1e', color: '#eee',
  display: 'flex', flexDirection: 'column', minHeight: 0,
  zIndex: 950, boxShadow: '0 -4px 12px rgba(0,0,0,0.2)',
};
const header: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  padding: '6px 12px', background: '#252526', borderBottom: '1px solid #333',
};
const pill = (color: string): React.CSSProperties => ({
  display: 'inline-block', padding: '2px 8px', borderRadius: 10,
  background: color, color: '#fff', fontSize: 11, fontWeight: 700, marginLeft: 8,
});
const btn = (bg = '#444'): React.CSSProperties => ({
  padding: '4px 10px', background: bg, color: '#fff', border: 'none',
  borderRadius: 3, cursor: 'pointer', fontSize: 12, marginLeft: 6,
});
const term: React.CSSProperties = {
  flex: 1, overflowY: 'auto', padding: 10, fontFamily: 'monospace', fontSize: 12,
  whiteSpace: 'pre-wrap', wordBreak: 'break-all',
};

const colorize = (line: string): string => {
  if (line.startsWith('[runner]')) return '#7ec';
  if (line.startsWith('[pip]')) return '#bbb';
  if (/error|exception|traceback|failed/i.test(line)) return '#ff6b6b';
  if (/warn/i.test(line)) return '#fc6';
  return '#eee';
};

const RunConsole: React.FC<RunConsoleProps> = ({
  visible, run, lines, isStarting, error, onStop, onClose, onClear,
}) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [lines, visible]);

  if (!visible) return null;

  const running = run?.status === 'running' || run?.status === 'installing' || run?.status === 'preparing';

  return (
    <div style={wrap}>
      <div style={header}>
        <div>
          <strong style={{ color: '#fff' }}>▶ Console de Execução</strong>
          {run && <span style={pill(statusColor(run.status))}>{statusLabel(run.status)}</span>}
          {isStarting && !run && <span style={pill('#f57c00')}>INICIANDO...</span>}
          {run?.exit_code !== undefined && run?.exit_code !== null && (
            <span style={{ marginLeft: 8, color: '#aaa', fontSize: 11 }}>exit={run.exit_code}</span>
          )}
          {run?.total_lines !== undefined && (
            <span style={{ marginLeft: 8, color: '#aaa', fontSize: 11 }}>lines={lines.length}</span>
          )}
        </div>
        <div>
          {running && <button onClick={onStop} style={btn('#c62828')}>⏹ Parar</button>}
          <button onClick={onClear} style={btn('#444')} disabled={running}>Limpar</button>
          <button onClick={onClose} style={btn('#444')}>×</button>
        </div>
      </div>
      <div ref={ref} style={term}>
        {error && <div style={{ color: '#ff6b6b' }}>⚠ {error}</div>}
        {lines.length === 0 && !error && (
          <div style={{ color: '#888' }}>
            Aguardando saída do processo... (criação do venv + pip install pode levar ~1 min na primeira vez)
          </div>
        )}
        {lines.map((line, i) => (
          <div key={i} style={{ color: colorize(line) }}>{line || ' '}</div>
        ))}
      </div>
    </div>
  );
};

export default RunConsole;
