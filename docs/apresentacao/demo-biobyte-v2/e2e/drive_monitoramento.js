// Etapa Monitoramento: mostra o que o sistema implantado executou de verdade.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '870', 10);
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1100}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/monitoring`,{waitUntil:'domcontentloaded'});
  await sleep(10000);
  await shot(p,'monitoramento-tarefas');
  for (const [rot,nome] of [['externas','monitoramento-servicos-externos'],['registro','monitoramento-registro']]){
    const ok = await p.evaluate((r)=>{const b=[...document.querySelectorAll('button,div,span')].find(x=>new RegExp(r,'i').test((x.textContent||'').trim()) && (x.textContent||'').length<40); if(b){b.click();return true;} return false;}, rot);
    await sleep(4000); await shot(p,nome); console.log(rot, ok?'aberta':'não achei');
  }
  const t=await p.evaluate(()=>document.body.innerText);
  const i=t.indexOf('Monitoramento');
  console.log(t.slice(i, i+1200));
  await b.close();
})();
