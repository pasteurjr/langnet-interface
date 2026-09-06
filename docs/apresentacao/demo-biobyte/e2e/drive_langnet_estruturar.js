// Dirige a etapa YAML pela interface: abre a sessão do tasks.yaml e clica "Estruturar passos".
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs'); process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '980', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{await p.screenshot({path:`${OUT}/${N}-langnet-${tag}.png`,timeout:60000});console.log('📸',`${N}-langnet-${tag}.png`);N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:'/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox'});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,400));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'});
  await sleep(6000);
  const aba=p.locator('.tab-button', { hasText: /tasks/i }).first();
  if(await aba.count()) { await aba.click({timeout:8000}); console.log('aba tasks.yaml aberta'); }
  for(let i=0;i<12;i++){ await sleep(2000); const b=p.getByRole('button',{name:/Estruturar passos/i}).first(); if(await b.count() && !(await b.isDisabled())) break; }
  const txt=await p.evaluate(()=>document.body.innerText);
  console.log('página:', txt.replace(/\n/g,' | ').slice(0,200));
  const btn=p.getByRole('button',{name:/Estruturar passos/i}).first();
  console.log('botão Estruturar:', await btn.count()?'presente':'AUSENTE', '| habilitado:', await btn.count()? !(await btn.isDisabled()) : '-');
  await shot(p,'yaml-antes-estruturar');
  if(await btn.count() && !(await btn.isDisabled())){
    await btn.click({timeout:10000}); console.log('▷ estruturar disparado');
    for(let i=0;i<90;i++){ await sleep(5000); const t=await p.evaluate(()=>document.body.innerText); if(/estruturada|já tinha contrato|falha do agente|não devolveu/i.test(t)) break; }
    await sleep(2000);
    const t=await p.evaluate(()=>document.body.innerText);
    const ini=t.indexOf('Estruturar passos'); console.log('relatório:', t.slice(ini, ini+900).replace(/\n/g,' | '));
    await shot(p,'yaml-passos-estruturados');
  }
  await b.close(); console.log('DONE');
})();
