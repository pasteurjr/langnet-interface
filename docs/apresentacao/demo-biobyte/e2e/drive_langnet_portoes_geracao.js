// Verifica pela interface o painel de PORTÕES na página de Geração de Código (sessão mais recente).
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '900', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000,fullPage:false});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,160));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/code-generation`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  // seleciona a sessão mais recente na lista, se a página não a carregou sozinha
  const item = p.locator('text=/v\\d+ · \\d+ arquivos · completed/').first();
  if (await item.count()) { await item.click().catch(()=>{}); await sleep(3000); }
  const painel = p.locator('.cg-portoes').first();
  console.log('painel de portões presente:', await painel.count());
  if (await painel.count()) {
    await painel.scrollIntoViewIfNeeded().catch(()=>{});
    console.log('texto:', (await painel.innerText()).replace(/\n/g,' | ').slice(0, 600));
  } else {
    console.log('tela:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0, 400));
  }
  await shot(p,'geracao-portoes');
  await b.close();
  console.log('DONE próximo índice', N);
})();
