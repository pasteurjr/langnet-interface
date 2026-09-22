const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N=parseInt(process.argv[2]||'431',10);
const PEDIDO=process.argv[3]||'';
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/petri-net`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(x=>/Refinar com o agente/i.test(x.textContent||'')); if(b)b.click();});
  await sleep(3000);
  const cx = p.locator('textarea').last();
  if (!await cx.count()) { console.log('!! caixa não achada'); await b.close(); return; }
  await cx.focus(); await p.keyboard.type(PEDIDO,{delay:1}); await sleep(600);
  await shot(p,'petri-pedido-de-ligacao');
  const ok = await p.evaluate(()=>{
    const b=[...document.querySelectorAll('button')].filter(x=>/^Enviar$|Refinar$/i.test((x.textContent||'').trim()) && !x.disabled);
    if(!b.length) return false; b[b.length-1].click(); return true;});
  console.log('enviado?', ok, new Date().toLocaleTimeString());
  for (let i=0;i<40;i++){ await sleep(10000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/lugares|atualizada|conclu/i.test(t) && !/Processando|Gerando/i.test(t)) break; }
  await sleep(3000); await shot(p,'petri-depois-do-refino');
  await b.close();
})();
