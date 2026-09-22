// Etapa YAML: gera agents.yaml e tasks.yaml a partir do documento de Agentes e Tarefas.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '390', 10);
const PROJ=fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};

async function gerar(p, aba, rotulo) {
  if (aba) { await p.getByRole('button',{name:aba}).first().click().catch(()=>{}); await sleep(3000); }
  // origem
  const abrir = p.locator('button[title="Selecionar Documento de Agentes/Tarefas Base"], button:has-text("Selecionar Documento MD")').first();
  if (await abrir.count()) {
    await abrir.click(); await sleep(2500);
    await p.waitForSelector('.session-card, .session-item',{timeout:15000}).catch(()=>{});
    const itens = await p.locator('.session-card, .session-item').evaluateAll(es=>es.map(e=>(e.innerText||'').replace(/\n/g,' | ').slice(0,70)));
    console.log(rotulo,'origens:', JSON.stringify(itens.slice(0,3)));
    if (itens.length) {
      await p.locator('.session-card, .session-item').first().click(); await sleep(3000);
      // 2o passo: a lista de VERSOES usa outra classe (version-*), nao session-card
      const vers = p.locator('.version-card, .version-item, [class*=version-]');
      const nv = await vers.count();
      console.log(rotulo, 'versoes:', nv);
      if (nv) { await vers.first().click(); await sleep(3000); }
    }
    await sleep(1500);
  }
  await shot(p, rotulo+'-origem');
  const btn = p.getByRole('button',{name:/Gerar (agents|tasks)\.yaml|Regenerar/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar não achado em', rotulo); return; }
  await btn.click({timeout:20000});
  console.log('▷', rotulo, 'disparado', new Date().toLocaleTimeString());
  await sleep(5000); await shot(p, rotulo+'-gerando');
  for (let i=0;i<150;i++){ await sleep(10000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/(agents|tasks)\.yaml/i.test(t) && !/Gerando|Processando|GERANDO/i.test(t)) break; }
  await sleep(2500); await shot(p, rotulo+'-pronto');
}

(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1600,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,110));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'yaml-etapa-aberta');
  await gerar(p, null, 'yaml-agentes');
  await gerar(p, /Tasks YAML/i, 'yaml-tarefas');
  console.log('final:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(200,500));
  await b.close();
})();
