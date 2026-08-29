// Abre a sessao de requisitos, carrega o doc e captura o "Visualizar" (para o PDF).
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs');
const BASE='http://localhost:3000', PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  let ok=false;for(let a=1;a<=4&&!ok;a++){await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'}).catch(()=>{});ok=await p.waitForSelector('.btn-history-compact',{timeout:40000}).then(()=>true).catch(()=>false);log('sidebar #'+a,ok);}
  if(!ok){log('ERRO sidebar');await b.close();process.exit(3);}
  await p.click('.btn-history-compact');await p.waitForSelector('.session-item',{timeout:15000});await sleep(800);
  await p.click('.sessions-list .session-item');await sleep(2500);
  await p.click('.session-item');await sleep(6000);
  log('doc carregado');
  // clicar em Visualizar (DocumentActionsCard)
  await p.click('button:has-text("Visualizar")',{force:true}).catch(()=>log('sem botao Visualizar'));
  await sleep(2500);
  await p.screenshot({path:`${OUT}/12-doc-refinado.png`});
  log('SHOT 12-doc-refinado');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
