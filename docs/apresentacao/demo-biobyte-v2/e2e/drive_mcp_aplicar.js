// Aplica as três atribuições certas de ferramenta externa aos agentes, pela interface.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '663', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
const PARES=[['microbiology_integration_agent','consultar_microbiologia'],
             ['cox_score_agent','escore_risco_cox'],
             ['notification_agent','enviar_email']];
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1100}});
  p.on('dialog', d=>d.accept().catch(()=>{}));
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/mcp`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(e=>/sugerir atribui/i.test(e.textContent||'')); if(b) b.click();});
  await sleep(5000);
  await shot(p,'ferramentas-sugeridas');
  for (const [ag,tool] of PARES){
    const ok = await p.evaluate(([ag,tool])=>{
      for (const bt of document.querySelectorAll('button')){
        if (!/aplicar/i.test(bt.textContent||'')) continue;
        const linha = bt.parentElement ? bt.parentElement.textContent||'' : '';
        if (linha.includes(ag) && linha.includes(tool)) { bt.click(); return true; }
      }
      return false;
    },[ag,tool]);
    console.log(ok?`aplicado: ${ag} ← ${tool}`:`!! não achei ${ag} ← ${tool}`);
    await sleep(2500);
  }
  await sleep(3000);
  await shot(p,'ferramentas-atribuidas-aos-agentes');
  const txt = await p.evaluate(()=>document.body.innerText);
  const i = txt.indexOf('Agentes e suas ferramentas');
  console.log(txt.slice(i, i+700));
  await b.close();
})();
