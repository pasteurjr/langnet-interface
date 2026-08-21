const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs'); const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const b=await chromium.launch({headless:true});
 const p=await b.newPage({viewport:{width:1500,height:1050}});
 await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
 await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
 await p.goto('http://localhost:3000/project/9cbea119-c57b-4df1-a183-2ff68b5040e1/code-generation',{waitUntil:'networkidle'});
 await sleep(3500);
 const gb=p.locator('button',{hasText:/Nova geração/}).first();
 console.log('Gerar Código btn:',await gb.count());
 if(await gb.count()){await gb.click();await sleep(2500);}
 await p.screenshot({path:`${OUT}/codegen-nova-modal.png`,fullPage:true});
 const els=await p.evaluate(()=>{const o=[];document.querySelectorAll('button,select,input,label').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>0&&r.height>0){const tx=(e.innerText||e.value||e.placeholder||'').slice(0,45);if(tx)o.push(e.tagName+':'+tx);}});return o.slice(0,45);});
 console.log('ELEMS:',JSON.stringify(els));
 await b.close();console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
