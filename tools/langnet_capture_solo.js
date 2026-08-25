const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/solo-v3-tutorial/shots';
const PROJ = 'c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const stage = process.argv[2], shot = process.argv[3], tab = process.argv[4] || '';
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1200 } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/${stage}`,{ waitUntil:'networkidle' });
  await sleep(4000);
  if (tab) { const t = p.locator('button',{ hasText: new RegExp('^'+tab+'$') }).first(); if (await t.count()) { await t.click(); await sleep(1500); } }
  await p.screenshot({ path: `${OUT}/${shot}.png`, fullPage: true });
  const txt = await p.evaluate(()=>document.body.innerText);
  console.log('VALIDACAO:', (txt.match(/Valida[cç][aã]o[^\n]*/i)||['(sem)'])[0]);
  console.log('📸', shot); await b.close(); console.log('DONE');
})().catch(e=>{ console.error('FALHOU:', e.message); process.exit(1); });
