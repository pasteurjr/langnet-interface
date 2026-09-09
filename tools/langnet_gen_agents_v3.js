// Gera o agents.yaml COERENTE a partir do ATS novo (bf41c118) pela aba "Agents YAML"
// (/yaml-generation). Cria agents_yaml_sessions proprio, SEM tocar no tasks.yaml.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:1050}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  let posted=false,st=0,sess='';
  p.on('response',async r=>{const u=r.url();if(r.request().method()==='POST'&&/agents-yaml\/?$/.test(u)){posted=true;st=r.status();try{sess=(await r.json()).session_id||'';}catch(e){}log('POST_AGENTS',st,sess.slice(0,8));}});
  await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  const SELBTN='button:has-text("Selecionar Documento")';
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`http://localhost:3000/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator(SELBTN).first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);log('nav yaml #'+a,navok);}
  if(!navok){log('ERRO: pagina yaml-generation nao carregou');await b.close();process.exit(3);}
  // garantir aba Agents YAML ativa
  await p.locator('button:has-text("Agents YAML")').first().click({timeout:5000}).catch(()=>{});
  await sleep(1200);
  // abrir modal de selecao de ATS
  await p.locator(SELBTN).first().click(); await sleep(2500);
  await p.waitForSelector('.session-card',{timeout:15000}).catch(()=>{});
  await p.screenshot({path:`${OUT}/47-agents-modal.png`,fullPage:true});
  // ATS mais recente (bf41c118, 30 tarefas) = primeiro .session-card, depois .version-card
  await p.locator('.session-card').first().click(); await sleep(2500);
  await p.locator('.version-card').first().click(); await sleep(2500);
  log('ATS selecionado');
  await p.screenshot({path:`${OUT}/48-agents-atssel.png`,fullPage:true});
  // gerar
  const gen=p.locator('button:has-text("Gerar agents.yaml")').first();
  if(await gen.isDisabled()){log('AVISO: botao gerar desabilitado');await p.keyboard.press('Escape').catch(()=>{});await sleep(800);}
  await gen.click({force:true});
  log('geracao agents.yaml disparada; aguardando POST...');
  for(let i=0;i<20;i++){await sleep(3000);if(posted)break;}
  await sleep(2000);
  await p.screenshot({path:`${OUT}/49-agents-iniciada.png`,fullPage:true});
  log(posted?('AGENTS_POSTED st='+st+' sess='+sess):'AGENTS_NAO_DISPAROU');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
