/**
 * Implantação — sobe o sistema gerado (servidor de agentes + API + interface) a partir de
 * uma versão da Geração de Código, mostra onde ele ficou disponível e permite parar.
 * Tudo real: fala com o motor de execução do backend (/api/code-generation/...).
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { listCodeSessions, CodeGenerationSession } from '../services/codeGenerationService';
import {
  startDeployment, getDeployment, stopDeployment, listProjectDeployments, getEnvTemplate,
  DeploymentRun,
} from '../services/deploymentService';
import './DeploymentPage.css';

const ATIVO = ['preparing', 'installing', 'running'];

/** O que o operador precisa informar para o sistema subir funcionando. */
const CAMPOS_CONFIG: { key: string; label: string; tipo?: string; dica?: string }[] = [
  { key: 'DB_HOST', label: 'Servidor do banco' },
  { key: 'DB_PORT', label: 'Porta do banco' },
  { key: 'DB_NAME', label: 'Banco de dados' },
  { key: 'DB_USER', label: 'Usuário do banco' },
  { key: 'DB_PASSWORD', label: 'Senha do banco', tipo: 'password' },
  { key: 'LLM_PROVIDER', label: 'Provedor de IA', dica: 'deepseek ou lmstudio' },
  { key: 'DEEPSEEK_API_KEY', label: 'Chave da IA (se nuvem)', tipo: 'password' },
];

const rotuloStatus: Record<string, string> = {
  preparing: 'preparando', installing: 'instalando dependências',
  running: 'no ar', stopped: 'parada', crashed: 'falhou',
};

const DeploymentPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [sessoes, setSessoes] = useState<CodeGenerationSession[]>([]);
  const [sessaoSel, setSessaoSel] = useState<string>('');
  const [run, setRun] = useState<DeploymentRun | null>(null);
  const [historico, setHistorico] = useState<DeploymentRun[]>([]);
  const [erro, setErro] = useState<string>('');
  const [implantando, setImplantando] = useState(false);
  const [config, setConfig] = useState<Record<string, string>>({});
  const logRef = useRef<HTMLPreElement>(null);

  useEffect(() => {
    if (!projectId) return;
    listCodeSessions(projectId)
      .then((s) => {
        const ok = s.filter((x) => x.status === 'completed');
        setSessoes(ok);
        setSessaoSel((v) => v || (ok[0]?.id ?? ''));
      })
      .catch((e) => setErro(String(e.message || e)));
    listProjectDeployments(projectId)
      .then((r) => {
        setHistorico(r.runs);
        const viva = r.runs.find((x) => ATIVO.includes(x.status));
        if (viva) setRun(viva);
      })
      .catch(() => {});
  }, [projectId]);

  // Ao escolher a versão, carrega o modelo de configuração que o pacote traz (.env.example).
  useEffect(() => {
    if (!sessaoSel) return;
    getEnvTemplate(sessaoSel)
      .then((t) => {
        const base: Record<string, string> = {};
        t.items.forEach((i) => { base[i.key] = i.value; });
        setConfig((atual) => {
          const novo = { ...base };
          // preserva o que o operador já digitou nesta sessão de tela
          CAMPOS_CONFIG.forEach(({ key }) => { if (atual[key]) novo[key] = atual[key]; });
          return novo;
        });
      })
      .catch(() => {});
  }, [sessaoSel]);

  // Acompanha a implantação viva (estado + fim do log) enquanto ela não termina.
  const acompanhar = useCallback(async (runId: string) => {
    try {
      const r = await getDeployment(runId);
      setRun(r);
      if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    } catch (e: any) { setErro(String(e.message || e)); }
  }, []);

  useEffect(() => {
    if (!run || !ATIVO.includes(run.status)) return;
    const t = setInterval(() => acompanhar(run.run_id), 2500);
    return () => clearInterval(t);
  }, [run, acompanhar]);

  const implantar = async () => {
    if (!sessaoSel) return;
    setErro(''); setImplantando(true);
    try {
      const r = await startDeployment(sessaoSel, config);
      setRun(r);
      if (projectId) listProjectDeployments(projectId).then((x) => setHistorico(x.runs)).catch(() => {});
    } catch (e: any) { setErro(String(e.message || e)); }
    setImplantando(false);
  };

  const parar = async () => {
    if (!run) return;
    try {
      const r = await stopDeployment(run.run_id);
      setRun(r);
      if (projectId) listProjectDeployments(projectId).then((x) => setHistorico(x.runs)).catch(() => {});
    } catch (e: any) { setErro(String(e.message || e)); }
  };

  const decorrido = (r: DeploymentRun) => {
    if (!r.started_at) return '—';
    const fim = r.finished_at ? new Date(r.finished_at) : new Date();
    const s = Math.max(0, Math.round((fim.getTime() - new Date(r.started_at).getTime()) / 1000));
    return s < 60 ? `${s}s` : `${Math.floor(s / 60)}min ${s % 60}s`;
  };
  const hora = (v?: string) => (v ? new Date(v).toLocaleString('pt-BR') : '—');

  return (
    <div className="dep-page">
      <header className="dep-header">
        <h1>🚀 Implantação</h1>
        <p>
          Sobe o sistema gerado a partir de uma versão da Geração de Código: o servidor de
          agentes, a API e a interface. Cada implantação roda em ambiente próprio e em portas
          livres — não interfere no que já está no ar.
        </p>
      </header>

      {erro && <div className="dep-erro">⚠ {erro}</div>}

      <div className="dep-grid">
        <section className="dep-card">
          <h2>Versão gerada</h2>
          {sessoes.length === 0 && <p className="dep-vazio">Nenhuma geração concluída neste projeto.</p>}
          <ul className="dep-sessoes">
            {sessoes.map((s) => (
              <li key={s.id}
                  className={s.id === sessaoSel ? 'sel' : ''}
                  onClick={() => setSessaoSel(s.id)}>
                <strong>{s.session_name || s.id.slice(0, 8)}</strong>
                <span>{s.total_files ?? s.generated_files?.length ?? 0} arquivos · {hora(s.created_at)}</span>
              </li>
            ))}
          </ul>
          <h3>Configuração da implantação</h3>
          <p className="dep-nota">
            O pacote gerado traz o modelo de configuração, mas nenhum segredo — credenciais
            são informadas aqui, na hora de implantar.
          </p>
          <div className="dep-config">
            {CAMPOS_CONFIG.map(({ key, label, tipo, dica }) => (
              <label key={key}>
                <span>{label}</span>
                <input
                  type={tipo || 'text'}
                  value={config[key] ?? ''}
                  placeholder={dica || key}
                  onChange={(e) => setConfig((c) => ({ ...c, [key]: e.target.value }))}
                />
              </label>
            ))}
          </div>
          <button className="dep-btn" disabled={!sessaoSel || implantando} onClick={implantar}>
            {implantando ? 'Implantando…' : '🚀 Implantar esta versão'}
          </button>
        </section>

        <section className="dep-card">
          <h2>Implantação atual</h2>
          {!run && <p className="dep-vazio">Nada implantado ainda. Escolha uma versão e implante.</p>}
          {run && (
            <>
              <div className="dep-status-linha">
                <span className={`dep-badge ${run.status}`}>{rotuloStatus[run.status] || run.status}</span>
                <span className="dep-meta">iniciada {hora(run.started_at)} · {decorrido(run)}</span>
                {ATIVO.includes(run.status) && (
                  <button className="dep-btn sec" onClick={parar}>⏹ Parar</button>
                )}
              </div>

              <h3>Onde o sistema ficou disponível</h3>
              {run.services.length === 0 && <p className="dep-vazio">subindo os serviços…</p>}
              <table className="dep-tabela">
                <tbody>
                  {run.services.map((sv) => (
                    <tr key={sv.name}>
                      <td>{sv.name}</td>
                      <td className="porta">porta {sv.port}</td>
                      <td>
                        {sv.url.startsWith('http')
                          ? <a href={sv.url} target="_blank" rel="noreferrer">{sv.url}</a>
                          : <code>{sv.url}</code>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <h3>Registro da implantação <small>({run.total_lines} linhas)</small></h3>
              <pre className="dep-log" ref={logRef}>
                {(run.stdout_tail || []).slice(-120).join('\n') || 'aguardando…'}
              </pre>
              <p className="dep-meta">pasta: <code>{run.work_dir}</code></p>
            </>
          )}
        </section>
      </div>

      <section className="dep-card">
        <h2>Histórico de implantações</h2>
        {historico.length === 0 && <p className="dep-vazio">Nenhuma implantação registrada.</p>}
        {historico.length > 0 && (
          <table className="dep-tabela hist">
            <thead>
              <tr><th>Início</th><th>Estado</th><th>Duração</th><th>Serviços</th><th>Versão gerada</th><th /></tr>
            </thead>
            <tbody>
              {historico.map((r) => (
                <tr key={r.run_id}>
                  <td>{hora(r.started_at)}</td>
                  <td><span className={`dep-badge ${r.status}`}>{rotuloStatus[r.status] || r.status}</span></td>
                  <td>{decorrido(r)}</td>
                  <td>{r.services.map((s) => s.port).join(', ') || '—'}</td>
                  <td><code>{r.session_id.slice(0, 8)}</code></td>
                  <td><button className="dep-link" onClick={() => setRun(r)}>ver</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
};

export default DeploymentPage;
