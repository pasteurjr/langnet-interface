const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1050 } });
  p.on('request', r => { if (r.method()==='POST' && /generate|code-generation/.test(r.url())) console.log('NET_POST:', r.url().split('/api/')[1]); });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/code`,{ waitUntil:'networkidle' });
  await sleep(3500);
  const btn = p.locator('button', { hasText: /Gerar\/Atualizar/i }).first();
  if (await btn.count()) { await btn.click(); await sleep(2500); }
  // clica o botão verde "Gerar Código Python" dentro do modal
  const genBtn = p.locator('button', { hasText: /Gerar Código Python/i }).last();
  console.log('Gerar Código Python btn:', await genBtn.count());
  let fired=false;
  p.on('request', r => { if (r.method()==='POST' && /generate/.test(r.url())) { fired=true; console.log('NET_POST_GEN:', r.url().split('/api/')[1]); } });
  if (await genBtn.count()) { await genBtn.click(); }
  await sleep(6000);
  await p.screenshot({ path: `${OUT}/code-gen-clicked.png`, fullPage: true });
  const txt = await p.evaluate(()=>document.body.innerText);
  console.log('POST_DISPAROU:', fired);
  console.log('APOS_CLIQUE_MENCIONA_ERRO:', /erro|falha|error/i.test(txt.slice(0,400)));
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
