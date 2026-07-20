import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import StagePageLayout from "../components/stage/StagePageLayout";
// Reutiliza os estilos compartilhados das etapas (chat, botões, badges) e os
// estilos específicos da galeria de mockups desta etapa.
import "./TestCasesPage.css";
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
interface ChatMessage {
  role: string;
  content: string;
  created_at?: string;
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
  const [instructions, setInstructions] = useState("");
  const [chatMsg, setChatMsg] = useState("");
  const [chatSending, setChatSending] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [approving, setApproving] = useState(false);
  const [authExpired, setAuthExpired] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  // Seleção da origem (Especificação Funcional). Vazio = auto-descobrir a mais recente.
  const [availableSpecs, setAvailableSpecs] = useState<{ id: string; version: number }[]>([]);
  const [selectedSpec, setSelectedSpec] = useState<string>("");

  const loadChat = useCallback(async (sid: string) => {
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${sid}/chat`, { headers });
      if (!r.ok) return;
      const d = await r.json();
      setChatMessages(d.messages || []);
    } catch {
      /* silencioso */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Especificações disponíveis (origem), com versão — para escolher a origem.
  const loadSpecs = useCallback(async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/specifications/?project_id=${effectiveProjectId}`, { headers });
      if (!r.ok) return;
      const d = await r.json();
      const rows = Array.isArray(d) ? d : d.sessions || d.specifications || d.results || d.items || [];
      const specs = rows
        .map((s: any) => ({ id: s.id || s.session_id, version: s.version || s.requirements_version || 1 }))
        .filter((s: any) => s.id);
      setAvailableSpecs(specs);
      setSelectedSpec((prev) => prev || (specs[0] ? specs[0].id : ""));
    } catch {
      /* silencioso */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveProjectId]);

  const loadLatest = useCallback(async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/ui-spec/project/${effectiveProjectId}/latest`, { headers });
      if (r.status === 401 || r.status === 403) {
        setAuthExpired(true);
        toast.error("Sessão expirada. Faça login novamente para ver a UI Spec.");
        return;
      }
      const d: Session = await r.json();
      if (!r.ok) throw new Error((d as any)?.detail || `HTTP ${r.status}`);
      setAuthExpired(false);
      setSession(d);
      if (d.session_id) {
        const rm = await fetch(`${API_BASE}/ui-spec/${d.session_id}/mockups`, { headers });
        const dm = await rm.json();
        setMockups(dm.mockups || {});
        setSelected((prev) => {
          const scr = d.ui_spec?.screens || [];
          if (prev && scr.some((s) => s.id === prev)) return prev;
          return scr[0] ? scr[0].id : null;
        });
        loadChat(d.session_id);
      }
    } catch (e: any) {
      toast.error(`Falha ao carregar UI Spec: ${e.message}`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveProjectId, loadChat]);

  useEffect(() => {
    loadLatest();
    loadSpecs();
  }, [loadLatest, loadSpecs]);

  const generate = async () => {
    if (!effectiveProjectId) {
      toast.error("Nenhum projeto selecionado.");
      return;
    }
    setGenerating(true);
    try {
      // Usa a Especificação selecionada; se nenhuma, auto-descobre a mais recente.
      let specId = selectedSpec;
      if (!specId) {
        const rs = await fetch(`${API_BASE}/specifications/project/${effectiveProjectId}/latest`, { headers }).catch(() => null);
        const specData = rs ? await rs.json() : {};
        specId = specData?.session_id;
      }
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
    const instruction = chatMsg;
    setChatMessages((m) => [...m, { role: "user", content: instruction }]);
    setChatMsg("");
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${session.session_id}/chat`, {
        method: "POST", headers,
        body: JSON.stringify({ content: instruction, screen_id: selected }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      // Atualiza só o mockup da tela refinada, sem recarregar tudo.
      if (d.mockup_update) setMockups((m) => ({ ...m, ...d.mockup_update }));
      if (d.ui_spec) setSession((s) => (s ? { ...s, ui_spec: d.ui_spec } : s));
      const msg = `Tela "${d.refined_screen || selected}" atualizada`;
      setChatMessages((m) => [...m, { role: "assistant", content: msg }]);
      toast.success(msg);
    } catch (e: any) {
      toast.error(`Falha no refino: ${e.message}`);
      setChatMessages((m) => [...m, { role: "assistant", content: `⚠️ ${e.message}` }]);
    } finally {
      setChatSending(false);
    }
  };

  const approve = async () => {
    if (!session?.session_id) return;
    setApproving(true);
    try {
      await fetch(`${API_BASE}/ui-spec/${session.session_id}/approve`, {
        method: "POST", headers, body: JSON.stringify({ approve: true }),
      });
      toast.success("UI Spec aprovada");
      await loadLatest();
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setApproving(false);
    }
  };

  const screens = session?.ui_spec?.screens || [];
  const current = screens.find((s) => s.id === selected) || null;

  // ---- Botões de origem da sidebar: seleção da Especificação de origem ----
  const sourceButtons = (
    <select
      className="tc-src-compact"
      value={selectedSpec}
      onChange={(e) => setSelectedSpec(e.target.value)}
      disabled={generating}
      title="Especificação Funcional de origem (casos de uso + wireframes)"
    >
      {availableSpecs.length === 0 && <option value="">— auto (mais recente) —</option>}
      {availableSpecs.map((s) => (
        <option key={s.id} value={s.id}>
          📋 Spec v{s.version} ({s.id.slice(0, 8)}…)
        </option>
      ))}
    </select>
  );

  const sourceBanner = (
    <div
      style={{
        padding: "8px 12px",
        backgroundColor: "#d4edda",
        borderBottom: "1px solid #c3e6cb",
        fontSize: "12px",
      }}
    >
      <strong>📋 Origem:</strong>{" "}
      {selectedSpec ? `Especificação ${selectedSpec.slice(0, 8)}…` : "Especificação mais recente (auto) + Modelo de Dados"}
    </div>
  );

  // ---- Chat de refino por tela (coluna do meio) ----
  const chatPanel = (
    <div className="tc-chat-panel">
      <div className="tc-chat-panel-header">
        <h2>💬 Refinar tela {current ? `— ${current.name}` : ""}</h2>
      </div>
      <div className="tc-chat-panel-body">
        {!current && (
          <div className="tc-chat-empty">
            <p>Selecione uma tela na galeria para refinar seu mockup.</p>
          </div>
        )}
        {current && (
          <p className="tc-refine-hint">
            Peça ajustes nesta tela (ex.: "adicione um campo telefone", "torne o botão de salvar
            primário"). O agente reajusta a UI Spec, regenera o mockup PNG e o reflete na galeria.
          </p>
        )}
        {chatMessages.length > 0 && (
          <div className="tc-chat-log">
            {chatMessages.map((m, i) => (
              <div key={i} className={`tc-chat-msg ${m.role}`}>
                <span className="tc-chat-role">{m.role === "user" ? "Você" : "Agente"}</span>
                {m.content}
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="tc-chat-input">
        <textarea
          value={chatMsg}
          onChange={(e) => setChatMsg(e.target.value)}
          placeholder={current ? `Refinar "${current.name}"…` : "Selecione uma tela…"}
          rows={2}
          disabled={chatSending || !current}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) sendRefine();
          }}
        />
        <button
          className="tc-btn primary"
          onClick={sendRefine}
          disabled={chatSending || !chatMsg.trim() || !current}
        >
          {chatSending ? "Refinando…" : "Refinar"}
        </button>
      </div>
    </div>
  );

  // ---- Miolo (coluna principal): galeria de mockups ----
  const galleryViewer = (
    <div className="tc-viewer">
      {session && session.session_id && (
        <div className="tc-summary">
          <span className={`tc-badge ${session.status}`}>{session.status}</span>
          <span>Versão <b>v{session.version || 1}</b></span>
          <span><b>{session.screens_count || screens.length}</b> telas</span>
          <div className="tc-summary-actions">
            {session.status !== "approved" && (
              <button className="tc-btn approve" onClick={approve} disabled={approving || generating}>
                {approving ? "…" : "✓ Aprovar"}
              </button>
            )}
          </div>
        </div>
      )}

      {authExpired && (
        <div className="tc-empty tc-auth">
          <p>🔒 <b>Sua sessão expirou.</b></p>
          <p>Faça <b>login novamente</b> para carregar a UI Spec — os dados continuam salvos.</p>
        </div>
      )}

      {!authExpired && (!session || !session.session_id) && (
        <div className="tc-empty">
          <p>Nenhuma UI Spec gerada ainda.</p>
          <p>
            A UI Spec é gerada a partir da Especificação Funcional (casos de uso + wireframes) e do
            Modelo de Dados. Escolha a origem na barra lateral e clique em <b>Gerar</b>.
          </p>
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
    </div>
  );

  // ---- Modal de histórico (placeholder — ui-spec ainda não tem endpoint de versões) ----
  const historyModal = historyOpen ? (
    <div className="tc-modal-overlay" onClick={() => setHistoryOpen(false)}>
      <div className="tc-modal" onClick={(e) => e.stopPropagation()}>
        <div className="tc-modal-head">
          <b>📜 Histórico de versões</b>
          <button className="tc-btn ghost" onClick={() => setHistoryOpen(false)}>Fechar</button>
        </div>
        <div className="tc-modal-body">
          <p>Histórico de versões: em breve.</p>
          <p style={{ color: "#888", fontSize: 12.5 }}>
            O refino por chat já sobe a versão da UI Spec; a navegação entre versões anteriores
            será habilitada em breve.
          </p>
        </div>
      </div>
    </div>
  ) : null;

  return (
    <StagePageLayout
      title="🎨 Interface & Protótipo"
      subtitle="Especificação e protótipo de interface gerados a partir da Especificação Funcional (casos de uso + wireframes) e do Modelo de Dados. Cada tela vira um mockup PNG refinável por chat."
      sidebarTitle="🎨 Telas"
      wideViewer
      sourceButtons={sourceButtons}
      sourceBanner={sourceBanner}
      instructions={instructions}
      onInstructionsChange={setInstructions}
      onGenerate={generate}
      generating={generating}
      generateLabel="⚡ Gerar UI Spec"
      onHistory={() => setHistoryOpen(true)}
      chat={chatPanel}
      modals={historyModal}
    >
      {galleryViewer}
    </StagePageLayout>
  );
};

export default UISpecPage;
