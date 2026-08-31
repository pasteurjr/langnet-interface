// Captura telas REAIS do pipeline LangNet (projeto Uso do Solo) para o script de vídeo.
// Harness: injeta user+token ANTES do load (ativa contexto de projeto e o menu lateral),
// e encaminha /api/* -> :8000 (contorna CORS+credenciais do dev-server). Dados 100% reais do backend.
// Saída: docs/apresentacao/demo-s61/real_shots/<id>.png   (landing "_stage" + documento)
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-s61/real_shots';
const USER = JSON.stringify({ id: 'f8edd66e-bcb8-11f0-b19e-a0ad9f2fcdf4', name: 'Admin Master', email: 'teste@teste.com', role: 'admin', is_active: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
fs.mkdirSync(OUT, { recursive: true });

// etapas do Pipeline (rota canônica do nav). doc=true => tem Visualizar do documento.
const STAGES = [
  ['documents',          'documents',           true ],
  ['spec',               'specification',       true ],
  ['data_model',         'data-model',          true ],
  ['ui_spec',            'ui-spec',             true ],
  ['agent_task',         'agent-task',          true ],
  ['yaml',               'yaml-generation',     true ],
  ['task_flow',          'task-execution-flow', false],
  ['petri',              'petri-net',           false],
  ['code',               'code-generation',     false],
  ['test_cases',         'test-cases',          false],
];

async function drillToDoc(p) {
  // abre Histórico -> sessão mais recente (2 níveis) -> Visualizar
  const h = p.locator('button:has-text("Histórico"), .btn-history-compact, button:has-text("📜")').first();
  if (await h.count()) {
    await h.click().catch(() => {}); await sleep(1600);
    for (let k = 0; k < 2; k++) {
      const it = p.locator('.session-item, [class*="session"] li, [class*="history"] li').first();
      if (await it.count()) { await it.click().catch(() => {}); await sleep(2000); }
    }
  }
  await p.keyboard.press('Escape').catch(() => {}); await sleep(1000);
  const v = p.locator('button:has-text("Visualizar"), button:has-text("👁")').first();
  if (await v.count()) { await v.click().catch(() => {}); await sleep(2600); return true; }
  return false;
}
async function scrollTo(p, text) {
  return await p.evaluate((t) => {
    const els = [...document.querySelectorAll('h1,h2,h3,h4,strong,td,p,div')];
    const el = els.find(e => e.textContent.trim().startsWith(t));
    if (el) { el.scrollIntoView({ block: 'start' }); return true; } return false;
  }, text);
}

(async () => {
  const b = await chromium.launch({ headless: true });
  const ctx = await b.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1.5 });
  await ctx.addInitScript(([t, u]) => {
    ['accessToken', 'token', 'authToken'].forEach(k => localStorage.setItem(k, t));
    localStorage.setItem('user', u);
  }, [TOKEN, USER]);
  await ctx.route('**/api/**', async route => {
    const nu = new URL(route.request().url());
    try {
      const r = await ctx.request.fetch('http://localhost:8000' + nu.pathname + nu.search, {
        method: route.request().method(),
        headers: { ...route.request().headers(), authorization: 'Bearer ' + TOKEN },
        data: route.request().postDataBuffer() || undefined, maxRedirects: 5,
      });
      const h = { ...r.headers() }; delete h['content-encoding']; delete h['content-length']; delete h['transfer-encoding'];
      h['access-control-allow-origin'] = 'http://localhost:3000'; h['access-control-allow-credentials'] = 'true';
      await route.fulfill({ status: r.status(), body: await r.body(), headers: h });
    } catch (e) { await route.abort(); }
  });
  const p = await ctx.newPage();
  const only = process.argv[2];

  for (const [id, route, hasDoc] of STAGES) {
    if (only && !id.includes(only)) continue;
    try {
      await p.goto(`http://localhost:3000/project/${PROJ}/${route}`, { waitUntil: 'domcontentloaded' });
      await p.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
      await sleep(4200);
      // LANDING (o que a etapa tem) — com o menu lateral do projeto visível
      await p.screenshot({ path: `${OUT}/${id}_stage.png` });
      // sidebar só uma vez (a partir de documents)
      if (id === 'documents') {
        const sb = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')
          .match(/Documentos|Especifica|Modelo de Dados|Interface|Agentes|YAML|Sequ|Petri|C[oó]digo|Casos de Teste/g)?.slice(0, 12).join(','));
        console.log('  sidebar tem:', sb);
      }
      // DOCUMENTO
      if (hasDoc) {
        const ok = await drillToDoc(p);
        if (id === 'documents' && ok) {
          // Requisitos: capturar seções FR e NFR do documento REAL
          for (const [nm, anchor] of [['req_fr', 'Requisitos Funcionais'], ['req_nfr', 'Requisitos N']]) {
            const s = await scrollTo(p, anchor); await sleep(1000);
            await p.screenshot({ path: `${OUT}/${nm}.png` }); console.log('  📄', nm, s);
          }
        } else if (ok) {
          await p.screenshot({ path: `${OUT}/${id}_doc.png` });
        }
      }
      const body = (await p.evaluate(() => document.body.innerText) || '').replace(/\s+/g, ' ').slice(0, 70);
      console.log('📸', id, '|', body);
    } catch (e) { console.log('⚠️', id, 'FALHOU:', e.message.slice(0, 90)); }
  }
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
