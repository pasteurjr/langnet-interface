import React, { useEffect, useState } from 'react';
import {
  projectServers, enableServer, disableServer, projectTools, projectAgents,
  agentTools, assignTool, unassignTool, suggestTools,
  ProjectServer, ProjectTool, AgentInfo, AgentTool, Suggestion,
} from '../../services/mcpService';

// Gestão MCP por PROJETO (F2 Fase 2): habilitar servidores + atribuir tools MCP aos
// agentes (sugerida pelo designer + manual). O que for atribuído aqui é consumido pela
// Geração de Código (Fase 3) — os agentes ganham essas tools MCP de verdade.

const box: React.CSSProperties = { background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 18, marginBottom: 16 };
const btn = (bg: string): React.CSSProperties => ({ padding: '6px 12px', borderRadius: 7, border: 'none', background: bg, color: '#fff', fontSize: 12, fontWeight: 600, cursor: 'pointer', marginLeft: 6 });
const chip = (bg: string, col: string): React.CSSProperties => ({ fontSize: 11, background: bg, color: col, border: `1px solid ${col}33`, borderRadius: 6, padding: '2px 8px', marginRight: 5, display: 'inline-block' });

const McpProjectManager: React.FC<{ projectId: string }> = ({ projectId }) => {
  const [servers, setServers] = useState<ProjectServer[]>([]);
  const [tools, setTools] = useState<ProjectTool[]>([]);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [assigned, setAssigned] = useState<AgentTool[]>([]);
  const [suggs, setSuggs] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [sel, setSel] = useState<Record<string, string>>({}); // agent_id -> "server|tool"

  const reload = async () => {
    const [s, t, a, at] = await Promise.all([
      projectServers(projectId), projectTools(projectId), projectAgents(projectId), agentTools(projectId),
    ]);
    setServers(s); setTools(t); setAgents(a); setAssigned(at); setLoading(false);
  };
  useEffect(() => { reload().catch(() => setLoading(false)); }, [projectId]);

  const toggle = async (s: ProjectServer) => {
    if (s.enabled) await disableServer(projectId, s.id); else await enableServer(projectId, s.id);
    reload();
  };
  const doSuggest = async () => setSuggs(await suggestTools(projectId));
  const applySugg = async (g: Suggestion) => {
    await assignTool(projectId, { agent_id: g.agent_id, mcp_server_id: g.mcp_server_id, tool_name: g.tool_name, source: 'sugerido' });
    reload();
  };
  const doAssign = async (agentId: string) => {
    const v = sel[agentId]; if (!v) return;
    const [sid, tname] = v.split('|');
    await assignTool(projectId, { agent_id: agentId, mcp_server_id: sid, tool_name: tname, source: 'manual' });
    reload();
  };
  const doRemove = async (agentId: string, tool: string) => { await unassignTool(projectId, agentId, tool); reload(); };

  if (loading) return <div style={{ padding: 16, color: '#64748b' }}>Carregando MCP do projeto…</div>;

  const toolsByAgent = (aid: string) => assigned.filter((x) => x.agent_id === aid);

  return (
    <div>
      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 14 }}>
        Habilite os servidores MCP deste projeto e atribua as ferramentas aos agentes.
        A atribuição (sugerida ou manual) é usada pela <b>Geração de Código</b> — os agentes
        ganham essas tools MCP de verdade no app gerado.
      </p>

      {/* Servidores do projeto */}
      <div style={box}>
        <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>🔌 Servidores MCP habilitados</h3>
        {servers.length === 0 ? <div style={{ color: '#94a3b8', fontSize: 13 }}>Nenhum servidor MCP registrado (registre em MCP → Configuração Global).</div> :
          servers.map((s) => (
            <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderTop: '1px solid #f1f5f9' }}>
              <b style={{ fontSize: 13 }}>{s.name}</b>
              <span style={{ fontSize: 11, color: '#94a3b8' }}>{s.status} · {s.tools_count} tool(s)</span>
              <button style={btn(s.enabled ? '#16a34a' : '#94a3b8')} onClick={() => toggle(s)}>
                {s.enabled ? '✓ habilitado' : 'habilitar'}
              </button>
            </div>
          ))}
      </div>

      {/* Sugestões */}
      <div style={box}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ margin: 0, fontSize: 15, color: '#312e81' }}>✨ Sugestões do designer</h3>
          <button style={btn('#7c3aed')} onClick={doSuggest}>Sugerir atribuições</button>
        </div>
        {suggs.length > 0 && (
          <div style={{ marginTop: 10 }}>
            {suggs.map((g, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 0', fontSize: 13 }}>
                <span style={chip('#f5f3ff', '#7c3aed')}>{g.agent_id}</span>←<span style={chip('#eef2ff', '#3730a3')}>🛠 {g.tool_name}</span>
                <span style={{ fontSize: 11, color: '#94a3b8' }}>match: {g.match.join(', ')}</span>
                <button style={btn('#4338ca')} onClick={() => applySugg(g)}>+ aplicar</button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Agentes + tools atribuídas */}
      <div style={box}>
        <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>🤖 Agentes e suas ferramentas MCP</h3>
        {agents.length === 0 ? <div style={{ color: '#94a3b8', fontSize: 13 }}>Sem agentes (gere o agents.yaml do projeto).</div> :
          agents.map((a) => (
            <div key={a.agent_id} style={{ padding: '10px 0', borderTop: '1px solid #f1f5f9' }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#334155' }}>{a.agent_id}</div>
              <div style={{ marginTop: 5, display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 6 }}>
                {toolsByAgent(a.agent_id).map((t) => (
                  <span key={t.tool_name} style={chip('#dcfce7', '#166534')}>
                    🛠 {t.tool_name} <span style={{ opacity: .6 }}>({t.source})</span>
                    <span style={{ cursor: 'pointer', marginLeft: 4 }} onClick={() => doRemove(a.agent_id, t.tool_name)}>✕</span>
                  </span>
                ))}
                <select value={sel[a.agent_id] || ''} onChange={(e) => setSel({ ...sel, [a.agent_id]: e.target.value })}
                  style={{ fontSize: 12, border: '1px solid #cbd5e1', borderRadius: 6, padding: '3px 6px' }}>
                  <option value="">+ atribuir tool…</option>
                  {tools.map((t) => <option key={t.tool_name} value={`${t.mcp_server_id}|${t.tool_name}`}>{t.tool_name} ({t.server_name})</option>)}
                </select>
                <button style={btn('#4338ca')} onClick={() => doAssign(a.agent_id)}>+</button>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
};

export default McpProjectManager;
