import React, { useEffect, useState } from 'react';
import {
  listServers, registerServer, testServer, testAdhoc, deleteServer, getCatalog,
  McpServer, McpTestResult, CatalogItem,
} from '../../services/mcpService';

// Gestão REAL de servidores MCP (F2 Fase 1): registrar, testar conexão (descobre as
// ferramentas), listar (segredos mascarados), remover.

const box: React.CSSProperties = { background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginBottom: 18 };
const inp: React.CSSProperties = { width: '100%', padding: '9px 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: 13, marginBottom: 10, boxSizing: 'border-box' };
const lbl: React.CSSProperties = { display: 'block', fontSize: 12.5, fontWeight: 600, color: '#334155', marginBottom: 4 };
const btn = (bg: string): React.CSSProperties => ({ padding: '8px 15px', borderRadius: 8, border: 'none', background: bg, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', marginRight: 8 });
const badge = (s: string): React.CSSProperties => ({
  fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 20,
  background: s === 'ativo' ? '#dcfce7' : s === 'erro' ? '#fee2e2' : '#e2e8f0',
  color: s === 'ativo' ? '#166534' : s === 'erro' ? '#991b1b' : '#475569',
});
const chip = (bg: string, col: string): React.CSSProperties => ({ fontSize: 11, background: bg, color: col, borderRadius: 6, padding: '2px 8px', marginRight: 5 });

const McpServersManager: React.FC = () => {
  const [servers, setServers] = useState<McpServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ name: '', transport: 'sse', url: '', command: '', category: '', cred: '' });
  const [adhoc, setAdhoc] = useState<McpTestResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [cat, setCat] = useState<CatalogItem[]>([]);

  const reload = () => listServers().then(setServers).catch((e) => setMsg(e.message)).finally(() => setLoading(false));
  useEffect(() => { reload(); getCatalog().then(setCat).catch(() => {}); }, []);

  const registerFromCatalog = async (c: CatalogItem) => {
    setBusy(true); setMsg(null);
    try {
      await registerServer({ name: c.name, transport: c.transport, url: c.url, command: c.command, category: c.category });
      setMsg(`"${c.name}" registrado. Clique em Testar para descobrir as ferramentas${c.needs_key ? ` (precisa de credencial ${c.key_env})` : ''}.`);
      reload();
    } catch (e: any) { setMsg(e.message); } finally { setBusy(false); }
  };

  const credObj = () => {
    const c = form.cred.trim();
    if (!c) return undefined;
    // formato "Header: valor" por linha
    const o: Record<string, string> = {};
    c.split('\n').forEach((ln) => { const i = ln.indexOf(':'); if (i > 0) o[ln.slice(0, i).trim()] = ln.slice(i + 1).trim(); });
    return Object.keys(o).length ? o : undefined;
  };

  const doTestAdhoc = async () => {
    setBusy(true); setAdhoc(null);
    try { setAdhoc(await testAdhoc({ transport: form.transport, url: form.url, command: form.command, credentials: credObj() } as any)); }
    finally { setBusy(false); }
  };
  const doRegister = async () => {
    setBusy(true); setMsg(null);
    try {
      await registerServer({ name: form.name, transport: form.transport, url: form.url, command: form.command, category: form.category, credentials: credObj() });
      setForm({ name: '', transport: 'sse', url: '', command: '', category: '', cred: '' }); setAdhoc(null);
      setMsg('Servidor registrado.'); reload();
    } catch (e: any) { setMsg(e.message); } finally { setBusy(false); }
  };
  const doTest = async (id: string) => {
    setMsg(null); const r = await testServer(id);
    setMsg(r.ok ? `Ativo — ${r.tools_count} ferramenta(s) descoberta(s).` : `Erro: ${r.error}`);
    reload();
  };
  const doDelete = async (id: string) => { await deleteServer(id); reload(); };

  return (
    <div>
      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 16 }}>
        Registre <b>servidores MCP</b> (Model Context Protocol) para dar aos agentes acesso a
        ferramentas externas reais. <b>Testar conexão</b> faz o handshake e <b>descobre as ferramentas</b>.
        Credenciais não são exibidas. Um servidor só fica <b>ativo</b> após um teste bem-sucedido.
      </p>
      {msg && <div style={{ ...box, background: '#eef2ff', color: '#3730a3', padding: 12 }}>{msg}</div>}

      {/* ── Catálogo de recomendados (1-clique) ── */}
      {cat.length > 0 && (
        <div style={box}>
          <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>⭐ Servidores recomendados</h3>
          <p style={{ color: '#94a3b8', fontSize: 12, marginTop: 0 }}>Cadastre com 1 clique. Depois clique em <b>Testar</b> na lista abaixo para descobrir as ferramentas. 🔑 = precisa de credencial.</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {cat.map((c) => (
              <div key={c.name} style={{ border: '1px solid #e2e8f0', borderRadius: 9, padding: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <b style={{ fontSize: 13 }}>{c.name}</b>
                  {c.needs_key && <span title={`precisa de ${c.key_env}`}>🔑</span>}
                  <span style={chip('#f1f5f9', '#64748b')}>{c.category}</span>
                  <button style={{ ...btn('#4338ca'), marginLeft: 'auto' }} onClick={() => registerFromCatalog(c)} disabled={busy}>+ cadastrar</button>
                </div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{c.description}</div>
                <code style={{ fontSize: 10.5, color: '#7c3aed' }}>{c.command || c.url}</code>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Registrar novo (manual) ── */}
      <div style={box}>
        <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>➕ Registrar servidor MCP</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div><label style={lbl}>Nome</label><input style={inp} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="CRM da empresa" /></div>
          <div><label style={lbl}>Categoria</label><input style={inp} value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} placeholder="crm, email, dados…" /></div>
          <div><label style={lbl}>Transporte</label>
            <select style={inp} value={form.transport} onChange={(e) => setForm({ ...form, transport: e.target.value })}>
              <option value="sse">SSE</option><option value="http">HTTP (streamable)</option><option value="stdio">stdio (comando)</option>
            </select></div>
          {form.transport === 'stdio' ? (
            <div><label style={lbl}>Comando</label><input style={inp} value={form.command} onChange={(e) => setForm({ ...form, command: e.target.value })} placeholder="uvx mcp-server-fetch" /></div>
          ) : (
            <div><label style={lbl}>URL</label><input style={inp} value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} placeholder="http://host:porta/sse" /></div>
          )}
        </div>
        <label style={lbl}>Credenciais (opcional — uma por linha, "Header: valor")</label>
        <textarea style={{ ...inp, fontFamily: 'monospace' }} rows={2} value={form.cred} onChange={(e) => setForm({ ...form, cred: e.target.value })} placeholder="Authorization: Bearer ..." />
        {adhoc && (
          <div style={{ margin: '4px 0 10px', padding: '8px 12px', borderRadius: 8, fontSize: 12.5,
            background: adhoc.ok ? '#dcfce7' : '#fee2e2', color: adhoc.ok ? '#166534' : '#991b1b' }}>
            {adhoc.ok ? `✓ ${adhoc.message} — ${(adhoc.tools || []).map((t) => t.name).join(', ')}` : `⚠ ${adhoc.error}`}
          </div>
        )}
        <button style={btn('#0ea5e9')} onClick={doTestAdhoc} disabled={busy || (!form.url && !form.command)}>🔌 Testar Conexão</button>
        <button style={{ ...btn('#4338ca'), opacity: form.name && (form.url || form.command) ? 1 : 0.5 }} onClick={doRegister} disabled={busy || !form.name || (!form.url && !form.command)}>💾 Registrar</button>
      </div>

      {/* ── Lista ── */}
      <div style={box}>
        <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>🔗 Servidores registrados</h3>
        {loading ? <div style={{ color: '#64748b' }}>Carregando…</div> : servers.length === 0 ? (
          <div style={{ color: '#94a3b8', fontSize: 13 }}>Nenhum servidor MCP registrado ainda.</div>
        ) : servers.map((s) => (
          <div key={s.id} style={{ borderTop: '1px solid #f1f5f9', padding: '12px 0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <b style={{ fontSize: 14 }}>{s.name}</b>
              <span style={badge(s.status)}>{s.status}</span>
              <span style={{ fontSize: 11, color: '#94a3b8' }}>{s.transport} · {s.category || '—'} · {s.tools_count} tool(s)</span>
              <div style={{ marginLeft: 'auto' }}>
                <button style={btn('#0ea5e9')} onClick={() => doTest(s.id)}>🔌 Testar</button>
                <button style={btn('#ef4444')} onClick={() => doDelete(s.id)}>🗑</button>
              </div>
            </div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 3 }}>{s.url}</div>
            {s.tools.length > 0 && (
              <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {s.tools.map((t) => (
                  <span key={t.name} title={t.description} style={{ fontSize: 11, background: '#eef2ff', color: '#3730a3', border: '1px solid #c7d2fe', borderRadius: 6, padding: '2px 8px' }}>
                    🛠 {t.name}
                  </span>
                ))}
              </div>
            )}
            {s.last_error && <div style={{ fontSize: 11, color: '#b91c1c', marginTop: 4 }}>⚠ {s.last_error}</div>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default McpServersManager;
