// Regera a etapa de CASOS DE TESTE pela interface do LangNet e captura as telas.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '930', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  let sessao='';
  p.on('response',async r=>{ if(r.request().method()==='POST' && /test-cases\/.*\/generate/.test(r.url())){
    try{ sessao=(await r.json()).session_id||''; }catch(e){} console.log('NET geração →', r.status(), sessao); }});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/test-cases`,{waitUntil:'domcontentloaded'});
  await sleep(5000);
  await shot(p,'casos-teste-antes');
  const btn=p.getByRole('button',{name:/Gerar casos de teste/i}).first();
  if(!await btn.count()){ console.log('botão não encontrado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração de casos disparada');
  for(let i=0;i<120;i++){ await sleep(5000);
    const t=await p.evaluate(()=>document.body.innerText).catch(()=>'');
    if(/UC-0\d+/.test(t) && !/Gerando|Processando/i.test(t)) break;
    if(i===2) await shot(p,'casos-teste-gerando');
  }
  await sleep(2000);
  await shot(p,'casos-teste-gerados');
  console.log('SESSÃO:', sessao);
  await b.close();
  console.log('DONE casos próximo índice', N);
})();
