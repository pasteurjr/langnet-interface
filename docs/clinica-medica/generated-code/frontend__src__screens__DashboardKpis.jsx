import React, { useState, useEffect } from "react";
import { runTask } from "./wsClient";

const TASK = null;
const INPUTS = [{"key": "busca", "label": "Busca"}];
const KPIS = [];
const IS_DASHBOARD = false;
const HAS_FK = false;

export default function DashboardKpis() {
  const [form, setForm] = useState(Object.fromEntries(INPUTS.map((f) => [f.key, ""])));
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const IN = "w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 outline-none";

  const executar = async () => {
    if (!TASK) { setErr("Ação indisponível: nenhuma tarefa definida para esta tela."); return; }
    setBusy(true); setResult(null); setErr(null);
    try { const r = await runTask(TASK, form); setResult(r); }
    catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  const renderResult = (r) => {
    if (r == null) return null;
    if (typeof r === "string") return <p className="text-slate-700 whitespace-pre-wrap">{r}</p>;
    if (Array.isArray(r)) return <ul className="list-disc pl-5 text-slate-700">{r.map((x, i) => <li key={i}>{typeof x === "object" ? JSON.stringify(x) : String(x)}</li>)}</ul>;
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {Object.entries(r).map(([k, v]) => (
          <div key={k} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-400 uppercase">{k}</div>
            <div className="text-sm text-slate-800 mt-0.5 break-words">{typeof v === "object" ? JSON.stringify(v) : String(v)}</div>
          </div>
        ))}
      </div>
    );
  };

  // G2: valor de um KPI a partir do resultado do agente (aceita {kpi:val} ou {kpis:{...}})
  const kpiVal = (key) => {
    if (!result || typeof result !== "object") return "—";
    const src = result.kpis && typeof result.kpis === "object" ? result.kpis : result;
    const v = src[key];
    return v == null ? "—" : (typeof v === "object" ? JSON.stringify(v) : String(v));
  };

  // P3: opções dos campos FK (dropdown) carregadas da entidade referenciada.
  const [fkOpts, setFkOpts] = useState({});
  useEffect(() => {
    if (!HAS_FK) return;
    (async () => {
      const next = {};
      for (const fd of INPUTS) {
        if (!fd.ref) continue;
        try {
          const r = await runTask("listar_" + fd.ref, {});
          next[fd.key] = Array.isArray(r) ? r : (r && r.rows ? r.rows : []);
        } catch (e) { next[fd.key] = []; }
      }
      setFkOpts(next);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="max-w-5xl">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-800">Dashboard KPIs</h1>
          <p className="text-xs text-slate-400 mt-0.5">UC-010 · {IS_DASHBOARD ? "painel · atualizado por agente de IA" : "executado por agente de IA"}</p>
        </div>
        <button className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-60 inline-flex items-center gap-2" disabled={busy || !TASK} onClick={executar}>
          {busy && <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />}
          {busy ? "Atualizando…" : (IS_DASHBOARD ? "↻ Atualizar" : "▷ Executar com IA")}
        </button>
      </div>

      {/* Dashboard: cards de KPI (placeholder — populados pelo resultado do agente) */}
      {IS_DASHBOARD && KPIS.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {KPIS.map((k) => (
            <div key={k.key} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
              <div className="text-xs text-slate-400 uppercase tracking-wide">{k.label}</div>
              <div className="text-3xl font-bold text-slate-800 mt-1">{kpiVal(k.key)}</div>
            </div>
          ))}
        </div>
      )}

      {INPUTS.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7 mb-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {INPUTS.map((fd) => (
              <div key={fd.key}>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">{fd.label}</label>
                {fd.ref ? (
                  <select className={IN} value={form[fd.key]} onChange={(e) => set(fd.key, e.target.value)}>
                    <option value="">Selecione…</option>
                    {(fkOpts[fd.key] || []).map((o) => (
                      <option key={o.id} value={o.id}>{o.nome || o.name || o.titulo || o.tema || o.descricao || o.id}</option>
                    ))}
                  </select>
                ) : (
                  <input className={IN} value={form[fd.key]} onChange={(e) => set(fd.key, e.target.value)} />
                )}
              </div>
            ))}
          </div>
          {!IS_DASHBOARD && (
            <div className="mt-4"><span className="text-xs text-slate-400">{TASK ? <>Dispara o agente <code>{TASK}</code></> : "Tarefa não definida para esta tela"}</span></div>
          )}
        </div>
      )}
      {INPUTS.length === 0 && !IS_DASHBOARD && (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7 mb-5">
          <span className="text-xs text-slate-400">{TASK ? <>Dispara o agente <code>{TASK}</code></> : "Tarefa não definida para esta tela"}</span>
        </div>
      )}

      {err && <div className="mt-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">⚠ {err}</div>}
      {result != null && !(IS_DASHBOARD && KPIS.length > 0) && (
        <div className="mt-5">
          <h3 className="text-sm font-semibold text-slate-600 mb-2">Resultado</h3>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">{renderResult(result)}</div>
        </div>
      )}
    </div>
  );
}
