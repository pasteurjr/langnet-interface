// Aprova o inventário de ferramentas da etapa, pela interface.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '675', 10);
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1100}});
  p.on('dialog', d=>d.accept().catch(()=>{}));
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/tools-stage`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  await shot(p,'ferramentas-inventario-com-servicos');
  const ok = await p.evaluate(()=>{
    const b=[...document.querySelectorAll('button')].find(e=>/aprovar/i.test(e.textContent||'') && !e.disabled);
    if(!b) return false; b.click(); return true;});
  console.log(ok?'aprovação clicada':'!! botão Aprovar não disponível');
  await sleep(5000);
  await shot(p,'ferramentas-aprovadas');
  const t=await p.evaluate(()=>document.body.innerText);
  const i=t.indexOf('Ferramenta');
  console.log(t.slice(i,i+900));
  await b.close();
})();
