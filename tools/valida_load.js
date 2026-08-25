// Carrega um artefato pela UI via botão "Histórico" (sessão -> versão) e screenshota.
// Uso: node valida_load.js <rota> <nome-shot> [steps] [segundos]
//   steps: quantos cliques em .session-item apos abrir Historico (1=so sessao mostrando versoes; 2=sessao+versao)
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'a1391183-f348-4a78-8773-8046b90a7676';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/validacao-pipeline/shots';
const route = process.argv[2].replace('PROJ', PROJ);
const name = process.argv[3];
const steps = parseInt(process.argv[4] || '2', 10);
const waitS = parseInt(process.argv[5] || '4', 10);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1150 } });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`http://localhost:3000${route}`, { waitUntil: 'networkidle' });
  await sleep(waitS * 1000);
  const hist = p.locator('button', { hasText: /Hist[oó]rico/ }).first();
  if (await hist.count()) {
    await hist.click(); await sleep(2500);
    for (let s = 0; s < steps; s++) {
      const it = p.locator('.session-item, .version-item').first();
      if (await it.count()) { await it.click(); await sleep(2800); }
    }
  } else { console.log('(sem botao Historico nesta pagina)'); }
  await sleep(waitS * 1000);
  await p.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
  const txt = await p.evaluate(() => document.body.innerText);
  console.log('SHOT:', name, '| VERSOES:', (txt.match(/Vers[aã]o \d+/g) || []).slice(0,6).join(','));
  console.log('TOPO:', txt.replace(/\n+/g,' | ').slice(120, 360));
  await b.close();
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
