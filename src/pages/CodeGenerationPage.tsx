import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import Editor from '@monaco-editor/react';
import {
  CodeFile,
  CodeGenerationSession,
  generateCode,
  getChatHistory,
  getCodeSession,
  listCodeSessions,
  refineCode,
  updateCodeFiles,
  downloadZip,
  CodeChatMessage,
} from '../services/codeGenerationService';
import GenerateCodeModal from '../components/code-generation/GenerateCodeModal';
import RunConsole from '../components/code-generation/RunConsole';
import { useCodeRun } from '../components/code-generation/useCodeRun';

const headerStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  padding: '12px 20px', borderBottom: '1px solid #e0e0e0', background: '#fafafa',
};
const layoutStyle: React.CSSProperties = {
  display: 'flex', flex: 1, minHeight: 0,
};
const leftStyle: React.CSSProperties = {
  width: 280, borderRight: '1px solid #e0e0e0', display: 'flex', flexDirection: 'column',
  background: '#fafafa', overflow: 'hidden',
};
const centerStyle: React.CSSProperties = {
  flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0,
};
const rightStyle: React.CSSProperties = {
  width: 360, borderLeft: '1px solid #e0e0e0', display: 'flex', flexDirection: 'column',
  background: '#fff', overflow: 'hidden',
};
const sectionTitle: React.CSSProperties = {
  fontSize: 12, fontWeight: 700, textTransform: 'uppercase',
  padding: '10px 12px 6px', color: '#666',
};
const itemStyle = (active: boolean): React.CSSProperties => ({
  padding: '8px 12px', cursor: 'pointer', fontSize: 13,
  background: active ? '#e3f2fd' : 'transparent',
  borderLeft: active ? '3px solid #1976d2' : '3px solid transparent',
});
const btn = (color = '#1976d2'): React.CSSProperties => ({
  padding: '6px 14px', background: color, color: '#fff', border: 'none',
  borderRadius: 4, cursor: 'pointer', fontSize: 13, marginLeft: 8,
});

const langOf = (path: string): string => {
  if (path.endsWith('.py')) return 'python';
  if (path.endsWith('.yaml') || path.endsWith('.yml')) return 'yaml';
  if (path.endsWith('.json')) return 'json';
  if (path.endsWith('.md')) return 'markdown';
  if (path === 'Dockerfile' || path.endsWith('.dockerfile')) return 'dockerfile';
  return 'plaintext';
};

