import React, { useState, useEffect } from "react";
import { runTask, splitList } from "./wsClient";

export default function GestaoDeConsentimentoLgpd() {
  const [form, setForm] = useState({ "paciente_id": "", "concorda": "" });
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);
  const [fkOpts, setFkOpts] = useState({});
  const FK_FIELDS = [{ field: "paciente_id", ref: "pacientes" }];
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
        <h1 className="text-xl font-semibold text-slate-800">Gestão de Consentimento LGPD</h1>
        <p className="text-xs text-slate-400 mt-0.5">UC-008 · form</p>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Data/Hora</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="text-xs text-slate-400 uppercase tracking-wide">Versão Termo</div>
            <div className="text-3xl font-bold text-slate-800 mt-1">—</div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Paciente</label>
            <select className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["paciente_id"]} onChange={(e) => set("paciente_id", e.target.value)}><option value="">Selecione…</option>{(fkOpts["paciente_id"] || []).map((o) => <option key={o.id} value={o.id}>{o.nome || o.name || o.titulo || o.descricao || o.id}</option>)}</select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Paciente concorda com os termos?</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["concorda"]} onChange={(e) => set("concorda", e.target.value)} />
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
