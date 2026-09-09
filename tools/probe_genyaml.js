const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/generate-yaml`,{waitUntil:'networkidle'});
  await sleep(3000);
  // clica Selecionar Documento
  const sel=p.locator('button',{hasText:/Selecionar Documento/i}).first();
  console.log('btn Selecionar Documento:', await sel.count());
  if(await sel.count()){ await sel.click(); await sleep(2500); }
  await p.screenshot({path:`${OUT}/probe-doc-modal.png`,fullPage:true});
  // lista o texto de itens clicáveis do modal
  const items = await p.evaluate(()=>{
    const els=[...document.querySelectorAll('button, li, [role="option"], .modal *')];
    return els.map(e=>e.innerText).filter(t=>t&&t.trim().length>3&&t.length<120).slice(0,40);
  });
  console.log('ITENS_MODAL:\n'+[...new Set(items)].join('\n'));
  await b.close();
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
