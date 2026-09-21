// Altera UMA tela pela conversa da etapa e captura antes/depois.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '273', 10);
const UC = process.argv[3] || 'UC-001';
const PEDIDO = process.argv[4] || '';
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const rolar=async p=>{await p.evaluate(()=>{const e=document.querySelector('.uispec-body'); if(e)e.scrollIntoView({block:'start'});}); await sleep(1200);};
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(10000);
  await p.evaluate((uc)=>{const e=[...document.querySelectorAll('.uispec-item')]
    .find(x=>new RegExp('^'+uc).test((x.textContent||'').trim())); if(e)e.click();},UC);
  await sleep(2500); await rolar(p);
  await shot(p,'uispec-tela-antes-do-ajuste');
  // a conversa da etapa começa RECOLHIDA — é preciso abrir antes de escrever
  const abrir = p.getByRole('button',{name:/refinar com o agente|mostrar chat/i}).first();
  if (await abrir.count()) { await abrir.click({force:true}).catch(()=>{}); await sleep(2500);
                             console.log('conversa aberta'); }
  const cx = p.getByPlaceholder(/^Refinar /i).first();
  if (!(await cx.count())) { console.log('!! caixa da conversa não achada'); await b.close(); return; }
  await cx.focus(); await p.keyboard.type(PEDIDO,{delay:2});
  await sleep(600); await shot(p,'uispec-pedido-de-ajuste');
  const env = p.getByRole('button',{name:/^refinar$/i}).first();
  if (!(await env.count())) { console.log('!! botão Enviar não achado'); await b.close(); return; }
  await env.click({force:true}).catch(()=>{});
  console.log('▷ pedido enviado', new Date().toLocaleTimeString());
  for (let i=0;i<40;i++){ await sleep(6000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/atualizada|Remontando|✅/i.test(t)) break; }
  await sleep(6000); await rolar(p);
  await shot(p,'uispec-tela-depois-do-ajuste');
  console.log(await p.evaluate(()=>{const m=[...document.querySelectorAll('*')]
    .filter(e=>e.children.length===0 && /atualizada|Remont|✅/i.test(e.textContent||''));
    return m.map(e=>(e.textContent||'').trim()).slice(-3).join(' | ');}));
  await b.close();
})();
