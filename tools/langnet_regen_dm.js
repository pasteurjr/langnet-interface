// Clica "Regenerar do zero" no Modelo de Dados pela UI. Uso: node langnet_regen_dm.js
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1050 } });
  let fired=false;
  p.on('request', r => { if (r.method()==='POST' && /data-model\/.*\/generate|data-model\/?$/.test(r.url())) { fired=true; console.log('NET_POST_REGEN:', r.url().split('/api/')[1]); } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/data-model`,{ waitUntil:'networkidle' });
  await sleep(3500);
  const btn = p.locator('button', { hasText: /Regenerar do zero/i }).first();
  console.log('Regenerar btn:', await btn.count());
  await btn.click();
  await sleep(2500);
  // pode abrir um confirm/modal
  const conf = p.locator('button', { hasText: /Confirmar|Sim|Regenerar|OK/i }).last();
  if (await conf.count()) { try { await conf.click(); } catch(e){} }
  await sleep(4000);
  console.log('POST_DISPAROU:', fired);
  await p.screenshot({ path: `${OUT}/dm-regen-disparado.png`, fullPage: true });
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
