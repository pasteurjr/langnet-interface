import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import DataModelHistoryModal from "../components/datamodel/DataModelHistoryModal";
import StagePageLayout from "../components/stage/StagePageLayout";
import "./DataModelPage.css";

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api";

interface Column {
  name: string;
  type: string;
  pk?: boolean;
  nullable?: boolean;
  default?: string;
  values?: string[];
}
interface Table {
  name: string;
  description?: string;
  columns: Column[];
  indexes?: { name: string; columns: string[]; unique?: boolean }[];
}
interface DataModelSession {
  session_id: string | null;
  status?: string;
  target_dbms?: string;
  version?: number;
  data_model_yaml?: string;
  schema_sql?: string;
  models_py?: string;
  alembic_migration?: string;
  entities_json?: string;
  validation_report?: string;
  message?: string;
}
interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  at: string;
}
interface ViewingVersion {
  version: number;
  change_type?: string;
  change_description?: string;
  created_at?: string;
  data_model_yaml?: string;
  schema_sql?: string;
  models_py?: string;
  alembic_migration?: string;
  entities_json?: string;
  validation_report?: string;
  tables: Table[];
}

type Tab = "entities" | "sql" | "models" | "alembic" | "yaml";

const DataModelPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const effectiveProjectId = projectId || localStorage.getItem("currentProjectId") || "";
  const token = localStorage.getItem("accessToken") || localStorage.getItem("access_token") || "";

  const [session, setSession] = useState<DataModelSession | null>(null);
  const [tables, setTables] = useState<Table[]>([]);
  const [tab, setTab] = useState<Tab>("entities");
  const [dbms, setDbms] = useState("mysql");
  const [generating, setGenerating] = useState(false);
  const [chatMsg, setChatMsg] = useState("");
  const [chatSending, setChatSending] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [availableSpecs, setAvailableSpecs] = useState<{ id: string; version: number }[]>([]);
  const [selectedSpec, setSelectedSpec] = useState<string>("");
  const [instructions, setInstructions] = useState("");
  const [historyOpen, setHistoryOpen] = useState(false);
  const [viewingData, setViewingData] = useState<ViewingVersion | null>(null);
  const [approving, setApproving] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [reviewSuggestions, setReviewSuggestions] = useState<string[] | null>(null);

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
  const viewingPast = viewingData !== null;

  const loadChat = useCallback(async (sessionId: string) => {
    try {
      const r = await fetch(`${API_BASE}/data-model/${sessionId}/chat`, { headers });
      const d = await r.json();
      setChatHistory(d.messages || []);
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadLatest = useCallback(async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/data-model/project/${effectiveProjectId}/latest`, { headers });
      if (r.status === 401) {
        toast.error("Sua sessão expirou. Faça login novamente.");
        localStorage.clear();
        setTimeout(() => (window.location.href = "/login"), 800);
        return;
      }
      const d: DataModelSession = await r.json();
      setSession(d);
      if (d.entities_json) {
        try {
          const parsed = JSON.parse(d.entities_json);
          setTables(parsed.tables || []);
        } catch {
          setTables([]);
        }
      }
      if (d.session_id) loadChat(d.session_id);
    } catch (e) {
      console.error(e);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveProjectId, token, loadChat]);

  const loadSpecs = useCallback(async () => {
    if (!effectiveProjectId) return;
    try {
      const r = await fetch(`${API_BASE}/specifications/?project_id=${effectiveProjectId}`, { headers });
      const d = await r.json();
      const rows = Array.isArray(d) ? d : (d.sessions || d.specifications || d.results || d.items || []);
      const list = rows.map((s: any) => ({
        id: s.id,
        version: s.version || s.requirements_version || 1,
      }));
      setAvailableSpecs(list);
      if (list.length > 0) setSelectedSpec((prev) => prev || list[0].id);
    } catch (e) {
      // fallback: pega a mais recente diretamente
      console.warn("Fallback: buscando specification session_id do projeto…", e);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effectiveProjectId, token]);

  useEffect(() => {
    loadLatest();
    loadSpecs();
  }, [loadLatest, loadSpecs]);

  const handleGenerate = async () => {
    if (!selectedSpec) {
      toast.error("Selecione uma especificação primeiro.");
      return;
    }
    setGenerating(true);
    try {
      const r = await fetch(`${API_BASE}/data-model/${effectiveProjectId}/generate`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          specification_session_id: selectedSpec,
          target_dbms: dbms,
          instructions: instructions || undefined,
        }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
      const d = await r.json();
      toast.success("Modelo de Dados gerado!");
      setSession(d);
      if (d.entities_json) {
        try {
          const parsed = JSON.parse(d.entities_json);
          setTables(parsed.tables || []);
        } catch {}
      }
    } catch (e: any) {
      toast.error(`Erro: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async () => {
    if (!session?.session_id) return;
    setApproving(true);
    try {
      const r = await fetch(`${API_BASE}/data-model/${session.session_id}/approve`, {
        method: "POST",
        headers,
        body: JSON.stringify({ approve: true }),
      });
      if (r.ok) {
        toast.success("Aprovado!");
        loadLatest();
      }
    } finally {
      setApproving(false);
    }
  };

  const review = async () => {
    if (!session?.session_id) {
      toast.error("Gere o Modelo de Dados antes de revisar.");
      return;
    }
    setReviewing(true);
    try {
      const r = await fetch(`${API_BASE}/data-model/${session.session_id}/review`, {
        method: "POST",
        headers,
        body: JSON.stringify({}),
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d?.detail || `HTTP ${r.status}`);
      const sugs: string[] = Array.isArray(d.suggestions)
        ? d.suggestions.map((s: any) => (typeof s === "string" ? s : s.text || s.description || JSON.stringify(s)))
        : d.suggestions
        ? [String(d.suggestions)]
        : [];
      setReviewSuggestions(sugs);
      toast.success(`Revisão concluída: ${sugs.length} sugestão(ões).`);
    } catch (e: any) {
      toast.error(`Falha na revisão: ${e.message}`);
    } finally {
      setReviewing(false);
    }
  };

  const handleChatSend = async () => {
    if (!session?.session_id || !chatMsg.trim()) return;
    setChatSending(true);
    const messageText = chatMsg;
    setChatMsg("");
    setChatHistory((h) => [...h, { role: "user", content: messageText, at: new Date().toISOString() }]);
    try {
      const r = await fetch(`${API_BASE}/data-model/${session.session_id}/chat`, {
        method: "POST",
        headers,
        body: JSON.stringify({ content: messageText, target_dbms: session.target_dbms || dbms }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      setSession((s) => (s ? { ...s, ...d } : d));
      if (d.entities_json) {
        try {
          setTables(JSON.parse(d.entities_json).tables || []);
        } catch {}
      }
      setChatHistory((h) => [...h, { role: "assistant", content: "Modelo atualizado.", at: new Date().toISOString() }]);
    } catch (e: any) {
      toast.error(`Erro no refino: ${e.message}`);
    } finally {
      setChatSending(false);
    }
  };

  const loadVersion = async (version: number) => {
    if (!session?.session_id) return;
    try {
      const r = await fetch(`${API_BASE}/data-model/${session.session_id}/versions/${version}`, { headers });
      if (r.status === 401) {
        toast.error("Sua sessão expirou. Faça login novamente.");
        localStorage.clear();
        setTimeout(() => (window.location.href = "/login"), 800);
        return;
      }
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      let vtables: Table[] = [];
      if (d.entities_json) {
        try {
          vtables = JSON.parse(d.entities_json).tables || [];
        } catch {
          vtables = [];
        }
      }
      setViewingData({
        version: d.version ?? version,
        change_type: d.change_type,
        change_description: d.change_description,
        created_at: d.created_at,
        data_model_yaml: d.data_model_yaml,
        schema_sql: d.schema_sql,
        models_py: d.models_py,
        alembic_migration: d.alembic_migration,
        entities_json: d.entities_json,
        validation_report: d.validation_report,
        tables: vtables,
      });
    } catch (e: any) {
      toast.error(`Falha ao carregar versão: ${e.message}`);
    }
  };

  const backToCurrent = () => {
    setViewingData(null);
  };

  // Artefatos exibidos: versão passada (somente leitura) OU sessão ao vivo
  const displayTables = viewingPast ? viewingData!.tables : tables;
  const displaySchemaSql = viewingPast ? viewingData!.schema_sql : session?.schema_sql;
  const displayModelsPy = viewingPast ? viewingData!.models_py : session?.models_py;
  const displayAlembic = viewingPast ? viewingData!.alembic_migration : session?.alembic_migration;
  const displayYaml = viewingPast ? viewingData!.data_model_yaml : session?.data_model_yaml;

  const renderValidation = () => {
    if (!session?.validation_report) return null;
    try {
      const v = JSON.parse(session.validation_report);
      if (!v.issues || v.issues.length === 0) return null;
      return (
        <div className="dm-validation">
          <strong>⚠️ Validação (score {v.score}/100) — {v.issues.length} problemas</strong>
          <ul style={{ margin: 4, paddingLeft: 16 }}>
            {v.issues.slice(0, 5).map((i: any, k: number) => (
              <li key={k}><strong>[{i.severity}]</strong> {i.table}: {i.issue}</li>
            ))}
          </ul>
        </div>
      );
    } catch {
      return null;
    }
  };

  // ---- Seleção da Especificação de origem (barra lateral) ----
  const sourceButtons = (
    <select
      className="tc-src-compact"
      value={selectedSpec}
      onChange={(e) => setSelectedSpec(e.target.value)}
      disabled={generating}
      title="Especificação de origem"
    >
      {availableSpecs.length === 0 && <option value="">— nenhuma Especificação —</option>}
      {availableSpecs.map((s) => (
        <option key={s.id} value={s.id}>
          📋 Spec v{s.version} ({s.id.slice(0, 8)}…)
        </option>
      ))}
    </select>
  );

  const sourceBanner = selectedSpec ? (
    <div
      style={{
        padding: "8px 12px",
        backgroundColor: "#d4edda",
        borderBottom: "1px solid #c3e6cb",
        fontSize: "12px",
      }}
    >
      <strong>📋 Origem:</strong> Especificação {selectedSpec.slice(0, 8)}…
    </div>
  ) : null;

  // ---- Configuração extra: banco de dados alvo ----
  const configExtras = (
    <div style={{ marginBottom: 10 }}>
      <label>Banco de dados (DBMS)</label>
      <select
        value={session?.session_id ? session.target_dbms || dbms : dbms}
        onChange={(e) => setDbms(e.target.value)}
        disabled={generating || viewingPast}
        style={{ width: "100%", padding: "8px 10px", border: "1px solid #d1d5db", borderRadius: 6, fontSize: 14 }}
      >
        <option value="mysql">MySQL</option>
        <option value="postgresql">PostgreSQL</option>
        <option value="sqlite">SQLite</option>
      </select>
    </div>
  );

  // ---- Chat de refino (coluna do meio) ----
  const chatPanel = (
    <div className="dm-chat">
      <h3>💬 Refinar via chat</h3>
      <div className="dm-chat-messages">
        {!session?.session_id && (
          <div style={{ color: "#94a3b8", fontSize: 12, textAlign: "center", padding: 20 }}>
            Gere o Modelo de Dados para refiná-lo por chat.
          </div>
        )}
        {session?.session_id && chatHistory.length === 0 && (
          <div style={{ color: "#94a3b8", fontSize: 12, textAlign: "center", padding: 20 }}>
            Peça mudanças: "adicione tabela X", "coloque índice em Y", "remova campo Z"…
          </div>
        )}
        {chatHistory.map((m, k) => (
          <div key={k} className={`dm-msg dm-msg-${m.role}`}>{m.content}</div>
        ))}
        {chatSending && <div className="dm-msg dm-msg-assistant">…refinando…</div>}
      </div>
      <div className="dm-chat-input">
        <input
          value={chatMsg}
          onChange={(e) => setChatMsg(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !chatSending && handleChatSend()}
          placeholder="Ex: adicione tabela comentarios"
          disabled={chatSending || !session?.session_id || viewingPast}
        />
        <button
          onClick={handleChatSend}
          disabled={chatSending || !chatMsg.trim() || !session?.session_id || viewingPast}
        >
          Enviar
        </button>
      </div>
    </div>
  );

  // ---- Miolo (coluna principal): visualizador em abas ----
  const viewer = (
    <div className="dm-viewer">
      {session?.session_id && (
        <div className="dm-summary">
          <span className={`status-pill dm-status-${session.status}`}>
            {session.status === "approved" ? "✓ Aprovado" : "📝 Rascunho"}
          </span>
          <span>Versão <b>v{session.version}</b></span>
          <span>DBMS <b>{(session.target_dbms || "").toUpperCase()}</b></span>
          <span><b>{tables.length}</b> tabelas</span>
          <div className="dm-summary-actions">
            {session.status !== "approved" && (
              <button className="dm-btn-approve" onClick={handleApprove} disabled={approving || generating || viewingPast}>
                {approving ? "…" : "✓ Aprovar"}
              </button>
            )}
          </div>
        </div>
      )}

      {viewingPast && (
        <div className="dm-viewing-banner">
          <span>🕘 Visualizando versão <b>{viewingData!.version}</b> (somente leitura)</span>
          <button className="dm-btn-ghost" onClick={backToCurrent}>Voltar à versão atual</button>
        </div>
      )}

      {reviewSuggestions && (
        <div className="tc-review-panel">
          <div className="tc-review-head">
            <b>🔍 Sugestões de revisão ({reviewSuggestions.length})</b>
            <button className="dm-btn-ghost" onClick={() => setReviewSuggestions(null)}>Fechar</button>
          </div>
          {reviewSuggestions.length === 0 ? (
            <p>Nenhuma sugestão — o modelo de dados parece consistente.</p>
          ) : (
            <ul>
              {reviewSuggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {renderValidation()}

      {!session?.session_id ? (
        <div className="dm-empty">
          <div>
            <h2>Nenhum Modelo de Dados ainda</h2>
            <p>Selecione uma especificação de origem na barra lateral e clique em "Gerar Modelo de Dados"
              para extrair entidades, criar schema SQL, models.py e migrations Alembic automaticamente.</p>
          </div>
        </div>
      ) : (
        <div className="dm-tabs-container">
          <div className="dm-tabs">
            <button className={`dm-tab ${tab === "entities" ? "active" : ""}`} onClick={() => setTab("entities")}>Entidades</button>
            <button className={`dm-tab ${tab === "sql" ? "active" : ""}`} onClick={() => setTab("sql")}>Schema SQL</button>
            <button className={`dm-tab ${tab === "models" ? "active" : ""}`} onClick={() => setTab("models")}>models.py</button>
            <button className={`dm-tab ${tab === "alembic" ? "active" : ""}`} onClick={() => setTab("alembic")}>Alembic</button>
            <button className={`dm-tab ${tab === "yaml" ? "active" : ""}`} onClick={() => setTab("yaml")}>YAML</button>
          </div>
          <div className="dm-tab-body">
            {tab === "entities" && (
              <div className="dm-tables-list">
                {displayTables.length === 0 && <div className="dm-loading">Nenhuma tabela extraída ainda.</div>}
                {displayTables.map((t) => (
                  <div key={t.name} className="dm-table-card">
                    <h3>📊 {t.name}</h3>
                    {t.description && <div style={{ color: "#64748b", fontSize: 12, marginBottom: 6 }}>{t.description}</div>}
                    <div className="dm-columns">
                      {(t.columns || []).map((c) => (
                        <div key={c.name} className="col-row">
                          <span className="col-name">
                            {c.pk && "🔑 "}{c.name}
                          </span>
                          <span className="col-type">{c.type}</span>
                          <span className="col-flags">
                            {c.nullable === false && "NN "}
                            {c.default && "DEF"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {tab === "sql" && <pre>{displaySchemaSql || "—"}</pre>}
            {tab === "models" && <pre>{displayModelsPy || "—"}</pre>}
            {tab === "alembic" && <pre>{displayAlembic || "—"}</pre>}
            {tab === "yaml" && <pre>{displayYaml || "—"}</pre>}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <StagePageLayout
      title="🗄️ Modelo de Dados"
      subtitle="Gera schema SQL, models.py (SQLAlchemy+Pydantic) e migrations Alembic a partir da especificação. Extrai entidades e relacionamentos automaticamente."
      sidebarTitle="📋 Especificação"
      wideViewer
      sourceButtons={sourceButtons}
      sourceBanner={sourceBanner}
      configExtras={configExtras}
      instructions={instructions}
      onInstructionsChange={setInstructions}
      onGenerate={handleGenerate}
      generating={generating}
      generateLabel={session?.session_id ? "↻ Regenerar do zero" : "▶ Gerar Modelo de Dados"}
      canGenerate={!!selectedSpec && !viewingPast}
      onReview={review}
      reviewing={reviewing}
      canReview={!!session?.session_id && !generating}
      onHistory={() => setHistoryOpen(true)}
      chat={chatPanel}
      modals={
        <DataModelHistoryModal
          isOpen={historyOpen}
          onClose={() => setHistoryOpen(false)}
          sessionId={session?.session_id || null}
          currentVersion={session?.version}
          onSelectVersion={loadVersion}
        />
      }
    >
      {viewer}
    </StagePageLayout>
  );
};

export default DataModelPage;
