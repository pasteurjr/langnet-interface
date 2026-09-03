// Regenera o código pela INTERFACE do LangNet (botão Nova geração) e captura as telas.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
let N = parseInt(process.argv[2] || '520', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  let sessao='';
  p.on('response',async r=>{ if(r.request().method()==='POST' && /code-generation\/.*\/generate/.test(r.url())){
    try{ sessao=(await r.json()).session_id||''; }catch(e){} console.log('NET geração →', r.status(), sessao); }});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/code-generation`,{waitUntil:'domcontentloaded'});
  await p.getByText('Geração de Código').first().waitFor({timeout:40000}); await sleep(3000);
  await shot(p,'geracao-antes');
  await p.getByRole('button',{name:/Nova geração/}).click({timeout:15000});
  await sleep(2500);
  // escolhe os artefatos de origem (agents.yaml e tasks.yaml são obrigatórios; ATS é recomendado)
  const sels = p.locator('.modal select, [role=dialog] select, select');
  const n = await sels.count();
  for (const idx of [0,1,3]) {
    if (idx >= n) continue;
    const val = await sels.nth(idx).evaluate(el => { const o=[...el.options].find(o=>o.value); return o?o.value:''; });
    if (val) { await sels.nth(idx).selectOption(val).catch(()=>{}); console.log('  origem', idx, '=', val.slice(0,8)); }
  }
  await sleep(800); await shot(p,'geracao-modal');
  const btn=p.getByRole('button',{name:/Gerar Código/}).last();
  await btn.click({timeout:15000}); console.log('▷ geração disparada');
  for(let i=0;i<70;i++){ await sleep(10000);
    if(i===1) await shot(p,'geracao-em-andamento');
    if(sessao) break;
  }
  await sleep(4000); await shot(p,'geracao-concluida');
  console.log('SESSÃO GERADA:', sessao);
  fs.writeFileSync('/tmp/regen_session.txt', sessao||'');
  await b.close(); console.log('DONE próximo índice', N);
})().catch(e=>{console.error('FALHOU',e.message);process.exit(1);});
