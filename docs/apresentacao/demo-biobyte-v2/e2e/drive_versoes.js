// Abre o documento refinado e a comparação entre a versão 1 e a 2.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '115', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  const hist = p.getByRole('button',{name:/hist[óo]rico/i}).first();
  await hist.click({force:true}).catch(()=>{}); await sleep(3000);
  const voltar = p.getByRole('button',{name:/voltar para lista de documentos/i}).first();
  if (await voltar.count()) { await voltar.click({force:true}).catch(()=>{}); await sleep(2500); }
  await p.evaluate(()=>{const a=[...document.querySelectorAll('div,li,tr,button')]
    .filter(e=>/Document Analysis/i.test(e.textContent||'')&&(e.textContent||'').length<200
               &&e.querySelectorAll('div,li,tr').length<4); if(a.length)a[0].click();});
  await sleep(4000);
  await shot(p,'historico-com-duas-versoes');
  // abre a versao 2 (a mais recente)
  const vers = await p.evaluate(()=>[...document.querySelectorAll('*')]
     .filter(e=>/Vers[ãa]o 2/i.test(e.textContent||'')&&(e.textContent||'').length<300).length);
  console.log('encontrou Versão 2 na tela:', vers>0);
  const comparar = p.getByRole('button',{name:/comparar|diferen|diff/i}).first();
  if (await comparar.count()) {
    await comparar.click({force:true}).catch(()=>{}); await sleep(4000);
    await shot(p,'comparacao-entre-versoes');
  } else {
    console.log('!! botão de comparar não encontrado — listando botões do modal');
    console.log(await p.evaluate(()=>[...document.querySelectorAll('button')].map(b=>(b.textContent||'').trim()).filter(Boolean).slice(0,25).join(' | ')));
  }
  const ver = p.getByText(/Clique para visualizar/i).first();
  if (await ver.count()) { await ver.click({force:true}).catch(()=>{}); await sleep(4000); }
  const fechar = p.getByRole('button',{name:/^fechar$/i}).first();
  if (await fechar.count()) { await fechar.click({force:true}).catch(()=>{}); await sleep(2500); }
  await shot(p,'documento-depois-do-refino');
  await b.close();
})();
