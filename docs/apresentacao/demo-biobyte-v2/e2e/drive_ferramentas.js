// Etapa Ferramentas: levanta o inventário a partir de Agentes & Tarefas e captura a sequência.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '370', 10);
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,120));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/tools-stage`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  await shot(p,'ferramentas-etapa-aberta');
  const btn = p.getByRole('button',{name:/Gerar a partir do ATS/i}).first();
  if (!await btn.count()) { console.log('!! botão não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ levantamento disparado às', new Date().toLocaleTimeString());
  await sleep(4000); await shot(p,'ferramentas-levantando');
  for (let i=0;i<120;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/resolvidas/i.test(t) && !/Processando/i.test(t)) break; }
  await sleep(2000); await shot(p,'ferramentas-inventario');
  console.log('resultado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,400));
  await b.close();
})();
