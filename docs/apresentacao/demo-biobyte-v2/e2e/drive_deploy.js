// Etapa Implantação: configura o banco e o modelo do APP, implanta e captura.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '610', 10);
const FORCAR = process.argv[3] === 'forcar';
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
const CONF = { DB_HOST:'127.0.0.1', DB_PORT:'3308', DB_NAME:'biobyte_v4_app',
               DB_USER:'producao', DB_PASSWORD:'112358123', LLM_PROVIDER:'lmstudio' };
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  p.on('dialog', d=>d.accept().catch(()=>{}));
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,110));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/deploy`,{waitUntil:'domcontentloaded'});
  await sleep(9000);
  await shot(p,'deploy-etapa-aberta');
  // versão de código: a mais recente
  const v = await p.evaluate(()=>{
    const s=document.querySelector('select'); if(!s) return null;
    const o=[...s.options].filter(x=>x.value && !/selecione/i.test(x.textContent||''));
    if(!o.length) return null; s.value=o[0].value; s.dispatchEvent(new Event('change',{bubbles:true}));
    return o[0].textContent.trim().slice(0,50);
  });
  console.log('versão de código:', v);
  await sleep(2500);
  // configuração
  const preenchidos = await p.evaluate((conf)=>{
    let n=0;
    document.querySelectorAll('input').forEach(i=>{
      const rot=((i.closest('label')||{}).textContent||'').toLowerCase();
      for (const [k,val] of Object.entries(conf)) {
        const ph=(i.placeholder||'').toUpperCase();
        if (ph===k || rot.includes(k.toLowerCase().replace('db_','').replace('_',' '))) {
          const set=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); n++; break;
        }
      }
    });
    return n;
  }, CONF);
  console.log('campos preenchidos:', preenchidos);
  await sleep(1500); await shot(p,'deploy-configuracao');
  // pendências dos portões, se houver
  const temPortoes = await p.evaluate(()=>/pendênc|barrada/i.test(document.body.innerText));
  if (temPortoes) await shot(p,'deploy-pendencias-dos-portoes');
  // implantar
  let ok = await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(x=>/Implantar esta versão/i.test(x.textContent||'')&&!x.disabled); if(!b) return false; b.click(); return true;});
  console.log('botão implantar?', ok);
  await sleep(4000);
  if (FORCAR) {
    const f = await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(x=>/forçar|mesmo assim|Implantar assim/i.test(x.textContent||'')&&!x.disabled); if(!b) return false; b.click(); return true;});
    console.log('decisão explícita (forçar)?', f);
    await sleep(4000);
  }
  await shot(p,'deploy-em-andamento');
  for (let i=0;i<90;i++){ await sleep(10000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/no ar|falhou|parada/i.test(t) && !/implantando|instalando|preparando/i.test(t)) break; }
  await sleep(3000); await shot(p,'deploy-resultado');
  console.log('estado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(250,520));
  await b.close();
})();