const CodeGenerationPage: React.FC = () => {
  const params = useParams<{ projectId?: string; id?: string }>();
  const navigate = useNavigate();
  const projectId = params.projectId || params.id || '';

  const [sessions, setSessions] = useState<CodeGenerationSession[]>([]);
  const [currentSession, setCurrentSession] = useState<CodeGenerationSession | null>(null);
  const [files, setFiles] = useState<CodeFile[]>([]);
  const [selectedPath, setSelectedPath] = useState<string>('');
  const [chat, setChat] = useState<CodeChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editorBuffer, setEditorBuffer] = useState<string>('');
  const [dirty, setDirty] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [warningsCollapsed, setWarningsCollapsed] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const codeRun = useCodeRun(currentSession?.id);
  const lastToastedRunRef = useRef<string | null>(null);

  // Quando o servidor agêntico fica running, oferece ir para Petri Net + autoconnect
  useEffect(() => {
    if (
      codeRun.run?.status === 'running' &&
      codeRun.run?.run_id !== lastToastedRunRef.current &&
      projectId
    ) {
      lastToastedRunRef.current = codeRun.run.run_id;
      const port = currentSession?.websocket_port ?? 5002;
      const wsUrl = `ws://localhost:${port}`;
      toast.success(
        <div>
          <div style={{ marginBottom: 6 }}>
            🌐 Servidor agêntico ativo em <code>{wsUrl}</code>
          </div>
          <button
            onClick={() => navigate(`/project/${projectId}/petri-net?autoconnect=${encodeURIComponent(wsUrl)}`)}
            style={{
              padding: '6px 14px', background: '#1976d2', color: '#fff',
              border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 13,
            }}
          >
            Ir para Petri Net e conectar →
          </button>
        </div>,
        { autoClose: 12000, position: 'top-right' },
      );
    }
  }, [codeRun.run?.status, codeRun.run?.run_id, currentSession?.websocket_port, projectId, navigate]);

  // Load sessions list when project changes
  useEffect(() => {
    if (!projectId) return;
    listCodeSessions(projectId).then(setSessions).catch(console.error);
  }, [projectId]);

  // Load session details when picking from list
  const loadSession = useCallback(async (sessionId: string) => {
    try {
      const s = await getCodeSession(sessionId);
      setCurrentSession(s);
      const sessionFiles = (s.generated_files as CodeFile[]) || [];
      setFiles(sessionFiles);
      setSelectedPath(sessionFiles[0]?.path || '');
      setWarnings(s.execution_metadata?.validation_warnings || []);
      setWarningsCollapsed(false);
      const msgs = await getChatHistory(sessionId);
      setChat(msgs);
    } catch (err: any) {
      console.error(err);
      alert(`Erro ao carregar sessão: ${err.message || err}`);
    }
  }, []);

  // Auto-scroll chat
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chat]);

  // Sync editor buffer when file changes (or files reload)
  useEffect(() => {
    const f = files.find((x) => x.path === selectedPath);
    setEditorBuffer(f?.content || '');
    setDirty(false);
  }, [selectedPath, files]);

  const handleGenerate = useCallback(async (sel: {
    agentsYamlSessionId: string;
    tasksYamlSessionId: string;
    taskExecutionFlowSessionId?: string;
    websocketPort: number;
  }) => {
    if (!projectId) return;
    setIsModalOpen(false);
    setIsGenerating(true);
    try {
      const res = await generateCode(projectId, sel);
      const sessionFiles = (res.files as CodeFile[]) || [];
      setFiles(sessionFiles);
      setSelectedPath(sessionFiles[0]?.path || '');
      setWarnings(res.validation_warnings || []);
      setWarningsCollapsed(false);
      const refreshed = await listCodeSessions(projectId);
      setSessions(refreshed);
      const found = refreshed.find((s) => s.id === res.session_id);
      if (found) setCurrentSession(found);
      setChat([]);
    } catch (err: any) {
      alert(`Erro ao gerar código: ${err.message || err}`);
    } finally {
      setIsGenerating(false);
    }
  }, [projectId]);

  const handleSaveFile = useCallback(async () => {
    if (!currentSession || !dirty) return;
    const next = files.map((f) => (f.path === selectedPath ? { ...f, content: editorBuffer } : f));
    setFiles(next);
    setDirty(false);
    try {
      await updateCodeFiles(currentSession.id, next, `Edição manual em ${selectedPath}`);
      const s = await getCodeSession(currentSession.id);
      setCurrentSession(s);
    } catch (err: any) {
      alert(`Erro ao salvar: ${err.message || err}`);
    }
  }, [currentSession, dirty, files, selectedPath, editorBuffer]);

  const handleSendRefine = useCallback(async () => {
    if (!currentSession || !chatInput.trim()) return;
    const message = chatInput.trim();
    setChatInput('');
    setIsRefining(true);
    const localUserMsg: CodeChatMessage = {
      id: `tmp-${Date.now()}`,
      sender_type: 'user',
      message_text: message,
      message_type: 'chat',
      timestamp: new Date().toISOString(),
    };
    setChat((c) => [...c, localUserMsg]);
    try {
      const res = await refineCode(currentSession.id, message);
      if (res.has_diff && res.files) {
        setFiles(res.files);
        if (res.affected_paths?.[0]) setSelectedPath(res.affected_paths[0]);
      }
      // Atualiza warnings se o backend re-validou (fecha o loop SDD)
      if (res.validation_warnings !== undefined) {
        setWarnings(res.validation_warnings);
      }
      const msgs = await getChatHistory(currentSession.id);
      setChat(msgs);
      const s = await getCodeSession(currentSession.id);
      setCurrentSession(s);
    } catch (err: any) {
      alert(`Erro no refinamento: ${err.message || err}`);
    } finally {
      setIsRefining(false);
    }
  }, [currentSession, chatInput]);

  // Gera prompt de refinamento por categoria de warning (SDD fix loop)
  const buildFixPrompt = useCallback((warning: string): string => {
    const colonIdx = warning.indexOf(':');
    const category = colonIdx > 0 ? warning.slice(0, colonIdx).trim() : warning;
    const detail = colonIdx > 0 ? warning.slice(colonIdx + 1).trim() : '';
    // Extrai lista de itens (depois do " — " ou parecidos)
    const dashIdx = detail.indexOf('—');
    const items = dashIdx > 0 ? detail.slice(dashIdx + 1).trim() : detail;

    switch (category) {
      case 'tools_orphan':
        return [
          `Em tools.py, crie as tools faltantes listadas abaixo, todas herdando de crewai.tools.BaseTool com docstring, args Pydantic e método _run, e adicione cada uma ao dict TOOL_REGISTRY no fim do arquivo:`,
          ``,
          items,
        ].join('\n');
      case 'missing_adapters':
        return [
          `Em adapters.py, adicione as funções input_func/output_func ausentes listadas abaixo. Use a assinatura padrão: def <task>_input_func(input_data: dict) -> dict e def <task>_output_func(input_data: dict, result: str) -> dict.`,
          ``,
          items,
        ].join('\n');
      case 'unknown_task_in_bindings':
        return `Em adapters.py, o dict TASK_TOOLS referencia tasks que não existem em tasks.yaml: ${items}. Remova essas entradas órfãs de TASK_TOOLS.`;
      case 'unknown_agent_in_bindings':
        return `Em adapters.py, o dict AGENT_TOOLS referencia agentes que não existem em agents.yaml: ${items}. Remova essas entradas órfãs de AGENT_TOOLS.`;
      case 'petri_unknown_agent':
        return `Em petri_net.json, os places listados referenciam agentId que não existe em agents.yaml: ${items}. Para cada um, ajuste o agentId para um agente válido (consulte agents.yaml) ou set null se o lugar não exigir agente.`;
      case 'petri_unknown_task':
        return `Em petri_net.json, os places referenciam tasks que não existem em tasks.yaml: ${items}. Renomeie cada place para apontar para uma task válida.`;
      default:
        return `Corrija o warning: ${warning}`;
    }
  }, []);

  const handleFixWarning = useCallback((warning: string) => {
    setChatInput(buildFixPrompt(warning));
  }, [buildFixPrompt]);

  const handleDownload = useCallback(async () => {
    if (!currentSession) return;
    try {
      const blob = await downloadZip(currentSession.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentSession.session_name || currentSession.id}.zip`;
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`Erro ao baixar ZIP: ${err.message || err}`);
    }
  }, [currentSession]);

  const fileTree = useMemo(() => files.map((f) => f.path), [files]);

  if (!projectId) {
    return (
      <div style={{ padding: 20 }}>
        <h1>💻 Geração de Código</h1>
        <p style={{ color: '#c00' }}>Selecione um projeto para gerar código.</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
      <div style={headerStyle}>
        <h1 style={{ margin: 0, fontSize: 20 }}>💻 Geração de Código Python</h1>
        <div>
          <button
            onClick={() => setIsModalOpen(true)}
            disabled={isGenerating}
            style={btn(isGenerating ? '#888' : '#1976d2')}
          >
            {isGenerating ? '⏳ Gerando...' : '⚡ Gerar Código'}
          </button>
          <button onClick={handleSaveFile} disabled={!dirty} style={btn(dirty ? '#2e7d32' : '#888')}>
            💾 Salvar Arquivo
          </button>
          <button onClick={handleDownload} disabled={!currentSession} style={btn('#ff9800')}>
            📦 Baixar ZIP
          </button>
          <button
            onClick={() => {
              setConsoleOpen(true);
              codeRun.start();
            }}
            disabled={!currentSession || codeRun.isStarting || codeRun.run?.status === 'running' || codeRun.run?.status === 'installing'}
            style={btn(codeRun.run?.status === 'running' ? '#888' : '#7b1fa2')}
            title="Cria venv, instala deps e sobe python main.py em /tmp/langnet-runs"
          >
            {codeRun.isStarting ? '⏳ Iniciando...' :
             codeRun.run?.status === 'running' ? '▶ Executando' :
             codeRun.run?.status === 'installing' ? '📦 Instalando' :
             '▶ Executar'}
          </button>
        </div>
      </div>

      {warnings.length > 0 && (
        <div
          style={{
            background: '#fff8e1', borderBottom: '1px solid #ffc107',
            padding: warningsCollapsed ? '8px 16px' : '12px 16px',
            display: 'flex', alignItems: 'flex-start', gap: 12,
          }}
        >
          <span style={{ fontSize: 18, marginTop: 2 }}>⚠️</span>
          <div style={{ flex: 1, fontSize: 12 }}>
            <div style={{ fontWeight: 700, marginBottom: warningsCollapsed ? 0 : 6 }}>
              {warnings.length} validation warning(s)
              <button
                onClick={() => setWarningsCollapsed(v => !v)}
                style={{ marginLeft: 8, background: 'none', border: 'none', color: '#1976d2', cursor: 'pointer', fontSize: 11, textDecoration: 'underline' }}
              >
                {warningsCollapsed ? 'expandir' : 'recolher'}
              </button>
            </div>
            {!warningsCollapsed && (
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {warnings.map((w, i) => {
                  const [category, ...rest] = w.split(': ');
                  return (
                    <li key={i} style={{ marginBottom: 6 }}>
                      <code style={{ background: '#fff', padding: '1px 6px', borderRadius: 3, fontSize: 11 }}>{category}</code>
                      <span style={{ marginLeft: 6 }}>{rest.join(': ')}</span>
                      <button
                        onClick={() => handleFixWarning(w)}
                        title="Pré-preenche o chat com instrução para corrigir este warning"
                        style={{
                          marginLeft: 8, padding: '1px 8px', fontSize: 10,
                          background: '#1976d2', color: '#fff',
                          border: 'none', borderRadius: 3, cursor: 'pointer',
                        }}
                      >
                        🔧 Corrigir
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
            {!warningsCollapsed && (
              <div style={{ marginTop: 6, fontSize: 11, color: '#666' }}>
                💡 Clique em <strong>🔧 Corrigir</strong> para preencher o chat com a instrução adequada — revise e envie. O loop spec → código → validate → fix → revalidate fecha automaticamente.
              </div>
            )}
          </div>
        </div>
      )}

      <div style={layoutStyle}>
        {/* LEFT — sessions + file tree */}
        <div style={leftStyle}>
          <div style={sectionTitle}>Sessões ({sessions.length})</div>
          <div style={{ maxHeight: '40%', overflowY: 'auto' }}>
            {sessions.map((s) => (
              <div
                key={s.id}
                style={itemStyle(currentSession?.id === s.id)}
                onClick={() => loadSession(s.id)}
                title={`session ${s.id}\nagents.yaml: ${s.agents_yaml_session_id || '—'}\ntasks.yaml: ${s.tasks_yaml_session_id || '—'}\nagent_task_spec: ${s.agent_task_spec_session_id || '—'}\ntask_execution_flow: ${s.task_execution_flow_session_id || '—'}`}
              >
                <div style={{ fontWeight: 600 }}>{s.session_name}</div>
                <div style={{ fontSize: 11, color: '#666' }}>
                  v{s.current_version} · {s.total_files} arquivos · {s.status}
                  {s.agent_task_spec_session_id && <span title="agent_task_spec usado (bindings de tools deterministic)" style={{ marginLeft: 4, color: '#1976d2' }}>🔗</span>}
                </div>
              </div>
            ))}
            {sessions.length === 0 && (
              <div style={{ padding: 12, color: '#888', fontSize: 12 }}>
                Nenhuma sessão. Clique em ⚡ Gerar Código.
              </div>
            )}
          </div>

          <div style={{ ...sectionTitle, borderTop: '1px solid #e0e0e0', marginTop: 4 }}>
            Arquivos ({fileTree.length})
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {fileTree.map((path) => (
              <div
                key={path}
                style={itemStyle(selectedPath === path)}
                onClick={() => setSelectedPath(path)}
              >
                {path}
              </div>
            ))}
          </div>
        </div>

        {/* CENTER — Monaco editor */}
        <div style={centerStyle}>
          {!selectedPath ? (
            <div style={{ padding: 40, color: '#666', textAlign: 'center' }}>
              Selecione um arquivo à esquerda, ou clique em <strong>⚡ Gerar Código</strong> para começar.
            </div>
          ) : (
            <>
              <div style={{
                padding: '6px 16px', borderBottom: '1px solid #e0e0e0',
                background: '#f5f5f5', fontFamily: 'monospace', fontSize: 12,
              }}>
                {selectedPath} {dirty && <span style={{ color: '#c80', fontWeight: 700 }}>● modificado</span>}
              </div>
              <Editor
                height="100%"
                language={langOf(selectedPath)}
                value={editorBuffer}
                onChange={(v) => { setEditorBuffer(v || ''); setDirty(true); }}
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  wordWrap: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
            </>
          )}
        </div>

        {/* RIGHT — chat */}
        <div style={rightStyle}>
          <div style={sectionTitle}>💬 Refinamento</div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '0 12px' }}>
            {chat.length === 0 && (
              <div style={{ fontSize: 12, color: '#888', padding: 12 }}>
                Selecione uma sessão e mande uma instrução (ex: "use gpt-4o no agente X" ou
                "adicione retry com backoff em tools.py").
              </div>
            )}
            {chat.map((m) => (
              <div
                key={m.id}
                style={{
                  margin: '8px 0', padding: 10, borderRadius: 6,
                  background: m.sender_type === 'user' ? '#e3f2fd' : '#f5f5f5',
                  fontSize: 13,
                }}
              >
                <div style={{ fontSize: 10, color: '#666', marginBottom: 4 }}>
                  {m.sender_type === 'user' ? 'Você' : 'LangNet'} · {new Date(m.timestamp).toLocaleTimeString('pt-BR')}
                </div>
                <div style={{ whiteSpace: 'pre-wrap' }}>{m.message_text}</div>
                {m.message_data?.has_diff && m.message_data.affected_paths && (
                  <div style={{ marginTop: 6, fontSize: 11, color: '#1976d2' }}>
                    ✏️ Alterados: {m.message_data.affected_paths.join(', ')}
                  </div>
                )}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div style={{ padding: 8, borderTop: '1px solid #e0e0e0', display: 'flex', gap: 4 }}>
            <textarea
              style={{ flex: 1, resize: 'none', padding: 6, fontSize: 13, border: '1px solid #ccc', borderRadius: 4 }}
              rows={2}
              placeholder={currentSession ? 'Refinar projeto...' : 'Selecione uma sessão primeiro'}
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={!currentSession || isRefining}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendRefine(); }
              }}
            />
            <button
              onClick={handleSendRefine}
              disabled={!currentSession || isRefining || !chatInput.trim()}
              style={btn(isRefining ? '#888' : '#1976d2')}
            >
              {isRefining ? '⏳' : '↵'}
            </button>
          </div>
        </div>
      </div>

      <RunConsole
        visible={consoleOpen}
        run={codeRun.run}
        lines={codeRun.lines}
        isStarting={codeRun.isStarting}
        error={codeRun.error}
        onStop={codeRun.stop}
        onClose={() => setConsoleOpen(false)}
        onClear={codeRun.clear}
      />

      <GenerateCodeModal
        isOpen={isModalOpen}
        projectId={projectId}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleGenerate}
      />
    </div>
  );
};

export default CodeGenerationPage;
