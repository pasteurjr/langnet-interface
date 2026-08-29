// Etapa 1b (pela UI): "Refinar" o documento de requisitos unificado — EXPANDIR o calculo
// que a analise colapsou em um FR-008 generico, transformando-o em FRs concretos por eixo.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync(OUT,{recursive:true});

const MSG = [
'Refine o documento SEM resumir o que ja existe. O bloco de calculo urbanistico esta',
'colapsado num unico requisito generico (FR-008 "Eixos de Calculo Urbanistico"). Substitua-o',
'por requisitos funcionais CONCRETOS E DETALHADOS, um para cada eixo, com formula/criterio de',
'aceite mensuravel:',
'',
'1. Coeficiente de Aproveitamento (CA): CA = area_construida / area_terreno; comparar com',
'   ca_maximo da zona; retornar conforme/nao-conforme.',
'2. Taxa de Ocupacao (TO): TO = area_projecao / area_terreno; comparar com to_maxima da zona.',
'3. Recuos: calcular recuo frontal, lateral e de fundos e validar contra os minimos da zona.',
'4. Gabarito / altura maxima: validar altura da edificacao contra o gabarito da zona.',
'5. Area de Preservacao Permanente (APP): delimitar faixa por curso d agua/nascente e detectar',
'   sobreposicao com o lote (Codigo Florestal).',
'6. Reserva Legal: calcular a area de reserva legal por imovel (percentual por bioma).',
'7. Declividade: avaliar declividade do terreno e classificar restricoes (0-5,5-15,15-25,>25%).',
'8. Parametros por zona: cadastrar/consultar ca_maximo, to_maxima, recuos minimos, gabarito,',
'   area minima de lote e usos permitidos por zona.',
'9. Importacao de Shapefile/GeoJSON para zonas, lotes e APP (SRID SIRGAS 2000 / EPSG 4674).',
'10. Consulta de conformidade: dado um lote/edificacao, retornar todos os calculos acima com o',
'    veredito de conformidade urbanistica.',
'',
'Adicione esses eixos como NOVOS requisitos (FR-015 em diante), sem renumerar os existentes.',
'Remova apenas o FR "Integracao de Documentos" (era instrucao minha, nao e requisito) e o',
'"Suporte a Multiplos Idiomas". PRESERVE identicos todos os demais requisitos operacionais',
'(cadastro, licenciamento, alvara, fiscalizacao, notificacoes, relatorios, dashboard).',
].join('\n');

(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.accept().catch(()=>{}));
  const log=(...a)=>console.log(...a);

  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  // esperar a sidebar (documentos) carregar — DB remoto pode demorar/flake -> ate 4 tentativas
  let ok=false;
  for(let att=1; att<=4 && !ok; att++){
    await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'}).catch(e=>log('nav warn',e.message));
    ok = await p.waitForSelector('.btn-history-compact',{timeout:40000}).then(()=>true).catch(()=>false);
    log('STEP tentativa sidebar #'+att+' ->', ok?'OK':'timeout(recarrega)');
  }
  if(!ok){log('ERRO: documentos nao carregaram (DB remoto lento). Abortando.');await b.close();process.exit(3);}
  await sleep(1000);
  log('STEP sidebar carregada');

  // 1) abrir Historico
  await p.click('.btn-history-compact');
  await p.waitForSelector('.session-item',{timeout:15000});
  await sleep(800);
  await p.screenshot({path:`${OUT}/07-historico-sessoes.png`});
  // 2) clicar na sessao mais recente (primeiro .session-item)
  await p.click('.sessions-list .session-item');
  // esperar a lista de VERSOES carregar (troca de conteudo, ainda .session-item)
  await sleep(2500);
  await p.screenshot({path:`${OUT}/08-historico-versoes.png`});
  // 3) clicar na Versao 1 (primeiro item de versao) -> seta currentSessionId (via onSelectSession)
  await p.click('.session-item');
  await sleep(6000); // deixar o onSelectSession propagar o currentSessionId
  log('STEP sessao+versao selecionada; doc carregado');
  await p.screenshot({path:`${OUT}/09-doc-carregado.png`});

  // 4) digitar refinamento e enviar via botao .btn-send
  // esperar o input ficar realmente habilitado (o polling pos-load pode desabilita-lo um instante)
  await p.waitForSelector('.chat-input:not([disabled])',{timeout:30000});
  await sleep(1500);
  await p.waitForSelector('.chat-input:not([disabled])',{timeout:30000});
  const inp=await p.$('.chat-input');
  if(!inp){log('ERRO: chat-input nao encontrado (sessao nao ativou)');await p.screenshot({path:`${OUT}/09b-sem-chat.png`});await b.close();process.exit(2);}
  await inp.scrollIntoViewIfNeeded().catch(()=>{});
  // setar o valor via JS + disparar input/change (React controlled) — evita timeout de actionability do .type
  await p.evaluate((val)=>{
    const el=document.querySelector('.chat-input');
    const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
    setter.call(el,val);
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  }, MSG);
  await sleep(600);
  await p.screenshot({path:`${OUT}/10-refino-digitado.png`});
  const val=await p.evaluate(()=>document.querySelector('.chat-input')?.value?.length||0);
  log('STEP input preenchido, len=',val);
  await p.click('.btn-send',{force:true});
  log('STEP refino enviado (btn-send) — aguardando processamento...');
  await sleep(8000);
  await p.screenshot({path:`${OUT}/11-refino-enviado.png`});
  const body=await p.evaluate(()=>document.body.innerText.slice(0,800).replace(/\n+/g,' | '));
  log('BODY:',body.slice(0,400));
  await b.close(); log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
