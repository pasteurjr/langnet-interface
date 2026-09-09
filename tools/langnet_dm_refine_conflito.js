// Etapa 3b: Refinar o Modelo de Dados pela UI — adicionar as colunas/entidades de CALCULO
// que a geracao dropou (o spec tinha; o DM perdeu). Preserva o operacional+geoespacial.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const MSG = [
"O portao de rastreabilidade achou uma task usando a tabela `conflitos_app`, que nao existe no modelo.",
"Adicione, SEM remover nada e mantendo PostGIS (geometry SRID 4674) e todas as tabelas atuais,",
"a tabela `conflitos_app` para registrar conflitos detectados entre zoneamento e APP (FR-036, alertas de conflito):",
"colunas id UUID PK, imovel_id UUID FK imoveis, zoneamento_id UUID FK zoneamentos, app_id UUID FK apps,",
"tipo_conflito VARCHAR, severidade VARCHAR, geometria_conflito geometry(Geometry,4674), descricao TEXT,",
"detectado_em timestamp, resolvido BOOLEAN. Nome em snake_case no plural igual ao que a task cita."
].join(" ");
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:1100}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  let done=false,st=0;
  p.on('response',async r=>{const u=r.url();if(r.request().method()==='POST'&&/data-model\/.*\/chat/.test(u)){done=true;st=r.status();log('CHAT_RESP',st);}});
  await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`http://localhost:3000/project/${PROJ}/data-model`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator('.dm-tabs, button.btn-chat-toggle').first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);log('nav dm #'+a,navok);}
  if(!navok){log('ERRO: data-model nao carregou');await b.close();process.exit(3);}
  await sleep(2500);
  // o chat comeca RECOLHIDO em wideViewer -> abrir
  await p.locator('button.btn-chat-toggle').first().click({timeout:8000}).catch(()=>log('aviso: btn-chat-toggle nao clicou'));
  await p.locator('.dm-chat-input input').first().waitFor({timeout:15000}).catch(()=>{});
  await sleep(1000);
  await p.screenshot({path:`${OUT}/44-dm-antes-conflito.png`,fullPage:true});
  // digitar no chat via JS-set + dispatch (input controlado) e enviar
  await p.evaluate((val)=>{const el=document.querySelector('.dm-chat-input input');const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(el,val);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},MSG);
  await sleep(600);
  const val=await p.evaluate(()=>document.querySelector('.dm-chat-input input')?.value?.length||0);
  log('STEP chat preenchido len=',val);
  await p.locator('.dm-chat-input input').first().press('Enter');
  log('STEP refino DM enviado; aguardando LLM re-gerar artefatos...');
  for(let i=0;i<200;i++){await sleep(5000);if(done)break;if(i%6===0)log('  ...',(i+1)*5,'s');}
  await sleep(3000);
  await p.screenshot({path:`${OUT}/45-dm-conflito.png`,fullPage:true});
  // abrir aba Schema SQL
  const sqlTab=p.locator('button.dm-tab',{hasText:/Schema SQL/}).first();
  if(await sqlTab.count()){await sqlTab.click();await sleep(1500);}
  await p.screenshot({path:`${OUT}/46-dm-schema-conflito.png`,fullPage:true});
  log(done?('CHAT_OK st='+st):'CHAT_NAO_RESP');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
