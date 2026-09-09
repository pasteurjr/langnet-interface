// Loop de convergência: refina o tasks.yaml (sessao 676b064b) pela UI com a lista EXATA
// de violacoes que o portao apontou, ate ficar verde.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const MSG=[
"Corrija SOMENTE os erros de SQL abaixo, mantendo TODAS as tasks e o resto identico:",
"1) ALIAS FORA DO FROM: toda query que usa `i.geometria`/`i.id` (imoveis) ou `a.`/`z.` deve ter a",
"   tabela no FROM. Ex. do conflito de APP: use `SELECT COUNT(*) AS conflito_app FROM apps a, imoveis i",
"   WHERE ST_Intersects(a.geometria, i.geometria) AND i.id = %s`. NENHUM alias pode aparecer no WHERE",
"   sem estar no FROM/JOIN. Corrija tambem o alias `coordenadas` usado fora do FROM.",
"2) COLUNA INEXISTENTE: `imoveis` NAO tem as colunas tipo, ca_max, to_max; `zoneamentos` NAO tem tipo.",
"   ca_maximo/to_maxima estao em `parametros_urbanisticos` (achado pela zona via ST_Contains + JOIN",
"   parametros_urbanisticos ON zona_id). Remova/corrija toda referencia a coluna que nao existe no schema.",
"Nao invente coluna nem tabela. Mantenha as fórmulas de calculo e a traceability de cada task."
].join(" ");
(async()=>{
  const b=await chromium.launch({headless:true});const p=await b.newPage({viewport:{width:1500,height:1050}});
  p.on('dialog',d=>d.accept().catch(()=>{}));const log=(...a)=>console.log(...a);
  let posted=false,st=0;
  p.on('response',r=>{const u=r.url();if(r.request().method()==='POST'&&/tasks-yaml\/.*\/refine/.test(u)){posted=true;st=r.status();log('REFINE_POST',st);}});
  await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`http://localhost:3000/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator('.btn-history-compact').first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);log('nav #'+a,navok);}
  if(!navok){log('ERRO: pagina nao carregou');await b.close();process.exit(3);}
  // aba Tasks YAML
  await p.locator('button:has-text("Tasks YAML")').first().click({timeout:6000}).catch(()=>{});
  await sleep(1200);
  // abrir historico -> selecionar sessao -> versao
  await p.locator('.btn-history-compact').first().click(); await sleep(2000);
  await p.waitForSelector('.session-item',{timeout:15000}).catch(()=>{});
  await p.locator('.session-item').first().click(); await sleep(2500);       // sessao mais recente (676b064b)
  await p.locator('.session-item').first().click(); await sleep(3500);       // versao -> seta currentSessionId
  log('sessao carregada');
  // abrir chat
  await p.locator('.btn-chat-toggle').first().click({timeout:6000}).catch(()=>log('sem chat-toggle'));
  await p.locator('.chat-input:not([disabled])').first().waitFor({timeout:15000}).catch(()=>{});
  await sleep(800);
  const inp=await p.$('.chat-input');
  if(!inp){log('ERRO: chat-input nao apareceu (sessao nao ativou)');await p.screenshot({path:`${OUT}/ty-refine-nochat.png`,fullPage:true});await b.close();process.exit(2);}
  await p.evaluate((val)=>{const el=document.querySelector('.chat-input');const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(el,val);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},MSG);
  await sleep(500);
  log('chat len:',await p.evaluate(()=>document.querySelector('.chat-input')?.value?.length||0));
  await p.locator('.btn-send').first().click({force:true}).catch(async()=>{await p.locator('.chat-input').press('Enter');});
  log('refino enviado; aguardando POST...');
  for(let i=0;i<20;i++){await sleep(3000);if(posted)break;}
  await sleep(2000);
  log(posted?('TY_REFINE_POSTED st='+st):'TY_REFINE_NAO_DISPAROU');
  await b.close();log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
