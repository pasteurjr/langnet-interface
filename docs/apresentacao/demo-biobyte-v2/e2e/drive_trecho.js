// Fotografa TRECHOS LEGÍVEIS do documento de requisitos, em vez da página inteira miniaturizada.
// Uso: node drive_trecho.js <numero-inicial> "<titulo-1>" "<titulo-2>" ...
// Cada título é procurado no texto do documento aberto; a página rola até ele e a captura sai
// com o trecho no topo da tela, em tamanho de leitura.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '20', 10);
const ALVOS = process.argv.slice(3);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const nome=t=>t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40);
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  // abre o documento de requisitos
  const abriu = await p.evaluate(()=>{
    const b=[...document.querySelectorAll('button,a')].find(e=>/ver documento|visualizar|abrir documento/i.test(e.textContent||''));
    if(!b) return false; b.click(); return true;});
  if(!abriu){ console.log('!! botão de abrir o documento não encontrado'); await b.close(); return; }
  await sleep(4000);
  await shot(p,'documento-de-requisitos-aberto');
  for (const alvo of ALVOS) {
    const achou = await p.evaluate((txt)=>{
      const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
      const alvo=norm(txt);
      const cand=[...document.querySelectorAll('h1,h2,h3,h4,h5,strong,p,li,td')]
        .find(e=>norm(e.textContent||'').includes(alvo));
      if(!cand) return null;
      cand.scrollIntoView({block:'start'});
      // sobe um pouco para o título não colar no topo
      const sc=cand.closest('[style*="overflow"],.modal-body,.markdown-body')||document.scrollingElement;
      if(sc && sc.scrollTop>40) sc.scrollTop -= 40;
      return (cand.textContent||'').trim().slice(0,70);
    }, alvo);
    if(!achou){ console.log('!! não achei:', alvo); continue; }
    console.log('→', achou);
    await sleep(900);
    await shot(p,'trecho-'+nome(alvo));
  }
  await b.close();
})();
