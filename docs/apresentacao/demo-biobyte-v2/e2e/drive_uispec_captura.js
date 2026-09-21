// Captura a etapa de Interface JÁ GERADA: a tela da etapa, a lista de telas e alguns mockups.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '191', 10);
const ALVOS = process.argv.slice(3);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const nome=t=>t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40);
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(10000);
  await shot(p,'uispec-etapa-com-33-telas');
  for (const alvo of ALVOS) {
    const ok = await p.evaluate((a)=>{
      const e=[...document.querySelectorAll('div,li,button,a,span')]
        .filter(x=>x.offsetParent && (x.textContent||'').trim().length<70
                   && new RegExp(a,'i').test(x.textContent||''));
      if(!e.length) return false; (e[0].closest('li,button,a,div[role],div')||e[0]).click(); return true;
    }, alvo);
    if(!ok){ console.log('!! não achei:', alvo); continue; }
    await sleep(3000); console.log('→', alvo);
    await shot(p,'uispec-tela-'+nome(alvo));
  }
  await b.close();
})();
