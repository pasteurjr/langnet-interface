import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
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

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

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
  }, [effectiveProjectId, token]);

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
      if (list.length > 0) setSelectedSpec(list[0].id);
    } catch (e) {
      // fallback: pega a mais recente diretamente
      console.warn("Fallback: buscando specification session_id do projeto…", e);
    }
  }, [effectiveProjectId, token]);

  const loadChat = async (sessionId: string) => {
    try {
      const r = await fetch(`${API_BASE}/data-model/${sessionId}/chat`, { headers });
      const d = await r.json();
      setChatHistory(d.messages || []);
    } catch {}
  };

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
        body: JSON.stringify({ specification_session_id: selectedSpec, target_dbms: dbms }),
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
    const r = await fetch(`${API_BASE}/data-model/${session.session_id}/approve`, {
      method: "POST",
      headers,
      body: JSON.stringify({ approve: true }),
    });
    if (r.ok) {
      toast.success("Aprovado!");
      loadLatest();
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
      setSession({ ...session, ...d });
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

  return (
    <div className="dm-page">
      <div className="dm-header">
        <div>
          <h1>🗄️ Modelo de Dados</h1>
          <div style={{ color: "#64748b", fontSize: 13, marginTop: 4 }}>
            Gera schema SQL, models.py (SQLAlchemy+Pydantic) e migrations Alembic a partir da especificação.
          </div>
        </div>
        {session?.session_id && (
          <div>
            <span className={`status-pill dm-status-${session.status}`}>
              {session.status === "approved" ? "✓ Aprovado" : "📝 Rascunho"}
            </span>
            <span style={{ marginLeft: 8, color: "#64748b", fontSize: 12 }}>
              v{session.version} · {(session.target_dbms || "").toUpperCase()}
            </span>
          </div>
        )}
      </div>

      <div className="dm-toolbar">
        {!session?.session_id ? (
          <>
            <label>Especificação:</label>
            <select value={selectedSpec} onChange={(e) => setSelectedSpec(e.target.value)}>
              {availableSpecs.length === 0 && <option value="">— nenhuma disponível —</option>}
              {availableSpecs.map((s) => (
                <option key={s.id} value={s.id}>Spec v{s.version} ({s.id.slice(0, 8)}…)</option>
              ))}
            </select>
            <label>Banco:</label>
            <select value={dbms} onChange={(e) => setDbms(e.target.value)}>
              <option value="mysql">MySQL</option>
              <option value="postgresql">PostgreSQL</option>
              <option value="sqlite">SQLite</option>
            </select>
            <button className="dm-btn-primary" onClick={handleGenerate} disabled={generating || !selectedSpec}>
              {generating ? "Gerando…" : "▶ Gerar Modelo de Dados"}
            </button>
          </>
        ) : (
          <>
            <span>DBMS: <strong>{(session.target_dbms || "").toUpperCase()}</strong></span>
            <span>Tabelas: <strong>{tables.length}</strong></span>
            <span>Versão: <strong>v{session.version}</strong></span>
            <button className="dm-btn-primary" onClick={handleGenerate} disabled={generating}>
              {generating ? "Regenerando…" : "↻ Regenerar do zero"}
            </button>
            {session.status !== "approved" && (
              <button className="dm-btn-approve" onClick={handleApprove}>✓ Aprovar</button>
            )}
          </>
        )}
      </div>

      {renderValidation()}

      {!session?.session_id ? (
        <div className="dm-empty">
          <div>
            <h2>Nenhum Modelo de Dados ainda</h2>
            <p>Selecione uma especificação existente e clique em "Gerar Modelo de Dados" para extrair
              entidades, criar schema SQL, models.py e migrations Alembic automaticamente.</p>
          </div>
        </div>
      ) : (
        <div className="dm-main">
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
                  {tables.length === 0 && <div className="dm-loading">Nenhuma tabela extraída ainda.</div>}
                  {tables.map((t) => (
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
              {tab === "sql" && <pre>{session.schema_sql || "—"}</pre>}
              {tab === "models" && <pre>{session.models_py || "—"}</pre>}
              {tab === "alembic" && <pre>{session.alembic_migration || "—"}</pre>}
              {tab === "yaml" && <pre>{session.data_model_yaml || "—"}</pre>}
            </div>
          </div>

          <div className="dm-chat">
            <h3>💬 Refinar via chat</h3>
            <div className="dm-chat-messages">
              {chatHistory.length === 0 && (
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
                disabled={chatSending}
              />
              <button onClick={handleChatSend} disabled={chatSending || !chatMsg.trim()}>Enviar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataModelPage;
