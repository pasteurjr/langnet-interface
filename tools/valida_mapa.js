const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/validacao-ui-rica/shots';
const fs=require('fs'); fs.mkdirSync(OUT,{recursive:true});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({headless:true});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  let osmTiles=0, consoleErrs=[];
  p.on('request', r=>{ if(/tile\.openstreetmap\.org/.test(r.url())) osmTiles++; });
  p.on('console', m=>{ if(m.type()==='error') consoleErrs.push(m.text().slice(0,120)); });
  p.on('pageerror', e=>consoleErrs.push('PAGEERROR: '+String(e).slice(0,140)));
  await p.goto('http://127.0.0.1:3900/', {waitUntil:'networkidle'});
  await sleep(2500);
  // menu presente?
  const menuItems = await p.evaluate(()=>[...document.querySelectorAll('nav a, nav button, aside a, aside button')].map(e=>e.innerText.trim()).filter(Boolean).slice(0,30));
  console.log('MENU:', JSON.stringify(menuItems.slice(0,14)));
  await p.screenshot({path:`${OUT}/app-home.png`, fullPage:false});
  // clica Consulta de Regramentos
  const link = p.locator('text=/Consulta de Regramentos/i').first();
  if(await link.count()){ await link.click(); } else { console.log('LINK Consulta nao encontrado'); }
  await sleep(4500); // deixa o Leaflet montar + tiles
  // mapa renderizou?
  const hasMap = await p.locator('.leaflet-container').count();
  const hasTiles = await p.locator('.leaflet-tile-loaded, img.leaflet-tile').count();
  const hasDraw = await p.locator('.leaflet-draw-toolbar, .leaflet-draw').count();
  const attr = await p.locator('.leaflet-control-attribution').first().innerText().catch(()=>'');
  console.log('LEAFLET container:', hasMap, '| tiles carregados:', hasTiles, '| toolbar desenho:', hasDraw);
  console.log('ATRIBUICAO:', attr.slice(0,60));
  console.log('OSM tile requests:', osmTiles);
  await p.screenshot({path:`${OUT}/tela-consulta-mapa.png`, fullPage:false});
  // testa PAN: drag no mapa
  const box = await p.locator('.leaflet-container').first().boundingBox().catch(()=>null);
  if(box){ await p.mouse.move(box.x+box.width/2, box.y+box.height/2); await p.mouse.down(); await p.mouse.move(box.x+box.width/2-120, box.y+box.height/2-80,{steps:8}); await p.mouse.up(); await sleep(1500); console.log('PAN executado'); }
  await p.screenshot({path:`${OUT}/tela-consulta-mapa-pan.png`, fullPage:false});
  // Dashboard (grafico)
  const dash=p.locator('text=/Dashboard de Gest/i').first();
  if(await dash.count()){ await dash.click(); await sleep(2500); const chart=await p.locator('svg.recharts-surface, .recharts-wrapper').count(); console.log('DASHBOARD grafico Recharts:', chart); await p.screenshot({path:`${OUT}/tela-dashboard.png`,fullPage:false}); }
  console.log('CONSOLE ERROS:', consoleErrs.slice(0,6));
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU:',e.message); process.exit(1);});
