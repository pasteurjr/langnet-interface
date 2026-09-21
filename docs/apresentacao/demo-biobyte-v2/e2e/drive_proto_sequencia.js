// Sequência COMPLETA da geração do protótipo: acionar, montar, abrir fora e navegar.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '276', 10);
const ALVOS = process.argv.slice(3);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const nome=t=>t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').slice(0,34);
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(10000);
  await p.evaluate(()=>{const e=[...document.querySelectorAll('.uispec-item')].find(x=>/^UC-001/.test((x.textContent||'').trim())); if(e)e.click();});
  await sleep(2500);
  await p.evaluate(()=>{const e=document.querySelector('.uispec-body'); if(e)e.scrollIntoView({block:'start'});});
  await sleep(1200);
  await shot(p,'uispec-antes-de-renderizar');
  const bt = p.getByRole('button',{name:/renderizar prot/i}).first();
  await bt.click({force:true}).catch(()=>{});
  console.log('▷ Renderizar acionado', new Date().toLocaleTimeString());
  await sleep(4000); await shot(p,'uispec-montando-o-prototipo');
  for(let i=0;i<40;i++){ await sleep(4000);
    const t=await p.evaluate(()=>document.body.innerText);
    if(!/Renderizando/i.test(t)) break; }
  await sleep(3000);
  await p.evaluate(()=>{const e=document.querySelector('.uispec-proto'); if(e)e.scrollIntoView({block:'start'});});
  await sleep(1500); await shot(p,'uispec-prototipo-montado-na-etapa');
  const url = await p.evaluate(()=>{const f=document.querySelector('iframe[title="protótipo"]'); return f?f.getAttribute('src'):'';});
  console.log('endereço:', (url||'(vazio)').slice(0,90));
  if (url) {
    const q = await b.newPage({viewport:{width:1600,height:1000}});
    await q.goto(url,{waitUntil:'domcontentloaded'}); await sleep(5000);
    await shot(q,'prototipo-aberto-fora-do-langnet');
    for (const alvo of ALVOS) {
      const ok = await q.evaluate((a)=>{const e=[...document.querySelectorAll('a')]
        .find(x=>new RegExp(a,'i').test(x.textContent||'')); if(!e) return false; e.click(); return true;},alvo);
      if(!ok){ console.log('!! não achei no menu:', alvo); continue; }
      await sleep(3000); console.log('→', alvo);
      await shot(q,'prototipo-'+nome(alvo));
    }
  }
  await b.close();
})();
