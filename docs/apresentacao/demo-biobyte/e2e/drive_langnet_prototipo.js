// Etapa Interface & Protótipo: gera as telas, monta o protótipo navegável e captura a navegação.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1370', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,150));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'uispec-etapa-aberta');
  console.log('tela:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(250,650));
  const btn = p.getByRole('button',{name:/Protótipo/i}).first();
  if (!await btn.count()) { console.log('!! botão Protótipo não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ montagem do protótipo às', new Date().toLocaleTimeString());
  for (let i=0;i<40;i++){ await sleep(5000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (!/Montando/i.test(t)) break; }
  await sleep(3000); await shot(p,'prototipo-montado');
  const quadro = p.frameLocator('iframe[title="protótipo"]');
  const itens = await quadro.locator('nav a, aside a, .menu a, li a, button').allTextContents().catch(()=>[]);
  console.log('telas do protótipo:', itens.filter(Boolean).slice(0,14).join(' · ').slice(0,300));
  await b.close();
})();
