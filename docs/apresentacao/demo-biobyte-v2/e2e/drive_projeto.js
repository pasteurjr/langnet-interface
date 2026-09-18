// Cria o projeto novo do BioByte pela interface e captura cada momento.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1', 10);
const BASE = 'http://localhost:3001';
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF = '/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const shot = async (p, tag) => {
  const f = `${OUT}/${String(N).padStart(3,'0')}-${tag}.png`;
  await p.screenshot({ path: f, timeout: 60000 });
  console.log('📸', f.split('/').pop()); N++;
};
(async () => {
  const b = await firefox.launch({ headless: true, executablePath: FF });
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  p.on('console', m => { if (m.type() === 'error') console.log('ERRO:', m.text().slice(0, 110)); });
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`${BASE}/projects`, { waitUntil: 'domcontentloaded' });
  await sleep(6000);
  await shot(p, 'lista-de-projetos');
  // botão de novo projeto
  const abriu = await p.evaluate(() => {
    const b = [...document.querySelectorAll('button,a')].find(e => /novo projeto|criar projeto|\+ *novo/i.test(e.textContent || ''));
    if (!b) return 'botão de novo projeto não achado';
    b.click(); return 'formulário aberto';
  });
  console.log(abriu);
  await sleep(3000);
  await shot(p, 'formulario-novo-projeto');
  console.log('campos do formulário:', await p.evaluate(() => [...document.querySelectorAll('input,textarea,select')]
    .map(c => ({ rotulo: ((c.closest('div')?.textContent) || c.placeholder || '').trim().slice(0, 40), tipo: c.tagName }))
    .filter(x => x.rotulo).slice(0, 12)));
  await b.close();
})();
