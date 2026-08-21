// Aprova a versão corrente de uma etapa pela UI. Uso: node langnet_approve.js <stage> <shot>
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const stage = process.argv[2], shot = process.argv[3] || (stage+'-aprovado');
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1000 } });
  let approved=false;
  p.on('response', r => { if (r.request().method()==='POST' && /approve/.test(r.url())) { approved=true; console.log('NET_APPROVE:', r.status()); } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/${stage}`,{ waitUntil:'networkidle' });
  await sleep(3500);
  const btn = p.locator('button', { hasText: /Aprovar/i }).first();
  console.log('botão Aprovar:', await btn.count());
  if (await btn.count()) { await btn.click(); await sleep(3000); }
  await sleep(2000);
  await p.screenshot({ path: `${OUT}/${shot}.png`, fullPage: true });
  const txt = await p.evaluate(()=>document.body.innerText);
  console.log('STATUS_TXT:', (txt.match(/Aprovad[oa]|Rascunho/i)||['?'])[0]);
  console.log('APPROVED_NET:', approved);
  console.log('📸', shot); await b.close(); console.log('DONE');
})().catch(e=>{ console.error('FALHOU:', e.message); process.exit(1); });
