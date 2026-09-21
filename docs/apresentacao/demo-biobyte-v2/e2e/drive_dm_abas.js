// Fotografa as ABAS DE ENTREGA do Modelo de Dados: Schema SQL, models.py, Alembic e YAML.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '187', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const nome=t=>t.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/data-model`,{waitUntil:'domcontentloaded'});
  await sleep(9000);
  for (const aba of ['Schema SQL','models.py','Alembic','YAML']) {
    const ok = await p.evaluate((a)=>{
      const e=[...document.querySelectorAll('button,div,span,li,a')]
        .filter(x=>(x.textContent||'').trim()===a && x.offsetParent);
      if(!e.length) return false; (e[0].closest('button,li,a')||e[0]).click(); return true;
    }, aba);
    if(!ok){ console.log('!! aba não achada:', aba); continue; }
    await sleep(2500); console.log('→', aba);
    await shot(p,'dm-aba-'+nome(aba));
  }
  await b.close();
})();
