// Harness de captura BioByte Sentinela — Playwright + inject user/token + proxy /api->:8003
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs');
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const USER=JSON.stringify({id:'f8edd66e-bcb8-11f0-b19e-a0ad9f2fcdf4',name:'Admin Master',email:'teste@teste.com',role:'admin',is_active:true});
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const BACKEND='http://localhost:8003';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function newCtx(){
  const b=await chromium.launch({headless:true});
  const ctx=await b.newContext({viewport:{width:1600,height:1000},deviceScaleFactor:1.5});
  await ctx.addInitScript(([t,u])=>{['accessToken','token','authToken'].forEach(k=>localStorage.setItem(k,t));localStorage.setItem('user',u);},[TOKEN,USER]);
  await ctx.route('**/api/**', async route=>{const nu=new URL(route.request().url());
    try{const r=await ctx.request.fetch(BACKEND+nu.pathname+nu.search,{method:route.request().method(),
      headers:{...route.request().headers(),authorization:'Bearer '+TOKEN},data:route.request().postDataBuffer()||undefined,maxRedirects:5});
      const h={...r.headers()};delete h['content-encoding'];delete h['content-length'];delete h['transfer-encoding'];
      h['access-control-allow-origin']='http://localhost:3005';h['access-control-allow-credentials']='true';
      await route.fulfill({status:r.status(),body:await r.body(),headers:h});}catch(e){await route.abort();}});
  return {b,ctx};
}
module.exports={newCtx,sleep,OUT,BACKEND,TOKEN,USER};
