// Etapa Modelo de Dados: escolhe a Especificação de origem, gera, e captura para o roteiro.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1360', 10);
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
  await p.goto(`${BASE}/project/${PROJ}/data-model`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  await shot(p,'dm-etapa-aberta');
  // origem: a Especificação nova (a lista vem ordenada; pega a primeira opção com valor)
  const sel = p.locator('select[title="Especificação de origem"]').first();
  if (await sel.count()) {
    const ops = await sel.locator('option').evaluateAll(os=>os.map(o=>({v:o.value,t:(o.textContent||'').trim()})));
    console.log('origens disponíveis:', JSON.stringify(ops.slice(0,4)));
    // a especificação de origem vem por argumento: escolher "a primeira da lista" já fez o modelo
    // de dados nascer de uma especificação antiga, sem a correção que o usuário tinha pedido
    const ALVO = process.argv[3] || '';
    const alvo = ALVO ? ops.find(o=>o.v === ALVO) : ops.find(o=>o.v);
    if (ALVO && !alvo) { console.log('!! especificação pedida não está na lista:', ALVO); await b.close(); return; }
    if (alvo) { await sel.selectOption(alvo.v); await sleep(2500); console.log('origem escolhida:', alvo.t.slice(0,50)); }
    await shot(p,'dm-origem-escolhida');
  } else console.log('!! seletor de origem não achado');
  const btn = p.getByRole('button',{name:/Gerar Modelo de Dados|Regenerar do zero/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar não achado'); await b.close(); return; }
  await btn.click({timeout:20000});
  console.log('▷ geração disparada às', new Date().toLocaleTimeString());
  await sleep(4000); await shot(p,'dm-gerando');
  for (let i=0;i<150;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/CREATE TABLE|entidades|Aprovar/i.test(t) && !/Gerando|Processando/i.test(t)) break; }
  await sleep(2000); await shot(p,'dm-pronto');
  console.log('final:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,300));
  await b.close();
})();
