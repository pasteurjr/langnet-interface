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
interface ScreenSource {
  screen_id: string;
  uc_id?: string | null;
  spec_session_id?: string;
  spec_version_used?: number | null;
  spec_version_current?: number | null;
  stale?: boolean;
  found?: boolean;
  actor?: string | null;
  objetivo?: string | null;
  screen_title?: string | null;
  flow?: string | null;
  wireframe?: string | null;
}
interface CoherenceFix {
  action: string;
  to?: string;
  label: string;
  table?: string;
  column?: string;
  sql_type?: string;
  new_table?: boolean;
}
interface CoherenceIssue {
  type: string;
  severity: string;
  detail: string;
  bindTo?: string;
  proposed_fixes: CoherenceFix[];
}
interface CoherenceScreen {
  screen_id: string;
  screen_name: string;
  uc_id?: string | null;
  kind?: string;
  layout?: string;
  entity?: string | null;
  issues: CoherenceIssue[];
  ok: boolean;
}
interface DMChange {
  table: string;
  column: string;
  sql_type: string;
  new_table: boolean;
  screens: string[];
}
interface CoherenceReport {
  summary: {
    screens: number;
    screens_with_issues: number;
    broken_binds: number;
    total_binds: number;
    kind_mismatches: number;
    proposed_dm_changes: number;
  };
  screens: CoherenceScreen[];
  proposed_dm_changes: DMChange[];
}

const UISpecPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const effectiveProjectId = projectId || localStorage.getItem("currentProjectId") || "";
  const token = localStorage.getItem("accessToken") || localStorage.getItem("access_token") || "";
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const [session, setSession] = useState<Session | null>(null);
  const [mockups, setMockups] = useState<Record<string, string>>({});
  // ── PROTÓTIPO (Fase 3): o protótipo React roda DENTRO da etapa, num quadro embutido.
  // Não é imagem: é o aplicativo com a fonte de dados trocada, navegável aqui mesmo.
  const [protoUrl, setProtoUrl] = useState<string>("");
  const [protoInfo, setProtoInfo] = useState<{ telas?: number; bytes?: number } | null>(null);
  const [protoBusy, setProtoBusy] = useState(false);
  const [protoErr, setProtoErr] = useState<string>("");
  // Alvo apontado DENTRO do protótipo: vai junto com a instrução para o agente, para ele saber
  // de que tela e de que componente se está falando (antes ia só o texto).
  const [apontando, setApontando] = useState(false);
  const [alvo, setAlvo] = useState<{ tela?: string; rotulo?: string; campo?: string } | null>(null);
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
  // AMARRAÇÃO Spec⟷Protótipo: origem (UC) da tela selecionada + edição da interação.
  const [source, setSource] = useState<ScreenSource | null>(null);
  const [sourceLoading, setSourceLoading] = useState(false);
  const [editingSource, setEditingSource] = useState(false);
  const [editFlow, setEditFlow] = useState("");
  const [editWireframe, setEditWireframe] = useState("");
  const [savingSource, setSavingSource] = useState(false);
  const [resyncing, setResyncing] = useState(false);
  // Contrato de coerência UC ⟷ Mockup ⟷ Modelo de Dados.
  const [coherence, setCoherence] = useState<CoherenceReport | null>(null);
  const [cohLoading, setCohLoading] = useState(false);
  const [applyingDm, setApplyingDm] = useState(false);
  const [dmSel, setDmSel] = useState<Record<string, boolean>>({});

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

  // Mensagens vindas do protótipo embutido (tela aberta / componente apontado).
  useEffect(() => {
    const ouvir = (ev: MessageEvent) => {
      const m: any = ev.data || {};
      if (m.origem !== "prototipo-langnet") return;
      if (m.tipo === "tela") setAlvo((a) => ({ ...(a || {}), tela: m.tela }));
      if (m.tipo === "componente") {
        setAlvo({ tela: m.tela, rotulo: m.rotulo, campo: m.campo });
        setApontando(false);
      }
    };
    window.addEventListener("message", ouvir);
    return () => window.removeEventListener("message", ouvir);
  }, []);

  const alternarApontar = () => {
    const q = document.querySelector('iframe[title="protótipo"]') as HTMLIFrameElement | null;
    const lig = !apontando;
    setApontando(lig);
    q?.contentWindow?.postMessage({ origem: "etapa-langnet", tipo: "apontar", ligado: lig }, "*");
  };

  // Protótipo já montado desta versão, se houver — abre junto com a etapa.
  useEffect(() => { carregarPrototipo(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [effectiveProjectId]);

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
        // O agente recebe a instrução JUNTO com a tela aberta e o componente apontado no
        // protótipo — sem isso ele precisa adivinhar de que tela se fala.
        body: JSON.stringify({
          content: alvo?.rotulo
            ? `Na tela "${alvo.tela}", no componente "${alvo.rotulo}"${alvo.campo ? ` (campo ${alvo.campo})` : ""}: ${instruction}`
            : instruction,
          screen_id: selected,
        }),
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

  // ── AMARRAÇÃO: carrega a origem (UC) da tela selecionada ──
  const loadSource = useCallback(async (sid: string, screenId: string) => {
    setSourceLoading(true);
    setEditingSource(false);
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${sid}/screen/${screenId}/source`, { headers });
      if (!r.ok) { setSource(null); return; }
      const d: ScreenSource = await r.json();
      setSource(d);
      setEditFlow(d.flow || "");
      setEditWireframe(d.wireframe || "");
    } catch {
      setSource(null);
    } finally {
      setSourceLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Recarrega a origem quando muda a tela selecionada ou a sessão.
  useEffect(() => {
    if (session?.session_id && selected) loadSource(session.session_id, selected);
    else setSource(null);
  }, [session?.session_id, selected, loadSource]);

  const applyUpdate = (d: any) => {
    if (d.mockup_update) setMockups((m) => ({ ...m, ...d.mockup_update }));
    if (d.ui_spec) setSession((s) => (s ? { ...s, ui_spec: d.ui_spec } : s));
  };

  // Salva a interação editada NO SPEC (nova versão) e regenera só esta tela.
  const saveSource = async () => {
    if (!session?.session_id || !selected) return;
    setSavingSource(true);
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${session.session_id}/screen/${selected}/edit-source`, {
        method: "POST", headers,
        body: JSON.stringify({ flow: editFlow, wireframe: editWireframe, screen_title: source?.screen_title }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      applyUpdate(d);
      toast.success(`Interação salva no spec (v${d.new_spec_version}) e tela regenerada`);
      setEditingSource(false);
      loadSource(session.session_id, selected);
    } catch (e: any) {
      toast.error(`Falha ao salvar/propagar: ${e.message}`);
    } finally {
      setSavingSource(false);
    }
  };

  // Re-sincroniza a tela com o spec atual (quando o spec mudou em outra etapa).
  const resync = async () => {
    if (!session?.session_id || !selected) return;
    setResyncing(true);
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${session.session_id}/screen/${selected}/resync`, {
        method: "POST", headers,
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      applyUpdate(d);
      toast.success("Tela re-sincronizada com a Especificação atual");
      loadSource(session.session_id, selected);
    } catch (e: any) {
      toast.error(`Falha ao re-sincronizar: ${e.message}`);
    } finally {
      setResyncing(false);
    }
  };

  // ── Contrato de coerência: relatório + reconciliação ──
  const loadCoherence = useCallback(async (sid: string) => {
    setCohLoading(true);
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${sid}/coherence`, { headers });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d: CoherenceReport = await r.json();
      setCoherence(d);
      // por padrão, marca todas as mudanças propostas
      const sel: Record<string, boolean> = {};
      (d.proposed_dm_changes || []).forEach((c) => { sel[`${c.table}.${c.column}`] = true; });
      setDmSel(sel);
    } catch (e: any) {
      toast.error(`Falha ao verificar coerência: ${e.message}`);
    } finally {
      setCohLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const applyDm = async () => {
    if (!session?.session_id || !coherence) return;
    const changes = (coherence.proposed_dm_changes || []).filter((c) => dmSel[`${c.table}.${c.column}`]);
    if (changes.length === 0) { toast.info("Nenhuma mudança selecionada."); return; }
    setApplyingDm(true);
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${session.session_id}/apply-dm-changes`, {
        method: "POST", headers, body: JSON.stringify({ changes }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      toast.success(`Modelo de Dados atualizado (v${d.new_data_model_version}) — ${(d.applied || []).length} adição(ões)`);
      await loadCoherence(session.session_id);
    } catch (e: any) {
      toast.error(`Falha ao aplicar no Modelo de Dados: ${e.message}`);
    } finally {
      setApplyingDm(false);
    }
  };

  const doRebind = async (screenId: string, bindOld: string, bindNew: string) => {
    if (!session?.session_id) return;
    try {
      const r = await fetch(`${API_BASE}/ui-spec/${session.session_id}/screen/${screenId}/rebind`, {
        method: "POST", headers, body: JSON.stringify({ screen_id: screenId, bind_old: bindOld, bind_new: bindNew }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      if (d.ui_spec) setSession((s) => (s ? { ...s, ui_spec: d.ui_spec } : s));
      toast.success(`Religado para ${bindNew}`);
      await loadCoherence(session.session_id);
    } catch (e: any) {
      toast.error(`Falha ao religar: ${e.message}`);
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

  const raizApi = API_BASE.replace(/\/api\/?$/, "");

  const carregarPrototipo = async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/prototype/project/${effectiveProjectId}/latest`, { headers });
      if (!r.ok) return;
      const d = await r.json();
      setProtoUrl(`${raizApi}${d.url}`);
      setProtoInfo({ bytes: d.bytes });
    } catch (e) { /* protótipo ainda não montado */ }
  };

  const gerarPrototipo = async () => {
    if (!effectiveProjectId) return;
    setProtoBusy(true); setProtoErr("");
    try {
      const r = await fetch(`${API_BASE}/prototype/${effectiveProjectId}/generate`, {
        method: "POST", headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "falha ao montar o protótipo");
      setProtoUrl(`${raizApi}${d.url}?t=${Date.now()}`);
      setProtoInfo({ telas: d.telas, bytes: d.bytes });
    } catch (e: any) { setProtoErr(String(e.message || e)); }
    setProtoBusy(false);
  };

  // ---- Miolo (coluna principal): galeria de mockups ----
  const galleryViewer = (
    <div className="tc-viewer">
      {session && session.session_id && (
        <div className="tc-summary">
          <span className={`tc-badge ${session.status}`}>{session.status}</span>
          <span>Versão <b>v{session.version || 1}</b></span>
          <span><b>{session.screens_count || screens.length}</b> telas</span>
          <div className="tc-summary-actions">
            <button
              className="tc-btn"
              onClick={gerarPrototipo}
              disabled={protoBusy || generating}
              title="Monta o protótipo React desta versão e abre aqui dentro, com dados fictícios do Modelo de Dados"
            >
              {protoBusy ? "Montando…" : "🧪 Protótipo"}
            </button>
            <button
              className="tc-btn"
              onClick={() => session.session_id && loadCoherence(session.session_id)}
              disabled={cohLoading || generating}
              title="Cruza casos de uso × mockups × Modelo de Dados e aponta divergências"
            >
              {cohLoading ? "Verificando…" : "🔎 Verificar coerência"}
            </button>
            {session.status !== "approved" && (
              <button className="tc-btn approve" onClick={approve} disabled={approving || generating}>
                {approving ? "…" : "✓ Aprovar"}
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── PROTÓTIPO EMBUTIDO: o aplicativo com a fonte de dados trocada, navegável aqui ── */}
      {(protoUrl || protoErr) && (
        <div className="uispec-proto">
          <div className="uispec-proto-head">
            <b>Protótipo navegável</b>
            <span className="uispec-proto-nota">
              mesmas telas do aplicativo · dados fictícios do Modelo de Dados
            </span>
            {protoInfo?.telas ? <span>{protoInfo.telas} telas</span> : null}
            {protoUrl && (
              <button
                className={`tc-btn ${apontando ? "apontando" : ""}`}
                onClick={alternarApontar}
                title="Clique num componente do protótipo para falar com o agente sobre ele"
              >
                {apontando ? "🎯 clique no componente…" : "🎯 Apontar componente"}
              </button>
            )}
            {alvo?.rotulo && (
              <span className="uispec-proto-alvo">
                alvo: <b>{alvo.rotulo}</b>{alvo.tela ? ` · ${alvo.tela}` : ""}
                <button className="uispec-proto-limpar" onClick={() => setAlvo(null)} title="limpar alvo">×</button>
              </span>
            )}
            {protoUrl && (
              <a href={protoUrl} target="_blank" rel="noreferrer" className="tc-btn">
                Abrir em outra aba ↗
              </a>
            )}
          </div>
          {protoErr ? (
            <div className="uispec-proto-erro">⚠ {protoErr}</div>
          ) : (
            <iframe title="protótipo" src={protoUrl} className="uispec-proto-quadro" />
          )}
        </div>
      )}

      {coherence && (
        <div className="coh-panel">
          <div className="coh-head">
            <b>🔎 Coerência UC ⟷ Mockup ⟷ Modelo de Dados</b>
            <button className="tc-btn ghost" onClick={() => setCoherence(null)}>Fechar</button>
          </div>
          <div className="coh-summary">
            <span className={coherence.summary.broken_binds ? "coh-bad" : "coh-ok"}>
              {coherence.summary.broken_binds}/{coherence.summary.total_binds} vínculos quebrados
            </span>
            <span className={coherence.summary.kind_mismatches ? "coh-warn" : "coh-ok"}>
              {coherence.summary.kind_mismatches} tipo(s) de tela incompatível(is)
            </span>
            <span className={coherence.summary.screens_with_issues ? "coh-warn" : "coh-ok"}>
              {coherence.summary.screens_with_issues}/{coherence.summary.screens} telas com pendência
            </span>
          </div>

          {coherence.proposed_dm_changes.length > 0 && (
            <div className="coh-dm">
              <div className="coh-dm-title">
                📦 Mudanças propostas ao <b>Modelo de Dados</b> (você aprova) — o mockup pede
                campos/tabelas que o banco não tem:
              </div>
              {coherence.proposed_dm_changes.map((c) => {
                const key = `${c.table}.${c.column}`;
                return (
                  <label key={key} className="coh-dm-row">
                    <input
                      type="checkbox"
                      checked={!!dmSel[key]}
                      onChange={(e) => setDmSel((s) => ({ ...s, [key]: e.target.checked }))}
                    />
                    <span className={c.new_table ? "coh-chip coh-chip-new" : "coh-chip"}>
                      {c.new_table ? "NOVA TABELA" : "nova coluna"}
                    </span>
                    <code>{c.table}.{c.column}</code>
                    <span className="coh-type">{c.sql_type}</span>
                    <span className="coh-screens">({c.screens.length} tela)</span>
                  </label>
                );
              })}
              <div className="coh-dm-actions">
                <button className="tc-btn primary" onClick={applyDm} disabled={applyingDm}>
                  {applyingDm ? "Aplicando…" : "✔ Aplicar no Modelo de Dados (nova versão)"}
                </button>
                <span className="coh-hint">
                  Só adiciona (nunca altera/remove). Se o nome for engano, prefira <b>religar</b> abaixo.
                </span>
              </div>
            </div>
          )}

          <div className="coh-screens">
            {coherence.screens.filter((s) => !s.ok).map((s) => (
              <div key={s.screen_id} className="coh-screen">
                <div className="coh-screen-head">
                  <b>{s.screen_name}</b>
                  <span className="coh-meta">{s.uc_id} · tipo={s.kind} · mockup={s.layout}</span>
                </div>
                {s.issues.map((iss, i) => (
                  <div key={i} className={`coh-issue ${iss.severity}`}>
                    <span className="coh-issue-detail">{iss.detail}</span>
                    <span className="coh-fixes">
                      {iss.proposed_fixes.filter((f) => f.action === "rebind_column" || f.action === "rebind_table").map((f, j) => (
                        <button
                          key={j}
                          className="tc-btn tiny"
                          onClick={() => iss.bindTo && f.to && doRebind(s.screen_id, iss.bindTo, f.to)}
                          title={f.label}
                        >
                          🔗 religar → {f.to}
                        </button>
                      ))}
                      {iss.type === "kind_mismatch" && (
                        <span className="coh-note">→ regenere a tela ou ajuste a interação no spec</span>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            ))}
            {coherence.summary.screens_with_issues === 0 && (
              <div className="coh-allok">✓ Todas as telas coerentes com o Modelo de Dados e com os casos de uso.</div>
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

                {/* ── AMARRAÇÃO Spec ⟷ Protótipo ── */}
                <div className="uispec-source">
                  <div className="uispec-source-head">
                    <h4>🔗 Origem na Especificação</h4>
                    {source?.uc_id && (
                      <span className="uispec-prov">
                        gerado de <b>{source.uc_id}</b>
                        {source.spec_version_used != null ? ` · Especificação v${source.spec_version_used}` : ""}
                      </span>
                    )}
                  </div>

                  {sourceLoading && <div className="uispec-nomock">Carregando origem…</div>}

                  {!sourceLoading && source && !source.found && (
                    <div className="uispec-nomock">
                      Não foi possível localizar o caso de uso de origem ({source.uc_id || "sem UC"}) na Especificação.
                    </div>
                  )}

                  {!sourceLoading && source?.stale && (
                    <div className="uispec-stale">
                      ⚠️ A Especificação foi atualizada (v{source.spec_version_current} &gt; v{source.spec_version_used}).
                      Esta tela pode estar desatualizada.
                      <button className="tc-btn" onClick={resync} disabled={resyncing}>
                        {resyncing ? "Re-sincronizando…" : "🔄 Re-sincronizar com o spec"}
                      </button>
                    </div>
                  )}

                  {!sourceLoading && source?.found && (
                    <>
                      <p className="uispec-source-hint">
                        Edite aqui a <b>interação da tela no caso de uso</b> (fluxo de eventos e o
                        esquema/wireframe). Ao salvar, a mudança vira uma <b>nova versão da Especificação</b> e
                        esta tela do protótipo é <b>regenerada</b> a partir dela.
                      </p>

                      {!editingSource ? (
                        <>
                          <div className="uispec-source-block">
                            <div className="uispec-source-label">Fluxo de eventos (ator → sistema)</div>
                            <pre className="uispec-source-pre">{source.flow || "(sem fluxo)"}</pre>
                          </div>
                          <div className="uispec-source-block">
                            <div className="uispec-source-label">Esquema da tela (wireframe)</div>
                            <pre className="uispec-source-pre uispec-wf">{source.wireframe || "(sem wireframe)"}</pre>
                          </div>
                          <button
                            className="tc-btn primary"
                            onClick={() => { setEditFlow(source.flow || ""); setEditWireframe(source.wireframe || ""); setEditingSource(true); }}
                          >
                            ✏️ Editar interação no spec
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="uispec-source-block">
                            <div className="uispec-source-label">Fluxo de eventos (ator → sistema)</div>
                            <textarea
                              className="uispec-source-edit"
                              rows={8}
                              value={editFlow}
                              onChange={(e) => setEditFlow(e.target.value)}
                            />
                          </div>
                          <div className="uispec-source-block">
                            <div className="uispec-source-label">Esquema da tela (wireframe)</div>
                            <textarea
                              className="uispec-source-edit uispec-wf"
                              rows={10}
                              value={editWireframe}
                              onChange={(e) => setEditWireframe(e.target.value)}
                            />
                          </div>
                          <div className="uispec-source-actions">
                            <button className="tc-btn primary" onClick={saveSource} disabled={savingSource}>
                              {savingSource ? "Salvando e regenerando…" : "💾 Salvar no spec e regenerar tela"}
                            </button>
                            <button className="tc-btn ghost" onClick={() => setEditingSource(false)} disabled={savingSource}>
                              Cancelar
                            </button>
                          </div>
                        </>
                      )}
                    </>
                  )}
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
