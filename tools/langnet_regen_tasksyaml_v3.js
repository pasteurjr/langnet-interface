// Regenera o tasks.yaml PERSISTIDO (build_single_task_prompt → tasks_yaml_sessions) pela UI.
// Rota /yaml-generation, aba Tasks YAML. É o tasks.yaml que o code-gen realmente lê.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  let genStatus=0, genDone=false, newSession='';
  p.on('response', async r=>{
    const u=r.url();
    if(r.request().method()==='POST' && /\/tasks-yaml\/?(\?|$)/.test(u) && !/refine|review|versions/.test(u)){
      genStatus=r.status(); genDone=true;
      try{ const j=await r.json(); newSession=j.session_id||j.id||''; }catch(e){}
      console.log('NET_GEN_RESPOSTA', r.status(), 'session='+newSession);
    }
  });
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`${BASE}/project/${PROJ}/yaml-generation`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator('button:has-text(\"Tasks YAML\"), button:has-text(\"Selecionar Documento\")').first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);console.log('nav yaml #'+a,navok);}
  await sleep(2500);
  // aba Tasks YAML
  const tab=p.locator('button',{hasText:/Tasks YAML/i}).first();
  if(await tab.count()){ await tab.click(); await sleep(1500); }
  // Selecionar Documento MD (ou botão base)
  let sel=p.locator('button',{hasText:/Selecionar Documento/i}).first();
  console.log('btn Selecionar:', await sel.count());
  await sel.click(); await sleep(2000);
  const nCards=await p.locator('.session-card').count();
  console.log('session-cards:', nCards);
  await p.locator('.session-card').first().click();
  // espera a view de versões carregar (loadVersions é async)
  await p.waitForSelector('.version-card', {timeout:12000}).catch(()=>console.log('  (sem version-card em 12s)'));
  const nVer=await p.locator('.version-card').count();
  console.log('version-cards:', nVer);
  if(nVer>0){ await p.locator('.version-card').first().click(); await sleep(2000); }
  else { await p.screenshot({path:`${OUT}/31-tasksyaml-modal.png`,fullPage:true}); }
  await p.screenshot({path:`${OUT}/31-tasksyaml-selected.png`,fullPage:true});
  // Gerar tasks.yaml
  const gen=p.locator('button',{hasText:/Gerar tasks\.yaml/i}).first();
  console.log('btn Gerar tasks.yaml:', await gen.count(), 'disabled?', await gen.getAttribute('disabled'));
  await gen.click({timeout:5000}).catch(e=>console.log('click err:',e.message));
  console.log('▷ geração disparada (8 tasks sequenciais)...');
  await p.screenshot({path:`${OUT}/32-tasksyaml-generating.png`,fullPage:true});
  for(let i=0;i<200;i++){          // até 50 min
    await sleep(15000);
    if(genDone){ console.log('GEN concluída status', genStatus, 'em ~', ((i+1)*15), 's'); break; }
    if(i%4===0) console.log('  ...', (i+1)*15, 's');
  }
  await sleep(3000);
  await p.screenshot({path:`${OUT}/33-tasksyaml-done.png`,fullPage:true});
  console.log('SESSION_NOVA:', newSession);
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
