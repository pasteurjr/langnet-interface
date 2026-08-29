// Etapa 3b: Refinar o Modelo de Dados pela UI — adicionar as colunas/entidades de CALCULO
// que a geracao dropou (o spec tinha; o DM perdeu). Preserva o operacional+geoespacial.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const MSG = [
"Adicione o suporte a CALCULO urbanistico ao modelo, SEM remover nenhuma tabela existente:",
"1) Nova tabela `parametros_urbanisticos` (1:1 ou N:1 com zoneamentos, FK zoneamento_id): colunas",
"   ca_maximo NUMERIC(6,3), to_maxima NUMERIC(5,2), taxa_permeabilidade_minima NUMERIC(5,2),",
"   recuo_frontal_min NUMERIC(6,2), recuo_lateral_min NUMERIC(6,2), recuo_fundos_min NUMERIC(6,2),",
"   gabarito_maximo NUMERIC(6,2), area_minima_lote NUMERIC(12,2), usos_permitidos TEXT.",
"2) Na tabela `empreendimentos` adicione: area_terreno NUMERIC(12,2), area_construida NUMERIC(12,2),",
"   area_projecao NUMERIC(12,2), numero_pavimentos INTEGER, altura_edificacao NUMERIC(6,2).",
"3) Na tabela `consultas` adicione as colunas de RESULTADO do calculo: ca_calculado NUMERIC(6,3),",
"   to_calculado NUMERIC(5,2), recuo_frontal_calc NUMERIC(6,2), gabarito_calc NUMERIC(6,2),",
"   conforme BOOLEAN, resultado_conformidade JSONB.",
"Mantenha PostGIS (geometry SRID 4674) e todas as tabelas atuais. Tipos numericos decimais para os calculos."
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
  await p.screenshot({path:`${OUT}/21-dm-antes-refino.png`,fullPage:true});
  // digitar no chat via JS-set + dispatch (input controlado) e enviar
  await p.evaluate((val)=>{const el=document.querySelector('.dm-chat-input input');const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(el,val);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},MSG);
  await sleep(600);
  const val=await p.evaluate(()=>document.querySelector('.dm-chat-input input')?.value?.length||0);
  log('STEP chat preenchido len=',val);
  await p.locator('.dm-chat-input input').first().press('Enter');
  log('STEP refino DM enviado; aguardando LLM re-gerar artefatos...');
  for(let i=0;i<200;i++){await sleep(5000);if(done)break;if(i%6===0)log('  ...',(i+1)*5,'s');}
  await sleep(3000);
  await p.screenshot({path:`${OUT}/22-dm-refinado.png`,fullPage:true});
  // abrir aba Schema SQL
  const sqlTab=p.locator('button.dm-tab',{hasText:/Schema SQL/}).first();
  if(await sqlTab.count()){await sqlTab.click();await sleep(1500);}
  await p.screenshot({path:`${OUT}/23-dm-schema-refinado.png`,fullPage:true});
  log(done?('CHAT_OK st='+st):'CHAT_NAO_RESP');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
