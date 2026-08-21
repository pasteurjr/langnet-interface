const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const PORT = process.argv[2] || '5014';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1050 } });
  let fired=false, status=0;
  p.on('request', r => { if (r.method()==='POST' && /code-generation\/.*\/generate/.test(r.url())) { fired=true; console.log('NET_POST_GEN:', r.url().split('/api/')[1]); } });
  p.on('response', r => { if (r.request().method()==='POST' && /code-generation\/.*\/generate/.test(r.url())) { status=r.status(); console.log('NET_RESP_GEN:', r.status()); } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/code-generation`,{ waitUntil:'networkidle' });
  await sleep(3500);
  await p.locator('button', { hasText: /Nova geração/i }).first().click();
  // espera selects renderizarem
  let nsel=0;
  for (let i=0;i<30;i++){ nsel = await p.locator('select').count(); if (nsel>=2) break; await sleep(1000); }
  console.log('n_selects:', nsel);
  if (nsel < 2) { await p.screenshot({ path:`${OUT}/codegen-modal-semselect.png`, fullPage:true }); console.log('SEM_SELECTS'); await b.close(); process.exit(3); }
  // loga opções
  const opts = await p.evaluate(()=>Array.from(document.querySelectorAll('select')).map(s=>Array.from(s.options).map(o=>o.text.slice(0,45))));
  opts.forEach((o,i)=>console.log('SELECT'+i+':', JSON.stringify(o)));
  // seleciona agents.yaml (0) e tasks.yaml (1) — índice 1 (1ª opção real, mais recente)
  await p.locator('select').nth(0).selectOption({ index: 1 });
  await p.locator('select').nth(1).selectOption({ index: 1 });
  // agent-task spec (recomendado) se existir como 4º select
  if (nsel >= 4) { try { await p.locator('select').nth(3).selectOption({ index: 1 }); } catch(e){} }
  // porta
  const portInput = p.locator('input[type=number], input[value="5002"]').first();
  if (await portInput.count()) { await portInput.fill(PORT); }
  await sleep(800);
  await p.screenshot({ path: `${OUT}/codegen-preenchido.png`, fullPage: true });
  const gen = p.locator('button', { hasText: /^Gerar Código$/ }).last();
  const dis = await gen.isDisabled().catch(()=>true);
  console.log('botao_habilitado:', !dis);
  await gen.click();
  await sleep(5000);
  console.log('POST_DISPAROU:', fired, '| status:', status);
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
