// Navega numa rota do LangNet e tira screenshot (documentação). Uso: node nav_shot.js <rota> <nome>
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE='http://localhost:3000';
const PROJ='c4871aaf-3c8c-41d3-8ca7-6c3e22189731';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const rota=process.argv[2]||'';
const nome=process.argv[3]||'shot';
fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog',d=>d.dismiss().catch(()=>{}));
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  const url = rota.startsWith('http') ? rota : `${BASE}/project/${PROJ}/${rota}`;
  await p.goto(url,{waitUntil:'networkidle'}).catch(e=>console.log('nav warn:',e.message));
  await sleep(3500);
  // texto de nav/sidebar p/ entender as etapas
  const nav = await p.evaluate(()=>[...document.querySelectorAll('nav a, aside a, .sidebar a, [class*=menu] a')].map(e=>e.innerText.trim()).filter(Boolean).slice(0,40));
  console.log('URL:', url);
  console.log('NAV:', JSON.stringify([...new Set(nav)].slice(0,25)));
  // título/heading da página
  const h = await p.evaluate(()=>{const el=document.querySelector('h1,h2');return el?el.innerText.slice(0,80):'(sem heading)';});
  console.log('HEADING:', h);
  await p.screenshot({path:`${OUT}/${nome}.png`, fullPage:false});
  console.log('SHOT:', `${nome}.png`);
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message);process.exit(1);});
