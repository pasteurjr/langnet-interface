const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const stage = process.argv[2] || 'ui-spec';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1000 } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/${stage}`,{ waitUntil:'networkidle' });
  await sleep(3500);
  const rb = p.locator('button', { hasText: /Refinar/i }).first();
  console.log('Refinar btn:', await rb.count());
  if (await rb.count()) { await rb.click(); await sleep(2000); }
  await p.screenshot({ path: `${OUT}/${stage}-refine-explore.png`, fullPage: true });
  const els = await p.evaluate(() => {
    const o = [];
    document.querySelectorAll('textarea,input,button').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.width>0 && r.height>0) o.push({ tag:e.tagName, ph:e.placeholder||'', txt:(e.innerText||e.value||'').slice(0,30) });
    });
    return o;
  });
  console.log('ELEMENTS:');
  els.forEach(e => console.log('  ', e.tag, '| ph:', JSON.stringify(e.ph), '| txt:', JSON.stringify(e.txt)));
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
