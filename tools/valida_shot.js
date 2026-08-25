// Driver de captura da UI para a validação do pipeline.
// Uso: node valida_shot.js <rota> <nome-do-shot> [segundos-espera]
// Ex.: node valida_shot.js /project/PROJ/documents req-01-documentos 5
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'a1391183-f348-4a78-8773-8046b90a7676';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/validacao-pipeline/shots';
const route = process.argv[2].replace('PROJ', PROJ);
const name = process.argv[3];
const waitS = parseInt(process.argv[4] || '5', 10);
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1100 } });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`http://localhost:3000${route}`, { waitUntil: 'networkidle' });
  await sleep(waitS * 1000);
  await p.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
  // reporta títulos/headers visíveis pra eu saber o que apareceu
  const txt = await p.evaluate(() => document.body.innerText.slice(0, 400));
  console.log('SHOT:', name);
  console.log('TÍTULO/TOPO:', txt.replace(/\n+/g, ' | ').slice(0, 300));
  await b.close();
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
