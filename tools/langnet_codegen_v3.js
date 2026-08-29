// Dispara a geração de código do uso-solo pela UI, selecionando as sessões corretas.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const AGENTS='f9bb86cb-'; const TASKS='166d5f85-'; const ATS='848a7a0b-'; const PORT='5025';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  let genStatus=0, genDone=false, sessionNew='';
  p.on('response', async r=>{
    const u=r.url();
    if(r.request().method()==='POST' && /code-generation\/.*\/generate/.test(u)){
      genStatus=r.status(); genDone=true;
      try{ const j=await r.json(); sessionNew=j.session_id||''; }catch(e){}
      console.log('NET_CODEGEN_RESPOSTA', r.status(), 'session='+sessionNew);
    }
  });
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){await p.goto(`${BASE}/project/${PROJ}/code-generation`,{waitUntil:'domcontentloaded'}).catch(()=>{});navok=await p.locator('button:has-text(\"Gerar Código\")').first().waitFor({timeout:40000}).then(()=>true).catch(()=>false);console.log('nav codegen #'+a,navok);}
  await sleep(2500);
  // abre o modal
  const gen=p.locator('button',{hasText:/Gerar Código/i}).first();
  await gen.click(); await sleep(2500);
  // helper: seleciona no <select> a option cujo value começa com prefixo
  async function pick(idx, prefix, label){
    const sel=p.locator('select').nth(idx);
    const val=await sel.evaluate((el,pref)=>{
      const o=[...el.options].find(o=>o.value.startsWith(pref)); return o?o.value:'';
    }, prefix);
    if(!val){ console.log('NAO ACHOU option', label, prefix); return false; }
    await sel.selectOption(val); console.log('sel', label, '=', val.slice(0,8)); return true;
  }
  await pick(0, AGENTS, 'agents');
  await pick(1, TASKS, 'tasks');
  await pick(3, ATS, 'ats');
  // porta
  const port=p.locator('input[type="number"]').first();
  await port.fill(PORT); console.log('porta =', PORT);
  await p.screenshot({path:`${OUT}/34-codegen-modal.png`,fullPage:true});
  // confirmar (o ultimo botao "Gerar Código" dentro do modal)
  const confirm=p.locator('button',{hasText:/Gerar Código/i}).last();
  console.log('confirmando...'); await confirm.click({timeout:5000}).catch(e=>console.log('click err',e.message));
  console.log('▷ code-gen disparado; aguardando (gera ~80-110 arquivos)...');
  for(let i=0;i<160;i++){
    await sleep(15000);
    if(genDone){ console.log('CODEGEN concluído status', genStatus, 'em ~', (i+1)*15, 's'); break; }
    if(i%4===0) console.log('  ...', (i+1)*15,'s');
  }
  await sleep(3000);
  await p.screenshot({path:`${OUT}/35-codegen-done.png`,fullPage:true});
  console.log('SESSION_CODE:', sessionNew);
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
