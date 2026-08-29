// Aprova a versao corrente de uma etapa do v3 pela UI. Uso: node langnet_approve_v3.js <stage> <shot>
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const stage=process.argv[2], shot=process.argv[3]||(stage+'-aprovado');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:1050}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  let approved=false,st=0;
  p.on('response',r=>{if(r.request().method()==='POST'&&/approve/i.test(r.url())){approved=true;st=r.status();log('NET_APPROVE',st);}});
  await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  const APPROVE_SEL='button:has-text("Aprovar")';
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`http://localhost:3000/project/${PROJ}/${stage}`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator(APPROVE_SEL).first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);log('nav #'+a,navok);}
  await sleep(1500);
  const btn=p.locator(APPROVE_SEL).first();
  if(!(await btn.count())){log('ERRO: botao Aprovar nao encontrado');await p.screenshot({path:`${OUT}/${shot}-ERRO.png`,fullPage:true});await b.close();process.exit(2);}
  if(await btn.isDisabled()){log('AVISO: Aprovar desabilitado (ja aprovado?)');}
  await btn.click({force:true}).catch(e=>log('click warn',e.message));
  await sleep(3000);
  await p.screenshot({path:`${OUT}/${shot}.png`,fullPage:true});
  log('APPROVED_NET:',approved,'st',st);
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
