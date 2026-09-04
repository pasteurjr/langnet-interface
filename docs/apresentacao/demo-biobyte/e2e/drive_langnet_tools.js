// Dirige a nova etapa FERRAMENTAS pela interface do LangNet e captura as telas.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '900', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,180));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/tools-stage`,{waitUntil:'domcontentloaded'});
  await sleep(4000);
  const corpo = await p.evaluate(()=>document.body.innerText.slice(0,300));
  console.log('tela:', corpo.replace(/\n/g,' | ').slice(0,220));
  await shot(p,'ferramentas-etapa');
  const btn = p.getByRole('button',{name:/Gerar a partir do ATS/i}).first();
  if (await btn.count()) {
    await btn.click({timeout:15000});
    console.log('▷ geração disparada');
    for (let i=0;i<60;i++){ await sleep(3000);
      const t = await p.evaluate(()=>document.body.innerText);
      if (/Ferramentas\s+\d|Com implementação/i.test(t) && !/Processando/i.test(t)) break; }
    await sleep(1500);
    const t = await p.evaluate(()=>document.body.innerText.slice(0,700));
    console.log('resultado:', t.replace(/\n/g,' | ').slice(0,500));
    await shot(p,'ferramentas-inventario');
  } else { console.log('botão Gerar não encontrado'); }
  await b.close();
  console.log('DONE ferramentas próximo índice', N);
})();
