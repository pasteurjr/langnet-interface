const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs'); const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const b=await chromium.launch({headless:true});
 const p=await b.newPage({viewport:{width:1500,height:1050}});
 await p.goto('http://localhost:3000',{waitUntil:'domcontentloaded'});
 await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
 await p.goto('http://localhost:3000/project/9cbea119-c57b-4df1-a183-2ff68b5040e1/code-generation',{waitUntil:'networkidle'});
 await sleep(3500);
 await p.locator('button',{hasText:/Nova geração/i}).first().click();
 await sleep(3500);
 console.log('n selects:', await p.locator('select').count());
 const sels=await p.evaluate(()=>{
   return Array.from(document.querySelectorAll('select')).map((s,i)=>({idx:i,opts:Array.from(s.options).map(o=>o.text.slice(0,50))}));
 });
 sels.forEach(s=>{console.log('SELECT',s.idx+':');s.opts.forEach((o,j)=>console.log('   ['+j+']',o));});
 await b.close();console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
