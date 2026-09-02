// Dirige as etapas Implantação e Monitoramento na interface do LangNet e captura as telas.
// uso: node drive_langnet_deploy.js <deploy|monitor> [indice]
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const MODE = process.argv[2] || 'deploy';
let N = parseInt(process.argv[3] || '500', 10);
const BASE = 'http://localhost:3001', PROJ = 'bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const RES = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/e2e/deploy_results.json';
const FF = '/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const shot = async (p, tag) => { const f = `${OUT}/${N}-langnet-${tag}.png`; await p.screenshot({ path: f, timeout: 60000 }); console.log('📸', f.split('/').pop()); N++; };

(async () => {
  const b = await firefox.launch({ headless: true, executablePath: FF });
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  p.on('dialog', d => d.dismiss().catch(() => {}));
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);

  if (MODE === 'deploy') {
    await p.goto(`${BASE}/project/${PROJ}/deploy`, { waitUntil: 'domcontentloaded' });
    await p.getByText('Versão gerada').first().waitFor({ timeout: 40000 });
    await sleep(1500);
    await shot(p, 'implantacao-inicial');
    // seleciona a versão mais recente (primeira da lista) e implanta
    await p.locator('.dep-sessoes li').first().click().catch(() => {});
    await sleep(500);
    await shot(p, 'implantacao-versao-escolhida');
    // preenche a configuração da implantação (banco + provedor de IA) como o operador faria
    const CFG = { 'Servidor do banco': '127.0.0.1', 'Porta do banco': '3308', 'Banco de dados': 'biobyte_app',
                  'Usuário do banco': 'producao', 'Senha do banco': '112358123',
                  'Provedor de IA': 'deepseek', 'Chave da IA (se nuvem)': process.env.DEEPSEEK_KEY || '' };
    for (const [rot, val] of Object.entries(CFG)) {
      if (!val) continue;
      const inp = p.locator('.dep-config label', { hasText: rot }).locator('input').first();
      await inp.fill(String(val)).catch(() => console.log('x campo', rot));
    }
    await sleep(500);
    await shot(p, 'implantacao-configuracao');
    await p.getByRole('button', { name: /Implantar esta versão/ }).click({ timeout: 15000 });
    console.log('▷ implantar clicado');
    let servicos = 0;
    for (let i = 0; i < 60; i++) {
      await sleep(3000);
      servicos = await p.locator('.dep-tabela tbody tr').count().catch(() => 0);
      const st = await p.locator('.dep-badge').first().innerText().catch(() => '');
      if (i === 2) await shot(p, 'implantacao-em-andamento');
      if (st.includes('no ar') && servicos >= 3) break;
    }
    await sleep(2500);
    await shot(p, 'implantacao-no-ar');
    const txt = await p.locator('.dep-card').nth(1).innerText().catch(() => '');
    const portas = [...txt.matchAll(/porta (\d+)/g)].map(m => m[1]);
    console.log('serviços no ar, portas:', portas.join(', '));
    fs.writeFileSync(RES, JSON.stringify({ portas, resumo: txt.slice(0, 900) }, null, 1));
    await p.locator('.dep-log').scrollIntoViewIfNeeded().catch(() => {});
    await shot(p, 'implantacao-registro');
    await p.getByText('Histórico de implantações').scrollIntoViewIfNeeded().catch(() => {});
    await sleep(600);
    await shot(p, 'implantacao-historico');
  }

  if (MODE === 'monitor') {
    await p.goto(`${BASE}/project/${PROJ}/monitoring`, { waitUntil: 'domcontentloaded' });
    await p.getByText('Monitoramento').first().waitFor({ timeout: 40000 });
    await sleep(4000);
    await shot(p, 'monitoramento-tarefas');
    await p.getByRole('button', { name: /Ferramentas externas/ }).click().catch(() => {});
    await sleep(1200); await shot(p, 'monitoramento-ferramentas-externas');
    await p.getByRole('button', { name: /Registro ao vivo/ }).click().catch(() => {});
    await sleep(1500); await shot(p, 'monitoramento-registro');
    await p.locator('.mon-filtro').fill('[task]').catch(() => {});
    await sleep(1200); await shot(p, 'monitoramento-registro-filtrado');
    const kpis = await p.locator('.mon-kpis').innerText().catch(() => '');
    console.log('KPIs:', kpis.replace(/\n/g, ' | ').slice(0, 300));
  }
  await b.close(); console.log('DONE', MODE, 'próximo índice', N);
})().catch(e => { console.error('FALHOU', e.message); process.exit(1); });
