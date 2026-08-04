import React, { useState, useEffect } from "react";
import { runTask, splitList } from "./wsClient";

export default function RegistroProntuario() {
  const [form, setForm] = useState({ "atendimento_id": "", "triagem": "", "classificacao_urgencia": "", "area_destino": "", "hipoteses": "", "nivel_confianca": "", "exames_sugeridos": "", "medico_id": "", "prioridade": "", "resumo_medico": "" });
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);
  const [fkOpts, setFkOpts] = useState({});
  const FK_FIELDS = [{ field: "atendimento_id", ref: "atendimentos" }, { field: "medico_id", ref: "medicos" }];
  useEffect(() => {
    (async () => {
      const next = {};
      for (const fk of FK_FIELDS) {
        try {
          const r = await runTask("listar_" + fk.ref, {});
          next[fk.field] = Array.isArray(r) ? r : (r && r.rows ? r.rows : []);
        } catch (e) { next[fk.field] = []; }
      }
      setFkOpts(next);
    })();
  }, []);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const onPrimary = async () => {
    setBusy(true); setResult(null); setErr(null);
    try {
      const payload = {
      "nome": "",
      "cpf": "",
      "data_nascimento": "",
      "contato": "",
      "convenio": "",
      "historico": "",
      "status": "",
      "consentimento": ""
      };
      const r = await runTask("cadastrar_paciente", payload);
      setResult(r);
    } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="max-w-5xl">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-800">Registro/Prontuário</h1>
        <p className="text-xs text-slate-400 mt-0.5">UC-006 · form</p>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Paciente</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Status</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Atendimento</label>
            <select className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["atendimento_id"]} onChange={(e) => set("atendimento_id", e.target.value)}><option value="">Selecione…</option>{(fkOpts["atendimento_id"] || []).map((o) => <option key={o.id} value={o.id}>{o.nome || o.name || o.titulo || o.descricao || o.id}</option>)}</select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Queixa inicial</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["triagem"]} onChange={(e) => set("triagem", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Classificação de urgência</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["classificacao_urgencia"]} onChange={(e) => set("classificacao_urgencia", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Área de destino</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["area_destino"]} onChange={(e) => set("area_destino", e.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Hipóteses</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["hipoteses"]} onChange={(e) => set("hipoteses", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Nível de confiança (%)</label>
            <input type="number" className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["nivel_confianca"]} onChange={(e) => set("nivel_confianca", e.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Exames sugeridos</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["exames_sugeridos"]} onChange={(e) => set("exames_sugeridos", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Médico</label>
            <select className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["medico_id"]} onChange={(e) => set("medico_id", e.target.value)}><option value="">Selecione…</option>{(fkOpts["medico_id"] || []).map((o) => <option key={o.id} value={o.id}>{o.nome || o.name || o.titulo || o.descricao || o.id}</option>)}</select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Prioridade</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["prioridade"]} onChange={(e) => set("prioridade", e.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Resumo para o médico</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["resumo_medico"]} onChange={(e) => set("resumo_medico", e.target.value)} />
          </div>
        </div>
        <div className="mt-6 pt-5 border-t border-slate-100 flex justify-end">
          <button className="px-5 py-2.5 rounded-lg bg-indigo-600 text-white text-sm font-medium shadow-sm hover:bg-indigo-700 disabled:opacity-60" disabled={busy} onClick={onPrimary}>{busy ? "Processando…" : "Salvar"}</button>
        </div>
      </div>
      {err && <div className="mt-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">⚠ {err}</div>}
      {result && <div className="mt-4 rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-3"><pre className="text-xs text-emerald-800 whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre></div>}
    </div>
  );
}
