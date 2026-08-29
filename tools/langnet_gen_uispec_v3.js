// Etapa 4: gera a UI Spec do v3 (c4871aaf) a partir da spec mais recente (573139a3, auto-descoberta).
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:1100}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  let done=false,st=0;
  p.on('response',r=>{const u=r.url();if(r.request().method()==='POST'&&/ui-spec\/.*\/generate/.test(u)){done=true;st=r.status();log('GEN_RESP',st);}});
  await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`http://localhost:3000/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator('button:has-text("Gerar UI Spec")').first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);log('nav uispec #'+a,navok);}
  if(!navok){log('ERRO: pagina ui-spec nao carregou');await b.close();process.exit(3);}
  await sleep(1500);
  await p.screenshot({path:`${OUT}/25-uispec-antes.png`,fullPage:true});
  await p.locator('button:has-text("Gerar UI Spec")').first().click({force:true});
  log('geracao UI Spec disparada (endpoint SINCRONO, pode levar 15-30 min)...');
  for(let i=0;i<360;i++){await sleep(5000);if(done)break;if(i%12===0)log('  ...',(i+1)*5,'s');}
  await sleep(3000);
  await p.screenshot({path:`${OUT}/26-uispec-resultado.png`,fullPage:true});
  log(done?('GEN_OK st='+st):'GEN_TIMEOUT');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
