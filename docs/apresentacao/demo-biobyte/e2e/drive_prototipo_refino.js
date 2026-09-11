// O TESTE: monta o protótipo, aponta um componente, pede a mudança ao agente e captura o
// antes/depois — o protótipo tem de se remontar sozinho.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1375', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,120));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  // 1) montar o protótipo das telas novas
  const btnProto = p.getByRole('button',{name:/Protótipo/i}).first();
  if (!await btnProto.count()) { console.log('!! botão Protótipo não achado'); await b.close(); return; }
  await btnProto.click({timeout:20000});
  for (let i=0;i<40;i++){ await sleep(5000);
    if (!/Montando/i.test(await p.evaluate(()=>document.body.innerText))) break; }
  await sleep(3000); await shot(p,'proto-montado-telas-novas');

  // 2) navegar no protótipo até a tela do escore de Cox e mostrar o APACHE II lá
  const q = p.frameLocator('iframe[title="protótipo"]');
  const linkCox = q.locator('a,li,button').filter({hasText:/Progn|Escore|Cox/i}).first();
  if (await linkCox.count()) { await linkCox.click({timeout:15000}).catch(()=>{}); await sleep(2500); }
  await shot(p,'proto-tela-escore-cox');
  const txt = await q.locator('body').innerText().catch(()=>'');
  console.log('APACHE visível no protótipo:', /APACHE/i.test(txt) ? 'SIM' : 'não');
  console.log('campos da tela:', (txt.match(/[A-ZÀ-Ú][^\n]{3,40}/g)||[]).slice(0,10).join(' · ').slice(0,240));
  await b.close();
})();
