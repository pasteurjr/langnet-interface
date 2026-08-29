// Etapa 1 (pela UI do LangNet): enriquecer os Requisitos do v3 (c4871aaf)
// Sobe os DOIS documentos-fonte (operacional v3 + calculador v2) no Assistente de
// Requisitos e dispara a Análise com instrução de UNIFICAR — o proprio pipeline funde.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const RD='/tmp/claude-1000/-home-pasteurjr-progreact-langnet-interface/6ffe399e-58d4-4438-b6ef-54d02554a4f7/scratchpad/reqdocs';
const F1=RD+'/requisitos_v3_operacional.md';
const F2=RD+'/requisitos_v2_calculador.md';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync(OUT,{recursive:true});

const INSTR = [
'Unifique os DOIS documentos anexados em um unico documento de requisitos, tratando-os como',
'evolucao de uma mesma aplicacao de gestao municipal de uso do solo (nao sao apps diferentes).',
'',
'REGRA 1 — PRESERVE INTEGRALMENTE todo o conteudo OPERACIONAL do primeiro documento',
'(requisitos_v3_operacional): cadastros, processos de licenciamento/alvara, protocolos,',
'fiscalizacao, notificacoes, fluxos administrativos, perfis de usuario e relatorios.',
'',
'REGRA 2 — ADICIONE por cima os EIXOS DE CALCULO URBANISTICO do segundo documento',
'(requisitos_v2_calculador), que HOJE FALTAM no primeiro: calculo de Coeficiente de',
'Aproveitamento (CA) e Taxa de Ocupacao (TO); recuos (frontal/lateral/fundos); gabarito/altura',
'maxima; Area de Preservacao Permanente (APP); reserva legal; declividade do terreno;',
'parametros por zona; dados de lote (area do terreno) e de edificacao (area construida);',
'importacao de Shapefile; e a consulta que retorna a conformidade urbanistica calculada.',
'',
'REGRA 3 — nao remova nada do operacional para caber o calculo: o resultado e a UNIAO dos dois,',
'com requisitos funcionais renumerados de forma continua (FR-XXX) e sem duplicatas.',
].join('\n');

(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.accept().catch(()=>{}));
  const log=(...a)=>console.log(...a);

  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'networkidle'}).catch(e=>log('nav warn',e.message));
  await sleep(3000);
  log('STEP navegou requirements');

  // 1) abrir modal de upload
  await p.click('text=Fazer Upload').catch(async()=>{ await p.click('text=+ Upload'); });
  await sleep(1200);
  await p.screenshot({path:`${OUT}/02-upload-modal.png`});
  log('STEP modal upload aberto');

  // 2) setar os DOIS arquivos no input[type=file]
  const input = await p.$('input[type=file]');
  await input.setInputFiles([F1,F2]);
  await sleep(1000);
  await p.screenshot({path:`${OUT}/03-arquivos-selecionados.png`});
  log('STEP arquivos selecionados');

  // 3) confirmar upload (botao ".btn-upload" no rodape do modal)
  await p.click('.footer-actions .btn-upload',{force:true});
  log('STEP clicou upload — aguardando ingestao...');
  // esperar aparecer os itens de documento na lista (status Pendente)
  await p.waitForFunction(()=>{const h=document.querySelector('.sidebar-header h3, .documents-sidebar h3'); return h && /\((\d+)\)/.test(h.textContent) && Number(RegExp.$1)>=2;}, {timeout:60000}).catch(()=>log('WARN nao confirmou 2 docs no header'));
  await sleep(1500);
  await p.screenshot({path:`${OUT}/04-docs-carregados.png`});
  const hdr=await p.evaluate(()=>{const h=document.querySelector('.sidebar-header h3, .documents-sidebar h3');return h?h.textContent.trim():'?';});
  log('STEP docs carregados — header:', hdr);

  // 4) instrucoes de unificacao
  const ta=await p.$('.analysis-config textarea, textarea');
  await ta.click(); await ta.fill(''); await ta.type(INSTR,{delay:1});
  await sleep(400);

  // 5) desmarcar Pesquisa Web (docs ja sao a saida da pesquisa; +rapido/deterministico)
  const cb=await p.$('.analysis-config input[type=checkbox], input[type=checkbox]');
  if(cb){const checked=await cb.isChecked(); if(checked) await cb.click();}
  await sleep(300);
  await p.screenshot({path:`${OUT}/05-instrucoes-config.png`});
  log('STEP instrucoes preenchidas, web research OFF');

  // 6) iniciar analise
  await p.click('button:has-text("Iniciar Análise")').catch(async()=>{await p.click('.btn-start-analysis');});
  await sleep(4000);
  await p.screenshot({path:`${OUT}/06-analise-iniciada.png`});
  log('STEP analise iniciada');

  // capturar session_id que aparece nas mensagens do chat / console
  await sleep(3000);
  const bodyTxt=await p.evaluate(()=>document.body.innerText.slice(0,1500));
  log('CHAT-PREVIEW:', bodyTxt.replace(/\n+/g,' | ').slice(0,600));

  await b.close(); log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
