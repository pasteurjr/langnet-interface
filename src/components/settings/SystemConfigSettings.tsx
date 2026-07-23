import React, { useEffect, useState } from 'react';
import {
  getSettings, updateSettings, testDb, testLlm,
  SystemSettings, TestResult,
} from '../../services/settingsService';

// Configuração REAL do Sistema (F1 / UC-P01): Banco de Dados + Provedor LLM.
// Segredos nunca são exibidos (campos vêm vazios); Salvar só habilita após Testar Conexão OK.

const box: React.CSSProperties = { background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginBottom: 20 };
const label: React.CSSProperties = { display: 'block', fontSize: 13, fontWeight: 600, color: '#334155', marginBottom: 5 };
const input: React.CSSProperties = { width: '100%', padding: '9px 12px', border: '1px solid #cbd5e1', borderRadius: 8, fontSize: 13, marginBottom: 12, boxSizing: 'border-box' };
const grid2: React.CSSProperties = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 };
const btn = (bg: string): React.CSSProperties => ({ padding: '9px 16px', borderRadius: 8, border: 'none', background: bg, color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer', marginRight: 10 });

function Banner({ r }: { r: TestResult | null }) {
  if (!r) return null;
  const ok = r.ok && (r.model_found !== false);
  return (
    <div style={{ marginTop: 6, marginBottom: 12, padding: '8px 12px', borderRadius: 8, fontSize: 12.5,
      background: ok ? '#dcfce7' : '#fee2e2', color: ok ? '#166534' : '#991b1b',
      border: `1px solid ${ok ? '#86efac' : '#fca5a5'}` }}>
      {ok ? '✓ ' : '⚠ '}{r.message || r.error || (r.ok ? 'OK' : 'Falhou')}
      {r.models_sample && r.models_sample.length > 0 && (
        <div style={{ fontSize: 11, opacity: 0.8, marginTop: 3 }}>modelos: {r.models_sample.slice(0, 6).join(', ')}…</div>
      )}
    </div>
  );
}

const SystemConfigSettings: React.FC = () => {
  const [s, setS] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [dbTest, setDbTest] = useState<TestResult | null>(null);
  const [llmTest, setLlmTest] = useState<TestResult | null>(null);
  const [dbBusy, setDbBusy] = useState(false);
  const [llmBusy, setLlmBusy] = useState(false);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  useEffect(() => {
    getSettings().then((d) => { setS(d); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <div style={{ padding: 20, color: '#64748b' }}>Carregando configurações…</div>;
  if (error || !s) return <div style={{ padding: 20, color: '#b91c1c' }}>Erro: {error}</div>;

  const setDb = (k: keyof SystemSettings['database'], v: string) => {
    setS({ ...s, database: { ...s.database, [k]: v } }); setDbTest(null);
  };
  const setLlm = (k: keyof SystemSettings['llm'], v: string) => {
    setS({ ...s, llm: { ...s.llm, [k]: v } }); setLlmTest(null);
  };

  const runDbTest = async () => {
    setDbBusy(true); setDbTest(null);
    try { setDbTest(await testDb(s.database)); } catch (e: any) { setDbTest({ ok: false, error: e.message }); }
    finally { setDbBusy(false); }
  };
  const runLlmTest = async () => {
    setLlmBusy(true); setLlmTest(null);
    const p = s.llm.llm_provider;
    const payload = p === 'lmstudio'
      ? { provider: p, api_base: s.llm.lmstudio_api_base, model: s.llm.lmstudio_model_name }
      : p === 'deepseek'
      ? { provider: p, api_base: s.llm.deepseek_api_base, model: s.llm.deepseek_model_name, api_key: s.llm.deepseek_api_key || undefined }
      : { provider: p, model: s.llm.openai_model_name, api_key: s.llm.openai_api_key || undefined };
    try { setLlmTest(await testLlm(payload)); } catch (e: any) { setLlmTest({ ok: false, error: e.message }); }
    finally { setLlmBusy(false); }
  };

  const saveDb = async () => {
    await updateSettings({ database: s.database });
    setSavedMsg('Banco de dados salvo.'); setTimeout(() => setSavedMsg(null), 3000);
  };
  const saveLlm = async () => {
    await updateSettings({ llm: s.llm });
    setSavedMsg('Configuração de LLM salva.'); setTimeout(() => setSavedMsg(null), 3000);
  };

  const dbOk = !!dbTest && dbTest.ok;
  const llmOk = !!llmTest && llmTest.ok && llmTest.model_found !== false;

  return (
    <div>
      <p style={{ color: '#64748b', fontSize: 13, marginBottom: 18 }}>
        Configuração persistida do sistema. <b>Segredos</b> (senha, API keys) não são exibidos —
        deixe o campo vazio para manter o valor atual. <b>Salvar</b> só habilita após <b>Testar Conexão</b>.
      </p>
      {savedMsg && <div style={{ ...box, background: '#eef2ff', color: '#3730a3', padding: 12 }}>✓ {savedMsg}</div>}

      {/* ── Banco de Dados ── */}
      <div style={box}>
        <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>🗄️ Banco de Dados</h3>
        <div style={grid2}>
          <div><label style={label}>Host</label><input style={input} value={s.database.db_host} onChange={(e) => setDb('db_host', e.target.value)} /></div>
          <div><label style={label}>Porta</label><input style={input} value={s.database.db_port} onChange={(e) => setDb('db_port', e.target.value)} /></div>
          <div><label style={label}>Usuário</label><input style={input} value={s.database.db_user} onChange={(e) => setDb('db_user', e.target.value)} /></div>
          <div><label style={label}>Senha {s.database.db_password_is_set && <span style={{ color: '#16a34a', fontWeight: 400 }}>(configurada)</span>}</label>
            <input style={input} type="password" placeholder={s.database.db_password_is_set ? '•••••• (deixe vazio p/ manter)' : ''} value={s.database.db_password} onChange={(e) => setDb('db_password', e.target.value)} /></div>
          <div><label style={label}>Base</label><input style={input} value={s.database.db_name} onChange={(e) => setDb('db_name', e.target.value)} /></div>
        </div>
        <Banner r={dbTest} />
        <button style={btn('#0ea5e9')} onClick={runDbTest} disabled={dbBusy}>{dbBusy ? 'Testando…' : '🔌 Testar Conexão'}</button>
        <button style={{ ...btn('#4338ca'), opacity: dbOk ? 1 : 0.5, cursor: dbOk ? 'pointer' : 'not-allowed' }} onClick={saveDb} disabled={!dbOk} title={dbOk ? '' : 'Teste a conexão primeiro'}>💾 Salvar Banco</button>
      </div>

      {/* ── Provedor LLM ── */}
      <div style={box}>
        <h3 style={{ marginTop: 0, fontSize: 15, color: '#312e81' }}>🤖 Provedor de LLM</h3>
        <label style={label}>Provedor</label>
        <select style={input} value={s.llm.llm_provider} onChange={(e) => setLlm('llm_provider', e.target.value)}>
          <option value="lmstudio">LM Studio (local)</option>
          <option value="deepseek">DeepSeek (nuvem)</option>
          <option value="openai">OpenAI</option>
        </select>

        {s.llm.llm_provider === 'lmstudio' && (
          <div style={grid2}>
            <div><label style={label}>Endpoint (API base)</label><input style={input} value={s.llm.lmstudio_api_base} onChange={(e) => setLlm('lmstudio_api_base', e.target.value)} /></div>
            <div><label style={label}>Modelo</label><input style={input} value={s.llm.lmstudio_model_name} onChange={(e) => setLlm('lmstudio_model_name', e.target.value)} /></div>
          </div>
        )}
        {s.llm.llm_provider === 'deepseek' && (
          <div style={grid2}>
            <div><label style={label}>API base</label><input style={input} value={s.llm.deepseek_api_base} onChange={(e) => setLlm('deepseek_api_base', e.target.value)} /></div>
            <div><label style={label}>Modelo</label><input style={input} value={s.llm.deepseek_model_name} onChange={(e) => setLlm('deepseek_model_name', e.target.value)} /></div>
            <div><label style={label}>API key {s.llm.deepseek_api_key_is_set && <span style={{ color: '#16a34a', fontWeight: 400 }}>(configurada)</span>}</label>
              <input style={input} type="password" placeholder={s.llm.deepseek_api_key_is_set ? '•••••• (deixe vazio p/ manter)' : ''} value={s.llm.deepseek_api_key} onChange={(e) => setLlm('deepseek_api_key', e.target.value)} /></div>
          </div>
        )}
        {s.llm.llm_provider === 'openai' && (
          <div style={grid2}>
            <div><label style={label}>Modelo</label><input style={input} value={s.llm.openai_model_name} onChange={(e) => setLlm('openai_model_name', e.target.value)} /></div>
            <div><label style={label}>API key {s.llm.openai_api_key_is_set && <span style={{ color: '#16a34a', fontWeight: 400 }}>(configurada)</span>}</label>
              <input style={input} type="password" placeholder={s.llm.openai_api_key_is_set ? '•••••• (deixe vazio p/ manter)' : ''} value={s.llm.openai_api_key} onChange={(e) => setLlm('openai_api_key', e.target.value)} /></div>
          </div>
        )}
        <Banner r={llmTest} />
        <button style={btn('#0ea5e9')} onClick={runLlmTest} disabled={llmBusy}>{llmBusy ? 'Testando…' : '🔌 Testar Conexão'}</button>
        <button style={{ ...btn('#4338ca'), opacity: llmOk ? 1 : 0.5, cursor: llmOk ? 'pointer' : 'not-allowed' }} onClick={saveLlm} disabled={!llmOk} title={llmOk ? '' : 'Teste a conexão primeiro'}>💾 Salvar LLM</button>
      </div>
    </div>
  );
};

export default SystemConfigSettings;
