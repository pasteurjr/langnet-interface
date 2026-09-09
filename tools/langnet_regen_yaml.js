// Regenera agents.yaml + tasks.yaml do uso-solo pela UI (para pegar o campo execution).
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/validacao-pipeline/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  // captura a resposta da geração
  let genStatus=0, genDone=false;
  p.on('response', async r=>{
    const u=r.url();
    if(r.request().method()==='POST' && /agent-task\/generate/.test(u)){
      genStatus=r.status(); genDone=true;
      console.log('NET_GEN_RESPOSTA', r.status(), u.split('/api/')[1]||u);
    }
  });
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/generate-yaml`,{waitUntil:'networkidle'});
  await sleep(3000);

  // 1) Selecionar Documento
  const selBtn=p.locator('button',{hasText:/Selecionar Documento/i}).first();
  await selBtn.click(); await sleep(2000);
  const card=p.locator('.session-card').first();
  console.log('session-cards:', await p.locator('.session-card').count());
  await card.click(); await sleep(1800);
  await p.screenshot({path:`${OUT}/regen-yaml-1-after-cardclick.png`,fullPage:true});

  // 2) pode abrir a tela de VERSÕES → clicar em "Selecionar" da versão
  const selVer=p.locator('button',{hasText:/^Selecionar$|Usar esta|Selecionar Vers/i}).first();
  if(await selVer.count()){ console.log('tela de versoes → Selecionar'); await selVer.click(); await sleep(1500); }
  // se ainda houver modal aberto, tenta fechar clicando fora não; screenshot
  await p.screenshot({path:`${OUT}/regen-yaml-2-selected.png`,fullPage:true});

  // 3) Gerar Agentes & Tarefas
  const genBtn=p.locator('button',{hasText:/Gerar Agentes & Tarefas/i}).first();
  const disabled = await genBtn.getAttribute('disabled');
  console.log('btn Gerar disabled?', disabled);
  await genBtn.click({timeout:5000}).catch(e=>console.log('click gerar err:',e.message));
  console.log('▷ geração disparada; aguardando (tasks sequenciais no LLM)...');
  await p.screenshot({path:`${OUT}/regen-yaml-3-generating.png`,fullPage:true});

  // 4) monitora até a resposta (até 40 min)
  for(let i=0;i<160;i++){
    await sleep(15000);
    if(genDone){ console.log('GEN concluída status', genStatus, 'em ~', ((i+1)*15), 's'); break; }
    if(i%4===0){
      const txt=await p.evaluate(()=>{const m=document.body.innerText.match(/(\d+)\s+agentes?\s+e\s+(\d+)\s+tarefas?/i);return m?m[0]:'';});
      console.log('  ...', (i+1)*15, 's', txt?('| '+txt):'');
    }
  }
  await sleep(3000);
  await p.screenshot({path:`${OUT}/regen-yaml-4-done.png`,fullPage:true});
  const done=await p.evaluate(()=>{const m=document.body.innerText.match(/(\d+)\s+agentes?\s+e\s+(\d+)\s+tarefas?/i);return m?m[0]:'(sem contagem)';});
  console.log('RESULTADO_UI:', done);
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
