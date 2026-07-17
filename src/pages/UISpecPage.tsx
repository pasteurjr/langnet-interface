import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import "./UISpecPage.css";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api";

interface ScreenComponent {
  type: string;
  field?: string;
  label?: string;
  bindTo?: string | null;
}
interface ScreenAction {
  label: string;
  kind: string;
  target?: string;
  primary?: boolean;
}
interface Screen {
  id: string;
  name: string;
  route?: string;
  uc?: string[];
  entity?: string | null;
  layout?: string;
  components?: ScreenComponent[];
  actions?: ScreenAction[];
}
interface UISpec {
  screens: Screen[];
  navigation: { label: string; route: string }[];
  action_map: Record<string, { kind: string; screen?: string }>;
}
interface Session {
  session_id: string | null;
  status?: string;
  version?: number;
  screens_count?: number;
  ui_spec?: UISpec;
  message?: string;
}

const UISpecPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const effectiveProjectId = projectId || localStorage.getItem("currentProjectId") || "";
  const token = localStorage.getItem("accessToken") || localStorage.getItem("access_token") || "";
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const [session, setSession] = useState<Session | null>(null);
  const [mockups, setMockups] = useState<Record<string, string>>({});
  const [generating, setGenerating] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [chatMsg, setChatMsg] = useState("");
  const [chatSending, setChatSending] = useState(false);

  const loadLatest = useCallback(async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/ui-spec/project/${effectiveProjectId}/latest`, { headers });
      const d = await r.json();
      setSession(d);
      if (d.session_id) {
        const rm = await fetch(`${API_BASE}/ui-spec/${d.session_id}/mockups`, { headers });
        const dm = await rm.json();
        setMockups(dm.mockups || {});
        const first = (d.ui_spec?.screens || [])[0];
        if (first) setSelected(first.id);
      }
    } catch (e: any) {
      toast.error(`Falha ao carregar UI Spec: ${e.message}`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveProjectId]);

  useEffect(() => {
    loadLatest();
  }, [loadLatest]);

  const generate = async () => {
    setGenerating(true);
    try {
      // descobre spec + data model mais recentes
      const rs = await fetch(`${API_BASE}/specifications/project/${effectiveProjectId}/latest`, { headers }).catch(() => null);
      const specData = rs ? await rs.json() : {};
      const specId = specData?.session_id;
      if (!specId) {
        toast.error("Nenhuma especificação encontrada. Gere a Especificação primeiro.");
        setGenerating(false);
        return;
      }
      const body = JSON.stringify({ specification_session_id: specId, render_png: true });
      const r = await fetch(`${API_BASE}/ui-spec/${effectiveProjectId}/generate`, { method: "POST", headers, body });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      toast.success("UI Spec gerada!");
      await loadLatest();
    } catch (e: any) {
      toast.error(`Falha na geração: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const sendRefine = async () => {
    if (!session?.session_id || !chatMsg.trim()) return;
    setChatSending(true);
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${session.session_id}/chat`, {
        method: "POST", headers,
        body: JSON.stringify({ content: chatMsg, screen_id: selected }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      setChatMsg("");
      // Atualiza só o mockup da tela refinada, sem recarregar tudo
      if (d.mockup_update) setMockups((m) => ({ ...m, ...d.mockup_update }));
      if (d.ui_spec) setSession((s) => (s ? { ...s, ui_spec: d.ui_spec } : s));
      toast.success(`Tela "${d.refined_screen || selected}" atualizada`);
    } catch (e: any) {
      toast.error(`Falha no refino: ${e.message}`);
    } finally {
      setChatSending(false);
    }
  };

  const approve = async () => {
    if (!session?.session_id) return;
    try {
      await fetch(`${API_BASE}/ui-spec/${session.session_id}/approve`, {
        method: "POST", headers, body: JSON.stringify({ approve: true }),
      });
      toast.success("UI Spec aprovada");
      await loadLatest();
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const screens = session?.ui_spec?.screens || [];
  const current = screens.find((s) => s.id === selected) || null;

  return (
    <div className="uispec-page">
      <div className="uispec-header">
        <div>
          <h1>🎨 Especificação & Protótipo de Interface</h1>
          <span className="uispec-meta">
            {session?.session_id
              ? `${session.screens_count || screens.length} telas · v${session.version} · ${session.status}`
              : "Nenhuma UI Spec gerada ainda"}
          </span>
        </div>
        <div className="uispec-actions">
          <button className="btn-primary" onClick={generate} disabled={generating}>
            {generating ? "Gerando… (pode levar min)" : "⚡ Gerar UI Spec"}
          </button>
          {session?.session_id && session.status !== "approved" && (
            <button className="btn-approve" onClick={approve}>✓ Aprovar</button>
          )}
        </div>
      </div>

      {!session?.session_id && (
        <div className="uispec-empty">
          A UI Spec é gerada a partir da Especificação Funcional (casos de uso + wireframes) e do
          Modelo de Dados. Clique em <b>Gerar UI Spec</b>.
        </div>
      )}

      {screens.length > 0 && (
        <div className="uispec-body">
          <div className="uispec-list">
            {screens.map((s) => (
              <div
                key={s.id}
                className={`uispec-item ${selected === s.id ? "active" : ""}`}
                onClick={() => setSelected(s.id)}
              >
                <div className="uispec-item-name">{s.name}</div>
                <div className="uispec-item-meta">
                  {(s.uc || []).join(",")} · {s.layout} · {s.entity || "—"}
                </div>
              </div>
            ))}
          </div>

          <div className="uispec-preview">
            {current && (
              <>
                <h3>{current.name}</h3>
                {mockups[current.id] ? (
                  <img className="uispec-mockup" src={mockups[current.id]} alt={current.name} />
                ) : (
                  <div className="uispec-nomock">Sem mockup renderizado.</div>
                )}
                <div className="uispec-struct">
                  <h4>Componentes</h4>
                  <ul>
                    {(current.components || []).map((c, i) => (
                      <li key={i}>
                        <code>{c.type}</code> {c.label} {c.bindTo ? `→ ${c.bindTo}` : ""}
                      </li>
                    ))}
                  </ul>
                  <h4>Ações</h4>
                  <ul>
                    {(current.actions || []).map((a, i) => (
                      <li key={i}>
                        <b>{a.label}</b> — {a.kind} {a.target ? `→ ${a.target}` : ""}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {session?.session_id && (
        <div className="uispec-chat">
          <input
            value={chatMsg}
            onChange={(e) => setChatMsg(e.target.value)}
            placeholder={current ? `Refinar "${current.name}" (ex.: "adicione um campo telefone")` : "Selecione uma tela para refinar"}
            onKeyDown={(e) => e.key === "Enter" && sendRefine()}
          />
          <button onClick={sendRefine} disabled={chatSending}>
            {chatSending ? "…" : "Refinar"}
          </button>
        </div>
      )}
    </div>
  );
};

export default UISpecPage;
