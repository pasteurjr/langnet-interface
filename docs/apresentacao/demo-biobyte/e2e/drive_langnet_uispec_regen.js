// Regenera a UI Spec a partir de uma Especificação ESCOLHIDA e monta o protótipo.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1372', 10);
const ALVO = process.argv[3] || '';
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,130));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  const sel = p.locator('select').filter({hasText:/Spec|EM FASES/i}).first();
  if (await sel.count()) {
    const ops = await sel.locator('option').evaluateAll(os=>os.map(o=>({v:o.value,t:(o.textContent||'').trim()})));
    console.log('origens:', ops.map(o=>o.t.slice(0,46)).join(' || '));
    const alvo = ALVO ? ops.find(o=>o.v===ALVO) : ops.find(o=>o.v);
    if (!alvo) { console.log('!! origem pedida não está na lista'); await b.close(); return; }
    await sel.selectOption(alvo.v); await sleep(2500);
    console.log('origem escolhida:', alvo.t.slice(0,60));
    await shot(p,'uispec-origem-escolhida');
  }
  const btn = p.getByRole('button',{name:/Gerar UI Spec/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar UI Spec não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração das telas às', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p,'uispec-gerando');
  for (let i=0;i<180;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/\d+ telas/i.test(t) && !/Gerando|Processando/i.test(t)) break; }
  await sleep(3000); await shot(p,'uispec-telas-prontas');
  console.log('resultado:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(250,520));
  await b.close();
})();
