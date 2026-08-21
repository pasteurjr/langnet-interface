// Captura o detalhe de UMA tela da UI Spec. Uso: node langnet_uispec_screen.js "<nome>" <shot>
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const name = process.argv[2], shot = process.argv[3];
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1050 } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/ui-spec`,{ waitUntil:'networkidle' });
  await sleep(3500);
  const item = p.getByText(name, { exact: true }).first();
  await item.click(); await sleep(1800);
  // confirma seleção pelo título do painel de detalhe
  const title = await p.evaluate(()=>{ const h=document.querySelector('main h1, h2'); return h?h.innerText:''; });
  console.log('DETALHE_TITULO:', title);
  await p.screenshot({ path: `${OUT}/${shot}.png`, fullPage: true });
  // dump do painel de detalhe (componentes/campos)
  const txt = await p.evaluate(()=>document.body.innerText);
  const start = txt.indexOf('Componentes');
  console.log('DETALHE:\n', txt.slice(start, start+600));
  console.log('---FLAGS---');
  ['nivel_urgencia','diagnostico_inicial','especialidade_encaminhada','detalhes_medicos'].forEach(f=>console.log(f, txt.includes(f)));
  await b.close(); console.log('DONE');
})().catch(e=>{ console.error('FALHOU:', e.message); process.exit(1); });
