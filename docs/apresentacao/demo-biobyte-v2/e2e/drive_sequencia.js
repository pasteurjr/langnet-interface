// Etapa Sequência de Tarefas: escolhe as TRÊS origens obrigatórias e gera o fluxo.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '411', 10);
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
  await p.goto(`http://localhost:3001/project/${PROJ}/task-execution-flow`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  await shot(p,'sequencia-etapa-aberta');
  await p.getByRole('button',{name:/Specs & Docs/i}).first().click(); await sleep(3000);
  // as três abas do modal (.tab-button) e, em cada uma, o item mais recente (.session-item)
  for (const nome of ['Especificação Funcional','Especificação de Agentes','Tasks YAML']) {
    const ok = await p.evaluate((n)=>{
      const abas=[...document.querySelectorAll('.yaml-selection-tabs .tab-button')];
      const a=abas.find(b=>(b.textContent||'').includes(n.slice(0,18)));
      if(!a) return false; a.click(); return true;
    }, nome);
    await sleep(2500);
    const escolhido = await p.evaluate(()=>{
      const it=document.querySelector('.yaml-selection-modal-body .session-item');
      if(!it) return null; it.click(); return (it.textContent||'').replace(/\s+/g,' ').slice(0,58);
    });
    console.log(nome, '| aba:', ok, '| escolhido:', escolhido);
    await sleep(2000);
  }
  await shot(p,'sequencia-tres-origens');
  const conf = p.getByRole('button',{name:/Selecione os 3 Documentos|Confirmar/i}).first();
  if (await conf.count()) { await conf.click({force:true}).catch(()=>{}); await sleep(2500); }
  const btn = p.getByRole('button',{name:/Gerar Sequência de Tarefas/i}).first();
  const off = await btn.isDisabled().catch(()=>true);
  console.log('botão Gerar desabilitado?', off);
  if (off) { console.log('estado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,300)); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração disparada', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p,'sequencia-gerando');
  for (let i=0;i<150;i++){ await sleep(10000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (/passos|fluxo|sequência gerada/i.test(t) && !/Gerando|Processando/i.test(t)) break; }
  await sleep(2500); await shot(p,'sequencia-pronta');
  await b.close();
})();
