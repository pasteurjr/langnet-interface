import React, { useEffect, useState } from "react";
import MainExecutor from "./components/MainExecutor";
import { CadastroDePacientes } from "./screens";
import { TriagemAgentiva } from "./screens";
import { PreAtendimentoEspecialista } from "./screens";
import { GeracaoPreDiagnostico } from "./screens";
import { SelecaoDeMedico } from "./screens";
import { RegistroProntuario } from "./screens";
import { ConsultaMedica } from "./screens";
import { GestaoDeConsentimentoLgpd } from "./screens";
import { ProcedimentoManual } from "./screens";
import { DashboardKpis } from "./screens";
import { GestaoDeAgendas } from "./screens";
import { GestaoDeAgentes } from "./screens";
import { GestaoDeEspecialidades } from "./screens";
import { GestaoDeMedicos } from "./screens";
import { GestaoDePacientes } from "./screens";
import { GestaoDeAtendimentos } from "./screens";
import { GestaoPreDiagnosticos } from "./screens";
import { GestaoDeEncaminhamentos } from "./screens";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";

const SCREENS = [
  { id: "cadastro-de-pacientes", label: "Cadastro de Pacientes", Comp: CadastroDePacientes, kind: "form", module: "Cadastros" },
  { id: "triagem-agentiva", label: "Triagem Agentiva", Comp: TriagemAgentiva, kind: "agent", module: "Cadastros" },
  { id: "pre-atendimento-especialista", label: "Pr\u00e9-atendimento por Especialista", Comp: PreAtendimentoEspecialista, kind: "agent", module: "Cadastros" },
  { id: "geracao-pre-diagnostico", label: "Gera\u00e7\u00e3o de Pr\u00e9-Diagn\u00f3stico", Comp: GeracaoPreDiagnostico, kind: "agent", module: "Cadastros" },
  { id: "selecao-de-medico", label: "Sele\u00e7\u00e3o de M\u00e9dico", Comp: SelecaoDeMedico, kind: "agent", module: "Cadastros" },
  { id: "registro-prontuario", label: "Registro/Prontu\u00e1rio", Comp: RegistroProntuario, kind: "form", module: "Cadastros" },
  { id: "consulta-medica", label: "Consulta M\u00e9dica", Comp: ConsultaMedica, kind: "form", module: "Cadastros" },
  { id: "gestao-de-consentimento-lgpd", label: "Gest\u00e3o de Consentimento LGPD", Comp: GestaoDeConsentimentoLgpd, kind: "form", module: "Cadastros" },
  { id: "procedimento-manual", label: "Procedimento Manual", Comp: ProcedimentoManual, kind: "form", module: "Cadastros" },
  { id: "dashboard-kpis", label: "Dashboard KPIs", Comp: DashboardKpis, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-agendas", label: "Gest\u00e3o de Agendas", Comp: GestaoDeAgendas, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-agentes", label: "Gest\u00e3o de Agentes", Comp: GestaoDeAgentes, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-especialidades", label: "Gest\u00e3o de Especialidades", Comp: GestaoDeEspecialidades, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-medicos", label: "Gest\u00e3o de M\u00e9dicos", Comp: GestaoDeMedicos, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-pacientes", label: "Gest\u00e3o de Pacientes", Comp: GestaoDePacientes, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-atendimentos", label: "Gest\u00e3o de Atendimentos", Comp: GestaoDeAtendimentos, kind: "agent", module: "Cadastros" },
  { id: "gestao-pre-diagnosticos", label: "Gest\u00e3o de Pr\u00e9-Diagn\u00f3sticos", Comp: GestaoPreDiagnosticos, kind: "agent", module: "Cadastros" },
  { id: "gestao-de-encaminhamentos", label: "Gest\u00e3o de Encaminhamentos", Comp: GestaoDeEncaminhamentos, kind: "agent", module: "Cadastros" }
];
const MODULE_ORDER = ["Cadastros", "Conteúdo", "Publicação", "Engajamento", "Relatórios", "Integrações", "Geral"];
const KIND_ICON = {"crud": "▦", "report": "▤", "agent": "✦", "form": "▧"};
const BRAND = "ClinIA — Clínica Médica Inteligente";

function App() {
  const [view, setView] = useState(SCREENS.length ? SCREENS[0].id : "admin");
  const [project, setProject] = useState(null);
  const [collapsed, setCollapsed] = useState({});

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/projects`).then((r) => r.json()).then((d) => {
      const p = (d.projects || [])[0];
      if (p) fetch(`${BACKEND_URL}/api/projects/${p.id}`).then((r) => r.json()).then((x) => setProject(x.project));
    }).catch(() => {});
  }, []);

  // agrupa telas por módulo, na ordem canônica
  const groups = {};
  SCREENS.forEach((s) => { (groups[s.module] = groups[s.module] || []).push(s); });
  const orderedMods = MODULE_ORDER.filter((m) => groups[m]).concat(Object.keys(groups).filter((m) => !MODULE_ORDER.includes(m)));

  const current = SCREENS.find((s) => s.id === view);
  const itemCls = (active) => "px-4 py-2 cursor-pointer text-sm rounded-md mx-2 flex items-center gap-2 " + (active ? "bg-indigo-600 text-white font-medium" : "text-slate-300 hover:bg-slate-800");

  return (
    <div className="flex min-h-screen bg-slate-100" style={{fontFamily:"Inter,sans-serif"}}>
      <aside className="w-64 bg-slate-900 flex flex-col shrink-0">
        <div className="px-5 py-4 text-white font-bold text-base flex items-center gap-2 border-b border-slate-800">
          <span className="w-7 h-7 rounded-lg bg-indigo-500 inline-flex items-center justify-center text-sm">{BRAND.slice(0,1)}</span>
          {BRAND}
        </div>
        <nav className="mt-2 flex-1 overflow-y-auto pb-4">
          {orderedMods.map((mod) => (
            <div key={mod} className="mb-1">
              <div className="px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500 flex items-center justify-between cursor-pointer select-none"
                   onClick={() => setCollapsed((c) => ({ ...c, [mod]: !c[mod] }))}>
                <span>{mod}</span><span className="text-slate-600">{collapsed[mod] ? "▸" : "▾"}</span>
              </div>
              {!collapsed[mod] && groups[mod].map((s) => (
                <div key={s.id} className={itemCls(view === s.id)} onClick={() => setView(s.id)}>
                  <span className="text-xs opacity-70">{KIND_ICON[s.kind] || "•"}</span>{s.label}
                </div>
              ))}
            </div>
          ))}
          <div className="border-t border-slate-800 mt-2 pt-2">
            <div className={itemCls(view === "admin")} onClick={() => setView("admin")}><span className="text-xs">⚙</span>Admin / Petri</div>
          </div>
        </nav>
      </aside>
      <main className="flex-1 p-8 overflow-auto">
        {current && <current.Comp />}
        {view === "admin" && (project ? <MainExecutor project={project} onBack={() => {}} /> : <p className="text-slate-400">Carregando projeto…</p>)}
      </main>
    </div>
  );
}

export default App;
