import React, { useState } from "react";
import { runTask, splitList } from "./wsClient";

export default function ConsultaMedica() {
  const [form, setForm] = useState({ "resumo_medico": "", "conduta": "", "prescricao": "" });
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const onPrimary = async () => {
    setBusy(true); setResult(null); setErr(null);
    try {
      const payload = {
      "paciente_id": "",
      "atendimento_id": "",
      "triagem": "",
      "pre_diagnostico_id": "",
      "encaminhamento_id": "",
      "resumo_medico": form["resumo_medico"]
      };
      const r = await runTask("registrar_prontuario", payload);
      setResult(r);
    } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="max-w-5xl">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-800">Consulta Médica</h1>
        <p className="text-xs text-slate-400 mt-0.5">UC-007 · form</p>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Paciente</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Atendimento</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Hipóteses</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Nível de confiança</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Exames sugeridos</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Diagnóstico Final</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["resumo_medico"]} onChange={(e) => set("resumo_medico", e.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Conduta</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["conduta"]} onChange={(e) => set("conduta", e.target.value)} />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Prescrição</label>
            <textarea className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" rows={2} value={form["prescricao"]} onChange={(e) => set("prescricao", e.target.value)} />
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
