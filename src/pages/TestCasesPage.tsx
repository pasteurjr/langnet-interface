import React, { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import "./TestCasesPage.css";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api";

interface Cause { id: string; desc: string; }
interface Effect { id: string; desc: string; }
interface CEG {
  uc: string;
  causes: Cause[];
  effects: Effect[];
  rules: { effect: string; expr: any }[];
  constraints: { type: string; causes?: string[]; effects?: string[] }[];
}
interface Column {
  target: string;
  causes: Record<string, boolean | "X">;
  effects: Record<string, boolean | null>;
}
interface TestCase {
  id: string;
  uc: string;
  entradas: { causa: string; desc: string; verdadeira: boolean }[];
  efeito_esperado: { efeito: string; desc: string };
}
interface UCResult {
  uc: string;
  name: string;
  actor?: string;
  objetivo?: string;
  error?: string;
  ceg?: CEG;
  svg?: string | null;
  decision_table?: Column[];
  test_cases?: TestCase[];
  n_causes?: number;
  n_effects?: number;
  n_cases?: number;
}
interface Session {
  session_id: string | null;
  status?: string;
  total_ucs?: number;
  total_cases?: number;
  results?: UCResult[];
  generation_log?: string;
  message?: string;
}

const cell = (v: boolean | "X" | null | undefined) =>
  v === true ? "1" : v === false ? "0" : "X";

const TestCasesPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const effectiveProjectId = projectId || localStorage.getItem("currentProjectId") || "";
  const token = localStorage.getItem("accessToken") || localStorage.getItem("access_token") || "";
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const [session, setSession] = useState<Session | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [authExpired, setAuthExpired] = useState(false);
  const pollRef = useRef<any>(null);

  const loadLatest = useCallback(async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/test-cases/project/${effectiveProjectId}/latest`, { headers });
      if (r.status === 401 || r.status === 403) {
        setAuthExpired(true);
        setGenerating(false);
        toast.error("Sessão expirada. Faça login novamente para ver os casos de teste.");
        return;
      }
      const d: Session = await r.json();
      if (!r.ok) throw new Error((d as any)?.detail || `HTTP ${r.status}`);
      setAuthExpired(false);
      setSession(d);
      setGenerating(d.status === "generating");
      setSelected((prev) => prev || (d.results && d.results[0] ? d.results[0].uc : null));
    } catch (e: any) {
      toast.error(`Falha ao carregar casos de teste: ${e.message}`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveProjectId]);

  useEffect(() => {
    loadLatest();
  }, [loadLatest]);

  // Polling enquanto está gerando
  useEffect(() => {
    if (generating) {
      pollRef.current = setInterval(loadLatest, 4000);
    } else if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => pollRef.current && clearInterval(pollRef.current);
  }, [generating, loadLatest]);

  const generate = async (only?: string[]) => {
    if (!effectiveProjectId) {
      toast.error("Nenhum projeto selecionado.");
      return;
    }
    setGenerating(true);
    try {
      const rs = await fetch(`${API_BASE}/specifications/project/${effectiveProjectId}/latest`, { headers }).catch(() => null);
      const specData = rs ? await rs.json() : {};
      const specId = specData?.session_id;
      if (!specId) {
        toast.error("Nenhuma especificação encontrada. Gere a Especificação Funcional primeiro.");
        setGenerating(false);
        return;
      }
      const body = JSON.stringify({ specification_session_id: specId, ...(only ? { only } : {}) });
      const r = await fetch(`${API_BASE}/test-cases/${effectiveProjectId}/generate`, { method: "POST", headers, body });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      toast.success("Geração de casos de teste iniciada (grafo causa-efeito por UC).");
      setTimeout(loadLatest, 1500);
    } catch (e: any) {
      toast.error(`Falha na geração: ${e.message}`);
      setGenerating(false);
    }
  };

  const results = session?.results || [];
  const current = results.find((r) => r.uc === selected) || null;

  return (
    <div className="tc-page">
      <header className="tc-header">
        <div>
          <h1>🧪 Casos de Teste &amp; Validação</h1>
          <p className="tc-sub">
            Casos de teste derivados dos casos de uso pela técnica do <b>Grafo de Causa-Efeito</b> (causas = ações do
            ator, efeitos = respostas do sistema). Cada coluna da tabela de decisão é um caso de teste.
          </p>
        </div>
        <div className="tc-actions">
          <button className="tc-btn primary" onClick={() => generate()} disabled={generating}>
            {generating ? "Gerando…" : "⚙️ Gerar casos de teste"}
          </button>
        </div>
      </header>

      {session && session.session_id && (
        <div className="tc-summary">
          <span className={`tc-badge ${session.status}`}>{session.status}</span>
          <span><b>{session.total_ucs || 0}</b> casos de uso</span>
          <span><b>{session.total_cases || 0}</b> casos de teste</span>
          {generating && <span className="tc-spin">↻ atualizando…</span>}
        </div>
      )}

      {authExpired && (
        <div className="tc-empty tc-auth">
          <p>🔒 <b>Sua sessão expirou.</b></p>
          <p>Faça <b>login novamente</b> para carregar os casos de teste — os dados continuam salvos.</p>
        </div>
      )}

      {!authExpired && (!session || !session.session_id) && (
        <div className="tc-empty">
          <p>Nenhum caso de teste gerado ainda.</p>
          <p>Clique em <b>Gerar casos de teste</b> para extrair o grafo causa-efeito de cada caso de uso da especificação.</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="tc-body">
          <aside className="tc-list">
            {results.map((r) => (
              <button
                key={r.uc}
                className={`tc-list-item ${selected === r.uc ? "active" : ""} ${r.error ? "err" : ""}`}
                onClick={() => setSelected(r.uc)}
              >
                <span className="tc-uc">{r.uc}</span>
                <span className="tc-name">{r.name}</span>
                {r.error ? (
                  <span className="tc-count err">falhou</span>
                ) : (
                  <span className="tc-count">{r.n_cases ?? 0} casos</span>
                )}
              </button>
            ))}
          </aside>

          <section className="tc-detail">
            {current && current.error && (
              <div className="tc-error-box">⚠️ Grafo não gerado para {current.uc}: {current.error}</div>
            )}
            {current && !current.error && (
              <>
                <div className="tc-uc-head">
                  <h2>{current.uc} — {current.name}</h2>
                  <div className="tc-meta">
                    {current.actor && <span><b>Ator:</b> {current.actor}</span>}
                    {current.objetivo && <span><b>Objetivo:</b> {current.objetivo}</span>}
                    <span><b>{current.n_causes}</b> causas · <b>{current.n_effects}</b> efeitos · <b>{current.n_cases}</b> casos</span>
                  </div>
                </div>

                {current.svg && (
                  <div className="tc-card">
                    <h3>Grafo de Causa-Efeito</h3>
                    <div className="tc-graph" dangerouslySetInnerHTML={{ __html: current.svg }} />
                  </div>
                )}

                {current.decision_table && current.decision_table.length > 0 && current.ceg && (
                  <div className="tc-card">
                    <h3>Tabela de Decisão</h3>
                    <div className="tc-table-wrap">
                      <table className="tc-dt">
                        <thead>
                          <tr>
                            <th></th>
                            {current.decision_table.map((_, i) => (
                              <th key={i}>C{i + 1}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {current.ceg.causes.map((c) => (
                            <tr key={c.id}>
                              <td className="lbl" title={c.desc}>{c.id}</td>
                              {current.decision_table!.map((col, i) => (
                                <td key={i}>{cell(col.causes[c.id])}</td>
                              ))}
                            </tr>
                          ))}
                          <tr className="sep"><td colSpan={current.decision_table.length + 1}></td></tr>
                          {current.ceg.effects.map((e) => (
                            <tr key={e.id}>
                              <td className="lbl eff" title={e.desc}>{e.id}</td>
                              {current.decision_table!.map((col, i) => (
                                <td key={i} className={col.effects[e.id] ? "on" : ""}>
                                  {cell(col.effects[e.id])}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <p className="tc-legend">1 = verdadeiro · 0 = falso · X = indiferente (don't-care). Efeito em verde = ativado.</p>
                  </div>
                )}

                {current.test_cases && current.test_cases.length > 0 && (
                  <div className="tc-card">
                    <h3>Casos de Teste ({current.test_cases.length})</h3>
                    <div className="tc-cases">
                      {current.test_cases.map((tcCase) => (
                        <div className="tc-case" key={tcCase.id}>
                          <div className="tc-case-id">{tcCase.id}</div>
                          <div className="tc-case-body">
                            <div className="tc-case-in">
                              <span className="tc-case-lbl">Entradas (ações do ator)</span>
                              <ul>
                                {tcCase.entradas.map((en) => (
                                  <li key={en.causa}>
                                    <span className={`tc-flag ${en.verdadeira ? "t" : "f"}`}>
                                      {en.verdadeira ? "V" : "F"}
                                    </span>
                                    {en.desc}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div className="tc-case-out">
                              <span className="tc-case-lbl">Resposta esperada do sistema</span>
                              <div className="tc-expected">✔ {tcCase.efeito_esperado.desc}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      )}
    </div>
  );
};

export default TestCasesPage;
