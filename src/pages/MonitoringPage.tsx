/**
 * Monitoramento — acompanha o sistema implantado: o que cada agente executou, quanto
 * demorou, o que falhou, e as chamadas às ferramentas externas. Lê o registro ao vivo da
 * implantação (o servidor de agentes escreve um evento por tarefa).
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  listProjectDeployments, getDeploymentLogs, DeploymentRun, DeployedService,
  parseTaskEvents, parseMcpCalls, summarizeTasks, TaskStat, McpCall, TaskEvent,
} from '../services/deploymentService';
import './MonitoringPage.css';

const ATIVO = ['preparing', 'installing', 'running'];
const rotuloStatus: Record<string, string> = {
  preparing: 'preparando', installing: 'instalando', running: 'no ar',
  stopped: 'parada', crashed: 'falhou',
};

const MonitoringPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [runs, setRuns] = useState<DeploymentRun[]>([]);
  const [runId, setRunId] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [servicos, setServicos] = useState<DeployedService[]>([]);
  const [linhas, setLinhas] = useState<string[]>([]);
  const [aba, setAba] = useState<'tarefas' | 'externas' | 'registro'>('tarefas');
  const [filtro, setFiltro] = useState('');
  const [erro, setErro] = useState('');
  const offsetRef = useRef(0);
  const logRef = useRef<HTMLPreElement>(null);

  useEffect(() => {
    if (!projectId) return;
    listProjectDeployments(projectId)
      .then((r) => {
        setRuns(r.runs);
        const alvo = r.runs.find((x) => ATIVO.includes(x.status)) || r.runs[0];
        if (alvo) setRunId(alvo.run_id);
      })
      .catch((e) => setErro(String(e.message || e)));
  }, [projectId]);

  // troca de implantação → recomeça a leitura do registro
  useEffect(() => { offsetRef.current = 0; setLinhas([]); }, [runId]);

  const puxar = useCallback(async () => {
    if (!runId) return;
    try {
      const r = await getDeploymentLogs(runId, offsetRef.current, 800);
      setStatus(r.status); setServicos(r.services);
      if (r.lines.length) {
        offsetRef.current = r.offset + r.lines.length;
        setLinhas((prev) => [...prev, ...r.lines].slice(-4000));
      }
    } catch (e: any) { setErro(String(e.message || e)); }
  }, [runId]);

  useEffect(() => {
    puxar();
    const t = setInterval(puxar, 3000);
    return () => clearInterval(t);
  }, [puxar]);

  useEffect(() => {
    if (aba === 'registro' && logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [linhas, aba]);

  const eventos: TaskEvent[] = parseTaskEvents(linhas);
  const tarefas: TaskStat[] = summarizeTasks(eventos);
  const chamadas: McpCall[] = parseMcpCalls(linhas);
  const totalOk = tarefas.reduce((a, t) => a + t.ok, 0);
  const totalErro = tarefas.reduce((a, t) => a + t.erros, 0);
  const durMedia = (() => {
    const ds = eventos.filter((e) => e.kind === 'OK' && e.seconds).map((e) => e.seconds as number);
    return ds.length ? (ds.reduce((a, b) => a + b, 0) / ds.length).toFixed(1) : '—';
  })();
  const visiveis = filtro ? linhas.filter((l) => l.toLowerCase().includes(filtro.toLowerCase())) : linhas;

  return (
    <div className="mon-page">
      <header className="mon-header">
        <h1>📈 Monitoramento</h1>
        <p>
          Acompanha o sistema implantado: quais tarefas os agentes executaram, quanto cada uma
          demorou, o que falhou e as chamadas às ferramentas externas. Os dados vêm do registro
          ao vivo da implantação — nada é simulado.
        </p>
      </header>

      {erro && <div className="mon-erro">⚠ {erro}</div>}

      <div className="mon-topo">
        <label>
          Implantação
          <select value={runId} onChange={(e) => setRunId(e.target.value)}>
            {runs.length === 0 && <option value="">nenhuma implantação</option>}
            {runs.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                {new Date(r.started_at).toLocaleString('pt-BR')} · {rotuloStatus[r.status] || r.status}
              </option>
            ))}
          </select>
        </label>
        <span className={`mon-badge ${status}`}>{rotuloStatus[status] || status || '—'}</span>
        <span className="mon-servicos">
          {servicos.map((s) => `${s.name.split(' (')[0]}:${s.port}`).join(' · ') || 'sem serviços'}
        </span>
      </div>

      <div className="mon-kpis">
        <div className="mon-kpi"><span>{tarefas.length}</span>tarefas exercitadas</div>
        <div className="mon-kpi ok"><span>{totalOk}</span>execuções com sucesso</div>
        <div className="mon-kpi err"><span>{totalErro}</span>falhas</div>
        <div className="mon-kpi"><span>{durMedia}s</span>duração média</div>
        <div className="mon-kpi"><span>{chamadas.length}</span>chamadas externas (MCP)</div>
        <div className="mon-kpi"><span>{linhas.length}</span>linhas de registro</div>
      </div>

      <div className="mon-abas">
        {(['tarefas', 'externas', 'registro'] as const).map((a) => (
          <button key={a} className={aba === a ? 'sel' : ''} onClick={() => setAba(a)}>
            {a === 'tarefas' ? 'Tarefas e agentes' : a === 'externas' ? 'Ferramentas externas' : 'Registro ao vivo'}
          </button>
        ))}
      </div>

      {aba === 'tarefas' && (
        <div className="mon-card">
          {tarefas.length === 0 && (
            <p className="mon-vazio">
              Nenhuma tarefa executada ainda nesta implantação. Use o sistema (ou o executor da
              Rede de Petri) e os eventos aparecem aqui.
            </p>
          )}
          {tarefas.length > 0 && (
            <table className="mon-tabela">
              <thead>
                <tr><th>Tarefa</th><th>Agente</th><th>Modo</th><th>Execuções</th>
                    <th>Sucesso</th><th>Falha</th><th>Última duração</th><th>Último erro</th></tr>
              </thead>
              <tbody>
                {tarefas.map((t) => (
                  <tr key={t.task}>
                    <td><strong>{t.task}</strong></td>
                    <td>{t.agent}</td>
                    <td><span className={`mon-modo ${t.mode}`}>{t.mode === 'agent' ? 'agente' : 'determinístico'}</span></td>
                    <td>{t.runs}</td>
                    <td className="ok">{t.ok}</td>
                    <td className={t.erros ? 'err' : ''}>{t.erros}</td>
                    <td>{t.lastSeconds != null ? `${t.lastSeconds}s` : '—'}</td>
                    <td className="erro-txt">{t.lastError || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {aba === 'externas' && (
        <div className="mon-card">
          {chamadas.length === 0 && <p className="mon-vazio">Nenhuma chamada a ferramenta externa registrada.</p>}
          {chamadas.length > 0 && (
            <table className="mon-tabela">
              <thead><tr><th>Ferramenta (MCP)</th><th>Argumentos enviados</th><th>Campos recebidos</th></tr></thead>
              <tbody>
                {chamadas.map((c, i) => (
                  <tr key={i}><td><strong>{c.tool}</strong></td><td><code>{c.args}</code></td><td><code>{c.fields}</code></td></tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {aba === 'registro' && (
        <div className="mon-card">
          <input className="mon-filtro" placeholder="filtrar (ex.: task, MCP, erro)…"
                 value={filtro} onChange={(e) => setFiltro(e.target.value)} />
          <pre className="mon-log" ref={logRef}>{visiveis.slice(-600).join('\n') || 'sem registro ainda…'}</pre>
        </div>
      )}
    </div>
  );
};

export default MonitoringPage;
