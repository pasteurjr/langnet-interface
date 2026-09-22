// Etapa Rede de Petri: escolhe agents.yaml + tasks.yaml + Sequência e gera a rede.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '427', 10);
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
  await p.goto(`http://localhost:3001/project/${PROJ}/petri-net`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  await shot(p,'petri-etapa-aberta');
  await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(x=>/Gerar Rede \/ Origem/i.test(x.textContent||'')); if(b)b.click();});
  await sleep(3500);
  const escolhas = await p.evaluate(()=>{
    const out=[];
    document.querySelectorAll('select').forEach(s=>{
      const ops=[...s.options].filter(o=>o.value);
      if(ops.length){ s.value=ops[0].value; s.dispatchEvent(new Event('change',{bubbles:true}));
                      out.push(ops[0].textContent.trim().slice(0,52)); }
    });
    return out;
  });
  console.log('origens escolhidas:', JSON.stringify(escolhas));
  const INSTR = process.argv[3] || '';
  if (INSTR) {
    const ta = p.locator('textarea').first();
    if (await ta.count()) { await ta.focus(); await p.keyboard.type(INSTR,{delay:1}); console.log('instruções escritas'); }
  }
  await sleep(2000); await shot(p,'petri-origens');
  const disparou = await p.evaluate(()=>{
    const bs=[...document.querySelectorAll('button')].filter(x=>/^Gerar Rede$/i.test((x.textContent||'').trim()));
    const b=bs[bs.length-1]; if(!b) return false; b.click(); return true;});
  console.log('botão Gerar Rede acionado?', disparou);
  console.log('▷ geração disparada', new Date().toLocaleTimeString());
  await sleep(6000); await shot(p,'petri-gerando');
  for (let i=0;i<120;i++){ await sleep(10000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/lugares|transições|rede gerada/i.test(t) && !/Gerando|Processando/i.test(t)) break; }
  await sleep(3000); await shot(p,'petri-rede');
  console.log('estado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,260));
  await b.close();
})();
