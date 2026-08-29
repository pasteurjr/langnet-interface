// Etapa 5: gera o Agent-Task Spec (ATS) do v3 a partir da Especificacao mais recente (573139a3).
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:1100}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  let posted=false,st=0,sess='';
  p.on('response',async r=>{const u=r.url();if(r.request().method()==='POST'&&/agent-task-spec\/?$/.test(u)){posted=true;st=r.status();try{sess=(await r.json()).session_id||'';}catch(e){}log('POST_ATS',st,sess.slice(0,8));}});
  await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  const SELBTN='button:has-text("Selecionar Especificação")';
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`http://localhost:3000/project/${PROJ}/agent-task`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator(SELBTN).first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);log('nav ats #'+a,navok);}
  if(!navok){log('ERRO: pagina agent-task nao carregou');await b.close();process.exit(3);}
  await sleep(1500);
  // 1) abrir modal de selecao de spec
  await p.locator(SELBTN).first().click(); await sleep(2500);
  await p.waitForSelector('.session-item',{timeout:15000}).catch(()=>{});
  await p.screenshot({path:`${OUT}/27-ats-modal-spec.png`,fullPage:true});
  // 2) sessao de spec mais recente
  await p.locator('.session-item').first().click(); await sleep(2500);
  // 3) versao (primeira)
  await p.locator('.session-item').first().click(); await sleep(2500);
  log('spec selecionada');
  await p.screenshot({path:`${OUT}/28-ats-spec-sel.png`,fullPage:true});
  // 4) gerar
  const gen=p.locator('button:has-text("Gerar Agentes")').first();
  if(await gen.isDisabled()){log('AVISO: botao Gerar desabilitado; tentando fechar modal e clicar');await p.keyboard.press('Escape').catch(()=>{});await sleep(1000);}
  await gen.click({force:true});
  log('geracao ATS disparada; aguardando POST...');
  for(let i=0;i<20;i++){await sleep(3000);if(posted)break;}
  await sleep(2000);
  await p.screenshot({path:`${OUT}/29-ats-iniciada.png`,fullPage:true});
  log(posted?('ATS_POSTED st='+st+' sess='+sess):'ATS_NAO_DISPAROU');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
