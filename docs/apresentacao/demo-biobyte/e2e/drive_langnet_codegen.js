// Captura, na interface do LangNet, a etapa Geração de Código do BioByte com as versões reais (v6/v7).
const { firefox: chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let N=200;
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`; await p.screenshot({path:f,fullPage:false, timeout:90000}); console.log('📸',f.split('/').pop()); N++;};
(async()=>{
  const b=await chromium.launch({headless:true, executablePath:'/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox'}); const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/code-generation`,{waitUntil:'networkidle'}).catch(()=>{});
  await sleep(3000); await shot(p,'codegen-pagina');
  const body=await p.locator('body').innerText().catch(()=> '');
  console.log('texto da página (trecho):', body.replace(/\s+/g,' ').slice(0,400));
  for (const label of [/Vers(ões|oes)|Hist(ó|o)rico/i, /Ver Diferen/i]) {
    const btn=p.getByRole('button',{name:label}).first();
    if (await btn.count().catch(()=>0)) { await btn.click().catch(()=>{}); await sleep(2000); await shot(p, String(label).replace(/[^a-z]/gi,'').slice(0,18).toLowerCase()); }
    else console.log('sem botão', String(label));
  }
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU',e.message);process.exit(1);});
