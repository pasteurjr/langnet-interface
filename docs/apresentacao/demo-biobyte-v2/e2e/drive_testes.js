// Etapa Casos de Teste: gera pelo grafo causa-efeito a partir da Especificação.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '436', 10);
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,110));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/test-cases`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  await shot(p,'testes-etapa-aberta');
  const ok = await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(x=>/Gerar casos de teste/i.test(x.textContent||'')); if(!b||b.disabled) return false; b.click(); return true;});
  console.log('disparado?', ok, new Date().toLocaleTimeString());
  await sleep(6000); await shot(p,'testes-gerando');
  for (let i=0;i<150;i++){ await sleep(10000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/casos de teste|CT-|tabela de decis/i.test(t) && !/Gerando|Processando/i.test(t) && !/Nenhum caso de teste gerado/i.test(t)) break; }
  await sleep(3000); await shot(p,'testes-prontos');
  console.log('estado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(250,520));
  await b.close();
})();
