// Refino da etapa Ferramentas pela conversa, com captura.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '381', 10);
const PEDIDO = process.argv[3] || '';
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,110));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/tools-stage`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  // abrir a ferramenta pendente para a conversa agir sobre ela
  await p.evaluate(()=>{const e=[...document.querySelectorAll('*')].find(x=>/json_parser_tool/.test(x.textContent||'')&&x.children.length===0); if(e&&e.parentElement)e.parentElement.click();});
  await sleep(2500);
  await shot(p,'ferramentas-pendencia');
  const ta = p.locator('textarea').last();
  if (!await ta.count()) { console.log('!! caixa não achada'); await b.close(); return; }
  await ta.focus(); await p.keyboard.type(PEDIDO,{delay:1}); await sleep(600);
  await shot(p,'ferramentas-pedido');
  const btn = p.getByRole("button",{name:/^Enviar$/i}).first();
  await btn.click({timeout:20000,force:true}).catch(e=>console.log('clique:',String(e.message).split('\n')[0]));
  console.log('▷ refino disparado', new Date().toLocaleTimeString());
  for (let i=0;i<40;i++){ await sleep(8000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/resolvidas/i.test(t) && !/Processando/i.test(t)) break; }
  await sleep(2500); await shot(p,'ferramentas-depois-do-refino');
  console.log('estado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,300));
  await b.close();
})();
