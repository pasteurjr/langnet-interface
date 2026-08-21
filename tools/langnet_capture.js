// Captura o estado de uma etapa da UI do LangNet. Uso: node langnet_capture.js <stage> <shot> [tabName]
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const stage = process.argv[2], shot = process.argv[3], tab = process.argv[4] || '';
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1150 } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/${stage}`,{ waitUntil:'networkidle' });
  await sleep(3800);
  if (tab) { const t = p.locator('button',{ hasText: new RegExp('^'+tab+'$') }).first(); if (await t.count()) { await t.click(); await sleep(1500); } }
  await p.screenshot({ path: `${OUT}/${shot}.png`, fullPage: true });
  const txt = await p.evaluate(()=>document.body.innerText);
  console.log('VALIDACAO:', (txt.match(/Valida[cç][aã]o[^\n]*/i)||['(sem)'])[0]);
  console.log('VERSAO:', (txt.match(/Vers[aã]o\s*v?\d+/i)||['?'])[0]);
  console.log('CHK_CASCADE:', /ON DELETE CASCADE/i.test(txt), '| CHK_idade:', /CHECK\s*\(\s*idade/i.test(txt), '| CHK_ts:', /data_criacao\s+TIMESTAMP/i.test(txt));
  console.log('📸', shot); await b.close(); console.log('DONE');
})().catch(e=>{ console.error('FALHOU:', e.message); process.exit(1); });
