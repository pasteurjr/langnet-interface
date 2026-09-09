// Captura a tela NOVA "Configurações do Projeto" (escolha do modelo da aplicação gerada).
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1300', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,200));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  // Entra PELO projeto: sem isso o menu lateral fica no contexto global e o vídeo não mostra
  // as treze etapas do pipeline.
  await p.goto(`${BASE}/projects`,{waitUntil:'domcontentloaded'}); await sleep(2500);
  const cartao = p.locator('text=BioByte Sentinela').first();
  if (await cartao.count()) { await cartao.click(); await sleep(3000); }
  await p.goto(`${BASE}/project/${PROJ}/settings`,{waitUntil:'domcontentloaded'});
  await sleep(4000);
  console.log('tela:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,400));
  await shot(p,'config-projeto-modelo');
  // troca para DeepSeek e volta, para o vídeo mostrar que a escolha é real
  const dsk = p.locator('label.opcao', { hasText: /DeepSeek/i }).first();
  if (await dsk.count()) { await dsk.click(); await sleep(2500); await shot(p,'config-projeto-deepseek'); }
  const cc = p.locator('label.opcao', { hasText: /Claude/i }).first();
  if (await cc.count()) { await cc.click(); await sleep(2500); await shot(p,'config-projeto-claude'); }
  console.log('final:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,300));
  await b.close();
})();
