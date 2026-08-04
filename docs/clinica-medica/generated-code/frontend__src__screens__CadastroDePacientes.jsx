import React, { useState } from "react";
import { runTask, splitList } from "./wsClient";

export default function CadastroDePacientes() {
  const [form, setForm] = useState({ "nome": "", "cpf": "", "data_nascimento": "", "contato": "", "convenio": "" });
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [busy, setBusy] = useState(false);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const onPrimary = async () => {
    setBusy(true); setResult(null); setErr(null);
    try {
      const payload = {
      "nome": form["nome"],
      "cpf": form["cpf"],
      "data_nascimento": form["data_nascimento"],
      "contato": form["contato"],
      "convenio": form["convenio"],
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
        <h1 className="text-xl font-semibold text-slate-800">Cadastro de Pacientes</h1>
        <p className="text-xs text-slate-400 mt-0.5">UC-001 · form</p>
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-7">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Nome</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["nome"]} onChange={(e) => set("nome", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">CPF</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["cpf"]} onChange={(e) => set("cpf", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Data de Nascimento</label>
            <input type="date" className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["data_nascimento"]} onChange={(e) => set("data_nascimento", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Contato</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["contato"]} onChange={(e) => set("contato", e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Convênio</label>
            <input className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" value={form["convenio"]} onChange={(e) => set("convenio", e.target.value)} />
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
